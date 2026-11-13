"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronDown, Play, Plus, Sparkles, X } from "lucide-react";
import type { Catalogue } from "@/lib/api";
import { Interrupteur } from "@/components/ui/Carte";
import { ChoixPortefeuille, portefeuilleInitial, validerPortefeuille, type ValeurPortefeuille } from "@/components/formulaire/ChoixPortefeuille";
import { champ, titreSection } from "@/components/formulaire/styles";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

export type Reglages = {
  /** 1 a 3 scenarios : au-dela d'un, les resultats sont compares. */
  scenarios: string[];
  portefeuille: ValeurPortefeuille;
  duree: number;
  modele: string;
  monteCarlo: boolean;
  prixReels: boolean;
  calibration: boolean;
  convertirEur: boolean;
};

const SCENARIO_LONGUEUR_MIN = 10;
const SCENARIO_LONGUEUR_MAX = 1000;

const DESCRIPTIONS_MODELE: Record<string, string> = {
  Probabiliste: "Variations quotidiennes classiques (loi normale)",
  Historique: "Rejoue de vraies séances de bourse, chocs violents inclus",
  Machine: "Tendance qui s'auto-entretient et s'accélère",
};

export function reglagesInitiaux(catalogue: Catalogue): Reglages {
  return {
    scenarios: [catalogue.scenarios_par_defaut[0]],
    portefeuille: portefeuilleInitial(catalogue),
    duree: catalogue.horizon.defaut,
    modele: catalogue.modeles[0],
    monteCarlo: true,
    prixReels: true,
    calibration: true,
    convertirEur: true,
  };
}

/** Message d'erreur a afficher, ou null si la demande peut partir. */
export function validerReglages(r: Reglages, catalogue: Catalogue): string | null {
  const court = r.scenarios.findIndex((s) => s.trim().length < SCENARIO_LONGUEUR_MIN);
  if (court >= 0) {
    return r.scenarios.length > 1
      ? `Décrivez le scénario ${catalogue.labels_scenarios[court]} en au moins 10 caractères.`
      : "Décrivez votre scénario en au moins 10 caractères.";
  }
  return validerPortefeuille(r.portefeuille, catalogue);
}

type Props = {
  catalogue: Catalogue;
  reglages: Reglages;
  onChange: (r: Reglages) => void;
  onLancer: () => void;
  enCours: boolean;
};

export function FormulaireSimulation({ catalogue, reglages: r, onChange, onLancer, enCours }: Props) {
  const maj = (partiel: Partial<Reglages>) => onChange({ ...r, ...partiel });
  const erreur = validerReglages(r, catalogue);
  const labels = catalogue.labels_scenarios;
  const max = labels.length;
  // Les scenarios rapides remplissent le dernier champ utilise.
  const [actif, setActif] = useState(0);
  const [optionsOuvertes, setOptionsOuvertes] = useState(false);
  const idGroupe = useId();
  const idOptions = useId();

  function definirNombre(nb: number) {
    const scenarios = Array.from({ length: nb }, (_, i) => r.scenarios[i] ?? catalogue.scenarios_par_defaut[i] ?? "");
    maj({ scenarios });
    setActif(Math.min(actif, nb - 1));
  }

  function majScenario(i: number, texte: string) {
    maj({ scenarios: r.scenarios.map((s, j) => (j === i ? texte : s)) });
  }

  function retirerScenario(i: number) {
    maj({ scenarios: r.scenarios.filter((_, j) => j !== i) });
    setActif(0);
  }

  return (
    <form
      noValidate
      className="flex flex-col gap-7"
      onSubmit={(e) => {
        e.preventDefault();
        if (!erreur && !enCours) onLancer();
      }}
    >
      {/* 1. Scenario(s) */}
      <fieldset className="flex flex-col gap-3">
        <legend className={titreSection}>1 · {r.scenarios.length > 1 ? "Vos scénarios" : "Votre scénario"}</legend>
        <div className="flex items-center justify-between gap-3">
          <span id={`${idGroupe}-nb-libelle`} className="text-xs text-ink-2">
            Comparer plusieurs scénarios
          </span>
          <div role="radiogroup" aria-labelledby={`${idGroupe}-nb-libelle`} className="flex rounded-lg bg-surface-2 p-0.5 text-xs font-semibold">
            {Array.from({ length: max }, (_, i) => i + 1).map((nb) => {
              const choisi = r.scenarios.length === nb;
              return (
                <button
                  key={nb}
                  type="button"
                  role="radio"
                  aria-checked={choisi}
                  aria-label={nb === 1 ? "Un seul scénario" : `Comparer ${nb} scénarios`}
                  title={nb === 1 ? "Un seul scénario" : `Comparer ${nb} scénarios`}
                  onClick={() => definirNombre(nb)}
                  className={`relative w-9 rounded-md py-1 tabular-nums transition-colors ${choisi ? "text-ink" : "text-muted hover:text-ink"}`}
                >
                  {choisi && <motion.span layoutId={`${idGroupe}-nb`} className="absolute inset-0 rounded-md bg-surface shadow-sm" transition={RESSORT} />}
                  <span className="relative">{nb}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col gap-2.5">
          <AnimatePresence initial={false}>
            {r.scenarios.map((texte, i) => (
              <motion.div
                key={labels[i]}
                layout
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
                className="overflow-hidden"
              >
                <div className="relative">
                  {r.scenarios.length > 1 ? (
                    <div className="mb-1.5 flex items-center justify-between">
                      <label htmlFor={`scenario-${i}`} className="flex items-center gap-2 text-sm font-medium">
                        <span aria-hidden className="grid size-5 place-items-center rounded-md bg-accent-soft text-[11px] font-semibold text-accent-ink">
                          {labels[i]}
                        </span>
                        Scénario {labels[i]}
                      </label>
                      {i > 0 && (
                        <button type="button" onClick={() => retirerScenario(i)} aria-label={`Retirer le scénario ${labels[i]}`} className="grid size-6 place-items-center rounded-md text-muted transition hover:bg-surface-2 hover:text-loss">
                          <X className="size-3.5" aria-hidden />
                        </button>
                      )}
                    </div>
                  ) : (
                    <label htmlFor={`scenario-${i}`} className="sr-only">
                      Événement économique à simuler
                    </label>
                  )}
                  <textarea
                    id={`scenario-${i}`}
                    rows={r.scenarios.length > 1 ? 3 : 4}
                    maxLength={SCENARIO_LONGUEUR_MAX}
                    value={texte}
                    onFocus={() => setActif(i)}
                    onChange={(e) => majScenario(i, e.target.value)}
                    placeholder="Ex. : la BCE baisse ses taux de 1 point par surprise pour relancer l'économie…"
                    className={`${champ} resize-y leading-relaxed ${actif === i && r.scenarios.length > 1 ? "border-accent/60" : ""}`}
                  />
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {r.scenarios.length < max && r.scenarios.length > 1 && (
          <motion.button
            type="button"
            layout
            whileTap={{ scale: 0.97 }}
            onClick={() => definirNombre(r.scenarios.length + 1)}
            className="flex items-center justify-center gap-1.5 rounded-xl border border-dashed border-line-strong py-2 text-sm font-medium text-ink-2 transition hover:border-accent hover:text-accent-ink"
          >
            <Plus className="size-4" aria-hidden />
            Ajouter le scénario {labels[r.scenarios.length]}
          </motion.button>
        )}

        <p className="text-xs leading-relaxed text-muted">
          {r.scenarios.length > 1
            ? `Les scénarios rapides remplissent le scénario ${labels[actif]}. Même portefeuille pour tous : seule la cause change.`
            : "Plus vous êtes précis (pays, secteur, ampleur, durée), plus l'analyse est pertinente."}
        </p>
        <div className="flex flex-wrap gap-1.5">
          {catalogue.scenarios_rapides.map((s) => {
            const choisi = r.scenarios[actif] === s.texte;
            return (
              <motion.button
                key={s.titre}
                type="button"
                whileTap={{ scale: 0.94 }}
                whileHover={{ y: -1 }}
                onClick={() => majScenario(actif, s.texte)}
                aria-pressed={choisi}
                className="rounded-full border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink aria-pressed:border-accent aria-pressed:bg-accent-soft aria-pressed:text-accent-ink"
              >
                {s.titre}
              </motion.button>
            );
          })}
        </div>
      </fieldset>

      {/* 2. Portefeuille */}
      <fieldset className="flex flex-col gap-3">
        <legend className={`${titreSection} mb-3`}>2 · Votre portefeuille</legend>
        <ChoixPortefeuille catalogue={catalogue} valeur={r.portefeuille} onChange={(portefeuille) => maj({ portefeuille })} />
      </fieldset>

      {/* 3. Options */}
      <div>
        <button
          type="button"
          aria-expanded={optionsOuvertes}
          aria-controls={idOptions}
          onClick={() => setOptionsOuvertes((o) => !o)}
          className={`flex w-full items-center justify-between ${titreSection}`}
        >
          3 · Options avancées
          <motion.span animate={{ rotate: optionsOuvertes ? 180 : 0 }} transition={RESSORT}>
            <ChevronDown className="size-4" aria-hidden />
          </motion.span>
        </button>
        <AnimatePresence initial={false}>
          {optionsOuvertes && (
            <motion.div
              id={idOptions}
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
              className="overflow-hidden"
            >
              <div className="flex flex-col gap-4 pt-4">
                <div>
                  <label htmlFor="duree" className="mb-1.5 flex items-center justify-between text-sm font-medium">
                    Horizon
                    <span className="font-normal text-ink-2 tabular-nums">{r.duree} jours de bourse</span>
                  </label>
                  <input
                    id="duree"
                    type="range"
                    min={catalogue.horizon.min}
                    max={catalogue.horizon.max}
                    step={catalogue.horizon.pas}
                    value={r.duree}
                    onChange={(e) => maj({ duree: Number(e.target.value) })}
                    className="w-full accent-(--accent)"
                  />
                </div>
                <div>
                  <label htmlFor="modele" className="mb-1.5 block text-sm font-medium">
                    Comportement du marché
                  </label>
                  <select id="modele" value={r.modele} onChange={(e) => maj({ modele: e.target.value })} className={champ}>
                    {catalogue.modeles.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                  <AnimatePresence mode="wait" initial={false}>
                    <motion.p key={r.modele} initial={{ opacity: 0, y: -3 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: DUREE.rapide }} className="mt-1.5 text-xs text-muted">
                      {DESCRIPTIONS_MODELE[r.modele.split(" ")[0]]}
                    </motion.p>
                  </AnimatePresence>
                </div>
                <div className="divide-y divide-line">
                  <Interrupteur
                    actif={r.monteCarlo}
                    onChange={(v) => maj({ monteCarlo: v })}
                    libelle={`Monte-Carlo (${catalogue.nb_simulations_monte_carlo.toLocaleString("fr-FR")} trajectoires)`}
                    aide="Affiche la fourchette des issues possibles et la probabilité de perte."
                  />
                  <Interrupteur actif={r.convertirEur} onChange={(v) => maj({ convertirEur: v })} libelle="Convertir en euros" aide="Tient compte du taux de change, comme le vivrait un investisseur européen." />
                  <Interrupteur actif={r.calibration} onChange={(v) => maj({ calibration: v })} libelle="Calibration historique" aide="L'IA s'ancre sur les amplitudes de crises réelles (2008, COVID, 2022…)." />
                  <Interrupteur actif={r.prixReels} onChange={(v) => maj({ prixReels: v })} libelle="Prix de marché actuels" aide="Part des dernières clôtures et des volatilités réelles (Yahoo Finance)." />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="sticky bottom-0 z-10 -mx-5 -mb-5 flex flex-col gap-2 rounded-b-2xl border-t border-line bg-surface/95 px-5 py-4 backdrop-blur">
        <AnimatePresence>
          {erreur && (
            <motion.p role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="text-xs text-warn">
              {erreur}
            </motion.p>
          )}
        </AnimatePresence>
        <motion.button
          type="submit"
          disabled={!!erreur || enCours}
          whileHover={!erreur && !enCours ? { scale: 1.01 } : undefined}
          whileTap={!erreur && !enCours ? { scale: 0.98 } : undefined}
          className="relative flex h-11 items-center justify-center gap-2 overflow-hidden rounded-xl bg-accent text-sm font-semibold text-white shadow-[0_6px_20px_-6px_var(--accent)] transition-[filter,opacity] hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.span key={enCours ? "attente" : "repos"} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: DUREE.rapide }} className="flex items-center gap-2">
              {enCours ? <Sparkles className="size-4 animate-pulse" aria-hidden /> : <Play className="size-4" aria-hidden />}
              {enCours ? "Analyse en cours…" : r.scenarios.length > 1 ? `Comparer les ${r.scenarios.length} scénarios` : "Lancer la simulation"}
            </motion.span>
          </AnimatePresence>
        </motion.button>
      </div>
    </form>
  );
}
