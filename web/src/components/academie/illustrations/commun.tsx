"use client";

import { useId, type ReactNode } from "react";
import { motion, useReducedMotion, type Variants } from "motion/react";
import { EASE_SORTIE } from "@/components/motion/transitions";

// Chaque schéma se dessine une fois, quand il arrive à l'écran.
// "custom" (secondes) décale un élément dans la séquence.

/** Trait qui se dessine. */
export const trait: Variants = {
  cache: { pathLength: 0, opacity: 0 },
  visible: (d: number = 0) => ({
    pathLength: 1,
    opacity: 1,
    transition: { pathLength: { duration: 0.55, ease: EASE_SORTIE, delay: d }, opacity: { duration: 0.05, delay: d } },
  }),
};

/** Élément qui apparaît en fondu. */
export const fondu: Variants = {
  cache: { opacity: 0 },
  visible: (d: number = 0) => ({ opacity: 1, transition: { duration: 0.35, ease: EASE_SORTIE, delay: d } }),
};

/** Élément qui pousse depuis son centre ou sa base (barres, corps de bougie). */
export const pousse: Variants = {
  cache: { scaleY: 0, opacity: 0 },
  visible: (d: number = 0) => ({ scaleY: 1, opacity: 1, transition: { duration: 0.45, ease: EASE_SORTIE, delay: d } }),
};

/** Point qui surgit. */
export const surgit: Variants = {
  cache: { scale: 0, opacity: 0 },
  visible: (d: number = 0) => ({ scale: 1, opacity: 1, transition: { type: "spring", stiffness: 420, damping: 22, delay: d } }),
};

/** Pour scale/scaleY sur des éléments SVG : l'origine doit être la boîte de l'élément. */
export const origine = (o: string = "center") => ({ transformBox: "fill-box" as const, transformOrigin: o });

type PropsSchema = {
  titre: string;
  description: string;
  viewBox: string;
  children: ReactNode;
  className?: string;
};

/** SVG accessible qui joue sa séquence d'entrée une seule fois. */
export function SchemaAnime({ titre, description, viewBox, children, className = "" }: PropsSchema) {
  const id = useId();
  const reduit = useReducedMotion();
  return (
    <motion.svg
      viewBox={viewBox}
      role="img"
      aria-labelledby={`${id}-t ${id}-d`}
      initial={reduit ? "visible" : "cache"}
      whileInView="visible"
      viewport={{ once: true, margin: "0px 0px -80px 0px" }}
      className={`block h-auto w-full select-none overflow-visible ${className}`}
      fontFamily="inherit"
    >
      <title id={`${id}-t`}>{titre}</title>
      <desc id={`${id}-d`}>{description}</desc>
      {children}
    </motion.svg>
  );
}

/** Cadre carte + légende sous le schéma. */
export function CadreSchema({ legende, credit, children }: { legende: ReactNode; credit?: string; children: ReactNode }) {
  return (
    <figure className="max-w-[46rem]">
      <div className="rounded-carte border border-line bg-surface p-4 shadow-card sm:p-6">{children}</div>
      <figcaption className="mt-2.5 text-sm leading-relaxed text-muted">
        {legende}
        {credit && <span className="text-xs opacity-80"> · {credit}</span>}
      </figcaption>
    </figure>
  );
}
