import { beforeEach, describe, expect, test, vi } from "vitest";

const { runAuditReport } = vi.hoisted(() => ({ runAuditReport: vi.fn() }));

vi.mock("../app/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../app/lib/api")>();
  return { ...actual, runAuditReport };
});

import { runAudit } from "../app/actions";
import { ApiError } from "../app/lib/api";

beforeEach(() => {
  runAuditReport.mockReset();
});

describe("runAudit", () => {
  test("rejects a blank url without calling the API", async () => {
    const result = await runAudit("  ");
    expect(result).toEqual({ ok: false, error: "Enter a URL to audit." });
    expect(runAuditReport).not.toHaveBeenCalled();
  });

  test("normalizes a bare host and returns the report", async () => {
    const report = { url: "https://example.com", overall_score: 80 };
    runAuditReport.mockResolvedValue(report);

    const result = await runAudit("example.com");

    expect(runAuditReport).toHaveBeenCalledWith("https://example.com");
    expect(result).toEqual({ ok: true, report });
  });

  test("surfaces an ApiError message to the caller", async () => {
    runAuditReport.mockRejectedValue(new ApiError(400, "Bad URL"));
    expect(await runAudit("example.com")).toEqual({
      ok: false,
      error: "Bad URL",
    });
  });

  test("maps an unexpected error to a generic message", async () => {
    runAuditReport.mockRejectedValue(new Error("boom"));
    expect(await runAudit("example.com")).toEqual({
      ok: false,
      error: "Could not reach the audit service. Try again.",
    });
  });
});
