import type { ReactNode } from "react";
import { Lightbulb, Quote, ShieldCheck, TriangleAlert } from "lucide-react";
import { Apparition } from "@/components/motion/Apparition";

// Briques de mise en page de l'Académie (sans état : rendues côté serveur).
// Largeur de lecture : ~70 caractères pour le texte courant.
export const LARGEUR_TEXTE = "max-w-[37rem]";

/** Section numérotée (h3) : son ancre est reprise par le sommaire. */
export function Section({ id, numero, titre, etiquette, children }: { id: string; numero?: string; titre: string; etiquette?: string; children: ReactNode }) {
  return (
    <section aria-labelledby={id}>
      <Apparition auDefilement decalage={10}>
        {etiquette && <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-accent">{etiquette}</p>}
        <h3 id={id} className="scroll-mt-6 text-xl font-semibold leading-snug tracking-tight text-ink lg:scroll-mt-36">
          {numero && <span className="mr-2 font-semibold text-accent-ink tabular-nums">{numero}</span>}
          {titre}
        </h3>
        <div className="mt-4 flex flex-col gap-4">{children}</div>
      </Apparition>
    </section>
  );
}

/** Paragraphe d'introduction d'un module, un peu plus grand. */
export function Chapeau({ children }: { children: ReactNode }) {
  return <p className={`${LARGEUR_TEXTE} text-lg leading-relaxed text-ink-2`}>{children}</p>;
}

export function P({ children }: { children: ReactNode }) {
  return <p className={`${LARGEUR_TEXTE} text-base leading-relaxed text-ink-2`}>{children}</p>;
}

/** Gras (le **texte** du markdown Streamlit). */
export function G({ children }: { children: ReactNode }) {
  return <strong className="font-semibold text-ink">{children}</strong>;
}

export function SousTitre({ children }: { children: ReactNode }) {
  return <h4 className="mt-2 text-base font-semibold tracking-tight text-ink">{children}</h4>;
}

export function Liste({ children }: { children: ReactNode }) {
  return <ul className={`${LARGEUR_TEXTE} flex flex-col gap-2.5 text-base leading-relaxed text-ink-2`}>{children}</ul>;
}

export function Point({ children }: { children: ReactNode }) {
  return (
    <li className="relative pl-5">
      <span aria-hidden className="absolute left-0.5 top-[0.72em] size-1.5 rounded-full bg-accent" />
      {children}
    </li>
  );
}

const TONS_ENCADRE = {
  info: { boite: "border-accent/25 bg-accent-soft", icone: "text-accent-ink", Icone: Lightbulb, libelle: "À retenir" },
  alerte: { boite: "border-warn/35 bg-warn-soft", icone: "text-warn", Icone: TriangleAlert, libelle: "Attention" },
};

/** Encadré pédagogique : "info" (à retenir) ou "alerte" (piège, limite). */
export function Encadre({ ton = "info", titre, children }: { ton?: keyof typeof TONS_ENCADRE; titre?: ReactNode; children: ReactNode }) {
  const t = TONS_ENCADRE[ton];
  return (
    <aside role="note" aria-label={t.libelle} className={`max-w-[40rem] rounded-carte border px-4 py-4 sm:px-5 ${t.boite}`}>
      <div className="flex gap-3">
        <t.Icone className={`mt-0.5 size-5 shrink-0 ${t.icone}`} aria-hidden />
        <div className="flex min-w-0 flex-col gap-2.5 text-titre leading-relaxed text-ink-2">
          {titre && <p className="font-semibold text-ink">{titre}</p>}
          {children}
        </div>
      </div>
    </aside>
  );
}

/** Liste à puces à l'intérieur d'un encadré. */
export function ListeEncadre({ children }: { children: ReactNode }) {
  return <ul className="flex flex-col gap-2">{children}</ul>;
}

export function Citation({ children, traduction, auteur }: { children: ReactNode; traduction?: ReactNode; auteur: string }) {
  return (
    <figure className={`${LARGEUR_TEXTE} relative rounded-carte border border-line bg-surface px-5 py-4 shadow-card`}>
      <Quote className="absolute right-4 top-4 size-5 text-accent/40" aria-hidden />
      <blockquote className="pr-8 text-lg font-medium italic leading-relaxed text-ink" lang="en">
        {children}
      </blockquote>
      {traduction && <p className="mt-2 text-titre leading-relaxed text-ink-2">{traduction}</p>}
      <figcaption className="mt-2 text-sm text-muted">— {auteur}</figcaption>
    </figure>
  );
}

/** Récit d'une crise en étapes (contexte, déclenchement, chute, enseignement). */
export function Chronologie({ children }: { children: ReactNode }) {
  return <ol className={`${LARGEUR_TEXTE} relative flex flex-col gap-5 border-l border-line pl-6`}>{children}</ol>;
}

export function Etape({ titre, ton = "neutre", children }: { titre: string; ton?: "neutre" | "perte" | "gain" | "accent"; children: ReactNode }) {
  const puce = { neutre: "bg-line-strong", perte: "bg-loss", gain: "bg-gain", accent: "bg-accent" }[ton];
  return (
    <li className="relative">
      <span aria-hidden className={`absolute -left-[29px] top-1.5 size-2.5 rounded-full ring-4 ring-bg ${puce}`} />
      <p className="text-xs font-semibold uppercase tracking-wide text-muted">{titre}</p>
      <div className="mt-1.5 flex flex-col gap-3 text-base leading-relaxed text-ink-2">{children}</div>
    </li>
  );
}

/** Tableau lisible sur mobile : il défile horizontalement dans son cadre, jamais la page. */
export function Tableau({ legende, entetes, lignes }: { legende: string; entetes: ReactNode[]; lignes: ReactNode[][] }) {
  return (
    <div tabIndex={0} className="max-w-[46rem] overflow-x-auto rounded-carte border border-line bg-surface shadow-card">
      <table className="w-full min-w-[34rem] border-collapse text-left text-sm">
        <caption className="sr-only">{legende}</caption>
        <thead className="bg-surface-2 text-xs uppercase tracking-wide text-muted">
          <tr>
            {entetes.map((e, i) => (
              <th key={i} scope="col" className="px-4 py-2.5 font-semibold">
                {e}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {lignes.map((ligne, i) => (
            <tr key={i} className="border-t border-line transition-colors hover:bg-surface-2/60">
              {ligne.map((cellule, j) =>
                j === 0 ? (
                  <th key={j} scope="row" className="px-4 py-3 font-semibold text-ink">
                    {cellule}
                  </th>
                ) : (
                  <td key={j} className="px-4 py-3 text-ink-2">
                    {cellule}
                  </td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Grille de cartes de texte (modèles, volets d'une comparaison, horizons). */
export function Grille({ colonnes = 2, children }: { colonnes?: 2 | 3; children: ReactNode }) {
  return <div className={`grid max-w-[46rem] grid-cols-1 gap-3 ${colonnes === 3 ? "md:grid-cols-3" : "md:grid-cols-2"}`}>{children}</div>;
}

export function CarteTexte({ etiquette, titre, icone, children }: { etiquette?: ReactNode; titre: ReactNode; icone?: ReactNode; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-3 rounded-carte border border-line bg-surface p-5 shadow-card">
      <div className="flex items-center gap-3">
        {etiquette && <span className="grid size-8 shrink-0 place-items-center rounded-controle bg-accent-soft text-sm font-semibold text-accent-ink">{etiquette}</span>}
        {icone}
        <h4 className="text-titre font-semibold leading-snug tracking-tight text-ink">{titre}</h4>
      </div>
      <div className="flex flex-col gap-2.5 text-titre leading-relaxed text-ink-2">{children}</div>
    </div>
  );
}

/** Conseil pratique pour contrer un biais. */
export function Antidote({ titre = "Antidote", children }: { titre?: string; children: ReactNode }) {
  return (
    <div className={`${LARGEUR_TEXTE} flex gap-3 rounded-tuile border border-gain/25 bg-gain-soft px-4 py-3`}>
      <ShieldCheck className="mt-1 size-4 shrink-0 text-gain" aria-hidden />
      <p className="text-titre leading-relaxed text-ink-2">
        <span className="font-semibold text-ink">{titre} :</span> {children}
      </p>
    </div>
  );
}

/** Lexique : terme et définition côte à côte sur grand écran, empilés sur mobile. */
export function Glossaire({ children }: { children: ReactNode }) {
  return <dl className="max-w-[46rem] divide-y divide-line overflow-hidden rounded-carte border border-line bg-surface shadow-card">{children}</dl>;
}

export function Terme({ nom, precision, children }: { nom: ReactNode; precision?: ReactNode; children: ReactNode }) {
  return (
    <div className="grid gap-1 px-4 py-3.5 transition-colors hover:bg-surface-2/60 sm:grid-cols-[12.5rem_minmax(0,1fr)] sm:gap-6 sm:px-5">
      <dt className="font-semibold text-ink">
        {nom}
        {precision && <span className="mt-0.5 block text-xs font-normal italic text-muted">{precision}</span>}
      </dt>
      <dd className="text-titre leading-relaxed text-ink-2">{children}</dd>
    </div>
  );
}
