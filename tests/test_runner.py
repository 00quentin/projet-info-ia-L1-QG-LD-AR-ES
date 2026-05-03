"""
tests/test_runner.py
====================
Tests des orchestrateurs core/runner.py.

On mocke `analyser_evenement_macro` (appel OpenAI) et les deux moteurs de
simulation (`simuler_marche_dynamique`, `simuler_monte_carlo`) via
monkeypatch sur le module `core.runner` -- c'est la qu'ils sont resolus
au moment de l'appel. Les tests valident la logique d'orchestration :
gestion des erreurs IA, branchement MC vs dynamique, calcul de perf,
mapping NOM_AFFICHAGE, tri ascendant, et helpers du backtest.
"""

import pandas as pd
import pytest

from core import runner


# === Fixtures =============================================================


@pytest.fixture
def df_simu():
    """Trois actifs sur 4 jours, perfs distinctes pour verifier le tri."""
    return pd.DataFrame(
        {
            "S&P 500":   [100.0, 102.0, 105.0, 110.0],   # +10%
            "Or":        [100.0,  99.0,  98.0,  95.0],   # -5%
            "EUR_USD":   [1.00,   1.01,  1.02,  1.04],   # +4%
        }
    )


@pytest.fixture
def df_histo():
    """DataFrame Yahoo simule : 2 actifs presents, 1 demande mais absent."""
    return pd.DataFrame(
        {
            "S&P 500": [100.0, 110.0, 120.0],
            "Or":      [100.0,  90.0,  80.0],
        }
    )


# === lancer_simulation_scenario : erreurs IA ==============================


def test_simulation_propage_erreur_explicite_de_lia(monkeypatch):
    """Si l'IA renvoie {'erreur': ...} seul, le runner remonte l'erreur."""
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda scenario, calibration_historique: {"erreur": "API indisponible"}
    )

    res, err = runner.lancer_simulation_scenario(
        scenario="krach", actifs_selectionnes=["S&P 500"], duree=10,
        modele="GBM", monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    assert res is None
    assert err == "API indisponible"


def test_simulation_rejette_chocs_vides(monkeypatch):
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda scenario, calibration_historique: {}
    )

    res, err = runner.lancer_simulation_scenario(
        scenario="bla", actifs_selectionnes=["S&P 500"], duree=10,
        modele="GBM", monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    assert res is None
    assert "n'a pas pu lier" in err


def test_simulation_rejette_chocs_sans_actifs_ni_macro(monkeypatch):
    """Un dict IA qui n'a ni 'actifs' ni 'macro' est juge invalide."""
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda scenario, calibration_historique: {"commentaire": "rien"}
    )

    res, err = runner.lancer_simulation_scenario(
        scenario="bla", actifs_selectionnes=["S&P 500"], duree=10,
        modele="GBM", monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    assert res is None
    assert err is not None


def test_simulation_accepte_chocs_avec_seulement_macro(monkeypatch, df_simu):
    """Un payload IA contenant uniquement 'macro' est valide."""
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda scenario, calibration_historique: {"macro": {"taux": 0.5}}
    )
    monkeypatch.setattr(
        runner, "simuler_marche_dynamique",
        lambda *a, **kw: df_simu
    )

    res, err = runner.lancer_simulation_scenario(
        scenario="hausse taux", actifs_selectionnes=["S&P 500"], duree=10,
        modele="GBM", monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    assert err is None
    assert res is not None


# === lancer_simulation_scenario : modes MC et dynamique ===================


def test_simulation_mode_dynamique_renvoie_structure_complete(monkeypatch, df_simu):
    chocs_ia = {"actifs": {"S&P 500": -10}, "macro": {}}
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda scenario, calibration_historique: chocs_ia
    )
    monkeypatch.setattr(
        runner, "simuler_marche_dynamique",
        lambda *a, **kw: df_simu
    )

    res, err = runner.lancer_simulation_scenario(
        scenario="krach", actifs_selectionnes=["S&P 500", "Or", "EUR_USD"],
        duree=4, modele="GBM", monte_carlo=False,
        prix_reels=None, vols_reelles=None, calibration_historique=False,
    )

    assert err is None
    assert set(res.keys()) == {"scenario", "chocs_ia", "df", "mc_data", "perf", "perf_df"}
    assert res["scenario"] == "krach"
    assert res["chocs_ia"] is chocs_ia
    assert res["mc_data"] is None  # pas de MC en mode dynamique
    assert res["df"] is df_simu


def test_simulation_mode_monte_carlo_utilise_mediane(monkeypatch, df_simu):
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda scenario, calibration_historique: {"actifs": {"S&P 500": 5}}
    )

    appels = {"dyn": 0, "mc": 0}

    def fake_mc(*a, **kw):
        appels["mc"] += 1
        return {"mediane": df_simu, "p10": df_simu, "p90": df_simu}

    def fake_dyn(*a, **kw):
        appels["dyn"] += 1
        return df_simu

    monkeypatch.setattr(runner, "simuler_monte_carlo", fake_mc)
    monkeypatch.setattr(runner, "simuler_marche_dynamique", fake_dyn)

    res, err = runner.lancer_simulation_scenario(
        scenario="boom", actifs_selectionnes=["S&P 500"], duree=4,
        modele="GBM", monte_carlo=True,
        prix_reels=None, vols_reelles=None, calibration_historique=False,
    )

    assert err is None
    assert appels == {"mc": 1, "dyn": 0}
    assert res["mc_data"]["mediane"] is df_simu
    assert res["df"] is df_simu  # pointe sur la mediane


def test_simulation_calcul_perf_correct(monkeypatch, df_simu):
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda *a, **kw: {"actifs": {}}
    )
    monkeypatch.setattr(runner, "simuler_marche_dynamique", lambda *a, **kw: df_simu)

    res, _ = runner.lancer_simulation_scenario(
        scenario="x", actifs_selectionnes=[], duree=4, modele="GBM",
        monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    perf = res["perf"]
    assert perf["S&P 500"] == pytest.approx(10.0)
    assert perf["Or"] == pytest.approx(-5.0)
    assert perf["EUR_USD"] == pytest.approx(4.0)


def test_simulation_perf_df_trie_ascendant(monkeypatch, df_simu):
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda *a, **kw: {"actifs": {}}
    )
    monkeypatch.setattr(runner, "simuler_marche_dynamique", lambda *a, **kw: df_simu)

    res, _ = runner.lancer_simulation_scenario(
        scenario="x", actifs_selectionnes=[], duree=4, modele="GBM",
        monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    perfs = res["perf_df"]["Performance (%)"].tolist()
    assert perfs == sorted(perfs)  # plus mauvais en haut


def test_simulation_libelles_via_nom_affichage(monkeypatch, df_simu):
    """Les codes presents dans NOM_AFFICHAGE prennent le libelle officiel."""
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda *a, **kw: {"actifs": {}}
    )
    monkeypatch.setattr(runner, "simuler_marche_dynamique", lambda *a, **kw: df_simu)

    res, _ = runner.lancer_simulation_scenario(
        scenario="x", actifs_selectionnes=[], duree=4, modele="GBM",
        monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    libelles = res["perf_df"]["Actif"].tolist()
    assert "S&P 500 (USA)" in libelles
    assert "EUR/USD (Euro-Dollar)" in libelles
    # Aucun underscore brut ne doit fuiter
    assert not any("_" in lib for lib in libelles)


def test_simulation_fallback_underscore_pour_code_inconnu(monkeypatch):
    """Un code hors NOM_AFFICHAGE perd ses underscores a l'affichage."""
    df = pd.DataFrame({"ACTIF_INCONNU_X": [100.0, 110.0]})
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda *a, **kw: {"actifs": {}}
    )
    monkeypatch.setattr(runner, "simuler_marche_dynamique", lambda *a, **kw: df)

    res, _ = runner.lancer_simulation_scenario(
        scenario="x", actifs_selectionnes=[], duree=2, modele="GBM",
        monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    assert res["perf_df"]["Actif"].tolist() == ["ACTIF INCONNU X"]


# === lancer_backtest ======================================================


def test_backtest_retourne_none_sur_dataframe_vide():
    assert runner.lancer_backtest(pd.DataFrame(), ["S&P 500"]) is None


def test_backtest_calcule_perf_et_tri(df_histo):
    res = runner.lancer_backtest(df_histo, ["S&P 500", "Or"])

    assert res is not None
    assert res["df"] is df_histo
    assert res["perf"]["S&P 500"] == pytest.approx(20.0)
    assert res["perf"]["Or"] == pytest.approx(-20.0)
    perfs = res["perf_df"]["Performance (%)"].tolist()
    assert perfs == sorted(perfs)


def test_backtest_detecte_actifs_indisponibles(df_histo):
    """Yahoo n'a pas renvoye 'NASDAQ' -> il doit apparaitre dans indisponibles."""
    res = runner.lancer_backtest(df_histo, ["S&P 500", "Or", "NASDAQ"])

    assert set(res["actifs_disponibles"]) == {"S&P 500", "Or"}
    assert res["actifs_indisponibles"] == ["NASDAQ"]


def test_backtest_indisponibles_vide_si_tout_present(df_histo):
    res = runner.lancer_backtest(df_histo, ["S&P 500", "Or"])
    assert res["actifs_indisponibles"] == []


# === actifs_extras (custom assets) ========================================


def test_simulation_propage_actifs_extras_au_simulateur(monkeypatch):
    """Les actifs_extras passes a runner doivent atteindre simuler_marche_dynamique."""
    extras_recus = {}

    def fake_dyn(*a, **kw):
        extras_recus.update(kw.get("actifs_extras") or {})
        return pd.DataFrame({"PERSO_TSLA": [100.0, 110.0]})

    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda *a, **kw: {"actifs": {}}
    )
    monkeypatch.setattr(runner, "simuler_marche_dynamique", fake_dyn)

    extras = {"PERSO_TSLA": {"prix": 250.0, "volatilite": 0.025}}
    res, err = runner.lancer_simulation_scenario(
        scenario="x", actifs_selectionnes=["PERSO_TSLA"], duree=2,
        modele="GBM", monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False, actifs_extras=extras,
    )

    assert err is None
    assert extras_recus == {"PERSO_TSLA": {"prix": 250.0, "volatilite": 0.025}}


def test_simulation_libelle_strip_prefixe_perso(monkeypatch):
    """Un sim_key PERSO_TSLA doit s'afficher 'TSLA' (sans prefixe)."""
    df = pd.DataFrame({"PERSO_TSLA": [100.0, 110.0]})
    monkeypatch.setattr(
        runner, "analyser_evenement_macro",
        lambda *a, **kw: {"actifs": {}}
    )
    monkeypatch.setattr(runner, "simuler_marche_dynamique", lambda *a, **kw: df)

    res, _ = runner.lancer_simulation_scenario(
        scenario="x", actifs_selectionnes=["PERSO_TSLA"], duree=2,
        modele="GBM", monte_carlo=False, prix_reels=None, vols_reelles=None,
        calibration_historique=False,
    )

    assert res["perf_df"]["Actif"].tolist() == ["TSLA"]
