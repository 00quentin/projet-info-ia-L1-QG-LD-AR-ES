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
export type Marches = { actifs: CoursMarche[]; en_direct: boolean; date: string | null };

export type Metriques = {
  vol_ann: number; sharpe: number; max_dd: number; var_95: number; qualite_sharpe: string;
  valeur_p5?: number; valeur_mediane?: number; valeur_p95?: number; proba_perte?: number;
};
export type Alerte = { severite: "info" | "success" | "warning" | "error"; titre: string; message: string; metrique: string };
export type LigneAllocation = { cle: string; nom: string; categorie: string; poids: number; investi: number; final: number; performance_pct: number };
export type SerieActif = { cle: string; nom: string; categorie: string; performance_pct: number; prix: number[]; prix_bas?: number[]; prix_haut?: number[] };
export type Portefeuille = { capital: number; valeur_finale: number; performance_pct: number; valeurs: number[]; valeurs_bas?: number[]; valeurs_haut?: number[] };
export type Benchmark = { cle: string; nom: string; valeurs: number[] };

export type Analyse = {
  explication: string | null; inflation: number; taux_directeurs: number;
  evenement_reference: string | null;
  references_historiques: { evenement?: string; poids?: number }[];
  fiabilite: { niveau?: string; raison?: string } | null;
  chocs: Record<string, number>;
  chocs_sans_calibration: Record<string, number> | null;
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
};
export type ReponseSimulation = {
  date: string; parametres: ParametresSimulation;
  prix_de_secours: { cle: string; nom: string; date: string }[];
  scenarios: (ResultatScenario | ScenarioEnErreur)[];
};

export type DemandeSimulation = {
  scenarios: string[]; actifs: string[]; profil: string; allocations: Record<string, number>;
  capital: number; tickers_perso: string[]; convertir_eur: boolean;
  duree: number; modele: string; monte_carlo: boolean; prix_reels: boolean; calibration: boolean;
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
export const lireMarches = () => appeler<Marches>("/api/marches");
export const lancerSimulation = (demande: DemandeSimulation) =>
  appeler<ReponseSimulation>("/api/simulations", { method: "POST", body: JSON.stringify(demande) });
