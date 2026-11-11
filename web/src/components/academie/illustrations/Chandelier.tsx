"use client";

import { motion } from "motion/react";
import { CadreSchema, SchemaAnime, fondu, origine, pousse, trait } from "./commun";

type Bougie = { x: number; haut: number; bas: number; corpsHaut: number; corpsBas: number; couleur: string };

const HAUSSIERE: Bougie = { x: 150, haut: 36, bas: 258, corpsHaut: 86, corpsBas: 196, couleur: "var(--gain)" };
const BAISSIERE: Bougie = { x: 330, haut: 50, bas: 246, corpsHaut: 80, corpsBas: 184, couleur: "var(--loss)" };
const DEMI_CORPS = 26;

function DessinBougie({ b, delai }: { b: Bougie; delai: number }) {
  return (
    <g>
      <motion.line x1={b.x} x2={b.x} y1={b.haut} y2={b.bas} stroke={b.couleur} strokeWidth={3} strokeLinecap="round" variants={trait} custom={delai} />
      <motion.rect
        x={b.x - DEMI_CORPS}
        y={b.corpsHaut}
        width={DEMI_CORPS * 2}
        height={b.corpsBas - b.corpsHaut}
        rx={5}
        fill={b.couleur}
        variants={pousse}
        custom={delai + 0.2}
        style={origine()}
      />
    </g>
  );
}

/** Étiquette O/H/L/C reliée à la bougie par un trait fin. */
function Repere({ y, texte, de, a, ancre, delai }: { y: number; texte: string; de: number; a: number; ancre: "start" | "end"; delai: number }) {
  return (
    <motion.g variants={fondu} custom={delai}>
      <line x1={de} x2={a} y1={y} y2={y} stroke="var(--line-strong)" strokeWidth={1.25} />
      <text x={ancre === "end" ? de - 6 : a + 6} y={y} dy="0.35em" textAnchor={ancre} fontSize={14} fill="var(--ink-2)">
        {texte}
      </text>
    </motion.g>
  );
}

/** Annotation centrale ("mèche", "corps") pointant vers les deux bougies. */
function Annotation({ y, yGauche, yDroite, xGauche, xDroite, texte, delai }: { y: number; yGauche: number; yDroite: number; xGauche: number; xDroite: number; texte: string; delai: number }) {
  return (
    <motion.g variants={fondu} custom={delai}>
      <path d={`M ${xGauche} ${yGauche} L 214 ${y}`} stroke="var(--muted)" strokeWidth={1} strokeDasharray="3 3" fill="none" />
      <path d={`M ${xDroite} ${yDroite} L 266 ${y}`} stroke="var(--muted)" strokeWidth={1} strokeDasharray="3 3" fill="none" />
      <text x={240} y={y} dy="0.35em" textAnchor="middle" fontSize={13} fontStyle="italic" fill="var(--muted)">
        {texte}
      </text>
    </motion.g>
  );
}

export function Chandelier() {
  return (
    <CadreSchema
      legende="Anatomie d’un chandelier japonais : ouverture, plus haut, plus bas, clôture (OHLC). C’est la brique de base de tous les graphiques de marché."
      credit="Schéma redessiné d’après Wikimedia Commons (domaine public)"
    >
      <SchemaAnime
        titre="Anatomie d’un chandelier japonais"
        description="Deux bougies. À gauche, une bougie haussière verte : l’ouverture est en bas du corps, la clôture en haut. À droite, une bougie baissière rouge : l’ouverture est en haut du corps, la clôture en bas. Les mèches relient le plus haut et le plus bas de la séance."
        viewBox="0 0 480 316"
        className="mx-auto max-w-[30rem]"
      >
        <DessinBougie b={HAUSSIERE} delai={0} />
        <DessinBougie b={BAISSIERE} delai={0.15} />

        <Repere y={HAUSSIERE.haut} texte="Plus haut" de={96} a={146} ancre="end" delai={0.5} />
        <Repere y={HAUSSIERE.corpsHaut} texte="Clôture" de={96} a={124} ancre="end" delai={0.56} />
        <Repere y={HAUSSIERE.corpsBas} texte="Ouverture" de={96} a={124} ancre="end" delai={0.62} />
        <Repere y={HAUSSIERE.bas} texte="Plus bas" de={96} a={146} ancre="end" delai={0.68} />

        <Repere y={BAISSIERE.haut} texte="Plus haut" de={334} a={384} ancre="start" delai={0.56} />
        <Repere y={BAISSIERE.corpsHaut} texte="Ouverture" de={356} a={384} ancre="start" delai={0.62} />
        <Repere y={BAISSIERE.corpsBas} texte="Clôture" de={356} a={384} ancre="start" delai={0.68} />
        <Repere y={BAISSIERE.bas} texte="Plus bas" de={334} a={384} ancre="start" delai={0.74} />

        <Annotation texte="mèche" y={62} xGauche={154} yGauche={62} xDroite={326} yDroite={66} delai={0.8} />
        <Annotation texte="corps" y={138} xGauche={178} yGauche={140} xDroite={302} yDroite={132} delai={0.86} />
        <Annotation texte="mèche" y={226} xGauche={154} yGauche={226} xDroite={326} yDroite={214} delai={0.92} />

        <motion.g variants={fondu} custom={0.4}>
          <text x={HAUSSIERE.x} y={288} textAnchor="middle" fontSize={14} fontWeight={600} fill="var(--gain)">
            Haussière
          </text>
          <text x={HAUSSIERE.x} y={306} textAnchor="middle" fontSize={12} fill="var(--muted)">
            {"clôture > ouverture"}
          </text>
          <text x={BAISSIERE.x} y={288} textAnchor="middle" fontSize={14} fontWeight={600} fill="var(--loss)">
            Baissière
          </text>
          <text x={BAISSIERE.x} y={306} textAnchor="middle" fontSize={12} fill="var(--muted)">
            {"clôture < ouverture"}
          </text>
        </motion.g>
      </SchemaAnime>
    </CadreSchema>
  );
}
