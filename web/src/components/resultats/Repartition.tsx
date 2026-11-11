"use client";

import { motion } from "motion/react";
import type { LigneAllocation } from "@/lib/api";
import { euros, pourcent } from "@/lib/format";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { EASE_SORTIE } from "@/components/motion/transitions";

const COULEURS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)", "var(--series-5)"];
// Etiquette blanche lisible sur toutes les couleurs, sauf le jaune (slot 4).
const ENCRE = ["#fff", "#fff", "#fff", "#0b0b0b", "#fff"];
const PART_MIN_ETIQUETTE = 0.09;
const NB_GROUPES_MAX = COULEURS.length;

type Groupe = { nom: string; poids: number; investi: number; final: number };

/** Regroupe les lignes par classe d'actifs ; au-dela de 5 classes, le reste devient "Autres". */
function grouper(lignes: LigneAllocation[]): Groupe[] {
  const parClasse = new Map<string, Groupe>();
  for (const l of lignes) {
    const g = parClasse.get(l.categorie) ?? { nom: l.categorie, poids: 0, investi: 0, final: 0 };
    g.poids += l.poids;
    g.investi += l.investi;
    g.final += l.final;
    parClasse.set(l.categorie, g);
  }
  const tries = [...parClasse.values()].sort((a, b) => b.poids - a.poids);
  if (tries.length <= NB_GROUPES_MAX) return tries;
  const autres = tries.slice(NB_GROUPES_MAX - 1).reduce<Groupe>(
    (acc, g) => ({ nom: "Autres", poids: acc.poids + g.poids, investi: acc.investi + g.investi, final: acc.final + g.final }),
    { nom: "Autres", poids: 0, investi: 0, final: 0 },
  );
  return [...tries.slice(0, NB_GROUPES_MAX - 1), autres];
}

/** Repartition du capital par classe d'actifs : barre segmentee + legende chiffree. */
export function Repartition({ allocations }: { allocations: LigneAllocation[] }) {
  const groupes = grouper(allocations);
  const description = groupes.map((g) => `${g.nom} ${pourcent(g.poids * 100, 0)}`).join(", ");
  return (
    <Carte className="p-6">
      <TitreCarte aide="Comment votre capital est réparti entre les grandes classes d'actifs.">Répartition du portefeuille</TitreCarte>
      <div role="img" aria-label={`Répartition : ${description}`} className="flex h-7 w-full gap-0.5 overflow-hidden rounded-md">
        {groupes.map((g, i) => (
          <motion.div
            key={g.nom}
            title={`${g.nom} : ${pourcent(g.poids * 100, 1)}`}
            className="flex h-full min-w-0 origin-left items-center overflow-hidden rounded px-2 text-xs font-semibold"
            style={{ width: `${g.poids * 100}%`, background: COULEURS[i], color: ENCRE[i] }}
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: EASE_SORTIE, delay: i * 0.08 }}
          >
            {g.poids >= PART_MIN_ETIQUETTE && <span className="truncate tabular-nums">{pourcent(g.poids * 100, 0)}</span>}
          </motion.div>
        ))}
      </div>
      <ul className="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
        {groupes.map((g, i) => {
          const perf = g.investi > 0 ? (g.final / g.investi - 1) * 100 : 0;
          return (
            <li key={g.nom} className="flex items-center justify-between gap-3">
              <span className="flex min-w-0 items-center gap-2">
                <span className="size-2.5 shrink-0 rounded-sm" style={{ background: COULEURS[i] }} />
                <span className="truncate text-ink-2">{g.nom}</span>
              </span>
              <span className="shrink-0 tabular-nums">
                <span className="font-medium">{pourcent(g.poids * 100, 0)}</span>
                <span className="text-muted"> · {euros(g.investi)} → </span>
                <span className="font-medium">{euros(g.final)}</span>
                <span className={`ml-1 text-xs ${perf >= 0 ? "text-gain" : "text-loss"}`}>
                  <span aria-hidden>{perf >= 0 ? "▲" : "▼"}</span>
                  <span className="sr-only">{perf >= 0 ? "hausse" : "baisse"}</span>
                </span>
              </span>
            </li>
          );
        })}
      </ul>
    </Carte>
  );
}
