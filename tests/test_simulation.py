"""
tests/test_simulation.py
========================
Tests du moteur de simulation : la mediane respecte le choc de l'IA, la
volatilite et les correlations simulees sont celles demandees, la conversion
en euros est coherente, le profil "crise" et la fourchette de l'IA sont respectes.
"""

import numpy as np
import pandas as pd
import pytest

from config import CRISE_DEPASSEMENT, CRISE_FRACTION_CREUX
from simulation import (
    construire_correlations, generer_chemins, profil_choc,
    simuler_marche_dynamique, simuler_monte_carlo, tirer_chocs,
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


# === Profil de choc "crise" ================================================


@pytest.mark.parametrize("modele", MODELES)
@pytest.mark.parametrize("pas", [1, 9, 29, 99, 249])
def test_profil_de_choc_realise_tout_le_choc(modele, pas):
    profil = profil_choc(modele, pas)
    assert len(profil) == pas
    assert profil.sum() == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("modele", MODELES[:2])
def test_profil_crise_chute_vite_depasse_puis_rebondit(modele):
    pas = 100
    profil = profil_choc(modele, pas)
    cumul = np.cumsum(profil)
    creux = int(np.argmax(cumul))
    # Le point extreme arrive vers 20 % de l'horizon et va 30 % au-dela du choc final
    assert creux + 1 == pytest.approx(CRISE_FRACTION_CREUX * pas, abs=1)
    assert cumul.max() == pytest.approx(1 + CRISE_DEPASSEMENT, abs=0.01)
    # L'essentiel du mouvement est fait a 10 % de l'horizon
    assert cumul[pas // 10 - 1] > 0.9
    # Chute la plus forte au debut, puis rebond partiel (pas negatifs) jusqu'au choc final
    assert profil[0] > profil[5] > 0
    assert (profil[creux + 1:] <= 0).all()
    assert cumul[-1] == pytest.approx(1.0)


def test_profil_tendance_reste_progressif():
    profil = profil_choc("Machine Learning (Tendance)", 100)
    assert (profil > 0).all()
    assert (np.diff(profil) > 0).all()                      # le choc s'accelere
    assert np.cumsum(profil).max() == pytest.approx(1.0)    # pas de depassement


def test_trajectoire_mediane_a_la_forme_crise():
    chocs = {"actifs": {"S&P 500": -0.20, "Or": 0.10}}
    mc = simuler_monte_carlo(chocs, jours=100, actifs=["S&P 500", "Or"],
                             nb_simulations=3000, graine=11)
    perf = mc["mediane"] / mc["mediane"].iloc[0] - 1
    creux = int(round(CRISE_FRACTION_CREUX * 99))
    attendu_creux = np.expm1(np.log1p(-0.20) * (1 + CRISE_DEPASSEMENT))
    assert perf["S&P 500"].iloc[creux] == pytest.approx(attendu_creux, abs=0.015)
    assert perf["S&P 500"].iloc[creux] < perf["S&P 500"].iloc[-1] - 0.03   # rebond partiel
    assert perf["Or"].iloc[creux] > perf["Or"].iloc[-1]                     # sommet puis repli
    assert perf["S&P 500"].iloc[-1] == pytest.approx(-0.20, abs=0.015)


# === Doute de l'IA : fourchette bas / central / haut =======================

FOURCHETTES = {
    "actifs": {"S&P 500": -0.18, "Or": 0.08},
    "fourchettes": {
        "S&P 500": {"bas": -0.35, "central": -0.18, "haut": -0.10},
        "Or": {"bas": 0.02, "central": 0.08, "haut": 0.20},
    },
}


def test_chocs_tires_dans_la_fourchette():
    rng = np.random.default_rng(0)
    bas, central, haut = np.array([-0.35, 0.02]), np.array([-0.18, 0.08]), np.array([-0.10, 0.20])
    tires = tirer_chocs(bas, central, haut, 20000, rng)
    assert tires.shape == (20000, 2)
    assert (tires >= bas).all() and (tires <= haut).all()
    # Mediane = central meme quand la fourchette est asymetrique
    assert np.median(tires, axis=0) == pytest.approx(central, abs=0.005)
    assert tires.min(axis=0) == pytest.approx(bas, abs=0.01)
    assert tires.max(axis=0) == pytest.approx(haut, abs=0.01)
    # Gravite commune : quand le S&P 500 chute plus fort, l'or monte plus fort
    assert np.corrcoef(tires.T)[0, 1] < -0.6


def test_chaque_trajectoire_finit_dans_la_fourchette():
    # Volatilite quasi nulle : la performance finale de chaque trajectoire = son choc tire
    _, chemins = generer_chemins(FOURCHETTES, jours=60, actifs=["S&P 500", "Or"],
                                 nb_simulations=2000, vols_reelles={"S&P 500": 1e-9, "Or": 1e-9},
                                 graine=12, incertitude_ia=True)
    perf = chemins[:, -1, :] / chemins[:, 0, :] - 1
    assert (perf[:, 0] >= -0.35 - 1e-6).all() and (perf[:, 0] <= -0.10 + 1e-6).all()
    assert (perf[:, 1] >= 0.02 - 1e-6).all() and (perf[:, 1] <= 0.20 + 1e-6).all()
    assert np.median(perf, axis=0) == pytest.approx([-0.18, 0.08], abs=0.005)


@pytest.mark.parametrize("modele", MODELES)
def test_mediane_reste_proche_du_central_avec_fourchette(modele):
    mc = simuler_monte_carlo(FOURCHETTES, jours=100, modele=modele,
                             actifs=["S&P 500", "Or"], nb_simulations=4000, graine=13)
    perf = mc["mediane"].iloc[-1] / mc["mediane"].iloc[0] - 1
    assert perf["S&P 500"] == pytest.approx(-0.18, abs=0.02)
    assert perf["Or"] == pytest.approx(0.08, abs=0.02)


def test_le_doute_de_l_ia_elargit_l_intervalle():
    sans = simuler_monte_carlo({"actifs": FOURCHETTES["actifs"]}, jours=100,
                               actifs=["S&P 500", "Or"], nb_simulations=3000, graine=14)
    avec = simuler_monte_carlo(FOURCHETTES, jours=100,
                               actifs=["S&P 500", "Or"], nb_simulations=3000, graine=14)

    def largeur(mc):
        return (mc["haut"].iloc[-1] - mc["bas"].iloc[-1]) / mc["mediane"].iloc[0]
    assert (largeur(avec) > largeur(sans)).all()
    assert largeur(avec)["S&P 500"] > largeur(sans)["S&P 500"] * 1.1


def test_sans_fourchette_monte_carlo_inchange():
    """Ancienne reponse IA (pas de fourchette) : exactement les memes trajectoires."""
    chocs = {"actifs": {"S&P 500": -0.18, "Or": 0.08}}
    _, certain = generer_chemins(chocs, jours=30, actifs=["S&P 500", "Or"],
                                 nb_simulations=50, graine=15)
    _, incertain = generer_chemins(chocs, jours=30, actifs=["S&P 500", "Or"],
                                   nb_simulations=50, graine=15, incertitude_ia=True)
    np.testing.assert_array_equal(certain, incertain)


def test_fourchette_d_un_autre_central_ignoree():
    chocs = {"actifs": {"S&P 500": -0.18},
             "fourchettes": {"S&P 500": {"bas": -0.05, "central": 0.0, "haut": 0.05}}}
    _, avec = generer_chemins(chocs, jours=30, actifs=["S&P 500"], nb_simulations=50,
                              graine=16, incertitude_ia=True)
    _, sans = generer_chemins({"actifs": chocs["actifs"]}, jours=30, actifs=["S&P 500"],
                              nb_simulations=50, graine=16)
    np.testing.assert_array_equal(avec, sans)


def test_trajectoire_unique_reste_sur_le_central():
    """Hors Monte-Carlo, une seule trajectoire : on garde le choc central."""
    df = simuler_marche_dynamique(FOURCHETTES, jours=60, actifs=["S&P 500"],
                                  vols_reelles={"S&P 500": 1e-9}, graine=17)
    assert df["S&P 500"].iloc[-1] / df["S&P 500"].iloc[0] - 1 == pytest.approx(-0.18, abs=1e-4)


def test_choc_entre_300_et_500_pourcent_reste_un_decimal():
    # VIX borne a +500 % dans schemas.py : 4.0 = +400 %, pas 4 %
    df = simuler_marche_dynamique({"actifs": {"VIX": 4.0}}, jours=60, actifs=["VIX"],
                                  vols_reelles={"VIX": 1e-9}, graine=18)
    assert df["VIX"].iloc[-1] / df["VIX"].iloc[0] - 1 == pytest.approx(4.0, rel=1e-3)
