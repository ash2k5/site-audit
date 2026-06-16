import { Check, X } from "lucide-react";
import type { TechnicalData } from "../lib/api";

function Flag({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center gap-2 ds-body-sm text-on-surface">
      {ok ? (
        <Check className="size-4 text-success" aria-hidden />
      ) : (
        <X className="size-4 text-error" aria-hidden />
      )}
      <span>{label}</span>
      <span className="sr-only">{ok ? "present" : "missing"}</span>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 ds-body-sm text-on-surface">
      <span className="text-on-surface-variant">{label}</span>
      <span className="tabular-nums">{value}</span>
    </div>
  );
}

export default function TechnicalSignals({
  technical,
}: {
  technical: TechnicalData;
}) {
  const redirects = technical.redirect_count ?? 0;
  return (
    <div className="flex flex-wrap gap-x-8 gap-y-3 border-t border-outline-variant pt-6">
      <Flag label="HTTPS" ok={technical.is_https ?? false} />
      <Flag label="robots.txt" ok={technical.has_robots_txt ?? false} />
      <Flag label="sitemap.xml" ok={technical.has_sitemap ?? false} />
      {technical.status_code != null && (
        <Fact label="Status" value={String(technical.status_code)} />
      )}
      {technical.response_time_ms != null && (
        <Fact
          label="Response"
          value={`${Math.round(technical.response_time_ms)} ms`}
        />
      )}
      {redirects > 0 && <Fact label="Redirects" value={String(redirects)} />}
    </div>
  );
}
