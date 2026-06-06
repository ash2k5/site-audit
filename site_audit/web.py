import logging
import os
import tempfile
import threading
from dataclasses import asdict

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask

from . import __version__
from .audit import build_report, safe_filename
from .models import AuditReport
from .pdf_generator import generate_pdf

log = logging.getLogger("site_audit")

app = FastAPI(title="AI Site Audit Generator", version=__version__)

# Chromium is memory hungry; serialize PDF rendering to survive small instances.
_pdf_lock = threading.Semaphore(1)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _FORM_HTML


@app.get("/api/audit")
def api_audit(url: str) -> dict:
    return asdict(_build(url))


@app.post("/audit")
def audit(url: str = Form(...)) -> FileResponse:
    report = _build(url)
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    try:
        with _pdf_lock:
            generate_pdf(report, tmp.name, skip_screenshot=False)
    except Exception as e:
        os.unlink(tmp.name)
        log.exception("PDF generation failed")
        raise HTTPException(status_code=502, detail=f"PDF generation failed: {e}") from e
    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename=safe_filename(report.url),
        background=BackgroundTask(os.unlink, tmp.name),
    )


def _build(url: str) -> AuditReport:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise HTTPException(status_code=503, detail="Server is missing GROQ_API_KEY")
    try:
        return build_report(url, groq_key=groq_key, pagespeed_key=os.getenv("PAGESPEED_API_KEY"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


_FORM_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Site Audit Generator</title>
<style>
  body { font-family: system-ui, -apple-system, Segoe UI, Arial, sans-serif;
         background: #0f172a; color: #e2e8f0; display: flex; min-height: 100vh;
         margin: 0; align-items: center; justify-content: center; }
  main { max-width: 520px; padding: 40px; }
  h1 { font-size: 28px; margin: 0 0 12px; }
  p { line-height: 1.6; color: #94a3b8; }
  form { display: flex; gap: 10px; margin: 24px 0 10px; flex-wrap: wrap; }
  input { flex: 1; min-width: 220px; padding: 12px 14px; border-radius: 8px;
          border: 1px solid #334155; background: #1e293b; color: #e2e8f0; font-size: 15px; }
  button { padding: 12px 20px; border: 0; border-radius: 8px; background: #0ea5e9;
           color: white; font-size: 15px; font-weight: 600; cursor: pointer; }
  .hint { font-size: 13px; }
</style>
</head>
<body>
<main>
  <h1>AI Site Audit Generator</h1>
  <p>Enter a website URL to generate a PDF audit covering SEO, performance,
     technical health, and content. It runs a live PageSpeed and AI analysis,
     so it can take up to a minute.</p>
  <form method="post" action="/audit">
    <input type="url" name="url" placeholder="https://example.com" required>
    <button type="submit">Generate audit</button>
  </form>
  <p class="hint">The PDF downloads when the analysis finishes. Keep this tab open.</p>
</main>
</body>
</html>
"""
