# Site Audit

Give it a URL and it scrapes the page, pulls Google PageSpeed metrics, and has an LLM score
SEO, performance, technical health, and content into a report. Read it in the browser or
download a PDF.

https://webaudit.ask2k5.com

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

## Run with Docker

Runs the whole app in containers, Chromium included (Docker Desktop must be running). Put your `GROQ_API_KEY` in `api/.env` first.

```bash
docker compose up --build
```

Production build:

```bash
docker compose -f compose.prod.yaml up --build
```

## Tests

```bash
cd api && pytest
cd web && npm test
```
