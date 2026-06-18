import Link from "next/link";
import { ThemeToggle } from "@ash2k5/ui";

export default function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-outline-variant bg-[var(--glass-fill)] [backdrop-filter:blur(16px)_saturate(1.1)] [@media(prefers-reduced-transparency:reduce)]:bg-surface [@media(prefers-reduced-transparency:reduce)]:[backdrop-filter:none]">
      <div className="ds-container flex items-center justify-between gap-4 py-4">
        <Link
          href="/"
          className="font-display text-xl leading-none text-on-surface"
        >
          Site Audit
        </Link>
        <ThemeToggle />
      </div>
    </header>
  );
}
