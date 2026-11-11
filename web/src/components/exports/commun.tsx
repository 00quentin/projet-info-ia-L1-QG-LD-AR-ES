"use client";

import { AnimatePresence, motion, type HTMLMotionProps } from "motion/react";
import { useCallback, useLayoutEffect, useRef, useState, type ComponentType, type ReactNode } from "react";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

/** Coche qui se dessine (retour de succes). */
export function CocheAnimee({ className = "size-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
      <motion.path d="M5 12.5l4.5 4.5L19 7.5" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: DUREE.normale, ease: EASE_SORTIE, delay: 0.05 }} />
    </svg>
  );
}

/** Etat vrai pendant `duree` ms apres chaque declenchement (ex. "Lien copie"). */
export function useFlash(duree: number): [boolean, () => void] {
  const [actif, setActif] = useState(false);
  const minuterie = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  // Page cachee (navigation) : on coupe le retour en cours pour ne pas le retrouver fige au retour.
  useLayoutEffect(
    () => () => {
      clearTimeout(minuterie.current);
      setActif(false);
    },
    [],
  );
  const declencher = useCallback(() => {
    clearTimeout(minuterie.current);
    setActif(true);
    minuterie.current = setTimeout(() => setActif(false), duree);
  }, [duree]);
  return [actif, declencher];
}

type PropsBouton = Omit<HTMLMotionProps<"button">, "children"> & {
  /** Change a chaque etat : le libelle precedent glisse vers le haut, le nouveau arrive par le bas. */
  cle: string;
  ton?: "neutre" | "succes";
  children: ReactNode;
};

export function BoutonExport({ cle, ton = "neutre", children, className = "", disabled, ...reste }: PropsBouton) {
  const tons = {
    neutre: "border-line bg-surface text-ink hover:border-line-strong hover:bg-surface-2",
    succes: "border-gain/40 bg-gain-soft text-gain",
  };
  return (
    <motion.button
      type="button"
      whileHover={disabled ? undefined : { y: -1 }}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      transition={RESSORT}
      disabled={disabled}
      className={`relative inline-flex h-10 w-full min-w-44 items-center justify-center overflow-hidden rounded-xl border px-4 text-sm font-medium transition-colors disabled:cursor-wait disabled:bg-surface-2 @md:w-auto ${tons[ton]} ${className}`}
      {...reste}
    >
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={cle}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }}
          className="inline-flex items-center gap-2 whitespace-nowrap"
        >
          {children}
        </motion.span>
      </AnimatePresence>
    </motion.button>
  );
}

type PropsLigne = {
  icone: ComponentType<{ className?: string; "aria-hidden"?: boolean }>;
  titre: string;
  description: ReactNode;
  meta?: ReactNode;
  action: ReactNode;
  /** Zone qui se deplie sous la ligne (progression, erreur, lien a copier). */
  children?: ReactNode;
};

/** Une ligne de la carte d'export : icone, texte, bouton ; empilee sur petit ecran. */
export function LigneExport({ icone: Icone, titre, description, meta, action, children }: PropsLigne) {
  return (
    <li className="py-4 first:pt-0 last:pb-0">
      <div className="flex flex-col gap-3 @md:flex-row @md:items-center @md:justify-between @md:gap-6">
        <div className="flex min-w-0 gap-3">
          <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent-ink">
            <Icone className="size-[18px]" aria-hidden />
          </span>
          <div className="min-w-0">
            <h4 className="text-sm font-semibold">{titre}</h4>
            <p className="mt-0.5 text-sm leading-relaxed text-ink-2">{description}</p>
            {meta && <p className="mt-1 text-xs text-muted">{meta}</p>}
          </div>
        </div>
        <div className="shrink-0">{action}</div>
      </div>
      {children}
    </li>
  );
}

/** Panneau qui se deplie en hauteur sous une ligne d'export. */
export function Depliant({ visible, children, id }: { visible: boolean; children: ReactNode; id?: string }) {
  return (
    <AnimatePresence initial={false}>
      {visible && (
        <motion.div
          id={id}
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
          className="overflow-hidden"
        >
          <div className="pt-3 @md:pl-12">{children}</div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/** Message lu par les lecteurs d'ecran sans etre affiche. */
export function Annonce({ message }: { message: string }) {
  return (
    <span role="status" aria-live="polite" className="sr-only">
      {message}
    </span>
  );
}
