"""
tests/test_schemas.py
=====================
Tests de la validation Pydantic des reponses IA.
Le bug critique deja corrige : l'IA renvoyait parfois 25 au lieu de 0.25,
provoquant Or a +1 222 891%. Ces tests verrouillent ce comportement.
"""

import pytest

from schemas import valider_reponse_ia, _normaliser_choc, BORNES_ACTIFS


# === _normaliser_choc =====================================================

@pytest.mark.parametrize("entree, attendu", [
    (0.15, 0.15),       # deja normalise
    (-0.20, -0.20),     # negatif normalise
    (15, 0.15),         # pourcentage entier -> decimal
    (-25, -0.25),       # pourcentage negatif -> decimal
    (1500, 15.0),       # tres gros -> divise par 100 (sera ensuite borne)
    (0, 0.0),           # zero
    (None, 0.0),        # None
    ("0.10", 0.10),     # string parse
    ("invalide", 0.0),  # string non-num -> fallback 0
])
def test_normaliser_choc(entree, attendu):
    assert _normaliser_choc(entree) == attendu


def test_normaliser_choc_seuil_5():
    """Heuristique : abs > 5 = pourcentage mal forme.
    Donc 4.99 reste tel quel, 5.01 est divise."""
    assert _normaliser_choc(4.99) == 4.99
    assert _normaliser_choc(5.01) == pytest.approx(0.0501, abs=1e-9)


# === valider_reponse_ia ===================================================

def test_reponse_complete_valide():
    """Cas nominal : tous les champs presents et coherents."""
    brut = {
        "macro": {"inflation": 2.5, "taux_directeurs": 0.5},
        "actifs": {"S&P 500": -0.10, "Or": 0.05, "Bitcoin": -0.30},
        "explication_courte": "Crise bancaire modérée.",
        "evenement_reference": "2008",
    }
    out = valider_reponse_ia(brut)
    assert "erreur" not in out
    assert out["macro"]["inflation"] == 2.5
    assert out["actifs"]["S&P 500"] == -0.10
    assert out["explication_courte"] == "Crise bancaire modérée."


def test_reponse_pourcentage_normalise():
    """L'IA renvoie 10 au lieu de 0.10 -> doit etre normalise.
    Note : la normalisation declenche pour abs(v) > 5, donc on prend
    des valeurs strictement superieures a 5 en magnitude."""
    brut = {
        "macro": {"inflation": 0, "taux_directeurs": 0},
        "actifs": {"S&P 500": -10, "Or": 6},  # -10% et +6% mal formes
    }
    out = valider_reponse_ia(brut)
    assert out["actifs"]["S&P 500"] == pytest.approx(-0.10, abs=1e-9)
    assert out["actifs"]["Or"] == pytest.approx(0.06, abs=1e-9)


def test_reponse_choc_extreme_borne():
    """L'IA renvoie -0.95 sur le S&P 500 (au-dela de la borne -0.55)
    -> doit etre clamp a -0.55."""
    brut = {
        "macro": {"inflation": 0, "taux_directeurs": 0},
        "actifs": {"S&P 500": -0.95},
    }
    out = valider_reponse_ia(brut)
    mn, _ = BORNES_ACTIFS["S&P 500"]
    assert out["actifs"]["S&P 500"] == mn


def test_reponse_choc_extreme_haut_borne():
    """+200% sur l'or -> clamp au plafond +60%."""
    brut = {
        "macro": {"inflation": 0, "taux_directeurs": 0},
        "actifs": {"Or": 2.0},
    }
    out = valider_reponse_ia(brut)
    _, mx = BORNES_ACTIFS["Or"]
    assert out["actifs"]["Or"] == mx


def test_reponse_avec_erreur_passe():
    """Si l'IA elle-meme retourne {erreur: ...}, on retourne tel quel."""
    out = valider_reponse_ia({"erreur": "API down"})
    assert out == {"erreur": "API down"}


def test_reponse_macro_manquante_remplace_par_zero():
    """Si macro absent, on doit avoir des defauts a 0 (pas un crash)."""
    brut = {"actifs": {"S&P 500": -0.10}}
    out = valider_reponse_ia(brut)
    assert out["macro"]["inflation"] == 0.0
    assert out["macro"]["taux_directeurs"] == 0.0


def test_reponse_actif_inconnu_pas_borne_mais_present():
    """Un actif inconnu (typo IA) ne plante pas, mais n'est pas borne."""
    brut = {
        "macro": {"inflation": 0, "taux_directeurs": 0},
        "actifs": {"Actif_Bidon": -0.99, "S&P 500": -0.10},
    }
    out = valider_reponse_ia(brut)
    # actif valide present
    assert out["actifs"]["S&P 500"] == -0.10


def test_reponse_non_dict_ne_crashe_pas():
    """Robustesse : un input non-dict (string, None) ne doit pas crasher.
    Le fallback retourne un dict avec actifs vides + macro a zero, ce qui
    est un comportement degrade acceptable (la simu donnera des chocs nuls
    plutot qu'une exception)."""
    out_str = valider_reponse_ia("pas un dict")
    assert isinstance(out_str, dict)
    assert out_str.get("actifs") == {}
    assert out_str.get("macro") == {"inflation": 0.0, "taux_directeurs": 0.0}

    out_none = valider_reponse_ia(None)
    assert isinstance(out_none, dict)


def test_bornes_par_classe_coherentes():
    """Tous les actifs ont des bornes (min, max) avec min < 0 < max."""
    for nom, (mn, mx) in BORNES_ACTIFS.items():
        assert mn < 0, f"{nom} : borne min ({mn}) devrait etre negative"
        assert mx > 0, f"{nom} : borne max ({mx}) devrait etre positive"
        assert mn < mx, f"{nom} : min ({mn}) >= max ({mx})"


def test_bornes_cryptos_plus_larges_que_actions():
    """Sanity check : les cryptos ont des amplitudes superieures aux actions."""
    btc_min, btc_max = BORNES_ACTIFS["Bitcoin"]
    sp_min, sp_max = BORNES_ACTIFS["S&P 500"]
    assert (btc_max - btc_min) > (sp_max - sp_min)


# === actifs custom (PERSO_*) ==============================================


def test_actifs_perso_preserves_par_validation():
    """Les cles PERSO_* ne doivent PAS etre filtrees par le schema Pydantic."""
    brut = {
        "macro": {"inflation": 1.0, "taux_directeurs": 0.5},
        "actifs": {
            "S&P 500": -0.10,
            "PERSO_TSLA": -0.25,
            "PERSO_NVDA": -0.30,
        },
        "explication_courte": "test",
    }
    out = valider_reponse_ia(brut)
    assert "PERSO_TSLA" in out["actifs"]
    assert "PERSO_NVDA" in out["actifs"]
    assert out["actifs"]["PERSO_TSLA"] == pytest.approx(-0.25)


def test_actifs_perso_normalisation_pourcentage():
    """Un PERSO_* en pourcentage entier est normalise comme les autres."""
    brut = {"actifs": {"PERSO_TSLA": -25}}
    out = valider_reponse_ia(brut)
    assert out["actifs"]["PERSO_TSLA"] == pytest.approx(-0.25)


def test_actifs_perso_borne_generique_appliquee():
    """Un PERSO_* avec valeur extreme est borne (-0.80 a 2.00)."""
    brut = {"actifs": {"PERSO_DOGE": 5.0}}  # +500% -> doit etre borne
    out = valider_reponse_ia(brut)
    assert out["actifs"]["PERSO_DOGE"] <= 2.0

    brut2 = {"actifs": {"PERSO_DOGE": -0.95}}  # -95% -> doit etre borne
    out2 = valider_reponse_ia(brut2)
    assert out2["actifs"]["PERSO_DOGE"] >= -0.80
