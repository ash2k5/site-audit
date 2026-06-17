# Site Audit API

The backend for [Site Audit](../README.md): a JSON API and a CLI that audit a website for
SEO, performance, technical health, and content. It scrapes the page, pulls Google PageSpeed
metrics, has a Groq LLM grade the findings, and can render the result as a PDF.

## Setup

```bash
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env   # add your GROQ_API_KEY
```

Needs Python 3.10+ and a free [Groq key](https://console.groq.com). A
[PageSpeed key](https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com)
is optional and raises the request quota.

## CLI

```bash
site-audit example.com
site-audit https://acme.com -o acme.pdf --no-screenshot
```

`--allow-private` permits localhost. The PDF path prints to stdout, progress to stderr.

## API

```bash
uvicorn site_audit.web:app --reload
```

- `GET /api/audit?url=` returns the audit as typed JSON.
- `POST /audit` (form field `url`) returns the audit as a PDF.
- `GET /healthz` and `GET /`; interactive docs at `/docs`, schema at `/openapi.json`.

Non-public hosts are refused (SSRF guard) and requests are rate-limited per IP.

## Tests

```bash
pytest
ruff check .
```
