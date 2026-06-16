import { Badge } from "@ash2k5/cinematic-ds";
import type { CategoryScore } from "../lib/api";
import { gradeTone, scoreTone, TONE_TEXT } from "../lib/format";

export default function CategoryCard({
  name,
  category,
}: {
  name: string;
  category: CategoryScore;
}) {
  const findings = category.findings ?? [];
  return (
    <div className="flex flex-col gap-4 bg-surface p-6 md:p-8">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <span className="ds-label-caps text-on-surface-variant">{name}</span>
          <span
            className={`font-display text-[2.5rem] leading-none tabular-nums ${TONE_TEXT[scoreTone(category.score)]}`}
          >
            {category.score}
          </span>
        </div>
        <Badge variant={gradeTone(category.grade)}>Grade {category.grade}</Badge>
      </div>
      <p className="ds-body-md text-on-surface-variant">{category.summary}</p>
      {findings.length > 0 && (
        <ul className="flex flex-col gap-2">
          {findings.map((finding, index) => (
            <li
              key={index}
              className="flex gap-3 ds-body-sm text-on-surface-variant"
            >
              <span
                aria-hidden
                className="mt-[0.55em] h-px w-3 shrink-0 bg-primary"
              />
              <span>{finding}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
