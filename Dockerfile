# Playwright's image bundles Chromium and its system dependencies. The tag must
# match the pinned playwright version below so the browser and client agree.
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

WORKDIR /app

COPY pyproject.toml README.md ./
COPY site_audit ./site_audit
RUN pip install --no-cache-dir "playwright==1.60.0" .

ENV PLAYWRIGHT_NO_SANDBOX=1
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn site_audit.web:app --host 0.0.0.0 --port ${PORT:-8000}"]
