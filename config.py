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
SCENARIO_C_DEFAUT = "Un choc geopolitique majeur (tensions Taiwan, conflit énergétique) déstabilise les marchés."

# Comparaison multi-scenarios : labels ordonnes utilisables pour 1, 2 ou 3 simulations
LABELS_SCENARIOS = ["A", "B", "C"]
NB_SCENARIOS_MAX = len(LABELS_SCENARIOS)


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
# COULEURS — palette unifiée (SOURCE DE VÉRITÉ Python)
# ------------------------------------------------------------------
# Miroir des tokens CSS de components/styling.py (--accent, --success…).
# Les graphiques Plotly et les SVG ne lisent pas le CSS : ils importent
# ces constantes pour rester cohérents avec le reste de l'interface.
# ==========================================
COULEUR_ACCENT  = "#6366f1"   # indigo — accent de marque
COULEUR_SUCCESS = "#16c784"   # vert TradingView — gains, "bon"
COULEUR_DANGER  = "#ef454a"   # rouge TradingView — pertes, "mauvais"
COULEUR_WARN    = "#f59e0b"   # ambre — "moyen / attention"
COULEUR_MUTED   = "#64748b"   # slate — neutre
COULEUR_TEXT    = "#1e293b"   # slate-800 — texte sombre

# Palette qualitative pour les graphiques multi-séries (Plotly).
# Couleurs distinctes mais harmonisées autour de l'indigo de marque.
PALETTE_GRAPHIQUES = [
    "#6366f1",  # indigo  (marque)
    "#16c784",  # vert
    "#f59e0b",  # ambre
    "#8b5cf6",  # violet
    "#06b6d4",  # cyan
    "#ef454a",  # rouge
    "#3b82f6",  # bleu
    "#64748b",  # slate
]

# Alias rétro-compatible
COULEURS_PLOTLY = PALETTE_GRAPHIQUES


# ==========================================
# PARAMÈTRES DE SIMULATION
# ==========================================
HORIZON_MIN = 30
HORIZON_MAX = 250
HORIZON_DEFAUT = 100
HORIZON_STEP = 10

NB_SIMULATIONS_MONTE_CARLO = 1000

# Modeles d'alea proposes (le moteur reconnait les mots Probabiliste / Historique)
MODELES_SIMULATION = [
    "Probabiliste (Réaliste)",
    "Historique (Chocs violents)",
    "Machine Learning (Tendance)",
]
PROFIL_PERSONNALISE = "Personnalisé"
BENCHMARKS = ["S&P 500", "MSCI_World"]
# Trajectoires gardees en memoire pour les metriques de risque (limite la RAM de session)
NB_CHEMINS_CONSERVES = 400

# Modele "Historique" : longueur des blocs de jours reels rejoues (preserve les
# enchainements de mauvaises seances) et minimum de seances pour l'activer.
BOOTSTRAP_TAILLE_BLOC = 5
BOOTSTRAP_MIN_SEANCES = 120
# Modele "Tendance" : autocorrelation des rendements et acceleration du choc.
MOMENTUM_AUTOCORRELATION = 0.2
MOMENTUM_ACCELERATION = 0.5
# Queues epaisses de secours (loi de Student) si l'historique reel manque.
STUDENT_DEGRES_LIBERTE = 4
# Garde-fou : pire variation possible sur une seule seance.
PERTE_MAX_QUOTIDIENNE = 0.5

# Fenetre (en jours calendaires) pour calibrer volatilites et correlations.
FENETRE_CALIBRATION_JOURS = 730

CAPITAL_MIN = 100
CAPITAL_MAX = 10_000_000
CAPITAL_DEFAUT = 10_000
CAPITAL_STEP = 500


# ==========================================
# AFFICHAGE
# ==========================================
HISTORIQUE_TAILLE_MAX = 10
# Cookie anonyme qui rattache un visiteur a son propre historique
COOKIE_VISITEUR = "qt_visiteur"
COOKIE_VISITEUR_DUREE_JOURS = 365
HAUTEUR_GRAPHIQUE = 380
TAUX_SANS_RISQUE_ANNUEL = 0.02  # Sharpe : valeur de secours si FRED est injoignable


# ==========================================
# MODELES D'IA (OpenAI)
# ------------------------------------------------------------------
# Chaque usage = parametres passes tels quels a chat.completions.create.
# Les modeles a raisonnement (gamme GPT-6) refusent "temperature" : on regle
# leur profondeur de reflexion avec "reasoning_effort" a la place.
# Choix mesures sur le prompt reel : analyse ~12 s, chat ~4 s.
# ==========================================
IA_ANALYSE = {"model": "gpt-6.1-terra", "reasoning_effort": "low"}
# Utilise si le modele d'analyse est indisponible (retire, surcharge, timeout)
IA_ANALYSE_SECOURS = {"model": "gpt-5.4-mini", "temperature": 0.45}
IA_CHAT = {"model": "gpt-5.4-mini", "temperature": 0.6}
IA_RAPPORT = {"model": "gpt-5.4-mini", "temperature": 0.5, "max_completion_tokens": 1200}
IA_TIMEOUT_SECONDES = 45.0


# ==========================================
# DEVISES — le portefeuille est en euros, les actifs non
# ------------------------------------------------------------------
# Devise de cotation de chaque actif. None = indicateur sans conversion
# (paire de devises, indice de volatilite).
# ==========================================
DEVISE_REFERENCE = "EUR"
ACTIF_TAUX_EUR_USD = "EUR_USD"

DEVISE_ACTIF = {
    "S&P 500": "USD", "NASDAQ": "USD", "CAC 40": "EUR",
    "MSCI_World": "USD", "Emerging_Markets": "USD",
    "Bons_Tresor_US_10Y": "USD", "Bund_10Y": "EUR", "OAT_10Y": "EUR",
    "JGB_10Y": "JPY", "Gilt_10Y": "GBP",
    "EUR_USD": None, "Dollar_Index": None, "VIX": None,
    "Or": "USD", "Argent": "USD", "Petrole": "USD", "Cuivre": "USD",
    "ETF_Terres_Rares": "USD", "ETF_Defense": "USD",
    "Bitcoin": "USD", "Ethereum": "USD", "XRP": "USD", "Solana": "USD",
}

# Actifs cotes 7j/7 : on les aligne sur les jours de bourse quand ils sont
# melanges a des actifs classiques (sinon les week-ends ecrasent la volatilite).
ACTIFS_COTES_7J = {"Bitcoin", "Ethereum", "XRP", "Solana"}

# Tolerance (en seances) pour un actif qui commence a coter juste apres le
# debut d'un backtest (jours feries decales). Au-dela, l'actif est ecarte :
# on n'invente pas de prix pour une periode ou il n'existait pas.
BACKTEST_TOLERANCE_DEBUT_SEANCES = 5


# ==========================================
# CORRELATIONS DE SECOURS (si l'historique Yahoo est indisponible)
# ------------------------------------------------------------------
# Ordres de grandeur de long terme entre grandes classes d'actifs.
# En fonctionnement normal, les correlations sont mesurees sur les
# vrais rendements des 2 dernieres annees.
# ==========================================
GROUPE_CORRELATION = {
    "S&P 500": "actions", "NASDAQ": "actions", "CAC 40": "actions",
    "MSCI_World": "actions", "Emerging_Markets": "actions",
    "ETF_Terres_Rares": "actions", "ETF_Defense": "actions",
    "Bons_Tresor_US_10Y": "obligations", "Bund_10Y": "obligations",
    "OAT_10Y": "obligations", "JGB_10Y": "obligations", "Gilt_10Y": "obligations",
    "EUR_USD": "euro", "Dollar_Index": "dollar", "VIX": "vix",
    "Or": "metaux", "Argent": "metaux",
    "Petrole": "cycliques", "Cuivre": "cycliques",
    "Bitcoin": "crypto", "Ethereum": "crypto", "XRP": "crypto", "Solana": "crypto",
}
GROUPE_CORRELATION_DEFAUT = "actions"  # actifs personnalises : majoritairement des actions

CORRELATION_INTRA_GROUPE = {
    "actions": 0.75, "obligations": 0.70, "metaux": 0.75,
    "cycliques": 0.35, "crypto": 0.75,
}

CORRELATION_INTER_GROUPES = {
    ("actions", "obligations"): -0.10, ("actions", "metaux"): 0.05,
    ("actions", "cycliques"): 0.30,    ("actions", "crypto"): 0.35,
    ("actions", "vix"): -0.70,         ("actions", "euro"): 0.20,
    ("actions", "dollar"): -0.20,
    ("obligations", "metaux"): 0.25,   ("obligations", "cycliques"): -0.15,
    ("obligations", "crypto"): 0.00,   ("obligations", "vix"): 0.15,
    ("obligations", "euro"): 0.10,     ("obligations", "dollar"): -0.10,
    ("metaux", "cycliques"): 0.20,     ("metaux", "crypto"): 0.10,
    ("metaux", "vix"): 0.00,           ("metaux", "euro"): 0.35,
    ("metaux", "dollar"): -0.40,
    ("cycliques", "crypto"): 0.15,     ("cycliques", "vix"): -0.25,
    ("cycliques", "euro"): 0.15,       ("cycliques", "dollar"): -0.20,
    ("crypto", "vix"): -0.25,          ("crypto", "euro"): 0.10,
    ("crypto", "dollar"): -0.10,
    ("vix", "euro"): -0.10,            ("vix", "dollar"): 0.10,
    ("euro", "dollar"): -0.95,
}


# ==========================================
# VALEURS DE SECOURS (dernier filet si Yahoo ET le snapshot disque manquent)
# ------------------------------------------------------------------
# Cloture reelle relevee a DATE_PRIX_SECOURS + volatilite quotidienne typique.
# L'interface signale explicitement quand ces valeurs sont utilisees.
# ==========================================
DATE_PRIX_SECOURS = "2026-11-10"

ACTIFS_SECOURS = {
    "S&P 500":              {"prix": 7520,   "volatilite": 0.010},
    "NASDAQ":               {"prix": 27740,  "volatilite": 0.013},
    "CAC 40":               {"prix": 8230,   "volatilite": 0.010},
    "MSCI_World":           {"prix": 204,    "volatilite": 0.009},
    "Emerging_Markets":     {"prix": 60.6,   "volatilite": 0.011},
    "Bons_Tresor_US_10Y":   {"prix": 91,     "volatilite": 0.004},
    "Bund_10Y":             {"prix": 117,    "volatilite": 0.003},
    "OAT_10Y":              {"prix": 118,    "volatilite": 0.003},
    "JGB_10Y":              {"prix": 1496,   "volatilite": 0.003},
    "Gilt_10Y":             {"prix": 9.74,   "volatilite": 0.004},
    "EUR_USD":              {"prix": 1.117,  "volatilite": 0.004},
    "Dollar_Index":         {"prix": 102.2,  "volatilite": 0.004},
    "VIX":                  {"prix": 19.5,   "volatilite": 0.065},
    "Or":                   {"prix": 4040,   "volatilite": 0.011},
    "Argent":               {"prix": 51.5,   "volatilite": 0.020},
    "Petrole":              {"prix": 86.3,   "volatilite": 0.022},
    "Cuivre":               {"prix": 6.27,   "volatilite": 0.017},
    "ETF_Terres_Rares":     {"prix": 51.8,   "volatilite": 0.024},
    "ETF_Defense":          {"prix": 72.4,   "volatilite": 0.012},
    "Bitcoin":              {"prix": 73400,  "volatilite": 0.025},
    "Ethereum":             {"prix": 2050,   "volatilite": 0.038},
    "XRP":                  {"prix": 1.05,   "volatilite": 0.042},
    "Solana":               {"prix": 83,     "volatilite": 0.045},
}



# ==========================================
# API WEB (FastAPI) — garde-fous
# ------------------------------------------------------------------
# L'API est publique et chaque analyse coute un appel OpenAI : on borne
# la taille des demandes et le nombre d'appels par visiteur.
# ==========================================
API_SCENARIO_LONGUEUR_MAX = 1000
API_ACTIFS_MAX = 40
API_TICKERS_PERSO_MAX = 10
API_CHAT_MESSAGES_MAX = 30
API_CHAT_LONGUEUR_MAX = 4000
API_BACKTEST_JOURS_MAX = 3660          # ~10 ans
API_FENETRE_LIMITE_SECONDES = 60
API_LIMITE_APPELS_IA = 12              # simulations + rapports + chat, par minute et par IP
API_LIMITE_APPELS_DONNEES = 120        # prix, catalogue, backtests, par minute et par IP
API_ORIGINES_PAR_DEFAUT = ["http://localhost:3000", "http://127.0.0.1:3000"]
# Un visiteur peut forcer le rechargement des prix, au plus une fois par periode
# (protege Yahoo Finance d'un afflux de requetes).
API_RAFRAICHISSEMENT_PRIX_MIN_SECONDES = 300


# ==========================================
# CONJONCTURE (FRED, Reserve federale de Saint-Louis — donnees publiques)
# ------------------------------------------------------------------
# Donne a l'IA les conditions de depart reelles (taux, inflation) et fournit
# le taux sans risque du ratio de Sharpe (taux de depot BCE : investisseur en euros).
# ==========================================
SERIES_FRED = {
    # cle: (identifiant FRED, libelle, nature) ; nature "taux" = niveau en %,
    # "indice" = indice de prix dont on calcule la variation sur 12 mois.
    "taux_fed":       ("DFF", "Taux directeur Fed (effectif)", "taux"),
    "taux_bce":       ("ECBDFR", "Taux de dépôt BCE", "taux"),
    "taux_10_ans_us": ("DGS10", "Taux à 10 ans États-Unis", "taux"),
    "taux_10_ans_de": ("IRLTLT01DEM156N", "Taux à 10 ans Allemagne", "taux"),
    "inflation_us":   ("CPIAUCSL", "Inflation États-Unis (sur 1 an)", "indice"),
    "inflation_ze":   ("CP0000EZ19M086NEST", "Inflation zone euro (sur 1 an)", "indice"),
}
SERIE_TAUX_SANS_RISQUE = "taux_bce"
CONJONCTURE_HISTORIQUE_ANNEES = 3
