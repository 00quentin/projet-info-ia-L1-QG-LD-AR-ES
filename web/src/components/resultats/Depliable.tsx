"use client";

import { useId, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronDown } from "lucide-react";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

/** Bloc replie par defaut : un bouton-lien discret, le contenu se deplie en hauteur. */
export function Depliable({ libelle, libelleOuvert, children, className = "" }: { libelle: string; libelleOuvert?: string; children: ReactNode; className?: string }) {
  const [ouvert, setOuvert] = useState(false);
  const id = useId();
  return (
    <div className={className}>
      <button
        type="button"
        aria-expanded={ouvert}
        aria-controls={id}
        onClick={() => setOuvert((o) => !o)}
        className="inline-flex items-center gap-1 rounded-controle text-aide font-medium text-accent-ink transition-colors hover:text-ink"
      >
        {ouvert && libelleOuvert ? libelleOuvert : libelle}
        <ChevronDown className={`size-3.5 transition-transform duration-150 ${ouvert ? "rotate-180" : ""}`} aria-hidden />
      </button>
      <AnimatePresence initial={false}>
        {ouvert && (
          <motion.div
            id={id}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
            className="overflow-hidden"
          >
            <div className="pt-3">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
