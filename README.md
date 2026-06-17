# site audit

give it a url and it scrapes the page, pulls google pagespeed metrics, and has an llm
score seo, performance, technical health, and content into a report. read it in the
browser or download a pdf.

https://site-audit-web-ecru.vercel.app

## run locally

a python api (`api/`) and a next.js frontend (`web/`).

api, on http://localhost:8000:

```bash
cd api
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env   # add your GROQ_API_KEY (free from console.groq.com)
uvicorn site_audit.web:app --reload
```

the cli renders a pdf straight to disk:

```bash
cd api && site-audit https://example.com
```

web, on http://localhost:3000 (point `NEXT_PUBLIC_API_BASE_URL` at your local api):

```bash
cd web
npm install
cp .env.example .env
npm run dev
```

## tests

```bash
cd api && pytest
cd web && npm test
```
