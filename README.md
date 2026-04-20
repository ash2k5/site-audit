# AI Site Audit Generator

Generates a structured PDF audit report from a website URL in under 60 seconds. Designed for sales outreach.

> **Test keys included.** This repo ships with a working `.env` for evaluation. For your own deployment, replace the keys with your own.

## Requirements

- Python 3.10+
- [Groq API key](https://console.groq.com) (free tier sufficient)
- [Google PageSpeed API key](https://developers.google.com/speed/docs/insights/v5/get-started) (optional — raises daily quota from 400 to 25,000 requests)

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```
python main.py <url> [-o output.pdf] [--no-screenshot]
```

**Examples**
```bash
python main.py example.com
python main.py https://acme.com -o acme_audit.pdf
python main.py example.com --no-screenshot
```

Output defaults to `audit_<domain>.pdf` in the current directory.

## Report Contents

- Cover page: overall score and per-category grades
- Homepage screenshot
- Per-category findings: SEO, Performance, Technical, Content
- Core Web Vitals (LCP, CLS, FCP, TTFB)
- Quick wins and prioritised recommendations table

## Project Structure

```
site_audit/
├── main.py            # CLI entry point
├── scraper.py         # HTML/SEO extraction via requests + BeautifulSoup
├── pagespeed.py       # Google PageSpeed Insights API (Core Web Vitals)
├── analyzer.py        # Groq API — structured audit analysis
├── pdf_generator.py   # Jinja2 template + Playwright PDF rendering
├── models.py          # Shared dataclasses
├── requirements.txt
├── .env               # API keys (test keys included)
└── templates/
    └── report.html    # PDF report template
```
