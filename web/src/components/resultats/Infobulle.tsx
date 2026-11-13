"use client";

import type { ReactNode } from "react";
import { AideInfo } from "@/components/ui/Infobulle";

/** Bouton (i) des resultats : une seule implementation d'infobulle sur le site (ui/Infobulle). */
export function Infobulle({ libelle, children, className = "" }: { libelle: string; children: ReactNode; className?: string }) {
  return (
    <span className={`inline-flex align-middle ${className}`}>
      <AideInfo texte={children} libelle={libelle} />
    </span>
  );
}
