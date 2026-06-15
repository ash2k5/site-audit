import threading

import pytest
from fastapi.testclient import TestClient

from site_audit import web
from site_audit.web import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def groq_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def reset_limits(monkeypatch):
    web._rate_limiter._hits.clear()
    web._rate_limiter.max_requests = 100
    web._daily_budget._day = None
    web._daily_budget._count = 0
    web._daily_budget.limit = 1000
    monkeypatch.setattr(web, "_API_KEY", None)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index():
    r = client.get("/")
    assert r.status_code == 200
    assert "Generate audit" in r.text


def test_api_audit_success(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)
    r = client.get("/api/audit", params={"url": "https://example.com"})
    assert r.status_code == 200
    assert r.json()["company_name"] == "Example Inc"


def test_api_audit_missing_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    r = client.get("/api/audit", params={"url": "https://example.com"})
    assert r.status_code == 503


def test_api_audit_bad_url(monkeypatch):
    def boom(url, **k):
        raise ValueError("bad url")

    monkeypatch.setattr(web, "build_report", boom)
    r = client.get("/api/audit", params={"url": "ftp://x"})
    assert r.status_code == 400
    assert "bad url" in r.json()["detail"]


def test_audit_pdf(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)
    captured = {}

    def fake_pdf(rep, path, skip_screenshot=False):
        captured["skip_screenshot"] = skip_screenshot
        with open(path, "wb") as f:
            f.write(b"%PDF-1.4 test")

    monkeypatch.setattr(web, "generate_pdf", fake_pdf)
    r = client.post("/audit", data={"url": "https://example.com"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    assert captured["skip_screenshot"] is True


def test_audit_upstream_failure_is_generic(monkeypatch):
    def boom(url, **k):
        raise RuntimeError("groq internal token=secret123")

    monkeypatch.setattr(web, "build_report", boom)
    r = client.post("/audit", data={"url": "https://example.com"})
    assert r.status_code == 502
    assert "secret123" not in r.text
    assert "RuntimeError" not in r.text


def test_rate_limit_returns_429(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)
    web._rate_limiter.max_requests = 1
    first = client.get("/api/audit", params={"url": "https://example.com"})
    second = client.get("/api/audit", params={"url": "https://example.com"})
    assert first.status_code == 200
    assert second.status_code == 429


def test_daily_budget_returns_503(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)
    web._daily_budget.limit = 1
    first = client.get("/api/audit", params={"url": "https://example.com"})
    second = client.get("/api/audit", params={"url": "https://example.com"})
    assert first.status_code == 200
    assert second.status_code == 503


def test_api_key_enforced(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)
    monkeypatch.setattr(web, "_API_KEY", "secret")
    denied = client.get("/api/audit", params={"url": "https://example.com"})
    assert denied.status_code == 401
    allowed = client.get(
        "/api/audit", params={"url": "https://example.com"}, headers={"x-api-key": "secret"}
    )
    assert allowed.status_code == 200


def test_concurrency_cap_returns_429(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)
    full = threading.BoundedSemaphore(1)
    full.acquire()
    monkeypatch.setattr(web, "_audit_slots", full)
    r = client.get("/api/audit", params={"url": "https://example.com"})
    assert r.status_code == 429
    full.release()


def test_body_too_large():
    r = client.post("/audit", data={"url": "x" * 20000})
    assert r.status_code == 413
