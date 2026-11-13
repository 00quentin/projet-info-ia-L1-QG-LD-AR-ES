// Donnees de la page Methodologie : miroir des reglages du moteur Python.
// A tenir a jour avec config.py (simulation, IA), schemas.py (BORNES_ACTIFS) et market_data.py (caches).

export const PARAMETRES = {
  nbSimulations: 1000, // NB_SIMULATIONS_MONTE_CARLO
  cheminsConserves: 400, // NB_CHEMINS_CONSERVES
  joursVolatilite: 252, // get_volatilites_historiques(jours=252)
  anneesCorrelation: 2, // FENETRE_CALIBRATION_JOURS = 730
  perteMaxQuotidiennePct: 50, // PERTE_MAX_QUOTIDIENNE
  modeleIa: "GPT-6.1", // IA_ANALYSE
  modeleIaSecours: "GPT-5.4 mini", // IA_ANALYSE_SECOURS
};

export const SOURCES = [
  { nom: "Yahoo Finance", usage: "Dernier cours de clôture, volatilités (1 an de séances), corrélations (2 ans), cours historiques du backtest", fraicheur: "Cours : 1 h · historiques : 24 h" },
  { nom: "BCE", usage: "Taux de change de référence officiels, jour par jour depuis 1999 (conversion en euros du backtest)", fraicheur: "24 h (publication quotidienne)" },
  { nom: "FRED (Fed de Saint-Louis)", usage: "Taux Fed et BCE, taux à 10 ans États-Unis et Allemagne, inflation États-Unis et zone euro ; taux sans risque du Sharpe", fraicheur: "6 h" },
  { nom: "OpenAI", usage: "Estimation du choc de chaque actif, analyste du chat, commentaire du rapport PDF", fraicheur: "À chaque demande" },
];

export const MODELES = [
  {
    nom: "Classique",
    nomMoteur: "Probabiliste (Réaliste)",
    description: "Rendements quotidiens gaussiens et corrélés : le mouvement brownien géométrique des manuels de finance.",
  },
  {
    nom: "Crises réelles",
    nomMoteur: "Historique (Chocs violents)",
    description:
      "Rejoue des blocs de 5 vraies séances passées, tous actifs ensemble : queues épaisses et co-mouvements réels. Sans 120 séances d'historique, une loi de Student à 4 degrés de liberté prend le relais.",
  },
  {
    nom: "Emballement",
    nomMoteur: "Machine Learning (Tendance)",
    description: "Rendements autocorrélés (0,2) et choc qui s'accélère dans le temps : la tendance s'auto-entretient, comme dans une bulle ou une panique.",
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
