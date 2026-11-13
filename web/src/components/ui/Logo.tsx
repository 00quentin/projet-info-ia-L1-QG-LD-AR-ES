import { useId } from "react";

/** Logo vectoriel (net a toutes les tailles) : une courbe qui monte sur un carre degrade. */
export function Logo({ className = "" }: { className?: string }) {
  const id = useId();
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="var(--accent)" />
          <stop offset="1" stopColor="var(--series-3)" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="8" fill={`url(#${id})`} />
      <polyline points="7,22.5 12.2,18.2 17.4,20 22.2,13.2 25.2,10.4" fill="none" stroke="var(--on-series-1)" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="25.2" cy="10.4" r="2.9" fill="var(--on-series-1)" />
    </svg>
  );
}
