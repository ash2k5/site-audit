import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from models import SEOData, TechnicalData

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

CTA_KEYWORDS = [
    "get started", "book", "schedule", "contact us", "free trial",
    "sign up", "request", "demo", "buy now", "learn more", "get a quote",
    "try for free", "start now", "call us",
]

CONTACT_KEYWORDS = ["tel:", "mailto:", "phone", "email", "contact"]


def scrape_site(url: str) -> tuple[SEOData, TechnicalData]:
    if not urlparse(url).scheme:
        url = "https://" + url

    resp, response_time = _fetch_page(url)
    final_url = resp.url

    tech = TechnicalData(
        status_code=resp.status_code,
        is_https=final_url.startswith("https://"),
        final_url=final_url,
        redirect_count=len(resp.history),
        response_time_ms=round(response_time, 1),
        has_robots_txt=_check_url(final_url, "/robots.txt"),
        has_sitemap=_check_url(final_url, "/sitemap.xml"),
    )

    soup = BeautifulSoup(resp.text, "html.parser")
    return _extract_seo(soup, final_url), tech


def _fetch_page(url: str) -> tuple[requests.Response, float]:
    for attempt in range(3):
        try:
            t0 = time.time()
            resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            return resp, (time.time() - t0) * 1000
        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f"Failed to fetch {url}: {e}")
            time.sleep(attempt + 1)
    raise RuntimeError(f"Failed to fetch {url}")


def _extract_seo(soup: BeautifulSoup, base_url: str) -> SEOData:
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    canonical = ""
    canon_tag = soup.find("link", rel="canonical")
    if canon_tag:
        canonical = canon_tag.get("href", "")

    h1_tags = [t.get_text(strip=True) for t in soup.find_all("h1")]
    h2_tags = [t.get_text(strip=True) for t in soup.find_all("h2")]

    images = soup.find_all("img")
    missing_alt = sum(1 for img in images if not img.get("alt", "").strip())

    parsed_base = urlparse(base_url)
    internal = external = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("javascript"):
            continue
        full = urljoin(base_url, href)
        if urlparse(full).netloc == parsed_base.netloc:
            internal += 1
        else:
            external += 1

    body_text = soup.get_text(separator=" ", strip=True)
    body_lower = body_text.lower()

    return SEOData(
        title=title,
        meta_description=meta_desc,
        h1_tags=h1_tags,
        h2_tags=h2_tags,
        canonical_url=canonical,
        og_title=_meta_content(soup, "og:title"),
        og_description=_meta_content(soup, "og:description"),
        has_schema_markup=bool(soup.find("script", type="application/ld+json")),
        images_missing_alt=missing_alt,
        total_images=len(images),
        internal_links=internal,
        external_links=external,
        word_count=len(body_text.split()),
        has_cta=any(kw in body_lower for kw in CTA_KEYWORDS),
        has_contact_info=any(kw in body_lower for kw in CONTACT_KEYWORDS),
    )


def _meta_content(soup: BeautifulSoup, property_name: str) -> str:
    tag = soup.find("meta", property=property_name)
    return tag.get("content", "") if tag else ""


def _check_url(base_url: str, path: str) -> bool:
    parsed = urlparse(base_url)
    try:
        r = requests.head(
            f"{parsed.scheme}://{parsed.netloc}{path}",
            headers=HEADERS, timeout=5, allow_redirects=True,
        )
        return r.status_code < 400
    except requests.RequestException:
        return False
