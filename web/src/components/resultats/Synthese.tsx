"use client";

import { motion } from "motion/react";
import type { ParametresSimulation, ResultatScenario } from "@/lib/api";
import { euros, pourcent, pourcentSigne } from "@/lib/format";
import { Carte, Pastille } from "@/components/ui/Carte";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { EASE_SORTIE } from "@/components/motion/transitions";

/**
 * Jauge de la fourchette Monte-Carlo : du pire 5 % au meilleur 5 %, avec la mediane
 * et le capital de depart reperes dessus. Plus parlant que trois chiffres seuls.
 */
function Fourchette({ p5, mediane, p95, capital }: { p5: number; mediane: number; p95: number; capital: number }) {
  const min = Math.min(p5, capital);
  const max = Math.max(p95, capital);
  const etendue = max - min || 1;
  const pos = (v: number) => ((v - min) / etendue) * 100;
  return (
    <div className="mt-6" aria-hidden>
      <div className="relative h-2.5 rounded-full bg-surface-2">
        <motion.div
          className="absolute inset-y-0 rounded-full bg-gradient-to-r from-loss/70 via-accent/60 to-gain/70"
          style={{ left: `${pos(p5)}%`, width: `${pos(p95) - pos(p5)}%` }}
          initial={{ scaleX: 0, opacity: 0 }}
          animate={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: 0.9, ease: EASE_SORTIE, delay: 0.3 }}
        />
        <motion.div
          className="absolute -top-1 h-4.5 w-0.5 -translate-x-1/2 rounded-full bg-ink-2"
          style={{ left: `${pos(capital)}%` }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
        />
        <motion.div
          className="absolute top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-accent shadow"
          initial={{ left: `${pos(capital)}%`, scale: 0 }}
          animate={{ left: `${pos(mediane)}%`, scale: 1 }}
          transition={{ type: "spring", stiffness: 120, damping: 16, delay: 0.5 }}
        />
      </div>
      <div className="relative mt-2 h-4 text-[11px] text-muted">
        <span className="absolute -translate-x-1/2 whitespace-nowrap" style={{ left: `${Math.min(92, Math.max(8, pos(capital)))}%` }}>
          Départ
        </span>
      </div>
    </div>
  );
}

export function Synthese({ s, p }: { s: ResultatScenario; p: ParametresSimulation }) {
  const pf = s.portefeuille;
  const gain = pf.valeur_finale - pf.capital;
  const hausse = gain >= 0;
  const m = s.metriques;
  const avecFourchette = m.proba_perte != null && m.valeur_p5 != null && m.valeur_p95 != null && m.valeur_mediane != null;
  return (
    <Carte className="relative overflow-hidden p-6 sm:p-7">
      {/* Halo colore discret : vert si gain, rouge si perte */}
      <motion.div
        aria-hidden
        className={`pointer-events-none absolute -right-24 -top-24 size-72 rounded-full blur-3xl ${hausse ? "bg-gain/15" : "bg-loss/15"}`}
        initial={{ opacity: 0, scale: 0.6 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.2, ease: EASE_SORTIE }}
      />
      <div className="relative">
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
          <NombreAnime valeur={pf.valeur_finale} depuis={pf.capital} format={(v) => euros(v)} duree={1.4} className="text-5xl font-semibold tracking-tight sm:text-6xl" />
          <motion.span
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, duration: 0.4, ease: EASE_SORTIE }}
            className={`mb-1.5 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-base font-semibold ${hausse ? "bg-gain-soft text-gain" : "bg-loss-soft text-loss"}`}
          >
            <span aria-hidden>{hausse ? "▲" : "▼"}</span>
            {pourcentSigne(pf.performance_pct)}
            <span className="font-medium opacity-80">
              ({hausse ? "+" : "−"}
              {euros(Math.abs(gain))})
            </span>
          </motion.span>
        </div>
        <p className="mt-2 text-sm text-muted">
          Capital de départ {euros(pf.capital)} · profil {p.profil.split(" (")[0].toLowerCase()} · {s.allocations.length} actif{s.allocations.length > 1 ? "s" : ""} en portefeuille
        </p>
        {avecFourchette && (
          <>
            <Fourchette p5={m.valeur_p5!} mediane={m.valeur_mediane!} p95={m.valeur_p95!} capital={pf.capital} />
            <div className="mt-3 grid grid-cols-1 gap-3 border-t border-line pt-4 text-sm sm:grid-cols-3">
              <div>
                <div className="text-xs text-muted">Scénario défavorable (5 % des cas)</div>
                <NombreAnime valeur={m.valeur_p5!} depuis={pf.capital} format={(v) => euros(v)} className="mt-0.5 block text-lg font-semibold" />
              </div>
              <div>
                <div className="text-xs text-muted">Scénario favorable (5 % des cas)</div>
                <NombreAnime valeur={m.valeur_p95!} depuis={pf.capital} format={(v) => euros(v)} className="mt-0.5 block text-lg font-semibold" />
              </div>
              <div>
                <div className="text-xs text-muted">Probabilité de finir en perte</div>
                <NombreAnime valeur={m.proba_perte!} depuis={0} format={(v) => pourcent(v, 0)} className="mt-0.5 block text-lg font-semibold" />
              </div>
            </div>
          </>
        )}
      </div>
    </Carte>
  );
}
