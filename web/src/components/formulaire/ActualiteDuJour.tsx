"use client";

import { useState } from "react";
import { Newspaper } from "lucide-react";
import { lireActualite } from "@/lib/api";
import { puce } from "./styles";

/** Bouton « Utiliser l'actualité du jour » : pré-remplit le scénario avec un texte neutre condensé par l'IA. */
export function ActualiteDuJour({ onUtiliser }: { onUtiliser: (texte: string) => void }) {
  const [chargement, setChargement] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function utiliser() {
    setChargement(true);
    setMessage(null);
    try {
      const actu = await lireActualite();
      if (actu.disponible && actu.scenario) onUtiliser(actu.scenario);
      else setMessage(actu.message ?? "Actualité indisponible pour le moment.");
    } catch {
      setMessage("Actualité indisponible pour le moment. Décrivez votre scénario vous-même.");
    } finally {
      setChargement(false);
    }
  }

  return (
    <div className="flex flex-col gap-1.5">
      <button
        type="button"
        onClick={utiliser}
        disabled={chargement}
        aria-busy={chargement}
        className={`${puce} inline-flex w-fit max-w-full items-center gap-1.5 disabled:cursor-wait disabled:opacity-60`}
      >
        <Newspaper className="size-3.5 shrink-0" aria-hidden />
        <span className="truncate">{chargement ? "Lecture de l'actualité…" : "Utiliser l'actualité du jour"}</span>
      </button>
      <p className="text-xs text-muted">Source : flux publics, texte condensé par l&apos;IA, à relire.</p>
      {message && (
        <p role="status" className="text-xs text-muted">
          {message}
        </p>
      )}
    </div>
  );
}
