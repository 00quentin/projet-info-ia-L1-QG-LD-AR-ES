"use client";

import { motion } from "motion/react";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

// Rejoue a chaque changement de page : un fondu court, sans deplacement.
export default function Transition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: DUREE.rapide + 0.03, ease: EASE_SORTIE }}>
      {children}
    </motion.div>
  );
}
