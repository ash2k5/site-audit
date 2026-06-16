import type { AuditReport } from "../lib/api";
import { displayUrl, scoreTone, TONE_TEXT } from "../lib/format";
import CategoryCard from "./CategoryCard";
import CoreWebVitals from "./CoreWebVitals";
import DownloadPdfButton from "./DownloadPdfButton";
import QuickWins from "./QuickWins";
import Recommendations from "./Recommendations";
import Section from "./Section";
import TechnicalSignals from "./TechnicalSignals";

export default function AuditReportView({ report }: { report: AuditReport }) {
  const categories = [
    ["SEO", report.seo],
    ["Performance", report.performance],
    ["Technical", report.technical],
    ["Content", report.content],
  ] as const;

  const performance = report.raw_data?.performance;
  const technical = report.raw_data?.technical;

  return (
    <article className="flex flex-col gap-16">
      <header className="flex flex-col gap-8 border-t border-on-surface pt-8 md:flex-row md:items-start md:justify-between">
        <div className="flex flex-col gap-2">
          <span className="ds-label-caps text-primary">Audit report</span>
          <h2 className="font-display ds-headline-lg text-on-surface">
            {report.company_name}
          </h2>
          <a
            href={report.url}
            target="_blank"
            rel="noopener noreferrer"
            className="ds-body-sm text-on-surface-variant underline-offset-4 hover:underline"
          >
            {displayUrl(report.url)}
          </a>
        </div>
        <div className="flex items-start gap-8">
          <div className="flex flex-col items-end">
            <span className="ds-label-caps text-on-surface-variant">Overall</span>
            <span
              className={`font-display text-[3.5rem] leading-none tabular-nums ${TONE_TEXT[scoreTone(report.overall_score)]}`}
            >
              {report.overall_score}
            </span>
            <span className="ds-label-sm text-on-surface-variant">/ 100</span>
          </div>
          <DownloadPdfButton url={report.url} />
        </div>
      </header>

      <Section kicker="Summary" title="Executive summary">
        <p className="max-w-3xl ds-body-lg text-on-surface-variant">
          {report.executive_summary}
        </p>
      </Section>

      <Section kicker="Scores" title="Category breakdown">
        <div className="grid gap-px bg-outline-variant md:grid-cols-2">
          {categories.map(([name, category]) => (
            <CategoryCard key={name} name={name} category={category} />
          ))}
        </div>
      </Section>

      {(performance || technical) && (
        <Section kicker="Measured" title="Performance & technical signals">
          {performance && <CoreWebVitals performance={performance} />}
          {technical && <TechnicalSignals technical={technical} />}
        </Section>
      )}

      {report.quick_wins.length > 0 && (
        <Section kicker="Start here" title="Quick wins">
          <QuickWins items={report.quick_wins} />
        </Section>
      )}

      {report.recommendations.length > 0 && (
        <Section kicker="Action plan" title="Recommendations">
          <Recommendations items={report.recommendations} />
        </Section>
      )}
    </article>
  );
}
