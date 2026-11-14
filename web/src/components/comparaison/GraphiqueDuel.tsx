"use client";

import type { ResultatScenario } from "@/lib/api";
import { euros, eurosCompacts, pourcentSigne } from "@/lib/format";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { etiquettesJours } from "@/components/Resultats";

export const COULEUR_A = "var(--series-1)";
export const COULEUR_B = "var(--series-2)";

/** Valeur des deux portefeuilles, courbes superposees, face au meme scenario. */
export function GraphiqueDuel({ a, b }: { a: ResultatScenario; b: ResultatScenario }) {
  const series: SerieLigne[] = [
    { nom: "Portefeuille A", couleur: COULEUR_A, valeurs: a.portefeuille.valeurs },
    { nom: "Portefeuille B", couleur: COULEUR_B, valeurs: b.portefeuille.valeurs },
  ];
  return (
    <Carte taille="normale">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-x-3 gap-y-2">
        <TitreCarte aide="Valeur de chaque portefeuille jour après jour, sous la même analyse de l'IA.">Évolution comparée</TitreCarte>
        <Legende series={series} reference="Capital de départ" />
      </div>
      <GraphiqueLignes
        series={series}
        etiquettesX={etiquettesJours(Math.max(a.portefeuille.valeurs.length, b.portefeuille.valeurs.length))}
        formatY={eurosCompacts}
        formatValeur={(v) => euros(v)}
        reference={{ valeur: a.portefeuille.capital, nom: "Capital de départ" }}
        description={`Évolution comparée de deux portefeuilles : A ${pourcentSigne(a.portefeuille.performance_pct)}, B ${pourcentSigne(b.portefeuille.performance_pct)}.`}
      />
    </Carte>
  );
}
