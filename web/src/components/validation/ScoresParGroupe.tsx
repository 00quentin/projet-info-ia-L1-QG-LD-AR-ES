import type { MetriquesValidation, ValidationIA } from "@/lib/validation";
import { Carte } from "@/components/ui/Carte";
import { coefficient, libelleCategorie, part, points } from "./outils";

type Ligne = { cle: string; nom: string; nb: number | undefined; m: MetriquesValidation };

function Rangee({ l }: { l: Ligne }) {
  const bonSens = l.m.part_sens_correct;
  return (
    <tr className="border-t border-line align-top">
      <th scope="row" className="px-3 py-2.5 text-left font-normal">
        <span className="block text-[13px] font-medium text-ink">{l.nom}</span>
        <span className="block text-[11px] text-muted">
          {l.nb != null ? `${l.nb} événement${l.nb > 1 ? "s" : ""} · ` : ""}
          {l.m.nb_actifs} comparaisons
        </span>
      </th>
      <td className="px-2 py-2.5 text-right tabular-nums">
        <span className="block text-[13px] font-semibold text-ink">{part(bonSens ?? null)}</span>
        <span aria-hidden className="mt-1 ml-auto block h-1 w-12 overflow-hidden rounded-full bg-surface-2 sm:w-16">
          <span className="block h-full rounded-full bg-[var(--series-1)]" style={{ width: `${(bonSens ?? 0) * 100}%` }} />
        </span>
      </td>
      <td className="px-2 py-2.5 text-right text-[13px] tabular-nums text-ink-2">{points(l.m.erreur_moyenne_pts)}</td>
      <td className="hidden px-2 py-2.5 text-right text-[13px] tabular-nums text-ink-2 sm:table-cell">{coefficient(l.m.correlation)}</td>
      <td className="px-3 py-2.5 text-right text-[13px] tabular-nums text-ink-2">{part(l.m.part_dans_fourchette ?? null)}</td>
    </tr>
  );
}

function Groupe({ titre, lignes }: { titre: string; lignes: Ligne[] }) {
  return (
    <tbody>
      <tr className="border-t border-line bg-surface-2/60">
        <th colSpan={5} scope="colgroup" className="px-3 py-1.5 text-left text-[11px] font-medium uppercase tracking-wide text-muted">
          {titre}
        </th>
      </tr>
      {lignes.map((l) => (
        <Rangee key={l.cle} l={l} />
      ))}
    </tbody>
  );
}

/** Scores par catégorie d'événement, puis hors échantillon contre échantillon du prompt. */
export function ScoresParGroupe({ v }: { v: ValidationIA }) {
  const categories: Ligne[] = Object.entries(v.par_categorie ?? {}).map(([nom, m]) => ({
    cle: nom,
    nom: libelleCategorie(nom),
    nb: m.nb_evenements,
    m,
  }));
  const echantillon: Ligne[] = [];
  if (v.hors_echantillon) echantillon.push({ cle: "hors", nom: "Hors échantillon", nb: v.hors_echantillon.nb_evenements, m: v.hors_echantillon });
  if (v.echantillon_prompt) echantillon.push({ cle: "prompt", nom: "Ayant servi à écrire la consigne", nb: v.echantillon_prompt.nb_evenements, m: v.echantillon_prompt });
  if (categories.length === 0 && echantillon.length === 0) return null;
  return (
    <Carte className="overflow-hidden">
      <table className="w-full text-sm">
        <caption className="sr-only">Scores de l’IA par catégorie d’événement et selon l’échantillon</caption>
        <thead className="text-left text-xs text-ink-2">
          <tr>
            <th scope="col" className="px-3 py-2.5 font-medium">
              Groupe
            </th>
            <th scope="col" className="px-2 py-2.5 text-right font-medium">
              Bon sens
            </th>
            <th scope="col" className="px-2 py-2.5 text-right font-medium">
              Erreur
            </th>
            <th scope="col" className="hidden px-2 py-2.5 text-right font-medium sm:table-cell">
              Corrélation
            </th>
            <th scope="col" className="px-3 py-2.5 text-right font-medium">
              Fourchette
            </th>
          </tr>
        </thead>
        {categories.length > 0 && <Groupe titre="Par catégorie" lignes={categories} />}
        {echantillon.length > 0 && <Groupe titre="Selon l’échantillon" lignes={echantillon} />}
      </table>
    </Carte>
  );
}
