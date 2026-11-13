"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { CircleAlert, History, RotateCw } from "lucide-react";
import { Carte } from "@/components/ui/Carte";
import { Cascade, LigneCascade } from "@/components/motion/Apparition";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

// Un krach puis une reprise : l'idee du backtest en une courbe.
const COURBE = "M6 22 C 18 20, 26 16, 34 19 S 46 50, 58 52 S 74 36, 86 30 S 104 18, 122 12";

function Illustration() {
  return (
    <div className="relative mx-auto h-24 w-48" aria-hidden>
      <svg viewBox="0 0 128 64" className="size-full overflow-visible">
        <line x1="4" x2="124" y1="22" y2="22" stroke="var(--line-strong)" strokeDasharray="3 3" />
        <motion.path
          d={COURBE}
          fill="none"
          stroke="var(--accent)"
          strokeWidth={2.5}
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2, ease: EASE_SORTIE, delay: 0.2 }}
        />
        <motion.circle
          cx="58"
          cy="52"
          r="3.5"
          fill="var(--loss)"
          stroke="var(--surface)"
          strokeWidth="1.5"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ ...RESSORT, delay: 0.75 }}
          style={{ transformBox: "fill-box", transformOrigin: "center" }}
        />
        <motion.circle
          cx="122"
          cy="12"
          r="4"
          fill="var(--accent)"
          stroke="var(--surface)"
          strokeWidth="1.5"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ ...RESSORT, delay: 1.25 }}
          style={{ transformBox: "fill-box", transformOrigin: "center" }}
        />
      </svg>
    </div>
  );
}

const ETAPES_GUIDE = ["Choisissez une crise passée (ou vos propres dates)", "Composez votre portefeuille", "Lancez le backtest : les vrais cours font le reste"];

export function EtatVide() {
  return (
    <Carte className="grid min-h-[26rem] place-items-center p-8 text-center">
      <div className="max-w-md">
        <motion.span
          className="mx-auto grid size-12 place-items-center rounded-carte bg-accent-soft text-accent-ink"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={RESSORT}
        >
          <History className="size-6" aria-hidden />
        </motion.span>
        <h2 className="mt-5 text-xl font-semibold tracking-tight">Rejouez l&apos;histoire avec les vrais cours</h2>
        <p className="mt-2 text-titre leading-relaxed text-ink-2">
          Krach de 2008, COVID-19, bulle internet… Mesurez ce qu&apos;aurait réellement donné votre portefeuille, jour après jour, avec les cours de Yahoo Finance convertis en euros.
        </p>
        <div className="mt-6">
          <Illustration />
        </div>
        <Cascade className="mt-6">
          <ol className="flex flex-col gap-2 text-left text-sm">
            {ETAPES_GUIDE.map((etape, i) => (
              <LigneCascade key={etape} className="flex items-center gap-3 rounded-tuile border border-line px-3.5 py-2.5">
                <span className="grid size-6 shrink-0 place-items-center rounded-full bg-surface-2 text-xs font-semibold text-ink-2 tabular-nums">{i + 1}</span>
                <span className="text-ink-2">{etape}</span>
              </LigneCascade>
            ))}
          </ol>
        </Cascade>
      </div>
    </Carte>
  );
}

const ETAPES_ATTENTE = ["Téléchargement des cours historiques…", "Alignement des séances de bourse…", "Conversion en euros (taux BCE)…", "Calcul du risque du portefeuille…"];

export function Chargement({ libelle, convertirEur }: { libelle: string; convertirEur: boolean }) {
  const etapes = convertirEur ? ETAPES_ATTENTE : ETAPES_ATTENTE.filter((e) => !e.startsWith("Conversion"));
  const [etape, setEtape] = useState(0);
  useEffect(() => {
    const minuterie = setInterval(() => setEtape((e) => Math.min(e + 1, etapes.length - 1)), 1100);
    return () => clearInterval(minuterie);
  }, [etapes.length]);

  return (
    <div className="flex flex-col gap-4" role="status" aria-live="polite" aria-label="Backtest en cours">
      <Carte className="p-6 sm:p-7">
        <div className="flex items-center gap-3">
          <span className="relative flex size-3">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-accent opacity-60" />
            <span className="relative inline-flex size-3 rounded-full bg-accent" />
          </span>
          <AnimatePresence mode="wait" initial={false}>
            <motion.span
              key={etape}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: DUREE.rapide }}
              className="text-titre font-medium"
            >
              {etapes[etape]}
            </motion.span>
          </AnimatePresence>
        </div>
        <p className="mt-2 text-sm text-muted">Backtest : {libelle}. Quelques secondes suffisent en général.</p>
        <div className="chargement mt-6 h-14 w-64 max-w-full rounded-tuile" />
        <div className="chargement mt-3 h-4 w-80 max-w-full rounded-md" />
      </Carte>
      <div className="chargement h-80 rounded-carte border border-line" />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="chargement h-28 rounded-tuile border border-line" />
        ))}
      </div>
    </div>
  );
}

export function Erreur({ titre = "Le backtest n'a pas abouti", message, onReessayer }: { titre?: string; message: string; onReessayer?: () => void }) {
  return (
    <Carte className="p-7">
      <div className="flex gap-3" role="alert">
        <CircleAlert className="mt-0.5 size-5 shrink-0 text-loss" aria-hidden />
        <div>
          <h2 className="text-titre font-semibold">{titre}</h2>
          <p className="mt-1 text-sm leading-relaxed text-ink-2">{message}</p>
          {onReessayer && (
            <motion.button
              type="button"
              onClick={onReessayer}
              whileTap={{ scale: 0.97 }}
              transition={RESSORT}
              className="mt-4 inline-flex items-center gap-2 rounded-controle border border-line px-3 py-2 text-sm font-medium transition-colors hover:border-line-strong"
            >
              <RotateCw className="size-4" aria-hidden />
              Réessayer
            </motion.button>
          )}
        </div>
      </div>
    </Carte>
  );
}
