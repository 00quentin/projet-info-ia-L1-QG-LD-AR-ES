"""
core/portfolio.py
=================
Calcul des poids d'allocation selon le profil d'investisseur, et
construction de la serie temporelle de valeur du portefeuille.
"""

from typing import Dict, List, Tuple

import pandas as pd

from config import PROFILS, NOM_AFFICHAGE


def calculer_poids(
    profil: str,
    actifs_sim: List[str],
    allocations_custom: Dict[str, int]
) -> Dict[str, float]:
    """
    Calcule les poids finaux du portefeuille (somme = 1.0).

    Args:
        profil: nom du profil ("Prudent...", "Équilibré...", "Agressif...", "Personnalisé")
        actifs_sim: liste des sim_keys d'actifs sélectionnés par l'utilisateur
        allocations_custom: dict {sim_key: pourcentage} pour profil Personnalisé

    Returns:
        Dict {sim_key: poids_normalise} où la somme = 1.0
    """
    if profil == "Personnalisé":
        total = sum(allocations_custom.values()) or 1
        poids = {k: v / total for k, v in allocations_custom.items() if v > 0}
    elif profil in PROFILS:
        poids_bruts = PROFILS[profil]
        poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}
    else:
        poids = {}

    # Renormalisation à 1.0
    total = sum(poids.values())
    if total > 0:
        poids = {k: v / total for k, v in poids.items()}

    # Fallback : si aucun actif du profil n'est dans la sélection, équipondéré
    if not poids and actifs_sim:
        poids = {k: 1 / len(actifs_sim) for k in actifs_sim}

    return poids


def construire_allocations_finales(
    perf_par_actif: Dict[str, float],
    poids: Dict[str, float],
    capital: float
) -> Tuple[List[Dict], float]:
    """
    Construit la liste détaillée des allocations finales du portefeuille.

    Args:
        perf_par_actif: dict {sim_key: perf_en_pourcentage}
        poids: dict {sim_key: poids_normalise}
        capital: capital initial en euros

    Returns:
        Tuple (liste de dicts avec détails, valeur finale totale)
        Chaque dict contient : nom, poids, investi, final, rendement
    """
    allocations = []
    valeur_finale = 0.0

    for sim_key, pct in poids.items():
        nom = NOM_AFFICHAGE.get(sim_key, sim_key.replace("_", " ").replace("EUR USD", "EUR/USD"))
        rend = perf_par_actif.get(sim_key, 0) / 100
        invest = capital * pct
        final = invest * (1 + rend)
        valeur_finale += final
        allocations.append({
            "nom": nom,
            "poids": pct,
            "investi": invest,
            "final": final,
            "rendement": rend,
        })

    return allocations, valeur_finale


def calculer_valeur_portefeuille(
    df: pd.DataFrame,
    poids: Dict[str, float],
    capital: float,
) -> pd.Series:
    """
    Construit la serie temporelle de la valeur du portefeuille en euros.

    Logique vectorisee : evite la boucle for + accumulation qui etait
    dupliquee dans dashboard.py / comparaison.py / backtest.py.

    Args:
        df: DataFrame des prix par actif (colonnes = sim_keys)
        poids: dict {sim_key: poids_normalise} dont la somme = 1.0
        capital: capital initial en euros

    Returns:
        pd.Series indexee comme df, donnant la valeur du portefeuille
        a chaque pas de temps.
    """
    # Filtre les actifs presents a la fois dans df et dans poids
    actifs_presents = [sk for sk in poids if sk in df.columns]
    if not actifs_presents:
        return pd.Series(capital, index=df.index, dtype=float)

    # ffill/bfill pour combler les trous de cotation (intra ou debut de periode)
    sub = df[actifs_presents].ffill().bfill()
    base = sub.iloc[0]

    # Defensif : on ecarte les actifs dont le prix initial reste invalide
    # (0 ou NaN apres ffill/bfill = aucune donnee dans toute la periode).
    actifs_valides = [sk for sk in actifs_presents
                       if pd.notna(base[sk]) and base[sk] > 0]
    if not actifs_valides:
        return pd.Series(capital, index=df.index, dtype=float)

    sub = sub[actifs_valides]
    base = sub.iloc[0]

    # Renormalisation des poids sur les actifs encore valides pour que la
    # somme reste a 1.0 (sinon le portefeuille serait mecaniquement < capital).
    total_poids = sum(poids[sk] for sk in actifs_valides)
    if total_poids <= 0:
        return pd.Series(capital, index=df.index, dtype=float)
    poids_serie = pd.Series({sk: poids[sk] / total_poids for sk in actifs_valides})

    return ((sub / base) * poids_serie * capital).sum(axis=1)