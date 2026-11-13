"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Check, Copy } from "lucide-react";
import { DUREE } from "@/components/motion/transitions";

const DELAI_CONFIRMATION_MS = 2000;

/** Bouton qui copie un texte (ex. l'adresse e-mail) et confirme brièvement. */
export function CopierTexte({ texte, libelle, confirmation = "Copié" }: { texte: string; libelle: string; confirmation?: string }) {
  const [copie, setCopie] = useState(false);

  useEffect(() => {
    if (!copie) return;
    const minuterie = setTimeout(() => setCopie(false), DELAI_CONFIRMATION_MS);
    return () => clearTimeout(minuterie);
  }, [copie]);

  async function copier() {
    try {
      await navigator.clipboard.writeText(texte);
      setCopie(true);
    } catch {
      /* presse-papiers refusé (contexte non sécurisé) : le texte reste sélectionnable à la main */
    }
  }

  return (
    <motion.button
      type="button"
      onClick={copier}
      whileTap={{ scale: 0.96 }}
      className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface px-3 py-1.5 text-sm font-medium text-ink-2 transition-colors hover:border-line-strong hover:text-ink"
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={copie ? "ok" : "copier"}
          initial={{ opacity: 0, scale: 0.6 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.6 }}
          transition={{ duration: DUREE.rapide }}
          className="grid"
          aria-hidden
        >
          {copie ? <Check className="size-4 text-gain" /> : <Copy className="size-4" />}
        </motion.span>
      </AnimatePresence>
      <span aria-live="polite">{copie ? confirmation : libelle}</span>
    </motion.button>
  );
}
