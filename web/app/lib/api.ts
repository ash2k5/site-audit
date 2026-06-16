import type { components } from "./schema";

export type AuditReport = components["schemas"]["AuditReport"];
export type CategoryScore = components["schemas"]["CategoryScore"];
export type Recommendation = components["schemas"]["Recommendation"];
export type CoreWebVitals = components["schemas"]["CoreWebVitals"];
export type PerformanceData = components["schemas"]["PerformanceData"];
export type TechnicalData = components["schemas"]["TechnicalData"];
export type AuditInput = components["schemas"]["AuditInput"];

export const API_BASE_URL = (
  process.env.API_BASE_URL ?? "https://site-audit-vil4.onrender.com"
).replace(/\/+$/, "");

// Audits scrape, hit PageSpeed, and call an LLM, so a single request can run
// close to a minute. The platform function timeout is the real ceiling.
const AUDIT_TIMEOUT_MS = 120_000;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function authHeaders(): Record<string, string> {
  const key = process.env.AUDIT_API_KEY;
  return key ? { "x-api-key": key } : {};
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
      headers: authHeaders(),
      cache: "no-store",
      signal: AbortSignal.timeout(AUDIT_TIMEOUT_MS),
    },
  );
  if (!res.ok) {
    throw new ApiError(res.status, await detailFrom(res, `Audit failed (${res.status})`));
  }
  return res.json() as Promise<AuditReport>;
}
