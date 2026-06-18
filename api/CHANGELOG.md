# Changelog

## Unreleased

- Split into a monorepo: this Python API plus a Next.js frontend in `web/`.
- The API returns typed JSON now (Pydantic models + OpenAPI schema); the old inline HTML
  form is gone.
- Redesigned the PDF report on the `@ash2k5/ui` design system.
- Added the web frontend: enter a URL and the scored report renders in the browser, with a
  one-click PDF download.
- Enabled CORS (via `ALLOWED_ORIGINS`) so the browser can call the audit directly.
- Renamed the design system dependency from `@ash2k5/cinematic-ds` to `@ash2k5/ui`.

## 2026-06-12

- The SSRF guard re-validates every fetch and redirect hop and pins each connection to its
  resolved IP; the hosted PDF no longer takes a live screenshot.
- Added per-IP rate limiting, a concurrent-audit cap, a daily ceiling, and request-size and
  URL-length limits.
- Scraped content is truncated and framed as untrusted in the LLM prompt; the Groq client has
  a timeout and a malformed response fails closed.
- Client-facing errors are generic; full detail stays in the logs.

## 2026-06-05

- Packaged the audit script into the `site_audit` package with a CLI, a FastAPI service,
  tests, and Docker config.
