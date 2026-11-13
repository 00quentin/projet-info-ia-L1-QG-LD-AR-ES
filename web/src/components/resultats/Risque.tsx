"use client";

import type { ReactNode } from "react";
import { CircleAlert, CircleCheck, Info, TriangleAlert } from "lucide-react";
import type { Alerte, Metriques } from "@/lib/api";
import { nombreSigne, pourcent, pourcentSigne } from "@/lib/format";
import { Cascade, ElementCascade, LigneCascade } from "@/components/motion/Apparition";
import { Infobulle } from "./Infobulle";

/** Cran 0 = favorable ... cran 3 = defavorable (echelle a 4 crans). */
export type Niveau = { libelle: string; cran: 0 | 1 | 2 | 3 };

// Memes seuils que core/risk_alerts.py et core/metrics.py (standards de l'industrie).
export function niveauVolatilite(v: number): Niveau {
  if (v < 15) return { libelle: "Modérée", cran: 0 };
  if (v < 25) return { libelle: "Normale", cran: 1 };
  if (v < 35) return { libelle: "Élevée", cran: 2 };
  return { libelle: "Très élevée", cran: 3 };
}
export function niveauSharpe(s: number, qualite: string): Niveau {
  return { libelle: qualite, cran: s >= 2 ? 0 : s >= 1 ? 1 : s >= 0 ? 2 : 3 };
}
export function niveauDrawdown(d: number): Niveau {
  if (d < 10) return { libelle: "Limitée", cran: 0 };
  if (d < 25) return { libelle: "Modérée", cran: 1 };
  if (d < 40) return { libelle: "Sévère", cran: 2 };
  return { libelle: "Critique", cran: 3 };
}
// 5 % et plus : seuil de l'alerte rouge de core/risk_alerts.py.
export function niveauVar(v: number): Niveau {
  const abs = Math.abs(v);
  if (abs < 2) return { libelle: "Faible", cran: 0 };
  if (abs < 4) return { libelle: "Modérée", cran: 1 };
  if (abs < 5) return { libelle: "Élevée", cran: 2 };
  return { libelle: "Très élevée", cran: 3 };
}

const CRANS = [
  { plein: "bg-gain", doux: "bg-gain/20" },
  { plein: "bg-muted", doux: "bg-line" },
  { plein: "bg-warn", doux: "bg-warn/25" },
  { plein: "bg-loss", doux: "bg-loss/20" },
] as const;

/** Echelle a 4 crans (du plus favorable au moins favorable), le cran atteint en couleur pleine. */
export function Echelle({ niveau }: { niveau: Niveau }) {
  return (
    <span className="flex items-center gap-2">
      <span className="flex gap-0.5" aria-hidden>
        {CRANS.map((c, i) => (
          <span key={i} className={`h-1.5 w-5 rounded-full ${i === niveau.cran ? c.plein : c.doux}`} />
        ))}
      </span>
      <span className="text-xs font-medium text-ink-2">
        {niveau.libelle}
        <span className="sr-only"> (niveau {niveau.cran + 1} sur 4, du plus favorable au moins favorable)</span>
      </span>
    </span>
  );
}

export type Recuperation = {
  /** Jour du sommet d'avant la chute (0 = capital de depart). */
  sommet: number;
  creux: number;
  /** Premier jour ou la valeur du sommet est retrouvee, ou null. */
  retour: number | null;
  /** Ampleur de la chute, en % (positif). */
  baisse: number;
};

/** Plus forte chute d'une trajectoire (sommet -> creux) et jour ou elle est effacee ; null s'il n'y a aucun recul. */
export function calculerRecuperation(valeurs: (number | null)[]): Recuperation | null {
  let sommet = -1;
  let pire = { sommet: 0, creux: 0, baisse: 0 };
  valeurs.forEach((v, i) => {
    if (v == null) return;
    if (sommet < 0 || v > (valeurs[sommet] as number)) sommet = i;
    const haut = valeurs[sommet] as number;
    const baisse = haut > 0 ? ((haut - v) / haut) * 100 : 0;
    if (baisse > pire.baisse) pire = { sommet, creux: i, baisse };
  });
  // En dessous d'un centieme de point, on parle d'une trajectoire sans recul.
  if (pire.baisse < 0.01) return null;
  const niveau = valeurs[pire.sommet] as number;
  const retour = valeurs.findIndex((v, i) => i > pire.creux && v != null && v >= niveau);
  return { ...pire, retour: retour < 0 ? null : retour };
}

/** Libelle court du retour (ex. « Retour au capital : jour 34 »). */
function libelleRetour(r: Recuperation | null, etiquette: (i: number) => string): string {
  if (!r) return "Aucun recul en cours de route";
  const cible = r.sommet === 0 ? "capital" : "plus haut";
  return r.retour == null ? `Pas de retour au ${cible} sur l'horizon` : `Retour au ${cible} : ${etiquette(r.retour)}`;
}

function phraseRetour(r: Recuperation | null, etiquette: (i: number) => string, precision: string): string {
  if (!r) return `${precision} ne recule jamais sous son plus haut.`;
  const depart = r.sommet === 0 ? "le capital de départ" : `son plus haut (${etiquette(r.sommet)})`;
  const fin = r.retour == null ? "Ce niveau n'est pas retrouvé avant la fin de l'horizon." : `Retour à ce niveau : ${etiquette(r.retour)}.`;
  return `${precision} recule au plus de ${pourcent(r.baisse)} sous ${depart} (creux : ${etiquette(r.creux)}). ${fin}`;
}

function Tuile({ titre, valeur, niveau, resume, explication, children }: { titre: string; valeur: string; niveau: Niveau; resume: string; explication: ReactNode; children?: ReactNode }) {
  return (
    <ElementCascade className="h-full">
      <div className="flex h-full flex-col gap-2 rounded-tuile border border-line bg-surface p-4">
        <span className="flex items-center gap-1 text-aide font-medium text-muted">
          {titre}
          <Infobulle libelle={`En savoir plus : ${titre}`}>{explication}</Infobulle>
        </span>
        <span className="text-2xl font-semibold tracking-tight tabular-nums">{valeur}</span>
        <Echelle niveau={niveau} />
        <span className="text-aide text-ink-2">{resume}</span>
        {children}
      </div>
    </ElementCascade>
  );
}

type Props = {
  m: Metriques;
  tauxSansRisquePct?: number;
  /** Trajectoire du portefeuille, pour le temps de retour apres la pire chute. */
  valeurs?: (number | null)[];
  /** Libelle d'un point de la trajectoire (« jour 34 », « 12 mai 2020 »). */
  etiquette?: (i: number) => string;
  /** Debut de phrase qui nomme la trajectoire mesuree (« La trajectoire médiane »). */
  precisionTrajectoire?: string;
};

/** Les 4 metriques de risque : valeur, echelle a 4 crans, une ligne courte ; la phrase complete en infobulle. */
export function TuilesRisque({ m, tauxSansRisquePct, valeurs, etiquette = (i) => `jour ${i}`, precisionTrajectoire = "Le portefeuille" }: Props) {
  const refSharpe = tauxSansRisquePct != null ? ` Calculé au-delà du taux sans risque de ${pourcent(tauxSansRisquePct, 2)} (taux de dépôt BCE).` : "";
  const recup = valeurs ? calculerRecuperation(valeurs) : undefined;
  return (
    <Cascade auDefilement className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Tuile
        titre="Volatilité annualisée"
        valeur={pourcent(m.vol_ann)}
        niveau={niveauVolatilite(m.vol_ann)}
        resume="Ampleur habituelle des variations sur un an"
        explication="L'ampleur habituelle des variations sur un an. Plus elle est haute, plus le parcours est agité. Repères : moins de 15 % modérée, 15 à 25 % normale, 25 à 35 % élevée, au-delà très élevée."
      />
      <Tuile
        titre="Ratio de Sharpe"
        valeur={nombreSigne(m.sharpe)}
        niveau={niveauSharpe(m.sharpe, m.qualite_sharpe)}
        resume="Rendement obtenu par unité de risque prise"
        explication={`Le rendement obtenu pour chaque unité de risque prise. Au-dessus de 1, le risque est bien payé.${refSharpe}`}
      />
      <Tuile
        titre="Perte maximale"
        valeur={`−${pourcent(Math.abs(m.max_dd))}`}
        niveau={niveauDrawdown(m.max_dd)}
        resume="Pire chute d'un sommet au creux suivant"
        explication={
          <>
            La pire chute entre un sommet et le creux qui suit, en cours de route (en anglais : <em>drawdown</em>).
            {recup !== undefined && <> {phraseRetour(recup, etiquette, precisionTrajectoire)}</>}
          </>
        }
      >
        {recup !== undefined && <span className="mt-auto border-t border-line pt-2 text-xs font-medium text-ink">{libelleRetour(recup, etiquette)}</span>}
      </Tuile>
      <Tuile
        titre="VaR 95 % sur 1 jour"
        valeur={pourcentSigne(m.var_95, 2)}
        niveau={niveauVar(m.var_95)}
        resume="Un jour sur vingt, la perte dépasse ce seuil"
        explication="Value at Risk : un jour sur vingt, la perte quotidienne dépasse ce seuil. Elle ne dit rien de l'ampleur des pires jours."
      />
    </Cascade>
  );
}

const ICONES_ALERTE = { error: CircleAlert, warning: TriangleAlert, success: CircleCheck, info: Info };
const TONS_ALERTE = {
  error: "border-loss/30 bg-loss-soft text-loss",
  warning: "border-warn/30 bg-warn-soft text-warn",
  success: "border-gain/30 bg-gain-soft text-gain",
  info: "border-line bg-surface-2 text-ink-2",
};

/** Alertes automatiques (drawdown severe, Sharpe negatif...), icone + texte, jamais la couleur seule. */
export function ListeAlertes({ alertes }: { alertes: Alerte[] }) {
  if (alertes.length === 0) return null;
  return (
    <Cascade auDefilement>
      <ul className="flex flex-col gap-2">
        {alertes.map((a) => {
          const Icone = ICONES_ALERTE[a.severite];
          return (
            <LigneCascade key={a.titre} className={`flex gap-3 rounded-tuile border px-4 py-3 text-sm ${TONS_ALERTE[a.severite]}`}>
              <Icone className="mt-0.5 size-4 shrink-0" aria-hidden />
              <span className="text-ink">
                <strong className="font-semibold">{a.titre}.</strong> {a.message}
              </span>
            </LigneCascade>
          );
        })}
      </ul>
    </Cascade>
  );
}
