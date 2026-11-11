"use client";

import { useId, useRef } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Info, Loader2, Play, RotateCcw } from "lucide-react";
import type { Catalogue, EvenementHistorique } from "@/lib/api";
import { dateFr } from "@/lib/format";
import { ChoixPortefeuille, portefeuilleInitial, validerPortefeuille, type ValeurPortefeuille } from "@/components/formulaire/ChoixPortefeuille";
import { champ, titreSection } from "@/components/formulaire/styles";
import { Interrupteur } from "@/components/ui/Carte";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { aujourdhui, dateMin, dureeLisible, periodeCourte, recouvreEvenement, validerPeriode } from "./outils";

export type ReglagesBacktest = {
  /** Nom de l'evenement du catalogue choisi. */
  evenement: string;
  periodePerso: boolean;
  /** AAAA-MM-JJ, utilisees seulement avec la periode personnalisee. */
  dateDebut: string;
  dateFin: string;
  portefeuille: ValeurPortefeuille;
  convertirEur: boolean;
};

export function reglagesInitiaux(catalogue: Catalogue): ReglagesBacktest {
  const e = catalogue.evenements_historiques[0];
  return {
    evenement: e.nom,
    periodePerso: false,
    dateDebut: e.debut,
    dateFin: e.fin,
    portefeuille: portefeuilleInitial(catalogue),
    convertirEur: true,
  };
}

/** Message d'erreur a afficher, ou null si le backtest peut partir. */
export function validerReglages(r: ReglagesBacktest, catalogue: Catalogue): string | null {
  return (r.periodePerso ? validerPeriode(r.dateDebut, r.dateFin, r.convertirEur) : null) ?? validerPortefeuille(r.portefeuille, catalogue);
}

/** Evenement seul, evenement aux dates ajustees, ou periode libre (dates qui ne recouvrent plus l'evenement). */
export function periodeDemandee(r: ReglagesBacktest, catalogue: Catalogue) {
  if (!r.periodePerso) return { evenement: r.evenement, date_debut: null, date_fin: null };
  const e = catalogue.evenements_historiques.find((x) => x.nom === r.evenement);
  return {
    evenement: e && recouvreEvenement(r.dateDebut, r.dateFin, e) ? e.nom : null,
    date_debut: r.dateDebut,
    date_fin: r.dateFin,
  };
}

const TOUCHES: Record<string, number> = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 };

function ChoixEvenement({ evenements, choisi, onChoisir }: { evenements: EvenementHistorique[]; choisi: string; onChoisir: (nom: string) => void }) {
  const idGroupe = useId();
  const boutons = useRef<(HTMLButtonElement | null)[]>([]);
  const index = Math.max(0, evenements.findIndex((e) => e.nom === choisi));

  // Groupe de boutons radio : les fleches passent d'un evenement a l'autre (une seule tabulation pour le groupe).
  function surClavier(e: React.KeyboardEvent) {
    const n = evenements.length;
    const cible = e.key in TOUCHES ? (index + TOUCHES[e.key] + n) % n : e.key === "Home" ? 0 : e.key === "End" ? n - 1 : null;
    if (cible === null) return;
    e.preventDefault();
    onChoisir(evenements[cible].nom);
    boutons.current[cible]?.focus();
  }

  return (
    <div role="radiogroup" aria-label="Événement historique" onKeyDown={surClavier} className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-1">
      {evenements.map((e, i) => {
        const actif = e.nom === choisi;
        return (
          <motion.button
            key={e.nom}
            ref={(el) => {
              boutons.current[i] = el;
            }}
            type="button"
            role="radio"
            aria-checked={actif}
            tabIndex={actif ? 0 : -1}
            onClick={() => onChoisir(e.nom)}
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.98 }}
            transition={RESSORT}
            className={`relative rounded-xl border px-3.5 py-3 text-left transition-colors ${actif ? "border-accent" : "border-line bg-surface hover:border-line-strong"}`}
          >
            {actif && <motion.span layoutId={`${idGroupe}-evenement`} className="absolute inset-0 rounded-[11px] bg-accent-soft" transition={RESSORT} />}
            <span className="relative block">
              <span className={`block text-sm font-semibold transition-colors ${actif ? "text-accent-ink" : ""}`}>{e.nom}</span>
              <span className="mt-0.5 block text-xs text-muted tabular-nums">
                {periodeCourte(e.debut, e.fin)} · {dureeLisible(e.debut, e.fin)}
              </span>
              <span className="mt-1.5 line-clamp-2 block text-xs leading-relaxed text-ink-2">{e.description}</span>
            </span>
          </motion.button>
        );
      })}
    </div>
  );
}

function ChoixPeriode({ r, evenement, maj }: { r: ReglagesBacktest; evenement: EvenementHistorique; maj: (p: Partial<ReglagesBacktest>) => void }) {
  const idPanneau = useId();
  const modifiee = r.dateDebut !== evenement.debut || r.dateFin !== evenement.fin;
  const libre = r.dateDebut && r.dateFin && !recouvreEvenement(r.dateDebut, r.dateFin, evenement);
  const min = dateMin(r.convertirEur);
  const max = aujourdhui();

  return (
    <div className="rounded-xl border border-line bg-surface">
      <div className="px-3.5">
        <Interrupteur
          actif={r.periodePerso}
          // Pre-remplie avec les dates de l'evenement : on part de la crise pour l'elargir ou la resserrer.
          onChange={(v) => maj({ periodePerso: v, dateDebut: evenement.debut, dateFin: evenement.fin })}
          libelle="Période personnalisée"
          aide={r.periodePerso ? "Élargissez ou resserrez la crise, ou explorez n'importe quelle période (10 ans au plus)." : `Du ${dateFr(evenement.debut)} au ${dateFr(evenement.fin)}, dates de l'événement.`}
        />
      </div>
      <AnimatePresence initial={false}>
        {r.periodePerso && (
          <motion.div
            id={idPanneau}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
            className="overflow-hidden"
          >
            <div className="flex flex-col gap-3 border-t border-line px-3.5 py-3">
              <div className="grid grid-cols-2 gap-2">
                <label className="flex min-w-0 flex-col gap-1.5 text-xs font-medium text-ink-2">
                  Date de début
                  <input
                    type="date"
                    value={r.dateDebut}
                    min={min}
                    max={r.dateFin || max}
                    onChange={(e) => maj({ dateDebut: e.target.value })}
                    className={`${champ} px-2.5 py-2 tabular-nums`}
                  />
                </label>
                <label className="flex min-w-0 flex-col gap-1.5 text-xs font-medium text-ink-2">
                  Date de fin
                  <input
                    type="date"
                    value={r.dateFin}
                    min={r.dateDebut || min}
                    max={max}
                    onChange={(e) => maj({ dateFin: e.target.value })}
                    className={`${champ} px-2.5 py-2 tabular-nums`}
                  />
                </label>
              </div>
              <AnimatePresence initial={false}>
                {libre && (
                  <motion.p
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="flex gap-2 text-xs leading-relaxed text-ink-2"
                    aria-live="polite"
                  >
                    <Info className="mt-0.5 size-3.5 shrink-0 text-accent-ink" aria-hidden />
                    Ces dates ne recouvrent plus « {evenement.nom} » : le backtest portera sur une période libre.
                  </motion.p>
                )}
              </AnimatePresence>
              {modifiee && (
                <button
                  type="button"
                  onClick={() => maj({ dateDebut: evenement.debut, dateFin: evenement.fin })}
                  className="inline-flex items-center gap-1.5 self-start text-xs font-medium text-accent-ink hover:underline"
                >
                  <RotateCcw className="size-3.5" aria-hidden />
                  Revenir aux dates de l&apos;événement
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

type Props = {
  catalogue: Catalogue;
  reglages: ReglagesBacktest;
  onChange: (r: ReglagesBacktest) => void;
  onLancer: () => void;
  enCours: boolean;
};

export function FormulaireBacktest({ catalogue, reglages: r, onChange, onLancer, enCours }: Props) {
  const maj = (partiel: Partial<ReglagesBacktest>) => onChange({ ...r, ...partiel });
  const erreur = validerReglages(r, catalogue);
  const evenement = catalogue.evenements_historiques.find((e) => e.nom === r.evenement) ?? catalogue.evenements_historiques[0];

  function choisirEvenement(nom: string) {
    const e = catalogue.evenements_historiques.find((x) => x.nom === nom);
    // La periode personnalisee suit l'evenement choisi.
    maj(e ? { evenement: nom, dateDebut: e.debut, dateFin: e.fin } : { evenement: nom });
  }

  return (
    <form
      noValidate
      aria-label="Paramètres du backtest"
      className="flex flex-col gap-7"
      onSubmit={(e) => {
        e.preventDefault();
        if (!erreur && !enCours) onLancer();
      }}
    >
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Backtest historique</h1>
        <p className="mt-1 text-sm leading-relaxed text-ink-2">Rejouez votre portefeuille sur une vraie crise passée, avec les cours réels de Yahoo Finance.</p>
      </div>

      <fieldset className="flex flex-col gap-3">
        <legend className={titreSection}>1 · L&apos;événement</legend>
        <div className="mt-3">
          <ChoixEvenement evenements={catalogue.evenements_historiques} choisi={r.evenement} onChoisir={choisirEvenement} />
        </div>
        <ChoixPeriode r={r} evenement={evenement} maj={maj} />
      </fieldset>

      <fieldset className="flex flex-col gap-3">
        <legend className={titreSection}>2 · Votre portefeuille</legend>
        <div className="mt-3">
          <ChoixPortefeuille catalogue={catalogue} valeur={r.portefeuille} onChange={(portefeuille) => maj({ portefeuille })} autoriserActifsPerso={false} />
        </div>
      </fieldset>

      <fieldset className="flex flex-col gap-1">
        <legend className={titreSection}>3 · Options</legend>
        <div className="mt-2">
          <Interrupteur
            actif={r.convertirEur}
            onChange={(v) => maj({ convertirEur: v })}
            libelle="Convertir en euros (taux BCE)"
            aide="Votre capital est en euros, mais la plupart des actifs cotent en dollars : la performance tient compte du taux de change, comme pour un investisseur européen."
          />
        </div>
      </fieldset>

      <div className="sticky bottom-0 z-10 -mx-5 -mb-5 flex flex-col gap-2 rounded-b-2xl border-t border-line bg-surface/95 px-5 py-4 backdrop-blur">
        <AnimatePresence initial={false}>
          {erreur && (
            <motion.p key={erreur} role="alert" initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: DUREE.rapide }} className="text-xs text-warn">
              {erreur}
            </motion.p>
          )}
        </AnimatePresence>
        <motion.button
          type="submit"
          disabled={!!erreur || enCours}
          whileHover={erreur || enCours ? undefined : { scale: 1.01 }}
          whileTap={erreur || enCours ? undefined : { scale: 0.98 }}
          transition={RESSORT}
          className="flex h-11 items-center justify-center gap-2 rounded-xl bg-accent text-sm font-semibold text-white transition-[filter,opacity] hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {enCours ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Play className="size-4" aria-hidden />}
          {enCours ? "Récupération des cours…" : "Lancer le backtest"}
        </motion.button>
      </div>
    </form>
  );
}
