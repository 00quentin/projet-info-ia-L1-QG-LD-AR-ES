"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { TrendingDown, TrendingUp } from "lucide-react";
import { lireMarchesPartages, type ParametresSimulation, type ResultatScenario } from "@/lib/api";
import { euros, pourcent, pourcentSigne } from "@/lib/format";
import { Carte } from "@/components/ui/Carte";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

/** "2026-11-12" ou "2026-11-12T18:03:00" -> "12/11" */
const jourMois = (iso: string) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;

/**
 * Date des cours utilises : la derniere cloture connue (celle du bandeau des marches),
 * a defaut le jour de la simulation.
 */
function useDateCours(dateSimulation: string): string {
  const [cloture, setCloture] = useState<string | null>(null);
  const [echec, setEchec] = useState(false);
  useEffect(() => {
    let actif = true;
    lireMarchesPartages()
      .then((m) => actif && (m.date ? setCloture(m.date) : setEchec(true)))
      .catch(() => actif && setEchec(true));
    return () => {
      actif = false;
    };
  }, []);
  return cloture ? jourMois(cloture) : echec ? jourMois(dateSimulation) : "";
}

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
          className="absolute inset-y-0 origin-left rounded-full bg-gradient-to-r from-loss/70 via-accent/60 to-gain/70"
          style={{ left: `${pos(p5)}%`, width: `${pos(p95) - pos(p5)}%` }}
          initial={{ scaleX: 0, opacity: 0 }}
          animate={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: DUREE.donnees, ease: EASE_SORTIE, delay: 0.2 }}
        />
        <div className="absolute -top-1 h-4.5 w-0.5 -translate-x-1/2 rounded-full bg-ink-2" style={{ left: `${pos(capital)}%` }} />
        <motion.div
          className="absolute top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-accent shadow-card"
          initial={{ left: `${pos(capital)}%`, opacity: 0 }}
          animate={{ left: `${pos(mediane)}%`, opacity: 1 }}
          transition={{ duration: DUREE.donnees, ease: EASE_SORTIE, delay: 0.3 }}
        />
      </div>
      <div className="relative mt-2 h-4 text-xs text-muted">
        <span className="absolute -translate-x-1/2 whitespace-nowrap" style={{ left: `${Math.min(92, Math.max(8, pos(capital)))}%` }}>
          Départ
        </span>
      </div>
    </div>
  );
}

/** Chiffre secondaire : apparait en fondu, sans compter (un seul compteur par ecran). */
function Chiffre({ libelle, children, delai }: { libelle: string; children: string; delai: number }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: DUREE.normale, ease: EASE_SORTIE, delay: delai }}>
      <div className="text-aide text-muted">{libelle}</div>
      <div className="mt-0.5 text-lg font-semibold tabular-nums">{children}</div>
    </motion.div>
  );
}

export function Synthese({ s, p, dateSimulation }: { s: ResultatScenario; p: ParametresSimulation; dateSimulation: string }) {
  const pf = s.portefeuille;
  const gain = pf.valeur_finale - pf.capital;
  const hausse = gain >= 0;
  const m = s.metriques;
  const avecFourchette = m.proba_perte != null && m.valeur_p5 != null && m.valeur_p95 != null && m.valeur_mediane != null;
  const dateCours = useDateCours(dateSimulation);
  const Tendance = hausse ? TrendingUp : TrendingDown;

  // Une seule ligne technique, neutre : ce qui a ete simule et avec quelles donnees.
  const technique = [
    "Simulation hypothétique",
    p.prix_reels ? (dateCours ? `cours du ${dateCours}` : "cours réels") : "prix de référence",
    s.converti_eur ? "en euros" : "en devise d'origine",
    p.monte_carlo ? `${p.nb_simulations.toLocaleString("fr-FR")} trajectoires` : "une trajectoire",
  ].join(" · ");

  return (
    <Carte taille="hero" className="relative overflow-hidden">
      {/* Halo colore discret : vert si gain, rouge si perte */}
      <motion.div
        aria-hidden
        className={`pointer-events-none absolute -right-24 -top-24 size-72 rounded-full blur-3xl ${hausse ? "bg-gain/15" : "bg-loss/15"}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: DUREE.lente * 2, ease: EASE_SORTIE }}
      />
      <div className="relative">
        <p className="text-sm text-ink-2">
          Valeur estimée de votre portefeuille dans <strong className="font-semibold text-ink">{p.duree} jours de bourse</strong>
        </p>
        <div className="mt-1.5 flex flex-wrap items-end gap-x-4 gap-y-2">
          <NombreAnime valeur={pf.valeur_finale} depuis={pf.capital} format={(v) => euros(v)} duree={1.2} className="text-5xl font-semibold tracking-tight tabular-nums sm:text-6xl" />
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: DUREE.normale, ease: EASE_SORTIE }}
            className={`mb-1.5 inline-flex items-center gap-1.5 rounded-controle px-2.5 py-1 text-base font-semibold tabular-nums ${hausse ? "bg-gain-soft text-gain" : "bg-loss-soft text-loss"}`}
          >
            <Tendance className="size-4" aria-hidden />
            {pourcentSigne(pf.performance_pct)}
            <span className="font-medium">
              ({hausse ? "+" : "−"}
              {euros(Math.abs(gain))})
            </span>
          </motion.span>
        </div>
        <p className="mt-2 text-sm text-ink-2">
          Capital de départ {euros(pf.capital)} · profil {p.profil.split(" (")[0].toLowerCase()} · {s.allocations.length} actif{s.allocations.length > 1 ? "s" : ""} en portefeuille
        </p>
        <p className="mt-1 text-aide text-muted">{technique}</p>
        {avecFourchette && (
          <>
            <Fourchette p5={m.valeur_p5!} mediane={m.valeur_mediane!} p95={m.valeur_p95!} capital={pf.capital} />
            <div className="mt-3 grid grid-cols-1 gap-3 border-t border-line pt-4 sm:grid-cols-3">
              <Chiffre libelle="Scénario défavorable (5 % des cas)" delai={0.3}>
                {euros(m.valeur_p5!)}
              </Chiffre>
              <Chiffre libelle="Scénario favorable (5 % des cas)" delai={0.35}>
                {euros(m.valeur_p95!)}
              </Chiffre>
              <Chiffre libelle="Probabilité de finir en perte" delai={0.4}>
                {pourcent(m.proba_perte!, 0)}
              </Chiffre>
            </div>
          </>
        )}
      </div>
    </Carte>
  );
}
