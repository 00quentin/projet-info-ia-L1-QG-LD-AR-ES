"""
tests/test_conjoncture.py
=========================
Tests de la mise en forme de la conjoncture (series FRED fournies en dur, pas de reseau)
et de la transmission du taux sans risque au ratio de Sharpe.
"""

import numpy as np
import pandas as pd
import pytest

from config import TAUX_SANS_RISQUE_ANNUEL
from core.conjoncture import construire_conjoncture, taux_sans_risque, texte_pour_ia, variation_sur_un_an
from core.metrics import calculer_metriques_risque
from ia_bot import _build_prompt_macro


def _mensuelle(valeurs, debut="2024-01-01"):
    return pd.Series(valeurs, index=pd.date_range(debut, periods=len(valeurs), freq="MS"), dtype=float)


def test_inflation_sur_un_an():
    indice = _mensuelle([100.0] * 12 + [103.0])
    variation, date = variation_sur_un_an(indice)
    assert variation == pytest.approx(3.0)
    assert date == pd.Timestamp("2025-01-01")
    assert variation_sur_un_an(_mensuelle([100.0] * 6)) is None


def test_construire_conjoncture_omet_les_series_absentes():
    taux = pd.Series([2.0, 2.25, 2.5], index=pd.to_datetime(["2026-11-07", "2026-11-10", "2026-11-11"]))
    c = construire_conjoncture({"taux_bce": taux, "inflation_ze": _mensuelle([100.0] * 12 + [104.0]),
                                "taux_fed": pd.Series(dtype=float)})
    cles = [i["cle"] for i in c["indicateurs"]]
    assert cles == ["taux_bce", "inflation_ze"]
    assert c["indicateurs"][0]["valeur"] == 2.5
    assert c["indicateurs"][1]["valeur"] == pytest.approx(4.0)
    assert c["date"] == "2026-11-11"
    assert "Taux de dépôt BCE : 2.50 %" in texte_pour_ia(c)


def test_taux_sans_risque_actuel_et_historique():
    serie = pd.Series([0.0, 1.0, 3.0], index=pd.to_datetime(["2020-06-01", "2022-06-01", "2024-06-01"]))
    assert taux_sans_risque(serie) == pytest.approx(0.03)
    assert taux_sans_risque(serie, "2020-01-01", "2022-12-31") == pytest.approx(0.005)
    # Periode non couverte (avant l'euro) ou serie vide : valeur de secours
    assert taux_sans_risque(serie, "1990-01-01", "1995-01-01") == TAUX_SANS_RISQUE_ANNUEL
    assert taux_sans_risque(pd.Series(dtype=float)) == TAUX_SANS_RISQUE_ANNUEL


def test_le_taux_sans_risque_change_le_sharpe():
    rng = np.random.default_rng(0)
    valeurs = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, 250)))
    bas = calculer_metriques_risque(valeurs, 0.0)["sharpe"]
    haut = calculer_metriques_risque(valeurs, 0.05)["sharpe"]
    assert bas > haut


def test_la_conjoncture_est_dans_le_prompt():
    prompt = _build_prompt_macro("krach bancaire", conjoncture="- Taux de dépôt BCE : 2.50 % (au 2026-11-11)")
    assert "CONJONCTURE DE DEPART" in prompt and "2.50 %" in prompt
    assert "CONJONCTURE DE DEPART" not in _build_prompt_macro("krach bancaire")
