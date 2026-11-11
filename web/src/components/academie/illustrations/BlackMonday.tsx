"use client";

import { motion } from "motion/react";
import { CadreSchema, SchemaAnime, fondu, surgit, trait, origine } from "./commun";

// Tracé simplifié du Dow Jones (août → novembre 1987), en séances de bourse.
// Seuls les points annotés sont des clôtures réelles ; le reste relie ces repères.
const REPERES: [number, number][] = [
  [0, 2560],
  [16, 2722], // 25 août : record de l'époque
  [35, 2490],
  [44, 2640],
  [54, 2247], // vendredi 16 octobre
  [55, 1739], // lundi 19 octobre
  [56, 1841],
  [57, 2028],
  [60, 1794],
  [70, 1960],
  [84, 1834],
];
const JOUR_PIC = 16;
const JOUR_VEILLE = 54;
const JOUR_KRACH = 55;

function valeur(j: number): number {
  const i = REPERES.findIndex(([jour]) => jour >= j);
  if (REPERES[i][0] === j) return REPERES[i][1];
  const [j0, v0] = REPERES[i - 1];
  const [j1, v1] = REPERES[i];
  const base = v0 + ((v1 - v0) * (j - j0)) / (j1 - j0);
  // Petites oscillations déterministes pour un aspect de cours (même rendu serveur et navigateur).
  return base + 22 * Math.sin(j * 1.7) + 12 * Math.sin(j * 0.63 + 1);
}

const DERNIER = 84;
const x = (j: number) => 56 + (j / DERNIER) * 480;
const y = (v: number) => 262 - ((v - 1600) / 1200) * 232;
const JOURS = Array.from({ length: DERNIER + 1 }, (_, j) => j);
const avant = JOURS.filter((j) => j <= JOUR_VEILLE).map((j) => `${x(j).toFixed(1)},${y(valeur(j)).toFixed(1)}`);
const apres = JOURS.filter((j) => j >= JOUR_KRACH).map((j) => `${x(j).toFixed(1)},${y(valeur(j)).toFixed(1)}`);

const GRADUATIONS = [1800, 2200, 2600];
const MOIS = [
  { j: 0, nom: "août" },
  { j: 21, nom: "sept." },
  { j: 42, nom: "oct." },
  { j: 64, nom: "nov." },
];

export function BlackMonday() {
  const xV = x(JOUR_VEILLE);
  const xK = x(JOUR_KRACH);
  const yV = y(valeur(JOUR_VEILLE));
  const yK = y(valeur(JOUR_KRACH));
  return (
    <CadreSchema
      legende="Le Dow Jones le 19 octobre 1987 : −22,6% en une seule séance, record absolu jamais égalé. Le trading algorithmique automatique a été identifié comme cause principale. (Tracé simplifié : seules les valeurs annotées sont des clôtures réelles.)"
      credit="Schéma redessiné d’après Wikimedia Commons (CC BY-SA)"
    >
      <SchemaAnime
        titre="Le Dow Jones autour du Black Monday de 1987"
        description="Le Dow Jones culmine à 2 722 points le 25 août 1987, recule à 2 247 points le vendredi 16 octobre, puis s’effondre à 1 739 points le lundi 19 octobre, soit −22,6 % en une séance, avant de rebondir partiellement."
        viewBox="0 0 560 300"
      >
        {GRADUATIONS.map((g, i) => (
          <motion.g key={g} variants={fondu} custom={i * 0.05}>
            <line x1={56} x2={536} y1={y(g)} y2={y(g)} stroke="var(--line)" strokeWidth={1} />
            <text x={48} y={y(g)} dy="0.35em" textAnchor="end" fontSize={12} fill="var(--muted)">
              {g.toLocaleString("fr-FR")}
            </text>
          </motion.g>
        ))}
        <motion.g variants={fondu} custom={0.1}>
          {MOIS.map((m) => (
            <text key={m.nom} x={x(m.j)} y={288} textAnchor="start" fontSize={12} fill="var(--muted)">
              {m.nom} 1987
            </text>
          ))}
        </motion.g>

        <motion.polyline points={avant.join(" ")} fill="none" stroke="var(--ink-2)" strokeWidth={2.25} strokeLinejoin="round" variants={trait} custom={0.15} />
        <motion.line x1={xV} y1={yV} x2={xK} y2={yK} stroke="var(--loss)" strokeWidth={3.5} strokeLinecap="round" variants={trait} custom={0.7} />
        <motion.polyline points={apres.join(" ")} fill="none" stroke="var(--ink-2)" strokeWidth={2.25} strokeLinejoin="round" variants={trait} custom={0.85} />

        <motion.circle cx={x(JOUR_PIC)} cy={y(2722)} r={4.5} fill="var(--ink)" stroke="var(--surface)" strokeWidth={2} variants={surgit} custom={0.55} style={origine()} />
        <motion.text x={x(JOUR_PIC)} y={y(2722) - 12} textAnchor="middle" fontSize={12.5} fill="var(--ink-2)" variants={fondu} custom={0.6}>
          25 août : 2 722
        </motion.text>

        <motion.circle cx={xV} cy={yV} r={4.5} fill="var(--ink)" stroke="var(--surface)" strokeWidth={2} variants={surgit} custom={0.65} style={origine()} />
        <motion.text x={xV - 8} y={yV + 18} textAnchor="end" fontSize={12.5} fill="var(--ink-2)" variants={fondu} custom={0.7}>
          ven. 16 oct. : 2 247
        </motion.text>

        <motion.circle cx={xK} cy={yK} r={5.5} fill="var(--loss)" stroke="var(--surface)" strokeWidth={2} variants={surgit} custom={0.95} style={origine()} />
        <motion.g variants={fondu} custom={1}>
          <text x={xK - 14} y={yK + 2} textAnchor="end" fontSize={13} fontWeight={600} fill="var(--loss)">
            lun. 19 oct. : 1 739
          </text>
          <text x={xK - 14} y={yK + 19} textAnchor="end" fontSize={13} fontWeight={600} fill="var(--loss)">
            −22,6 % en une séance
          </text>
        </motion.g>
      </SchemaAnime>
    </CadreSchema>
  );
}
