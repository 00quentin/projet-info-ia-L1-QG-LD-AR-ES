"""Tests de api/recherche.py : nettoyage, filtrage, repli, cache (reseau moque)."""
import pytest

from api import recherche


@pytest.fixture(autouse=True)
def _vider_cache():
    recherche._rechercher.clear()
    yield
    recherche._rechercher.clear()


def _quote(symbole, type_, nom="Nom"):
    return {"symbol": symbole, "quoteType": type_, "shortname": nom, "exchDisp": "NYSE"}


def test_nettoyage():
    assert recherche.nettoyer_requete("  S&P   500 Europe ") == "S&P 500 Europe"
    assert recherche.nettoyer_requete("a") == ""
    assert recherche.nettoyer_requete("x" * 41) == ""
    assert recherche.nettoyer_requete(None) == ""
    assert "<" not in recherche.nettoyer_requete("<script>alert(1)</script>")
    assert ";" not in recherche.nettoyer_requete("apple; DROP TABLE")


def test_requete_invalide_sans_appel_reseau(monkeypatch):
    def interdit(q):
        raise AssertionError("pas d'appel reseau")
    monkeypatch.setattr(recherche, "_interroger_yahoo", interdit)
    res = recherche.rechercher_actifs("a")
    assert res["resultats"] == [] and res["message"]


def test_filtre_types_et_limite(monkeypatch):
    brut = [_quote("AAPL", "EQUITY"), _quote("AAPL=F", "FUTURE"), _quote("X", "OPTION"), _quote("VTI", "ETF"),
            _quote("AAPL", "EQUITY")] + [_quote(f"T{i}", "EQUITY") for i in range(30)]
    monkeypatch.setattr(recherche, "_interroger_yahoo", lambda q: brut)
    res = recherche.rechercher_actifs("apple")
    symboles = [r["symbole"] for r in res["resultats"]]
    assert symboles[:2] == ["AAPL", "VTI"] and len(symboles) == 10
    assert "AAPL=F" not in symboles and res["message"] is None
    assert res["resultats"][0]["type"] == "action"


def test_repli_si_yahoo_en_panne(monkeypatch):
    def panne(q):
        raise ConnectionError("hors ligne")
    monkeypatch.setattr(recherche, "_interroger_yahoo", panne)
    res = recherche.rechercher_actifs("apple")
    assert res["resultats"] == [] and res["message"]


def test_cache_et_panne_non_memorisee(monkeypatch):
    appels = []
    monkeypatch.setattr(recherche, "_interroger_yahoo", lambda q: appels.append(q) or [_quote("AAPL", "EQUITY")])
    recherche.rechercher_actifs("apple")
    recherche.rechercher_actifs("apple")
    assert len(appels) == 1

    recherche._rechercher.clear()
    etat = {"n": 0}

    def instable(q):
        etat["n"] += 1
        if etat["n"] == 1:
            raise TimeoutError()
        return [_quote("AAPL", "EQUITY")]
    monkeypatch.setattr(recherche, "_interroger_yahoo", instable)
    assert recherche.rechercher_actifs("apple")["message"]
    assert recherche.rechercher_actifs("apple")["resultats"]
