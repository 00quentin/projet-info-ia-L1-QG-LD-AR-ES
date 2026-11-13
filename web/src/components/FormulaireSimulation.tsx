"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronDown, GitCompareArrows, Loader2, Play, Plus, Settings2, X } from "lucide-react";
import type { Catalogue } from "@/lib/api";
import { Interrupteur } from "@/components/ui/Carte";
import { ChoixPortefeuille, portefeuilleInitial, validerPortefeuille, type ValeurPortefeuille } from "@/components/formulaire/ChoixPortefeuille";
import { barreLancement, boutonPrincipal, champ, puce, titreSection } from "@/components/formulaire/styles";
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
/** Scenarios rapides visibles d'emblee ; les autres sont derriere « Plus d'idees ». */
const SCENARIOS_RAPIDES_VISIBLES = 4;
const JOURS_BOURSE_PAR_MOIS = 21;
const MOIS_PAR_AN = 12;

// Noms grand public des modeles ; la valeur envoyee a l'API reste celle du catalogue.
const MODELES: Record<string, { nom: string; description: string }> = {
  Probabiliste: { nom: "Classique", description: "Variations quotidiennes classiques (loi normale)." },
  Historique: { nom: "Crises réelles", description: "Rejoue de vraies séances de bourse, chocs violents inclus." },
  Machine: { nom: "Emballement", description: "Tendance qui s'auto-entretient et s'accélère." },
};
const presentationModele = (m: string) => MODELES[m.split(" ")[0]] ?? { nom: m.split(" (")[0], description: "" };

/** « ≈ 5 mois » pour 100 jours de bourse. */
export function equivalentDuree(jours: number): string {
  const mois = Math.max(1, Math.round(jours / JOURS_BOURSE_PAR_MOIS));
  return mois >= MOIS_PAR_AN ? "≈ 1 an" : `≈ ${mois} mois`;
}

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
  const [plusIdees, setPlusIdees] = useState(false);
  const idOptions = useId();
  const idModele = useId();
  const idGroupe = useId();

  const rapides = catalogue.scenarios_rapides;
  const indexChoisi = rapides.findIndex((s) => s.texte === r.scenarios[actif]);
  // Un scenario rapide deja choisi parmi les « autres idees » reste visible.
  const idees = plusIdees || indexChoisi >= SCENARIOS_RAPIDES_VISIBLES ? rapides : rapides.slice(0, SCENARIOS_RAPIDES_VISIBLES);
  const modele = presentationModele(r.modele);

  function definirNombre(nb: number) {
    const scenarios = Array.from({ length: nb }, (_, i) => r.scenarios[i] ?? catalogue.scenarios_par_defaut[i] ?? "");
    maj({ scenarios });
    setActif(Math.min(actif, nb - 1));
    if (nb > r.scenarios.length) requestAnimationFrame(() => document.getElementById(`scenario-${nb - 1}`)?.focus());
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
      aria-label="Paramètres de la simulation"
      className="flex flex-col gap-6"
      onSubmit={(e) => {
        e.preventDefault();
        if (!erreur && !enCours) onLancer();
      }}
    >
      {/* 1. Scenario(s) */}
      <fieldset className="flex flex-col gap-3">
        <legend className={`${titreSection} mb-3`}>{r.scenarios.length > 1 ? "Vos scénarios" : "Votre scénario"}</legend>

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
                {r.scenarios.length > 1 ? (
                  <div className="mb-1.5 flex items-center justify-between">
                    <label htmlFor={`scenario-${i}`} className="flex items-center gap-2 text-sm font-medium">
                      <span aria-hidden className="grid size-5 place-items-center rounded-[calc(var(--radius-controle)/2)] bg-accent-soft text-xs font-semibold text-accent-ink">
                        {labels[i]}
                      </span>
                      Scénario {labels[i]}
                    </label>
                    {i > 0 && (
                      <button type="button" onClick={() => retirerScenario(i)} aria-label={`Retirer le scénario ${labels[i]}`} className="grid size-6 place-items-center rounded-controle text-muted transition-colors hover:bg-surface-2 hover:text-loss">
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
                  className={`${champ} block resize-y leading-relaxed ${actif === i && r.scenarios.length > 1 ? "border-accent/60" : ""}`}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {r.scenarios.length > 1 && r.scenarios.length < max && (
          <motion.button
            type="button"
            layout
            whileTap={{ scale: 0.98 }}
            onClick={() => definirNombre(r.scenarios.length + 1)}
            className="flex items-center justify-center gap-1.5 rounded-controle border border-dashed border-line-strong py-2 text-sm font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink"
          >
            <Plus className="size-4" aria-hidden />
            Ajouter le scénario {labels[r.scenarios.length]}
          </motion.button>
        )}

        <p className="text-aide leading-relaxed text-muted">
          {r.scenarios.length > 1
            ? `Les idées ci-dessous remplissent le scénario ${labels[actif]}. Même portefeuille pour tous : seule la cause change.`
            : "Plus vous êtes précis (pays, secteur, ampleur, durée), plus l'analyse est pertinente."}
        </p>
        <div role="group" aria-label="Idées de scénarios" className="flex flex-wrap gap-1.5">
          <AnimatePresence initial={false}>
            {idees.map((s) => (
              <motion.button
                key={s.titre}
                type="button"
                layout="position"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: DUREE.rapide }}
                whileTap={{ scale: 0.97 }}
                onClick={() => majScenario(actif, s.texte)}
                aria-pressed={r.scenarios[actif] === s.texte}
                className={puce}
              >
                {s.titre}
              </motion.button>
            ))}
          </AnimatePresence>
          {rapides.length > SCENARIOS_RAPIDES_VISIBLES && indexChoisi < SCENARIOS_RAPIDES_VISIBLES && (
            <motion.button
              type="button"
              layout="position"
              aria-expanded={plusIdees}
              onClick={() => setPlusIdees((o) => !o)}
              className="flex items-center gap-1 rounded-full px-2.5 py-1.5 text-aide font-medium text-accent-ink transition-colors hover:bg-accent-soft"
            >
              {plusIdees ? "Moins d'idées" : "Plus d'idées"}
              <ChevronDown className={`size-3.5 transition-transform duration-200 ${plusIdees ? "rotate-180" : ""}`} aria-hidden />
            </motion.button>
          )}
        </div>

        {r.scenarios.length === 1 && max > 1 && (
          <button type="button" onClick={() => definirNombre(2)} className="flex items-center gap-1.5 self-start text-aide font-medium text-ink-2 transition-colors hover:text-accent-ink">
            <GitCompareArrows className="size-3.5" aria-hidden />
            Comparer avec un autre scénario
          </button>
        )}
      </fieldset>

      {/* 2. Portefeuille */}
      <fieldset className="flex flex-col gap-3">
        <legend className={`${titreSection} mb-3`}>Votre portefeuille</legend>
        <ChoixPortefeuille catalogue={catalogue} valeur={r.portefeuille} onChange={(portefeuille) => maj({ portefeuille })} />
      </fieldset>

      {/* 3. Options : ligne repliable distincte, son resume reste visible une fois fermee */}
      <div className="-mx-(--marge-carte) -mb-6 border-t border-line px-(--marge-carte)">
        <button type="button" aria-expanded={optionsOuvertes} aria-controls={idOptions} onClick={() => setOptionsOuvertes((o) => !o)} className="flex w-full items-center gap-2 py-3.5 text-left">
          <Settings2 className="size-4 shrink-0 text-muted" aria-hidden />
          <span className={titreSection}>Options avancées</span>
          <span className="ml-auto min-w-0 truncate text-aide text-muted">
            {r.duree} j · {modele.nom}
          </span>
          <ChevronDown className={`size-4 shrink-0 text-muted transition-transform duration-200 ${optionsOuvertes ? "rotate-180" : ""}`} aria-hidden />
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
              <div className="flex flex-col gap-5 pb-4 pt-1">
                <div>
                  <label htmlFor="duree" className="mb-2 flex items-baseline justify-between gap-2 text-sm font-medium">
                    Horizon
                    <span className="font-normal text-ink-2 tabular-nums">
                      {r.duree} jours de bourse <span className="text-muted">· {equivalentDuree(r.duree)}</span>
                    </span>
                  </label>
                  <input
                    id="duree"
                    type="range"
                    min={catalogue.horizon.min}
                    max={catalogue.horizon.max}
                    step={catalogue.horizon.pas}
                    value={r.duree}
                    aria-valuetext={`${r.duree} jours de bourse, ${equivalentDuree(r.duree)}`}
                    onChange={(e) => maj({ duree: Number(e.target.value) })}
                    className="w-full accent-(--accent)"
                  />
                </div>
                <div>
                  <p id={idModele} className="mb-2 text-sm font-medium">
                    Comportement du marché
                  </p>
                  <div role="radiogroup" aria-labelledby={idModele} className="grid grid-cols-3 gap-1.5">
                    {catalogue.modeles.map((m) => {
                      const choisi = r.modele === m;
                      const p = presentationModele(m);
                      return (
                        <button
                          key={m}
                          type="button"
                          role="radio"
                          aria-checked={choisi}
                          onClick={() => maj({ modele: m })}
                          className={`relative rounded-controle border px-2 py-2 text-center text-aide font-medium transition-colors ${choisi ? "border-accent text-accent-ink" : "border-line text-ink-2 hover:border-line-strong hover:text-ink"}`}
                        >
                          {choisi && <motion.span layoutId={`${idGroupe}-modele`} className="absolute inset-0 rounded-[calc(var(--radius-controle)-1px)] bg-accent-soft" transition={RESSORT} />}
                          <span className="relative">{p.nom}</span>
                          <span className="sr-only">
                            {" "}
                            (modèle « {m} ») : {p.description}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                  <p className="mt-2 text-aide text-muted" aria-live="polite">
                    {modele.description}
                  </p>
                </div>
                <div className="divide-y divide-line">
                  <Interrupteur
                    actif={r.monteCarlo}
                    onChange={(v) => maj({ monteCarlo: v })}
                    libelle={`Monte-Carlo (${catalogue.nb_simulations_monte_carlo.toLocaleString("fr-FR")} trajectoires)`}
                    info="Affiche la fourchette des issues possibles et la probabilité de perte."
                  />
                  <Interrupteur actif={r.convertirEur} onChange={(v) => maj({ convertirEur: v })} libelle="Convertir en euros" info="Tient compte du taux de change, comme le vivrait un investisseur européen." />
                  <Interrupteur actif={r.calibration} onChange={(v) => maj({ calibration: v })} libelle="Calibration historique" info="L'IA s'ancre sur les amplitudes de crises réelles (2008, COVID, 2022…)." />
                  <Interrupteur actif={r.prixReels} onChange={(v) => maj({ prixReels: v })} libelle="Prix de marché actuels" info="Part des dernières clôtures et des volatilités réelles (Yahoo Finance)." />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className={barreLancement}>
        <AnimatePresence>
          {erreur && (
            <motion.p role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="text-aide text-warn">
              {erreur}
            </motion.p>
          )}
        </AnimatePresence>
        <motion.button type="submit" disabled={!!erreur || enCours} whileTap={!erreur && !enCours ? { scale: 0.98 } : undefined} className={boutonPrincipal}>
          <AnimatePresence mode="wait" initial={false}>
            <motion.span key={enCours ? "attente" : "repos"} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: DUREE.rapide }} className="flex items-center gap-2">
              {enCours ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Play className="size-4" aria-hidden />}
              {enCours ? "Analyse en cours…" : r.scenarios.length > 1 ? `Comparer les ${r.scenarios.length} scénarios` : "Lancer la simulation"}
            </motion.span>
          </AnimatePresence>
        </motion.button>
      </div>
    </form>
  );
}
