import pytest
from fastapi.testclient import TestClient

from site_audit import web
from site_audit.web import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def groq_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")


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


def test_audit_pdf(monkeypatch, report):
    monkeypatch.setattr(web, "build_report", lambda url, **k: report)

    def fake_pdf(rep, path, skip_screenshot=False):
        with open(path, "wb") as f:
            f.write(b"%PDF-1.4 test")

    monkeypatch.setattr(web, "generate_pdf", fake_pdf)
    r = client.post("/audit", data={"url": "https://example.com"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")


def test_audit_upstream_failure(monkeypatch):
    def boom(url, **k):
        raise RuntimeError("groq down")

    monkeypatch.setattr(web, "build_report", boom)
    r = client.post("/audit", data={"url": "https://example.com"})
    assert r.status_code == 502
