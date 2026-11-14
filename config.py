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
    "Choc pétrolier":        "Un conflit au Moyen-Orient coupe 30 % de la production mondiale de pétrole, faisant exploser les prix de l'énergie.",
    "Hausse brutale de la Fed": "La Fed annonce une hausse surprise de ses taux directeurs de 2 points pour combattre une inflation hors de contrôle.",
    "Crise Chine-Taïwan":    "La Chine impose un blocus militaire autour de Taïwan, paralysant la production mondiale de semi-conducteurs.",
}


# ==========================================
# SCÉNARIO PAR DÉFAUT
# ==========================================
SCENARIO_A_DEFAUT = "Les États-Unis annoncent une impression massive de monnaie face à une crise soudaine."
SCENARIO_B_DEFAUT = "Une percée majeure dans l'intelligence artificielle dope la productivité mondiale."
SCENARIO_C_DEFAUT = "Un choc géopolitique majeur (tensions autour de Taïwan, conflit énergétique) déstabilise les marchés."

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

# Portefeuilles d'exemple proposés en un clic sur le site (ils remplissent le profil Personnalisé).
PORTEFEUILLES_EXEMPLE = {
    "60/40 classique": {
        "description": "Le grand classique : 60 % d'actions pour la croissance, "
                       "40 % d'obligations d'État pour amortir les chutes.",
        "poids": {
            "S&P 500": 0.30, "MSCI_World": 0.20, "CAC 40": 0.10,
            "Bons_Tresor_US_10Y": 0.20, "Bund_10Y": 0.10, "OAT_10Y": 0.10,
        },
    },
    "Tout actions monde": {
        "description": "100 % actions mondiales : 90 % pays développés (MSCI World) "
                       "et 10 % pays émergents. Plus de rendement espéré, plus de secousses.",
        "poids": {"MSCI_World": 0.90, "Emerging_Markets": 0.10},
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
# Profil de choc "crise" (modeles Probabiliste et Historique) : comme en 1987, 2008
# ou 2020, l'essentiel du mouvement arrive vite, depasse sa cible puis se resorbe en
# partie. Le point extreme tombe a CRISE_FRACTION_CREUX de l'horizon et va
# CRISE_DEPASSEMENT plus loin que le choc final de l'IA (0.3 = 30 % plus profond).
CRISE_FRACTION_CREUX = 0.2
CRISE_DEPASSEMENT = 0.3
# Doute de l'IA (Monte-Carlo) : chaque trajectoire tire son choc dans la fourchette
# bas / central / haut de l'IA. Part commune du tirage a tous les actifs (le scenario
# s'avere plus ou moins grave pour tous a la fois) : 0 = independants, 1 = identiques.
INCERTITUDE_IA_CORRELATION = 0.8
# Recalage de la fourchette de l'IA (schemas.elargir_fourchette) : elargit le cote
# "aggravation" (loin de zero), le cote "attenuation" et impose une demi-largeur minimale
# (part de l'amplitude des bornes de l'actif, plafonnee). Avec le prompt v8, l'IA donnait
# des fourchettes trop etroites (53 % de couverture) et le recalage 1.75 / 1.25 / 0.15
# montait a 78 %. Le prompt v9 demande lui-meme des fourchettes 10e-90e centile : seul,
# il couvre 84 % des vrais mouvements sur 6 crises, 85 % sur 9 dont 86 % sur 3 crises hors
# echantillon (scripts/valider_ia_historique.py), sans reglage
# choisi sur ces crises. Le recalage est donc neutre (1, 1, 0) mais reste disponible.
FOURCHETTE_ELARGISSEMENT_AGGRAVATION = 1.0
FOURCHETTE_ELARGISSEMENT_ATTENUATION = 1.0
FOURCHETTE_DEMI_LARGEUR_MIN = 0.0
FOURCHETTE_AMPLITUDE_REF_MAX = 1.2
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
API_TICKERS_PERSO_MAX = 20
API_CHAT_MESSAGES_MAX = 30
API_CHAT_LONGUEUR_MAX = 4000
API_CHAT_CONTEXTE_LONGUEUR_MAX = 4000   # resume du resultat affiche, transmis a l'analyste
API_BACKTEST_JOURS_MAX = 3660          # ~10 ans
API_FENETRE_LIMITE_SECONDES = 60
API_LIMITE_APPELS_IA = 12              # simulations + rapports + chat, par minute et par IP
API_LIMITE_APPELS_DONNEES = 120        # prix, catalogue, backtests, par minute et par IP
# Plafond de depense OpenAI : demandes IA par jour (UTC), tous visiteurs confondus.
# Une simulation compte pour 1 mais peut faire jusqu'a 6 appels OpenAI (3 scenarios
# x calibration). Surchargeable sur l'hebergeur : QT_PLAFOND_IA_JOUR=500.
API_PLAFOND_APPELS_IA_JOUR = 300
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


# ==========================================
# PROTÉGER MON PORTEFEUILLE (core/couverture.py, api/couverture.py)
# ==========================================
COUVERTURE_POIDS_MAX_LIGNE = 40          # % : aucune ligne au-dessus
COUVERTURE_ECART_MAX_LIGNE = 15          # points : variation maximale d'une ligne
COUVERTURE_ROTATION_MAX = 30             # % du portefeuille qui peut changer de main
COUVERTURE_PAS_TRANSFERT = 5             # points déplacés à chaque étape
COUVERTURE_ETAPES_MAX = 12               # 12 x 5 points : couvre largement la rotation maximale
COUVERTURE_GAIN_MIN_RELATIF = 0.01       # un transfert doit gagner au moins 1 % de score
COUVERTURE_PLANCHER_PROBA_PERTE = 5.0    # % : évite de diviser par une probabilité quasi nulle
COUVERTURE_PLANCHER_PERTE_MAX = 0.1      # % : idem pour un portefeuille quasi immobile
COUVERTURE_NB_TRAJECTOIRES_RECHERCHE = 400
COUVERTURE_NB_TRAJECTOIRES_EVALUATION = 1000
COUVERTURE_GRAINE = 2026                 # résultat reproductible pour une même demande
COUVERTURE_TAILLE_LOT = 48               # portefeuilles évalués ensemble (borne la mémoire)
JOURS_PAR_AN = 252                       # jours de bourse par an (annualisation)
# Bornes des actifs personnalises (miroir de schemas._BORNE_GENERIQUE_CUSTOM).
COUVERTURE_BORNES_ACTIF_PERSO = (-0.80, 2.00)
# Tolerance d'arrondi sur la somme des poids envoyes par le site (fractions).
COUVERTURE_TOLERANCE_SOMME_POIDS = 0.01
# Longueurs maximales des textes rediges par l'IA (au-dela : tronques).
COUVERTURE_JUSTIFICATION_LONGUEUR_MAX = 280
COUVERTURE_SYNTHESE_LONGUEUR_MAX = 320


# ==========================================
# L'IA À L'ÉPREUVE DE L'HISTOIRE (core/validation_ia.py, scripts/valider_ia_historique.py)
# ==========================================
# Sous ce mouvement réel (en points de %), le sens de variation n'est pas net :
# l'actif n'entre pas dans le score « bon sens » (il reste dans l'erreur moyenne).
SEUIL_SENS_PTS = 2.0
# Taille minimale d'un échantillon pour calculer une corrélation.
MIN_POINTS_CORRELATION = 3
# Mots des noms de crises qui ne trahissent pas l'événement : tous les autres
# mots du nom (Lehman, Brexit, COVID, Ukraine…) sont interdits dans la description.
MOTS_GENERIQUES = {"krach", "crise", "bulle", "guerre", "petrolier", "petroliere"}
# L'IA n'estime ni la livre ni le yen : ces actifs sont comparés dans leur devise.
VALIDATION_DEVISES_EN_LOCAL = {"GBP", "JPY"}
# Garde-fou de coût : nombre maximal d'appels IA par exécution.
VALIDATION_MAX_APPELS = 14

# Nouveau site (Next.js, dossier web/) : cible du bandeau de migration affiche dans Streamlit.
URL_NOUVEAU_SITE = "https://quant-terminal-qg-team.vercel.app"


# ==========================================
# ACTUALITÉ DU JOUR (ia_actualite.py, api/actualite.py)
# ==========================================
# Flux RSS publics FIXES (jamais fournis par le visiteur) : (nom affiché, URL).
ACTUALITE_FLUX = (
    ("Le Monde Économie", "https://www.lemonde.fr/economie/rss_full.xml"),
    ("France 24 Éco", "https://www.france24.com/fr/%C3%A9co-tech/rss"),
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
)
ACTUALITE_TIMEOUT_S = 5
ACTUALITE_TAILLE_MAX_OCTETS = 600_000     # un flux plus gros est ignoré
ACTUALITE_TITRES_PAR_FLUX = 15
ACTUALITE_TITRE_LONGUEUR_MAX = 160
ACTUALITE_SCENARIO_MIN = 40
ACTUALITE_SCENARIO_MAX = 600
ACTUALITE_THEMES_MAX = 3
ACTUALITE_TTL_S = 86400                   # 1 appel IA par jour et par instance

# --- Explication par actif (ia_explication.py) ---
EXPLICATION_TTL_SECONDES = 86400
EXPLICATION_PHRASE_MIN = 10
EXPLICATION_PHRASE_MAX = 220
EXPLICATION_CHOC_MIN_PCT = -100.0
EXPLICATION_CHOC_MAX_PCT = 1000.0
EXPLICATION_MAX_TOKENS = 1500

# --- Recherche d actifs (api/recherche.py) ---
RECHERCHE_LONGUEUR_MIN = 2
RECHERCHE_LONGUEUR_MAX = 40
RECHERCHE_RESULTATS_MAX = 10
RECHERCHE_TTL_S = 3600
RECHERCHE_TIMEOUT_S = 5
RECHERCHE_URL_YAHOO = "https://query2.finance.yahoo.com/v1/finance/search"
RECHERCHE_TYPES = {"EQUITY": "action", "ETF": "ETF", "INDEX": "indice", "CRYPTOCURRENCY": "crypto", "MUTUALFUND": "fonds"}
# Recherche : noms francais courants que la recherche Yahoo ne trouve pas (« Total »
# renvoie des ETF americains). Symbole verifie aupres de Yahoo au moment de l'ajout.
RECHERCHE_ALIAS = {
    "totalenergies": ("TTE.PA", "TotalEnergies"), "lvmh": ("MC.PA", "LVMH"),
    "l'oreal loreal oreal": ("OR.PA", "L'Oréal"), "airbus": ("AIR.PA", "Airbus"),
    "sanofi": ("SAN.PA", "Sanofi"), "bnp paribas": ("BNP.PA", "BNP Paribas"),
    "schneider electric": ("SU.PA", "Schneider Electric"), "air liquide": ("AI.PA", "Air Liquide"),
    "hermes": ("RMS.PA", "Hermès"), "kering": ("KER.PA", "Kering"), "axa": ("CS.PA", "AXA"),
    "vinci": ("DG.PA", "Vinci"), "safran": ("SAF.PA", "Safran"),
    "essilorluxottica essilor": ("EL.PA", "EssilorLuxottica"), "danone": ("BN.PA", "Danone"),
    "capgemini": ("CAP.PA", "Capgemini"), "credit agricole": ("ACA.PA", "Crédit Agricole"),
    "societe generale": ("GLE.PA", "Société Générale"), "orange": ("ORA.PA", "Orange"),
    "pernod ricard": ("RI.PA", "Pernod Ricard"), "saint-gobain saint gobain": ("SGO.PA", "Saint-Gobain"),
    "engie": ("ENGI.PA", "Engie"), "veolia": ("VIE.PA", "Veolia"), "michelin": ("ML.PA", "Michelin"),
    "renault": ("RNO.PA", "Renault"), "stellantis": ("STLAP.PA", "Stellantis"), "thales": ("HO.PA", "Thales"),
    "dassault systemes": ("DSY.PA", "Dassault Systèmes"), "publicis": ("PUB.PA", "Publicis"),
    "legrand": ("LR.PA", "Legrand"), "bouygues": ("EN.PA", "Bouygues"), "carrefour": ("CA.PA", "Carrefour"),
    "accor": ("AC.PA", "Accor"), "vivendi": ("VIV.PA", "Vivendi"),
}
