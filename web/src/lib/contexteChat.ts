// Resume du dernier resultat affiche (simulation, comparaison ou backtest), transmis
// a l'analyste IA pour qu'on puisse lui demander de l'expliquer. Garde le temps de la
// session du navigateur (sessionStorage), jamais sur le serveur.

import { useSyncExternalStore } from "react";
import type { ReponseBacktest, ResultatScenario } from "@/lib/api";
import { euros, nombreSigne, pourcent, pourcentSigne } from "@/lib/format";

export type ContexteChat = { titre: string; texte: string };

const CLE = "qt-chat-contexte";
const EVENEMENT = "qt-chat-contexte";
const LONGUEUR_MAX = 3800;
const NB_ACTIFS_CITES = 8;

let cache: ContexteChat | null | undefined;

function lire(): ContexteChat | null {
  if (cache !== undefined) return cache;
  try {
    const brut = sessionStorage.getItem(CLE);
    cache = brut ? (JSON.parse(brut) as ContexteChat) : null;
  } catch {
    cache = null;
  }
  return cache;
}

function ecrire(c: ContexteChat | null) {
  cache = c;
  try {
    if (c) sessionStorage.setItem(CLE, JSON.stringify(c));
    else sessionStorage.removeItem(CLE);
  } catch {
    /* stockage bloque : le contexte vit le temps de la page */
  }
  window.dispatchEvent(new Event(EVENEMENT));
}

export const definirContexteChat = (c: ContexteChat) => ecrire({ titre: c.titre, texte: c.texte.slice(0, LONGUEUR_MAX) });
export const retirerContexteChat = () => ecrire(null);

function abonner(rappel: () => void) {
  window.addEventListener(EVENEMENT, rappel);
  return () => window.removeEventListener(EVENEMENT, rappel);
}

export function useContexteChat(): ContexteChat | null {
  return useSyncExternalStore(abonner, lire, () => null);
}

function lignesPortefeuille(capital: number, valeurFinale: number, perf: number, m: { vol_ann: number; sharpe: number; max_dd: number; var_95: number; proba_perte?: number }) {
  return [
    `Capital : ${euros(capital)} → valeur finale ${euros(valeurFinale)} (${pourcentSigne(perf)}).`,
    `Risque : volatilité ${pourcent(m.vol_ann)}, Sharpe ${nombreSigne(m.sharpe)}, perte maximale −${pourcent(Math.abs(m.max_dd))}, VaR 95 % ${pourcentSigne(m.var_95, 2)}` +
      (m.proba_perte != null ? `, probabilité de perte ${pourcent(m.proba_perte, 0)}.` : "."),
  ];
}

function lignesActifs(actifs: { nom: string; performance_pct: number }[]) {
  const tries = [...actifs].sort((a, b) => b.performance_pct - a.performance_pct);
  const cites = tries.length > NB_ACTIFS_CITES ? [...tries.slice(0, NB_ACTIFS_CITES / 2), ...tries.slice(-NB_ACTIFS_CITES / 2)] : tries;
  return `Performance par actif : ${cites.map((a) => `${a.nom} ${pourcentSigne(a.performance_pct)}`).join(" ; ")}.`;
}

/** Contexte d'une ou plusieurs simulations prospectives. */
export function contexteSimulation(scenarios: ResultatScenario[], profil: string, duree: number): ContexteChat {
  const blocs = scenarios.map((s) => {
    const pf = s.portefeuille;
    return [
      `${scenarios.length > 1 ? `Scénario ${s.label}` : "Scénario"} : « ${s.scenario} » (simulation sur ${duree} jours de bourse, profil ${profil}).`,
      ...lignesPortefeuille(pf.capital, pf.valeur_finale, pf.performance_pct, s.metriques),
      lignesActifs(s.actifs),
      s.analyse.evenement_reference ? `Précédent historique retenu par l'IA : ${s.analyse.evenement_reference}.` : "",
    ]
      .filter(Boolean)
      .join("\n");
  });
  return {
    titre: scenarios.length > 1 ? `Comparaison de ${scenarios.length} scénarios` : "Votre dernière simulation",
    texte: blocs.join("\n\n"),
  };
}

/** Contexte d'un backtest historique. */
export function contexteBacktest(r: ReponseBacktest, libelle: string): ContexteChat {
  const pf = r.portefeuille;
  return {
    titre: `Backtest : ${libelle}`,
    texte: [
      `Backtest historique « ${libelle} », du ${r.date_debut} au ${r.date_fin} (${r.dates.length} séances, vrais cours), profil ${r.parametres.profil}.`,
      ...lignesPortefeuille(pf.capital, pf.valeur_finale, pf.performance_pct, r.metriques),
      ...r.benchmarks.map((b) => `${b.nom} sur la même période : ${pourcentSigne((b.valeurs[b.valeurs.length - 1] / b.valeurs[0] - 1) * 100)}.`),
      lignesActifs(r.actifs),
      r.actifs_indisponibles.length ? `Actifs non cotés à l'époque : ${r.actifs_indisponibles.map((a) => a.nom).join(", ")}.` : "",
    ]
      .filter(Boolean)
      .join("\n"),
  };
}
