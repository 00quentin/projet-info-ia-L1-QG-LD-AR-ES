"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "motion/react";
import type { CriseValidee } from "@/lib/validation";
import { pourcentSigne } from "@/lib/format";
import { EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { COULEUR_IA } from "./BarresAppariees";

type Point = { id: string; crise: string; actif: string; estime: number; reel: number; sens: boolean | null };

const MARGE = { haut: 12, droite: 14, bas: 40, gauche: 46 };
const COTE_MAX = 460;
// Bornes des axes : au-dela (VIX), le point est pose sur le bord, creux.
const BORNE_MAX_PCT = 100;
const RAYON = 4.5;
const RAYON_CIBLE = 12;

function nomCourtCrise(nom: string) {
  return nom.replace(/\s*\(.*\)$/, "");
}

/**
 * Nuage estime / reel : chaque point est un actif dans une crise. Sur la diagonale,
 * l'IA tombe pile ; dans les zones teintees, elle a vu le bon sens de variation.
 */
export function NuageEstimeReel({ crises }: { crises: CriseValidee[] }) {
  const conteneur = useRef<HTMLDivElement>(null);
  const [largeur, setLargeur] = useState(520);
  const [selection, setSelection] = useState<string | null>(null);
  const [survol, setSurvol] = useState<Point | null>(null);

  useEffect(() => {
    const el = conteneur.current;
    if (!el) return;
    const obs = new ResizeObserver(([e]) => setLargeur(Math.max(260, e.contentRect.width)));
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const points = useMemo<Point[]>(
    () =>
      crises.flatMap((c) =>
        c.actifs.map((a) => ({ id: `${c.nom}-${a.cle}`, crise: c.nom, actif: a.nom_court, estime: a.estime_pct, reel: a.reel_pct, sens: a.sens_correct })),
      ),
    [crises],
  );

  const borne = useMemo(() => {
    const max = Math.max(10, ...points.map((p) => Math.max(Math.abs(p.estime), Math.abs(p.reel))));
    return Math.min(BORNE_MAX_PCT, Math.ceil(max / 20) * 20);
  }, [points]);

  const cote = Math.min(COTE_MAX, largeur - MARGE.gauche - MARGE.droite);
  const largeurSvg = cote + MARGE.gauche + MARGE.droite;
  const hauteurSvg = cote + MARGE.haut + MARGE.bas;
  const x = (v: number) => MARGE.gauche + ((Math.max(-borne, Math.min(borne, v)) + borne) / (2 * borne)) * cote;
  const y = (v: number) => MARGE.haut + (1 - (Math.max(-borne, Math.min(borne, v)) + borne) / (2 * borne)) * cote;
  const graduations = [-borne, -borne / 2, 0, borne / 2, borne];
  const horsCadre = (p: Point) => Math.abs(p.estime) > borne || Math.abs(p.reel) > borne;

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-1.5" role="group" aria-label="Mettre une crise en avant">
        {[null, ...crises.map((c) => c.nom)].map((nom) => {
          const actif = selection === nom;
          return (
            <button
              key={nom ?? "toutes"}
              type="button"
              onClick={() => setSelection(nom)}
              aria-pressed={actif}
              className={`relative rounded-full px-3 py-1 text-xs font-medium transition-colors ${actif ? "text-ink" : "text-muted hover:text-ink"}`}
            >
              {actif && <motion.span layoutId="nuage-selection" className="absolute inset-0 rounded-full bg-surface-2 ring-1 ring-line-strong" transition={RESSORT} />}
              <span className="relative">{nom ? nomCourtCrise(nom) : "Toutes les crises"}</span>
            </button>
          );
        })}
      </div>

      <div ref={conteneur} className="relative w-full">
        <svg
          width={largeurSvg}
          height={hauteurSvg}
          viewBox={`0 0 ${largeurSvg} ${hauteurSvg}`}
          className="mx-auto block max-w-full overflow-visible"
          role="img"
          aria-label={`Nuage de ${points.length} points : estimation de l'IA en ordonnée, vrai mouvement en abscisse. Le détail chiffré de chaque point figure dans les cartes par crise.`}
          onPointerLeave={() => setSurvol(null)}
        >
          {/* Zones « bon sens » : hausse estimee et reelle, ou baisse estimee et reelle */}
          <rect x={x(0)} y={y(borne)} width={cote / 2} height={cote / 2} fill="var(--gain)" opacity={0.07} />
          <rect x={x(-borne)} y={y(0)} width={cote / 2} height={cote / 2} fill="var(--gain)" opacity={0.07} />
          {graduations.map((g) => (
            <g key={g}>
              <line x1={x(g)} x2={x(g)} y1={MARGE.haut} y2={MARGE.haut + cote} stroke={g === 0 ? "var(--line-strong)" : "var(--line)"} />
              <line x1={MARGE.gauche} x2={MARGE.gauche + cote} y1={y(g)} y2={y(g)} stroke={g === 0 ? "var(--line-strong)" : "var(--line)"} />
              <text x={x(g)} y={MARGE.haut + cote + 16} textAnchor="middle" className="fill-muted text-[10.5px] tabular-nums">
                {g > 0 ? "+" : g < 0 ? "−" : ""}
                {Math.abs(g)}
              </text>
              <text x={MARGE.gauche - 6} y={y(g) + 3.5} textAnchor="end" className="fill-muted text-[10.5px] tabular-nums">
                {g > 0 ? "+" : g < 0 ? "−" : ""}
                {Math.abs(g)}
              </text>
            </g>
          ))}
          <text x={MARGE.gauche + cote - 6} y={MARGE.haut + 14} textAnchor="end" className="fill-muted text-[11px]">
            Bon sens
          </text>
          <text x={MARGE.gauche + 6} y={MARGE.haut + cote - 8} className="fill-muted text-[11px]">
            Bon sens
          </text>
          <text x={MARGE.gauche + 6} y={MARGE.haut + 14} className="fill-muted text-[11px]">
            Sens inverse
          </text>
          <text x={MARGE.gauche + cote - 6} y={MARGE.haut + cote - 8} textAnchor="end" className="fill-muted text-[11px]">
            Sens inverse
          </text>
          <line x1={x(-borne)} y1={y(-borne)} x2={x(borne)} y2={y(borne)} stroke="var(--ink-2)" strokeOpacity={0.55} />
          <text
            x={x(borne * 0.5)}
            y={y(borne * 0.5) - 6}
            textAnchor="middle"
            transform={`rotate(-45 ${x(borne * 0.5)} ${y(borne * 0.5) - 6})`}
            className="fill-ink-2 text-[11px]"
          >
            estimation parfaite
          </text>
          <text x={MARGE.gauche + cote / 2} y={hauteurSvg - 4} textAnchor="middle" className="fill-ink-2 text-[11px]">
            Vrai mouvement (%)
          </text>
          <text
            x={12}
            y={MARGE.haut + cote / 2}
            textAnchor="middle"
            transform={`rotate(-90 12 ${MARGE.haut + cote / 2})`}
            className="fill-ink-2 text-[11px]"
          >
            Estimation de l’IA (%)
          </text>

          {points.map((p, i) => {
            const estompe = selection !== null && p.crise !== selection;
            const creux = horsCadre(p);
            return (
              <g key={p.id} opacity={estompe ? 0.15 : 1} style={{ transition: "opacity 0.25s" }}>
                <motion.circle
                  cx={x(p.reel)}
                  cy={y(p.estime)}
                  r={survol?.id === p.id ? RAYON + 1.5 : RAYON}
                  fill={creux ? "var(--surface)" : COULEUR_IA}
                  stroke={creux ? COULEUR_IA : "var(--surface)"}
                  strokeWidth={2}
                  initial={{ opacity: 0, scale: 0 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, ease: EASE_SORTIE, delay: Math.min(i * 0.008, 0.8) }}
                  style={{ transformBox: "fill-box", transformOrigin: "center" }}
                />
                {!estompe && (
                  <circle cx={x(p.reel)} cy={y(p.estime)} r={RAYON_CIBLE} fill="transparent" onPointerEnter={() => setSurvol(p)} />
                )}
              </g>
            );
          })}
        </svg>

        {survol && (
          <div
            className="pointer-events-none absolute z-10 w-max max-w-[15rem] rounded-xl border border-line bg-surface px-3 py-2 text-xs shadow-card"
            style={{
              left: Math.min(Math.max(x(survol.reel) + (largeur - largeurSvg) / 2 + 12, 0), largeur - 200),
              top: Math.max(y(survol.estime) - 70, 0),
            }}
          >
            <p className="font-semibold text-ink">
              {survol.actif} · {nomCourtCrise(survol.crise)}
            </p>
            <p className="mt-1 tabular-nums text-ink">
              IA <strong className="font-semibold">{pourcentSigne(survol.estime)}</strong> · réel <strong className="font-semibold">{pourcentSigne(survol.reel)}</strong>
            </p>
            <p className="text-muted">
              {survol.sens === null ? "Mouvement réel trop faible pour juger le sens" : survol.sens ? "Bon sens de variation" : "Sens inverse"}
            </p>
          </div>
        )}
      </div>
      <p className="mt-2 text-[11px] leading-relaxed text-muted">
        Axes de −{borne} % à +{borne} % : un point creux sort du cadre (souvent le VIX) et est posé sur le bord. Survolez un point pour le détail.
      </p>
    </div>
  );
}
