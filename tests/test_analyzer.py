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
    def __init__(self, tool_calls):
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, tool_calls):
        self.message = _Message(tool_calls)


class _Resp:
    def __init__(self, tool_calls):
        self.choices = [_Choice(tool_calls)]


class FakeClient:
    def __init__(self, errors: int = 0, payload=None, with_tool_call: bool = True):
        self._errors = errors
        self._payload = PAYLOAD if payload is None else payload
        self._with_tool_call = with_tool_call
        self.calls = 0
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self._errors:
            raise RuntimeError("transient")
        if not self._with_tool_call:
            return _Resp(None)
        return _Resp([_ToolCall(json.dumps(self._payload))])


def test_analyze_site_maps_payload(monkeypatch):
    monkeypatch.setattr(analyzer, "Groq", lambda **kw: FakeClient())
    report = analyze_site(_audit(), api_key="k")
    assert report.company_name == "Acme"
    assert report.overall_score == 77
    assert report.seo.grade == "B"
    assert report.recommendations[0].impact == "High"
    assert report.raw_data is not None


def test_call_groq_retries(monkeypatch):
    monkeypatch.setattr(analyzer.time, "sleep", lambda s: None)
    fake = FakeClient(errors=2)
    monkeypatch.setattr(analyzer, "Groq", lambda **kw: fake)
    report = analyze_site(_audit(), api_key="k")
    assert fake.calls == 3
    assert report.company_name == "Acme"


def test_call_groq_gives_up(monkeypatch):
    monkeypatch.setattr(analyzer.time, "sleep", lambda s: None)
    monkeypatch.setattr(analyzer, "Groq", lambda **kw: FakeClient(errors=99))
    with pytest.raises(RuntimeError):
        analyze_site(_audit(), api_key="k")


def test_client_configured_with_timeout_and_no_sdk_retries(monkeypatch):
    captured = {}

    def fake_groq(**kw):
        captured.update(kw)
        return FakeClient()

    monkeypatch.setattr(analyzer, "Groq", fake_groq)
    analyze_site(_audit(), api_key="k")
    assert captured["timeout"] == analyzer.GROQ_TIMEOUT
    assert captured["max_retries"] == 0


def test_missing_tool_call_raises_runtime(monkeypatch):
    monkeypatch.setattr(analyzer.time, "sleep", lambda s: None)
    monkeypatch.setattr(analyzer, "Groq", lambda **kw: FakeClient(with_tool_call=False))
    with pytest.raises(RuntimeError):
        analyze_site(_audit(), api_key="k")


def test_malformed_payload_raises_runtime(monkeypatch):
    incomplete = {k: v for k, v in PAYLOAD.items() if k != "company_name"}
    monkeypatch.setattr(analyzer, "Groq", lambda **kw: FakeClient(payload=incomplete))
    with pytest.raises(RuntimeError):
        analyze_site(_audit(), api_key="k")


def test_prompt_clips_untrusted_fields():
    audit = _audit()
    audit.seo.title = "BUY NOW " * 1000
    p = _build_prompt(audit)
    title_line = next(line for line in p.splitlines() if line.startswith("- Title:"))
    assert "..." in title_line
    assert len(title_line) < 300
    assert "(8000 chars)" in title_line


def test_call_groq_frames_data_as_untrusted(monkeypatch):
    fake = FakeClient()
    captured = {}

    real_create = fake.create

    def spy(**kwargs):
        captured["messages"] = kwargs["messages"]
        return real_create(**kwargs)

    fake.create = spy
    analyzer._call_groq(fake, "PROMPT BODY")
    user_msg = captured["messages"][1]["content"]
    assert "<site_data>" in user_msg
    assert "untrusted" in user_msg.lower()
    assert "PROMPT BODY" in user_msg
