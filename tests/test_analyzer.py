import json

import pytest

from site_audit import analyzer
from site_audit.analyzer import _build_prompt, analyze_site
from site_audit.models import (
    AuditInput,
    CoreWebVitals,
    PerformanceData,
    SEOData,
    TechnicalData,
)


def _audit() -> AuditInput:
    return AuditInput(
        url="https://acme.com",
        seo=SEOData(title="Acme", meta_description="d", h1_tags=["H"], word_count=100),
        performance=PerformanceData(
            mobile_score=70,
            desktop_score=90,
            mobile_vitals=CoreWebVitals(lcp=2400.0, cls=0.05, fcp=1500.0, ttfb=300.0),
        ),
        technical=TechnicalData(status_code=200, is_https=True, response_time_ms=120.0),
    )


def test_build_prompt_contains_signals():
    p = _build_prompt(_audit())
    assert "URL: https://acme.com" in p
    assert "Mobile score: 70/100" in p
    assert "LCP: 2.40s" in p
    assert "TTFB: 300ms" in p


PAYLOAD = {
    "company_name": "Acme",
    "overall_score": 77,
    "executive_summary": "Good",
    "seo": {"score": 80, "grade": "B", "summary": "s", "findings": ["a"]},
    "performance": {"score": 70, "grade": "C", "summary": "s", "findings": []},
    "technical": {"score": 90, "grade": "A", "summary": "s", "findings": []},
    "content": {"score": 75, "grade": "C", "summary": "s", "findings": []},
    "quick_wins": ["w1"],
    "recommendations": [{"title": "t", "impact": "High", "effort": "Low", "detail": "d"}],
}


class _Fn:
    def __init__(self, arguments):
        self.arguments = arguments


class _ToolCall:
    def __init__(self, arguments):
        self.function = _Fn(arguments)


class _Message:
    def __init__(self, arguments):
        self.tool_calls = [_ToolCall(arguments)]


class _Choice:
    def __init__(self, arguments):
        self.message = _Message(arguments)


class _Resp:
    def __init__(self, arguments):
        self.choices = [_Choice(arguments)]


class FakeClient:
    def __init__(self, errors: int = 0):
        self._errors = errors
        self.calls = 0
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self._errors:
            raise RuntimeError("transient")
        return _Resp(json.dumps(PAYLOAD))


def test_analyze_site_maps_payload(monkeypatch):
    monkeypatch.setattr(analyzer, "Groq", lambda api_key: FakeClient())
    report = analyze_site(_audit(), api_key="k")
    assert report.company_name == "Acme"
    assert report.overall_score == 77
    assert report.seo.grade == "B"
    assert report.recommendations[0].impact == "High"
    assert report.raw_data is not None


def test_call_groq_retries(monkeypatch):
    monkeypatch.setattr(analyzer.time, "sleep", lambda s: None)
    fake = FakeClient(errors=2)
    monkeypatch.setattr(analyzer, "Groq", lambda api_key: fake)
    report = analyze_site(_audit(), api_key="k")
    assert fake.calls == 3
    assert report.company_name == "Acme"


def test_call_groq_gives_up(monkeypatch):
    monkeypatch.setattr(analyzer.time, "sleep", lambda s: None)
    monkeypatch.setattr(analyzer, "Groq", lambda api_key: FakeClient(errors=99))
    with pytest.raises(RuntimeError):
        analyze_site(_audit(), api_key="k")
