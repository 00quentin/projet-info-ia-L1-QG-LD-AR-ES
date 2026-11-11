"""
core/metrics.py
===============
Calculs des métriques de risque institutionnelles.

Toutes les formules suivent les standards utilisés par les gérants
de fonds professionnels (Bâle III, GIPS).
"""

from typing import Dict, Iterable, List, Optional
import numpy as np
import pandas as pd

from config import TAUX_SANS_RISQUE_ANNUEL


def calculer_metriques_risque(
    valeur_portefeuille: Iterable[float],
    taux_sans_risque: float = TAUX_SANS_RISQUE_ANNUEL,
) -> Dict[str, float]:
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
    sharpe = (rendement_moyen_ann - taux_sans_risque) / (vol_quotidienne * np.sqrt(252))

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

def calculer_metriques_monte_carlo(
    chemins: np.ndarray,
    colonnes: List[str],
    poids: Dict[str, float],
    capital: float,
    taux_sans_risque: float = TAUX_SANS_RISQUE_ANNUEL,
) -> Optional[Dict[str, float]]:
    """
    Metriques de risque calculees sur les trajectoires Monte-Carlo du portefeuille.

    Pourquoi : la trajectoire mediane est lissee (l'alea s'y annule), donc y
    mesurer volatilite/drawdown/VaR sous-estime fortement le risque. Ici chaque
    metrique est calculee sur chaque trajectoire puis on prend la mediane, et la
    VaR sur l'ensemble des rendements quotidiens simules.

    Returns:
        Les 4 cles habituelles (vol_ann, sharpe, max_dd, var_95) plus la
        distribution de la valeur finale : valeur_p5, valeur_mediane, valeur_p95,
        proba_perte (en %). None si aucun actif du portefeuille n'est simule.
    """
    idx = [colonnes.index(k) for k in poids if k in colonnes]
    if not idx or chemins is None or len(chemins) == 0:
        return None
    w = np.array([poids[colonnes[i]] for i in idx], dtype=float)
    if w.sum() <= 0:
        return None
    w = w / w.sum()

    prix = chemins[:, :, idx].astype(float)
    valeurs = capital * (prix / prix[:, :1, :] * w).sum(axis=2)
    rendements = valeurs[:, 1:] / valeurs[:, :-1] - 1
    if rendements.shape[1] == 0:
        return None

    vol_q = rendements.std(axis=1, ddof=1) if rendements.shape[1] > 1 else np.zeros(len(valeurs))
    vol_ann = vol_q * np.sqrt(252)
    rend_ann = rendements.mean(axis=1) * 252
    with np.errstate(divide="ignore", invalid="ignore"):
        sharpes = np.where(vol_ann > 0, (rend_ann - taux_sans_risque) / vol_ann, 0.0)
    plus_hauts = np.maximum.accumulate(valeurs, axis=1)
    max_dd = ((plus_hauts - valeurs) / plus_hauts).max(axis=1)
    finales = valeurs[:, -1]

    return {
        "vol_ann": float(np.median(vol_ann) * 100),
        "sharpe": float(np.median(sharpes)),
        "max_dd": float(np.median(max_dd) * 100),
        "var_95": float(np.percentile(rendements, 5) * 100),
        "valeur_p5": float(np.percentile(finales, 5)),
        "valeur_mediane": float(np.median(finales)),
        "valeur_p95": float(np.percentile(finales, 95)),
        "proba_perte": float((finales < capital).mean() * 100),
    }


def metriques_du_resultat(
    resultat: Dict,
    valeur_portefeuille: Iterable[float],
    poids: Dict[str, float],
    capital: float,
    taux_sans_risque: float = TAUX_SANS_RISQUE_ANNUEL,
) -> Dict[str, float]:
    """Choisit le bon calcul : sur les trajectoires Monte-Carlo si le resultat
    en contient, sinon sur la serie de valeur du portefeuille."""
    mc = resultat.get("mc_data") if isinstance(resultat, dict) else None
    if mc and mc.get("chemins") is not None:
        metriques = calculer_metriques_monte_carlo(
            mc["chemins"], list(mc["colonnes"]), poids, capital, taux_sans_risque
        )
        if metriques is not None:
            return metriques
    return calculer_metriques_risque(valeur_portefeuille, taux_sans_risque)


def bandes_portefeuille_monte_carlo(
    chemins: np.ndarray,
    colonnes: List[str],
    poids: Dict[str, float],
    capital: float,
) -> Optional[Dict[str, np.ndarray]]:
    """
    Enveloppe 5%-95% de la valeur du portefeuille, jour par jour.

    Calculee sur les trajectoires du portefeuille entier : additionner les
    percentiles de chaque actif serait faux (les pires cas de tous les actifs
    n'arrivent pas le meme jour).

    Returns:
        {"bas", "mediane", "haut"} : tableaux de longueur `jours`. None si
        aucun actif du portefeuille n'est simule.
    """
    idx = [colonnes.index(k) for k in poids if k in colonnes]
    if not idx or chemins is None or len(chemins) == 0:
        return None
    w = np.array([poids[colonnes[i]] for i in idx], dtype=float)
    if w.sum() <= 0:
        return None
    w = w / w.sum()
    prix = chemins[:, :, idx].astype(float)
    valeurs = capital * (prix / prix[:, :1, :] * w).sum(axis=2)
    bas, mediane, haut = np.percentile(valeurs, [5, 50, 95], axis=0)
    return {"bas": bas, "mediane": mediane, "haut": haut}
