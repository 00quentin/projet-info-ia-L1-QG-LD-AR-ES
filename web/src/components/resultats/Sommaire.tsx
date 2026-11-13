"use client";

import { useEffect, useRef, useState } from "react";

export type EntreeSommaire = { id: string; libelle: string };

const ECART = 8;

/**
 * Bas de l'en-tete du site s'il reste colle en haut de l'ecran (0 sinon).
 * Mesure au lieu d'une valeur ecrite en dur : la mise en page de l'en-tete peut changer.
 */
function useBasEntete(): number {
  const [bas, setBas] = useState(0);
  useEffect(() => {
    let image = 0;
    let collant: HTMLElement | null | undefined;
    // L'en-tete du site est le premier <header> de la page ; on garde son ancetre collant le plus haut.
    const trouver = () => {
      let trouve: HTMLElement | null = null;
      for (let n = document.querySelector("header") as HTMLElement | null; n && n !== document.body; n = n.parentElement) {
        const position = getComputedStyle(n).position;
        if (position === "sticky" || position === "fixed") trouve = n;
      }
      return trouve;
    };
    const mesurer = () => {
      image = 0;
      if (collant === undefined) collant = trouver();
      setBas(collant ? Math.max(0, Math.round(collant.getBoundingClientRect().bottom)) : 0);
    };
    const planifier = () => {
      if (!image) image = requestAnimationFrame(mesurer);
    };
    const surRedimension = () => {
      collant = undefined;
      planifier();
    };
    planifier();
    window.addEventListener("scroll", planifier, { passive: true });
    window.addEventListener("resize", surRedimension);
    return () => {
      cancelAnimationFrame(image);
      window.removeEventListener("scroll", planifier);
      window.removeEventListener("resize", surRedimension);
    };
  }, []);
  return bas;
}

/** Navigation interne des resultats : reste visible au defilement, la partie lue est surlignee. */
export function Sommaire({ entrees, libelle = "Sommaire des résultats" }: { entrees: EntreeSommaire[]; libelle?: string }) {
  const basEntete = useBasEntete();
  const nav = useRef<HTMLElement>(null);
  const [courante, setCourante] = useState(entrees[0]?.id);

  useEffect(() => {
    let image = 0;
    const mesurer = () => {
      image = 0;
      const ligne = basEntete + (nav.current?.offsetHeight ?? 0) + ECART * 3;
      let id = entrees[0]?.id;
      for (const e of entrees) {
        const el = document.getElementById(e.id);
        if (el && el.getBoundingClientRect().top <= ligne) id = e.id;
      }
      // Tout en bas de la page, la derniere partie est forcement celle qu'on lit.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) id = entrees[entrees.length - 1]?.id;
      setCourante(id);
    };
    const planifier = () => {
      if (!image) image = requestAnimationFrame(mesurer);
    };
    planifier();
    window.addEventListener("scroll", planifier, { passive: true });
    window.addEventListener("resize", planifier);
    return () => {
      cancelAnimationFrame(image);
      window.removeEventListener("scroll", planifier);
      window.removeEventListener("resize", planifier);
    };
  }, [entrees, basEntete]);

  // Garde le lien actif visible quand la barre defile horizontalement (mobile).
  useEffect(() => {
    const liste = nav.current?.querySelector("ul");
    const lien = liste?.querySelector<HTMLElement>(`[data-cible="${courante}"]`);
    if (!liste || !lien) return;
    if (lien.offsetLeft < liste.scrollLeft || lien.offsetLeft + lien.offsetWidth > liste.scrollLeft + liste.clientWidth) {
      liste.scrollTo({ left: lien.offsetLeft - ECART });
    }
  }, [courante]);

  function aller(id: string) {
    const el = document.getElementById(id);
    if (!el) return;
    const haut = el.getBoundingClientRect().top + window.scrollY - basEntete - (nav.current?.offsetHeight ?? 0) - ECART * 2;
    const reduit = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: Math.max(0, haut), behavior: reduit ? "auto" : "smooth" });
    // Le focus suit pour le clavier et les lecteurs d'ecran (sans redefiler).
    el.focus({ preventScroll: true });
  }

  return (
    <nav ref={nav} aria-label={libelle} className="sticky z-20" style={{ top: basEntete + ECART }}>
      <ul className="flex gap-0.5 overflow-x-auto rounded-controle border border-line bg-surface/90 p-1 shadow-card backdrop-blur [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {entrees.map((e) => {
          const actif = e.id === courante;
          return (
            <li key={e.id} className="shrink-0">
              <a
                href={`#${e.id}`}
                data-cible={e.id}
                aria-current={actif ? "location" : undefined}
                onClick={(ev) => {
                  ev.preventDefault();
                  aller(e.id);
                }}
                className={`block rounded-md px-2.5 py-1.5 text-aide font-medium transition-colors ${actif ? "bg-surface-2 text-ink" : "text-muted hover:text-ink"}`}
              >
                {e.libelle}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
