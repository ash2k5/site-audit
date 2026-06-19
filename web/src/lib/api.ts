import type { components } from "./schema";
import { normalizeUrl } from "./format";

export type AuditReport = components["schemas"]["AuditReport"];
export type CategoryScore = components["schemas"]["CategoryScore"];
export type Recommendation = components["schemas"]["Recommendation"];
export type CoreWebVitals = components["schemas"]["CoreWebVitals"];
export type PerformanceData = components["schemas"]["PerformanceData"];
export type TechnicalData = components["schemas"]["TechnicalData"];
export type AuditInput = components["schemas"]["AuditInput"];

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://site-audit-vil4.onrender.com"
).replace(/\/+$/, "");

// A cold backend plus the scrape, PageSpeed, and LLM steps can run well past a
// minute. The browser calls the API directly, so this is the only ceiling (no
// serverless function timeout in the way).
const AUDIT_TIMEOUT_MS = 150_000;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// The Render dyno sleeps after ~15 min idle and takes 30-60s to cold start.
// Pinging /healthz on page load wakes it while the user reads and types, so the
// cold start is off the audit's critical path. Best-effort: resolves true once
// the backend answers, false if it stays unreachable within the window.
export async function wakeBackend(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/healthz`, {
      cache: "no-store",
      signal: AbortSignal.timeout(90_000),
    });
    return res.ok;
  } catch {
    return false;
  }
}

async function detailFrom(res: Response, fallback: string): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail) return body.detail;
  } catch {
    // Non-JSON or empty error body; fall through to the generic message.
  }
  return fallback;
}

export async function runAuditReport(url: string): Promise<AuditReport> {
  const res = await fetch(
    `${API_BASE_URL}/api/audit?url=${encodeURIComponent(url)}`,
    {
      cache: "no-store",
      signal: AbortSignal.timeout(AUDIT_TIMEOUT_MS),
    },
  );
  if (!res.ok) {
    throw new ApiError(res.status, await detailFrom(res, `Audit failed (${res.status})`));
  }
  return res.json() as Promise<AuditReport>;
}

export type AuditResult =
  | { ok: true; report: AuditReport }
  | { ok: false; error: string };

export async function runAudit(rawUrl: string): Promise<AuditResult> {
  const url = normalizeUrl(rawUrl);
  if (!url) return { ok: false, error: "Enter a URL to audit." };
  try {
    return { ok: true, report: await runAuditReport(url) };
  } catch (err) {
    if (err instanceof ApiError) return { ok: false, error: err.message };
    if (err instanceof Error && err.name === "TimeoutError") {
      return { ok: false, error: "The audit took too long. Try again in a moment." };
    }
    return { ok: false, error: "Could not reach the audit service. Try again." };
  }
}

export async function fetchAuditPdf(
  rawUrl: string,
): Promise<{ blob: Blob; filename: string }> {
  const url = normalizeUrl(rawUrl);
  const res = await fetch(`${API_BASE_URL}/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ url }).toString(),
    cache: "no-store",
    signal: AbortSignal.timeout(AUDIT_TIMEOUT_MS),
  });
  if (!res.ok) {
    throw new ApiError(res.status, `PDF request failed (${res.status})`);
  }
  const filename =
    res.headers
      .get("content-disposition")
      ?.match(/filename="?([^";]+)"?/)?.[1] ?? "site-audit.pdf";
  return { blob: await res.blob(), filename };
}
