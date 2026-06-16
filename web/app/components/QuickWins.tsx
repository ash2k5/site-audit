export default function QuickWins({ items }: { items: string[] }) {
  return (
    <ul className="flex max-w-3xl flex-col">
      {items.map((item, index) => (
        <li
          key={index}
          className="flex gap-3 border-b border-outline-variant py-3 ds-body-md text-on-surface first:pt-0"
        >
          <span
            aria-hidden
            className="mt-[0.6em] h-px w-4 shrink-0 bg-primary"
          />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
