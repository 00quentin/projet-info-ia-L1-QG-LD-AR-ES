"use client";

import { motion } from "motion/react";
import { Check, Minus, X } from "lucide-react";
import type { ActifValide } from "@/lib/validation";
import { pourcentSigne } from "@/lib/format";
import { EASE_SORTIE } from "@/components/motion/transitions";

export const COULEUR_IA = "var(--series-1)";
export const COULEUR_REEL = "var(--series-2)";
// Au-dela, la barre est coupee au bord (le VIX ecraserait sinon tous les autres actifs).
const ECHELLE_MAX_PCT = 100;

/** Pastille de legende (forme de la marque : rectangle pour une barre). */
export function Cle({ couleur, children }: { couleur: string; children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-ink-2">
      <span aria-hidden className="h-2 w-3 rounded-[2px]" style={{ background: couleur }} />
      {children}
    </span>
  );
}

/** Echelle calee sur le 2e plus gros mouvement : le plus gros (souvent le VIX) peut etre
 *  coupe, mais il n'ecrase plus les barres de tous les autres actifs. */
function echelle(actifs: ActifValide[]): number {
  const amplitudes = actifs.map((a) => Math.max(Math.abs(a.estime_pct), Math.abs(a.reel_pct))).sort((a, b) => b - a);
  const reference = (amplitudes.length > 3 ? amplitudes[1] : amplitudes[0]) ?? 1;
  return Math.min(ECHELLE_MAX_PCT, Math.max(10, Math.ceil(reference / 10) * 10));
}

function Valeur({ couleur, libelle, valeur, accent }: { couleur: string; libelle: string; valeur: string; accent?: boolean }) {
  return (
    <span className={`inline-flex items-center justify-end gap-1 whitespace-nowrap ${accent ? "text-ink" : "text-muted"}`}>
      <span aria-hidden className="h-1.5 w-2 shrink-0 rounded-[1px]" style={{ background: couleur }} />
      <span className="sr-only">{libelle} </span>
      {valeur}
    </span>
  );
}

/** Une barre qui part du zero central ; bout arrondi cote donnee, carre cote zero. */
function Barre({ valeur, max, couleur, delai }: { valeur: number; max: number; couleur: string; delai: number }) {
  const coupee = Math.abs(valeur) > max;
  const part = (Math.min(Math.abs(valeur), max) / max) * 50;
  const positif = valeur >= 0;
  return (
    <span className="relative block h-2">
      <motion.span
        className={`absolute inset-y-0 ${positif ? "left-1/2 origin-left rounded-r" : "right-1/2 origin-right rounded-l"}`}
        style={{ width: `${Math.max(part, 0.8)}%`, background: couleur }}
        initial={{ scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: EASE_SORTIE, delay: delai }}
      />
      {coupee && (
        // Coupure : un trait couleur surface au bout de la barre signale qu'elle continue au-dela.
        <span aria-hidden className={`absolute -inset-y-0.5 w-0.5 bg-surface ${positif ? "right-1" : "left-1"}`} />
      )}
    </span>
  );
}

function IconeSens({ sens }: { sens: boolean | null }) {
  if (sens === null)
    return (
      <span title="Vrai mouvement trop faible pour juger le sens" className="text-muted">
        <Minus className="size-4" aria-hidden />
        <span className="sr-only">sens non jugé</span>
      </span>
    );
  return sens ? (
    <span title="Bon sens de variation" className="text-gain">
      <Check className="size-4" aria-hidden />
      <span className="sr-only">bon sens</span>
    </span>
  ) : (
    <span title="Sens inverse" className="text-loss">
      <X className="size-4" aria-hidden />
      <span className="sr-only">sens inverse</span>
    </span>
  );
}

/**
 * Estimation de l'IA et vrai mouvement, actif par actif : deux barres appariees
 * autour d'un zero commun. Les valeurs sont ecrites a cote (pas de survol obligatoire).
 */
export function BarresAppariees({ actifs }: { actifs: ActifValide[] }) {
  const max = echelle(actifs);
  const tronque = actifs.some((a) => Math.abs(a.estime_pct) > max || Math.abs(a.reel_pct) > max);
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-x-4 gap-y-1">
        <Cle couleur={COULEUR_IA}>Estimation de l’IA</Cle>
        <Cle couleur={COULEUR_REEL}>Vrai mouvement</Cle>
      </div>
      <ul className="flex flex-col" aria-label="Estimation de l'IA et vrai mouvement, actif par actif">
        {actifs.map((a, i) => (
          // Sur telephone : nom et valeurs sur une ligne, barres pleine largeur dessous.
          <li
            key={a.cle}
            className="grid grid-cols-[minmax(0,1fr)_auto_1rem] items-center gap-x-2 gap-y-1.5 rounded-lg px-1.5 py-2 transition-colors hover:bg-surface-2 sm:grid-cols-[minmax(0,9rem)_minmax(0,1fr)_5.75rem_1rem] sm:gap-x-3 sm:py-1.5"
            title={`${a.nom} : IA ${pourcentSigne(a.estime_pct)}, réel ${pourcentSigne(a.reel_pct)}, écart ${pourcentSigne(a.ecart_pts).replace(" %", " pts")}`}
          >
            <span className="col-start-1 row-start-1 min-w-0 text-[13px] leading-snug text-ink-2">
              <span className="line-clamp-2">
                {a.nom_court}
                {a.devise && a.devise !== "EUR" && <span className="ml-1 text-[11px] text-muted sm:ml-0 sm:block">en {a.devise === "GBP" ? "livres" : "yens"}</span>}
              </span>
            </span>
            <span className="relative col-span-3 row-start-2 flex flex-col gap-0.5 py-0.5 sm:col-span-1 sm:col-start-2 sm:row-start-1" aria-hidden>
              <span className="absolute -inset-y-1 left-1/2 w-px bg-line-strong" />
              <Barre valeur={a.estime_pct} max={max} couleur={COULEUR_IA} delai={i * 0.03} />
              <Barre valeur={a.reel_pct} max={max} couleur={COULEUR_REEL} delai={i * 0.03 + 0.08} />
            </span>
            <span className="col-start-2 row-start-1 flex gap-2.5 text-xs leading-tight tabular-nums sm:col-start-3 sm:flex-col sm:gap-0">
              <Valeur couleur={COULEUR_IA} libelle="IA" valeur={`${pourcentSigne(a.estime_pct)}${a.ecrete ? "*" : ""}`} accent />
              <Valeur couleur={COULEUR_REEL} libelle="réel" valeur={pourcentSigne(a.reel_pct)} />
            </span>
            <span className="col-start-3 row-start-1 sm:col-start-4">
              <IconeSens sens={a.sens_correct} />
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-2 text-[11px] leading-relaxed text-muted">
        Échelle de −{max} % à +{max} %{tronque ? " ; une barre coupée continue au-delà (la valeur exacte est à droite)" : ""}. En haut l’IA, en dessous la réalité.
      </p>
    </div>
  );
}
