"""
tests/test_custom_assets.py
============================
Tests des helpers de core/custom_assets.py.

On ne teste pas valider_et_calibrer (appel reseau Yahoo) -- c'est une
integration externe. On teste les helpers purs : normalisation de
ticker, construction de cle, conversion vers le format simulation.
"""

from core import custom_assets as ca


def test_normaliser_ticker_majuscule_et_strip():
    assert ca.normaliser_ticker("  tsla  ") == "TSLA"
    assert ca.normaliser_ticker("btc-usd") == "BTC-USD"
    assert ca.normaliser_ticker("MSFT") == "MSFT"


def test_normaliser_ticker_chaine_vide():
    assert ca.normaliser_ticker("") == ""
    assert ca.normaliser_ticker("   ") == ""


def test_cle_simulation_prefixe():
    assert ca.cle_simulation("TSLA") == "PERSO_TSLA"
    assert ca.cle_simulation(" tsla ") == "PERSO_TSLA"


def test_cle_simulation_evite_collision_avec_catalogue():
    """Un ticker = nom d'actif standard (peu probable mais possible) ne doit
    pas ecraser l'actif standard apres prefixage."""
    assert ca.cle_simulation("S&P 500") != "S&P 500"
    assert ca.cle_simulation("Or") != "Or"


def test_vers_actifs_extras_format_attendu():
    perso = {
        "PERSO_TSLA": {"ticker": "TSLA", "nom": "Tesla Inc",
                        "prix": 250.0, "volatilite": 0.025},
        "PERSO_MSFT": {"ticker": "MSFT", "nom": "Microsoft",
                        "prix": 420.0, "volatilite": 0.014},
    }
    extras = ca.vers_actifs_extras(perso)

    assert set(extras.keys()) == {"PERSO_TSLA", "PERSO_MSFT"}
    assert extras["PERSO_TSLA"] == {"prix": 250.0, "volatilite": 0.025}
    assert extras["PERSO_MSFT"] == {"prix": 420.0, "volatilite": 0.014}


def test_vers_actifs_extras_vide():
    assert ca.vers_actifs_extras({}) == {}


def test_valider_et_calibrer_ticker_vide():
    info, err = ca.valider_et_calibrer("")
    assert info is None
    assert "vide" in err.lower()


def test_valider_et_calibrer_ticker_trop_long():
    info, err = ca.valider_et_calibrer("A" * 30)
    assert info is None
    assert "long" in err.lower()
