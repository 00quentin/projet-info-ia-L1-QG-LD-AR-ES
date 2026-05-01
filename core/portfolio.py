"""
core/portfolio.py
=================
Calcul des poids d'allocation selon le profil d'investisseur.
"""

from typing import Dict, List, Tuple

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