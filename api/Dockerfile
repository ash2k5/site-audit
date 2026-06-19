# Slim Python base plus Chromium only. The full Playwright image bundles three
# browsers; this app launches Chromium alone (PDF rendering), so installing just
# Chromium shrinks the image and the Render cold start. The pin must match the
# playwright client below so the browser and client agree.
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY pyproject.toml README.md ./
COPY site_audit ./site_audit
RUN pip install --no-cache-dir "playwright==1.60.0" . \
    && playwright install --with-deps chromium

ENV PLAYWRIGHT_NO_SANDBOX=1
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn site_audit.web:app --host 0.0.0.0 --port ${PORT:-8000}"]
