
import pandas as pd
import numpy as np

# --- PARAMÉTRAGE DES CLASSES D'ACTIFS ---
# On garde les clés exactes pour ne pas planter l'IA, l'interface graphique (app.py) se chargera d'enlever les "_" pour faire joli.
ACTIFS_PRO = {
    "S&P 500": {"prix": 5200, "volatilite": 0.012},
    "CAC 40": {"prix": 8100, "volatilite": 0.014},
    "Bons_Tresor_US_10Y": {"prix": 100, "volatilite": 0.003},
    "Or": {"prix": 2350, "volatilite": 0.008},
    "Petrole": {"prix": 85, "volatilite": 0.025},
    "EUR_USD": {"prix": 1.08, "volatilite": 0.004},
    "Bitcoin": {"prix": 65000, "volatilite": 0.045},
    "Ethereum": {"prix": 3300, "volatilite": 0.055}
}

def simuler_marche_dynamique(chocs_ia, jours=100, modele="Probabiliste (Réaliste)"):
    """
    Génère les trajectoires des prix avec 3 comportements mathématiques distincts.
    Utilise les paramètres de volatilité historique et les chocs fournis par l'IA.
    """
    impacts = chocs_ia.get("actifs", {})
    historique = pd.DataFrame(index=range(jours), columns=ACTIFS_PRO.keys())
    
    # Initialisation Jour 0 pour tous les actifs
    for actif, params in ACTIFS_PRO.items():
        historique.loc[0, actif] = params["prix"]
        
    # Génération stochastique quotidienne
    for jour in range(1, jours):
        for actif in ACTIFS_PRO.keys():
            vol = ACTIFS_PRO[actif]["volatilite"]
            
            # La tendance imposée par le scénario IA, lissée sur la durée
            tendance_globale = impacts.get(actif, 0) / jours
            ancien_prix = historique.loc[jour-1, actif]
            
            # --- MODÈLE 1 : PROBABILISTE (Bruit standard - Mouvement Brownien) ---
            if "Probabiliste" in modele:
                variation = np.random.normal(0, vol)
                nouveau_prix = ancien_prix * (1 + tendance_globale + variation)
                
            # --- MODÈLE 2 : HISTORIQUE (Chocs soudains / Queues épaisses) ---
            elif "Historique" in modele:
                variation = np.random.normal(0, vol * 0.8) # Bruit ambiant réduit
                
                # Événement "Queue épaisse" : 2% de chance d'avoir un krach/rebond violent
                if np.random.rand() < 0.02: 
                    variation += np.random.choice([-1, 1]) * (vol * 5)
                    
                nouveau_prix = ancien_prix * (1 + tendance_globale + variation)
                
            # --- MODÈLE 3 : MACHINE LEARNING (Lissage et Momentum de Tendance) ---
            else:
                variation = np.random.normal(0, vol * 0.5) # Bruit fortement réduit
                
                # Effet momentum : la conviction du marché s'accélère avec le temps
                momentum = tendance_globale * (1 + (jour / jours)) 
                nouveau_prix = ancien_prix * (1 + momentum + variation)
            
            # Application du nouveau prix calculé
            historique.loc[jour, actif] = nouveau_prix
            
    # Conversion finale pour garantir la compatibilité Plotly/Streamlit
    return historique.astype(float)