import type { ReactNode } from "react";

export default function Section({
  kicker,
  title,
  children,
}: {
  kicker?: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        {kicker && <span className="ds-label-caps text-primary">{kicker}</span>}
        <h2 className="font-display ds-headline-md text-on-surface">{title}</h2>
      </div>
      {children}
    </section>
  );
}
