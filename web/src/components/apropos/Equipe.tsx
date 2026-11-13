"use client";

import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { MEMBRES_EQUIPE } from "@/contenu/apropos";

const initiales = (nom: string) =>
  nom
    .split(" ")
    .slice(0, 2)
    .map((m) => m[0])
    .join("");

export function Equipe() {
  return (
    <Cascade auDefilement className="grid grid-cols-1 gap-3 min-[420px]:grid-cols-2 lg:grid-cols-4">
      {MEMBRES_EQUIPE.map((m) => (
        <ElementCascade key={m.nom}>
          <div className="flex h-full flex-col items-center rounded-carte border border-line bg-surface px-4 py-6 text-center shadow-card">
            <span aria-hidden className="grid size-16 place-items-center rounded-full bg-accent-soft text-lg font-semibold text-accent-ink">
              {initiales(m.nom)}
            </span>
            <h3 className="mt-4 text-titre font-semibold tracking-tight text-ink">{m.nom}</h3>
            <p className="mt-1.5 text-sm leading-snug text-muted">{m.description}</p>
          </div>
        </ElementCascade>
      ))}
    </Cascade>
  );
}
