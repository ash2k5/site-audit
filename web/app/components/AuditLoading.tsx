import { Loader2 } from "lucide-react";
import { displayUrl } from "../lib/format";

export default function AuditLoading({ url }: { url: string }) {
  return (
    <div
      aria-live="polite"
      className="flex max-w-2xl flex-col gap-3 border border-outline-variant bg-surface-container px-6 py-8"
    >
      <div className="flex items-center gap-3 text-on-surface">
        <Loader2 className="size-5 animate-spin text-primary" aria-hidden />
        <span className="font-display ds-headline-md">
          Auditing {displayUrl(url)}
        </span>
      </div>
      <p className="ds-body-sm text-on-surface-variant">
        Scraping the page, measuring Core Web Vitals, and analyzing with the
        model. This usually takes 30 to 60 seconds.
      </p>
    </div>
  );
}
