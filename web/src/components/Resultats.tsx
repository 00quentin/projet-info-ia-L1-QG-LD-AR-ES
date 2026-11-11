"use client";

import { motion } from "motion/react";
import { GitCompareArrows, TriangleAlert } from "lucide-react";
import type { DemandeRapport, ParametresSimulation, ReponseSimulation, ResultatScenario } from "@/lib/api";
import { euros, eurosCompacts, pourcentSigne } from "@/lib/format";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { BarresPerformance } from "@/components/charts/BarresPerformance";
import { Apparition } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { Synthese } from "@/components/resultats/Synthese";
import { AnalyseIA } from "@/components/resultats/AnalyseIA";
import { Repartition } from "@/components/resultats/Repartition";
import { CourbesCategories } from "@/components/resultats/CourbesCategories";
import { ListeAlertes, TuilesRisque } from "@/components/resultats/Risque";
import { DetailPortefeuille } from "@/components/resultats/DetailPortefeuille";
import { BoutonsExport } from "@/components/exports/BoutonsExport";
import { colonnesPoches } from "@/lib/poches";

const COULEURS_BENCHMARKS = ["var(--series-2)", "var(--series-3)"];

export const etiquettesJours = (n: number) => Array.from({ length: n }, (_, i) => (i === 0 ? "Aujourd'hui" : `Jour ${i}`));

/** Contenu du rapport PDF d'un scenario simule. */
export function rapportSimulation(s: ResultatScenario, p: ParametresSimulation): DemandeRapport {
  return {
    type_rapport: "Simulation",
    scenario: s.scenario,
    profil: p.profil,
    capital: s.portefeuille.capital,
    valeur_finale: s.portefeuille.valeur_finale,
    duree: p.duree,
    monte_carlo: p.monte_carlo,
    prix_reels: p.prix_reels,
    calibration: p.calibration,
    nb_actifs: s.actifs.length,
    inflation: s.analyse.inflation,
    taux_directeurs: s.analyse.taux_directeurs,
    explication: s.analyse.explication ?? "",
    evenement_reference: s.analyse.evenement_reference,
    performances: s.actifs.map((a) => ({ nom: a.nom, performance: a.performance_pct })),
    allocations: s.allocations.map((a) => ({ nom: a.nom, poids: a.poids, investi: a.investi, final: a.final, rendement: a.performance_pct / 100 })),
    vol_ann: s.metriques.vol_ann,
    sharpe: s.metriques.sharpe,
    max_dd: s.metriques.max_dd,
    var_95: s.metriques.var_95,
    avec_analyse_ia: true,
  };
}

function CarteFinale({ nom, couleur, valeur, capital, principale }: { nom: string; couleur: string; valeur: number; capital: number; principale?: boolean }) {
  const perf = (valeur / capital - 1) * 100;
  return (
    <div className={`rounded-xl border px-4 py-3 ${principale ? "border-accent/40 bg-accent-soft/40" : "border-line"}`}>
      <div className="flex items-center gap-1.5 text-xs text-ink-2">
        <span className="inline-block h-0.5 w-3 rounded-full" style={{ background: couleur }} />
        {nom}
      </div>
      <NombreAnime valeur={valeur} depuis={capital} format={(v) => euros(v)} className="mt-1 block text-lg font-semibold" />
      <div className={`text-xs font-medium ${perf >= 0 ? "text-gain" : "text-loss"}`}>
        <span aria-hidden>{perf >= 0 ? "▲ " : "▼ "}</span>
        {pourcentSigne(perf)}
      </div>
    </div>
  );
}

function Evolution({ s, p }: { s: ResultatScenario; p: ParametresSimulation }) {
  const pf = s.portefeuille;
  const series: SerieLigne[] = [
    { nom: "Votre portefeuille", couleur: "var(--series-1)", valeurs: pf.valeurs, principale: true },
    ...s.benchmarks.map((b, i) => ({ nom: b.nom.split(" (")[0], couleur: COULEURS_BENCHMARKS[i % 2], valeurs: b.valeurs })),
  ];
  const bande = pf.valeurs_bas && pf.valeurs_haut ? { bas: pf.valeurs_bas, haut: pf.valeurs_haut, nom: "90 % des trajectoires" } : undefined;
  const etiquettes = etiquettesJours(pf.valeurs.length);
  const pas = Math.max(1, Math.round(pf.valeurs.length / 10));
  const lignesTableau = pf.valeurs.map((_, i) => i).filter((i) => i % pas === 0 || i === pf.valeurs.length - 1);

  return (
    <Carte className="p-6">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <TitreCarte
          aide={
            bande
              ? "La courbe est la trajectoire médiane. La zone claire contient 90 % des trajectoires simulées."
              : "Une trajectoire possible parmi d'autres. Activez Monte-Carlo pour voir la fourchette des issues."
          }
        >
          Évolution du portefeuille
        </TitreCarte>
        <Legende series={series} bande={bande ? { nom: bande.nom, couleur: "var(--series-1)" } : undefined} reference="Capital de départ" />
      </div>
      <div className="mb-5 grid grid-cols-1 gap-2 sm:grid-cols-3">
        {series.map((se, i) => (
          <CarteFinale key={se.nom} nom={se.nom} couleur={se.couleur} valeur={se.valeurs[se.valeurs.length - 1] ?? pf.capital} capital={pf.capital} principale={i === 0} />
        ))}
      </div>
      <GraphiqueLignes
        series={series}
        bande={bande}
        etiquettesX={etiquettes}
        formatY={eurosCompacts}
        formatValeur={(v) => euros(v)}
        reference={{ valeur: pf.capital, nom: "Capital de départ" }}
        description={`Évolution simulée du portefeuille sur ${p.duree} jours, de ${euros(pf.capital)} à ${euros(pf.valeur_finale)}, comparée aux indices de référence.`}
      />
      <details className="mt-3 text-sm">
        <summary className="cursor-pointer text-xs font-medium text-accent-ink">Voir les valeurs en tableau</summary>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-96 text-right text-xs tabular-nums">
            <thead className="text-muted">
              <tr>
                <th className="py-1.5 text-left font-medium">Jour</th>
                {series.map((se) => (
                  <th key={se.nom} className="py-1.5 font-medium">
                    {se.nom}
                  </th>
                ))}
                {bande && <th className="py-1.5 font-medium">Fourchette 90 %</th>}
              </tr>
            </thead>
            <tbody>
              {lignesTableau.map((i) => (
                <tr key={i} className="border-t border-line">
                  <td className="py-1.5 text-left">{etiquettes[i]}</td>
                  {series.map((se) => (
                    <td key={se.nom} className="py-1.5">
                      {se.valeurs[i] != null ? euros(se.valeurs[i] as number) : "—"}
                    </td>
                  ))}
                  {bande && (
                    <td className="py-1.5">
                      {euros(bande.bas[i] as number)} – {euros(bande.haut[i] as number)}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </Carte>
  );
}

type Props = {
  reponse: ReponseSimulation;
  scenario: ResultatScenario;
  /** Nom d'affichage de chaque cle d'actif (catalogue + actifs personnalises). */
  noms: Map<string, string>;
  lienPartage?: string;
  /** Propose de comparer avec un 2e scenario (affiche seulement s'il est fourni). */
  onComparer?: () => void;
};

export function Resultats({ reponse, scenario, noms, lienPartage, onComparer }: Props) {
  const p = reponse.parametres;
  const etiquettes = etiquettesJours(scenario.portefeuille.valeurs.length);

  return (
    <div className="flex flex-col gap-4">
      <Apparition className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <p className="text-sm leading-relaxed text-ink-2">
          <span className="font-medium text-ink">Scénario :</span> {scenario.scenario}
        </p>
        {onComparer && (
          <motion.button
            type="button"
            onClick={onComparer}
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.97 }}
            className="flex shrink-0 items-center gap-1.5 self-start rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink"
          >
            <GitCompareArrows className="size-3.5" aria-hidden />
            Comparer avec un autre scénario
          </motion.button>
        )}
      </Apparition>

      {reponse.prix_de_secours.length > 0 && (
        <Apparition role="status" className="flex gap-3 rounded-xl border border-warn/30 bg-warn-soft px-4 py-3 text-sm">
          <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
          <span>Yahoo Finance n&apos;a pas répondu pour {reponse.prix_de_secours.map((x) => x.nom).join(", ")} : les dernières valeurs connues ont été utilisées.</span>
        </Apparition>
      )}

      <Apparition delai={0.05}>
        <Synthese s={scenario} p={p} />
      </Apparition>
      <Apparition delai={0.12}>
        <AnalyseIA s={scenario} calibration={p.calibration} noms={noms} conjoncture={reponse.conjoncture} />
      </Apparition>
      <Apparition auDefilement>
        <Evolution s={scenario} p={p} />
      </Apparition>

      <div className="flex flex-col gap-3">
        <h3 className="mt-2 text-[15px] font-semibold tracking-tight">Le risque de ce portefeuille</h3>
        <TuilesRisque m={scenario.metriques} tauxSansRisquePct={p.taux_sans_risque_pct} />
        <ListeAlertes alertes={scenario.alertes} />
      </div>

      <Apparition auDefilement>
        <Repartition allocations={scenario.allocations} />
      </Apparition>

      <Apparition auDefilement>
        <Carte className="p-6">
          <TitreCarte aide={`Variation estimée de chaque actif sur ${p.duree} jours${scenario.converti_eur ? ", en euros" : ""}.`}>Performance par actif</TitreCarte>
          <BarresPerformance lignes={scenario.actifs.map((a) => ({ cle: a.cle, nom: a.nom, valeur: a.performance_pct }))} />
        </Carte>
      </Apparition>

      <CourbesCategories actifs={scenario.actifs} etiquettesX={etiquettes} />

      <Apparition auDefilement>
        <DetailPortefeuille
          allocations={scenario.allocations}
          capital={scenario.portefeuille.capital}
          valeurFinale={scenario.portefeuille.valeur_finale}
          performancePct={scenario.portefeuille.performance_pct}
        />
      </Apparition>

      <Apparition auDefilement>
        <BoutonsExport
          csv={{
            nomFichier: `quant_terminal_simulation${scenario.label !== "A" ? `_${scenario.label}` : ""}`,
            titreColonneEtiquette: "jour",
            etiquettes: scenario.portefeuille.valeurs.map((_, i) => String(i)),
            colonnes: colonnesPoches(scenario.portefeuille, scenario.allocations, scenario.actifs),
          }}
          rapport={rapportSimulation(scenario, p)}
          lienPartage={lienPartage}
        />
      </Apparition>

      <p className="px-1 text-xs leading-relaxed text-muted">
        Outil pédagogique : ces résultats sont des estimations issues d&apos;un modèle et d&apos;une IA, pas un conseil en investissement. La réalité peut fortement diverger.
      </p>
    </div>
  );
}
