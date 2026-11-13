"use client";

import { useCallback, useId, useState } from "react";
import { Link2 } from "lucide-react";
import { Annonce, BoutonExport, CocheAnimee, Depliant, LigneExport, useFlash } from "./commun";

/** Ligne "Lien de partage" : copie dans le presse-papiers, ou champ a copier a la main. */
export function ExportPartage({ lien }: { lien: string }) {
  const idChamp = useId();
  const [copie, flashCopie] = useFlash(2500);
  const [manuel, setManuel] = useState(false);
  // Stable : sinon React rappellerait la ref (et volerait le focus) a chaque rendu.
  const selectionner = useCallback((el: HTMLInputElement | null) => {
    el?.focus();
    el?.select();
  }, []);

  async function copier() {
    try {
      // Absent hors HTTPS ou refuse par le navigateur : on bascule sur la copie manuelle.
      if (!navigator.clipboard?.writeText) throw new Error("presse-papiers indisponible");
      await navigator.clipboard.writeText(lien);
      setManuel(false);
      flashCopie();
    } catch {
      setManuel(true);
    }
  }

  return (
    <LigneExport
      icone={Link2}
      titre="Lien de partage"
      description="L'adresse contient vos réglages : la personne qui l'ouvre retrouve la même simulation."
      action={
        copie ? (
          <BoutonExport cle="copie" ton="succes" onClick={copier}>
            <CocheAnimee />
            Lien copié
          </BoutonExport>
        ) : (
          <BoutonExport cle="repos" onClick={copier} aria-controls={manuel ? idChamp : undefined}>
            <Link2 className="size-4 text-accent" aria-hidden />
            Copier le lien
          </BoutonExport>
        )
      }
    >
      <Depliant visible={manuel}>
        <label htmlFor={idChamp} className="mb-1.5 block text-xs text-ink-2">
          Copie automatique indisponible : sélectionnez le lien puis copiez-le (Ctrl+C, ou appui long sur mobile).
        </label>
        <input
          id={idChamp}
          type="text"
          readOnly
          value={lien}
          ref={selectionner}
          onFocus={(e) => e.currentTarget.select()}
          className="w-full rounded-controle border border-line bg-surface px-3.5 py-2.5 font-mono text-xs text-ink outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
      </Depliant>
      <Annonce message={copie ? "Lien copié dans le presse-papiers." : ""} />
    </LigneExport>
  );
}
