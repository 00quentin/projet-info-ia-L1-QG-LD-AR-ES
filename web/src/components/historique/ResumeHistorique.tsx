"use client";

import { motion } from "motion/react";
import { ArrowRight, Layers } from "lucide-react";
import type { EntreeHistorique } from "@/lib/historique";
import { pourcentSigne } from "@/lib/format";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { RESSORT } from "@/components/motion/transitions";
import { extremes, titreEntree, type Filtre } from "./outils";

const LIBELLES: Record<Filtre, string> = { tout: "Dans l'historique", Simulation: "Simulations", Backtest: "Backtests" };

function TuilePerformance({ titre, entree, onVoir }: { titre: string; entree: EntreeHistorique; onVoir: (id: string) => void }) {
  const hausse = entree.performance_pct >= 0;
  const nom = titreEntree(entree);
  return (
    <ElementCascade className="min-w-0">
      <motion.button
        type="button"
        onClick={() => onVoir(entree.id)}
        whileHover={{ y: -3 }}
        whileTap={{ scale: 0.98 }}
        transition={RESSORT}
        aria-label={`${titre} : ${pourcentSigne(entree.performance_pct, 2)}, ${nom}. Afficher le détail.`}
        className="group flex h-full w-full flex-col rounded-xl border border-line bg-surface p-4 text-left transition-shadow hover:shadow-card"
      >
        <span className="text-xs font-medium text-muted">{titre}</span>
        <span className={`mt-1.5 flex items-baseline gap-1.5 text-2xl font-semibold tracking-tight ${hausse ? "text-gain" : "text-loss"}`}>
          <span aria-hidden className="text-base">
            {hausse ? "▲" : "▼"}
          </span>
          <NombreAnime valeur={entree.performance_pct} depuis={0} duree={0.9} format={(v) => pourcentSigne(v, 2)} className="tabular-nums" />
        </span>
        <span className="mt-1 flex min-w-0 items-center gap-1 text-xs text-ink-2">
          <span className="truncate">{nom}</span>
          <ArrowRight className="size-3.5 shrink-0 text-muted transition-transform group-hover:translate-x-0.5" aria-hidden />
        </span>
      </motion.button>
    </ElementCascade>
  );
}

/** Trois chiffres en tete de page : combien d'entrees, la meilleure et la pire performance. */
export function ResumeHistorique({ entrees, total, filtre, onVoir }: { entrees: EntreeHistorique[]; total: number; filtre: Filtre; onVoir: (id: string) => void }) {
  const ext = extremes(entrees);
  const nbSimulations = entrees.filter((e) => e.type === "Simulation").length;
  const nbBacktests = entrees.length - nbSimulations;
  const detail =
    filtre === "tout"
      ? `${nbSimulations} simulation${nbSimulations > 1 ? "s" : ""} · ${nbBacktests} backtest${nbBacktests > 1 ? "s" : ""}`
      : `sur ${total} entrée${total > 1 ? "s" : ""} au total`;

  return (
    <Cascade className="grid grid-cols-2 gap-3 sm:grid-cols-3" aria-label="Résumé de l'historique" role="group">
      <ElementCascade className="col-span-2 min-w-0 sm:col-span-1">
        <div className="flex h-full flex-col rounded-xl border border-line bg-surface p-4">
          <span className="flex items-center justify-between gap-2 text-xs font-medium text-muted">
            {LIBELLES[filtre]}
            <Layers className="size-3.5" aria-hidden />
          </span>
          <NombreAnime valeur={entrees.length} depuis={0} duree={0.6} format={(v) => String(Math.round(v))} className="mt-1.5 block text-2xl font-semibold tracking-tight tabular-nums" />
          <span className="mt-1 truncate text-xs text-ink-2">{detail}</span>
        </div>
      </ElementCascade>
      {ext && <TuilePerformance titre="Meilleure performance" entree={ext.meilleure} onVoir={onVoir} />}
      {ext && <TuilePerformance titre="Pire performance" entree={ext.pire} onVoir={onVoir} />}
    </Cascade>
  );
}
