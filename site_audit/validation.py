import ipaddress
import socket
from urllib.parse import urlparse

_ALLOWED_SCHEMES = ("http", "https")


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("URL is empty")
    if "://" not in url:
        url = "https://" + url
    return url


def validate_url(url: str, *, allow_private: bool = False) -> str:
    """Normalize and validate a target URL, returning the normalized form.

    Raises ValueError for malformed input or, unless allow_private is set, for a
    host that resolves to a non-public address (loopback, private, link-local,
    reserved). This is the SSRF guard for the hosted service.
    """
    normalized = normalize_url(url)
    parsed = urlparse(normalized)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme!r}")
    host = parsed.hostname
    if not host:
        raise ValueError("URL has no host")

    if not allow_private:
        _reject_non_public_host(host)
    return normalized


def _reject_non_public_host(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise ValueError(f"Cannot resolve host {host!r}") from e
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError(f"Refusing to audit non-public address for host {host!r}")
