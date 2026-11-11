"use client";

import { motion } from "motion/react";
import type { ResultatScenario } from "@/lib/api";
import { pourcentSigne } from "@/lib/format";
import { Carte, Pastille, TitreCarte } from "@/components/ui/Carte";
import { EASE_SORTIE } from "@/components/motion/transitions";

const FIABILITES: Record<string, { libelle: string; ton: "gain" | "alerte" | "perte" }> = {
  elevee: { libelle: "Fiabilité élevée", ton: "gain" },
  moyenne: { libelle: "Fiabilité moyenne", ton: "alerte" },
  faible: { libelle: "Fiabilité faible", ton: "perte" },
};

const points = (v: number) => pourcentSigne(v, 2).replace(" %", " pt");

/** Ecart entre estimation calibree et libre : < 5 pts = l'histoire confirme, > 15 pts = scenario inedit. */
function tonEcart(ecart: number): "gain" | "alerte" | "perte" {
  const abs = Math.abs(ecart);
  return abs < 5 ? "gain" : abs < 15 ? "alerte" : "perte";
}

function CalibreeVsLibre({ s, noms }: { s: ResultatScenario; noms: Map<string, string> }) {
  const a = s.analyse;
  if (!a.chocs_sans_calibration) return null;
  const lignes = Object.keys(a.chocs)
    .map((cle) => {
      const calibree = (a.chocs[cle] ?? 0) * 100;
      const libre = (a.chocs_sans_calibration?.[cle] ?? 0) * 100;
      return { cle, nom: noms.get(cle) ?? cle, calibree, libre, ecart: libre - calibree };
    })
    .sort((x, y) => Math.abs(y.ecart) - Math.abs(x.ecart));
  const macroLibre = a.macro_sans_calibration;
  return (
    <div className="mt-5 border-t border-line pt-5">
      <h4 className="text-sm font-semibold">Calibrée ou libre ?</h4>
      <p className="mt-1 text-xs leading-relaxed text-ink-2">
        <strong className="font-medium text-ink">Calibrée</strong> : l&apos;IA s&apos;ancre sur des crises passées comparables. <strong className="font-medium text-ink">Libre</strong> : sa projection sans contrainte historique. Un grand écart signale un scénario peu couvert par l&apos;histoire.
      </p>
      {macroLibre && (
        <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
          {[
            ["Inflation", a.inflation, macroLibre.inflation],
            ["Taux directeurs", a.taux_directeurs, macroLibre.taux_directeurs],
          ].map(([nom, c, l]) => (
            <div key={nom as string} className="rounded-xl bg-surface-2 px-3 py-2.5">
              <dt className="text-xs text-muted">{nom}</dt>
              <dd className="mt-1 flex items-baseline justify-between gap-2 tabular-nums">
                <span>
                  <span className="text-[11px] text-muted">Calibrée </span>
                  <strong className="font-semibold">{points(c as number)}</strong>
                </span>
                <span>
                  <span className="text-[11px] text-muted">Libre </span>
                  <strong className="font-semibold">{points(l as number)}</strong>
                </span>
              </dd>
            </div>
          ))}
        </dl>
      )}
      <div className="mt-3 overflow-x-auto">
        <table className="w-full min-w-[26rem] text-sm tabular-nums">
          <thead className="text-xs text-muted">
            <tr>
              <th className="pb-2 text-left font-medium">Actif</th>
              <th className="pb-2 text-right font-medium">Calibrée</th>
              <th className="pb-2 text-right font-medium">Libre</th>
              <th className="pb-2 text-right font-medium">Écart</th>
            </tr>
          </thead>
          <tbody>
            {lignes.map((l, i) => (
              <motion.tr
                key={l.cle}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.03 }}
                className="border-t border-line"
              >
                <td className="py-2 pr-3">{l.nom}</td>
                <td className="py-2 text-right">{pourcentSigne(l.calibree)}</td>
                <td className="py-2 text-right text-ink-2">{pourcentSigne(l.libre)}</td>
                <td className="py-2 text-right">
                  <Pastille ton={tonEcart(l.ecart)}>{pourcentSigne(l.ecart).replace(" %", " pts")}</Pastille>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-muted">Écart &lt; 5 pts : l&apos;ancrage historique confirme la projection. Écart &gt; 15 pts : scénario peu couvert par l&apos;histoire.</p>
    </div>
  );
}

export function AnalyseIA({ s, calibration, noms }: { s: ResultatScenario; calibration: boolean; noms: Map<string, string> }) {
  const a = s.analyse;
  const refs = a.references_historiques.filter((r) => r.evenement);
  const fiab = a.fiabilite?.niveau ? FIABILITES[a.fiabilite.niveau] : undefined;
  return (
    <Carte className="p-6">
      <TitreCarte>Analyse de l&apos;IA</TitreCarte>
      <p className="text-[15px] leading-relaxed text-ink-2">{a.explication ?? "Analyse non disponible."}</p>
      <dl className="mt-5 grid grid-cols-2 gap-4 border-t border-line pt-5">
        <div>
          <dt className="text-xs text-muted">Inflation (variation estimée)</dt>
          <dd className="mt-0.5 text-xl font-semibold">{points(a.inflation)}</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Taux directeurs (variation estimée)</dt>
          <dd className="mt-0.5 text-xl font-semibold">{points(a.taux_directeurs)}</dd>
        </div>
      </dl>
      {calibration && (refs.length > 0 || fiab) && (
        <div className="mt-5 border-t border-line pt-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-medium text-muted">Précédents historiques utilisés</span>
            {fiab && <Pastille ton={fiab.ton}>{fiab.libelle}</Pastille>}
          </div>
          {refs.length > 0 && (
            <ul className="mt-3 flex flex-col gap-2">
              {refs.map((r, i) => (
                <li key={r.evenement} className="grid grid-cols-[1fr_6rem_3rem] items-center gap-3 text-sm">
                  <span className="truncate">{r.evenement}</span>
                  <span className="h-1.5 overflow-hidden rounded-full bg-surface-2" aria-hidden>
                    <motion.span
                      className="block h-full origin-left rounded-full bg-accent"
                      style={{ width: `${Math.round((r.poids ?? 0) * 100)}%` }}
                      initial={{ scaleX: 0 }}
                      whileInView={{ scaleX: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.7, ease: EASE_SORTIE, delay: 0.1 + i * 0.08 }}
                    />
                  </span>
                  <span className="text-right text-ink-2 tabular-nums">{Math.round((r.poids ?? 0) * 100)} %</span>
                </li>
              ))}
            </ul>
          )}
          {a.fiabilite?.raison && <p className="mt-3 text-xs leading-relaxed text-muted">{a.fiabilite.raison}</p>}
        </div>
      )}
      {calibration && <CalibreeVsLibre s={s} noms={noms} />}
    </Carte>
  );
}
