"use client";

import { motion } from "motion/react";
import type { LigneAllocation } from "@/lib/api";
import { euros, pourcent, pourcentSigne } from "@/lib/format";
import { nomCourt } from "@/contenu/actifs";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

type Props = {
  allocations: LigneAllocation[];
  capital: number;
  valeurFinale: number;
  performancePct: number;
  /** Phrase lue par les lecteurs d'ecran (le titre suffit a l'ecran). */
  aide?: string;
};

/** Tableau ligne par ligne : part, montant investi, valeur finale, performance. */
export function DetailPortefeuille({ allocations, capital, valeurFinale, performancePct, aide = "Ce que devient chaque ligne de votre portefeuille dans ce scénario." }: Props) {
  const lignes = [...allocations].sort((a, b) => b.poids - a.poids);
  return (
    <Carte taille="normale">
      <TitreCarte>Détail du portefeuille</TitreCarte>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[34rem] text-sm">
          <caption className="sr-only">{aide}</caption>
          <thead className="text-xs text-muted">
            <tr>
              <th className="pb-2 text-left font-medium">Actif</th>
              <th className="pb-2 text-left font-medium">Part</th>
              <th className="pb-2 text-right font-medium">Investi</th>
              <th className="pb-2 text-right font-medium">Valeur finale</th>
              <th className="pb-2 text-right font-medium">Performance</th>
            </tr>
          </thead>
          <tbody className="tabular-nums">
            {lignes.map((l, i) => (
              <motion.tr
                key={l.cle}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: DUREE.normale, ease: EASE_SORTIE, delay: Math.min(i, 10) * 0.03 }}
                className="border-t border-line"
              >
                <td className="py-2.5 pr-3">{nomCourt(l.cle, l.nom)}</td>
                <td className="py-2.5 pr-3">
                  <span className="flex items-center gap-2">
                    <span className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-2" aria-hidden>
                      <motion.span
                        className="block h-full origin-left rounded-full bg-accent"
                        style={{ width: `${l.poids * 100}%` }}
                        initial={{ scaleX: 0 }}
                        whileInView={{ scaleX: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: DUREE.donnees * 0.75, ease: EASE_SORTIE, delay: 0.1 + Math.min(i, 10) * 0.03 }}
                      />
                    </span>
                    <span className="text-ink-2">{pourcent(l.poids * 100, 0)}</span>
                  </span>
                </td>
                <td className="py-2.5 text-right text-ink-2">{euros(l.investi)}</td>
                <td className="py-2.5 text-right font-medium">{euros(l.final)}</td>
                <td className={`whitespace-nowrap py-2.5 text-right font-medium ${l.performance_pct >= 0 ? "text-gain" : "text-loss"}`}>{pourcentSigne(l.performance_pct)}</td>
              </motion.tr>
            ))}
          </tbody>
          <tfoot className="tabular-nums">
            <tr className="border-t border-line-strong font-semibold">
              <td className="pt-3" colSpan={2}>
                Total
              </td>
              <td className="pt-3 text-right">{euros(capital)}</td>
              <td className="pt-3 text-right">{euros(valeurFinale)}</td>
              <td className={`pt-3 text-right ${performancePct >= 0 ? "text-gain" : "text-loss"}`}>{pourcentSigne(performancePct)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </Carte>
  );
}
