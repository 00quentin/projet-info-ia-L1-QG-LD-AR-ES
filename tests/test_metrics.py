"""
tests/test_metrics.py
=====================
Tests des metriques de risque institutionnelles.
On verifie les invariants mathematiques (signe, plages) plutot que
des valeurs exactes a 8 decimales : les formules peuvent evoluer mais
les invariants restent.
"""

import math
import numpy as np
import pandas as pd
import pytest

from core.metrics import calculer_metriques_risque, evaluer_qualite_sharpe


# === calculer_metriques_risque ===========================================

def test_serie_constante_renvoie_zeros():
    """Une serie plate -> volatilite, sharpe, dd, var tous a 0."""
    serie = [10000.0] * 50
    m = calculer_metriques_risque(serie)
    assert m == {"vol_ann": 0.0, "sharpe": 0.0, "max_dd": 0.0, "var_95": 0.0}


def test_serie_vide_ne_crashe_pas():
    """Edge case : serie sans donnees -> retour neutre, pas d'exception."""
    m = calculer_metriques_risque([])
    assert m == {"vol_ann": 0.0, "sharpe": 0.0, "max_dd": 0.0, "var_95": 0.0}


def test_serie_un_seul_point_ne_crashe_pas():
    m = calculer_metriques_risque([10000.0])
    assert m == {"vol_ann": 0.0, "sharpe": 0.0, "max_dd": 0.0, "var_95": 0.0}


def test_serie_haussiere_sharpe_positif():
    """Une croissance lineaire reguliere a un Sharpe tres positif (peu de vol)."""
    serie = np.linspace(10000, 12000, 100)
    m = calculer_metriques_risque(serie)
    assert m["sharpe"] > 0
    assert m["vol_ann"] >= 0


def test_serie_baissiere_sharpe_negatif():
    """Une decroissance lineaire reguliere a un Sharpe tres negatif."""
    serie = np.linspace(10000, 8000, 100)
    m = calculer_metriques_risque(serie)
    assert m["sharpe"] < 0


def test_max_drawdown_calcule_correctement():
    """Si la serie monte a 12000 puis tombe a 9000, dd = 25%."""
    serie = list(np.linspace(10000, 12000, 50)) + list(np.linspace(12000, 9000, 50))
    m = calculer_metriques_risque(serie)
    # 12000 -> 9000 = -25%, on accepte une marge a cause de la pas-a-pas
    assert 24.0 <= m["max_dd"] <= 26.0


def test_drawdown_jamais_negatif():
    """Le max drawdown ne peut etre negatif par definition."""
    rng = np.random.default_rng(42)
    serie = 10000 * np.cumprod(1 + rng.normal(0, 0.01, 100))
    m = calculer_metriques_risque(serie)
    assert m["max_dd"] >= 0


def test_volatilite_annualisee_positive():
    """Toute serie volatile a une vol_ann strictement positive."""
    rng = np.random.default_rng(7)
    serie = 10000 * np.cumprod(1 + rng.normal(0, 0.02, 100))
    m = calculer_metriques_risque(serie)
    assert m["vol_ann"] > 0


def test_var_95_negative_ou_nulle():
    """La VaR au quantile 5% est par construction <= 0 (perte).
    Un cas marginal peut donner 0 si tous les rendements sont positifs."""
    rng = np.random.default_rng(7)
    serie = 10000 * np.cumprod(1 + rng.normal(0, 0.02, 100))
    m = calculer_metriques_risque(serie)
    assert m["var_95"] <= 0.0


def test_pandas_series_acceptee():
    """Le calcul accepte aussi des pd.Series, pas que des listes."""
    serie = pd.Series(np.linspace(10000, 11000, 60))
    m = calculer_metriques_risque(serie)
    assert isinstance(m["sharpe"], float)


def test_resultat_toujours_floats():
    """Important pour la serialisation JSON / passage au PDF."""
    rng = np.random.default_rng(1)
    serie = 10000 * np.cumprod(1 + rng.normal(0, 0.01, 50))
    m = calculer_metriques_risque(serie)
    for k, v in m.items():
        assert isinstance(v, float), f"{k} doit etre float, est {type(v)}"
        assert math.isfinite(v), f"{k} doit etre fini, vaut {v}"


# === evaluer_qualite_sharpe ===============================================

@pytest.mark.parametrize("sharpe, attendu", [
    (-1.5, "Mauvais"),
    (-0.01, "Mauvais"),
    (0.0, "Acceptable"),
    (0.5, "Acceptable"),
    (0.99, "Acceptable"),
    (1.0, "Bon"),
    (1.5, "Bon"),
    (1.99, "Bon"),
    (2.0, "Excellent"),
    (3.5, "Excellent"),
])
def test_evaluer_qualite_sharpe(sharpe, attendu):
    assert evaluer_qualite_sharpe(sharpe) == attendu


# === Metriques sur trajectoires Monte-Carlo ================================


def _chemins_gaussiens(nb=400, jours=120, vol=0.01, graine=0):
    rng = np.random.default_rng(graine)
    r = rng.normal(0, vol, size=(nb, jours - 1, 2))
    chemins = np.ones((nb, jours, 2)) * 100.0
    chemins[:, 1:, :] = 100.0 * np.exp(np.cumsum(r, axis=1))
    return chemins


def test_metriques_monte_carlo_mesurent_le_vrai_risque():
    from core.metrics import calculer_metriques_monte_carlo, calculer_metriques_risque
    chemins = _chemins_gaussiens()
    m = calculer_metriques_monte_carlo(chemins, ["A", "B"], {"A": 1.0}, 10_000)
    # Vol annualisee attendue : 1% x sqrt(252) ~ 15.9%
    assert m["vol_ann"] == pytest.approx(15.9, rel=0.08)
    assert m["var_95"] == pytest.approx(-1.645, rel=0.1)
    assert 30 < m["proba_perte"] < 70
    assert m["valeur_p5"] < m["valeur_mediane"] < m["valeur_p95"]
    # La trajectoire mediane, elle, sous-estime massivement la volatilite
    mediane = np.median(chemins[:, :, 0], axis=0)
    assert calculer_metriques_risque(mediane)["vol_ann"] < m["vol_ann"] / 3


def test_metriques_monte_carlo_diversification():
    from core.metrics import calculer_metriques_monte_carlo
    chemins = _chemins_gaussiens()
    seul = calculer_metriques_monte_carlo(chemins, ["A", "B"], {"A": 1.0}, 1000)
    mixte = calculer_metriques_monte_carlo(chemins, ["A", "B"], {"A": 0.5, "B": 0.5}, 1000)
    # Deux actifs independants : la vol du 50/50 est ~ vol / sqrt(2)
    assert mixte["vol_ann"] == pytest.approx(seul["vol_ann"] / np.sqrt(2), rel=0.1)


def test_metriques_du_resultat_choisit_la_bonne_methode():
    from core.metrics import metriques_du_resultat
    chemins = _chemins_gaussiens()
    serie = chemins[0, :, 0]
    sans_mc = metriques_du_resultat({"mc_data": None}, serie, {"A": 1.0}, 100)
    assert "proba_perte" not in sans_mc
    avec_mc = metriques_du_resultat(
        {"mc_data": {"chemins": chemins, "colonnes": ["A", "B"]}}, serie, {"A": 1.0}, 100)
    assert "proba_perte" in avec_mc
    # Aucun actif du portefeuille dans les chemins -> repli sur la serie
    repli = metriques_du_resultat(
        {"mc_data": {"chemins": chemins, "colonnes": ["A", "B"]}}, serie, {"Z": 1.0}, 100)
    assert "proba_perte" not in repli
