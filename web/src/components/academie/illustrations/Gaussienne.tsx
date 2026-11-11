"use client";

import { motion } from "motion/react";
import { CadreSchema, SchemaAnime, fondu, trait } from "./commun";

const BASE = 236;
const x = (z: number) => 280 + z * 62;
const y = (densite: number) => BASE - densite * 480;
const normale = (z: number, s = 1) => Math.exp(-(z * z) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI));
// Schéma (pas une estimation) : un mélange de deux gaussiennes donne des queues plus épaisses.
const reelle = (z: number) => 0.7 * normale(z, 0.75) + 0.3 * normale(z, 1.6);

function courbe(f: (z: number) => number, de = -4, a = 4, pas = 0.05) {
  const points: string[] = [];
  for (let z = de; z <= a + 1e-9; z += pas) points.push(`${x(z).toFixed(1)},${y(f(z)).toFixed(1)}`);
  return points;
}

function aire(de: number, a: number) {
  return `M ${x(de)},${BASE} L ${courbe(normale, de, a, 0.04).join(" L ")} L ${x(a)},${BASE} Z`;
}

const BANDES = [
  { de: -1, a: 1, opacite: 0.34 },
  { de: -2, a: -1, opacite: 0.2 },
  { de: 1, a: 2, opacite: 0.2 },
  { de: -3, a: -2, opacite: 0.11 },
  { de: 2, a: 3, opacite: 0.11 },
];

const PARTS = [
  { z: -0.5, y: 182, texte: "34,1 %" },
  { z: 0.5, y: 182, texte: "34,1 %" },
  { z: -1.5, y: 218, texte: "13,6 %" },
  { z: 1.5, y: 218, texte: "13,6 %" },
  { z: -2.45, y: 212, texte: "2,1 %" },
  { z: 2.45, y: 212, texte: "2,1 %" },
];

function Accolade({ de, a, yLigne, texte, delai }: { de: number; a: number; yLigne: number; texte: string; delai: number }) {
  return (
    <motion.g variants={fondu} custom={delai}>
      <path d={`M ${x(de)} ${yLigne - 5} V ${yLigne} H ${x(a)} V ${yLigne - 5}`} fill="none" stroke="var(--line-strong)" strokeWidth={1.25} />
      <text x={280} y={yLigne + 14} textAnchor="middle" fontSize={12.5} fill="var(--ink-2)">
        {texte}
      </text>
    </motion.g>
  );
}

export function Gaussienne() {
  return (
    <CadreSchema
      legende="Loi normale : 68% des rendements quotidiens tombent dans −1 sigma à +1 sigma, 95% dans −2 à +2 sigma. Les krachs (−10% en un jour) sont théoriquement impossibles selon ce modèle, alors qu’ils arrivent en pratique tous les 5-10 ans. La courbe pointillée schématise ces queues épaisses."
      credit="Schéma redessiné d’après Wikimedia Commons (CC BY-SA)"
    >
      <SchemaAnime
        titre="Loi normale et écarts-types"
        description="Courbe en cloche centrée sur la moyenne. 34,1 % des valeurs entre la moyenne et un écart-type de chaque côté, 13,6 % entre un et deux écarts-types, 2,1 % entre deux et trois. Une courbe pointillée, plus haute aux extrémités, représente les queues épaisses observées sur les marchés."
        viewBox="0 0 560 318"
      >
        {BANDES.map((b, i) => (
          <motion.path key={i} d={aire(b.de, b.a)} fill="var(--accent)" fillOpacity={b.opacite} variants={fondu} custom={0.35 + i * 0.05} />
        ))}
        {[-3, -2, -1, 1, 2, 3].map((z) => (
          <motion.line key={z} x1={x(z)} x2={x(z)} y1={BASE} y2={y(normale(z))} stroke="var(--surface)" strokeWidth={1.5} variants={fondu} custom={0.5} />
        ))}

        <motion.line x1={x(-4)} x2={x(4)} y1={BASE} y2={BASE} stroke="var(--line-strong)" strokeWidth={1.25} variants={trait} custom={0} />
        <motion.polyline points={courbe(normale).join(" ")} fill="none" stroke="var(--accent)" strokeWidth={2.75} strokeLinejoin="round" variants={trait} custom={0.1} />
        <motion.polyline
          points={courbe(reelle).join(" ")}
          fill="none"
          stroke="var(--series-2)"
          strokeWidth={2}
          strokeDasharray="5 5"
          strokeLinejoin="round"
          variants={fondu}
          custom={0.75}
        />

        {PARTS.map((p) => (
          <motion.text key={p.z} x={x(p.z)} y={p.y} textAnchor="middle" fontSize={p.texte.length > 5 ? 13 : 11.5} fontWeight={600} fill="var(--ink)" variants={fondu} custom={0.6}>
            {p.texte}
          </motion.text>
        ))}

        <motion.g variants={fondu} custom={0.3}>
          {[-3, -2, -1, 0, 1, 2, 3].map((z) => (
            <text key={z} x={x(z)} y={BASE + 17} textAnchor="middle" fontSize={12} fill="var(--muted)">
              {z === 0 ? "μ" : `${z > 0 ? "+" : "−"}${Math.abs(z)}σ`}
            </text>
          ))}
        </motion.g>

        <Accolade de={-1} a={1} yLigne={268} texte="68 % des séances" delai={0.8} />
        <Accolade de={-2} a={2} yLigne={298} texte="95 % des séances" delai={0.88} />

        <motion.g variants={fondu} custom={0.95}>
          <path d={`M ${x(-3.15)} ${y(reelle(-3.15)) - 4} Q ${x(-3.4)} 190 ${x(-3.3)} 172`} fill="none" stroke="var(--series-2)" strokeWidth={1.25} />
          <text x={x(-3.75)} y={160} fontSize={12.5} fill="var(--ink-2)">
            queues épaisses :
          </text>
          <text x={x(-3.75)} y={175} fontSize={12.5} fill="var(--ink-2)" dy="0.2em">
            les krachs réels
          </text>
        </motion.g>

        <motion.g variants={fondu} custom={0.2}>
          <line x1={24} x2={46} y1={22} y2={22} stroke="var(--accent)" strokeWidth={2.75} />
          <text x={52} y={22} dy="0.35em" fontSize={12.5} fill="var(--ink-2)">
            Loi normale (modèle)
          </text>
          <line x1={24} x2={46} y1={42} y2={42} stroke="var(--series-2)" strokeWidth={2} strokeDasharray="5 5" />
          <text x={52} y={42} dy="0.35em" fontSize={12.5} fill="var(--ink-2)">
            Réalité des marchés
          </text>
        </motion.g>
      </SchemaAnime>
    </CadreSchema>
  );
}
