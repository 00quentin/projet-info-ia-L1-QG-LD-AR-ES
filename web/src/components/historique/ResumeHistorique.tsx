"use client";

import { ArrowRight, Layers } from "lucide-react";
import type { EntreeHistorique } from "@/lib/historique";
import { pourcentSigne } from "@/lib/format";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { extremes, titreEntree, type Filtre } from "./outils";

const LIBELLES: Record<Filtre, string> = { tout: "Dans l'historique", Simulation: "Simulations", Backtest: "Backtests" };

function TuilePerformance({ titre, entree, onVoir }: { titre: string; entree: EntreeHistorique; onVoir: (id: string) => void }) {
  const hausse = entree.performance_pct >= 0;
  const nom = titreEntree(entree);
  return (
    <ElementCascade className="min-w-0">
      <button
        type="button"
        onClick={() => onVoir(entree.id)}
        aria-label={`${titre} : ${pourcentSigne(entree.performance_pct, 2)}, ${nom}. Afficher le détail.`}
        className="group flex h-full w-full flex-col rounded-tuile border border-line bg-surface p-4 text-left transition-colors hover:border-line-strong"
      >
        <span className="text-xs font-medium text-muted">{titre}</span>
        <span className={`mt-1.5 text-2xl font-semibold tracking-tight tabular-nums ${hausse ? "text-gain" : "text-loss"}`}>{pourcentSigne(entree.performance_pct, 2)}</span>
        <span className="mt-1 flex min-w-0 items-center gap-1 text-xs text-ink-2">
          <span className="truncate">{nom}</span>
          <ArrowRight className="size-3.5 shrink-0 text-muted transition-transform group-hover:translate-x-0.5" aria-hidden />
        </span>
      </button>
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
        <div className="flex h-full flex-col rounded-tuile border border-line bg-surface p-4">
          <span className="flex items-center justify-between gap-2 text-xs font-medium text-muted">
            {LIBELLES[filtre]}
            <Layers className="size-3.5" aria-hidden />
          </span>
          <span className="mt-1.5 block text-2xl font-semibold tracking-tight tabular-nums">{entrees.length}</span>
          <span className="mt-1 truncate text-xs text-ink-2">{detail}</span>
        </div>
      </ElementCascade>
      {ext && <TuilePerformance titre="Meilleure performance" entree={ext.meilleure} onVoir={onVoir} />}
      {ext && <TuilePerformance titre="Pire performance" entree={ext.pire} onVoir={onVoir} />}
    </Cascade>
  );
}
