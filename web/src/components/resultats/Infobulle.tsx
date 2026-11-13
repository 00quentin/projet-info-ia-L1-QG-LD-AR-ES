"use client";

import { useEffect, useId, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { Info } from "lucide-react";

// Marge minimale entre la bulle et le bord de l'ecran (px).
const MARGE_ECRAN = 12;

/**
 * Petit bouton (i) qui affiche une explication au survol, au focus clavier ou au toucher.
 * Remplace les infobulles natives `title=` : lisible au clavier, fermee par Echap,
 * et le texte reste lu par les lecteurs d'ecran meme bulle fermee (aria-describedby).
 */
export function Infobulle({ libelle, children, className = "" }: { libelle: string; children: ReactNode; className?: string }) {
  const id = useId();
  const [ouvert, setOuvert] = useState(false);
  const [decalage, setDecalage] = useState(0);
  const zone = useRef<HTMLSpanElement>(null);
  const bulle = useRef<HTMLSpanElement>(null);

  // La bulle est centree sous le bouton, puis recalee pour ne jamais deborder de l'ecran.
  useLayoutEffect(() => {
    if (!ouvert || !bulle.current) return;
    const r = bulle.current.getBoundingClientRect();
    const largeurEcran = document.documentElement.clientWidth;
    const centre = r.left - decalage + r.width / 2;
    const gauche = centre - r.width / 2;
    let d = 0;
    if (gauche < MARGE_ECRAN) d = MARGE_ECRAN - gauche;
    else if (gauche + r.width > largeurEcran - MARGE_ECRAN) d = largeurEcran - MARGE_ECRAN - (gauche + r.width);
    if (Math.abs(d - decalage) > 0.5) setDecalage(d);
  }, [ouvert, decalage]);

  useEffect(() => {
    if (!ouvert) return;
    const surTouche = (e: KeyboardEvent) => e.key === "Escape" && setOuvert(false);
    const surClic = (e: PointerEvent) => !zone.current?.contains(e.target as Node) && setOuvert(false);
    document.addEventListener("keydown", surTouche);
    document.addEventListener("pointerdown", surClic);
    return () => {
      document.removeEventListener("keydown", surTouche);
      document.removeEventListener("pointerdown", surClic);
    };
  }, [ouvert]);

  return (
    <span
      ref={zone}
      className={`relative inline-flex align-middle ${className}`}
      onPointerEnter={(e) => e.pointerType === "mouse" && setOuvert(true)}
      onPointerLeave={(e) => e.pointerType === "mouse" && setOuvert(false)}
    >
      <button
        type="button"
        aria-label={libelle}
        aria-describedby={id}
        onClick={() => setOuvert(true)}
        onFocus={() => setOuvert(true)}
        onBlur={() => setOuvert(false)}
        className="grid size-5 place-items-center rounded-full text-muted transition-colors hover:text-ink"
      >
        <Info className="size-3.5" aria-hidden />
      </button>
      <span
        ref={bulle}
        id={id}
        role="tooltip"
        style={{ transform: `translateX(calc(-50% + ${decalage}px))` }}
        className={`absolute left-1/2 top-full z-30 mt-1.5 w-max max-w-[min(18rem,calc(100vw-2rem))] rounded-tuile border border-line bg-surface px-3 py-2 text-left text-aide font-normal normal-case tracking-normal text-ink-2 shadow-card ${ouvert ? "block" : "hidden"}`}
      >
        {children}
      </span>
    </span>
  );
}
