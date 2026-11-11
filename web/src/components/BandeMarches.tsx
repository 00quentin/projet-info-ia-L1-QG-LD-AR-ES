"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { RotateCw, TriangleAlert } from "lucide-react";
import { notifier } from "@/components/ui/Notifications";
import { lireMarches, type CoursMarche, type Marches } from "@/lib/api";
import { dateFr, pourcent, prix } from "@/lib/format";

const ACTIFS_AFFICHES: Record<string, string> = {
  "S&P 500": "S&P 500",
  "CAC 40": "CAC 40",
  VIX: "VIX",
  Or: "Or",
  Petrole: "Pétrole WTI",
  Bitcoin: "Bitcoin",
  EUR_USD: "EUR/USD",
};

function Tendance({ points, hausse }: { points: number[]; hausse: boolean }) {
  if (points.length < 2) return null;
  const min = Math.min(...points);
  const etendue = Math.max(...points) - min || 1;
  const trace = points
    .map((p, i) => `${(i / (points.length - 1)) * 44 + 2},${18 - ((p - min) / etendue) * 14}`)
    .join(" ");
  return (
    <svg width={48} height={22} aria-hidden className="shrink-0">
      <polyline points={trace} fill="none" stroke={hausse ? "var(--gain)" : "var(--loss)"} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

function Cours({ c, nom }: { c: CoursMarche; nom: string }) {
  const hausse = c.variation_pct >= 0;
  return (
    <li className="flex shrink-0 items-center gap-2.5 px-4">
      <span className="text-xs text-muted">{nom}</span>
      <span className="text-sm font-semibold tabular-nums">{prix(c.prix)}</span>
      <Tendance points={c.sparkline} hausse={hausse} />
      <span className={`text-xs font-medium tabular-nums ${hausse ? "text-gain" : "text-loss"}`}>
        <span aria-hidden>{hausse ? "▲" : "▼"}</span>
        <span className="sr-only">{hausse ? "en hausse de" : "en baisse de"}</span> {pourcent(Math.abs(c.variation_pct), 2)}
      </span>
    </li>
  );
}

export function BandeMarches() {
  const [marches, setMarches] = useState<Marches | null>(null);
  const [echec, setEchec] = useState(false);
  const [recharge, setRecharge] = useState(false);

  useEffect(() => {
    let actif = true;
    lireMarches()
      .then((m) => actif && setMarches(m))
      .catch(() => actif && setEchec(true));
    return () => {
      actif = false;
    };
  }, []);

  async function rafraichir() {
    setRecharge(true);
    try {
      const m = await lireMarches(true);
      setMarches(m);
      notifier(m.recharge ? "Prix rechargés depuis Yahoo Finance." : "Prix déjà à jour (rechargement possible toutes les 5 minutes).", "info");
    } catch {
      notifier("Impossible de recharger les prix pour le moment.", "erreur");
    } finally {
      setRecharge(false);
    }
  }

  if (echec) return null;

  const cours = marches ? Object.keys(ACTIFS_AFFICHES).flatMap((cle) => marches.actifs.filter((a) => a.cle === cle)) : [];

  return (
    <section aria-label="Cours des marchés" className="border-b border-line bg-surface">
      <div className="mx-auto flex h-11 max-w-[1400px] items-center gap-4 px-4 sm:px-6">
        {marches ? (
          <>
            {marches.en_direct ? (
              <span className="hidden shrink-0 text-xs text-muted sm:block" title="Source : Yahoo Finance">
                Clôture du {marches.date ? dateFr(marches.date) : "—"}
              </span>
            ) : (
              <span
                className="flex shrink-0 items-center gap-1.5 rounded-md bg-warn-soft px-2 py-1 text-xs font-medium text-warn"
                title="Yahoo Finance est injoignable : dernières valeurs connues."
              >
                <TriangleAlert className="size-3.5" aria-hidden />
                Données de secours{marches.date ? ` du ${dateFr(marches.date)}` : ""}
              </span>
            )}
            {/* Bandeau qui defile en continu (s'arrete au survol ou au focus) */}
            <div className="defilement relative min-w-0 flex-1 overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_3%,#000_97%,transparent)]">
              <div className="defilement-piste flex w-max">
                {[0, 1].map((copie) => (
                  <ul key={copie} aria-hidden={copie === 1 || undefined} className="flex shrink-0 items-center divide-x divide-line pr-4">
                    {cours.map((c) => (
                      <Cours key={c.cle} c={c} nom={ACTIFS_AFFICHES[c.cle]} />
                    ))}
                  </ul>
                ))}
              </div>
            </div>
            <motion.button
              type="button"
              onClick={rafraichir}
              disabled={recharge}
              whileTap={{ scale: 0.9 }}
              aria-label="Recharger les prix depuis Yahoo Finance"
              title="Recharger les prix"
              className="grid size-7 shrink-0 place-items-center rounded-md text-muted transition-colors hover:bg-surface-2 hover:text-ink disabled:opacity-60"
            >
              <motion.span animate={recharge ? { rotate: 360 } : { rotate: 0 }} transition={recharge ? { repeat: Infinity, duration: 0.8, ease: "linear" } : { duration: 0 }} className="grid">
                <RotateCw className="size-3.5" aria-hidden />
              </motion.span>
            </motion.button>
          </>
        ) : (
          <div className="h-4 w-full max-w-xl animate-pulse rounded bg-surface-2" aria-label="Chargement des cours" />
        )}
      </div>
    </section>
  );
}
