"use client";

import type { CriseValidee } from "@/lib/validation";
import { libelleCategorie } from "./outils";

/** Catégories présentes dans les données, dans l'ordre d'apparition, avec leur nombre d'événements. */
export function categoriesDe(crises: CriseValidee[]): { nom: string; nb: number }[] {
  const comptes = new Map<string, number>();
  for (const c of crises) {
    if (c.categorie) comptes.set(c.categorie, (comptes.get(c.categorie) ?? 0) + 1);
  }
  return [...comptes].map(([nom, nb]) => ({ nom, nb }));
}

/** Puces de filtre par catégorie (une seule active à la fois). Rien si les données n'ont pas de catégories. */
export function FiltreCategories({
  crises,
  valeur,
  onChange,
  libelle,
}: {
  crises: CriseValidee[];
  valeur: string | null;
  onChange: (categorie: string | null) => void;
  libelle: string;
}) {
  const categories = categoriesDe(crises);
  if (categories.length < 2) return null;
  const puces = [{ nom: null as string | null, texte: "Toutes", nb: crises.length }, ...categories.map((c) => ({ nom: c.nom as string | null, texte: libelleCategorie(c.nom), nb: c.nb }))];
  return (
    <div className="flex flex-wrap gap-1.5" role="group" aria-label={libelle}>
      {puces.map((p) => {
        const actif = valeur === p.nom;
        return (
          <button
            key={p.nom ?? "toutes"}
            type="button"
            onClick={() => onChange(p.nom)}
            aria-pressed={actif}
            className={`rounded-full px-3 py-1.5 text-xs font-medium ring-1 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
              actif ? "bg-surface-2 text-ink ring-line-strong" : "text-ink-2 ring-line hover:bg-surface-2/60 hover:text-ink"
            }`}
          >
            {p.texte} <span className="tabular-nums text-muted">· {p.nb}</span>
          </button>
        );
      })}
    </div>
  );
}
