"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { Trash2 } from "lucide-react";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

/** "Effacer l'historique" avec une petite fenetre de confirmation (action definitive). */
export function BoutonEffacer({ nombre, onConfirmer }: { nombre: number; onConfirmer: () => void }) {
  const [ouvert, setOuvert] = useState(false);
  const zone = useRef<HTMLDivElement>(null);
  const declencheur = useRef<HTMLButtonElement>(null);
  const annuler = useRef<HTMLButtonElement>(null);
  const idFenetre = useId();

  // Page cachee par la navigation : on ne veut pas retrouver la confirmation ouverte au retour.
  useLayoutEffect(() => () => setOuvert(false), []);

  useEffect(() => {
    if (!ouvert) return;
    annuler.current?.focus();
    const surTouche = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOuvert(false);
        declencheur.current?.focus();
      }
    };
    const surClic = (e: PointerEvent) => {
      if (!zone.current?.contains(e.target as Node)) setOuvert(false);
    };
    document.addEventListener("keydown", surTouche);
    document.addEventListener("pointerdown", surClic);
    return () => {
      document.removeEventListener("keydown", surTouche);
      document.removeEventListener("pointerdown", surClic);
    };
  }, [ouvert]);

  function fermer() {
    setOuvert(false);
    declencheur.current?.focus();
  }

  return (
    <div ref={zone} className="relative">
      <motion.button
        ref={declencheur}
        type="button"
        onClick={() => setOuvert((o) => !o)}
        aria-expanded={ouvert}
        aria-haspopup="dialog"
        aria-controls={ouvert ? idFenetre : undefined}
        whileHover={{ y: -1 }}
        whileTap={{ scale: 0.97 }}
        transition={RESSORT}
        className="inline-flex h-9 items-center gap-2 rounded-xl border border-line bg-surface px-3 text-sm font-medium text-ink-2 transition-colors hover:border-loss/40 hover:text-loss"
      >
        <Trash2 className="size-4" aria-hidden />
        Effacer l&apos;historique
      </motion.button>
      <AnimatePresence>
        {ouvert && (
          <motion.div
            id={idFenetre}
            role="dialog"
            aria-labelledby={`${idFenetre}-titre`}
            aria-describedby={`${idFenetre}-texte`}
            initial={{ opacity: 0, scale: 0.95, y: -6 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: -4, transition: { duration: DUREE.rapide } }}
            transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }}
            style={{ transformOrigin: "top right" }}
            className="absolute right-0 top-full z-20 mt-2 w-72 max-w-[calc(100vw-2rem)] rounded-xl border border-line bg-surface p-4 shadow-[0_8px_32px_rgba(15,17,21,0.14)]"
          >
            <p id={`${idFenetre}-titre`} className="text-sm font-semibold">
              Effacer tout l&apos;historique ?
            </p>
            <p id={`${idFenetre}-texte`} className="mt-1 text-xs leading-relaxed text-ink-2">
              {nombre > 1 ? `Les ${nombre} entrées seront supprimées` : "L'entrée sera supprimée"} de ce navigateur. Cette action est définitive.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <motion.button
                ref={annuler}
                type="button"
                onClick={fermer}
                whileTap={{ scale: 0.97 }}
                className="h-8 rounded-lg border border-line px-3 text-sm font-medium transition-colors hover:bg-surface-2"
              >
                Annuler
              </motion.button>
              <motion.button
                type="button"
                onClick={() => {
                  setOuvert(false);
                  onConfirmer();
                }}
                whileTap={{ scale: 0.97 }}
                className="h-8 rounded-lg bg-loss px-3 text-sm font-semibold text-white transition hover:brightness-110"
              >
                Tout effacer
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
