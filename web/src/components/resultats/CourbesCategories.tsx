"use client";

import type { SerieActif } from "@/lib/api";
import { nombre } from "@/lib/format";
import { libelleCategorie, nomCourt } from "@/contenu/actifs";
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
 * (au plus 5 courbes par graphique, au-dela un second graphique), dans une seule carte.
 */
export function CourbesCategories({ actifs, etiquettesX, avecFourchettes = true, description }: Props) {
  const groupes = new Map<string, SerieActif[]>();
  for (const a of actifs) groupes.set(a.categorie, [...(groupes.get(a.categorie) ?? []), a]);
  const blocs: { titre: string; actifs: SerieActif[] }[] = [];
  for (const [categorie, liste] of groupes) {
    const nom = libelleCategorie(categorie);
    const morceaux = Math.ceil(liste.length / SERIES_MAX);
    for (let k = 0; k < morceaux; k++) {
      blocs.push({ titre: morceaux > 1 ? `${nom} (${k + 1}/${morceaux})` : nom, actifs: liste.slice(k * SERIES_MAX, (k + 1) * SERIES_MAX) });
    }
  }
  const avecBandes = avecFourchettes && actifs.some((a) => a.prix_bas);

  return (
    <Carte taille="normale">
      <TitreCarte aide={`${description ?? "Base 100 au départ : 120 signifie +20 %."}${avecBandes ? " Zone claire : 90 % des trajectoires." : ""}`}>Évolution par classe d&apos;actifs</TitreCarte>
      <Cascade auDefilement className="grid grid-cols-1 gap-x-6 gap-y-8 xl:grid-cols-2">
        {blocs.map((b, i) => {
          const series: SerieLigne[] = b.actifs.map((a, k) => {
            const depart = a.prix[0];
            return {
              nom: nomCourt(a.cle, a.nom),
              couleur: COULEURS[k],
              valeurs: base100(a.prix, depart),
              bande: avecFourchettes && a.prix_bas && a.prix_haut ? { bas: base100(a.prix_bas, depart), haut: base100(a.prix_haut, depart) } : undefined,
            };
          });
          // Un graphique seul sur sa ligne prend toute la largeur.
          const seul = blocs.length % 2 === 1 && i === blocs.length - 1;
          return (
            <ElementCascade key={b.titre} className={`min-w-0 ${seul ? "xl:col-span-2" : ""}`}>
              <div className="mb-3 flex flex-wrap items-start justify-between gap-x-3 gap-y-1.5">
                <h4 className="text-sm font-semibold">{b.titre}</h4>
                <Legende series={series} />
              </div>
              <GraphiqueLignes
                series={series}
                etiquettesX={etiquettesX}
                formatY={(v) => nombre(v, 0)}
                formatValeur={(v) => nombre(v, 1)}
                reference={{ valeur: 100, nom: "Départ" }}
                hauteur={240}
                description={`${b.titre} : évolution en base 100 de ${series.map((s) => s.nom).join(", ")}.`}
              />
            </ElementCascade>
          );
        })}
      </Cascade>
    </Carte>
  );
}
