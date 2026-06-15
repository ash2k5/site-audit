import requests

from site_audit import pagespeed
from site_audit.pagespeed import _score, _vitals, get_pagespeed_data

MOBILE = {
    "lighthouseResult": {
        "categories": {"performance": {"score": 0.75}},
        "audits": {
            "largest-contentful-paint": {"numericValue": 2400.0},
            "cumulative-layout-shift": {"numericValue": 0.05},
            "first-contentful-paint": {"numericValue": 1500.0},
            "server-response-time": {"numericValue": 300.0},
            "speed-index": {"numericValue": 3000.0},
            "uses-optimized-images": {
                "score": 0.5,
                "title": "Efficiently encode images",
                "displayValue": "1.0 s",
                "details": {"type": "opportunity"},
            },
            "unminified-css": {
                "score": 0.4,
                "title": "Minify CSS",
                "displayValue": "0.5 s",
                "details": {"type": "table"},
            },
            "color-contrast": {"score": 0.8, "title": "Contrast", "displayValue": ""},
        },
    }
}
DESKTOP = {"lighthouseResult": {"categories": {"performance": {"score": 0.95}}, "audits": {}}}


def test_score():
    assert _score(MOBILE) == 75
    assert _score(None) is None
    assert _score({"lighthouseResult": {}}) is None


def test_vitals():
    v = _vitals(MOBILE)
    assert v.lcp == 2400.0
    assert v.cls == 0.05
    assert v.ttfb == 300.0
    assert _vitals(None).lcp is None


def test_get_pagespeed_data(monkeypatch):
    monkeypatch.setattr(
        pagespeed,
        "_fetch",
        lambda url, strategy, key: MOBILE if strategy == "mobile" else DESKTOP,
    )
    data = get_pagespeed_data("https://acme.com", None)
    assert data.mobile_score == 75
    assert data.desktop_score == 95
    assert data.mobile_vitals.lcp == 2400.0
    assert any("Efficiently encode images" in o for o in data.opportunities)
    assert any("Minify CSS" in d for d in data.diagnostics)


def test_fetch_returns_none_on_failure(monkeypatch):
    monkeypatch.setattr(pagespeed.time, "sleep", lambda s: None)

    def boom(*a, **k):
        raise requests.RequestException("err")

    monkeypatch.setattr(pagespeed.requests, "get", boom)
    assert pagespeed._fetch("https://x.com", "mobile", None) is None
