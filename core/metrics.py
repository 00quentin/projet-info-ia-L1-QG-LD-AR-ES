"""
core/metrics.py
===============
Calculs des métriques de risque institutionnelles.

Toutes les formules suivent les standards utilisés par les gérants
de fonds professionnels (Bâle III, GIPS).
"""

from typing import Dict, Iterable
import numpy as np
import pandas as pd

from config import TAUX_SANS_RISQUE_ANNUEL


def calculer_metriques_risque(valeur_portefeuille: Iterable[float]) -> Dict[str, float]:
    """
    Calcule les 4 métriques de risque institutionnelles à partir d'une série
    de valeurs de portefeuille jour par jour.

    Args:
        valeur_portefeuille: série temporelle des valeurs du portefeuille

    Returns:
        Dict avec les clés : vol_ann, sharpe, max_dd, var_95
    """
    serie = pd.Series(valeur_portefeuille).astype(float)
    rendements = serie.pct_change().dropna()

    if len(rendements) == 0 or rendements.std() == 0:
        return {"vol_ann": 0.0, "sharpe": 0.0, "max_dd": 0.0, "var_95": 0.0}

    # Volatilité annualisée : σ_quotidien × √252
    vol_quotidienne = rendements.std()
    vol_ann = vol_quotidienne * np.sqrt(252) * 100

    # Sharpe Ratio : (rendement - taux sans risque) / volatilité
    rendement_moyen_ann = rendements.mean() * 252
    sharpe = (rendement_moyen_ann - TAUX_SANS_RISQUE_ANNUEL) / (vol_quotidienne * np.sqrt(252))

    # Max Drawdown : pire chute depuis un plus-haut
    cummax = serie.cummax()
    drawdown = (cummax - serie) / cummax
    max_dd = drawdown.max() * 100

    # VaR 95% à 1 jour : percentile 5% des rendements
    var_95 = np.percentile(rendements, 5) * 100

    return {
        "vol_ann": float(vol_ann),
        "sharpe": float(sharpe),
        "max_dd": float(max_dd),
        "var_95": float(var_95),
    }


def evaluer_qualite_sharpe(sharpe: float) -> str:
    """Classifie un Sharpe Ratio en qualité humainement compréhensible."""
    if sharpe < 0:
        return "Mauvais"
    elif sharpe < 1:
        return "Acceptable"
    elif sharpe < 2:
        return "Bon"
    else:
        return "Excellent"