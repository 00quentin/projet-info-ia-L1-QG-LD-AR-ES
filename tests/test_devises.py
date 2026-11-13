"""
tests/test_devises.py
=====================
Tests de la conversion en euros (taux BCE fournis en dur, pas de reseau).
"""

import numpy as np
import pandas as pd
import pytest

from core.devises import convertir_en_eur


def _taux():
    idx = pd.bdate_range("2024-01-01", periods=10)
    return pd.DataFrame({"USD": [1.10] * 5 + [1.21] * 5, "JPY": [160.0] * 10}, index=idx)


def test_conversion_divise_par_le_taux_du_jour():
    idx = pd.bdate_range("2024-01-01", periods=10)
    prix = pd.DataFrame({"S&P 500": [110.0] * 10, "CAC 40": [50.0] * 10}, index=idx)
    out, non_convertis = convertir_en_eur(
        prix, {"S&P 500": "USD", "CAC 40": "EUR"}, _taux())
    assert non_convertis == []
    assert out["S&P 500"].iloc[0] == pytest.approx(100.0)
    assert out["S&P 500"].iloc[-1] == pytest.approx(110.0 / 1.21)
    assert (out["CAC 40"] == 50.0).all()


def test_indicateurs_sans_devise_non_convertis():
    idx = pd.bdate_range("2024-01-01", periods=3)
    prix = pd.DataFrame({"VIX": [18.0, 19.0, 20.0]}, index=idx)
    out, non_convertis = convertir_en_eur(prix, {"VIX": None}, _taux())
    assert out.equals(prix) and non_convertis == []


def test_week_end_utilise_le_dernier_taux_connu():
    idx = pd.date_range("2024-01-05", periods=3)   # vendredi, samedi, dimanche
    prix = pd.DataFrame({"Bitcoin": [1.10, 1.10, 1.10]}, index=idx)
    out, _ = convertir_en_eur(prix, {"Bitcoin": "USD"}, _taux())
    assert np.allclose(out["Bitcoin"].values, 1.0)


def test_taux_absent_signale_sans_planter():
    idx = pd.bdate_range("1995-01-02", periods=3)   # avant l'euro
    prix = pd.DataFrame({"S&P 500": [1.0, 2.0, 3.0], "Gilt_10Y": [1.0, 1.0, 1.0]}, index=idx)
    out, non_convertis = convertir_en_eur(
        prix, {"S&P 500": "USD", "Gilt_10Y": "GBP"}, _taux())
    assert set(non_convertis) == {"S&P 500", "Gilt_10Y"}
    assert out.equals(prix)
    out, non_convertis = convertir_en_eur(prix, {"S&P 500": "USD"}, pd.DataFrame())
    assert non_convertis == ["S&P 500"]
