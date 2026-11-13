"use client";

import { useId, useLayoutEffect, type RefObject } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ArrowUp } from "lucide-react";
import { LONGUEUR_MAX } from "./conversation";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

/** Le compteur n'apparait qu'a l'approche de la limite. */
const SEUIL_COMPTEUR = 3500;
const LIGNES_MAX = 5;

type Props = {
  valeur: string;
  onChange: (v: string) => void;
  onEnvoyer: () => void;
  enAttente: boolean;
  champRef: RefObject<HTMLTextAreaElement | null>;
};

export function Saisie({ valeur, onChange, onEnvoyer, enAttente, champRef }: Props) {
  const idAide = useId();
  const vide = !valeur.trim();
  const longueur = valeur.length;

  // La zone grandit avec le texte, jusqu'a LIGNES_MAX lignes, puis defile.
  useLayoutEffect(() => {
    const champ = champRef.current;
    if (!champ) return;
    const style = getComputedStyle(champ);
    const ligne = parseFloat(style.lineHeight) || 20;
    const marges = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
    champ.style.height = "auto";
    champ.style.height = `${Math.min(champ.scrollHeight, ligne * LIGNES_MAX + marges)}px`;
  }, [valeur, champRef]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!vide && !enAttente) onEnvoyer();
      }}
    >
      <div
        className={`flex items-end gap-2 rounded-tuile border bg-surface py-1.5 pl-3.5 pr-1.5 transition-colors focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20 ${enAttente ? "border-line opacity-70" : "border-line-strong"}`}
      >
        <label htmlFor={`${idAide}-champ`} className="sr-only">
          Votre question à l&apos;analyste
        </label>
        <textarea
          id={`${idAide}-champ`}
          ref={champRef}
          rows={1}
          value={valeur}
          maxLength={LONGUEUR_MAX}
          // Lecture seule plutot que "disabled" : le focus reste dans la zone pendant l'attente.
          readOnly={enAttente}
          aria-disabled={enAttente || undefined}
          aria-describedby={idAide}
          placeholder={enAttente ? "L'analyste rédige sa réponse…" : "Posez votre question…"}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              e.currentTarget.form?.requestSubmit();
            }
          }}
          // Le cadre autour porte deja l'anneau de focus ; le contour global (hors couche Tailwind) le doublerait.
          style={{ outline: "none" }}
          className="min-h-9 flex-1 resize-none bg-transparent py-2 text-sm leading-5 text-ink placeholder:text-muted"
        />
        <motion.button
          type="submit"
          disabled={vide || enAttente}
          whileTap={vide || enAttente ? undefined : { scale: 0.97 }}
          aria-label="Envoyer la question (Entrée)"
          className="grid size-9 shrink-0 place-items-center rounded-controle bg-accent text-on-accent transition-[background-color,opacity] disabled:cursor-not-allowed disabled:bg-line-strong disabled:text-surface"
        >
          <ArrowUp className="size-4" strokeWidth={2.5} aria-hidden />
        </motion.button>
      </div>
      <div className="mt-1.5 flex items-center justify-between gap-3 px-1 text-xs leading-4 text-muted">
        <p id={idAide}>
          <span className="hidden sm:inline">Entrée pour envoyer, Maj + Entrée pour aller à la ligne · </span>
          Réponses générées par une IA, pas un conseil.
        </p>
        <AnimatePresence>
          {longueur >= SEUIL_COMPTEUR && (
            <motion.span
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }}
              className={`shrink-0 tabular-nums ${longueur >= LONGUEUR_MAX ? "font-semibold text-loss" : "text-warn"}`}
            >
              {longueur.toLocaleString("fr-FR")} / {LONGUEUR_MAX.toLocaleString("fr-FR")}
            </motion.span>
          )}
        </AnimatePresence>
      </div>
    </form>
  );
}
