"use client";

import { cloneElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState, useSyncExternalStore, type ReactElement, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "motion/react";
import { Info } from "lucide-react";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

const DELAI_SURVOL_MS = 300;
const MARGE_ECRAN_PX = 8;
const ECART_PX = 6;
/** En dessous de cette distance au haut de l'ecran, la bulle s'ouvre sous l'element. */
const PLACE_MIN_AU_DESSUS_PX = 56;

type Ancre = { x: number; haut: number; bas: number };

const abonnementVide = () => () => {};
/** Vrai seulement apres l'hydratation : un portail vers <body> n'existe pas cote serveur. */
export const useEstClient = () =>
  useSyncExternalStore(
    abonnementVide,
    () => true,
    () => false,
  );

/**
 * Infobulle maison, a la place des `title=` du navigateur : s'ouvre au survol de la souris
 * (apres un court delai) ou au focus clavier, se ferme avec Echap. Le texte reste lu par les
 * lecteurs d'ecran via aria-describedby, meme bulle fermee.
 */
export function Infobulle({
  texte,
  children,
  ouvrirAuClic = false,
  className = "inline-flex",
}: {
  texte: ReactNode;
  /** Un seul element focalisable (bouton, lien) ou un element rendu focalisable. */
  children: ReactElement<{ "aria-describedby"?: string }>;
  /** Le clic (ou l'appui sur mobile) ouvre aussi la bulle : pour les boutons (i). */
  ouvrirAuClic?: boolean;
  /** Affichage de l'enveloppe (par defaut inline-flex ; "flex" pour remplir une grille). */
  className?: string;
}) {
  const id = useId();
  const zone = useRef<HTMLSpanElement>(null);
  const bulle = useRef<HTMLDivElement>(null);
  const minuterie = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [ancre, setAncre] = useState<Ancre | null>(null);
  const estClient = useEstClient();

  const ouvrir = useCallback(() => {
    const r = zone.current?.getBoundingClientRect();
    if (r) setAncre({ x: r.left + r.width / 2, haut: r.top, bas: r.bottom });
  }, []);
  const fermer = useCallback(() => {
    clearTimeout(minuterie.current);
    setAncre(null);
  }, []);

  // Une bulle en position fixe ne suit pas la page : on la ferme au defilement.
  useEffect(() => {
    if (!ancre) return;
    const surTouche = (e: KeyboardEvent) => e.key === "Escape" && fermer();
    window.addEventListener("scroll", fermer, true);
    window.addEventListener("keydown", surTouche);
    return () => {
      window.removeEventListener("scroll", fermer, true);
      window.removeEventListener("keydown", surTouche);
    };
  }, [ancre, fermer]);

  useEffect(() => () => clearTimeout(minuterie.current), []);

  // Recentrage horizontal une fois la largeur de la bulle connue, sans deborder de l'ecran.
  useLayoutEffect(() => {
    const el = bulle.current;
    if (!ancre || !el) return;
    const largeur = el.offsetWidth;
    const gauche = Math.min(Math.max(ancre.x - largeur / 2, MARGE_ECRAN_PX), window.innerWidth - largeur - MARGE_ECRAN_PX);
    el.style.left = `${gauche}px`;
  }, [ancre]);

  const dessous = ancre ? ancre.haut < PLACE_MIN_AU_DESSUS_PX : false;

  return (
    <span
      ref={zone}
      className={className}
      onPointerEnter={(e) => {
        if (e.pointerType !== "mouse") return;
        clearTimeout(minuterie.current);
        minuterie.current = setTimeout(ouvrir, DELAI_SURVOL_MS);
      }}
      onPointerLeave={(e) => e.pointerType === "mouse" && fermer()}
      onFocus={(e) => (e.target as HTMLElement).matches?.(":focus-visible") && ouvrir()}
      onBlur={fermer}
      onClick={ouvrirAuClic ? ouvrir : undefined}
    >
      {cloneElement(children, { "aria-describedby": id })}
      <span id={id} className="sr-only">
        {texte}
      </span>
      {estClient &&
        createPortal(
          <AnimatePresence>
            {ancre && (
              <motion.div
                ref={bulle}
                aria-hidden
                initial={{ opacity: 0, y: dessous ? -2 : 2 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }}
                style={{ top: dessous ? ancre.bas + ECART_PX : ancre.haut - ECART_PX, left: ancre.x }}
                className={`pointer-events-none fixed z-[60] max-w-72 rounded-controle bg-ink px-2.5 py-1.5 text-aide text-bg shadow-card ${dessous ? "" : "-translate-y-full"}`}
              >
                {texte}
              </motion.div>
            )}
          </AnimatePresence>,
          document.body,
        )}
    </span>
  );
}

/** Petit bouton (i) qui montre une explication : remplace les phrases d'aide affichees en permanence. */
export function AideInfo({ texte, libelle = "Plus d'informations" }: { texte: ReactNode; libelle?: string }) {
  return (
    <Infobulle texte={texte} ouvrirAuClic>
      <button type="button" aria-label={libelle} className="-m-1 grid size-6 shrink-0 place-items-center rounded-full text-muted transition-colors hover:text-ink">
        <Info className="size-3.5" aria-hidden />
      </button>
    </Infobulle>
  );
}
