# Site Audit

Generate a structured website audit from a URL: SEO, performance (PageSpeed / Core Web
Vitals), technical health, and content, scored and analyzed by an LLM into a prioritized
action plan and a polished PDF.

- **Web app:** https://site-audit-web-ecru.vercel.app — Next.js frontend on `@ash2k5/cinematic-ds`
- **API:** https://site-audit-vil4.onrender.com — [OpenAPI schema](https://site-audit-vil4.onrender.com/openapi.json)

## What it does

Give it a URL and it scrapes the page (SSRF-guarded), pulls Google PageSpeed metrics,
and sends the signals to a Groq-hosted LLM that returns category scores (SEO,
performance, technical, content), an executive summary, quick wins, and ranked
recommendations. The result is available as typed JSON or as a print-ready PDF.

## Architecture

```
site-audit/
├── api/   FastAPI JSON API + Playwright PDF rendering   ->  Render (Docker)
└── web/   Next.js App Router frontend on @ash2k5/cinematic-ds  ->  Vercel
```

The two halves deploy independently. The frontend's API client is **typed from the
backend's OpenAPI schema**, so the contract between them is checked at compile time.
The audit runs server-side from a Next route handler / server action, so the API key
stays off the client and there is no CORS round trip.

| | Stack |
|---|---|
| api | Python 3.10+, FastAPI, BeautifulSoup, Groq, Playwright/Jinja2 PDF; pytest + ruff + mypy; Docker on Render |
| web | Next.js (App Router), React, TypeScript, Tailwind v4, the [`@ash2k5/cinematic-ds`](https://github.com/ash2k5/design-system) design system; Vercel |

## Run locally

**API** (http://localhost:8000, `/docs` for Swagger):

```bash
cd api
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env   # add your GROQ_API_KEY
uvicorn site_audit.web:app --reload
```

The CLI renders a PDF directly:

```bash
cd api && site-audit https://example.com
```

**Web** (http://localhost:3000):

```bash
cd web
npm install
cp .env.example .env    # API_BASE_URL defaults to the deployed API
npm run dev
```

`npm run gen:api` regenerates the typed API client from the live OpenAPI schema.

## Tests

```bash
cd api && pytest        # scraper, analyzer, limits, PDF, and API endpoint tests
cd web && npm test      # api client, server action, format helpers, components
```

## License

MIT (`LICENSE`).
