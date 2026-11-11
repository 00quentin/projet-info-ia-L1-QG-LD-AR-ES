"use client";

import { useEffect, useMemo, useRef, type ComponentProps } from "react";
import { GraphiqueLignes } from "@/components/charts/GraphiqueLignes";
import { dateCourte } from "./outils";

type Props = Omit<ComponentProps<typeof GraphiqueLignes>, "etiquettesX"> & {
  /** Une date AAAA-MM-JJ par point des series. */
  dates: string[];
};

const ECART_MIN = 10;

type Boite = { x: number; y: number; width: number; height: number };
const chevauche = (a: Boite, b: Boite) =>
  a.x < b.x + b.width + ECART_MIN && b.x < a.x + a.width + ECART_MIN && a.y < b.y + b.height && b.y < a.y + a.height;

/**
 * GraphiqueLignes sur l'axe des vraies dates. Les dates completes ("17 févr. 2020")
 * sont lisibles dans la bulle de survol, mais trop longues pour toutes tenir sous
 * l'axe : on masque les etiquettes qui se chevauchent, en gardant la premiere et la derniere.
 */
export function GraphiqueDates({ dates, ...props }: Props) {
  const conteneur = useRef<HTMLDivElement>(null);
  const etiquettes = useMemo(() => dates.map(dateCourte), [dates]);

  useEffect(() => {
    const racine = conteneur.current;
    const svg = racine?.querySelector("svg");
    if (!svg) return;
    let image = 0;
    const ajuster = () => {
      cancelAnimationFrame(image);
      image = requestAnimationFrame(() => {
        // Les etiquettes de l'axe horizontal sont les <text> enfants directs du SVG.
        const textes = Array.from(svg.querySelectorAll<SVGTextElement>(":scope > text"));
        for (const t of textes) t.style.removeProperty("visibility");
        if (textes.length < 3) return;
        const boites = textes.map((t) => t.getBBox());
        const derniere = boites[boites.length - 1];
        let gardee = boites[0];
        for (let i = 1; i < textes.length - 1; i++) {
          if (chevauche(boites[i], gardee) || chevauche(boites[i], derniere)) textes[i].style.visibility = "hidden";
          else gardee = boites[i];
        }
      });
    };
    ajuster();
    document.fonts?.ready.then(ajuster);
    const observateur = new MutationObserver(ajuster);
    observateur.observe(svg, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["x", "text-anchor", "width"] });
    return () => {
      observateur.disconnect();
      cancelAnimationFrame(image);
    };
  }, []);

  return (
    <div ref={conteneur}>
      <GraphiqueLignes etiquettesX={etiquettes} {...props} />
    </div>
  );
}
