"use client";

import { motion, type Variants } from "motion/react";
import { nombreSigne } from "@/lib/format";
import { EASE_SORTIE } from "@/components/motion/transitions";

const ACTIFS = ["Actions US", "Obligs 10Y", "Or", "Pétrole", "BTC"];
const VALEURS = [
  [1, -0.3, 0.1, 0.3, 0.4],
  [-0.3, 1, 0.2, -0.1, -0.05],
  [0.1, 0.2, 1, 0.2, 0.2],
  [0.3, -0.1, 0.2, 1, 0.2],
  [0.4, -0.05, 0.2, 0.2, 1],
];

// Les cellules apparaissent en vague, depuis le coin haut-gauche.
const cellule: Variants = {
  cache: { opacity: 0, scale: 0.9 },
  visible: (rang: number) => ({ opacity: 1, scale: 1, transition: { duration: 0.3, ease: EASE_SORTIE, delay: 0.05 + rang * 0.05 } }),
};

function fond(v: number, diagonale: boolean) {
  if (diagonale) return "var(--surface-2)";
  const couleur = v >= 0 ? "var(--accent)" : "var(--series-2)";
  return `color-mix(in oklab, ${couleur} ${Math.round(Math.abs(v) * 80)}%, transparent)`;
}

/** Corrélations en régime normal : chiffre + intensité de couleur (le signe ne repose pas que sur la teinte). */
export function MatriceCorrelations() {
  return (
    <figure className="max-w-[46rem]">
      <div tabIndex={0} className="overflow-x-auto rounded-carte border border-line bg-surface p-3 shadow-card sm:p-4">
        <motion.table className="w-full min-w-[30rem] border-separate border-spacing-1 text-sm" initial="cache" whileInView="visible" viewport={{ once: true }}>
          <caption className="sr-only">Corrélations entre classes d’actifs en régime normal</caption>
          <thead>
            <tr>
              <td />
              {ACTIFS.map((a) => (
                <th key={a} scope="col" className="px-2 pb-1 text-center text-xs font-semibold text-muted">
                  {a}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ACTIFS.map((ligne, i) => (
              <tr key={ligne}>
                <th scope="row" className="whitespace-nowrap pr-2 text-left text-xs font-semibold text-ink">
                  {ligne}
                </th>
                {VALEURS[i].map((v, j) => (
                  <motion.td
                    key={j}
                    variants={cellule}
                    custom={i + j}
                    className={`rounded-controle px-2 py-2.5 text-center tabular-nums ${i === j ? "text-muted" : "font-medium text-ink"}`}
                    style={{ background: fond(v, i === j) }}
                  >
                    {nombreSigne(v, 2)}
                  </motion.td>
                ))}
              </tr>
            ))}
          </tbody>
        </motion.table>
      </div>
      <figcaption className="mt-2.5 flex flex-wrap gap-x-5 gap-y-1.5 text-xs text-muted">
        <span className="inline-flex items-center gap-1.5">
          <span className="size-3 rounded" style={{ background: fond(0.5, false) }} aria-hidden />
          positive : les actifs évoluent ensemble
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="size-3 rounded" style={{ background: fond(-0.5, false) }} aria-hidden />
          négative : ils évoluent en sens inverse
        </span>
      </figcaption>
    </figure>
  );
}
