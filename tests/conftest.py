import pytest

from site_audit.models import (
    AuditInput,
    AuditReport,
    CategoryScore,
    CoreWebVitals,
    PerformanceData,
    Recommendation,
    SEOData,
    TechnicalData,
)


def _cat(score: int = 80, grade: str = "B") -> CategoryScore:
    return CategoryScore(score=score, grade=grade, summary="summary text", findings=["f1", "f2"])


def make_report(url: str = "https://example.com") -> AuditReport:
    seo = SEOData(
        title="Example",
        meta_description="An example site",
        h1_tags=["Welcome"],
        word_count=500,
        total_images=4,
        images_missing_alt=1,
        internal_links=10,
        external_links=3,
        has_cta=True,
        has_contact_info=True,
    )
    perf = PerformanceData(
        mobile_score=70,
        desktop_score=90,
        mobile_vitals=CoreWebVitals(lcp=2400.0, cls=0.05, fcp=1500.0, ttfb=300.0),
        opportunities=["Reduce unused JavaScript"],
        diagnostics=["Serve static assets with an efficient cache policy"],
    )
    tech = TechnicalData(
        status_code=200,
        is_https=True,
        final_url=url,
        response_time_ms=120.0,
        has_robots_txt=True,
        has_sitemap=True,
    )
    raw = AuditInput(url=url, seo=seo, performance=perf, technical=tech)
    return AuditReport(
        url=url,
        company_name="Example Inc",
        overall_score=78,
        executive_summary="Solid foundation with a few high-impact gaps.",
        seo=_cat(82, "B"),
        performance=_cat(70, "C"),
        technical=_cat(90, "A"),
        content=_cat(75, "C"),
        quick_wins=["Add alt text to images", "Compress hero image"],
        recommendations=[
            Recommendation(
                title="Improve LCP",
                impact="High",
                effort="Medium",
                detail="Optimize the hero image and preload it.",
            ),
        ],
        raw_data=raw,
    )


@pytest.fixture
def report() -> AuditReport:
    return make_report()
