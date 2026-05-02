"""
tests/test_risk_alerts.py
=========================
Tests des alertes de risque automatiques. On verrouille les seuils
business (calibres avec les standards de l'industrie) pour eviter
qu'un refactor casse silencieusement la classification.
"""

import pytest

from core.risk_alerts import evaluer_alertes_risque, AlerteRisque


def _metriques(**kwargs):
    """Helper : construit un dict metriques avec valeurs neutres par defaut."""
    return {
        "vol_ann": kwargs.get("vol_ann", 15.0),
        "sharpe":  kwargs.get("sharpe",  1.0),
        "max_dd":  kwargs.get("max_dd",  10.0),
        "var_95":  kwargs.get("var_95", -1.5),
    }


# === Sharpe ==============================================================

def test_sharpe_neutre_aucune_alerte_sharpe():
    alertes = evaluer_alertes_risque(_metriques(sharpe=0.5))
    titres = [a.metrique for a in alertes]
    assert "sharpe" not in titres


def test_sharpe_negatif_alerte_warning():
    alertes = evaluer_alertes_risque(_metriques(sharpe=-0.5))
    sharpe_alertes = [a for a in alertes if a.metrique == "sharpe"]
    assert len(sharpe_alertes) == 1
    assert sharpe_alertes[0].severite == "warning"


def test_sharpe_tres_negatif_alerte_error():
    alertes = evaluer_alertes_risque(_metriques(sharpe=-1.5))
    sharpe_alertes = [a for a in alertes if a.metrique == "sharpe"]
    assert len(sharpe_alertes) == 1
    assert sharpe_alertes[0].severite == "error"


def test_sharpe_excellent_alerte_success():
    """Sharpe >= 2.0 declenche une alerte positive (success)."""
    alertes = evaluer_alertes_risque(_metriques(sharpe=2.5))
    sharpe_alertes = [a for a in alertes if a.metrique == "sharpe"]
    assert len(sharpe_alertes) == 1
    assert sharpe_alertes[0].severite == "success"


# === Max Drawdown ========================================================

def test_drawdown_normal_aucune_alerte():
    alertes = evaluer_alertes_risque(_metriques(max_dd=15.0))
    assert not [a for a in alertes if a.metrique == "max_dd"]


def test_drawdown_severe_warning():
    alertes = evaluer_alertes_risque(_metriques(max_dd=30.0))
    dd_alertes = [a for a in alertes if a.metrique == "max_dd"]
    assert len(dd_alertes) == 1
    assert dd_alertes[0].severite == "warning"


def test_drawdown_critique_error():
    alertes = evaluer_alertes_risque(_metriques(max_dd=50.0))
    dd_alertes = [a for a in alertes if a.metrique == "max_dd"]
    assert len(dd_alertes) == 1
    assert dd_alertes[0].severite == "error"


# === Volatilite ==========================================================

def test_vol_normale_aucune_alerte():
    alertes = evaluer_alertes_risque(_metriques(vol_ann=20.0))
    assert not [a for a in alertes if a.metrique == "vol_ann"]


def test_vol_tres_elevee_warning():
    alertes = evaluer_alertes_risque(_metriques(vol_ann=40.0))
    vol_alertes = [a for a in alertes if a.metrique == "vol_ann"]
    assert len(vol_alertes) == 1
    assert vol_alertes[0].severite == "warning"


def test_vol_extreme_error():
    alertes = evaluer_alertes_risque(_metriques(vol_ann=70.0))
    vol_alertes = [a for a in alertes if a.metrique == "vol_ann"]
    assert len(vol_alertes) == 1
    assert vol_alertes[0].severite == "error"


# === VaR =================================================================

def test_var_modere_aucune_alerte():
    alertes = evaluer_alertes_risque(_metriques(var_95=-2.5))
    assert not [a for a in alertes if a.metrique == "var_95"]


def test_var_eleve_warning():
    alertes = evaluer_alertes_risque(_metriques(var_95=-6.0))
    var_alertes = [a for a in alertes if a.metrique == "var_95"]
    assert len(var_alertes) == 1
    assert var_alertes[0].severite == "warning"


# === Cas combines + tri ==================================================

def test_metriques_neutres_aucune_alerte():
    """Un portefeuille raisonnable ne genere aucune alerte."""
    alertes = evaluer_alertes_risque(_metriques())
    assert alertes == []


def test_portefeuille_catastrophique_multiple_alertes():
    """Une simulation desastreuse declenche plusieurs alertes simultanees."""
    metriques = _metriques(sharpe=-1.5, max_dd=50.0, vol_ann=70.0, var_95=-7.0)
    alertes = evaluer_alertes_risque(metriques)
    assert len(alertes) >= 4
    # Tri : les error doivent venir avant les warning
    severites = [a.severite for a in alertes]
    erreurs_avant_warnings = all(
        severites.index("error") < i
        for i, s in enumerate(severites) if s == "warning"
    )
    assert erreurs_avant_warnings


def test_alertes_sont_dataclass_immutables():
    """AlerteRisque est frozen -> impossible a muter accidentellement."""
    alertes = evaluer_alertes_risque(_metriques(sharpe=-1.5))
    a = alertes[0]
    with pytest.raises(Exception):  # FrozenInstanceError
        a.titre = "modifie"


def test_message_contient_la_valeur_observee():
    """Les messages utilisateurs incluent la metrique pour transparence."""
    alertes = evaluer_alertes_risque(_metriques(max_dd=42.5))
    dd_alerte = next(a for a in alertes if a.metrique == "max_dd")
    assert "42" in dd_alerte.message
