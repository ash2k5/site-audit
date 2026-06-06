from site_audit import audit
from site_audit.audit import build_report, safe_filename


def test_safe_filename():
    assert safe_filename("example.com") == "audit_example_com.pdf"
    assert safe_filename("https://www.acme.com") == "audit_acme_com.pdf"
    assert safe_filename("https://acme.com:8080") == "audit_acme_com_8080.pdf"


def test_build_report(monkeypatch, report):
    monkeypatch.setattr(
        audit, "scrape_site", lambda url: (report.raw_data.seo, report.raw_data.technical)
    )
    monkeypatch.setattr(audit, "get_pagespeed_data", lambda url, key: report.raw_data.performance)
    monkeypatch.setattr(audit, "analyze_site", lambda inp, api_key: report)
    out = build_report("example.com", groq_key="k", allow_private=True)
    assert out is report
