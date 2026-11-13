"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { motion } from "motion/react";
import { RotateCw, TriangleAlert } from "lucide-react";
import { notifier } from "@/components/ui/Notifications";
import { Infobulle } from "@/components/ui/Infobulle";
import { Prix, uniteCours } from "@/components/ui/Prix";
import { EVENEMENT_SERVEUR_PRET } from "@/components/ui/ReveilServeur";
import { lireMarches, lireMarchesPartages, type CoursMarche, type Marches } from "@/lib/api";
import { dateFr, pourcentSigne } from "@/lib/format";

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
  const trace = points.map((p, i) => `${(i / (points.length - 1)) * 34 + 1},${13 - ((p - min) / etendue) * 11}`).join(" ");
  return (
    <svg width={36} height={14} aria-hidden className="shrink-0">
      <polyline points={trace} fill="none" stroke={hausse ? "var(--gain)" : "var(--loss)"} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

function Cours({ c, nom }: { c: CoursMarche; nom: string }) {
  const hausse = c.variation_pct >= 0;
  return (
    <li className="flex shrink-0 items-center gap-2.5 px-3">
      <span className="flex flex-col leading-tight">
        <span className="text-xs text-muted">{nom}</span>
        <Prix valeur={c.prix} unite={uniteCours(c.cle, c.devise)} className="text-sm font-semibold" />
      </span>
      <span className="flex flex-col items-end gap-0.5 leading-tight">
        <span className={`text-xs font-medium tabular-nums ${hausse ? "text-gain" : "text-loss"}`}>
          <span className="sr-only">{hausse ? "en hausse de" : "en baisse de"} </span>
          {pourcentSigne(c.variation_pct, 2)}
        </span>
        <Tendance points={c.sparkline} hausse={hausse} />
      </span>
    </li>
  );
}

export function BandeMarches() {
  const [marches, setMarches] = useState<Marches | null>(null);
  const [echec, setEchec] = useState(false);
  const [essai, setEssai] = useState(0);
  const [recharge, setRecharge] = useState(false);
  const [deborde, setDeborde] = useState(false);
  const conteneur = useRef<HTMLDivElement>(null);
  const liste = useRef<HTMLUListElement>(null);

  useEffect(() => {
    let actif = true;
    lireMarchesPartages()
      .then((m) => {
        if (!actif) return;
        setMarches(m);
        setEchec(false);
      })
      .catch(() => actif && setEchec(true));
    return () => {
      actif = false;
    };
  }, [essai]);

  // Serveur endormi au premier chargement : on retente des qu'il se reveille.
  useEffect(() => {
    const relancer = () => setEssai((n) => n + 1);
    window.addEventListener(EVENEMENT_SERVEUR_PRET, relancer);
    return () => window.removeEventListener(EVENEMENT_SERVEUR_PRET, relancer);
  }, []);

  // Affichage fixe si tout tient, defilement seulement si la liste deborde reellement.
  useLayoutEffect(() => {
    const c = conteneur.current;
    const l = liste.current;
    if (!c || !l) return;
    const mesurer = () => setDeborde(l.scrollWidth > c.clientWidth + 1);
    const observateur = new ResizeObserver(mesurer);
    observateur.observe(c);
    observateur.observe(l);
    return () => observateur.disconnect();
  }, [marches]);

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
  const dateCourte = marches?.date ? dateFr(marches.date).slice(0, 5) : "—";

  return (
    <section aria-label="Cours des marchés" className="border-b border-line bg-surface">
      <div className="mx-auto flex h-12 max-w-[1400px] items-center gap-3 px-4 sm:px-6">
        {marches ? (
          <>
            {marches.en_direct ? (
              <Infobulle texte={`Cours de clôture du ${marches.date ? dateFr(marches.date) : "—"} · source Yahoo Finance`}>
                <span tabIndex={0} className="shrink-0 rounded-full bg-surface-2 px-2 py-1 text-xs font-medium tabular-nums text-ink-2">
                  {dateCourte}
                </span>
              </Infobulle>
            ) : (
              <Infobulle texte="Yahoo Finance est injoignable : dernières valeurs connues.">
                <span tabIndex={0} className="flex shrink-0 items-center gap-1.5 rounded-full bg-warn-soft px-2 py-1 text-xs font-medium text-warn">
                  <TriangleAlert className="size-3.5" aria-hidden />
                  <span className="hidden sm:inline">Données de secours</span>
                  {marches.date ? <span className="tabular-nums">{dateCourte}</span> : null}
                </span>
              </Infobulle>
            )}
            <div
              ref={conteneur}
              className={`relative min-w-0 flex-1 overflow-hidden ${deborde ? "defilement [mask-image:linear-gradient(90deg,transparent,var(--ink)_3%,var(--ink)_97%,transparent)]" : ""}`}
            >
              <div className={`flex w-max ${deborde ? "defilement-piste" : ""}`}>
                <ul ref={liste} className="flex shrink-0 items-center divide-x divide-line">
                  {cours.map((c) => (
                    <Cours key={c.cle} c={c} nom={ACTIFS_AFFICHES[c.cle]} />
                  ))}
                </ul>
                {/* Seconde copie pour boucler le defilement sans a-coup */}
                {deborde && (
                  <ul aria-hidden className="flex shrink-0 items-center divide-x divide-line">
                    {cours.map((c) => (
                      <Cours key={c.cle} c={c} nom={ACTIFS_AFFICHES[c.cle]} />
                    ))}
                  </ul>
                )}
              </div>
            </div>
            <Infobulle texte="Recharger les prix">
              <motion.button
                type="button"
                onClick={rafraichir}
                disabled={recharge}
                whileTap={{ scale: 0.95 }}
                aria-label="Recharger les prix depuis Yahoo Finance"
                className="grid size-8 shrink-0 place-items-center rounded-controle text-muted transition-colors hover:bg-surface-2 hover:text-ink disabled:opacity-60"
              >
                <RotateCw className={`size-3.5 ${recharge ? "animate-spin" : ""}`} aria-hidden />
              </motion.button>
            </Infobulle>
          </>
        ) : (
          <div className="chargement h-4 w-full max-w-xl rounded-full" aria-label="Chargement des cours" />
        )}
      </div>
    </section>
  );
}
