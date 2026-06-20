# 1. split api/ and web/, deploy independently

- Status: accepted
- Date: 2026-06-20

## Context
The audit engine is Python (FastAPI + Playwright + Groq); the UI is Next.js. They have different
runtimes and scaling needs.

## Decision
One repo, two deployables: `api/` to Render (`render.yaml`, `rootDir: api`) and `web/` to Vercel
(Root Directory `web`). CI is path-filtered (`api/**`, `web/**`). The web API client is typed from the
API's OpenAPI schema (`npm run gen:api`).

## Consequences
Each side deploys on its own cadence. An API contract change means regenerating the web types.
Cross-cutting changes touch both halves.
