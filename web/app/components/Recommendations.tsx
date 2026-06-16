import { Badge } from "@ash2k5/cinematic-ds";
import type { Recommendation } from "../lib/api";
import { levelTone } from "../lib/format";

export default function Recommendations({
  items,
}: {
  items: Recommendation[];
}) {
  return (
    <ol className="flex flex-col">
      {items.map((rec, index) => (
        <li
          key={index}
          className="flex flex-col gap-3 border-t border-outline-variant py-6 first:border-t-0 first:pt-0 md:flex-row md:gap-8"
        >
          <span className="font-display text-2xl leading-none tabular-nums text-primary md:w-12">
            {String(index + 1).padStart(2, "0")}
          </span>
          <div className="flex flex-1 flex-col gap-3">
            <h3 className="font-display text-xl text-on-surface">{rec.title}</h3>
            <p className="ds-body-md text-on-surface-variant">{rec.detail}</p>
            <div className="flex flex-wrap gap-2">
              <Badge variant={levelTone(rec.impact)}>Impact: {rec.impact}</Badge>
              <Badge variant={levelTone(rec.effort)}>Effort: {rec.effort}</Badge>
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}
