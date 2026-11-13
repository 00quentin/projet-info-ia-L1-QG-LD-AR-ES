import { Check, X } from "lucide-react";
import type { CriseValidee } from "@/lib/validation";
import { pourcentSigne } from "@/lib/format";
import { points } from "./outils";

const NB_ECARTS = 6;

/** Là où l'IA s'est le plus trompée : à montrer autant que ses réussites. */
export function PlusGrosEcarts({ crises }: { crises: CriseValidee[] }) {
  const ecarts = crises
    .flatMap((c) => c.actifs.map((a) => ({ ...a, crise: c.nom.replace(/\s*\(.*\)$/, "") })))
    .sort((a, b) => Math.abs(b.ecart_pts) - Math.abs(a.ecart_pts))
    .slice(0, NB_ECARTS);
  return (
    <div>
      <h3 className="text-sm font-semibold text-ink">Les plus gros écarts</h3>
      <p className="mt-1 text-xs leading-relaxed text-muted">Les comparaisons où l’IA est le plus loin de la réalité, toutes crises confondues.</p>
      <ol className="mt-3 flex flex-col divide-y divide-line">
        {ecarts.map((e) => (
          <li key={`${e.crise}-${e.cle}`} className="flex items-start justify-between gap-3 py-2.5">
            <div className="min-w-0">
              <p className="text-[13px] font-medium text-ink">
                {e.nom_court} <span className="font-normal text-muted">· {e.crise}</span>
              </p>
              <p className="mt-0.5 text-xs text-ink-2 tabular-nums">
                IA {pourcentSigne(e.estime_pct)} · réel {pourcentSigne(e.reel_pct)}
              </p>
            </div>
            <span className="flex shrink-0 items-center gap-1 whitespace-nowrap text-xs font-semibold text-ink tabular-nums">
              {points(Math.abs(e.ecart_pts), 0)}
              {e.sens_correct === false ? (
                <X className="size-3.5 text-loss" aria-label="sens inverse" />
              ) : e.sens_correct ? (
                <Check className="size-3.5 text-gain" aria-label="bon sens" />
              ) : null}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
