"""
tests/test_api_couverture.py
============================
Route POST /api/couverture. Le moteur et la recherche sont reels ; seuls les
acces reseau (Yahoo, FRED, OpenAI) sont remplaces.
"""

import json
from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import ia_bot
from api import couverture, main, services

client = TestClient(main.app, raise_server_exceptions=False)

DEMANDE = {
    "scenario": "Une crise bancaire majeure éclate aux États-Unis.",
    "chocs": {"S&P 500": -0.30, "CAC 40": -0.25, "Bitcoin": -0.50,
              "Bons_Tresor_US_10Y": 0.06, "Or": 0.12, "EUR_USD": -0.02},
    "poids": {"S&P 500": 0.35, "CAC 40": 0.20, "Bitcoin": 0.15, "Bons_Tresor_US_10Y": 0.20, "Or": 0.10},
    "capital": 10000,
    "duree": 60,
}


class _FauxClient:
    """Client OpenAI factice : renvoie le JSON demande et compte les appels."""

    def __init__(self, contenu):
        self.appels = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._creer))
        self.contenu = contenu

    def _creer(self, **kwargs):
        self.appels.append(kwargs)
        if isinstance(self.contenu, Exception):
            raise self.contenu
        message = SimpleNamespace(content=self.contenu)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


@pytest.fixture(autouse=True)
def _sans_reseau(monkeypatch):
    main.limiteur_ia.reinitialiser()
    couverture._rediger_justifications.clear()
    monkeypatch.setattr(ia_bot, "_cle_api", lambda: "cle-de-test")
    monkeypatch.setattr(services.market_data, "get_volatilites_historiques", lambda actifs: {})
    monkeypatch.setattr(services.market_data, "get_rendements_historiques", lambda actifs: pd.DataFrame())
    monkeypatch.setattr(services.market_data, "get_taux_sans_risque", lambda debut=None, fin=None: 0.02)


def _brancher_ia(monkeypatch, contenu):
    faux = _FauxClient(contenu)
    monkeypatch.setattr(ia_bot, "_get_openai_client", lambda: faux)
    return faux


def test_protection_complete(monkeypatch):
    faux = _brancher_ia(monkeypatch, json.dumps({
        "synthese": "On déplace le risque des actions vers les valeurs refuges.",
        "justifications": {"Or": "Valeur refuge classique dans une crise bancaire.",
                           "Inconnu": "ignoré"},
    }))
    r = client.post("/api/couverture", json=DEMANDE)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["deja_protege"] is False
    assert sum(data["allocations"].values()) == 100
    assert max(data["allocations"].values()) <= 40
    assert data["allocations"]["Or"] > 10 and data["allocations"]["Bitcoin"] < 15
    av, ap = data["avant"]["metriques"], data["apres"]["metriques"]
    assert ap["max_dd"] < av["max_dd"]
    assert ap["proba_perte"] <= av["proba_perte"]
    assert len(data["avant"]["valeurs"]) == len(data["apres"]["valeurs"]) == DEMANDE["duree"]
    assert data["avant"]["valeurs"][0] == pytest.approx(10000)

    # Une phrase par changement : celle de l'IA si elle existe, sinon la phrase de secours
    assert data["changements"] and all(c["justification"] for c in data["changements"])
    par_cle = {c["cle"]: c for c in data["changements"]}
    assert par_cle["Or"]["justification"] == "Valeur refuge classique dans une crise bancaire."
    assert par_cle["Or"]["justification_ia"] is True
    assert data["synthese"].startswith("On déplace")
    assert data["justifications_ia"] is False  # l'IA n'a pas tout justifie
    assert {l["cle"] for l in data["lignes"]} == set(DEMANDE["chocs"])

    # Un seul appel, au modele de chat, et le meme resultat ensuite (cache)
    assert len(faux.appels) == 1 and faux.appels[0]["model"] == ia_bot.IA_CHAT["model"]
    assert client.post("/api/couverture", json=DEMANDE).json()["allocations"] == data["allocations"]
    assert len(faux.appels) == 1


def test_ia_indisponible_phrases_de_secours(monkeypatch):
    _brancher_ia(monkeypatch, ValueError("réponse illisible"))
    data = client.post("/api/couverture", json=DEMANDE).json()
    assert data["changements"] and all(c["justification"] and not c["justification_ia"] for c in data["changements"])
    assert data["synthese"] is None and data["justifications_ia"] is False


def test_sans_cle_openai_pas_d_appel(monkeypatch):
    faux = _brancher_ia(monkeypatch, "{}")
    monkeypatch.setattr(ia_bot, "_cle_api", lambda: None)
    r = client.post("/api/couverture", json=DEMANDE)
    assert r.status_code == 200 and faux.appels == []


def test_portefeuille_deja_protege(monkeypatch):
    faux = _brancher_ia(monkeypatch, "{}")
    # Actifs tous identiques (meme choc, vol et correlation de secours) : rien a gagner
    demande = {**DEMANDE, "chocs": {"Bund_10Y": -0.01, "OAT_10Y": -0.01, "Gilt_10Y": -0.01},
               "poids": {"Bund_10Y": 0.34, "OAT_10Y": 0.33, "Gilt_10Y": 0.33}, "convertir_eur": False}
    monkeypatch.setattr(services.market_data, "get_volatilites_historiques",
                        lambda actifs: {a: 0.003 for a in actifs})
    data = client.post("/api/couverture", json=demande).json()
    assert data["deja_protege"] is True and data["changements"] == []
    assert data["allocations"] == {"Bund_10Y": 34, "OAT_10Y": 33, "Gilt_10Y": 33}
    assert faux.appels == []


@pytest.mark.parametrize("modif, extrait", [
    ({"chocs": {**DEMANDE["chocs"], "Or": 3.0}}, "hors bornes"),
    ({"chocs": {**DEMANDE["chocs"], "Inconnu": 0.1}}, "inconnu"),
    ({"poids": {**DEMANDE["poids"], "S&P 500": 0.25, "NASDAQ": 0.1}}, "sans choc"),
    ({"poids": {"S&P 500": 0.5, "Or": 0.2}}, "somme"),
    ({"poids": {**DEMANDE["poids"], "Or": -0.1}}, "fraction"),
    ({"modele": "Boule de cristal"}, "Modèle inconnu"),
    ({"duree": 5}, None),
    ({"chocs": {**DEMANDE["chocs"], "PERSO_TSLA": 0.1}}, "tickers_perso"),
])
def test_demandes_invalides(modif, extrait):
    r = client.post("/api/couverture", json={**DEMANDE, **modif})
    assert r.status_code == 422
    if extrait:
        assert extrait in json.dumps(r.json(), ensure_ascii=False)


def test_trop_peu_d_actifs_message_clair(monkeypatch):
    _brancher_ia(monkeypatch, "{}")
    r = client.post("/api/couverture", json={**DEMANDE, "chocs": {"S&P 500": -0.3, "Or": 0.1},
                                             "poids": {"S&P 500": 0.5, "Or": 0.5}})
    assert r.status_code == 422 and "au moins 3 actifs" in r.json()["detail"]


def test_limite_d_appels_partagee_avec_l_ia(monkeypatch):
    _brancher_ia(monkeypatch, "{}")
    # Le client de test a deja epuise son quota (simulations, chat...)
    for _ in range(1000):
        if not main.limiteur_ia.autoriser("testclient"):
            break
    assert client.post("/api/couverture", json=DEMANDE).status_code == 429


def test_justifications_rattachees_meme_cle_mal_recopiee():
    changements = [{"cle": "Bons_Tresor_US_10Y", "nom": "U.S. Treasury 10Y"},
                   {"cle": "Or", "nom": "Or (Gold Spot, $/oz)"},
                   {"cle": "Bitcoin", "nom": "Bitcoin (BTC)"}]
    textes = {"[Bons_Tresor_US_10Y]": "Fuite vers la qualité.", "or": "Valeur refuge.",
              "Bitcoin (BTC)": "Trop volatil.", "Autre": "ignoré"}
    assert couverture._associer_justifications(textes, changements) == {
        "Bons_Tresor_US_10Y": "Fuite vers la qualité.", "Or": "Valeur refuge.", "Bitcoin": "Trop volatil."}
