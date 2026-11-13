"use client";

import { animate, useInView, useReducedMotion } from "motion/react";
import { useEffect, useRef } from "react";
import { EASE_SORTIE } from "./transitions";

type Props = {
  valeur: number;
  /** Valeur de depart du premier comptage (ex. le capital initial). */
  depuis?: number;
  format: (v: number) => string;
  duree?: number;
  className?: string;
};

/**
 * Nombre qui "compte" jusqu'a sa valeur quand il entre a l'ecran, puis glisse
 * d'une valeur a l'autre quand elle change. Le texte est ecrit directement dans
 * le DOM a chaque image (pas de re-rendu React par image).
 */
export function NombreAnime({ valeur, depuis, format, duree = 1.1, className }: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const precedente = useRef<number>(depuis ?? valeur);
  const visible = useInView(ref, { once: true });
  const reduit = useReducedMotion();
  // Le format est souvent une fonction recreee a chaque rendu : on la garde dans
  // une ref pour ne pas relancer (et couper) le comptage a chaque re-rendu du parent.
  const formatRef = useRef(format);
  useEffect(() => {
    formatRef.current = format;
  });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (!visible || reduit) {
      el.textContent = formatRef.current(valeur);
      precedente.current = valeur;
      return;
    }
    const controle = animate(precedente.current, valeur, {
      duration: duree,
      ease: EASE_SORTIE,
      onUpdate: (v) => {
        el.textContent = formatRef.current(v);
      },
    });
    precedente.current = valeur;
    return () => controle.stop();
  }, [valeur, visible, reduit, duree]);

  // Rendu serveur / premier affichage : la valeur finale (lisible meme sans JS).
  return (
    <span ref={ref} className={className}>
      {format(valeur)}
    </span>
  );
}
