"use client";

import { motion } from "motion/react";
import type { Conjoncture as TypeConjoncture } from "@/lib/api";
import { dateFr, nombre } from "@/lib/format";
import { EASE_SORTIE } from "@/components/motion/transitions";

/**
 * Taux et inflation du moment (FRED) : le point de depart dont l'IA a tenu compte.
 * Rien n'est affiche si FRED n'a pas repondu.
 */
export function Conjoncture({ conjoncture, titre = "Point de départ (conjoncture réelle)", compacte = false }: { conjoncture?: TypeConjoncture | null; titre?: string; compacte?: boolean }) {
  if (!conjoncture?.indicateurs.length) return null;
  return (
    <section aria-label={titre}>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h4 className="text-xs font-medium text-muted">{titre}</h4>
        <span className="text-[11px] text-muted">Source : FRED (Réserve fédérale de Saint-Louis)</span>
      </div>
      <ul className={`mt-2.5 grid gap-2 ${compacte ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-2 sm:grid-cols-3 xl:grid-cols-6"}`}>
        {conjoncture.indicateurs.map((i, k) => (
          <motion.li
            key={i.cle}
            initial={{ opacity: 0, y: 6 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.35, ease: EASE_SORTIE, delay: k * 0.05 }}
            title={`${i.source} · donnée du ${dateFr(i.date)}`}
            className="rounded-xl bg-surface-2/70 px-3 py-2"
          >
            <span className="block text-[11px] leading-tight text-muted">{i.nom}</span>
            <span className="mt-0.5 block text-base font-semibold tabular-nums">{nombre(i.valeur, 2)} %</span>
          </motion.li>
        ))}
      </ul>
    </section>
  );
}
