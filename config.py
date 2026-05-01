"""
config.py
=========
Configuration centralisée de Quant Terminal.
Toutes les constantes du projet sont ici, ce qui permet de les modifier
en un seul endroit sans toucher à la logique métier.
"""

# ==========================================
# CATALOGUE DES ACTIFS — noms officiels organisés par catégorie
# ==========================================
ACTIFS_DISPONIBLES = {
    "Actions & Indices": {
        "S&P 500 (USA)":                            "S&P 500",
        "NASDAQ 100 (Tech US)":                     "NASDAQ",
        "CAC 40 (France)":                          "CAC 40",
        "MSCI World (Global)":                      "MSCI_World",
        "MSCI Emerging Markets":                    "Emerging_Markets",
    },
    "Obligations d'État (10 ans)": {
        "U.S. Treasury 10Y":                        "Bons_Tresor_US_10Y",
        "Bund Allemagne 10Y":                       "Bund_10Y",
        "OAT France 10Y":                           "OAT_10Y",
        "JGB Japon 10Y":                            "JGB_10Y",
        "Gilt Royaume-Uni 10Y":                     "Gilt_10Y",
    },
    "Devises & Volatilité": {
        "EUR/USD (Euro-Dollar)":                    "EUR_USD",
        "DXY (US Dollar Index)":                    "Dollar_Index",
        "VIX (CBOE Volatility Index)":              "VIX",
    },
    "Matières Premières": {
        "Or (Gold Spot, $/oz)":                     "Or",
        "Argent (Silver Spot, $/oz)":               "Argent",
        "Pétrole WTI (Crude Oil)":                  "Petrole",
        "Cuivre (Copper Futures)":                  "Cuivre",
        "ETF Terres Rares (REMX)":                  "ETF_Terres_Rares",
    },
    "Sectoriels": {
        "ETF Aérospatiale & Défense (ITA)":         "ETF_Defense",
    },
    "Cryptomonnaies": {
        "Bitcoin (BTC)":                            "Bitcoin",
        "Ethereum (ETH)":                           "Ethereum",
        "XRP (Ripple)":                             "XRP",
        "Solana (SOL)":                             "Solana",
    },
}

# Mapping inverse : sim_key → nom d'affichage
NOM_AFFICHAGE = {v: k for cat in ACTIFS_DISPONIBLES.values() for k, v in cat.items()}

# Actifs cochés par défaut au chargement
ACTIFS_PAR_DEFAUT = {
    "S&P 500", "CAC 40", "Bons_Tresor_US_10Y",
    "EUR_USD", "Or", "Petrole", "Bitcoin", "Ethereum"
}

# Regroupement pour les graphiques par catégorie
CATEGORIES_GRAPHIQUES = {
    "Actions & Indices":     ["S&P 500", "NASDAQ", "CAC 40", "MSCI_World", "Emerging_Markets"],
    "Obligations d'État":    ["Bons_Tresor_US_10Y", "Bund_10Y", "OAT_10Y", "JGB_10Y", "Gilt_10Y"],
    "Devises & Volatilité":  ["EUR_USD", "Dollar_Index", "VIX"],
    "Matières Premières":    ["Or", "Argent", "Petrole", "Cuivre", "ETF_Terres_Rares"],
    "Sectoriels":            ["ETF_Defense"],
    "Cryptomonnaies":        ["Bitcoin", "Ethereum", "XRP", "Solana"],
}


# ==========================================
# SCÉNARIOS PRÉ-DÉFINIS (boutons rapides sidebar)
# ==========================================
EVENEMENTS_PRESETS = {
    "Guerre mondiale":       "Une guerre majeure éclate entre plusieurs grandes puissances, provoquant une mobilisation mondiale et une explosion des dépenses militaires.",
    "Pandémie mondiale":     "Un nouveau virus très contagieux se propage rapidement dans le monde, entraînant des confinements massifs et un arrêt partiel de l'économie mondiale.",
    "Révolution IA":         "Une intelligence artificielle générale (AGI) est annoncée par une grande entreprise tech, remplaçant une large part des emplois intellectuels en quelques années.",
    "Krach 2008 bis":        "Une crise bancaire majeure éclate aux États-Unis avec la faillite de plusieurs grandes banques, provoquant une panique financière mondiale.",
    "Fusion nucléaire":      "Des chercheurs annoncent la maîtrise industrielle de la fusion nucléaire, promettant une énergie illimitée et bon marché d'ici 5 ans.",
    "Choc pétrolier":        "Un conflit au Moyen-Orient coupe 30% de la production mondiale de pétrole, faisant exploser les prix de l'énergie.",
    "Hausse brutale FED":    "La FED annonce une hausse surprise des taux directeurs de +2% pour combattre une inflation hors de contrôle.",
    "Crise Chine-Taïwan":    "La Chine impose un blocus militaire autour de Taïwan, paralysant la production mondiale de semi-conducteurs.",
}


# ==========================================
# SCÉNARIO PAR DÉFAUT
# ==========================================
SCENARIO_A_DEFAUT = "Les États-Unis annoncent une impression massive de monnaie face à une crise soudaine."
SCENARIO_B_DEFAUT = "Une percée majeure dans l'intelligence artificielle dope la productivité mondiale."


# ==========================================
# PROFILS D'INVESTISSEMENT
# ==========================================
PROFILS = {
    "Prudent (Hyper Sécurisé)": {
        "Bons_Tresor_US_10Y": 0.50, "Or": 0.20, "S&P 500": 0.10,
        "EUR_USD": 0.10, "Bund_10Y": 0.05, "OAT_10Y": 0.05,
    },
    "Équilibré (Normal)": {
        "S&P 500": 0.25, "CAC 40": 0.08, "NASDAQ": 0.07,
        "Bons_Tresor_US_10Y": 0.25, "Or": 0.12, "Petrole": 0.05,
        "EUR_USD": 0.05, "Bitcoin": 0.08, "Ethereum": 0.05,
    },
    "Agressif (Risqué)": {
        "Bitcoin": 0.20, "Ethereum": 0.10, "XRP": 0.05, "Solana": 0.05,
        "S&P 500": 0.30, "NASDAQ": 0.15, "CAC 40": 0.05,
        "Petrole": 0.05, "ETF_Defense": 0.05,
    },
}


# ==========================================
# COULEURS — palette graphiques (utilisée par Plotly)
# ==========================================
COULEURS_PLOTLY = ["#1a365d", "#319795", "#d69e2e", "#c53030", "#805ad5", "#2f855a"]
COULEUR_PRIMAIRE = "#1a365d"
COULEUR_ACCENT = "#319795"
COULEUR_SUCCESS = "#2f855a"
COULEUR_DANGER = "#c53030"
COULEUR_MUTED = "#718096"
COULEUR_TEXT = "#2d3748"


# ==========================================
# PARAMÈTRES DE SIMULATION
# ==========================================
HORIZON_MIN = 30
HORIZON_MAX = 250
HORIZON_DEFAUT = 100
HORIZON_STEP = 10

NB_SIMULATIONS_MONTE_CARLO = 50

CAPITAL_MIN = 100
CAPITAL_MAX = 10_000_000
CAPITAL_DEFAUT = 10_000
CAPITAL_STEP = 500


# ==========================================
# AFFICHAGE
# ==========================================
HISTORIQUE_TAILLE_MAX = 10
HAUTEUR_GRAPHIQUE = 380
TAUX_SANS_RISQUE_ANNUEL = 0.02  # Pour le calcul du Sharpe Ratio