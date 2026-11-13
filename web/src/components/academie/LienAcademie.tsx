"use client";

import type { ReactNode } from "react";
import { changerAncre } from "./ancre";

/** Lien vers une autre partie de l'Académie (change de module et défile jusqu'à la section). */
export function LienAcademie({ ancre, children }: { ancre: string; children: ReactNode }) {
  return (
    <a
      href={`#${ancre}`}
      onClick={(e) => {
        e.preventDefault();
        changerAncre(ancre);
      }}
      className="font-medium text-accent-ink underline decoration-accent/40 underline-offset-2 transition-colors hover:decoration-accent"
    >
      {children}
    </a>
  );
}
