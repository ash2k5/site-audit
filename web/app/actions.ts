"use server";

import { ApiError, runAuditReport, type AuditReport } from "./lib/api";
import { normalizeUrl } from "./lib/format";

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
