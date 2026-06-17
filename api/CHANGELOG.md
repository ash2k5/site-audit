# changelog

## unreleased

- split into a monorepo: this python api plus a next.js frontend in `web/`.
- the api returns typed json now (pydantic models + openapi schema); the old inline
  html form is gone.
- redesigned the pdf report on the cinematic-ds design system.
- added the web frontend: enter a url and the scored report renders in the browser,
  with a one-click pdf download.
- enabled cors (via `ALLOWED_ORIGINS`) so the browser can call the audit directly.

## 2026-06-12

- ssrf guard re-validates every fetch and redirect hop and pins each connection to its
  resolved ip; the hosted pdf no longer takes a live screenshot.
- added per-ip rate limiting, a concurrent-audit cap, a daily ceiling, and request-size
  and url-length limits.
- scraped content is truncated and framed as untrusted in the llm prompt; the groq
  client has a timeout and a malformed response fails closed.
- client-facing errors are generic; full detail stays in the logs.

## 2026-06-05

- packaged the audit script into the `site_audit` package with a cli, a fastapi service,
  tests, and docker config.
