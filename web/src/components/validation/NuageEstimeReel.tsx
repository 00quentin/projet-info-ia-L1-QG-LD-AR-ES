"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { CriseValidee } from "@/lib/validation";
import { pourcentSigne } from "@/lib/format";
import { COULEUR_IA } from "./BarresAppariees";
import { nomCourtEvenement } from "./outils";

type Point = { id: string; crise: string; categorie?: string; actif: string; estime: number; reel: number; sens: boolean | null };

const MARGE = { haut: 12, droite: 14, bas: 40, gauche: 46 };
const COTE_MAX = 460;
// Bornes des axes : au-dela (VIX), le point est pose sur le bord, creux.
const BORNE_MAX_PCT = 100;
// Au-dela de ce nombre de points, ils sont plus petits et translucides (superposition).
const SEUIL_DENSE = 400;
const DISTANCE_SURVOL = 14;

/**
 * Nuage estime / reel : chaque point est un actif dans un evenement (des centaines de points
 * supportes : cercles simples, survol au point le plus proche). Sur la diagonale, l'IA tombe
 * pile ; dans les zones teintees, elle a vu le bon sens de variation. `categorie` met en
 * avant une categorie et estompe les autres.
 */
export function NuageEstimeReel({ crises, categorie = null }: { crises: CriseValidee[]; categorie?: string | null }) {
  const conteneur = useRef<HTMLDivElement>(null);
  const [largeur, setLargeur] = useState(520);
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
        c.actifs.map((a) => ({
          id: `${c.nom}-${a.cle}`,
          crise: c.nom,
          categorie: c.categorie,
          actif: a.nom_court,
          estime: a.estime_pct,
          reel: a.reel_pct,
          sens: a.sens_correct,
        })),
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
  const estompe = (p: Point) => categorie !== null && p.categorie !== categorie;
  const dense = points.length > SEUIL_DENSE;
  const rayon = dense ? 3 : 4.5;
  // Les points estompes d'abord : ceux de la categorie choisie restent visibles par-dessus.
  const ordonnes = useMemo(
    () => (categorie === null ? points : [...points.filter((p) => p.categorie !== categorie), ...points.filter((p) => p.categorie === categorie)]),
    [points, categorie],
  );

  function survoler(e: React.PointerEvent<SVGSVGElement>) {
    const boite = e.currentTarget.getBoundingClientRect();
    const px = e.clientX - boite.left;
    const py = e.clientY - boite.top;
    let meilleur: Point | null = null;
    let distance = DISTANCE_SURVOL;
    for (const p of points) {
      if (estompe(p)) continue;
      const d = Math.hypot(x(p.reel) - px, y(p.estime) - py);
      if (d <= distance) {
        distance = d;
        meilleur = p;
      }
    }
    setSurvol(meilleur);
  }

  const visibles = points.filter((p) => !estompe(p)).length;

  return (
    <div>
      <div ref={conteneur} className="relative w-full">
        <svg
          width={largeurSvg}
          height={hauteurSvg}
          viewBox={`0 0 ${largeurSvg} ${hauteurSvg}`}
          className="mx-auto block max-w-full touch-pan-y overflow-visible"
          role="img"
          aria-label={`Nuage de ${points.length} points${categorie ? ` dont ${visibles} mis en avant` : ""} : estimation de l'IA en ordonnée, vrai mouvement en abscisse. Le détail chiffré de chaque point figure dans la liste des événements, plus bas.`}
          onPointerDown={survoler}
          onPointerMove={survoler}
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

          {ordonnes.map((p) => {
            const creux = horsCadre(p);
            return (
              <circle
                key={p.id}
                cx={x(p.reel)}
                cy={y(p.estime)}
                r={survol?.id === p.id ? rayon + 2.5 : rayon}
                fill={creux ? "var(--surface)" : COULEUR_IA}
                stroke={creux ? COULEUR_IA : "var(--surface)"}
                strokeWidth={creux ? 1.5 : 0.75}
                opacity={estompe(p) ? 0.1 : dense ? 0.65 : 0.92}
              />
            );
          })}
        </svg>

        {survol && (
          <div
            className="pointer-events-none absolute z-10 w-max max-w-[15rem] rounded-xl border border-line bg-surface px-3 py-2 text-xs shadow-card"
            style={{
              left: Math.min(Math.max(x(survol.reel) + (largeur - largeurSvg) / 2 + 12, 0), Math.max(largeur - 200, 0)),
              top: Math.max(y(survol.estime) - 70, 0),
            }}
          >
            <p className="font-semibold text-ink">
              {survol.actif} · {nomCourtEvenement(survol.crise)}
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
        Axes de −{borne} % à +{borne} % : un point creux sort du cadre (souvent le VIX) et est posé sur le bord. Survolez ou touchez un point pour le détail.
      </p>
    </div>
  );
}
