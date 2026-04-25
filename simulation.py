import pandas as pd
import numpy as np

# --- PARAMÉTRAGE DES CLASSES D'ACTIFS (prix par défaut + volatilité) ---
ACTIFS_PRO = {
    "S&P 500":              {"prix": 5200,   "volatilite": 0.012},
    "NASDAQ":               {"prix": 18200,  "volatilite": 0.016},
    "CAC 40":               {"prix": 8100,   "volatilite": 0.014},
    "MSCI_World":           {"prix": 3500,   "volatilite": 0.011},
    "Emerging_Markets":     {"prix": 1100,   "volatilite": 0.018},
    "Bons_Tresor_US_10Y":   {"prix": 100,    "volatilite": 0.003},
    "Bund_10Y":             {"prix": 100,    "volatilite": 0.002},
    "OAT_10Y":              {"prix": 100,    "volatilite": 0.0025},
    "JGB_10Y":              {"prix": 100,    "volatilite": 0.0015},
    "Gilt_10Y":             {"prix": 100,    "volatilite": 0.003},
    "EUR_USD":              {"prix": 1.08,   "volatilite": 0.004},
    "Dollar_Index":         {"prix": 104,    "volatilite": 0.004},
    "VIX":                  {"prix": 18,     "volatilite": 0.06},
    "Or":                   {"prix": 2350,   "volatilite": 0.008},
    "Argent":               {"prix": 28,     "volatilite": 0.022},
    "Petrole":              {"prix": 85,     "volatilite": 0.025},
    "Cuivre":               {"prix": 4.5,    "volatilite": 0.020},
    "ETF_Terres_Rares":     {"prix": 55,     "volatilite": 0.030},
    "ETF_Defense":          {"prix": 42,     "volatilite": 0.015},
    "Bitcoin":              {"prix": 65000,  "volatilite": 0.045},
    "Ethereum":             {"prix": 3300,   "volatilite": 0.055},
    "XRP":                  {"prix": 0.55,   "volatilite": 0.065},
    "Solana":               {"prix": 160,    "volatilite": 0.070},
}


def simuler_marche_dynamique(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                              actifs=None, prix_reels=None, vols_reelles=None):
    """
    UNE trajectoire stochastique des prix selon 3 comportements.

    Paramètres :
    - chocs_ia    : dict avec clé 'actifs' contenant les chocs IA
    - jours       : horizon de simulation
    - modele      : 'Probabiliste', 'Historique', 'Machine Learning'
    - actifs      : liste des sim_keys à simuler (None = tous)
    - prix_reels  : dict {sim_key: prix} venant de Yahoo Finance (None = prix par défaut)
    - vols_reelles: dict {sim_key: vol} volatilités historiques calculées (None = vols par défaut)
    """
    impacts = chocs_ia.get("actifs", {})

    if actifs is not None:
        actifs_a_simuler = {k: v.copy() for k, v in ACTIFS_PRO.items() if k in actifs}
    else:
        actifs_a_simuler = {k: v.copy() for k, v in ACTIFS_PRO.items()}

    if not actifs_a_simuler:
        actifs_a_simuler = {k: v.copy() for k, v in ACTIFS_PRO.items()}

    # Override avec les prix réels si fournis
    if prix_reels:
        for sim_key in actifs_a_simuler:
            if sim_key in prix_reels and prix_reels[sim_key] > 0:
                actifs_a_simuler[sim_key]["prix"] = prix_reels[sim_key]

    # Override avec les volatilités réelles si fournies
    if vols_reelles:
        for sim_key in actifs_a_simuler:
            if sim_key in vols_reelles and vols_reelles[sim_key] > 0:
                actifs_a_simuler[sim_key]["volatilite"] = vols_reelles[sim_key]

    historique = pd.DataFrame(index=range(jours), columns=actifs_a_simuler.keys())

    for actif, params in actifs_a_simuler.items():
        historique.loc[0, actif] = params["prix"]

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
            else:
                variation = np.random.normal(0, vol * 0.5)
                momentum = tendance_globale * (1 + (jour / jours))
                nouveau_prix = ancien_prix * (1 + momentum + variation)

            historique.loc[jour, actif] = nouveau_prix

    return historique.astype(float)


def simuler_monte_carlo(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                         actifs=None, nb_simulations=50, prix_reels=None, vols_reelles=None):
    """Lance plusieurs simulations et calcule les percentiles 5/50/95."""
    toutes_simus = []
    for _ in range(nb_simulations):
        df = simuler_marche_dynamique(chocs_ia, jours=jours, modele=modele,
                                       actifs=actifs, prix_reels=prix_reels,
                                       vols_reelles=vols_reelles)
        toutes_simus.append(df)

    stack = np.stack([df.values for df in toutes_simus], axis=-1)
    colonnes = toutes_simus[0].columns
    mediane = pd.DataFrame(np.median(stack, axis=-1), columns=colonnes)
    percentile_bas = pd.DataFrame(np.percentile(stack, 5, axis=-1), columns=colonnes)
    percentile_haut = pd.DataFrame(np.percentile(stack, 95, axis=-1), columns=colonnes)

    return {
        "mediane": mediane.astype(float),
        "bas": percentile_bas.astype(float),
        "haut": percentile_haut.astype(float),
    }
