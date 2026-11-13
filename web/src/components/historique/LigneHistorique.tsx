"use client";

import Link from "next/link";
import { AnimatePresence, motion } from "motion/react";
import { useId, useState, type FormEvent, type ReactNode } from "react";
import { ChevronDown, Dices, History, LineChart, Play, Trash2 } from "lucide-react";
import { renommerEntree, type EntreeHistorique } from "@/lib/historique";
import { euros, pourcentSigne } from "@/lib/format";
import { Pastille } from "@/components/ui/Carte";
import { CocheAnimee, useFlash } from "@/components/exports/commun";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { cheminRelance, dateComplete, dateLisible, profilCourt, titreEntree } from "./outils";

const NOM_LONGUEUR_MAX = 80;

function Performance({ valeur, className = "" }: { valeur: number; className?: string }) {
  const hausse = valeur >= 0;
  return (
    <span className={`inline-flex items-center gap-1 whitespace-nowrap font-semibold tabular-nums ${hausse ? "text-gain" : "text-loss"} ${className}`}>
      <span className="sr-only">{hausse ? "Hausse de" : "Baisse de"}</span>
      {pourcentSigne(valeur, 2)}
    </span>
  );
}

function Chiffre({ libelle, children, ton }: { libelle: string; children: ReactNode; ton?: "gain" | "perte" }) {
  const fond = ton === "gain" ? "border-gain/25 bg-gain-soft" : ton === "perte" ? "border-loss/25 bg-loss-soft" : "border-line bg-surface-2/50";
  return (
    <div className={`rounded-tuile border px-3.5 py-3 ${fond}`}>
      <dt className="text-xs text-muted">{libelle}</dt>
      <dd className={`mt-0.5 text-base font-semibold tabular-nums ${ton === "gain" ? "text-gain" : ton === "perte" ? "text-loss" : ""}`}>{children}</dd>
    </div>
  );
}

function FormulaireNom({ entree, annoncer }: { entree: EntreeHistorique; annoncer: (m: string) => void }) {
  const idChamp = useId();
  const [nom, setNom] = useState(entree.nom ?? "");
  const [enregistre, flash] = useFlash(2000);
  const inchange = nom.trim() === (entree.nom ?? "");

  function valider(e: FormEvent) {
    e.preventDefault();
    renommerEntree(entree.id, nom.slice(0, NOM_LONGUEUR_MAX));
    setNom(nom.trim());
    flash();
    annoncer(nom.trim() ? `Simulation renommée « ${nom.trim()} ».` : "Nom personnalisé retiré.");
  }

  return (
    <form onSubmit={valider} className="min-w-0 flex-1">
      <label htmlFor={idChamp} className="mb-1.5 block text-xs font-medium text-ink-2">
        Nom de cette simulation
      </label>
      <div className="flex gap-2">
        <input
          id={idChamp}
          value={nom}
          onChange={(e) => setNom(e.target.value)}
          maxLength={NOM_LONGUEUR_MAX}
          placeholder="Ex : « Krach 2008 — profil défensif »"
          className="h-10 w-full min-w-0 rounded-controle border border-line bg-surface px-3.5 text-sm outline-none transition placeholder:text-muted focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <motion.button
          type="submit"
          disabled={inchange && !enregistre}
          whileTap={{ scale: 0.96 }}
          transition={RESSORT}
          className={`relative inline-flex h-10 w-28 shrink-0 items-center justify-center gap-1.5 overflow-hidden rounded-controle border text-sm font-medium transition-colors disabled:cursor-not-allowed ${enregistre ? "border-gain/40 bg-gain-soft text-gain" : "border-line bg-surface hover:border-line-strong hover:bg-surface-2 disabled:opacity-50 disabled:hover:bg-surface"}`}
        >
          <AnimatePresence mode="popLayout" initial={false}>
            <motion.span
              key={enregistre ? "ok" : "repos"}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }}
              className="inline-flex items-center gap-1.5"
            >
              {enregistre ? (
                <>
                  <CocheAnimee /> Enregistré
                </>
              ) : (
                "Renommer"
              )}
            </motion.span>
          </AnimatePresence>
        </motion.button>
      </div>
    </form>
  );
}

function Detail({ entree, onSupprimer, annoncer }: { entree: EntreeHistorique; onSupprimer: () => void; annoncer: (m: string) => void }) {
  const gain = entree.valeur_finale - entree.capital;
  const chemin = cheminRelance(entree.lien);
  return (
    <div className="border-t border-line px-4 pb-5 pt-4 sm:px-5">
      <div className="text-xs font-medium text-muted">Scénario</div>
      <p className="mt-1 text-sm leading-relaxed text-ink">{entree.scenario}</p>
      <p className="mt-2 text-xs text-ink-2">
        Profil {entree.profil}
        {entree.monte_carlo && " · Monte-Carlo activé"}
        {entree.label_comparaison && ` · scénario ${entree.label_comparaison} d'une comparaison`}
      </p>

      <dl className="mt-4 grid grid-cols-2 gap-2.5 sm:grid-cols-4">
        <Chiffre libelle="Actifs analysés">{entree.nb_actifs}</Chiffre>
        <Chiffre libelle="Capital initial">{euros(entree.capital)}</Chiffre>
        <Chiffre libelle="Valeur finale">{euros(entree.valeur_finale)}</Chiffre>
        <Chiffre libelle={gain >= 0 ? "Gain" : "Perte"} ton={gain >= 0 ? "gain" : "perte"}>
          {gain >= 0 ? "+" : "−"}
          {euros(Math.abs(gain))}
        </Chiffre>
      </dl>

      <div className="mt-5 flex flex-col gap-4 border-t border-line pt-4 sm:flex-row sm:items-end">
        <FormulaireNom entree={entree} annoncer={annoncer} />
        <div className="flex shrink-0 gap-2">
          {chemin && (
            <motion.span whileTap={{ scale: 0.97 }} transition={RESSORT} className="flex flex-1 sm:flex-none">
              <Link href={chemin} className="inline-flex h-10 flex-1 items-center justify-center gap-1.5 rounded-controle bg-accent px-3.5 text-sm font-semibold text-white transition hover:brightness-110">
                <Play className="size-3.5" aria-hidden />
                Relancer
              </Link>
            </motion.span>
          )}
          <motion.button
            type="button"
            onClick={onSupprimer}
            whileTap={{ scale: 0.97 }}
            transition={RESSORT}
            className="inline-flex h-10 flex-1 items-center justify-center gap-1.5 rounded-controle border border-line px-3.5 text-sm font-medium text-ink-2 transition-colors hover:border-loss/40 hover:bg-loss-soft hover:text-loss sm:flex-none"
          >
            <Trash2 className="size-3.5" aria-hidden />
            Supprimer
          </motion.button>
        </div>
      </div>
    </div>
  );
}

type Props = {
  entree: EntreeHistorique;
  ouvert: boolean;
  onBasculer: () => void;
  onSupprimer: () => void;
  annoncer: (m: string) => void;
};

/** Une simulation de l'historique : resume cliquable, detail qui se deplie. */
export function LigneHistorique({ entree, ouvert, onBasculer, onSupprimer, annoncer }: Props) {
  const idPanneau = useId();
  const backtest = entree.type === "Backtest";
  const Icone = backtest ? History : LineChart;
  const titre = titreEntree(entree);

  return (
    <>
      <h3>
        <button
          type="button"
          id={`bouton-${entree.id}`}
          aria-expanded={ouvert}
          aria-controls={idPanneau}
          onClick={onBasculer}
          className={`flex w-full items-center gap-3 px-4 py-3.5 text-left transition-colors hover:bg-surface-2/50 sm:gap-4 sm:px-5 ${ouvert ? "rounded-t-carte" : "rounded-carte"}`}
        >
          <span className={`hidden size-9 shrink-0 place-items-center rounded-tuile sm:grid ${backtest ? "bg-warn-soft text-warn" : "bg-accent-soft text-accent-ink"}`}>
            <Icone className="size-4.5" aria-hidden />
          </span>
          <span className="min-w-0 flex-1">
            <AnimatePresence mode="popLayout" initial={false}>
              <motion.span
                key={titre}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: DUREE.rapide }}
                className="line-clamp-2 text-sm font-semibold break-words sm:line-clamp-1"
              >
                {titre}
              </motion.span>
            </AnimatePresence>
            {entree.nom && <span className="mt-0.5 line-clamp-1 text-xs text-ink-2">{entree.scenario}</span>}
            <span className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1.5 text-xs text-muted">
              <time dateTime={entree.date} aria-label={dateComplete(entree.date)}>
                {dateLisible(entree.date)}
              </time>
              <Pastille ton={backtest ? "alerte" : "accent"}>{entree.type}</Pastille>
              <span>{profilCourt(entree.profil)}</span>
              {entree.monte_carlo && (
                <Pastille>
                  <Dices className="size-3" aria-hidden />
                  Monte-Carlo
                </Pastille>
              )}
              {entree.label_comparaison && <Pastille>Scénario {entree.label_comparaison}</Pastille>}
            </span>
          </span>
          <span className="flex shrink-0 flex-col items-end gap-0.5">
            <Performance valeur={entree.performance_pct} className="text-titre" />
            <span className="hidden text-xs text-muted tabular-nums sm:block">{euros(entree.valeur_finale)}</span>
          </span>
          <motion.span animate={{ rotate: ouvert ? 180 : 0 }} transition={RESSORT} className="shrink-0 text-muted">
            <ChevronDown className="size-4" aria-hidden />
          </motion.span>
        </button>
      </h3>
      <AnimatePresence initial={false}>
        {ouvert && (
          <motion.div
            id={idPanneau}
            role="region"
            aria-labelledby={`bouton-${entree.id}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
            className="overflow-hidden"
          >
            <Detail entree={entree} onSupprimer={onSupprimer} annoncer={annoncer} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
