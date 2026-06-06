# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-06-05

### Added
- `site_audit` package with a reusable `build_report` orchestration, a CLI, and a
  FastAPI web service (`/`, `POST /audit`, `GET /api/audit`, `/healthz`).
- SSRF guard that refuses to audit non-public hosts in the hosted service.
- pytest suite covering URL validation, scraping, PageSpeed parsing, LLM mapping,
  PDF rendering, and the web endpoints.
- Dockerfile, Render blueprint, and GitHub Actions CI (lint and test).
- MIT license.

### Changed
- Restructured the flat module layout into the `site_audit` package.
- API keys are injected explicitly instead of being read from globals deep in the
  call stack; library modules log instead of printing to stdout.
- Jinja rendering now autoescapes report data.

### Security
- Removed committed API keys from the tree and purged them from git history;
  `.env` is now ignored.
