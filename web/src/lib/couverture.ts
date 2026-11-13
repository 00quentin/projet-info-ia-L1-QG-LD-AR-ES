// « Protéger mon portefeuille » : types et appel de POST /api/couverture (miroir de api/couverture.py).

import { API_URL, ErreurApi, type ParametresSimulation, type ResultatScenario } from "@/lib/api";

const PREFIXE_PERSO = "PERSO_";

/** Ce que le site renvoie de la simulation affichée : l'API ne relance pas l'analyse de l'IA. */
export type DemandeCouverture = {
  scenario: string;
  /** Choc estimé par l'IA sur l'horizon, en décimal (−0,2 = −20 %). */
  chocs: Record<string, number>;
  /** Répartition actuelle, en fractions de somme 1. */
  poids: Record<string, number>;
  capital: number;
  duree: number;
  modele: string;
  prix_reels: boolean;
  convertir_eur: boolean;
  tickers_perso: string[];
};

export type MetriquesCouverture = {
  /** Valeur finale médiane des trajectoires. */
  valeur_finale: number;
  performance_pct: number;
  max_dd: number;
  vol_ann: number;
  var_95: number;
  proba_perte: number;
  valeur_p5: number;
  valeur_p95: number;
  sharpe: number;
};

export type PortefeuilleCouverture = {
  /** Pourcentages entiers de somme 100. */
  poids: Record<string, number>;
  metriques: MetriquesCouverture;
  /** Trajectoire médiane jour par jour, et fourchette 5 %–95 %. */
  valeurs: number[];
  valeurs_bas: number[];
  valeurs_haut: number[];
};

export type ChangementPoids = {
  cle: string;
  nom: string;
  avant_pct: number;
  apres_pct: number;
  ecart_pct: number;
  choc_pct: number;
  volatilite_pct: number;
  correlation: number;
  /** Une phrase : rédigée par l'IA, ou calculée si l'IA n'a pas répondu. */
  justification: string;
  justification_ia: boolean;
};

export type ReponseCouverture = {
  scenario: string;
  capital: number;
  duree: number;
  /** Aucune répartition nettement plus résistante trouvée : rien ne change. */
  deja_protege: boolean;
  /** Nouvelle répartition en % entiers (somme 100), prête pour le profil Personnalisé. */
  allocations: Record<string, number>;
  avant: PortefeuilleCouverture;
  apres: PortefeuilleCouverture;
  changements: ChangementPoids[];
  lignes: { cle: string; nom: string; avant_pct: number; apres_pct: number; choc_pct: number }[];
  synthese: string | null;
  justifications_ia: boolean;
  methode: {
    nb_trajectoires_recherche: number;
    nb_trajectoires_verification: number;
    nb_portefeuilles_testes: number;
    nb_etapes: number;
    pas_transfert_pct: number;
    poids_max_ligne_pct: number;
    ecart_max_ligne_pct: number;
    rotation_max_pct: number;
    rotation_pct: number;
  };
};

/** Demande de protection construite à partir d'un scénario simulé. */
export function demandeCouverture(s: ResultatScenario, p: ParametresSimulation): DemandeCouverture {
  // Actif sans choc renvoyé : le moteur l'a simulé avec un choc nul, on fait de même.
  const chocs = Object.fromEntries(s.actifs.map((a) => [a.cle, Number.isFinite(s.analyse.chocs[a.cle]) ? s.analyse.chocs[a.cle] : 0]));
  for (const a of s.allocations) chocs[a.cle] ??= Number.isFinite(s.analyse.chocs[a.cle]) ? s.analyse.chocs[a.cle] : 0;
  return {
    scenario: s.scenario,
    chocs,
    poids: Object.fromEntries(s.allocations.map((a) => [a.cle, a.poids])),
    capital: s.portefeuille.capital,
    duree: p.duree,
    modele: p.modele,
    prix_reels: p.prix_reels,
    convertir_eur: p.convertir_eur,
    tickers_perso: Object.keys(chocs)
      .filter((cle) => cle.startsWith(PREFIXE_PERSO))
      .map((cle) => cle.slice(PREFIXE_PERSO.length)),
  };
}

/** Calcule la protection (2 à 6 s : recherche, re-simulation, puis rédaction par l'IA). */
export async function demanderCouverture(demande: DemandeCouverture, signal?: AbortSignal): Promise<ReponseCouverture> {
  let reponse: Response;
  try {
    reponse = await fetch(`${API_URL}/api/couverture`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(demande),
      signal,
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ErreurApi("Impossible de joindre le serveur. Vérifiez votre connexion puis réessayez.", 0);
  }
  if (!reponse.ok) {
    let detail = "La protection n'a pas pu être calculée. Réessayez dans un instant.";
    try {
      const corps = await reponse.json();
      if (typeof corps.detail === "string") detail = corps.detail;
      else if (Array.isArray(corps.detail) && corps.detail[0]?.msg) detail = String(corps.detail[0].msg).replace(/^Value error, /, "");
    } catch {
      /* corps non JSON : message generique */
    }
    throw new ErreurApi(detail, reponse.status);
  }
  return reponse.json() as Promise<ReponseCouverture>;
}
