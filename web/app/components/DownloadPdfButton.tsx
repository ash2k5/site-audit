"use client";

import { useState } from "react";
import { Download } from "lucide-react";
import { Button } from "@ash2k5/cinematic-ds";
import { displayUrl } from "../lib/format";

export default function DownloadPdfButton({ url }: { url: string }) {
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);

  async function onDownload() {
    setLoading(true);
    setFailed(false);
    try {
      const res = await fetch("/api/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error(`PDF request failed (${res.status})`);
      const blob = await res.blob();
      const href = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = href;
      anchor.download = `${displayUrl(url).replace(/[^a-z0-9.-]+/gi, "_")}-audit.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(href);
    } catch {
      setFailed(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <Button variant="ghost" onClick={onDownload} loading={loading}>
        {!loading && <Download className="size-[14px]" aria-hidden />}
        {loading ? "Preparing" : "Download PDF"}
      </Button>
      <span className="ds-label-sm text-on-surface-variant">
        {failed ? (
          <span className="text-error">PDF failed — try again</span>
        ) : (
          "Reruns the audit (~1 min)"
        )}
      </span>
    </div>
  );
}
