// Client de l'API Quant Terminal (FastAPI). Les types refletent api/services.py.

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export type Actif = { cle: string; nom: string; devise: string | null; ticker: string | null; par_defaut: boolean };
export type Categorie = { nom: string; actifs: Actif[] };
export type Profil = { nom: string; poids: Record<string, number> | null };
export type EvenementHistorique = { nom: string; debut: string; fin: string; description: string };
export type Bornes = { min: number; max: number; defaut: number; pas: number };

export type Catalogue = {
  categories: Categorie[];
  profils: Profil[];
  scenarios_rapides: { titre: string; texte: string }[];
  scenarios_par_defaut: string[];
  labels_scenarios: string[];
  modeles: string[];
  evenements_historiques: EvenementHistorique[];
  horizon: Bornes;
  capital: Bornes;
  nb_simulations_monte_carlo: number;
  benchmarks: { cle: string; nom: string }[];
};

export type CoursMarche = {
  cle: string; nom: string; categorie: string; devise: string | null;
  prix: number; variation_pct: number; sparkline: number[];
  source: "yahoo" | "snapshot" | "secours"; date: string | null;
};
export type Marches = { actifs: CoursMarche[]; en_direct: boolean; date: string | null; recharge?: boolean };

export type IndicateurConjoncture = { cle: string; nom: string; valeur: number; unite: string; date: string; source: string };
/** Taux et inflation du moment (FRED). `indicateurs` est vide si FRED est injoignable. */
export type Conjoncture = { indicateurs: IndicateurConjoncture[]; date: string | null; taux_sans_risque_pct?: number };

export type Metriques = {
  vol_ann: number; sharpe: number; max_dd: number; var_95: number; qualite_sharpe: string;
  valeur_p5?: number; valeur_mediane?: number; valeur_p95?: number; proba_perte?: number;
};
export type Alerte = { severite: "info" | "success" | "warning" | "error"; titre: string; message: string; metrique: string };
export type LigneAllocation = { cle: string; nom: string; categorie: string; poids: number; investi: number; final: number; performance_pct: number };
export type SerieActif = { cle: string; nom: string; categorie: string; performance_pct: number; prix: number[]; prix_bas?: number[]; prix_haut?: number[] };
export type Portefeuille = { capital: number; valeur_finale: number; performance_pct: number; valeurs: number[]; valeurs_bas?: number[]; valeurs_haut?: number[] };
export type Benchmark = { cle: string; nom: string; valeurs: number[] };

/** Doute de l'IA sur un actif : choc bas ≤ central ≤ haut (décimaux, -0.15 = -15 %). */
export type FourchetteChoc = { bas: number; central: number; haut: number };

export type Analyse = {
  explication: string | null; inflation: number; taux_directeurs: number;
  evenement_reference: string | null;
  references_historiques: { evenement?: string; poids?: number }[];
  fiabilite: { niveau?: string; raison?: string } | null;
  chocs: Record<string, number>;
  /** Fourchette de l'IA par actif ; en Monte-Carlo, chaque trajectoire tire son choc dedans. Absente des anciens résultats. */
  fourchettes?: Record<string, FourchetteChoc>;
  chocs_sans_calibration: Record<string, number> | null;
  macro_sans_calibration: { inflation: number; taux_directeurs: number } | null;
};

export type ResultatScenario = {
  label: string; scenario: string; erreur: string | null;
  analyse: Analyse; portefeuille: Portefeuille; metriques: Metriques; alertes: Alerte[];
  allocations: LigneAllocation[]; actifs: SerieActif[]; benchmarks: Benchmark[]; converti_eur: boolean;
};
export type ScenarioEnErreur = { label: string; scenario: string; erreur: string };

export type ParametresSimulation = {
  profil: string; capital: number; duree: number; modele: string; monte_carlo: boolean;
  prix_reels: boolean; calibration: boolean; convertir_eur: boolean; nb_actifs: number; nb_simulations: number;
  /** Taux sans risque utilise pour le ratio de Sharpe (taux de depot BCE). */
  taux_sans_risque_pct?: number;
};
export type ReponseSimulation = {
  date: string; parametres: ParametresSimulation;
  prix_de_secours: { cle: string; nom: string; date: string }[];
  conjoncture?: Conjoncture;
  scenarios: (ResultatScenario | ScenarioEnErreur)[];
};

export type DemandePortefeuille = {
  actifs: string[]; profil: string; allocations: Record<string, number>;
  capital: number; tickers_perso: string[]; convertir_eur: boolean;
};

export type DemandeSimulation = DemandePortefeuille & {
  scenarios: string[]; duree: number; modele: string; monte_carlo: boolean; prix_reels: boolean; calibration: boolean;
};

/** Evenement du catalogue, ou periode libre (date_debut + date_fin au format AAAA-MM-JJ). */
export type DemandeBacktest = DemandePortefeuille & {
  evenement?: string | null; date_debut?: string | null; date_fin?: string | null;
};

export type ReponseBacktest = {
  date: string;
  evenement: string | null;
  description: string | null;
  date_debut: string;
  date_fin: string;
  /** Une date (AAAA-MM-JJ) par point des series ci-dessous. */
  dates: string[];
  parametres: { profil: string; capital: number; duree: number; convertir_eur: boolean; nb_actifs: number; taux_sans_risque_pct?: number };
  /** Actifs coches mais qui ne cotaient pas encore au debut de la periode. */
  actifs_indisponibles: { cle: string; nom: string }[];
  portefeuille: Portefeuille; metriques: Metriques; alertes: Alerte[];
  allocations: LigneAllocation[]; actifs: SerieActif[]; benchmarks: Benchmark[]; converti_eur: boolean;
};

export type ActifPerso = { cle: string; ticker: string; nom: string; devise: string | null; prix: number; volatilite: number };

export type MessageChat = { role: "user" | "assistant"; content: string };

/** Contenu du rapport PDF (miroir de DemandeRapport dans api/modeles.py). */
export type DemandeRapport = {
  type_rapport: "Simulation" | "Backtest";
  scenario: string; profil: string; capital: number; valeur_finale: number; duree: number;
  monte_carlo: boolean; prix_reels: boolean; calibration: boolean; nb_actifs: number;
  inflation: number; taux_directeurs: number; explication: string; evenement_reference: string | null;
  performances: { nom: string; performance: number }[];
  allocations: { nom: string; poids: number; investi: number; final: number; rendement: number }[];
  vol_ann: number; sharpe: number; max_dd: number; var_95: number;
  avec_analyse_ia: boolean;
};

export function estReussi(s: ResultatScenario | ScenarioEnErreur): s is ResultatScenario {
  return s.erreur === null;
}

export class ErreurApi extends Error {
  constructor(message: string, public statut: number) {
    super(message);
  }
}

async function appeler<T>(chemin: string, init?: RequestInit): Promise<T> {
  let reponse: Response;
  try {
    reponse = await fetch(`${API_URL}${chemin}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ErreurApi("Impossible de joindre le serveur. Vérifiez votre connexion puis réessayez.", 0);
  }
  if (!reponse.ok) {
    let detail = "Une erreur est survenue. Réessayez dans un instant.";
    try {
      const corps = await reponse.json();
      if (typeof corps.detail === "string") detail = corps.detail;
      else if (Array.isArray(corps.detail) && corps.detail[0]?.msg) detail = String(corps.detail[0].msg).replace(/^Value error, /, "");
    } catch {
      /* corps non JSON : on garde le message generique */
    }
    throw new ErreurApi(detail, reponse.status);
  }
  return reponse.json() as Promise<T>;
}

export const lireCatalogue = () => appeler<Catalogue>("/api/catalogue");
/** `rafraichir` recharge les prix depuis Yahoo (le serveur l'accepte au plus toutes les 5 minutes). */
export const lireMarches = (rafraichir = false) => appeler<Marches>(`/api/marches${rafraichir ? "?rafraichir=true" : ""}`);

let marchesEnCours: Promise<Marches> | null = null;
/** Cours partages entre composants (bandeau, selecteur d'actifs) : une seule requete par page. */
export function lireMarchesPartages(): Promise<Marches> {
  marchesEnCours ??= lireMarches().catch((e) => {
    marchesEnCours = null; // on pourra retenter
    throw e;
  });
  return marchesEnCours;
}
export const lireConjoncture = () => appeler<Conjoncture>("/api/conjoncture");
export const lancerSimulation = (demande: DemandeSimulation) =>
  appeler<ReponseSimulation>("/api/simulations", { method: "POST", body: JSON.stringify(demande) });
export const lancerBacktest = (demande: DemandeBacktest) =>
  appeler<ReponseBacktest>("/api/backtests", { method: "POST", body: JSON.stringify(demande) });
export const lireActifPerso = (ticker: string) => appeler<ActifPerso>(`/api/actifs-perso/${encodeURIComponent(ticker.trim())}`);
/** `contexte` : resume du resultat affiche, pour que l'analyste puisse l'expliquer. */
export const discuter = (messages: MessageChat[], contexte?: string | null) =>
  appeler<{ reponse: string }>("/api/chat", { method: "POST", body: JSON.stringify(contexte ? { messages, contexte } : { messages }) });

/** Genere le rapport PDF (15-30 s avec l'analyse IA) et renvoie le fichier. */
export async function telechargerRapportPdf(demande: DemandeRapport): Promise<Blob> {
  let reponse: Response;
  try {
    reponse = await fetch(`${API_URL}/api/rapports/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(demande),
    });
  } catch {
    throw new ErreurApi("Impossible de joindre le serveur. Vérifiez votre connexion puis réessayez.", 0);
  }
  if (!reponse.ok) {
    let detail = "Le rapport n'a pas pu être généré.";
    try {
      const corps = await reponse.json();
      if (typeof corps.detail === "string") detail = corps.detail;
    } catch {
      /* corps non JSON */
    }
    throw new ErreurApi(detail, reponse.status);
  }
  return reponse.blob();
}
