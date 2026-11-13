"use client";

import type { SerieActif } from "@/lib/api";
import { nombre } from "@/lib/format";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";

const COULEURS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)", "var(--series-5)"];
const SERIES_MAX = COULEURS.length;

const base100 = (valeurs: (number | null)[], depart: number) => valeurs.map((v) => (v == null || !depart ? null : (v / depart) * 100));

type Props = {
  actifs: SerieActif[];
  /** Une etiquette par point (dates reelles ou "Jour N"). */
  etiquettesX: string[];
  /** Ajoute la fourchette Monte-Carlo de chaque actif quand elle existe. */
  avecFourchettes?: boolean;
  description?: string;
};

/**
 * Prix de chaque actif ramenes a une base 100, regroupes par classe d'actifs
 * (au plus 5 courbes par graphique, au-dela un second graphique).
 */
export function CourbesCategories({ actifs, etiquettesX, avecFourchettes = true, description }: Props) {
  const groupes = new Map<string, SerieActif[]>();
  for (const a of actifs) groupes.set(a.categorie, [...(groupes.get(a.categorie) ?? []), a]);
  const blocs: { titre: string; actifs: SerieActif[] }[] = [];
  for (const [categorie, liste] of groupes) {
    for (let i = 0; i < liste.length; i += SERIES_MAX) {
      blocs.push({ titre: i === 0 ? categorie : `${categorie} (suite)`, actifs: liste.slice(i, i + SERIES_MAX) });
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div>
        <h3 className="mt-2 text-[15px] font-semibold tracking-tight">Évolution par classe d&apos;actifs</h3>
        <p className="mt-1 text-sm text-ink-2">
          {description ?? "Chaque prix est ramené à 100 au départ : 120 signifie +20 %."}
          {avecFourchettes && actifs.some((a) => a.prix_bas) ? " La zone claire contient 90 % des trajectoires simulées." : ""}
        </p>
      </div>
      <Cascade auDefilement className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        {blocs.map((b) => {
          const series: SerieLigne[] = b.actifs.map((a, i) => {
            const depart = a.prix[0];
            return {
              nom: a.nom,
              couleur: COULEURS[i],
              valeurs: base100(a.prix, depart),
              bande: avecFourchettes && a.prix_bas && a.prix_haut ? { bas: base100(a.prix_bas, depart), haut: base100(a.prix_haut, depart) } : undefined,
            };
          });
          return (
            <ElementCascade key={b.titre} className="min-w-0">
              <Carte className="h-full p-5">
                <div className="mb-3 flex flex-col gap-2">
                  <TitreCarte aide={series.length === 1 ? series[0].nom : undefined}>{b.titre}</TitreCarte>
                  {series.length > 1 && <Legende series={series} />}
                </div>
                <GraphiqueLignes
                  series={series}
                  etiquettesX={etiquettesX}
                  formatY={(v) => nombre(v, 0)}
                  formatValeur={(v) => nombre(v, 1)}
                  reference={{ valeur: 100, nom: "Départ" }}
                  hauteur={240}
                  description={`${b.titre} : évolution en base 100 de ${b.actifs.map((a) => a.nom).join(", ")}.`}
                />
              </Carte>
            </ElementCascade>
          );
        })}
      </Cascade>
    </div>
  );
}
