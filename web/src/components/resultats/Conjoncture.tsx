"use client";

import { motion } from "motion/react";
import type { Conjoncture as TypeConjoncture } from "@/lib/api";
import { dateFr, nombre } from "@/lib/format";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import { Infobulle } from "./Infobulle";

/**
 * Taux et inflation du moment (FRED) : le point de depart dont l'IA a tenu compte.
 * Rien n'est affiche si FRED n'a pas repondu.
 */
export function Conjoncture({ conjoncture, titre = "Point de départ (conjoncture réelle)", compacte = false }: { conjoncture?: TypeConjoncture | null; titre?: string; compacte?: boolean }) {
  if (!conjoncture?.indicateurs.length) return null;
  return (
    <section aria-label={titre}>
      <div className="flex flex-wrap items-center justify-between gap-x-2 gap-y-1">
        <h4 className="text-aide font-medium text-muted">{titre}</h4>
        <span className="inline-flex items-center gap-1 text-xs text-muted">
          Source : FRED (Réserve fédérale de Saint-Louis)
          <Infobulle libelle="Dates des données de conjoncture">
            <span className="flex flex-col gap-0.5">
              {conjoncture.indicateurs.map((i) => (
                <span key={i.cle}>
                  {i.nom} : {i.source}, donnée du {dateFr(i.date)}
                </span>
              ))}
            </span>
          </Infobulle>
        </span>
      </div>
      <ul className={`mt-2.5 grid gap-2 ${compacte ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-2 sm:grid-cols-3 xl:grid-cols-6"}`}>
        {conjoncture.indicateurs.map((i, k) => (
          <motion.li
            key={i.cle}
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: DUREE.normale, ease: EASE_SORTIE, delay: k * 0.04 }}
            className="rounded-tuile bg-surface-2/70 px-3 py-2"
          >
            <span className="block text-xs leading-tight text-muted">{i.nom}</span>
            <span className="mt-0.5 block text-base font-semibold tabular-nums">{nombre(i.valeur, 2)} %</span>
          </motion.li>
        ))}
      </ul>
    </section>
  );
}
