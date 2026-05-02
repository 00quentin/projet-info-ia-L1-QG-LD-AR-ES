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
