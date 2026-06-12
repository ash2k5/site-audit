import socket

import pytest
import requests
from requests.structures import CaseInsensitiveDict

from site_audit import safe_http


class FakeResp:
    def __init__(self, status=200, headers=None, text="body"):
        self.status_code = status
        self.headers = CaseInsensitiveDict(headers or {})
        self.text = text
        self.url = None
        self.history = None
        self.closed = False

    def close(self):
        self.closed = True


def _addr(ip):
    def fake_getaddrinfo(host, port, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port or 0))]

    return fake_getaddrinfo


def _resolves(mapping):
    def fake_getaddrinfo(host, port, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (mapping[host], port or 0))]

    return fake_getaddrinfo


def test_resolve_validated_returns_public_ip(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("93.184.216.34"))
    assert safe_http._resolve_validated("example.com", 443) == "93.184.216.34"


def test_resolve_validated_rejects_private(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("127.0.0.1"))
    with pytest.raises(ValueError):
        safe_http._resolve_validated("localhost", 80)


def test_resolve_validated_rejects_mixed_records(monkeypatch):
    def mixed(host, port, *a, **k):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 0)),
        ]

    monkeypatch.setattr(safe_http.socket, "getaddrinfo", mixed)
    with pytest.raises(ValueError):
        safe_http._resolve_validated("mixed.example", 80)


def test_resolve_validated_unresolvable(monkeypatch):
    def boom(*a, **k):
        raise socket.gaierror("nope")

    monkeypatch.setattr(safe_http.socket, "getaddrinfo", boom)
    with pytest.raises(ValueError):
        safe_http._resolve_validated("no-such-host.invalid", 80)


def test_connects_to_validated_ip_and_keeps_logical_url(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("93.184.216.34"))
    seen = {}

    def fake_send(method, scheme, host, port, ip, path_qs, headers, timeout):
        seen.update(method=method, scheme=scheme, host=host, ip=ip, path_qs=path_qs)
        return FakeResp(200, text="ok")

    monkeypatch.setattr(safe_http, "_send", fake_send)
    r = safe_http.safe_request("GET", "https://public.example/path?q=1", timeout=5)

    assert seen == {
        "method": "GET",
        "scheme": "https",
        "host": "public.example",
        "ip": "93.184.216.34",
        "path_qs": "/path?q=1",
    }
    assert r.url == "https://public.example/path?q=1"
    assert r.status_code == 200


def test_private_host_never_connects(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("10.0.0.5"))
    calls = []
    monkeypatch.setattr(safe_http, "_send", lambda *a, **k: calls.append(a) or FakeResp())
    with pytest.raises(ValueError):
        safe_http.safe_request("GET", "http://evil.example", timeout=5)
    assert calls == []


def test_redirect_to_private_rejected(monkeypatch):
    monkeypatch.setattr(
        safe_http.socket,
        "getaddrinfo",
        _resolves({"public.example": "93.184.216.34", "169.254.169.254": "169.254.169.254"}),
    )
    monkeypatch.setattr(
        safe_http,
        "_send",
        lambda *a, **k: FakeResp(302, {"Location": "http://169.254.169.254/latest/meta-data/"}),
    )
    with pytest.raises(ValueError):
        safe_http.safe_request("GET", "http://public.example", timeout=5)


def test_redirect_to_bad_scheme_rejected(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("93.184.216.34"))
    monkeypatch.setattr(
        safe_http, "_send", lambda *a, **k: FakeResp(302, {"Location": "file:///etc/passwd"})
    )
    with pytest.raises(ValueError):
        safe_http.safe_request("GET", "https://public.example", timeout=5)


def test_follows_public_redirect(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("93.184.216.34"))
    responses = iter(
        [
            FakeResp(301, {"Location": "https://public.example/final"}),
            FakeResp(200, text="done"),
        ]
    )
    monkeypatch.setattr(safe_http, "_send", lambda *a, **k: next(responses))
    r = safe_http.safe_request("GET", "https://public.example/start", timeout=5)
    assert r.status_code == 200
    assert r.url == "https://public.example/final"
    assert len(r.history) == 1


def test_too_many_redirects(monkeypatch):
    monkeypatch.setattr(safe_http.socket, "getaddrinfo", _addr("93.184.216.34"))
    monkeypatch.setattr(
        safe_http,
        "_send",
        lambda *a, **k: FakeResp(302, {"Location": "https://public.example/loop"}),
    )
    with pytest.raises(requests.TooManyRedirects):
        safe_http.safe_request("GET", "https://public.example/loop", timeout=5)
