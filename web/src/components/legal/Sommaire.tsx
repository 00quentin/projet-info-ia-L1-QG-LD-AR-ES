"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { ListTree } from "lucide-react";
import { RESSORT } from "@/components/motion/transitions";

export type EntreeSommaire = { id: string; titre: string; numero?: string };

// Sous cette ligne (px depuis le haut de la fenêtre), une partie est « en cours de lecture ».
const LIGNE_LECTURE = 160;

function useSectionVisible(entrees: EntreeSommaire[]) {
  const [visible, setVisible] = useState(entrees[0]?.id);

  useEffect(() => {
    let image = 0;
    const mesurer = () => {
      image = 0;
      let courante = entrees[0]?.id;
      for (const e of entrees) {
        const el = document.getElementById(e.id);
        if (el && el.getBoundingClientRect().top <= LIGNE_LECTURE) courante = e.id;
      }
      // Tout en bas de la page, la dernière partie est forcément celle qu'on lit.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) courante = entrees[entrees.length - 1]?.id;
      setVisible(courante);
    };
    const auDefilement = () => {
      if (!image) image = requestAnimationFrame(mesurer);
    };
    auDefilement();
    window.addEventListener("scroll", auDefilement, { passive: true });
    window.addEventListener("resize", auDefilement);
    return () => {
      cancelAnimationFrame(image);
      window.removeEventListener("scroll", auDefilement);
      window.removeEventListener("resize", auDefilement);
    };
  }, [entrees]);

  return visible;
}

/** Table des matières collante (grand écran) : la partie en cours de lecture est surlignée. */
export function SommaireLateral({ entrees, libelle = "Sur cette page" }: { entrees: EntreeSommaire[]; libelle?: string }) {
  const visible = useSectionVisible(entrees);
  return (
    <nav aria-label="Sommaire" className="sticky top-32">
      <p className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted">
        <ListTree className="size-3.5" aria-hidden />
        {libelle}
      </p>
      <ul className="relative flex flex-col border-l border-line">
        {entrees.map((e) => {
          const actif = e.id === visible;
          return (
            <li key={e.id} className="relative">
              {actif && <motion.span layoutId="legal-sommaire-actif" className="absolute -left-px inset-y-0 w-0.5 rounded-full bg-accent" transition={RESSORT} />}
              <a
                href={`#${e.id}`}
                aria-current={actif ? "location" : undefined}
                className={`block py-1.5 pl-4 text-[13px] leading-snug transition-colors ${actif ? "font-medium text-ink" : "text-muted hover:text-ink"}`}
              >
                {e.numero && <span className="mr-1.5 tabular-nums text-accent">{e.numero}</span>}
                {e.titre}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

/** Sommaire repliable affiché à la place de la table latérale sur mobile. */
export function SommaireMobile({ entrees }: { entrees: EntreeSommaire[] }) {
  return (
    <details className="group rounded-2xl border border-line bg-surface px-4 py-3 shadow-card lg:hidden">
      <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-medium text-ink [&::-webkit-details-marker]:hidden">
        <ListTree className="size-4 text-muted" aria-hidden />
        Sommaire
        <span className="ml-auto text-muted transition-transform group-open:rotate-90" aria-hidden>
          ›
        </span>
      </summary>
      <ul className="mt-3 flex flex-col gap-1 border-t border-line pt-3">
        {entrees.map((e) => (
          <li key={e.id}>
            <a href={`#${e.id}`} className="block py-1 text-sm text-ink-2 hover:text-ink">
              {e.numero && <span className="mr-1.5 tabular-nums text-accent">{e.numero}</span>}
              {e.titre}
            </a>
          </li>
        ))}
      </ul>
    </details>
  );
}
