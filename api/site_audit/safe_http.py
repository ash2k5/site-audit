"""SSRF-safe HTTP fetches.

Every request and every redirect hop is re-resolved and re-checked against the
public-address policy, and the connection is pinned to the validated IP so a
short-TTL rebinding record cannot swap a public answer for a private one between
the check and the connect. TLS SNI and certificate verification stay bound to
the original hostname.
"""

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter

from .validation import MAX_URL_LENGTH, is_public_address, normalize_url

MAX_REDIRECTS = 10
_REDIRECT_CODES = (301, 302, 303, 307, 308)
_ALLOWED_SCHEMES = ("http", "https")
_DEFAULT_PORTS = {"http": 80, "https": 443}


class _PinnedSNIAdapter(HTTPAdapter):
    """Verifies the certificate and sets SNI for the original hostname even
    though the socket connects to a pre-validated IP literal."""

    def __init__(self, hostname: str) -> None:
        self._hostname = hostname
        super().__init__()

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        kwargs["server_hostname"] = self._hostname
        kwargs["assert_hostname"] = self._hostname
        super().init_poolmanager(connections, maxsize, block=block, **kwargs)


def _resolve_validated(host: str, port: int) -> str:
    """Resolve host and return one validated IP, rejecting if it cannot be
    resolved or any resolved address is non-public."""
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise ValueError(f"Cannot resolve host {host!r}") from e
    if not infos:
        raise ValueError(f"Cannot resolve host {host!r}")
    for info in infos:
        if not is_public_address(ipaddress.ip_address(info[4][0])):
            raise ValueError(f"Refusing to fetch non-public address for host {host!r}")
    return str(infos[0][4][0])


def _send(
    method: str,
    scheme: str,
    host: str,
    port: int | None,
    validated_ip: str,
    path_qs: str,
    headers: dict | None,
    timeout: float,
) -> requests.Response:
    netloc_ip = f"[{validated_ip}]" if ":" in validated_ip else validated_ip
    if port is not None:
        netloc_ip = f"{netloc_ip}:{port}"
    ip_url = f"{scheme}://{netloc_ip}{path_qs}"

    req_headers = dict(headers or {})
    req_headers["Host"] = host if port is None else f"{host}:{port}"

    session = requests.Session()
    session.trust_env = False
    if scheme == "https":
        session.mount("https://", _PinnedSNIAdapter(host))
    try:
        return session.request(
            method, ip_url, headers=req_headers, timeout=timeout, allow_redirects=False
        )
    finally:
        session.close()


def safe_request(
    method: str, url: str, *, headers: dict | None = None, timeout: float
) -> requests.Response:
    """Fetch url, following redirects manually and re-validating every hop.

    Raises ValueError if any hop resolves to a non-public address or cannot be
    resolved, requests.TooManyRedirects past MAX_REDIRECTS, and the usual
    requests.RequestException on transport failure.
    """
    current = normalize_url(url)
    history: list[requests.Response] = []

    for _ in range(MAX_REDIRECTS + 1):
        if len(current) > MAX_URL_LENGTH:
            raise ValueError("URL is too long")
        parsed = urlparse(current)
        scheme = parsed.scheme
        if scheme not in _ALLOWED_SCHEMES:
            raise ValueError(f"Unsupported URL scheme: {scheme!r}")
        host = parsed.hostname
        if not host:
            raise ValueError("URL has no host")

        validated_ip = _resolve_validated(host, parsed.port or _DEFAULT_PORTS[scheme])
        path_qs = parsed.path or "/"
        if parsed.query:
            path_qs = f"{path_qs}?{parsed.query}"

        resp = _send(method, scheme, host, parsed.port, validated_ip, path_qs, headers, timeout)

        location = resp.headers.get("Location") if resp.status_code in _REDIRECT_CODES else None
        if location:
            resp.close()
            history.append(resp)
            current = urljoin(current, location)
            continue

        resp.url = current
        resp.history = history
        return resp

    raise requests.TooManyRedirects(f"Exceeded {MAX_REDIRECTS} redirects")
