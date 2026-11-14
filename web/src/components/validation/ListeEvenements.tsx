"use client";

import { useMemo, useState } from "react";
import { ChevronDown } from "lucide-react";
import type { CriseValidee } from "@/lib/validation";
import { Pastille } from "@/components/ui/Carte";
import { CarteCrise } from "./CarteCrise";
import { libelleCategorie, part, periode, points } from "./outils";

type Tri = "date" | "erreur" | "sens";

const TRIS: { valeur: Tri; libelle: string }[] = [
  { valeur: "date", libelle: "Date" },
  { valeur: "erreur", libelle: "Erreur moyenne (la plus forte d’abord)" },
  { valeur: "sens", libelle: "Bon sens (le plus faible d’abord)" },
];

function trier(crises: CriseValidee[], tri: Tri): CriseValidee[] {
  const copie = [...crises];
  if (tri === "erreur") return copie.sort((a, b) => (b.metriques.erreur_moyenne_pts ?? 0) - (a.metriques.erreur_moyenne_pts ?? 0));
  if (tri === "sens") return copie.sort((a, b) => (a.metriques.part_sens_correct ?? 1) - (b.metriques.part_sens_correct ?? 1));
  return copie.sort((a, b) => a.debut.localeCompare(b.debut));
}

function Ligne({ crise }: { crise: CriseValidee }) {
  const [ouvert, setOuvert] = useState(false);
  const idDetail = `detail-${crise.nom.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}`;
  const m = crise.metriques;
  return (
    <li className="border-t border-line first:border-t-0">
      <h3>
        <button
          type="button"
          onClick={() => setOuvert((o) => !o)}
          aria-expanded={ouvert}
          aria-controls={idDetail}
          className="flex w-full items-start gap-3 px-3 py-3 text-left transition-colors hover:bg-surface-2/60 focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent sm:px-4"
        >
          <span className="min-w-0 flex-1">
            <span className="block text-[14px] font-semibold leading-snug text-ink">{crise.nom}</span>
            <span className="mt-0.5 block text-xs text-muted">
              {periode(crise.premiere_seance, crise.derniere_seance)} · {crise.nb_seances} séances
            </span>
            <span className="mt-1.5 flex flex-wrap items-center gap-1.5">
              {crise.categorie && <Pastille>{libelleCategorie(crise.categorie)}</Pastille>}
              {crise.hors_echantillon && <Pastille ton="accent">Hors échantillon</Pastille>}
            </span>
          </span>
          <span className="flex shrink-0 flex-col items-end text-right text-xs leading-snug tabular-nums">
            <span className="text-[13px] font-semibold text-ink">
              <span className="sr-only">Bon sens : </span>
              {m.nb_sens_corrects} / {m.nb_sens_comptes}
              <span className="ml-1 font-normal text-muted">({part(m.part_sens_correct)})</span>
            </span>
            <span className="text-ink-2">
              <span className="sr-only">Erreur moyenne : </span>
              {points(m.erreur_moyenne_pts)}
            </span>
          </span>
          <ChevronDown className={`mt-0.5 size-4 shrink-0 text-muted transition-transform ${ouvert ? "rotate-180" : ""}`} aria-hidden />
        </button>
      </h3>
      {ouvert && (
        <div id={idDetail} className="px-2 pb-3 sm:px-3">
          <CarteCrise crise={crise} />
        </div>
      )}
    </li>
  );
}

/** Liste compacte des événements : une ligne repliée chacune, le détail s'ouvre à la demande. */
export function ListeEvenements({ crises }: { crises: CriseValidee[] }) {
  const [tri, setTri] = useState<Tri>("date");
  const triees = useMemo(() => trier(crises, tri), [crises, tri]);
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <p className="text-sm text-muted" aria-live="polite">
          {crises.length} événement{crises.length > 1 ? "s" : ""}
        </p>
        <label className="flex items-center gap-2 text-xs text-ink-2">
          Trier par
          <select
            value={tri}
            onChange={(e) => setTri(e.target.value as Tri)}
            className="max-w-[14rem] rounded-controle border border-line bg-surface px-2 py-1.5 text-xs text-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            {TRIS.map((t) => (
              <option key={t.valeur} value={t.valeur}>
                {t.libelle}
              </option>
            ))}
          </select>
        </label>
      </div>
      <ul className="overflow-hidden rounded-carte border border-line bg-surface shadow-card">
        {triees.map((c) => (
          <Ligne key={c.nom} crise={c} />
        ))}
      </ul>
    </div>
  );
}
