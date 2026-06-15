# Site Audit API

The backend half of the [Site Audit](../README.md) monorepo: a typed JSON API (plus a
CLI) that audits any website for SEO, performance, technical health, and content. It
scrapes the page, pulls real Google PageSpeed metrics, has a Groq LLM turn the data
into graded findings and recommendations, and can render the result as a PDF.

Pipeline: validate URL → scrape (requests + BeautifulSoup) and PageSpeed
(Google) → Groq structured analysis → Jinja2 + Playwright PDF.

## Requirements

- Python 3.10+
- A free [Groq API key](https://console.groq.com)
- Optional: a [Google PageSpeed key](https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com) (raises the request quota)

## Setup

```bash
uv venv && uv pip install -e ".[dev]"
uv run playwright install chromium
cp .env.example .env            # then add your GROQ_API_KEY
```

Plain pip works too: `pip install -e ".[dev]"` inside an activated venv.

## CLI

```bash
site-audit example.com
site-audit https://acme.com -o acme.pdf --no-screenshot
```

`--allow-private` permits localhost. The PDF path prints to stdout, progress to stderr.

## API

```bash
uv run uvicorn site_audit.web:app --reload
```

- `GET /api/audit?url=` returns the audit as typed JSON (the response model).
- `POST /audit` (form field `url`) returns the audit as a PDF.
- `GET /healthz` and `GET /` (service descriptor); interactive docs at `/docs`.

The response schema is published at `/openapi.json`; the frontend generates its
typed client from it. Non-public hosts are refused (SSRF guard), and requests are
rate-limited per IP with a daily ceiling and an optional `AUDIT_API_KEY`.

## Docker

```bash
docker build -t site-audit .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key site-audit
```

## Deploy (Render)

`render.yaml` at the repo root defines a free Docker web service with `rootDir: api`.
Create a Render Blueprint from the repo, set `GROQ_API_KEY` in the dashboard (never
commit it), and Render builds from `api/` and health-checks `/healthz`.

## Test

```bash
uv run pytest          # offline; all network is mocked
uv run ruff check .
```

## License

[MIT](../LICENSE)
