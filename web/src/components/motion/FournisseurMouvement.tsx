"use client";

import { MotionConfig } from "motion/react";
import type { ReactNode } from "react";

/** Coupe les animations si le visiteur a demande "reduire les animations" dans son systeme. */
export function FournisseurMouvement({ children }: { children: ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
