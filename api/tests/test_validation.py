import socket

import pytest

from site_audit.validation import normalize_url, validate_url


def test_normalize_adds_https():
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("  example.com  ") == "https://example.com"
    assert normalize_url("http://x.com") == "http://x.com"


def test_normalize_rejects_empty():
    with pytest.raises(ValueError):
        normalize_url("   ")


def test_validate_rejects_bad_scheme():
    with pytest.raises(ValueError):
        validate_url("ftp://example.com", allow_private=True)


def test_validate_rejects_missing_host():
    with pytest.raises(ValueError):
        validate_url("https://", allow_private=True)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1",
        "http://10.0.0.5",
        "http://169.254.169.254",
    ],
)
def test_validate_blocks_non_public(url):
    with pytest.raises(ValueError):
        validate_url(url)


def test_allow_private_skips_resolution(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("should not resolve when allow_private is set")

    monkeypatch.setattr(socket, "getaddrinfo", boom)
    assert validate_url("http://localhost", allow_private=True) == "http://localhost"


def test_validate_accepts_public(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [(socket.AF_INET, None, None, "", ("93.184.216.34", 0))],
    )
    assert validate_url("example.com") == "https://example.com"


def test_validate_unresolvable(monkeypatch):
    def boom(*a, **k):
        raise socket.gaierror("nope")

    monkeypatch.setattr(socket, "getaddrinfo", boom)
    with pytest.raises(ValueError):
        validate_url("https://no-such-host.invalid")
