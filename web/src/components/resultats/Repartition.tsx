"use client";

import { motion } from "motion/react";
import type { LigneAllocation } from "@/lib/api";
import { euros, pourcent, pourcentSigne } from "@/lib/format";
import { libelleCategorie } from "@/contenu/actifs";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

const COULEURS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)", "var(--series-5)"];
// Texte lisible pose sur chaque couleur de serie (jetons de globals.css).
const ENCRE = ["var(--on-series-1)", "var(--on-series-2)", "var(--on-series-3)", "var(--on-series-4)", "var(--on-series-5)"];
const PART_MIN_ETIQUETTE = 0.09;
const NB_GROUPES_MAX = COULEURS.length;

type Groupe = { nom: string; poids: number; investi: number; final: number };

/** Regroupe les lignes par classe d'actifs ; au-dela de 5 classes, le reste devient "Autres". */
function grouper(lignes: LigneAllocation[]): Groupe[] {
  const parClasse = new Map<string, Groupe>();
  for (const l of lignes) {
    const nom = libelleCategorie(l.categorie);
    const g = parClasse.get(nom) ?? { nom, poids: 0, investi: 0, final: 0 };
    g.poids += l.poids;
    g.investi += l.investi;
    g.final += l.final;
    parClasse.set(nom, g);
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
    <Carte taille="normale">
      <TitreCarte>Répartition du portefeuille</TitreCarte>
      <p className="sr-only">Comment votre capital est réparti entre les grandes classes d&apos;actifs.</p>
      <div role="img" aria-label={`Répartition : ${description}`} className="flex h-7 w-full gap-0.5 overflow-hidden rounded-controle">
        {groupes.map((g, i) => (
          <motion.div
            key={g.nom}
            className="flex h-full min-w-0 origin-left items-center overflow-hidden px-2 text-xs font-semibold first:rounded-l-controle last:rounded-r-controle"
            style={{ width: `${g.poids * 100}%`, background: COULEURS[i], color: ENCRE[i] }}
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: DUREE.donnees * 0.75, ease: EASE_SORTIE, delay: i * 0.08 }}
          >
            {g.poids >= PART_MIN_ETIQUETTE && <span className="truncate tabular-nums">{pourcent(g.poids * 100, 0)}</span>}
          </motion.div>
        ))}
      </div>
      <ul className="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
        {groupes.map((g, i) => {
          const perf = g.investi > 0 ? (g.final / g.investi - 1) * 100 : 0;
          return (
            <li key={g.nom} className="flex flex-wrap items-center justify-between gap-x-3 gap-y-0.5">
              <span className="flex min-w-0 items-center gap-2">
                <span className="size-2.5 shrink-0 rounded-sm" style={{ background: COULEURS[i] }} aria-hidden />
                <span className="truncate text-ink-2">{g.nom}</span>
                <span className="font-medium tabular-nums">{pourcent(g.poids * 100, 0)}</span>
              </span>
              <span className="shrink-0 tabular-nums">
                <span className="text-muted">{euros(g.investi)} → </span>
                <span className="font-medium">{euros(g.final)}</span>
                <span className={`ml-1.5 text-xs font-medium ${perf >= 0 ? "text-gain" : "text-loss"}`}>{pourcentSigne(perf)}</span>
              </span>
            </li>
          );
        })}
      </ul>
    </Carte>
  );
}
