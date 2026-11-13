"use client";

import { motion, type HTMLMotionProps } from "motion/react";
import { DUREE, EASE_SORTIE, PAS_CASCADE } from "./transitions";

type Props = HTMLMotionProps<"div"> & {
  /** Retard en secondes. */
  delai?: number;
  /** Ne s'anime qu'a l'arrivee dans l'ecran (defilement), une seule fois. */
  auDefilement?: boolean;
  /** Distance de glissement verticale en px. */
  decalage?: number;
};

/** Fondu + leger glissement vers le haut a l'apparition. */
// Sans flou : couteux sur les grands blocs et peu lisible (docs/BENCHMARK.md 3.6).
export function Apparition({ delai = 0, auDefilement = false, decalage = 8, children, ...reste }: Props) {
  const cible = { opacity: 1, y: 0 };
  return (
    <motion.div
      initial={{ opacity: 0, y: decalage }}
      {...(auDefilement ? { whileInView: cible, viewport: { once: true, margin: "0px 0px -60px 0px" } } : { animate: cible })}
      transition={{ duration: DUREE.normale + 0.1, ease: EASE_SORTIE, delay: delai }}
      {...reste}
    >
      {children}
    </motion.div>
  );
}

const conteneur = {
  cache: {},
  visible: { transition: { staggerChildren: PAS_CASCADE } },
};
const element = {
  cache: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } },
};

/** Conteneur dont les enfants <ElementCascade> apparaissent l'un apres l'autre. */
export function Cascade({ auDefilement = false, children, ...reste }: HTMLMotionProps<"div"> & { auDefilement?: boolean }) {
  return (
    <motion.div
      variants={conteneur}
      initial="cache"
      {...(auDefilement ? { whileInView: "visible", viewport: { once: true, margin: "0px 0px -40px 0px" } } : { animate: "visible" })}
      {...reste}
    >
      {children}
    </motion.div>
  );
}

export function ElementCascade({ children, ...reste }: HTMLMotionProps<"div">) {
  return (
    <motion.div variants={element} {...reste}>
      {children}
    </motion.div>
  );
}

/** Variante <li> pour les listes. */
export function LigneCascade({ children, ...reste }: HTMLMotionProps<"li">) {
  return (
    <motion.li variants={element} {...reste}>
      {children}
    </motion.li>
  );
}
