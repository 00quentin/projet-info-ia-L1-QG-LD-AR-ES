"""
tests/test_validation.py
========================
Tests des helpers de validation (logique pure, sans Streamlit).
"""

from core.validation import (
    valider_actifs_et_allocation, valider_scenarios_textes,
    construire_params_sim_simulation, construire_params_sim_backtest,
)


# === valider_actifs_et_allocation ========================================


def test_valider_actifs_aucun_actif():
    msg = valider_actifs_et_allocation([], "Équilibré", {})
    assert msg is not None
    assert "actif" in msg.lower()


def test_valider_actifs_profil_standard_ok():
    msg = valider_actifs_et_allocation(["S&P 500", "Or"], "Équilibré", {})
    assert msg is None


def test_valider_actifs_profil_personnalise_total_correct():
    msg = valider_actifs_et_allocation(
        ["S&P 500", "Or"], "Personnalisé", {"S&P 500": 60, "Or": 40},
    )
    assert msg is None


def test_valider_actifs_profil_personnalise_total_pas_a_100():
    msg = valider_actifs_et_allocation(
        ["S&P 500", "Or"], "Personnalisé", {"S&P 500": 60, "Or": 30},
    )
    assert msg is not None
    assert "100%" in msg
    assert "90" in msg  # total actuel reporte


def test_valider_actifs_personnalise_zero_pour_zero_ne_passe_pas():
    """Allocation Personnalisee a 0 doit echouer (besoin de 100)."""
    msg = valider_actifs_et_allocation(
        ["S&P 500"], "Personnalisé", {"S&P 500": 0},
    )
    assert msg is not None


# === valider_scenarios_textes ============================================


def test_valider_scenarios_tous_ok():
    textes = {"A": "Krach 2008 type Lehman", "B": "Hausse FED 2022"}
    assert valider_scenarios_textes(textes) is None


def test_valider_scenarios_un_trop_court():
    textes = {"A": "Krach 2008 type Lehman", "B": "court"}
    res = valider_scenarios_textes(textes)
    assert res is not None
    label, msg = res
    assert label == "B"
    assert "court" in msg.lower() or "10" in msg


def test_valider_scenarios_avec_espaces_seulement():
    """Que des espaces -> trop court apres strip."""
    textes = {"A": "          "}
    res = valider_scenarios_textes(textes)
    assert res is not None


def test_valider_scenarios_min_len_personnalise():
    textes = {"A": "abc"}  # 3 chars
    assert valider_scenarios_textes(textes, min_len=3) is None
    assert valider_scenarios_textes(textes, min_len=4) is not None


# === construire_params_sim ===============================================


def _config_simulation(**overrides):
    base = {
        "actifs_selectionnes": ["S&P 500", "Or"],
        "allocations_custom": {"S&P 500": 60, "Or": 40},
        "profil_risque": "Équilibré",
        "capital_initial": 10000,
        "duree": 100,
        "mode_monte_carlo": False,
        "utiliser_prix_reels": True,
        "calibration_historique": False,
    }
    base.update(overrides)
    return base


def test_construire_params_sim_simulation_contient_toutes_les_cles():
    cfg = _config_simulation()
    p = construire_params_sim_simulation(cfg, nb_scenarios=2)
    for cle in ("actifs_sim", "allocations", "profil", "capital", "duree", "mc",
                "nb_scenarios", "prix_reels", "calib"):
        assert cle in p, f"{cle} manquante"
    assert p["nb_scenarios"] == 2
    assert p["mc"] is False
    assert p["calib"] is False


def test_construire_params_sim_simulation_copie_les_listes():
    """Les listes/dicts doivent etre copies pour eviter les mutations partagees."""
    cfg = _config_simulation()
    p = construire_params_sim_simulation(cfg, 1)
    cfg["actifs_selectionnes"].append("HACK")
    cfg["allocations_custom"]["HACK"] = 999
    assert "HACK" not in p["actifs_sim"]
    assert "HACK" not in p["allocations"]


def test_construire_params_sim_backtest():
    cfg = _config_simulation()
    p = construire_params_sim_backtest(cfg, ["S&P 500", "Or"])
    assert p["actifs_sim"] == ["S&P 500", "Or"]
    assert p["profil"] == "Équilibré"
    # Backtest n'a ni mc ni duree (la periode vient de Yahoo)
    assert "mc" not in p
    assert "duree" not in p
