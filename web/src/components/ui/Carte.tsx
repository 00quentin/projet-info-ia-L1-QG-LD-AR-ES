import type { ReactNode } from "react";

/** Marges interieures autorisees (docs/BENCHMARK.md 3.3) : 16 px sur mobile, 24 px (ou 32 px pour la carte heros) au-dela. */
const MARGES = { compacte: "p-4", normale: "p-4 sm:p-6", hero: "p-5 sm:p-8" } as const;

export function Carte({ children, className = "", taille }: { children: ReactNode; className?: string; taille?: keyof typeof MARGES }) {
  return <section className={`rounded-carte border border-line bg-surface shadow-card ${taille ? MARGES[taille] : ""} ${className}`}>{children}</section>;
}

/** Titre de carte (15 px) ; l'aide eventuelle tient sur une ligne courte en 13 px discret. */
export function TitreCarte({ children, aide }: { children: ReactNode; aide?: ReactNode }) {
  return (
    <div className="mb-4">
      <h3 className="text-titre font-semibold tracking-tight">{children}</h3>
      {aide && <p className="mt-1 text-aide text-muted">{aide}</p>}
    </div>
  );
}

/** Titre de section, au-dessus d'un groupe de cartes (20 px). */
export function TitreSection({ children, id }: { children: ReactNode; id?: string }) {
  return (
    <h2 id={id} className="text-section font-semibold tracking-tight">
      {children}
    </h2>
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
