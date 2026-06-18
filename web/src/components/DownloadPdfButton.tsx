"use client";

import { useState } from "react";
import { Download } from "lucide-react";
import { Button } from "@ash2k5/ui";
import { fetchAuditPdf } from "../lib/api";

export default function DownloadPdfButton({ url }: { url: string }) {
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);

  async function onDownload() {
    setLoading(true);
    setFailed(false);
    try {
      const { blob, filename } = await fetchAuditPdf(url);
      const href = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = href;
      anchor.download = filename;
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
