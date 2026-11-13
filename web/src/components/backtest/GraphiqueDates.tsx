"use client";

import { useMemo, type ComponentProps } from "react";
import { GraphiqueLignes } from "@/components/charts/GraphiqueLignes";
import { dateCourte } from "./outils";

type Props = Omit<ComponentProps<typeof GraphiqueLignes>, "etiquettesX"> & {
  /** Une date AAAA-MM-JJ par point des series. */
  dates: string[];
};

/** GraphiqueLignes sur l'axe des vraies dates (le graphique espace lui-meme les graduations). */
export function GraphiqueDates({ dates, ...props }: Props) {
  const etiquettes = useMemo(() => dates.map(dateCourte), [dates]);
  return <GraphiqueLignes etiquettesX={etiquettes} {...props} />;
}
