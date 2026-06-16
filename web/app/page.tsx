import AuditClient from "./components/AuditClient";

export default function Home() {
  return (
    <div className="ds-container flex flex-col gap-12 py-16 md:py-20">
      <header className="flex max-w-3xl flex-col gap-5">
        <span className="ds-label-caps text-primary">Website audit</span>
        <h1 className="font-display ds-display text-on-surface">
          See what your site is leaving on the table.
        </h1>
        <p className="ds-body-lg text-on-surface-variant">
          Enter a URL. We scrape the page, measure Core Web Vitals, and score
          SEO, performance, technical health, and content into a prioritized
          action plan.
        </p>
      </header>
      <AuditClient />
    </div>
  );
}
