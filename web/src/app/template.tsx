"use client";

import { motion } from "motion/react";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

// Rejoue a chaque changement de page : transition douce entre les pages.
export default function Transition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}>
      {children}
    </motion.div>
  );
}
