"""
api/comparaison.py
==================
« Comparer deux portefeuilles » face au meme scenario.

Deux simulations a la suite (une par portefeuille) : l'analyse de l'IA est
cachee 24 h sur (scenario, calibration, tickers perso, conjoncture), jamais sur
les actifs ni l'allocation. La 2e simulation relit donc l'analyse de la 1re
sans rappeler l'IA, a condition d'avoir les memes actifs personnalises.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from api import services
from api.modeles import DemandePortefeuille, DemandeSimulation
from config import API_SCENARIO_LONGUEUR_MAX, HORIZON_DEFAUT, HORIZON_MAX, HORIZON_MIN, MODELES_SIMULATION


class DemandeComparaison(BaseModel):
    scenario: str = Field(min_length=1, max_length=API_SCENARIO_LONGUEUR_MAX)
    portefeuille_a: DemandePortefeuille
    portefeuille_b: DemandePortefeuille
    duree: int = Field(default=HORIZON_DEFAUT, ge=HORIZON_MIN, le=HORIZON_MAX)
    modele: str = MODELES_SIMULATION[0]
    monte_carlo: bool = False
    prix_reels: bool = True
    calibration: bool = True
    convertir_eur: bool = True

    @field_validator("modele")
    @classmethod
    def _modele_connu(cls, v: str) -> str:
        if v not in MODELES_SIMULATION:
            raise ValueError(f"Modèle inconnu. Choix possibles : {', '.join(MODELES_SIMULATION)}")
        return v


def _tickers(p: DemandePortefeuille) -> set:
    return {t.strip().upper() for t in p.tickers_perso if t.strip()}


def _demande_simulation(demande: DemandeComparaison, p: DemandePortefeuille) -> DemandeSimulation:
    # La devise est un reglage commun : les deux portefeuilles sont traites pareil.
    champs = {**p.model_dump(), "convertir_eur": demande.convertir_eur}
    return DemandeSimulation(
        **champs, scenarios=[demande.scenario], duree=demande.duree,
        modele=demande.modele, monte_carlo=demande.monte_carlo, prix_reels=demande.prix_reels,
        calibration=demande.calibration,
    )


def _ecart(b: Optional[float], a: Optional[float]) -> Optional[float]:
    return None if a is None or b is None else b - a


def comparer_portefeuilles(demande: DemandeComparaison) -> Dict[str, Any]:
    """Simule A puis B (sequentiel, pour que B profite du cache de l'analyse IA)."""
    if _tickers(demande.portefeuille_a) != _tickers(demande.portefeuille_b):
        raise services.DemandeInvalide(
            "Pour comparer deux portefeuilles sur la même analyse de l'IA, utilisez les mêmes "
            "actifs personnalisés dans les deux portefeuilles."
        )
    reponse_a = services.executer_simulation(_demande_simulation(demande, demande.portefeuille_a))
    reponse_b = services.executer_simulation(_demande_simulation(demande, demande.portefeuille_b))
    a, b = reponse_a["scenarios"][0], reponse_b["scenarios"][0]
    if a.get("erreur") or b.get("erreur"):
        raise services.ServiceIndisponible(a.get("erreur") or b.get("erreur"))

    # Ecarts = B moins A (en points de % pour la performance).
    ma, mb = a["metriques"], b["metriques"]
    ecarts = {
        "perf_pts": _ecart(b["portefeuille"]["performance_pct"], a["portefeuille"]["performance_pct"]),
        "valeur_finale": _ecart(b["portefeuille"]["valeur_finale"], a["portefeuille"]["valeur_finale"]),
        "volatilite": _ecart(mb.get("vol_ann"), ma.get("vol_ann")),
        "sharpe": _ecart(mb.get("sharpe"), ma.get("sharpe")),
        "var": _ecart(mb.get("var_95"), ma.get("var_95")),
        "drawdown": _ecart(mb.get("max_dd"), ma.get("max_dd")),
    }
    return {
        "a": a, "b": b, "analyse_partagee": True, "ecarts": ecarts,
        "date": reponse_a["date"], "parametres": reponse_a["parametres"],
        "prix_de_secours": reponse_a["prix_de_secours"],
    }
