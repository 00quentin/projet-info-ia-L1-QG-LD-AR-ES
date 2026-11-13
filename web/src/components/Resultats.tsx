"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import { ArrowRight, GitCompareArrows, TriangleAlert } from "lucide-react";
import type { DemandeRapport, ParametresSimulation, ReponseSimulation, ResultatScenario } from "@/lib/api";
import { euros, eurosCompacts, pourcentSigne } from "@/lib/format";
import { nomCourt } from "@/contenu/actifs";
import { Carte, TitreCarte, TitreSection } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { BarresPerformance } from "@/components/charts/BarresPerformance";
import { Apparition } from "@/components/motion/Apparition";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import { Synthese } from "@/components/resultats/Synthese";
import { AnalyseIA } from "@/components/resultats/AnalyseIA";
import { Repartition } from "@/components/resultats/Repartition";
import { CourbesCategories } from "@/components/resultats/CourbesCategories";
import { ListeAlertes, TuilesRisque } from "@/components/resultats/Risque";
import { DetailPortefeuille } from "@/components/resultats/DetailPortefeuille";
import { Infobulle } from "@/components/resultats/Infobulle";
import { Depliable } from "@/components/resultats/Depliable";
import { Sommaire, type EntreeSommaire } from "@/components/resultats/Sommaire";
import { BoutonsExport } from "@/components/exports/BoutonsExport";
import { Protection } from "@/components/resultats/Protection";
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

// Ancres des parties des resultats (un seul jeu de resultats affiche a la fois).
const PARTIES = {
  synthese: "resultats-synthese",
  evolution: "resultats-evolution",
  analyse: "resultats-analyse",
  risque: "resultats-risque",
  repartition: "resultats-repartition",
  detail: "resultats-detail",
  exports: "resultats-exports",
} as const;

const SOMMAIRE: EntreeSommaire[] = [
  { id: PARTIES.synthese, libelle: "Vue d'ensemble" },
  { id: PARTIES.evolution, libelle: "Évolution" },
  { id: PARTIES.analyse, libelle: "Analyse de l'IA" },
  { id: PARTIES.risque, libelle: "Risque" },
  { id: PARTIES.repartition, libelle: "Répartition" },
  { id: PARTIES.detail, libelle: "Détail" },
  { id: PARTIES.exports, libelle: "Exporter" },
];

/**
 * Partie des resultats : cible du sommaire (focusable sans entrer dans l'ordre de tabulation).
 * Avec `titre`, un titre de section (20 px) coiffe le groupe de cartes ; sinon la carte porte son propre titre.
 */
function Partie({ id, libelle, titre, children }: { id: string; libelle?: string; titre?: string; children: ReactNode }) {
  return (
    <section id={id} tabIndex={-1} aria-label={titre ? undefined : libelle} aria-labelledby={titre ? `${id}-titre` : undefined} className="flex flex-col gap-4 outline-none">
      {titre && <TitreSection id={`${id}-titre`}>{titre}</TitreSection>}
      {children}
    </section>
  );
}

/** Valeur finale d'une courbe : apparait en fondu, sans compter (seul le chiffre heros compte). */
function CarteFinale({ nom, couleur, valeur, capital, principale, delai }: { nom: string; couleur: string; valeur: number; capital: number; principale?: boolean; delai: number }) {
  const perf = (valeur / capital - 1) * 100;
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: DUREE.normale, ease: EASE_SORTIE, delay: delai }}
      className={`rounded-tuile border px-4 py-3 ${principale ? "border-accent/40 bg-accent-soft/40" : "border-line"}`}
    >
      <div className="flex items-center gap-1.5 text-xs text-ink-2">
        <span className="inline-block h-0.5 w-3 rounded-full" style={{ background: couleur }} aria-hidden />
        {nom}
      </div>
      <div className="mt-1 text-lg font-semibold tabular-nums">{euros(valeur)}</div>
      <div className={`text-xs font-medium tabular-nums ${perf >= 0 ? "text-gain" : "text-loss"}`}>{pourcentSigne(perf)}</div>
    </motion.div>
  );
}

function Evolution({ s, p }: { s: ResultatScenario; p: ParametresSimulation }) {
  const pf = s.portefeuille;
  const series: SerieLigne[] = [
    { nom: "Votre portefeuille", couleur: "var(--series-1)", valeurs: pf.valeurs, principale: true },
    ...s.benchmarks.map((b, i) => ({ nom: nomCourt(b.cle, b.nom.split(" (")[0]), couleur: COULEURS_BENCHMARKS[i % 2], valeurs: b.valeurs })),
  ];
  const bande = pf.valeurs_bas && pf.valeurs_haut ? { bas: pf.valeurs_bas, haut: pf.valeurs_haut, nom: "90 % des trajectoires" } : undefined;
  const etiquettes = etiquettesJours(pf.valeurs.length);
  const pas = Math.max(1, Math.round(pf.valeurs.length / 10));
  const lignesTableau = pf.valeurs.map((_, i) => i).filter((i) => i % pas === 0 || i === pf.valeurs.length - 1);

  return (
    <Carte taille="normale">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-x-3 gap-y-2">
        <h3 className="flex items-center gap-1 text-titre font-semibold tracking-tight">
          Évolution du portefeuille
          <Infobulle libelle="Comment lire ce graphique">
            {bande
              ? "La courbe est la trajectoire médiane. La zone claire contient 90 % des trajectoires simulées."
              : "Une trajectoire possible parmi d'autres. Activez Monte-Carlo pour voir la fourchette des issues."}
          </Infobulle>
        </h3>
        <Legende series={series} bande={bande ? { nom: bande.nom, couleur: "var(--series-1)" } : undefined} reference="Capital de départ" />
      </div>
      <div className="mb-5 grid grid-cols-1 gap-2 sm:grid-cols-3">
        {series.map((se, i) => (
          <CarteFinale key={se.nom} nom={se.nom} couleur={se.couleur} valeur={se.valeurs[se.valeurs.length - 1] ?? pf.capital} capital={pf.capital} principale={i === 0} delai={i * 0.05} />
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
      <Depliable libelle="Voir les valeurs en tableau" libelleOuvert="Masquer le tableau" className="mt-3">
        <div className="overflow-x-auto">
          <table className="w-full min-w-96 text-right text-xs tabular-nums">
            <thead className="text-muted">
              <tr>
                <th className="py-1.5 text-left font-medium">Jour</th>
                {series.map((se) => (
                  <th key={se.nom} className="py-1.5 pl-3 font-medium">
                    {se.nom}
                  </th>
                ))}
                {bande && <th className="py-1.5 pl-3 font-medium">Fourchette 90 %</th>}
              </tr>
            </thead>
            <tbody>
              {lignesTableau.map((i) => (
                <tr key={i} className="border-t border-line">
                  <td className="py-1.5 text-left">{etiquettes[i]}</td>
                  {series.map((se) => (
                    <td key={se.nom} className="py-1.5 pl-3">
                      {se.valeurs[i] != null ? euros(se.valeurs[i] as number) : "—"}
                    </td>
                  ))}
                  {bande && (
                    <td className="py-1.5 pl-3">
                      {euros(bande.bas[i] as number)} – {euros(bande.haut[i] as number)}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Depliable>
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
  /** Applique une repartition proposee par « Proteger mon portefeuille » (affiche seulement s'il est fourni). */
  onAppliquerProtection?: (allocations: Record<string, number>) => void;
};

export function Resultats({ reponse, scenario, noms, lienPartage, onComparer, onAppliquerProtection }: Props) {
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
            whileTap={{ scale: 0.97 }}
            className="flex shrink-0 items-center gap-1.5 self-start rounded-controle border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink"
          >
            <GitCompareArrows className="size-3.5" aria-hidden />
            Comparer avec un autre scénario
          </motion.button>
        )}
      </Apparition>

      <Sommaire entrees={SOMMAIRE} />

      {reponse.prix_de_secours.length > 0 && (
        <Apparition role="status" className="flex gap-3 rounded-tuile border border-warn/30 bg-warn-soft px-4 py-3 text-sm">
          <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
          <span>Yahoo Finance n&apos;a pas répondu pour {reponse.prix_de_secours.map((x) => nomCourt(x.cle, x.nom)).join(", ")} : les dernières valeurs connues ont été utilisées.</span>
        </Apparition>
      )}

      <div className="flex flex-col gap-8">
        <Partie id={PARTIES.synthese} libelle="Vue d'ensemble">
          <Apparition delai={0.05}>
            <Synthese s={scenario} p={p} dateSimulation={reponse.date} />
          </Apparition>
        </Partie>

        <Partie id={PARTIES.evolution} libelle="Évolution du portefeuille">
          <Apparition delai={0.1}>
            <Evolution s={scenario} p={p} />
          </Apparition>
        </Partie>

        <Partie id={PARTIES.analyse} libelle="Analyse de l'IA">
          <Apparition auDefilement>
            <AnalyseIA s={scenario} calibration={p.calibration} noms={noms} conjoncture={reponse.conjoncture} />
          </Apparition>
        </Partie>

        <Partie id={PARTIES.risque} titre="Risque du portefeuille">
          <TuilesRisque
            m={scenario.metriques}
            tauxSansRisquePct={p.taux_sans_risque_pct}
            valeurs={scenario.portefeuille.valeurs}
            etiquette={(i) => (i === 0 ? "aujourd'hui" : `jour ${i}`)}
            precisionTrajectoire={scenario.portefeuille.valeurs_bas ? "La trajectoire médiane" : "La trajectoire simulée"}
          />
          <ListeAlertes alertes={scenario.alertes} />
        </Partie>

        {onAppliquerProtection && (
          <Apparition auDefilement>
            <Protection reponse={reponse} scenario={scenario} onAppliquer={onAppliquerProtection} />
          </Apparition>
        )}

        <Partie id={PARTIES.repartition} libelle="Répartition du portefeuille">
          <Apparition auDefilement>
            <Repartition allocations={scenario.allocations} />
          </Apparition>
        </Partie>

        <Partie id={PARTIES.detail} titre="Détail par actif">
          <Apparition auDefilement>
            <Carte taille="normale">
              <TitreCarte aide={`Variation estimée de chaque actif sur ${p.duree} jours${scenario.converti_eur ? ", en euros" : ""}.`}>Performance par actif</TitreCarte>
              <BarresPerformance lignes={scenario.actifs.map((a) => ({ cle: a.cle, nom: nomCourt(a.cle, a.nom), valeur: a.performance_pct }))} />
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
        </Partie>

        <Partie id={PARTIES.exports} libelle="Exporter et partager">
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
          <p className="px-1 text-aide leading-relaxed text-muted">
            Simulation hypothétique, pas un conseil en investissement : ces résultats sont des estimations d&apos;un modèle et d&apos;une IA, la réalité peut fortement diverger.{" "}
            <Link href="/methodologie" className="inline-flex items-center gap-0.5 font-medium text-accent-ink hover:underline">
              Comment c&apos;est calculé
              <ArrowRight className="size-3.5" aria-hidden />
            </Link>
          </p>
        </Partie>
      </div>
    </div>
  );
}
