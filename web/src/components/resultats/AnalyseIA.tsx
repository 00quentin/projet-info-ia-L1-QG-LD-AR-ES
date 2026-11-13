"use client";

import { motion } from "motion/react";
import { History, ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react";
import type { Conjoncture as TypeConjoncture, ResultatScenario } from "@/lib/api";
import { Conjoncture } from "@/components/resultats/Conjoncture";
import { pourcentSigne } from "@/lib/format";
import { nomCourt } from "@/contenu/actifs";
import { Carte, Pastille, TitreCarte } from "@/components/ui/Carte";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import { Depliable } from "./Depliable";
import { FourchettesIA } from "./FourchettesIA";

// Un statut n'est ni vert ni rouge (couleurs reservees aux gains et pertes) : accent, neutre ou alerte.
const FIABILITES = {
  elevee: { libelle: "Fiabilité élevée", ton: "accent", Icone: ShieldCheck },
  moyenne: { libelle: "Fiabilité moyenne", ton: "neutre", Icone: ShieldQuestion },
  faible: { libelle: "Fiabilité faible", ton: "alerte", Icone: ShieldAlert },
} as const;

const points = (v: number) => pourcentSigne(v, 2).replace(" %", " pt");

/** Ecart entre estimation calibree et libre : < 5 pts = l'histoire confirme, > 15 pts = scenario inedit. */
function tonEcart(ecart: number): "neutre" | "alerte" | "perte" {
  const abs = Math.abs(ecart);
  return abs < 5 ? "neutre" : abs < 15 ? "alerte" : "perte";
}

function CalibreeVsLibre({ s, noms }: { s: ResultatScenario; noms: Map<string, string> }) {
  const a = s.analyse;
  if (!a.chocs_sans_calibration) return null;
  const lignes = Object.keys(a.chocs)
    .map((cle) => {
      const calibree = (a.chocs[cle] ?? 0) * 100;
      const libre = (a.chocs_sans_calibration?.[cle] ?? 0) * 100;
      return { cle, nom: nomCourt(cle, noms.get(cle)), calibree, libre, ecart: libre - calibree };
    })
    .sort((x, y) => Math.abs(y.ecart) - Math.abs(x.ecart));
  const macroLibre = a.macro_sans_calibration;
  return (
    <Depliable libelle="Comment l'IA a calibré son estimation" libelleOuvert="Masquer le détail de la calibration" className="mt-5 border-t border-line pt-4">
      <p className="text-aide leading-relaxed text-ink-2">
        <strong className="font-medium text-ink">Calibrée</strong> : l&apos;IA s&apos;ancre sur des crises passées comparables. <strong className="font-medium text-ink">Libre</strong> : sa projection sans contrainte historique. Un grand écart signale un scénario peu couvert par l&apos;histoire.
      </p>
      {macroLibre && (
        <dl className="mt-3 grid grid-cols-1 gap-3 text-sm min-[420px]:grid-cols-2">
          {[
            ["Inflation", a.inflation, macroLibre.inflation],
            ["Taux directeurs", a.taux_directeurs, macroLibre.taux_directeurs],
          ].map(([nom, c, l]) => (
            <div key={nom as string} className="rounded-tuile bg-surface-2 px-3 py-2.5">
              <dt className="text-xs text-muted">{nom}</dt>
              <dd className="mt-1 flex items-baseline justify-between gap-2 tabular-nums">
                <span>
                  <span className="text-xs text-muted">Calibrée </span>
                  <strong className="font-semibold">{points(c as number)}</strong>
                </span>
                <span>
                  <span className="text-xs text-muted">Libre </span>
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
            {lignes.map((l) => (
              <tr key={l.cle} className="border-t border-line">
                <td className="py-2 pr-3">{l.nom}</td>
                <td className="py-2 text-right">{pourcentSigne(l.calibree)}</td>
                <td className="py-2 text-right text-ink-2">{pourcentSigne(l.libre)}</td>
                <td className="py-2 text-right">
                  <Pastille ton={tonEcart(l.ecart)}>{pourcentSigne(l.ecart).replace(" %", " pts")}</Pastille>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-muted">Écart &lt; 5 pts : l&apos;ancrage historique confirme la projection. Écart &gt; 15 pts : scénario peu couvert par l&apos;histoire.</p>
    </Depliable>
  );
}

export function AnalyseIA({ s, calibration, noms, conjoncture }: { s: ResultatScenario; calibration: boolean; noms: Map<string, string>; conjoncture?: TypeConjoncture }) {
  const a = s.analyse;
  const refs = a.references_historiques.filter((r) => r.evenement);
  const niveau = a.fiabilite?.niveau;
  const fiab = niveau && niveau in FIABILITES ? FIABILITES[niveau as keyof typeof FIABILITES] : undefined;
  return (
    <Carte taille="normale">
      <div className="flex flex-wrap items-start justify-between gap-x-3">
        <TitreCarte>Analyse de l&apos;IA</TitreCarte>
        {calibration && fiab && (
          <Pastille ton={fiab.ton}>
            <fiab.Icone className="size-3.5" aria-hidden />
            {fiab.libelle}
          </Pastille>
        )}
      </div>
      <p className="text-titre leading-relaxed text-ink-2">{a.explication ?? "Analyse non disponible."}</p>
      {conjoncture?.indicateurs.length ? (
        <div className="mt-5 border-t border-line pt-5">
          <Conjoncture conjoncture={conjoncture} compacte />
        </div>
      ) : null}
      <dl className="mt-5 grid grid-cols-2 gap-4 border-t border-line pt-5">
        <div>
          <dt className="text-aide text-muted">Inflation (variation estimée)</dt>
          <dd className="mt-0.5 text-xl font-semibold tabular-nums">{points(a.inflation)}</dd>
        </div>
        <div>
          <dt className="text-aide text-muted">Taux directeurs (variation estimée)</dt>
          <dd className="mt-0.5 text-xl font-semibold tabular-nums">{points(a.taux_directeurs)}</dd>
        </div>
      </dl>
      <FourchettesIA a={a} noms={noms} />
      {calibration && (refs.length > 0 || a.evenement_reference || a.fiabilite?.raison) && (
        <div className="mt-5 border-t border-line pt-5">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <span className="text-aide font-medium text-muted">Précédents historiques utilisés</span>
            {a.evenement_reference && (
              <span className="inline-flex items-center gap-1.5 text-aide text-ink-2">
                <History className="size-3.5 text-muted" aria-hidden />
                Calibré sur : <strong className="font-medium text-ink">{a.evenement_reference}</strong>
              </span>
            )}
          </div>
          {refs.length > 0 && (
            <ul className="mt-3 flex flex-col gap-2">
              {refs.map((r, i) => (
                <li key={r.evenement} className="grid grid-cols-[minmax(0,1fr)_5rem_3rem] items-center gap-3 text-sm sm:grid-cols-[minmax(0,1fr)_6rem_3rem]">
                  <span className="truncate">{r.evenement}</span>
                  <span className="h-1.5 overflow-hidden rounded-full bg-surface-2" aria-hidden>
                    <motion.span
                      className="block h-full origin-left rounded-full bg-accent"
                      style={{ width: `${Math.round((r.poids ?? 0) * 100)}%` }}
                      initial={{ scaleX: 0 }}
                      whileInView={{ scaleX: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: DUREE.donnees, ease: EASE_SORTIE, delay: 0.1 + i * 0.08 }}
                    />
                  </span>
                  <span className="text-right text-ink-2 tabular-nums">{Math.round((r.poids ?? 0) * 100)} %</span>
                </li>
              ))}
            </ul>
          )}
          {a.fiabilite?.raison && <p className="mt-3 text-aide leading-relaxed text-muted">{a.fiabilite.raison}</p>}
        </div>
      )}
      {calibration && <CalibreeVsLibre s={s} noms={noms} />}
    </Carte>
  );
}
