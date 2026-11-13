"use client";

import { motion } from "motion/react";
import { pourcentSigne } from "@/lib/format";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

type Ligne = { cle: string; nom: string; valeur: number };

/**
 * Barres horizontales de performance autour d'un zero central.
 * Le signe est porte par la position, le signe du nombre et sa couleur — pas par la seule couleur.
 */
export function BarresPerformance({ lignes }: { lignes: Ligne[] }) {
  const triees = [...lignes].sort((a, b) => b.valeur - a.valeur);
  const max = Math.max(1, ...triees.map((l) => Math.abs(l.valeur)));

  return (
    <ul className="flex flex-col gap-2.5" aria-label="Performance par actif, du meilleur au moins bon">
      {triees.map((l, i) => {
        const part = (Math.abs(l.valeur) / max) * 50;
        const positif = l.valeur >= 0;
        return (
          <li key={l.cle} className="grid grid-cols-[minmax(0,8rem)_1fr_4.5rem] items-center gap-3 text-sm sm:grid-cols-[minmax(0,13rem)_1fr_5rem]">
            <span className="line-clamp-2 leading-snug text-ink-2">{l.nom}</span>
            <span className="relative h-4" aria-hidden>
              <span className="absolute inset-y-0 left-1/2 w-px bg-line-strong" />
              {/* La barre pousse depuis le zero central, vers la droite ou la gauche selon le signe. */}
              <motion.span
                className={`absolute top-0.5 h-3 ${positif ? "left-1/2 origin-left rounded-r-sm bg-gain" : "right-1/2 origin-right rounded-l-sm bg-loss"}`}
                style={{ width: `${Math.max(part, 0.6)}%` }}
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: DUREE.donnees * 0.85, ease: EASE_SORTIE, delay: Math.min(i, 12) * 0.04 }}
              />
            </span>
            <span className={`whitespace-nowrap text-right font-medium tabular-nums ${positif ? "text-gain" : "text-loss"}`}>{pourcentSigne(l.valeur)}</span>
          </li>
        );
      })}
    </ul>
  );
}
