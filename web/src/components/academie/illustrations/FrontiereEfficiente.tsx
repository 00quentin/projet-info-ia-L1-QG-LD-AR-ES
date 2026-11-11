"use client";

import { motion } from "motion/react";
import { CadreSchema, SchemaAnime, fondu, origine, surgit, trait } from "./commun";

// Schéma : frontière σ(μ) = √(σ0² + k(μ − μ0)²), en % annuels.
const SIGMA0 = 8;
const MU0 = 5;
const K = 6;
const sigma = (mu: number) => Math.sqrt(SIGMA0 ** 2 + K * (mu - MU0) ** 2);
const x = (s: number) => 56 + s * 15.8;
const y = (mu: number) => 280 - mu * 18;

function trace(de: number, a: number) {
  const pts: string[] = [];
  for (let mu = de; mu <= a + 1e-9; mu += 0.1) pts.push(`${x(sigma(mu)).toFixed(1)},${y(mu).toFixed(1)}`);
  return pts.join(" ");
}

// Nuage de portefeuilles possibles : générateur pseudo-aléatoire à graine fixe (rendu identique partout).
function nuage(n: number) {
  let graine = 7;
  const alea = () => {
    graine = (graine * 16807) % 2147483647;
    return graine / 2147483647;
  };
  return Array.from({ length: n }, () => {
    const mu = 2 + alea() * 9.5;
    const ecart = 0.6 + alea() ** 1.6 * 10;
    return { cx: x(sigma(mu) + ecart), cy: y(mu) };
  });
}
const POINTS = nuage(70);

// Portefeuille sous-optimal mis en évidence, et son équivalent sur la frontière à risque égal.
const S_EXEMPLE = 16;
const MU_EXEMPLE = 6;
const MU_FRONTIERE = MU0 + Math.sqrt((S_EXEMPLE ** 2 - SIGMA0 ** 2) / K);

export function FrontiereEfficiente() {
  return (
    <CadreSchema
      legende="La frontière efficiente de Markowitz (1952) : pour chaque niveau de risque, il existe un portefeuille qui maximise le rendement attendu. Les portefeuilles en-dessous de cette courbe sont sous-optimaux."
      credit="Schéma redessiné d’après Wikimedia Commons (CC BY-SA)"
    >
      <SchemaAnime
        titre="La frontière efficiente de Markowitz"
        description="Nuage de portefeuilles possibles placés selon leur risque (en abscisse) et leur rendement attendu (en ordonnée). La courbe supérieure du nuage est la frontière efficiente. Un portefeuille du nuage peut être remplacé par un portefeuille de la frontière qui a le même risque et un meilleur rendement."
        viewBox="0 0 560 320"
      >
        <motion.g variants={fondu} custom={0}>
          <line x1={56} x2={536} y1={280} y2={280} stroke="var(--line-strong)" strokeWidth={1.25} />
          <line x1={56} x2={56} y1={20} y2={280} stroke="var(--line-strong)" strokeWidth={1.25} />
          <text x={536} y={302} textAnchor="end" fontSize={12.5} fill="var(--muted)">
            Risque (volatilité) →
          </text>
          <text x={20} y={150} textAnchor="middle" fontSize={12.5} fill="var(--muted)" transform="rotate(-90 20 150)">
            Rendement attendu →
          </text>
        </motion.g>

        {POINTS.map((p, i) => (
          <motion.circle key={i} cx={p.cx} cy={p.cy} r={3.25} fill="var(--muted)" fillOpacity={0.5} variants={surgit} custom={0.05 + (i % 14) * 0.025} style={origine()} />
        ))}

        <motion.polyline points={trace(1.5, MU0)} fill="none" stroke="var(--muted)" strokeWidth={1.75} strokeDasharray="4 5" variants={trait} custom={0.45} />
        <motion.polyline points={trace(MU0, 13)} fill="none" stroke="var(--accent)" strokeWidth={3} strokeLinecap="round" variants={trait} custom={0.5} />

        <motion.circle cx={x(SIGMA0)} cy={y(MU0)} r={5.5} fill="var(--accent)" stroke="var(--surface)" strokeWidth={2} variants={surgit} custom={0.9} style={origine()} />
        <motion.text x={x(SIGMA0) - 10} y={y(MU0) + 4} textAnchor="end" fontSize={12} fill="var(--ink-2)" variants={fondu} custom={0.95}>
          <tspan x={x(SIGMA0) - 10} dy="-0.4em">Variance</tspan>
          <tspan x={x(SIGMA0) - 10} dy="1.2em">minimale</tspan>
        </motion.text>
        <motion.text x={x(sigma(13)) + 10} y={y(13) + 4} fontSize={13.5} fontWeight={600} fill="var(--accent)" variants={fondu} custom={1}>
          Frontière efficiente
        </motion.text>

        <motion.g variants={fondu} custom={1.05}>
          <circle cx={x(S_EXEMPLE)} cy={y(MU_EXEMPLE)} r={6} fill="none" stroke="var(--ink-2)" strokeWidth={1.5} />
          <line x1={x(S_EXEMPLE)} x2={x(S_EXEMPLE)} y1={y(MU_EXEMPLE) - 9} y2={y(MU_FRONTIERE) + 8} stroke="var(--ink-2)" strokeWidth={1.5} />
          <path
            d={`M ${x(S_EXEMPLE) - 5} ${y(MU_FRONTIERE) + 14} L ${x(S_EXEMPLE)} ${y(MU_FRONTIERE) + 6} L ${x(S_EXEMPLE) + 5} ${y(MU_FRONTIERE) + 14}`}
            fill="none"
            stroke="var(--ink-2)"
            strokeWidth={1.5}
          />
          <text x={x(S_EXEMPLE) + 10} y={(y(MU_EXEMPLE) + y(MU_FRONTIERE)) / 2} fontSize={12.5} fill="var(--ink-2)">
            <tspan x={x(S_EXEMPLE) + 10} dy="-0.4em">même risque,</tspan>
            <tspan x={x(S_EXEMPLE) + 10} dy="1.25em">meilleur rendement</tspan>
          </text>
        </motion.g>
        <motion.text x={452} y={236} textAnchor="middle" fontSize={12.5} fontStyle="italic" fill="var(--muted)" variants={fondu} custom={0.6}>
          portefeuilles sous-optimaux
        </motion.text>
      </SchemaAnime>
    </CadreSchema>
  );
}
