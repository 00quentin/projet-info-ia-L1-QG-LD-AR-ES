"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import { motion } from "motion/react";
import { EASE_SORTIE } from "@/components/motion/transitions";
import { scaleLinear } from "d3-scale";
import { area, line } from "d3-shape";

export type SerieLigne = {
  nom: string;
  /** Variable CSS de couleur, ex. "var(--series-1)" */
  couleur: string;
  valeurs: (number | null)[];
  /** La serie principale est plus epaisse. Sans serie principale, toutes ont le meme poids. */
  principale?: boolean;
  /** Fourchette propre a cette serie (ex. 5 %–95 % Monte-Carlo d'un actif). */
  bande?: { bas: (number | null)[]; haut: (number | null)[] };
};

type Props = {
  series: SerieLigne[];
  /** Enveloppe (ex. 5 %–95 % Monte-Carlo) dessinee autour de la serie principale. */
  bande?: { bas: (number | null)[]; haut: (number | null)[]; nom: string };
  /** Libelle de chaque abscisse (date ou "Jour 12"). */
  etiquettesX: string[];
  formatY: (v: number) => string;
  formatValeur: (v: number) => string;
  /** Ligne de reference horizontale (ex. capital de depart). */
  reference?: { valeur: number; nom: string };
  hauteur?: number;
  description: string;
};

const MARGE = { haut: 16, droite: 16, bas: 28, gauche: 56 };
// Echantillon de libelles pour estimer leur largeur (sans mesurer le DOM).
const ticksCandidats = (etiquettes: string[]) => (etiquettes.length ? [etiquettes[0], etiquettes[Math.floor(etiquettes.length / 2)], etiquettes[etiquettes.length - 1]] : [""]);
const DUREE_TRACE = 1.2;

function graduations(min: number, max: number, nb: number): number[] {
  return scaleLinear().domain([min, max]).nice(nb).ticks(nb);
}

export function GraphiqueLignes({ series, bande, etiquettesX, formatY, formatValeur, reference, hauteur = 320, description }: Props) {
  const conteneur = useRef<HTMLDivElement>(null);
  const [largeur, setLargeur] = useState(720);
  const [survol, setSurvol] = useState<number | null>(null);
  const idDesc = useId();

  useEffect(() => {
    const el = conteneur.current;
    if (!el) return;
    const obs = new ResizeObserver(([entree]) => setLargeur(Math.max(280, entree.contentRect.width)));
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const n = etiquettesX.length;
  const { x, y, ticksY } = useMemo(() => {
    const toutes: number[] = [];
    for (const s of series) for (const v of s.valeurs) if (v != null) toutes.push(v);
    if (bande) for (const v of [...bande.bas, ...bande.haut]) if (v != null) toutes.push(v);
    for (const s of series) if (s.bande) for (const v of [...s.bande.bas, ...s.bande.haut]) if (v != null) toutes.push(v);
    if (reference) toutes.push(reference.valeur);
    const min = Math.min(...toutes);
    const max = Math.max(...toutes);
    const marge = (max - min || Math.abs(max) || 1) * 0.06;
    const echelleY = scaleLinear().domain([min - marge, max + marge]).nice(5).range([hauteur - MARGE.bas, MARGE.haut]);
    const echelleX = scaleLinear().domain([0, Math.max(1, n - 1)]).range([MARGE.gauche, largeur - MARGE.droite]);
    return { x: echelleX, y: echelleY, ticksY: graduations(echelleY.domain()[0], echelleY.domain()[1], 5) };
  }, [series, bande, reference, n, largeur, hauteur]);

  const tracer = line<number | null>().defined((v) => v != null).x((_, i) => x(i)).y((v) => y(v as number));
  const zone = (b: { bas: (number | null)[]; haut: (number | null)[] }) =>
    area<number>()
      .defined((i) => b.bas[i] != null && b.haut[i] != null)
      .x((i) => x(i))
      .y0((i) => y(b.bas[i] as number))
      .y1((i) => y(b.haut[i] as number))(Array.from({ length: n }, (_, i) => i)) ?? undefined;

  // Graduations "rondes" (0, 20, 40…) gardees de gauche a droite seulement si elles laissent
  // assez de place a leurs voisines ; la derniere abscisse est toujours etiquetee.
  // Largeur estimee des libelles (11 px, ~7 px par caractere) : prudent pour les dates longues.
  const largeurLibelle = Math.max(...ticksCandidats(etiquettesX).map((t) => t.length)) * 7 + 16;
  const placeX = largeur - MARGE.gauche - MARGE.droite;
  const nbTicksX = Math.max(2, Math.min(6, Math.floor(placeX / largeurLibelle)));
  const ticksX: number[] = [];
  for (const t of x.ticks(nbTicksX)) {
    if (!Number.isInteger(t) || t < 0 || t >= n - 1) continue;
    const precedent = ticksX.at(-1);
    // Le premier libelle est aligne a gauche et le dernier a droite, les autres sont centres :
    // a cote d'une extremite il faut 1,5 largeur d'ecart, entre deux libelles centres 1 largeur.
    if (precedent != null && x(t) - x(precedent) < largeurLibelle * (ticksX.length === 1 ? 1.5 : 1)) continue;
    if (x(n - 1) - x(t) < largeurLibelle * 1.5) continue;
    ticksX.push(t);
  }
  ticksX.push(n - 1);

  function surDeplacement(e: React.PointerEvent<SVGRectElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * largeur;
    setSurvol(Math.max(0, Math.min(n - 1, Math.round(x.invert(px)))));
  }
  function surClavier(e: React.KeyboardEvent<SVGSVGElement>) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    e.preventDefault();
    const pas = e.shiftKey ? 10 : 1;
    setSurvol((i) => Math.max(0, Math.min(n - 1, (i ?? n - 1) + (e.key === "ArrowRight" ? pas : -pas))));
  }

  const principale = series.find((s) => s.principale);
  const reference0 = principale ?? series[0];
  // Nouvelle cle a chaque nouveau jeu de donnees : les courbes se redessinent.
  const cleTrace = `${n}-${series.length}-${reference0.valeurs[0]}-${reference0.valeurs[n - 1]}`;
  const avecPointFinal = principale ? [principale] : series;
  const bulleAGauche = survol != null && x(survol) > largeur * 0.6;

  return (
    <div ref={conteneur} className="relative w-full">
      <svg
        width={largeur}
        height={hauteur}
        viewBox={`0 0 ${largeur} ${hauteur}`}
        role="img"
        aria-describedby={idDesc}
        tabIndex={0}
        onKeyDown={surClavier}
        onBlur={() => setSurvol(null)}
        className="block max-w-full select-none"
      >
        <desc id={idDesc}>{description}</desc>

        {ticksY.map((t) => (
          <g key={t}>
            <line x1={MARGE.gauche} x2={largeur - MARGE.droite} y1={y(t)} y2={y(t)} stroke="var(--line)" strokeWidth={1} />
            <text x={MARGE.gauche - 8} y={y(t)} dy="0.32em" textAnchor="end" fontSize={11} fill="var(--muted)" style={{ fontVariantNumeric: "tabular-nums" }}>
              {formatY(t)}
            </text>
          </g>
        ))}
        {ticksX.map((i, k) => (
          <text
            key={i}
            x={x(i)}
            y={hauteur - 8}
            textAnchor={k === 0 ? "start" : k === ticksX.length - 1 ? "end" : "middle"}
            fontSize={11}
            fill="var(--muted)"
          >
            {etiquettesX[i]}
          </text>
        ))}

        {reference && (
          <line x1={MARGE.gauche} x2={largeur - MARGE.droite} y1={y(reference.valeur)} y2={y(reference.valeur)} stroke="var(--muted)" strokeWidth={1} />
        )}

        <g key={cleTrace}>
          {/* Les zones se deploient depuis la gauche pendant que les courbes se dessinent. */}
          {bande && principale && (
            <motion.path
              d={zone(bande)}
              fill={principale.couleur}
              initial={{ opacity: 0, clipPath: "inset(0 100% 0 0)" }}
              animate={{ opacity: 0.12, clipPath: "inset(0 0% 0 0)" }}
              transition={{ duration: DUREE_TRACE, ease: EASE_SORTIE }}
            />
          )}
          {series.map((s) =>
            s.bande ? (
              <motion.path
                key={`zone-${s.nom}`}
                d={zone(s.bande)}
                fill={s.couleur}
                initial={{ opacity: 0, clipPath: "inset(0 100% 0 0)" }}
                animate={{ opacity: 0.09, clipPath: "inset(0 0% 0 0)" }}
                transition={{ duration: DUREE_TRACE, ease: EASE_SORTIE }}
              />
            ) : null,
          )}

          {series
            .filter((s) => s !== principale)
            .map((s, i) => (
              <motion.path
                key={s.nom}
                d={tracer(s.valeurs) ?? undefined}
                fill="none"
                stroke={s.couleur}
                strokeWidth={principale ? 1.5 : 2}
                strokeLinejoin="round"
                strokeLinecap="round"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: DUREE_TRACE, ease: EASE_SORTIE, delay: 0.1 + i * 0.08 }}
              />
            ))}
          {principale && (
            <motion.path
              d={tracer(principale.valeurs) ?? undefined}
              fill="none"
              stroke={principale.couleur}
              strokeWidth={2.5}
              strokeLinejoin="round"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: DUREE_TRACE, ease: EASE_SORTIE }}
            />
          )}

          {survol == null &&
            avecPointFinal.map((s) => {
              const derniere = s.valeurs[n - 1];
              return derniere == null ? null : (
                <motion.circle
                  key={`fin-${s.nom}`}
                  cx={x(n - 1)}
                  cy={y(derniere)}
                  r={4.5}
                  fill={s.couleur}
                  stroke="var(--surface)"
                  strokeWidth={2}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 18, delay: DUREE_TRACE * 0.85 }}
                  style={{ transformBox: "fill-box", transformOrigin: "center" }}
                />
              );
            })}
        </g>

        {survol != null && (
          <g>
            <line x1={x(survol)} x2={x(survol)} y1={MARGE.haut} y2={hauteur - MARGE.bas} stroke="var(--line-strong)" strokeWidth={1} />
            {series.map((s) => {
              const v = s.valeurs[survol];
              return v == null ? null : <circle key={s.nom} cx={x(survol)} cy={y(v)} r={4.5} fill={s.couleur} stroke="var(--surface)" strokeWidth={2} />;
            })}
          </g>
        )}

        <rect
          x={MARGE.gauche}
          y={MARGE.haut}
          width={Math.max(0, largeur - MARGE.gauche - MARGE.droite)}
          height={Math.max(0, hauteur - MARGE.haut - MARGE.bas)}
          fill="transparent"
          onPointerMove={surDeplacement}
          onPointerDown={surDeplacement}
          onPointerLeave={() => setSurvol(null)}
          style={{ touchAction: "pan-y" }}
        />
      </svg>

      {survol != null && (
        <div
          className="pointer-events-none absolute top-2 z-10 min-w-44 rounded-lg border border-line bg-surface/95 px-3 py-2 text-xs shadow-card backdrop-blur transition-[left,right] duration-75 ease-out"
          style={bulleAGauche ? { right: largeur - x(survol) + 12 } : { left: x(survol) + 12 }}
        >
          <div className="mb-1.5 font-medium text-ink-2">{etiquettesX[survol]}</div>
          {series.map((s) => {
            const v = s.valeurs[survol];
            if (v == null) return null;
            return (
              <div key={s.nom} className="flex items-center justify-between gap-4 py-0.5">
                <span className="flex items-center gap-1.5 text-ink-2">
                  <span className="inline-block h-0.5 w-3 rounded-full" style={{ background: s.couleur }} />
                  {s.nom}
                </span>
                <span className="font-semibold text-ink tabular-nums">{formatValeur(v)}</span>
              </div>
            );
          })}
          {bande && bande.bas[survol] != null && bande.haut[survol] != null && (
            <div className="mt-1 flex items-center justify-between gap-4 border-t border-line pt-1.5 text-ink-2">
              <span>{bande.nom}</span>
              <span className="tabular-nums">
                {formatValeur(bande.bas[survol] as number)} – {formatValeur(bande.haut[survol] as number)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/** Legende : un trait de la couleur de la serie + son nom (jamais du texte colore). */
export function Legende({ series, bande, reference }: { series: Pick<SerieLigne, "nom" | "couleur">[]; bande?: { nom: string; couleur: string }; reference?: string }) {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-2">
      {series.map((s) => (
        <li key={s.nom} className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 rounded-full" style={{ background: s.couleur }} />
          {s.nom}
        </li>
      ))}
      {bande && (
        <li className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-4 rounded-sm" style={{ background: bande.couleur, opacity: 0.2 }} />
          {bande.nom}
        </li>
      )}
      {reference && (
        <li className="flex items-center gap-1.5">
          <span className="inline-block h-px w-4 bg-muted" />
          {reference}
        </li>
      )}
    </ul>
  );
}
