# Changelog

## 1.0.0 - 2026-06-05

Packaged the original audit script into the `site_audit` package with a CLI and a
FastAPI web service, plus a pytest suite and Docker/Render deploy. The hosted
service refuses non-public hosts (SSRF guard), and previously committed API keys
were removed from the tree and git history.
