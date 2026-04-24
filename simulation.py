import pandas as pd
import numpy as np

# --- PARAMÉTRAGE DES CLASSES D'ACTIFS ---
ACTIFS_PRO = {
    # Actions & Indices
    "S&P 500":              {"prix": 5200,   "volatilite": 0.012},
    "NASDAQ":               {"prix": 18200,  "volatilite": 0.016},
    "CAC 40":               {"prix": 8100,   "volatilite": 0.014},
    "MSCI_World":           {"prix": 3500,   "volatilite": 0.011},
    "Emerging_Markets":     {"prix": 1100,   "volatilite": 0.018},

    # Obligations d'État 10Y
    "Bons_Tresor_US_10Y":   {"prix": 100,    "volatilite": 0.003},
    "Bund_10Y":             {"prix": 100,    "volatilite": 0.002},
    "OAT_10Y":              {"prix": 100,    "volatilite": 0.0025},
    "JGB_10Y":              {"prix": 100,    "volatilite": 0.0015},
    "Gilt_10Y":             {"prix": 100,    "volatilite": 0.003},

    # Devises & Volatilité
    "EUR_USD":              {"prix": 1.08,   "volatilite": 0.004},
    "Dollar_Index":         {"prix": 104,    "volatilite": 0.004},
    "VIX":                  {"prix": 18,     "volatilite": 0.06},

    # Matières premières
    "Or":                   {"prix": 2350,   "volatilite": 0.008},
    "Argent":               {"prix": 28,     "volatilite": 0.022},
    "Petrole":              {"prix": 85,     "volatilite": 0.025},
    "Cuivre":               {"prix": 4.5,    "volatilite": 0.020},
    "ETF_Terres_Rares":     {"prix": 55,     "volatilite": 0.030},

    # Sectoriels
    "ETF_Defense":          {"prix": 42,     "volatilite": 0.015},

    # Cryptomonnaies
    "Bitcoin":              {"prix": 65000,  "volatilite": 0.045},
    "Ethereum":             {"prix": 3300,   "volatilite": 0.055},
    "XRP":                  {"prix": 0.55,   "volatilite": 0.065},
    "Solana":               {"prix": 160,    "volatilite": 0.070},
}


def simuler_marche_dynamique(chocs_ia, jours=100, modele="Probabiliste (Réaliste)", actifs=None):
    """
    Génère les trajectoires des prix selon 3 comportements stochastiques.

    - chocs_ia : dict retourné par analyser_evenement_macro()
    - jours    : horizon de simulation
    - modele   : Probabiliste / Historique / Machine Learning
    - actifs   : liste des sim_keys à simuler (None = tous)
    """
    impacts = chocs_ia.get("actifs", {})

    # Filtre selon la sélection utilisateur
    if actifs is not None:
        actifs_a_simuler = {k: v for k, v in ACTIFS_PRO.items() if k in actifs}
    else:
        actifs_a_simuler = ACTIFS_PRO

    if not actifs_a_simuler:
        actifs_a_simuler = ACTIFS_PRO

    historique = pd.DataFrame(index=range(jours), columns=actifs_a_simuler.keys())

    # Initialisation jour 0
    for actif, params in actifs_a_simuler.items():
        historique.loc[0, actif] = params["prix"]

    # Simulation stochastique quotidienne
    for jour in range(1, jours):
        for actif in actifs_a_simuler.keys():
            vol = actifs_a_simuler[actif]["volatilite"]
            tendance_globale = impacts.get(actif, 0) / jours
            ancien_prix = historique.loc[jour - 1, actif]

            if "Probabiliste" in modele:
                variation = np.random.normal(0, vol)
                nouveau_prix = ancien_prix * (1 + tendance_globale + variation)

            elif "Historique" in modele:
                variation = np.random.normal(0, vol * 0.8)
                if np.random.rand() < 0.02:
                    variation += np.random.choice([-1, 1]) * (vol * 5)
                nouveau_prix = ancien_prix * (1 + tendance_globale + variation)

            else:  # Machine Learning / Momentum
                variation = np.random.normal(0, vol * 0.5)
                momentum = tendance_globale * (1 + (jour / jours))
                nouveau_prix = ancien_prix * (1 + momentum + variation)

            historique.loc[jour, actif] = nouveau_prix

    return historique.astype(float)
