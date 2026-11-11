// Contenu de la page À propos (repris de l'onglet Streamlit, stack mise à jour pour le nouveau site).

export const MEMBRES_EQUIPE = [
  { nom: "Quentin Geldreich", description: "Étudiant en MIASHS et Économie & Gestion" },
  { nom: "Lukha Doazan", description: "Étudiant en MIASHS et Économie & Gestion" },
  { nom: "Evan Saadi", description: "Étudiant en MIASHS et Économie & Gestion" },
  { nom: "Alex Ruimy", description: "Étudiant en MIASHS et Économie & Gestion" },
];

export type BlocStack = { id: string; titre: string; role: string; outils: string[] };

export const STACK: BlocStack[] = [
  {
    id: "site",
    titre: "Site web",
    role: "L’interface que vous utilisez : pages, graphiques, animations.",
    outils: ["Next.js", "React", "TypeScript", "Tailwind CSS", "Motion", "D3 (graphiques)", "KaTeX (formules)"],
  },
  {
    id: "moteur",
    titre: "Moteur & API",
    role: "Le moteur de simulation en Python, exposé au site par une API web.",
    outils: ["Python", "FastAPI", "NumPy", "Pandas", "Pydantic"],
  },
  {
    id: "donnees",
    titre: "Données de marché",
    role: "Vrais prix, volatilités et corrélations ; conversion en euros.",
    outils: ["Yahoo Finance (yfinance)", "Taux de change de référence BCE"],
  },
  {
    id: "ia",
    titre: "Intelligence artificielle",
    role: "GPT-6.1 analyse les scénarios ; GPT-5.4 mini répond dans le chat, commente le rapport et prend le relais si besoin.",
    outils: ["OpenAI GPT-6.1", "OpenAI GPT-5.4 mini"],
  },
  {
    id: "rapports",
    titre: "Rapports & hébergement",
    role: "Rapports PDF générés côté serveur ; code source versionné.",
    outils: ["ReportLab (PDF)", "GitHub", "Render (API)"],
  },
];

export const FONCTIONNALITES: { titre: string; texte: string; lien?: string }[] = [
  { titre: "Simulation prospective", texte: "tester l’impact d’un scénario fictif sur un portefeuille", lien: "/" },
  { titre: "Backtest historique", texte: "rejouer les vraies données de crises passées (COVID, Lehman, dot-com…)", lien: "/backtest" },
  { titre: "Mode comparaison", texte: "opposer deux scénarios sur le même portefeuille" },
  { titre: "Mode Monte-Carlo", texte: "1 000 simulations pour une vision statistiquement robuste" },
  { titre: "Calibration historique IA", texte: "amplitudes calibrées sur les vraies crises" },
  { titre: "Connexion Yahoo Finance", texte: "prix actuels + volatilités historiques en direct" },
  { titre: "Métriques institutionnelles", texte: "Volatilité annualisée, Sharpe Ratio, Max Drawdown, VaR 95%" },
  { titre: "Génération de rapport PDF", texte: "professionnel" },
  { titre: "Analyste IA conversationnel", texte: "pour poser toutes vos questions" },
  { titre: "Académie pédagogique", texte: "7 modules pour comprendre la finance de marché, plus un lexique et la méthodologie", lien: "/academie" },
];
