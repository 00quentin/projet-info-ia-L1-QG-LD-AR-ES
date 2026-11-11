"use client";

import { TriangleAlert } from "lucide-react";
import type { ParametresSimulation, ReponseSimulation, ResultatScenario } from "@/lib/api";
import { euros, eurosCompacts, pourcent, pourcentSigne } from "@/lib/format";
import { ListeAlertes, TuilesRisque } from "@/components/resultats/Risque";
import { DetailPortefeuille } from "@/components/resultats/DetailPortefeuille";
import { Carte, Pastille, TitreCarte } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { BarresPerformance } from "@/components/charts/BarresPerformance";

function Synthese({ s, p }: { s: ResultatScenario; p: ParametresSimulation }) {
  const pf = s.portefeuille;
  const gain = pf.valeur_finale - pf.capital;
  const hausse = gain >= 0;
  const m = s.metriques;
  return (
    <Carte className="p-6 sm:p-7">
      <div className="flex flex-wrap items-center gap-1.5">
        {p.prix_reels && <Pastille ton="gain">● Prix réels</Pastille>}
        {p.calibration && s.analyse.evenement_reference && <Pastille ton="accent">Calibré sur : {s.analyse.evenement_reference}</Pastille>}
        {s.converti_eur && <Pastille>Converti en €</Pastille>}
        {p.monte_carlo && <Pastille>Monte-Carlo · {p.nb_simulations.toLocaleString("fr-FR")} trajectoires</Pastille>}
      </div>
      <p className="mt-5 text-sm text-ink-2">
        Valeur estimée de votre portefeuille dans <strong className="font-semibold text-ink">{p.duree} jours de bourse</strong>
      </p>
      <div className="mt-1.5 flex flex-wrap items-end gap-x-4 gap-y-2">
        <span className="text-5xl font-semibold tracking-tight sm:text-6xl">{euros(pf.valeur_finale)}</span>
        <span className={`mb-1.5 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-base font-semibold ${hausse ? "bg-gain-soft text-gain" : "bg-loss-soft text-loss"}`}>
          <span aria-hidden>{hausse ? "▲" : "▼"}</span>
          {pourcentSigne(pf.performance_pct)}
          <span className="font-medium opacity-80">
            ({hausse ? "+" : "−"}
            {euros(Math.abs(gain))})
          </span>
        </span>
      </div>
      <p className="mt-2 text-sm text-muted">
        Capital de départ {euros(pf.capital)} · profil {p.profil.split(" (")[0].toLowerCase()} · {s.allocations.length} actif{s.allocations.length > 1 ? "s" : ""} en portefeuille
      </p>
      {m.proba_perte != null && m.valeur_p5 != null && m.valeur_p95 != null && (
        <div className="mt-5 grid grid-cols-1 gap-3 border-t border-line pt-5 text-sm sm:grid-cols-3">
          <div>
            <div className="text-xs text-muted">Scénario défavorable (5 % des cas)</div>
            <div className="mt-0.5 text-lg font-semibold">{euros(m.valeur_p5)}</div>
          </div>
          <div>
            <div className="text-xs text-muted">Scénario favorable (5 % des cas)</div>
            <div className="mt-0.5 text-lg font-semibold">{euros(m.valeur_p95)}</div>
          </div>
          <div>
            <div className="text-xs text-muted">Probabilité de finir en perte</div>
            <div className="mt-0.5 text-lg font-semibold">{pourcent(m.proba_perte, 0)}</div>
          </div>
        </div>
      )}
    </Carte>
  );
}

function AnalyseIA({ s, calibration }: { s: ResultatScenario; calibration: boolean }) {
  const a = s.analyse;
  const refs = a.references_historiques.filter((r) => r.evenement);
  const fiabilites: Record<string, { libelle: string; ton: "gain" | "alerte" | "perte" }> = {
    elevee: { libelle: "Fiabilité élevée", ton: "gain" },
    moyenne: { libelle: "Fiabilité moyenne", ton: "alerte" },
    faible: { libelle: "Fiabilité faible", ton: "perte" },
  };
  const fiab = a.fiabilite?.niveau ? fiabilites[a.fiabilite.niveau] : undefined;
  return (
    <Carte className="p-6">
      <TitreCarte>Analyse de l&apos;IA</TitreCarte>
      <p className="text-[15px] leading-relaxed text-ink-2">{a.explication ?? "Analyse non disponible."}</p>
      <dl className="mt-5 grid grid-cols-2 gap-4 border-t border-line pt-5">
        <div>
          <dt className="text-xs text-muted">Inflation (variation estimée)</dt>
          <dd className="mt-0.5 text-xl font-semibold">{pourcentSigne(a.inflation, 2).replace(" %", " pt")}</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Taux directeurs (variation estimée)</dt>
          <dd className="mt-0.5 text-xl font-semibold">{pourcentSigne(a.taux_directeurs, 2).replace(" %", " pt")}</dd>
        </div>
      </dl>
      {calibration && (refs.length > 0 || fiab) && (
        <div className="mt-5 border-t border-line pt-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-medium text-muted">Précédents historiques utilisés</span>
            {fiab && <Pastille ton={fiab.ton}>{fiab.libelle}</Pastille>}
          </div>
          {refs.length > 0 && (
            <ul className="mt-3 flex flex-col gap-2">
              {refs.map((r) => (
                <li key={r.evenement} className="grid grid-cols-[1fr_6rem_3rem] items-center gap-3 text-sm">
                  <span className="truncate">{r.evenement}</span>
                  <span className="h-1.5 overflow-hidden rounded-full bg-surface-2" aria-hidden>
                    <span className="block h-full rounded-full bg-accent" style={{ width: `${Math.round((r.poids ?? 0) * 100)}%` }} />
                  </span>
                  <span className="text-right text-ink-2 tabular-nums">{Math.round((r.poids ?? 0) * 100)} %</span>
                </li>
              ))}
            </ul>
          )}
          {a.fiabilite?.raison && <p className="mt-3 text-xs leading-relaxed text-muted">{a.fiabilite.raison}</p>}
        </div>
      )}
    </Carte>
  );
}

function Evolution({ s, p }: { s: ResultatScenario; p: ParametresSimulation }) {
  const pf = s.portefeuille;
  const couleursBenchmarks = ["var(--series-2)", "var(--series-3)"];
  const series: SerieLigne[] = [
    { nom: "Votre portefeuille", couleur: "var(--series-1)", valeurs: pf.valeurs, principale: true },
    ...s.benchmarks.map((b, i) => ({ nom: b.nom.split(" (")[0], couleur: couleursBenchmarks[i % 2], valeurs: b.valeurs })),
  ];
  const bande = pf.valeurs_bas && pf.valeurs_haut ? { bas: pf.valeurs_bas, haut: pf.valeurs_haut, nom: "90 % des trajectoires" } : undefined;
  const etiquettes = pf.valeurs.map((_, i) => (i === 0 ? "Aujourd'hui" : `Jour ${i}`));
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

export function Resultats({ reponse, scenario }: { reponse: ReponseSimulation; scenario: ResultatScenario }) {
  const p = reponse.parametres;
  return (
    <div className="apparition flex flex-col gap-4">
      <p className="text-sm leading-relaxed text-ink-2">
        <span className="font-medium text-ink">Scénario :</span> {scenario.scenario}
      </p>

      {reponse.prix_de_secours.length > 0 && (
        <div role="status" className="flex gap-3 rounded-xl border border-warn/30 bg-warn-soft px-4 py-3 text-sm">
          <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
          <span>
            Yahoo Finance n&apos;a pas répondu pour {reponse.prix_de_secours.map((x) => x.nom).join(", ")} : les dernières valeurs connues ont été utilisées.
          </span>
        </div>
      )}

      <Synthese s={scenario} p={p} />
      <AnalyseIA s={scenario} calibration={p.calibration} />
      <Evolution s={scenario} p={p} />

      <div className="flex flex-col gap-3">
        <h3 className="mt-2 text-[15px] font-semibold tracking-tight">Le risque de ce portefeuille</h3>
        <TuilesRisque m={scenario.metriques} />
        <ListeAlertes alertes={scenario.alertes} />
      </div>

      <Carte className="p-6">
        <TitreCarte aide={`Variation estimée de chaque actif sur ${p.duree} jours${scenario.converti_eur ? ", en euros" : ""}.`}>Performance par actif</TitreCarte>
        <BarresPerformance lignes={scenario.actifs.map((a) => ({ cle: a.cle, nom: a.nom, valeur: a.performance_pct }))} />
      </Carte>

      <DetailPortefeuille
        allocations={scenario.allocations}
        capital={scenario.portefeuille.capital}
        valeurFinale={scenario.portefeuille.valeur_finale}
        performancePct={scenario.portefeuille.performance_pct}
      />

      <p className="px-1 text-xs leading-relaxed text-muted">
        Outil pédagogique : ces résultats sont des estimations issues d&apos;un modèle et d&apos;une IA, pas un conseil en investissement. La réalité peut fortement diverger.
      </p>
    </div>
  );
}
