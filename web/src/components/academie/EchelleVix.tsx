"use client";

import type { ReactNode } from "react";
import { motion } from "motion/react";
import { Cascade, LigneCascade } from "@/components/motion/Apparition";
import { EASE_SORTIE } from "@/components/motion/transitions";

// Largeurs de la jauge : zones 0-15, 15-25, 25-40, 40-85 (le VIX a culminé à 82).
const ZONES: { seuil: string; couleur: string; largeur: number; texte: ReactNode }[] = [
  { seuil: "VIX < 15", couleur: "var(--gain)", largeur: 15, texte: "marché calme, euphorie, complaisance. Danger latent." },
  { seuil: "VIX 15-25", couleur: "var(--accent)", largeur: 10, texte: "volatilité normale." },
  { seuil: "VIX 25-40", couleur: "var(--warn)", largeur: 15, texte: "marché nerveux, tensions." },
  {
    seuil: "VIX > 40",
    couleur: "var(--loss)",
    largeur: 45,
    texte: "panique. Le VIX a culminé à 82 le 16 mars 2020 (COVID) et à 80 en octobre 2008 (Lehman Brothers).",
  },
];

/** Les zones du VIX : jauge colorée + explication de chaque zone. */
export function EchelleVix() {
  return (
    <div className="max-w-[40rem] rounded-carte border border-line bg-surface p-5 shadow-card">
      <div className="flex h-3 gap-0.5 overflow-hidden rounded-full" aria-hidden>
        {ZONES.map((z, i) => (
          <motion.span
            key={z.seuil}
            className="h-full origin-left"
            style={{ width: `${(z.largeur / 85) * 100}%`, background: z.couleur }}
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, ease: EASE_SORTIE, delay: 0.1 + i * 0.1 }}
          />
        ))}
      </div>
      <div className="mt-1.5 flex text-xs text-muted tabular-nums" aria-hidden>
        <span style={{ width: `${(15 / 85) * 100}%` }}>0</span>
        <span style={{ width: `${(10 / 85) * 100}%` }}>15</span>
        <span style={{ width: `${(15 / 85) * 100}%` }}>25</span>
        <span className="flex-1">40</span>
        <span>85</span>
      </div>
      <Cascade auDefilement>
        <ul className="mt-4 flex flex-col gap-2.5 text-titre leading-relaxed text-ink-2">
          {ZONES.map((z) => (
            <LigneCascade key={z.seuil} className="flex gap-3">
              <span className="mt-1.5 h-3 w-1.5 shrink-0 rounded-full" style={{ background: z.couleur }} aria-hidden />
              <span>
                <span className="font-semibold text-ink tabular-nums">{z.seuil}</span> : {z.texte}
              </span>
            </LigneCascade>
          ))}
        </ul>
      </Cascade>
    </div>
  );
}
