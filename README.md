# AI Site Audit Generator

Generate a PDF audit of any website (SEO, performance, technical, content) for
sales outreach. It scrapes the page, pulls real Google PageSpeed metrics, has a
Groq LLM turn the data into graded findings and recommendations, and renders a
PDF. Runs as a CLI or a small web service.

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

## Web service

```bash
uv run uvicorn site_audit.web:app --reload
```

`GET /` form · `POST /audit` returns the PDF · `GET /api/audit?url=` returns JSON ·
`GET /healthz`. Non-public hosts are refused (SSRF guard), and requests are
rate-limited per IP.

## Docker

```bash
docker build -t site-audit .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key site-audit
```

## Test

```bash
uv run pytest          # offline; all network is mocked
uv run ruff check .
```

## License

[MIT](LICENSE)
