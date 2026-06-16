import type { CoreWebVitals as Vitals, PerformanceData } from "../lib/api";
import {
  formatVital,
  ratingTone,
  scoreTone,
  TONE_TEXT,
  VITAL_ORDER,
  VITALS,
  vitalRating,
  type Rating,
} from "../lib/format";

const RATING_LABEL: Record<Rating, string> = {
  good: "Good",
  "needs-improvement": "Needs work",
  poor: "Poor",
};

function ScorePill({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="ds-label-caps text-on-surface-variant">
        {label} PageSpeed
      </span>
      <span
        className={`font-display text-3xl leading-none tabular-nums ${TONE_TEXT[scoreTone(value)]}`}
      >
        {value}
        <span className="ds-body-sm text-on-surface-variant"> / 100</span>
      </span>
    </div>
  );
}

export default function CoreWebVitals({
  performance,
}: {
  performance: PerformanceData;
}) {
  const vitals: Vitals = performance.mobile_vitals ?? {};
  const present = VITAL_ORDER.filter((key) => vitals[key] != null);
  const hasScores =
    performance.mobile_score != null || performance.desktop_score != null;

  if (present.length === 0 && !hasScores) {
    return (
      <p className="ds-body-sm text-on-surface-variant">
        PageSpeed data was unavailable for this site.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {hasScores && (
        <div className="flex flex-wrap gap-10">
          {performance.mobile_score != null && (
            <ScorePill label="Mobile" value={performance.mobile_score} />
          )}
          {performance.desktop_score != null && (
            <ScorePill label="Desktop" value={performance.desktop_score} />
          )}
        </div>
      )}
      {present.length > 0 && (
        <dl className="grid grid-cols-2 gap-px bg-outline-variant sm:grid-cols-3">
          {present.map((key) => {
            const value = vitals[key] as number;
            const rating = vitalRating(key, value);
            return (
              <div key={key} className="flex flex-col gap-1 bg-surface p-4">
                <dt
                  className="ds-label-sm text-on-surface-variant"
                  title={VITALS[key].name}
                >
                  {VITALS[key].label}
                </dt>
                <dd
                  className={`font-display text-2xl leading-none tabular-nums ${TONE_TEXT[ratingTone(rating)]}`}
                >
                  {formatVital(key, value)}
                </dd>
                <span className="ds-label-sm text-on-surface-variant">
                  {RATING_LABEL[rating]}
                </span>
              </div>
            );
          })}
        </dl>
      )}
    </div>
  );
}
