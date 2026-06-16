import { API_BASE_URL, authHeaders } from "../../lib/api";
import { normalizeUrl } from "../../lib/format";

// PDF generation reruns the full audit and renders Chromium, so it needs the
// long ceiling. Capped at 60s on Vercel Hobby; raise on a paid plan.
export const maxDuration = 60;

export async function POST(req: Request): Promise<Response> {
  let url = "";
  try {
    const body = (await req.json()) as { url?: unknown };
    if (typeof body.url === "string") url = normalizeUrl(body.url);
  } catch {
    // Malformed JSON body falls through to the missing-url guard.
  }
  if (!url) return new Response("Missing url", { status: 400 });

  let upstream: Response;
  try {
    upstream = await fetch(`${API_BASE_URL}/audit`, {
      method: "POST",
      headers: {
        ...authHeaders(),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ url }).toString(),
      cache: "no-store",
      signal: AbortSignal.timeout(120_000),
    });
  } catch {
    return new Response("Could not reach the audit service.", { status: 502 });
  }

  if (!upstream.ok || !upstream.body) {
    return new Response("PDF generation failed.", { status: 502 });
  }

  const filename =
    upstream.headers
      .get("content-disposition")
      ?.match(/filename="?([^";]+)"?/)?.[1] ?? "site-audit.pdf";

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
      "Cache-Control": "no-store",
    },
  });
}
