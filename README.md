# Site Audit

Give it a URL and it scrapes the page, pulls Google PageSpeed metrics, and has an LLM score
SEO, performance, technical health, and content into a report. Read it in the browser or
download a PDF.

https://site-audit-web-ecru.vercel.app

## Run locally

A Python API (`api/`) and a Next.js frontend (`web/`).

API, on http://localhost:8000:

```bash
cd api
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env   # add your GROQ_API_KEY (free from console.groq.com)
uvicorn site_audit.web:app --reload
```

The CLI renders a PDF straight to disk:

```bash
cd api && site-audit https://example.com
```

Web, on http://localhost:3000 (point `NEXT_PUBLIC_API_BASE_URL` at your local API):

```bash
cd web
npm install
cp .env.example .env
npm run dev
```

## Tests

```bash
cd api && pytest
cd web && npm test
```
