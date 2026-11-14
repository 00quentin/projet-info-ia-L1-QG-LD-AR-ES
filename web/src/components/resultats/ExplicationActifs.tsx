"use client";

import { useEffect, useRef, useState } from "react";
import { CircleAlert, Lightbulb, Loader2, RotateCw } from "lucide-react";
import { ErreurApi, expliquerActifs } from "@/lib/api";
import { pourcentSigne } from "@/lib/format";

type Actif = { cle: string; nom: string; performance_pct: number };
type Etat =
  | { phase: "repos" }
  | { phase: "attente" }
  | { phase: "erreur"; message: string }
  | { phase: "resultat"; explications: Record<string, string> };

/**
 * « Pourquoi ces mouvements ? » : une phrase par actif, demandée à l'IA (un seul appel, à la demande).
 * L'IA explique les variations déjà calculées, elle ne les modifie pas.
 */
export function ExplicationActifs({ scenario, actifs }: { scenario: string; actifs: Actif[] }) {
  const cle = `${scenario}|${actifs.map((a) => `${a.cle}:${a.performance_pct.toFixed(1)}`).join(",")}`;
  const [suivi, setSuivi] = useState<{ cle: string; etat: Etat }>({ cle, etat: { phase: "repos" } });
  const etat: Etat = suivi.cle === cle ? suivi.etat : { phase: "repos" };
  const actif = useRef(cle);

  useEffect(() => {
    actif.current = cle;
  }, [cle]);

  async function expliquer() {
    const lancee = cle;
    setSuivi({ cle, etat: { phase: "attente" } });
    try {
      const chocs = Object.fromEntries(actifs.map((a) => [a.cle, Math.round(a.performance_pct * 10) / 10]));
      const r = await expliquerActifs({ scenario, chocs });
      if (actif.current === lancee) setSuivi({ cle, etat: { phase: "resultat", explications: r.explications } });
    } catch (e) {
      if (actif.current !== lancee) return;
      setSuivi({ cle, etat: { phase: "erreur", message: e instanceof ErreurApi ? e.message : "L'explication n'a pas pu être obtenue." } });
    }
  }

  return (
    <div className="mt-5 border-t border-line pt-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-ink-2">Pourquoi chaque actif évolue-t-il ainsi dans ce scénario ?</p>
        {etat.phase === "repos" && (
          <button
            type="button"
            onClick={expliquer}
            className="flex h-9 shrink-0 items-center gap-2 self-start rounded-xl border border-line bg-surface px-3.5 text-sm font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink"
          >
            <Lightbulb className="size-4" aria-hidden />
            Pourquoi ces mouvements ?
          </button>
        )}
      </div>

      {etat.phase === "attente" && (
        <p role="status" className="mt-3 flex items-center gap-2 text-sm text-muted">
          <Loader2 className="size-4 animate-spin" aria-hidden />
          Rédaction des explications…
        </p>
      )}
      {etat.phase === "erreur" && (
        <div role="alert" className="mt-3 flex flex-col gap-3 rounded-xl border border-loss/30 bg-loss-soft px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between">
          <span className="flex gap-2 text-ink">
            <CircleAlert className="mt-0.5 size-4 shrink-0 text-loss" aria-hidden />
            {etat.message}
          </span>
          <button type="button" onClick={expliquer} className="flex shrink-0 items-center gap-1.5 self-start rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink">
            <RotateCw className="size-3.5" aria-hidden />
            Réessayer
          </button>
        </div>
      )}
      {etat.phase === "resultat" && (
        <>
          <ul className="mt-3 space-y-2.5">
            {actifs.map((a) =>
              etat.explications[a.cle] ? (
                <li key={a.cle} className="rounded-tuile bg-surface-2 px-3 py-2.5 text-sm leading-relaxed">
                  <span className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <strong className="font-medium text-ink">{a.nom}</strong>
                    <span className="tabular-nums text-xs text-muted">{pourcentSigne(a.performance_pct, 1)}</span>
                  </span>
                  <span className="mt-0.5 block text-ink-2">{etat.explications[a.cle]}</span>
                </li>
              ) : null,
            )}
          </ul>
          <p className="mt-2 text-xs text-muted">Explication générée par l&apos;IA, indicative.</p>
        </>
      )}
    </div>
  );
}
