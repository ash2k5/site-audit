# site audit api

the backend for [site audit](../README.md): a json api and a cli that audit a website
for seo, performance, technical health, and content. it scrapes the page, pulls google
pagespeed metrics, has a groq llm grade the findings, and can render the result as a pdf.

## setup

```bash
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env   # add your GROQ_API_KEY
```

needs python 3.10+ and a free [groq key](https://console.groq.com). a
[pagespeed key](https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com)
is optional and raises the request quota.

## cli

```bash
site-audit example.com
site-audit https://acme.com -o acme.pdf --no-screenshot
```

`--allow-private` permits localhost. the pdf path prints to stdout, progress to stderr.

## api

```bash
uvicorn site_audit.web:app --reload
```

- `GET /api/audit?url=` returns the audit as typed json.
- `POST /audit` (form field `url`) returns the audit as a pdf.
- `GET /healthz` and `GET /`; interactive docs at `/docs`, schema at `/openapi.json`.

non-public hosts are refused (ssrf guard) and requests are rate-limited per ip.

## tests

```bash
pytest
ruff check .
```
