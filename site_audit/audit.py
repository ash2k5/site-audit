import logging
from urllib.parse import urlparse

from .analyzer import analyze_site
from .models import AuditInput, AuditReport
from .pagespeed import get_pagespeed_data
from .scraper import scrape_site
from .validation import normalize_url, validate_url

log = logging.getLogger(__name__)


def build_report(
    url: str,
    *,
    groq_key: str,
    pagespeed_key: str | None = None,
    allow_private: bool = False,
) -> AuditReport:
    """Scrape, measure, and analyze a site, returning the structured report.

    Raises ValueError for an invalid or non-public URL and RuntimeError when an
    upstream service (the target site or Groq) fails.
    """
    url = validate_url(url, allow_private=allow_private)

    log.info("Scraping site metadata and SEO signals")
    seo, tech = scrape_site(url)
    log.info(
        "  HTTPS=%s  status=%s  %sms",
        tech.is_https,
        tech.status_code,
        tech.response_time_ms,
    )

    log.info("Fetching PageSpeed / Lighthouse metrics")
    perf = get_pagespeed_data(url, pagespeed_key)
    log.info("  mobile=%s  desktop=%s", perf.mobile_score, perf.desktop_score)

    log.info("Analyzing with Groq")
    report = analyze_site(
        AuditInput(url=url, seo=seo, performance=perf, technical=tech),
        api_key=groq_key,
    )
    log.info("  score=%s  %s", report.overall_score, report.company_name)
    return report


def safe_filename(url: str) -> str:
    netloc = urlparse(normalize_url(url)).netloc
    domain = netloc.replace("www.", "").replace(":", "_").replace(".", "_")
    return f"audit_{domain or 'site'}.pdf"
