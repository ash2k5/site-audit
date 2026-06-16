"use client";

import { type FormEvent, useState, useTransition } from "react";
import { Button, Input } from "@ash2k5/cinematic-ds";
import { runAudit } from "../actions";
import type { AuditReport } from "../lib/api";
import AuditLoading from "./AuditLoading";
import AuditReportView from "./AuditReportView";

export default function AuditClient() {
  const [url, setUrl] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [report, setReport] = useState<AuditReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const value = url.trim();
    if (!value || pending) return;
    setSubmitted(value);
    setError(null);
    setReport(null);
    startTransition(async () => {
      const result = await runAudit(value);
      if (result.ok) setReport(result.report);
      else setError(result.error);
    });
  }

  return (
    <div className="flex flex-col gap-12">
      <form onSubmit={onSubmit} className="flex max-w-2xl flex-col gap-3">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Input
              label="Website URL"
              type="text"
              inputMode="url"
              autoComplete="url"
              placeholder="example.com"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              disabled={pending}
              required
            />
          </div>
          <Button type="submit" loading={pending} className="sm:shrink-0">
            {pending ? "Auditing" : "Run audit"}
          </Button>
        </div>
        <p className="ds-body-sm text-on-surface-variant">
          Runs a live scrape, PageSpeed, and an LLM analysis — up to a minute.
        </p>
      </form>

      {pending && <AuditLoading url={submitted} />}
      {!pending && error && (
        <div
          role="alert"
          className="max-w-2xl bg-error-container px-5 py-4 ds-body-md text-error"
        >
          {error}
        </div>
      )}
      {!pending && report && <AuditReportView report={report} />}
    </div>
  );
}
