import Link from "next/link";
import { Button } from "@ash2k5/cinematic-ds";

export default function NotFound() {
  return (
    <div className="ds-container flex flex-col items-start gap-6 py-24">
      <span className="ds-label-caps text-primary">404</span>
      <h1 className="font-display ds-headline-lg text-on-surface">
        Page not found
      </h1>
      <p className="max-w-md ds-body-lg text-on-surface-variant">
        That page does not exist. Head back and run an audit.
      </p>
      <Button asChild variant="ghost">
        <Link href="/">Back to audit</Link>
      </Button>
    </div>
  );
}
