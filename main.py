import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

from analyzer import analyze_site
from models import AuditInput
from pagespeed import get_pagespeed_data
from pdf_generator import generate_pdf
from scraper import scrape_site


def normalise_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def safe_filename(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "").replace(".", "_")
    return f"audit_{domain}.pdf"


def run_audit(url: str, output_path: str, skip_screenshot: bool = False) -> None:
    url = normalise_url(url)

    print(f"\n  Site Audit: {url}\n")

    print("[1/4] Scraping site metadata and SEO signals...")
    seo_data, tech_data = scrape_site(url)
    print(f"      Title: {seo_data.title[:60] or '(none)'}  |  HTTPS: {tech_data.is_https}  |  {tech_data.response_time_ms}ms")

    print("[2/4] Fetching PageSpeed / Lighthouse metrics...")
    perf_data = get_pagespeed_data(url, os.getenv("PAGESPEED_API_KEY"))
    print(f"      Mobile: {perf_data.mobile_score}/100  |  Desktop: {perf_data.desktop_score}/100")

    print("[3/4] Analysing with AI...")
    report = analyze_site(AuditInput(url=url, seo=seo_data, performance=perf_data, technical=tech_data))
    print(f"      Score: {report.overall_score}/100  |  {report.company_name}")

    print("[4/4] Generating PDF report...")
    generate_pdf(report, output_path, skip_screenshot=skip_screenshot)

    print(f"\n  Done. Report saved to: {Path(output_path).resolve()}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Site Audit Generator — produce a PDF audit from a URL"
    )
    parser.add_argument("url", help="Website URL to audit (e.g. example.com)")
    parser.add_argument("-o", "--output", help="Output PDF path (default: audit_<domain>.pdf)", default=None)
    parser.add_argument("--no-screenshot", action="store_true", help="Skip screenshot capture")
    args = parser.parse_args()

    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY is not set. Add it to your .env file.")
        sys.exit(1)

    run_audit(args.url, args.output or safe_filename(args.url), skip_screenshot=args.no_screenshot)


if __name__ == "__main__":
    main()
