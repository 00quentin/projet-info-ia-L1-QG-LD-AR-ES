"use client";

import { motion } from "motion/react";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { RESSORT } from "@/components/motion/transitions";
import { MEMBRES_EQUIPE } from "@/contenu/apropos";

const initiales = (nom: string) =>
  nom
    .split(" ")
    .slice(0, 2)
    .map((m) => m[0])
    .join("");

export function Equipe() {
  return (
    <Cascade auDefilement className="grid grid-cols-1 gap-3 min-[420px]:grid-cols-2 lg:grid-cols-4">
      {MEMBRES_EQUIPE.map((m) => (
        <ElementCascade key={m.nom} whileHover="survol" className="group">
          <motion.div
            variants={{ survol: { y: -3 } }}
            transition={RESSORT}
            className="flex h-full flex-col items-center rounded-2xl border border-line bg-surface px-4 py-6 text-center shadow-card transition-colors group-hover:border-line-strong"
          >
            <motion.span
              variants={{ survol: { scale: 1.06, rotate: -4 } }}
              transition={RESSORT}
              aria-hidden
              className="grid size-16 place-items-center rounded-full bg-gradient-to-br from-[#4338ca] to-[#6366f1] text-lg font-bold text-white shadow-card"
            >
              {initiales(m.nom)}
            </motion.span>
            <h3 className="mt-4 text-[15px] font-semibold tracking-tight text-ink">{m.nom}</h3>
            <p className="mt-1.5 text-sm leading-snug text-muted">{m.description}</p>
          </motion.div>
        </ElementCascade>
      ))}
    </Cascade>
  );
}
