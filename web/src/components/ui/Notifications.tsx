"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { CircleAlert, CircleCheck, Info, X } from "lucide-react";
import { RESSORT } from "@/components/motion/transitions";

type Ton = "succes" | "info" | "erreur";
type Notification = { id: number; message: string; ton: Ton };

const EVENEMENT = "qt-notification";
const DUREE_AFFICHAGE_MS = 4500;
let compteur = 0;

/** Affiche une notification ephemere en bas de l'ecran (utilisable partout). */
export function notifier(message: string, ton: Ton = "succes") {
  window.dispatchEvent(new CustomEvent<Notification>(EVENEMENT, { detail: { id: ++compteur, message, ton } }));
}

const ICONES = { succes: CircleCheck, info: Info, erreur: CircleAlert };
const COULEURS = { succes: "text-gain", info: "text-accent-ink", erreur: "text-loss" };

export function ZoneNotifications() {
  const [liste, setListe] = useState<Notification[]>([]);

  useEffect(() => {
    const recevoir = (e: Event) => {
      const n = (e as CustomEvent<Notification>).detail;
      setListe((l) => [...l.slice(-2), n]);
      setTimeout(() => setListe((l) => l.filter((x) => x.id !== n.id)), DUREE_AFFICHAGE_MS);
    };
    window.addEventListener(EVENEMENT, recevoir);
    return () => window.removeEventListener(EVENEMENT, recevoir);
  }, []);

  return (
    <div aria-live="polite" className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex flex-col items-center gap-2 px-4">
      <AnimatePresence>
        {liste.map((n) => {
          const Icone = ICONES[n.ton];
          return (
            <motion.div
              key={n.id}
              layout
              initial={{ opacity: 0, y: 24, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 12, scale: 0.97 }}
              transition={RESSORT}
              role={n.ton === "erreur" ? "alert" : "status"}
              className="pointer-events-auto flex max-w-md items-center gap-3 rounded-xl border border-line bg-surface/95 px-4 py-3 text-sm shadow-[0_10px_30px_-10px_rgba(0,0,0,0.25)] backdrop-blur"
            >
              <Icone className={`size-4 shrink-0 ${COULEURS[n.ton]}`} aria-hidden />
              <span>{n.message}</span>
              <button type="button" onClick={() => setListe((l) => l.filter((x) => x.id !== n.id))} aria-label="Fermer la notification" className="ml-1 grid size-6 shrink-0 place-items-center rounded-md text-muted hover:bg-surface-2 hover:text-ink">
                <X className="size-3.5" aria-hidden />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
