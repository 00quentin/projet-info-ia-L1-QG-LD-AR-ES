"use client";

import { motion } from "motion/react";
import { CircleAlert, CircleCheck, Info, TriangleAlert } from "lucide-react";
import type { Alerte, Metriques } from "@/lib/api";
import { nombreSigne, pourcent, pourcentSigne } from "@/lib/format";
import { Pastille } from "@/components/ui/Carte";
import { Cascade, ElementCascade, LigneCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { RESSORT } from "@/components/motion/transitions";

export type Niveau = { libelle: string; ton: "gain" | "neutre" | "alerte" | "perte" };

// Memes seuils que core/risk_alerts.py (standards de l'industrie).
export function niveauVolatilite(v: number): Niveau {
  if (v < 15) return { libelle: "Modérée", ton: "gain" };
  if (v < 25) return { libelle: "Normale", ton: "neutre" };
  if (v < 35) return { libelle: "Élevée", ton: "alerte" };
  return { libelle: "Très élevée", ton: "perte" };
}
export function niveauSharpe(s: number, qualite: string): Niveau {
  return { libelle: qualite, ton: s < 0 ? "perte" : s < 1 ? "neutre" : "gain" };
}
export function niveauDrawdown(d: number): Niveau {
  if (d < 10) return { libelle: "Limité", ton: "gain" };
  if (d < 25) return { libelle: "Modéré", ton: "neutre" };
  if (d < 40) return { libelle: "Sévère", ton: "alerte" };
  return { libelle: "Critique", ton: "perte" };
}
export function niveauVar(v: number): Niveau {
  const abs = Math.abs(v);
  if (abs < 2) return { libelle: "Faible", ton: "gain" };
  if (abs < 4) return { libelle: "Modérée", ton: "neutre" };
  return { libelle: "Élevée", ton: "perte" };
}

function Tuile({ titre, valeur, format, niveau, explication }: { titre: string; valeur: number; format: (v: number) => string; niveau: Niveau; explication: string }) {
  return (
    <ElementCascade>
      <motion.div whileHover={{ y: -3 }} transition={RESSORT} className="h-full rounded-xl border border-line bg-surface p-4 transition-shadow hover:shadow-card">
        <div className="flex items-start justify-between gap-2">
          <span className="text-xs font-medium text-muted">{titre}</span>
          <Pastille ton={niveau.ton}>{niveau.libelle}</Pastille>
        </div>
        <NombreAnime valeur={valeur} format={format} className="mt-2 block text-2xl font-semibold tracking-tight" />
        <p className="mt-1.5 text-xs leading-relaxed text-ink-2">{explication}</p>
      </motion.div>
    </ElementCascade>
  );
}

/** Les 4 metriques de risque, chacune avec son niveau et une phrase d'explication. */
export function TuilesRisque({ m, tauxSansRisquePct }: { m: Metriques; tauxSansRisquePct?: number }) {
  const refSharpe = tauxSansRisquePct != null ? ` Calculé au-delà du taux sans risque de ${pourcent(tauxSansRisquePct, 2)} (taux de dépôt BCE).` : "";
  return (
    <Cascade auDefilement className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Tuile titre="Volatilité annualisée" valeur={m.vol_ann} format={(v) => pourcent(v)} niveau={niveauVolatilite(m.vol_ann)} explication="L'ampleur habituelle des variations sur un an. Plus elle est haute, plus le parcours est agité." />
      <Tuile titre="Ratio de Sharpe" valeur={m.sharpe} format={(v) => nombreSigne(v)} niveau={niveauSharpe(m.sharpe, m.qualite_sharpe)} explication={`Le rendement obtenu pour chaque unité de risque prise. Au-dessus de 1, le risque est bien payé.${refSharpe}`} />
      <Tuile titre="Perte maximale (drawdown)" valeur={m.max_dd} format={(v) => `−${pourcent(Math.abs(v))}`} niveau={niveauDrawdown(m.max_dd)} explication="La pire chute entre un sommet et le creux qui suit, en cours de route." />
      <Tuile titre="VaR 95 % sur 1 jour" valeur={m.var_95} format={(v) => pourcentSigne(v, 2)} niveau={niveauVar(m.var_95)} explication="Un jour sur vingt, la perte quotidienne dépasse ce seuil." />
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
            <LigneCascade key={a.titre} className={`flex gap-3 rounded-xl border px-4 py-3 text-sm ${TONS_ALERTE[a.severite]}`}>
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
