import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ApiError, runAuditReport, wakeBackend } from "../src/lib/api";

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("runAuditReport", () => {
  test("encodes the url into the query and returns the parsed report", async () => {
    const report = { url: "https://x.com", overall_score: 72 };
    fetchMock.mockResolvedValue({ ok: true, json: async () => report });

    const result = await runAuditReport("https://x.com/a b");

    expect(String(fetchMock.mock.calls[0][0])).toContain(
      "/api/audit?url=https%3A%2F%2Fx.com%2Fa%20b",
    );
    expect(result).toEqual(report);
  });

  test("throws ApiError carrying the server detail", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Refusing to fetch a private address" }),
    });

    await expect(runAuditReport("https://x.com")).rejects.toMatchObject({
      status: 400,
      message: "Refusing to fetch a private address",
    });
  });

  test("falls back to a generic message when the error body has no detail", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error("not json");
      },
    });

    const err = await runAuditReport("https://x.com").catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(502);
    expect(err.message).toBe("Audit failed (502)");
  });
});

describe("wakeBackend", () => {
  test("pings /healthz and resolves true when the backend answers", async () => {
    fetchMock.mockResolvedValue({ ok: true });

    const ok = await wakeBackend();

    expect(String(fetchMock.mock.calls[0][0])).toContain("/healthz");
    expect(ok).toBe(true);
  });

  test("resolves false when the backend responds not-ok", async () => {
    fetchMock.mockResolvedValue({ ok: false });
    expect(await wakeBackend()).toBe(false);
  });

  test("resolves false when the backend is unreachable", async () => {
    fetchMock.mockRejectedValue(new Error("network down"));
    expect(await wakeBackend()).toBe(false);
  });
});
