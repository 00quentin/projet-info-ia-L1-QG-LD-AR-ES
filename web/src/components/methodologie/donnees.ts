// Donnees de la page Methodologie : miroir des reglages du moteur Python.
// A tenir a jour avec config.py (simulation, IA), schemas.py (BORNES_ACTIFS) et market_data.py (caches).

export const PARAMETRES = {
  nbSimulations: 1000, // NB_SIMULATIONS_MONTE_CARLO
  cheminsConserves: 400, // NB_CHEMINS_CONSERVES
  joursVolatilite: 252, // get_volatilites_historiques(jours=252)
  anneesCorrelation: 2, // FENETRE_CALIBRATION_JOURS = 730
  perteMaxQuotidiennePct: 50, // PERTE_MAX_QUOTIDIENNE = 0.5
  horizonMin: 30, // HORIZON_MIN
  horizonMax: 250, // HORIZON_MAX
  horizonDefaut: 100, // HORIZON_DEFAUT
  tauxSansRisqueSecoursPct: 2, // TAUX_SANS_RISQUE_ANNUEL = 0.02
  // Modele "Crises reelles"
  blocBootstrapSeances: 5, // BOOTSTRAP_TAILLE_BLOC
  minSeancesBootstrap: 120, // BOOTSTRAP_MIN_SEANCES
  studentDegresLiberte: 4, // STUDENT_DEGRES_LIBERTE
  // Modele "Emballement"
  autocorrelation: 0.2, // MOMENTUM_AUTOCORRELATION
  accelerationPct: 50, // MOMENTUM_ACCELERATION = 0.5
  // Profil de crise (modeles Classique et Crises reelles)
  criseCreuxPctHorizon: 20, // CRISE_FRACTION_CREUX = 0.2
  criseDepassementPct: 30, // CRISE_DEPASSEMENT = 0.3
  // Fourchette bas / central / haut de l'IA (Monte-Carlo)
  incertitudePartCommunePct: 80, // INCERTITUDE_IA_CORRELATION = 0.8
  // Recalage de la fourchette sur les crises passees (schemas.elargir_fourchette)
  fourchetteAggravation: 1.75, // FOURCHETTE_ELARGISSEMENT_AGGRAVATION
  fourchetteAttenuation: 1.25, // FOURCHETTE_ELARGISSEMENT_ATTENUATION
  fourchetteDemiLargeurMinPct: 15, // FOURCHETTE_DEMI_LARGEUR_MIN = 0.15 (part de l'amplitude des bornes)
  modeleIa: "GPT-6.1 Terra", // IA_ANALYSE (gpt-6.1-terra)
  modeleIaSecours: "GPT-5.4 mini", // IA_ANALYSE_SECOURS (gpt-5.4-mini)
};

/** Bornes hors actifs (schemas.py) : [min, max]. */
export const BORNES_AUTRES = {
  inflationPoints: [-10, 30], // ChocsMacro.inflation : Field(ge=-10.0, le=30.0)
  tauxDirecteursPoints: [-5, 10], // ChocsMacro.taux_directeurs : Field(ge=-5.0, le=10.0)
  actifPersoPct: [-80, 200], // _BORNE_GENERIQUE_CUSTOM = (-0.80, 2.00)
} as const;

/** Ordre de grandeur pedagogique du profil de crise : choc final -> point extreme (meme calcul que simulation.profil_choc, en log). */
export function extremeDeCrise(chocFinal: number): number {
  return Math.expm1((1 + PARAMETRES.criseDepassementPct / 100) * Math.log1p(chocFinal));
}

export const SOURCES = [
  { nom: "Yahoo Finance", usage: "Dernier cours de clôture, volatilités (1 an de séances), corrélations (2 ans), cours historiques du backtest", fraicheur: "Cours : 1 h · historiques : 24 h" },
  { nom: "BCE", usage: "Taux de change de référence officiels, jour par jour depuis 1999 (conversion en euros du backtest)", fraicheur: "24 h (publication quotidienne)" },
  { nom: "FRED (Fed de Saint-Louis)", usage: "Taux Fed et BCE, taux à 10 ans États-Unis et Allemagne, inflation États-Unis et zone euro ; taux sans risque du Sharpe", fraicheur: "6 h" },
  { nom: "OpenAI", usage: "Estimation du choc de chaque actif (bas, central, haut), analyste du chat, commentaire du rapport PDF", fraicheur: "À chaque demande" },
];

const P = PARAMETRES;

export const MODELES = [
  {
    nom: "Classique",
    nomMoteur: "Probabiliste (Réaliste)",
    description:
      "Rendements quotidiens gaussiens et corrélés : le mouvement brownien géométrique des manuels de finance. Le choc suit un profil de crise : rapide, il dépasse sa cible puis se résorbe en partie.",
  },
  {
    nom: "Crises réelles",
    nomMoteur: "Historique (Chocs violents)",
    description: `Rejoue des blocs de ${P.blocBootstrapSeances} vraies séances passées, tous actifs ensemble : queues épaisses et co-mouvements réels. Sans ${P.minSeancesBootstrap} séances d'historique, une loi de Student à ${P.studentDegresLiberte} degrés de liberté prend le relais. Même profil de crise que le modèle Classique.`,
  },
  {
    nom: "Emballement",
    nomMoteur: "Machine Learning (Tendance)",
    description: `Rendements autocorrélés (${P.autocorrelation.toLocaleString("fr-FR")}) et choc qui s'accélère dans le temps (+${P.accelerationPct} % de vitesse en fin d'horizon) : la tendance s'auto-entretient, comme dans une bulle ou une panique.`,
  },
];

/** [cle, pire choc, meilleur choc] en decimal (schemas.py, BORNES_ACTIFS). */
export const BORNES_IA: [string, number, number][] = [
  ["S&P 500", -0.55, 0.45],
  ["NASDAQ", -0.6, 0.55],
  ["CAC 40", -0.55, 0.45],
  ["MSCI_World", -0.5, 0.45],
  ["Emerging_Markets", -0.6, 0.55],
  ["Bons_Tresor_US_10Y", -0.25, 0.2],
  ["Bund_10Y", -0.2, 0.2],
  ["OAT_10Y", -0.2, 0.2],
  ["JGB_10Y", -0.15, 0.15],
  ["Gilt_10Y", -0.2, 0.2],
  ["EUR_USD", -0.2, 0.2],
  ["Dollar_Index", -0.2, 0.2],
  ["VIX", -0.5, 5],
  ["Or", -0.25, 0.6],
  ["Argent", -0.3, 0.7],
  ["Petrole", -0.7, 1],
  ["Cuivre", -0.4, 0.5],
  ["ETF_Terres_Rares", -0.4, 0.7],
  ["ETF_Defense", -0.3, 0.5],
  ["Bitcoin", -0.8, 3],
  ["Ethereum", -0.8, 3.5],
  ["XRP", -0.85, 4],
  ["Solana", -0.85, 4],
];
