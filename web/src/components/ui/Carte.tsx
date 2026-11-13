import type { ReactNode } from "react";

export function Carte({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-line bg-surface shadow-card ${className}`}>{children}</section>;
}

export function TitreCarte({ children, aide }: { children: ReactNode; aide?: ReactNode }) {
  return (
    <div className="mb-4">
      <h3 className="text-[15px] font-semibold tracking-tight">{children}</h3>
      {aide && <p className="mt-1 text-sm leading-relaxed text-ink-2">{aide}</p>}
    </div>
  );
}

export function Pastille({ children, ton = "neutre" }: { children: ReactNode; ton?: "neutre" | "accent" | "gain" | "perte" | "alerte" }) {
  const tons = {
    neutre: "bg-surface-2 text-ink-2",
    accent: "bg-accent-soft text-accent-ink",
    gain: "bg-gain-soft text-gain",
    perte: "bg-loss-soft text-loss",
    alerte: "bg-warn-soft text-warn",
  };
  return <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${tons[ton]}`}>{children}</span>;
}

export function Interrupteur({ actif, onChange, libelle, aide }: { actif: boolean; onChange: (v: boolean) => void; libelle: string; aide?: string }) {
  return (
    <label className="flex cursor-pointer items-start justify-between gap-4 py-2">
      <span>
        <span className="block text-sm font-medium">{libelle}</span>
        {aide && <span className="mt-0.5 block text-xs leading-relaxed text-muted">{aide}</span>}
      </span>
      <span className="relative mt-0.5 shrink-0">
        <input type="checkbox" checked={actif} onChange={(e) => onChange(e.target.checked)} className="peer sr-only" />
        <span className="block h-5 w-9 rounded-full bg-line-strong transition peer-checked:bg-accent peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-accent" />
        <span className="absolute left-0.5 top-0.5 size-4 rounded-full bg-white shadow transition peer-checked:translate-x-4" />
      </span>
    </label>
  );
}
