"""
tests/test_simulation.py
========================
Tests du moteur de simulation : la mediane respecte le choc de l'IA, la
volatilite et les correlations simulees sont celles demandees, la conversion
en euros est coherente.
"""

import numpy as np
import pandas as pd
import pytest

from simulation import (
    construire_correlations, generer_chemins,
    simuler_marche_dynamique, simuler_monte_carlo,
)

MODELES = ["Probabiliste (Réaliste)", "Historique (Chocs violents)",
           "Machine Learning (Tendance)"]


def _rendements_correles(n=400, rho=0.9, graine=0):
    rng = np.random.default_rng(graine)
    commun = rng.standard_normal(n)
    a = 0.01 * commun
    b = 0.01 * (rho * commun + np.sqrt(1 - rho ** 2) * rng.standard_normal(n))
    return pd.DataFrame({"S&P 500": a, "NASDAQ": b})


@pytest.mark.parametrize("modele", MODELES)
def test_mediane_atteint_le_choc_ia(modele):
    chocs = {"actifs": {"S&P 500": -0.20, "Or": 0.10}}
    mc = simuler_monte_carlo(chocs, jours=100, modele=modele,
                             actifs=["S&P 500", "Or"], nb_simulations=3000, graine=1)
    perf = mc["mediane"].iloc[-1] / mc["mediane"].iloc[0] - 1
    assert perf["S&P 500"] == pytest.approx(-0.20, abs=0.015)
    assert perf["Or"] == pytest.approx(0.10, abs=0.015)
    assert (mc["bas"].iloc[-1] < mc["mediane"].iloc[-1]).all()
    assert (mc["mediane"].iloc[-1] < mc["haut"].iloc[-1]).all()


def test_volatilite_simulee_egale_volatilite_demandee():
    _, chemins = generer_chemins({"actifs": {}}, jours=250, actifs=["S&P 500"],
                                 nb_simulations=200, vols_reelles={"S&P 500": 0.02},
                                 graine=2)
    rendements = np.diff(np.log(chemins[:, :, 0]), axis=1)
    assert rendements.std() == pytest.approx(0.02, rel=0.03)


def test_prix_initial_reel_utilise():
    df = simuler_marche_dynamique({"actifs": {}}, jours=10, actifs=["S&P 500"],
                                  prix_reels={"S&P 500": 1234.0}, graine=3)
    assert df["S&P 500"].iloc[0] == 1234.0
    assert len(df) == 10
    assert (df > 0).all().all()


@pytest.mark.parametrize("modele", MODELES)
def test_correlations_reelles_reproduites(modele):
    hist = _rendements_correles(rho=0.9)
    _, chemins = generer_chemins({"actifs": {}}, jours=250, modele=modele,
                                 actifs=["S&P 500", "NASDAQ"], nb_simulations=100,
                                 rendements_historiques=hist, graine=4)
    r = np.diff(np.log(chemins), axis=1).reshape(-1, 2)
    assert np.corrcoef(r.T)[0, 1] == pytest.approx(0.9, abs=0.05)


def test_correlations_de_secours_sans_historique():
    corr = construire_correlations(["S&P 500", "NASDAQ", "VIX", "Or", "PERSO_TSLA"])
    assert corr[0, 1] > 0.5          # actions entre elles
    assert corr[0, 2] < -0.5         # actions vs VIX
    assert np.allclose(np.diag(corr), 1.0)
    assert np.linalg.eigvalsh(corr).min() > 0   # matrice exploitable (Cholesky)


def test_correlations_incoherentes_sont_reparees():
    # Correlations mesurees impossibles a satisfaire ensemble
    idx = ["S&P 500", "NASDAQ", "Or"]
    rng = np.random.default_rng(0)
    base = rng.standard_normal(200)
    hist = pd.DataFrame({"S&P 500": base, "NASDAQ": base * 0.999 + 0.001 * rng.standard_normal(200),
                         "Or": -base}, columns=idx)
    corr = construire_correlations(idx, hist)
    assert np.linalg.eigvalsh(corr).min() > 0


def test_chocs_en_pourcentage_sont_normalises():
    mc = simuler_monte_carlo({"actifs": {"Or": 25}}, jours=50, actifs=["Or"],
                             nb_simulations=2000, graine=5)
    perf = mc["mediane"]["Or"].iloc[-1] / mc["mediane"]["Or"].iloc[0] - 1
    assert perf == pytest.approx(0.25, abs=0.02)


def test_conversion_euros_dollar_qui_baisse_reduit_la_performance():
    # S&P 500 stable en dollars, euro qui s'apprecie de 10% : perte en euros
    chocs = {"actifs": {"S&P 500": 0.0, "EUR_USD": 0.10, "CAC 40": 0.0}}
    mc = simuler_monte_carlo(chocs, jours=100, actifs=["S&P 500", "CAC 40", "EUR_USD"],
                             nb_simulations=3000, actifs_en_usd=["S&P 500"], graine=6,
                             prix_reels={"S&P 500": 5000.0, "EUR_USD": 1.25})
    med = mc["mediane"]
    assert med["S&P 500"].iloc[0] == pytest.approx(4000.0)   # 5000 $ / 1.25
    assert med["S&P 500"].iloc[-1] / med["S&P 500"].iloc[0] - 1 == pytest.approx(-1 / 11, abs=0.02)
    assert med["CAC 40"].iloc[-1] / med["CAC 40"].iloc[0] - 1 == pytest.approx(0.0, abs=0.02)


def test_monte_carlo_conserve_un_echantillon_de_chemins():
    mc = simuler_monte_carlo({"actifs": {}}, jours=20, actifs=["S&P 500", "Or"],
                             nb_simulations=50, graine=7)
    assert mc["chemins"].shape == (50, 20, 2)
    assert mc["colonnes"] == ["S&P 500", "Or"]


def test_actif_personnalise_simule():
    df = simuler_marche_dynamique(
        {"actifs": {"PERSO_TSLA": 0.3}}, jours=30, actifs=["PERSO_TSLA"],
        actifs_extras={"PERSO_TSLA": {"prix": 250.0, "volatilite": 0.03, "devise": "USD"}},
        graine=8,
    )
    assert list(df.columns) == ["PERSO_TSLA"]
    assert df["PERSO_TSLA"].iloc[0] == 250.0
