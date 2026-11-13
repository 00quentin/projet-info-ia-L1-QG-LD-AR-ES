"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { History, Play } from "lucide-react";
import { Carte } from "@/components/ui/Carte";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import type { Filtre } from "./outils";

/** Squelette affiche le temps que le navigateur lise l'historique (evite un faux "historique vide"). */
export function ChargementHistorique() {
  return (
    <div aria-busy="true" className="flex flex-col gap-5">
      <span role="status" className="sr-only">
        Chargement de l&apos;historique…
      </span>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3" aria-hidden>
        <div className="chargement col-span-2 h-[6.5rem] rounded-controle sm:col-span-1" />
        <div className="chargement h-[6.5rem] rounded-controle" />
        <div className="chargement h-[6.5rem] rounded-controle" />
      </div>
      <div className="chargement h-9 w-72 max-w-full rounded-controle" aria-hidden />
      <div className="flex flex-col gap-2.5" aria-hidden>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="chargement h-[4.75rem] rounded-carte" />
        ))}
      </div>
    </div>
  );
}

// Pile de fiches, clin d'oeil a l'illustration de l'ancienne app.
function Illustration() {
  const fiches = [
    { rotation: -6, y: 6, opacite: 0.55 },
    { rotation: -2, y: 3, opacite: 0.8 },
    { rotation: 3, y: 0, opacite: 1 },
  ];
  return (
    <svg viewBox="0 0 160 100" className="mx-auto h-24 w-auto" aria-hidden>
      {fiches.map((f, i) => (
        <motion.g
          key={i}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: f.opacite, y: f.y }}
          transition={{ duration: DUREE.lente, ease: EASE_SORTIE, delay: 0.08 * i }}
        >
          <rect x="35" y="18" width="90" height="62" rx="8" fill="var(--surface)" stroke="var(--line-strong)" transform={`rotate(${f.rotation} 80 49)`} />
        </motion.g>
      ))}
      <g transform="rotate(3 80 49)">
        <rect x="45" y="28" width="26" height="4" rx="2" fill="var(--line-strong)" />
        <rect x="45" y="37" width="40" height="3" rx="1.5" fill="var(--line)" />
        <rect x="45" y="44" width="32" height="3" rx="1.5" fill="var(--line)" />
        <motion.polyline
          points="58,68 72,58 84,62 98,50 112,44"
          fill="none"
          stroke="var(--accent)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: DUREE.lente, ease: EASE_SORTIE, delay: 0.3 }}
        />
        <motion.circle cx="112" cy="44" r="3" fill="var(--accent)" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ ...RESSORT, delay: 0.75 }} />
      </g>
    </svg>
  );
}

const lienPrincipal = "inline-flex h-10 items-center justify-center gap-2 rounded-controle bg-accent px-4 text-sm font-semibold text-white transition hover:brightness-110";
const lienSecondaire = "inline-flex h-10 items-center justify-center gap-2 rounded-controle border border-line bg-surface px-4 text-sm font-medium transition-colors hover:border-line-strong hover:bg-surface-2";

export function HistoriqueVide({ tailleMax }: { tailleMax: number }) {
  return (
    <Carte className="px-6 py-12 text-center sm:py-14">
      <Illustration />
      <h2 className="mt-6 text-xl font-semibold tracking-tight">Aucune simulation dans l&apos;historique</h2>
      <p className="mx-auto mt-2 max-w-md text-titre leading-relaxed text-ink-2">
        Vos {tailleMax} dernières simulations et backtests apparaîtront ici automatiquement. Lancez votre première analyse pour commencer.
      </p>
      <div className="mt-6 flex flex-col justify-center gap-2 sm:flex-row">
        <motion.span whileTap={{ scale: 0.97 }} transition={RESSORT} className="flex">
          <Link href="/" className={`${lienPrincipal} flex-1`}>
            <Play className="size-4" aria-hidden />
            Lancer une simulation
          </Link>
        </motion.span>
        <motion.span whileTap={{ scale: 0.97 }} transition={RESSORT} className="flex">
          <Link href="/backtest" className={`${lienSecondaire} flex-1`}>
            <History className="size-4 text-accent" aria-hidden />
            Rejouer une crise passée
          </Link>
        </motion.span>
      </div>
    </Carte>
  );
}

/** Le filtre ne retient aucune entree. */
export function FiltreVide({ filtre }: { filtre: Exclude<Filtre, "tout"> }) {
  const backtest = filtre === "Backtest";
  return (
    <div className="rounded-carte border border-dashed border-line-strong px-6 py-10 text-center">
      <p className="text-sm font-medium">{backtest ? "Aucun backtest dans l'historique." : "Aucune simulation dans l'historique."}</p>
      <p className="mt-1 text-sm text-ink-2">{backtest ? "Rejouez votre portefeuille sur une vraie crise passée." : "Testez un événement économique sur votre portefeuille."}</p>
      <Link href={backtest ? "/backtest" : "/"} className={`${lienSecondaire} mt-4`}>
        {backtest ? <History className="size-4 text-accent" aria-hidden /> : <Play className="size-4 text-accent" aria-hidden />}
        {backtest ? "Faire un backtest" : "Lancer une simulation"}
      </Link>
    </div>
  );
}
