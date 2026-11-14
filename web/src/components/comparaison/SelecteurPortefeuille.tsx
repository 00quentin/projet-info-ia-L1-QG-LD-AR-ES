"use client";

import type { Catalogue } from "@/lib/api";
import { Carte } from "@/components/ui/Carte";
import { ChoixPortefeuille, type ValeurPortefeuille } from "@/components/formulaire/ChoixPortefeuille";

type Props = {
  etiquette: "A" | "B";
  /** Variable CSS de la couleur de ce portefeuille (la meme que sur le graphique). */
  couleur: string;
  catalogue: Catalogue;
  valeur: ValeurPortefeuille;
  onChange: (v: ValeurPortefeuille) => void;
};

/** Un des deux portefeuilles a comparer. Les actifs personnalises sont masques : l'analyse de l'IA doit etre partagee. */
export function SelecteurPortefeuille({ etiquette, couleur, catalogue, valeur, onChange }: Props) {
  return (
    <Carte taille="normale" className="min-w-0">
      <h2 className="mb-4 flex items-center gap-2.5 text-titre font-semibold tracking-tight">
        <span aria-hidden className="grid size-6 place-items-center rounded-controle text-xs font-semibold text-white" style={{ background: couleur }}>
          {etiquette}
        </span>
        Portefeuille {etiquette}
      </h2>
      <ChoixPortefeuille catalogue={catalogue} valeur={valeur} onChange={onChange} autoriserActifsPerso={false} />
    </Carte>
  );
}
