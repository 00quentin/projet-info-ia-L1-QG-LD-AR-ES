"""
tests/test_comparaison.py
=========================
POST /api/comparaison-portefeuilles : deux portefeuilles, une seule analyse IA.
Le moteur est reel ; l'IA est remplacee au niveau ia_bot._analyser_impl.
"""

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import ia_bot
from api import main, services
from api.comparaison import DemandeComparaison

client = TestClient(main.app, raise_server_exceptions=False)

CHOCS = {
    "macro": {"inflation": 1.3, "taux_directeurs": -0.4},
    "actifs": {"S&P 500": -0.20, "CAC 40": -0.15, "Or": 0.10, "EUR_USD": 0.0, "MSCI_World": -0.17},
    "explication_courte": "Crise de liquidité.",
    "evenement_reference": "Crise 2008",
}
PORT_A = {"actifs": ["S&P 500", "CAC 40", "Or"], "profil": "Équilibré (Normal)", "capital": 10000}
PORT_B = {"actifs": ["S&P 500", "Or"], "profil": "Équilibré (Normal)", "capital": 10000}
DEMANDE = {
    "scenario": "Une crise bancaire majeure éclate aux États-Unis.",
    "portefeuille_a": PORT_A, "portefeuille_b": PORT_B, "duree": 60,
}


@pytest.fixture(autouse=True)
def _sans_reseau(monkeypatch):
    main.limiteur_ia.reinitialiser()
    main.plafond_ia.reinitialiser()
    monkeypatch.setattr(ia_bot, "_cle_api", lambda: "cle-de-test")
    monkeypatch.setattr(services.market_data, "get_prix_actuels", lambda actifs: ({a: 100.0 for a in actifs}, []))
    monkeypatch.setattr(services.market_data, "get_volatilites_historiques", lambda actifs: {a: 0.01 for a in actifs})
    monkeypatch.setattr(services.market_data, "get_rendements_historiques", lambda actifs: pd.DataFrame())
    monkeypatch.setattr(services.market_data, "get_conjoncture", lambda: {"indicateurs": [], "date": None})
    monkeypatch.setattr(services.market_data, "get_taux_sans_risque", lambda debut=None, fin=None: 0.025)


def test_schema_valide_et_bornes():
    d = DemandeComparaison(**DEMANDE)
    assert d.portefeuille_a.actifs != d.portefeuille_b.actifs
    with pytest.raises(ValidationError):
        DemandeComparaison(**{**DEMANDE, "scenario": "x" * 5000})
    with pytest.raises(ValidationError):
        DemandeComparaison(**{**DEMANDE, "modele": "Inconnu"})
    with pytest.raises(ValidationError):
        DemandeComparaison(**{k: v for k, v in DEMANDE.items() if k != "portefeuille_b"})


def test_un_seul_appel_ia_pour_deux_portefeuilles(monkeypatch):
    appels = []

    def faux(*args, **kwargs):
        appels.append(args)
        return {**CHOCS, "actifs": dict(CHOCS["actifs"])}

    monkeypatch.setattr(ia_bot, "_analyser_impl", faux)
    # Scenario unique a ce test : le cache de 24 h ne doit pas venir d'un autre test.
    demande = {**DEMANDE, "calibration": False,
               "scenario": "Un test de comparaison : crise bancaire inédite aux États-Unis."}
    r = client.post("/api/comparaison-portefeuilles", json=demande)
    assert r.status_code == 200, r.text
    data = r.json()
    assert len(appels) == 1
    assert data["analyse_partagee"] is True
    assert data["a"]["erreur"] is None and data["b"]["erreur"] is None
    pa, pb = data["a"]["portefeuille"], data["b"]["portefeuille"]
    assert pa["valeur_finale"] != pb["valeur_finale"]
    assert data["ecarts"]["perf_pts"] == pytest.approx(pb["performance_pct"] - pa["performance_pct"])
    assert set(data["ecarts"]) >= {"perf_pts", "volatilite", "sharpe", "var", "drawdown"}


def test_avec_calibration_deux_analyses_au_total_pas_quatre(monkeypatch):
    # Calibration = 1 analyse ancree + 1 analyse libre pour le 1er portefeuille ; le 2e relit le cache.
    appels = []
    monkeypatch.setattr(ia_bot, "_analyser_impl",
                        lambda *a, **k: appels.append(a) or {**CHOCS, "actifs": dict(CHOCS["actifs"])})
    demande = {**DEMANDE, "scenario": "Un autre test de comparaison : krach obligataire en Europe."}
    assert client.post("/api/comparaison-portefeuilles", json=demande).status_code == 200
    assert len(appels) == 2


def test_tickers_perso_differents_refuses_sans_appel_ia(monkeypatch):
    appels = []
    monkeypatch.setattr(ia_bot, "_analyser_impl", lambda *a, **k: appels.append(a) or CHOCS)
    demande = {**DEMANDE, "portefeuille_b": {**PORT_B, "tickers_perso": ["TSLA"]}}
    r = client.post("/api/comparaison-portefeuilles", json=demande)
    assert r.status_code == 422
    assert "mêmes actifs personnalisés" in r.json()["detail"]
    assert appels == []
