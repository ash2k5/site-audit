# Changelog

## 2026-06-12

Reworked the project into a monorepo (`api/` here + a `web/` Next.js frontend) and
turned the API into a typed JSON service:

- The audit models are now Pydantic, so `/api/audit` returns a fully typed response
  and the OpenAPI schema describes every field (the frontend generates its client
  from it). The inline HTML form was removed; `/` returns a small service descriptor.
- The PDF report was redesigned on the Cinematic Editorial design system: light print
  theme, Bodoni display headings, Inter body, tabular figures, sharp edges, and
  semantic colors from the shared tokens.

Hardened the public web service ahead of deploy:

- SSRF guard now re-validates every fetch and redirect hop and pins each
  connection to its resolved IP, closing the redirect-bypass and DNS-rebinding
  gaps. The hosted PDF no longer takes a live page screenshot.
- Added per-IP rate limiting, a concurrent-audit cap, a daily audit ceiling,
  request-size and URL-length limits.
- Scraped content is truncated and framed as untrusted in the LLM prompt; the
  Groq client has an explicit timeout; a malformed model response fails closed.
- Client-facing errors are generic; full detail stays in server logs.
- CI runs mypy and pip-audit. Default branch is now `main`.

## 2026-06-05

Packaged the original audit script into the `site_audit` package with a CLI and a
FastAPI web service, plus a pytest suite and Docker/Render deploy. The hosted
service refuses non-public hosts (SSRF guard), and previously committed API keys
were removed from the tree and git history.
