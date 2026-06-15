import pytest
import requests
from bs4 import BeautifulSoup

from site_audit import scraper
from site_audit.scraper import _extract_seo, scrape_site

SAMPLE_HTML = """<html><head>
<title>Acme Co</title>
<meta name="description" content="We build things">
<link rel="canonical" href="https://acme.com/">
<meta property="og:title" content="Acme">
<meta property="og:description" content="Acme OG">
<script type="application/ld+json">{}</script>
</head><body>
<h1>Welcome</h1><h2>Services</h2><h2>About</h2>
<img src="a.png" alt="logo"><img src="b.png">
<a href="/internal">in</a><a href="https://other.com">out</a>
<a href="#frag">frag</a><a href="javascript:void(0)">js</a>
<p>Get started today. Contact us at mailto:x@y.com. Plenty of words here now.</p>
</body></html>"""


def test_extract_seo():
    soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
    seo = _extract_seo(soup, "https://acme.com")
    assert seo.title == "Acme Co"
    assert seo.meta_description == "We build things"
    assert seo.canonical_url == "https://acme.com/"
    assert seo.og_title == "Acme"
    assert seo.h1_tags == ["Welcome"]
    assert seo.h2_tags == ["Services", "About"]
    assert seo.total_images == 2
    assert seo.images_missing_alt == 1
    assert seo.internal_links == 1
    assert seo.external_links == 1
    assert seo.has_schema_markup is True
    assert seo.has_cta is True
    assert seo.has_contact_info is True
    assert seo.word_count > 0


class FakeResp:
    def __init__(self, text="", url="https://acme.com", status=200, history=()):
        self.text = text
        self.url = url
        self.status_code = status
        self.history = list(history)


def test_scrape_site(monkeypatch):
    monkeypatch.setattr(scraper, "_fetch_page", lambda url: (FakeResp(SAMPLE_HTML), 120.0))
    monkeypatch.setattr(scraper, "_check_url", lambda base, path: True)
    seo, tech = scrape_site("acme.com")
    assert tech.status_code == 200
    assert tech.is_https is True
    assert tech.response_time_ms == 120.0
    assert tech.has_robots_txt is True
    assert seo.title == "Acme Co"


def test_fetch_page_failure(monkeypatch):
    def boom(*a, **k):
        raise requests.RequestException("down")

    monkeypatch.setattr(scraper.safe_http, "safe_request", boom)
    monkeypatch.setattr(scraper.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError):
        scraper._fetch_page("https://acme.com")


def test_fetch_page_ssrf_propagates(monkeypatch):
    def refuse(*a, **k):
        raise ValueError("Refusing to fetch non-public address")

    monkeypatch.setattr(scraper.safe_http, "safe_request", refuse)
    monkeypatch.setattr(scraper.time, "sleep", lambda s: None)
    with pytest.raises(ValueError):
        scraper._fetch_page("https://acme.com")


def test_check_url_swallows_ssrf(monkeypatch):
    def refuse(*a, **k):
        raise ValueError("Refusing to fetch non-public address")

    monkeypatch.setattr(scraper.safe_http, "safe_request", refuse)
    assert scraper._check_url("https://acme.com", "/robots.txt") is False
