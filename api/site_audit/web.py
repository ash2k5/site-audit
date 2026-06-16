import logging
import os
import tempfile
import threading
from contextlib import contextmanager

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.background import BackgroundTask

from . import __version__
from .audit import build_report, safe_filename
from .limits import DailyBudget, RateLimiter, int_env
from .models import AuditReport
from .pdf_generator import generate_pdf

log = logging.getLogger("site_audit")

app = FastAPI(
    title="AI Site Audit Generator",
    version=__version__,
    description="Scrape a URL, measure it, and return an LLM-scored audit as JSON or PDF.",
)

# The browser calls this API directly (the audit runs longer than a serverless
# function may live), so it is a public read API guarded by rate limits, not CORS.
_ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    if _ALLOWED_ORIGINS.strip() == "*"
    else [o.strip() for o in _ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

_API_KEY = os.getenv("AUDIT_API_KEY")
_MAX_BODY_BYTES = int_env("MAX_BODY_BYTES", 16384)

_rate_limiter = RateLimiter(int_env("RATE_LIMIT_PER_MINUTE", 5))
_daily_budget = DailyBudget(int_env("DAILY_AUDIT_LIMIT", 200))
# Cap concurrent audits so a flood is rejected fast instead of queueing until OOM.
_audit_slots = threading.BoundedSemaphore(int_env("MAX_CONCURRENT_AUDITS", 2))
# Chromium is memory hungry; serialize PDF rendering to survive small instances.
_pdf_lock = threading.Semaphore(1)


@app.middleware("http")
async def _limit_body_size(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > _MAX_BODY_BYTES:
        return PlainTextResponse("Request body too large", status_code=413)
    return await call_next(request)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _guard(request: Request) -> None:
    if _API_KEY and request.headers.get("x-api-key") != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    if not _rate_limiter.allow(_client_ip(request)):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")
    if not _daily_budget.allow():
        raise HTTPException(status_code=503, detail="Daily audit limit reached. Try again later.")


@contextmanager
def _audit_slot():
    if not _audit_slots.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Server is busy. Try again shortly.")
    try:
        yield
    finally:
        _audit_slots.release()


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/")
def index() -> dict:
    return {
        "service": "AI Site Audit Generator",
        "version": __version__,
        "docs": "/docs",
        "endpoints": {
            "audit_json": "/api/audit?url=",
            "audit_pdf": "POST /audit (form field: url)",
            "health": "/healthz",
        },
    }


@app.get("/api/audit", dependencies=[Depends(_guard)])
def api_audit(url: str) -> AuditReport:
    with _audit_slot():
        return _build(url)


@app.post("/audit", dependencies=[Depends(_guard)])
def audit(url: str = Form(...)) -> FileResponse:
    with _audit_slot():
        report = _build(url)
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.close()
        try:
            with _pdf_lock:
                # No live screenshot on the public path: Chromium navigation is a
                # second, unpinnable SSRF vector. The CLI keeps the screenshot.
                generate_pdf(report, tmp.name, skip_screenshot=True)
        except Exception as e:
            os.unlink(tmp.name)
            log.exception("PDF generation failed")
            raise HTTPException(status_code=502, detail="PDF generation failed") from e
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
        log.exception("Audit pipeline failed")
        raise HTTPException(status_code=502, detail="Audit failed. Try again later.") from e
