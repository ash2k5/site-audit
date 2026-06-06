import json
import time

from groq import Groq

from .models import AuditInput, AuditReport, CategoryScore, Recommendation

MODEL = "llama-3.3-70b-versatile"

_CATEGORY_SCHEMA = {
    "type": "object",
    "required": ["score", "grade", "summary", "findings"],
    "properties": {
        "score": {"type": "integer"},
        "grade": {"type": "string", "enum": ["A", "B", "C", "D", "F"]},
        "summary": {"type": "string"},
        "findings": {"type": "array", "items": {"type": "string"}},
    },
}

_TOOL = {
    "type": "function",
    "function": {
        "name": "render_audit_report",
        "description": "Render a structured site audit report for the sales team",
        "parameters": {
            "type": "object",
            "required": [
                "company_name",
                "overall_score",
                "executive_summary",
                "seo",
                "performance",
                "technical",
                "content",
                "quick_wins",
                "recommendations",
            ],
            "properties": {
                "company_name": {"type": "string"},
                "overall_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "executive_summary": {"type": "string"},
                "seo": _CATEGORY_SCHEMA,
                "performance": _CATEGORY_SCHEMA,
                "technical": _CATEGORY_SCHEMA,
                "content": _CATEGORY_SCHEMA,
                "quick_wins": {"type": "array", "items": {"type": "string"}},
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["title", "impact", "effort", "detail"],
                        "properties": {
                            "title": {"type": "string"},
                            "impact": {
                                "type": "string",
                                "enum": ["High", "Medium", "Low"],
                            },
                            "effort": {
                                "type": "string",
                                "enum": ["High", "Medium", "Low"],
                            },
                            "detail": {"type": "string"},
                        },
                    },
                },
            },
        },
    },
}

_SYSTEM = (
    "You are an expert digital marketing consultant producing site audits "
    "for a B2B sales team. Be specific, actionable, and honest. "
    "Frame findings as opportunities the prospect has not yet captured. "
    "Tone: professional, direct, credibility-building."
)


def _fmt_seconds(ms: float | None) -> str:
    if ms is None:
        return "N/A"
    seconds = ms / 1000 if ms > 100 else ms
    return f"{seconds:.2f}s"


def _fmt_ms(ms: float | None) -> str:
    return f"{ms:.0f}ms" if ms is not None else "N/A"


def _build_prompt(audit: AuditInput) -> str:
    seo = audit.seo
    perf = audit.performance
    tech = audit.technical

    lines = [
        f"URL: {audit.url}",
        "",
        "## Technical",
        f"- HTTPS: {tech.is_https}",
        f"- Status code: {tech.status_code}",
        f"- Response time: {tech.response_time_ms}ms",
        f"- Redirects: {tech.redirect_count}",
        f"- robots.txt present: {tech.has_robots_txt}",
        f"- sitemap.xml present: {tech.has_sitemap}",
        "",
        "## SEO",
        f"- Title: {seo.title!r} ({len(seo.title)} chars)",
        f"- Meta description: {seo.meta_description!r} ({len(seo.meta_description)} chars)",
        f"- H1 tags ({len(seo.h1_tags)}): {seo.h1_tags[:3]}",
        f"- H2 tags ({len(seo.h2_tags)}): {seo.h2_tags[:5]}",
        f"- Canonical URL: {seo.canonical_url or 'not set'}",
        f"- Open Graph title: {seo.og_title or 'missing'}",
        f"- Open Graph description: {seo.og_description or 'missing'}",
        f"- Schema markup: {seo.has_schema_markup}",
        f"- Images missing alt text: {seo.images_missing_alt}/{seo.total_images}",
        f"- Internal links: {seo.internal_links}",
        f"- External links: {seo.external_links}",
        "",
        "## Content",
        f"- Word count: {seo.word_count}",
        f"- CTA present: {seo.has_cta}",
        f"- Contact info present: {seo.has_contact_info}",
        "",
        "## Performance",
        f"- Mobile score: {perf.mobile_score}/100",
        f"- Desktop score: {perf.desktop_score}/100",
    ]

    mv = perf.mobile_vitals
    if mv.lcp is not None:
        lines += [
            "",
            "### Mobile Core Web Vitals",
            f"- LCP: {_fmt_seconds(mv.lcp)}",
            f"- CLS: {mv.cls if mv.cls is not None else 'N/A'}",
            f"- FCP: {_fmt_seconds(mv.fcp)}",
            f"- TTFB: {_fmt_ms(mv.ttfb)}",
        ]

    if perf.opportunities:
        lines += ["", "### Opportunities", *[f"- {o}" for o in perf.opportunities]]
    if perf.diagnostics:
        lines += ["", "### Diagnostics", *[f"- {d}" for d in perf.diagnostics]]

    return "\n".join(lines)


def _call_groq(client: Groq, prompt: str) -> dict:
    user_content = f"Produce a site audit report for the following data:\n\n{prompt}"
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": user_content},
                ],
                tools=[_TOOL],
                tool_choice={
                    "type": "function",
                    "function": {"name": "render_audit_report"},
                },
            )
            return json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"LLM analysis failed: {e}") from e
            time.sleep(attempt + 1)
    raise RuntimeError("LLM analysis failed")


def analyze_site(audit: AuditInput, *, api_key: str) -> AuditReport:
    client = Groq(api_key=api_key)
    data = _call_groq(client, _build_prompt(audit))

    def cat(key: str) -> CategoryScore:
        c = data[key]
        return CategoryScore(
            score=c["score"],
            grade=c["grade"],
            summary=c["summary"],
            findings=c["findings"],
        )

    return AuditReport(
        url=audit.url,
        company_name=data["company_name"],
        overall_score=data["overall_score"],
        executive_summary=data["executive_summary"],
        seo=cat("seo"),
        performance=cat("performance"),
        technical=cat("technical"),
        content=cat("content"),
        quick_wins=data["quick_wins"],
        recommendations=[
            Recommendation(
                title=r["title"],
                impact=r["impact"],
                effort=r["effort"],
                detail=r["detail"],
            )
            for r in data["recommendations"]
        ],
        raw_data=audit,
    )
