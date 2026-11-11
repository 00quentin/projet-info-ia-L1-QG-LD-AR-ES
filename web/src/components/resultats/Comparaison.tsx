"use client";

import { motion } from "motion/react";
import { ArrowRight, Crown, Star } from "lucide-react";
import type { ParametresSimulation, ResultatScenario } from "@/lib/api";
import { euros, eurosCompacts, nombreSigne, pourcent, pourcentSigne } from "@/lib/format";
import { Carte, Pastille, TitreCarte } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { Apparition, Cascade, ElementCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { RESSORT } from "@/components/motion/transitions";
import { BoutonsExport } from "@/components/exports/BoutonsExport";
import { etiquettesJours } from "@/components/Resultats";

const COULEURS = ["var(--series-1)", "var(--series-2)", "var(--series-3)"];
const RANGS = ["1er", "2e", "3e"];
const EGALITE_PTS = 0.01;

type Props = {
  scenarios: ResultatScenario[];
  parametres: ParametresSimulation;
  lienPartage?: string;
  onVoirDetail: (label: string) => void;
};

type LigneMetrique = { nom: string; valeur: (s: ResultatScenario) => number; format: (v: number) => string; plusGrandEstMieux: boolean; aide: string };

const METRIQUES: LigneMetrique[] = [
  { nom: "Performance", valeur: (s) => s.portefeuille.performance_pct, format: (v) => pourcentSigne(v, 2), plusGrandEstMieux: true, aide: "Gain ou perte sur l'horizon" },
  { nom: "Volatilité annualisée", valeur: (s) => s.metriques.vol_ann, format: (v) => pourcent(v, 2), plusGrandEstMieux: false, aide: "Plus bas = parcours plus calme" },
  { nom: "Ratio de Sharpe", valeur: (s) => s.metriques.sharpe, format: (v) => nombreSigne(v), plusGrandEstMieux: true, aide: "Plus haut = risque mieux payé" },
  { nom: "Perte maximale", valeur: (s) => s.metriques.max_dd, format: (v) => `−${pourcent(Math.abs(v), 2)}`, plusGrandEstMieux: false, aide: "Pire chute en cours de route" },
  { nom: "VaR 95 % (1 jour)", valeur: (s) => Math.abs(s.metriques.var_95), format: (v) => `−${pourcent(v, 2)}`, plusGrandEstMieux: false, aide: "Perte d'un mauvais jour" },
];

export function Comparaison({ scenarios, parametres: p, lienPartage, onVoirDetail }: Props) {
  const capital = scenarios[0].portefeuille.capital;
  const classement = [...scenarios].sort((a, b) => b.portefeuille.performance_pct - a.portefeuille.performance_pct);
  const rang = new Map(classement.map((s, i) => [s.label, i]));
  const [premier, second] = classement;
  const ecart = premier.portefeuille.performance_pct - second.portefeuille.performance_pct;
  const egalite = ecart < EGALITE_PTS;
  const couleur = new Map(scenarios.map((s, i) => [s.label, COULEURS[i]]));

  const series: SerieLigne[] = scenarios.map((s) => ({ nom: `Scénario ${s.label}`, couleur: couleur.get(s.label)!, valeurs: s.portefeuille.valeurs }));
  const etiquettes = etiquettesJours(scenarios[0].portefeuille.valeurs.length);

  return (
    <div className="flex flex-col gap-4">
      <Apparition>
        <h2 className="text-xl font-semibold tracking-tight">{scenarios.length >= 3 ? "Tournoi" : "Duel"} de scénarios</h2>
        <p className="mt-1 text-sm text-ink-2">
          Même portefeuille ({p.profil.split(" (")[0].toLowerCase()}, {euros(capital)}), même horizon ({p.duree} jours) : seule la cause change.
        </p>
      </Apparition>

      {/* Cartes des scenarios */}
      <Cascade className={`grid grid-cols-1 gap-3 ${scenarios.length >= 3 ? "lg:grid-cols-3" : "sm:grid-cols-2"}`}>
        {scenarios.map((s) => {
          const r = rang.get(s.label)!;
          const hausse = s.portefeuille.performance_pct >= 0;
          return (
            <ElementCascade key={s.label} className="min-w-0">
              <motion.div whileHover={{ y: -3 }} transition={RESSORT} className={`relative flex h-full flex-col rounded-2xl border bg-surface p-5 shadow-card ${r === 0 && !egalite ? "border-accent/50" : "border-line"}`}>
                <div className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2 text-sm font-semibold">
                    <span className="inline-block h-0.5 w-4 rounded-full" style={{ background: couleur.get(s.label) }} />
                    Scénario {s.label}
                  </span>
                  <Pastille ton={r === 0 && !egalite ? "accent" : "neutre"}>
                    {r === 0 && !egalite && <Crown className="size-3" aria-hidden />}
                    {egalite && r < 2 ? "Égalité" : RANGS[r]}
                  </Pastille>
                </div>
                <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-ink-2" title={s.scenario}>
                  {s.scenario}
                </p>
                <div className="mt-auto pt-4">
                  <NombreAnime valeur={s.portefeuille.valeur_finale} depuis={capital} format={(v) => euros(v)} className="block text-2xl font-semibold tracking-tight" />
                  <div className="mt-1 flex items-center justify-between gap-2">
                    <span className={`text-sm font-semibold ${hausse ? "text-gain" : "text-loss"}`}>
                      <span aria-hidden>{hausse ? "▲ " : "▼ "}</span>
                      {pourcentSigne(s.portefeuille.performance_pct)}
                    </span>
                    <button type="button" onClick={() => onVoirDetail(s.label)} className="group flex items-center gap-1 text-xs font-medium text-accent-ink">
                      Voir le détail
                      <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" aria-hidden />
                    </button>
                  </div>
                </div>
              </motion.div>
            </ElementCascade>
          );
        })}
      </Cascade>

      {/* Verdict */}
      <Apparition delai={0.25} className="rounded-xl border border-line bg-surface-2/60 px-4 py-3 text-sm">
        {egalite ? (
          <span>Égalité : les scénarios {premier.label} et {second.label} mènent au même résultat pour ce portefeuille.</span>
        ) : (
          <span>
            <strong className="font-semibold">Le scénario {premier.label} est le plus favorable</strong> à ce portefeuille, avec{" "}
            {nombreSigne(ecart, 2).replace("−", "")} point{ecart >= 2 ? "s" : ""} d&apos;avance sur le scénario {second.label}.
          </span>
        )}
      </Apparition>

      {/* Evolution comparee */}
      <Apparition auDefilement>
        <Carte className="p-6">
          <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
            <TitreCarte aide="Valeur du même portefeuille dans chaque scénario (trajectoire médiane si Monte-Carlo).">Évolution comparée</TitreCarte>
            <Legende series={series} reference="Capital de départ" />
          </div>
          <GraphiqueLignes
            series={series}
            etiquettesX={etiquettes}
            formatY={eurosCompacts}
            formatValeur={(v) => euros(v)}
            reference={{ valeur: capital, nom: "Capital de départ" }}
            description={`Évolution comparée du portefeuille dans ${scenarios.length} scénarios : ${scenarios.map((s) => `${s.label} ${pourcentSigne(s.portefeuille.performance_pct)}`).join(", ")}.`}
          />
        </Carte>
      </Apparition>

      {/* Tableau des metriques */}
      <Apparition auDefilement>
        <Carte className="p-6">
          <TitreCarte aide="La valeur la plus favorable de chaque ligne est marquée d'une étoile.">Comparatif des métriques de risque</TitreCarte>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[30rem] text-sm tabular-nums">
              <thead className="text-xs text-muted">
                <tr>
                  <th className="pb-2 text-left font-medium">Métrique</th>
                  {scenarios.map((s) => (
                    <th key={s.label} className="pb-2 text-right font-medium">
                      Scénario {s.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {METRIQUES.map((m) => {
                  const valeurs = scenarios.map(m.valeur);
                  const meilleure = m.plusGrandEstMieux ? Math.max(...valeurs) : Math.min(...valeurs);
                  const unique = valeurs.filter((v) => Math.abs(v - meilleure) < 1e-9).length === 1;
                  return (
                    <tr key={m.nom} className="border-t border-line">
                      <td className="py-2.5 pr-3">
                        <span className="block">{m.nom}</span>
                        <span className="block text-xs text-muted">{m.aide}</span>
                      </td>
                      {valeurs.map((v, i) => {
                        const best = unique && Math.abs(v - meilleure) < 1e-9;
                        return (
                          <td key={scenarios[i].label} className="py-2.5 text-right">
                            <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 ${best ? "bg-gain-soft font-semibold text-gain" : ""}`}>
                              {best && <Star className="size-3 fill-current" aria-label="Meilleure valeur" />}
                              <span className={best ? "" : "text-ink"}>{m.format(v)}</span>
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Carte>
      </Apparition>

      {/* Classement */}
      <Apparition auDefilement>
        <Carte className="p-6">
          <TitreCarte>Classement</TitreCarte>
          <ol className="flex flex-col gap-2">
            {classement.map((s, i) => {
              const retard = s.portefeuille.performance_pct - premier.portefeuille.performance_pct;
              return (
                <motion.li
                  key={s.label}
                  layout
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                  className="flex items-center gap-3 rounded-xl bg-surface-2/60 px-4 py-3 text-sm"
                >
                  <span className={`grid size-7 shrink-0 place-items-center rounded-full text-xs font-bold ${i === 0 ? "bg-accent text-white" : "bg-surface text-ink-2"}`}>{i + 1}</span>
                  <span className="min-w-0 flex-1">
                    <strong className="font-semibold">Scénario {s.label}</strong>
                    <span className="text-ink-2"> · {pourcentSigne(s.portefeuille.performance_pct, 2)}</span>
                    {i > 0 && <span className="text-muted"> · {pourcentSigne(retard, 2).replace(" %", " pts")} par rapport au 1er</span>}
                  </span>
                  <span className="hidden truncate text-xs text-muted sm:block sm:max-w-[45%]">{s.scenario}</span>
                </motion.li>
              );
            })}
          </ol>
        </Carte>
      </Apparition>

      <Apparition auDefilement>
        <BoutonsExport
          csv={{
            nomFichier: "quant_terminal_comparaison",
            titreColonneEtiquette: "jour",
            etiquettes: scenarios[0].portefeuille.valeurs.map((_, i) => String(i)),
            colonnes: scenarios.map((s) => ({ nom: `valeur_portefeuille_${s.label}_eur`, valeurs: s.portefeuille.valeurs })),
          }}
          lienPartage={lienPartage}
        />
      </Apparition>
    </div>
  );
}
