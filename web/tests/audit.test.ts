import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fetchAuditPdf, runAudit } from "../src/lib/api";

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("runAudit", () => {
  test("rejects a blank url without calling the API", async () => {
    expect(await runAudit("  ")).toEqual({
      ok: false,
      error: "Enter a URL to audit.",
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("normalizes a bare host and returns the report", async () => {
    const report = { url: "https://example.com", overall_score: 80 };
    fetchMock.mockResolvedValue({ ok: true, json: async () => report });

    const result = await runAudit("example.com");

    expect(String(fetchMock.mock.calls[0][0])).toContain(
      "/api/audit?url=https%3A%2F%2Fexample.com",
    );
    expect(result).toEqual({ ok: true, report });
  });

  test("surfaces the server detail on an API error", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Refusing to fetch a private address" }),
    });
    expect(await runAudit("example.com")).toEqual({
      ok: false,
      error: "Refusing to fetch a private address",
    });
  });

  test("maps a network failure to a generic message", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
    expect(await runAudit("example.com")).toEqual({
      ok: false,
      error: "Could not reach the audit service. Try again.",
    });
  });

  test("maps a timeout to a friendly message", async () => {
    const timeout = new Error("timed out");
    timeout.name = "TimeoutError";
    fetchMock.mockRejectedValue(timeout);
    expect(await runAudit("example.com")).toEqual({
      ok: false,
      error: "The audit took too long. Try again in a moment.",
    });
  });
});

describe("fetchAuditPdf", () => {
  test("posts the url to /audit and reads the filename header", async () => {
    const blob = new Blob(["%PDF"], { type: "application/pdf" });
    fetchMock.mockResolvedValue({
      ok: true,
      blob: async () => blob,
      headers: {
        get: (h: string) =>
          h.toLowerCase() === "content-disposition"
            ? 'attachment; filename="audit_example_com.pdf"'
            : null,
      },
    });

    const result = await fetchAuditPdf("example.com");
    const [calledUrl, init] = fetchMock.mock.calls[0];

    expect(String(calledUrl)).toContain("/audit");
    expect(init.method).toBe("POST");
    expect(result.filename).toBe("audit_example_com.pdf");
    expect(result.blob).toBe(blob);
  });
});
