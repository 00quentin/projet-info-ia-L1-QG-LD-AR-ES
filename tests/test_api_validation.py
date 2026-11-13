"""
tests/test_api_validation.py
============================
Route GET /api/validation-ia, fichier data/validation_ia.json versionné et
script scripts/valider_ia_historique.py (sans réseau : IA et Yahoo remplacés).
"""

import importlib.util
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

import market_data
from api import main, validation
from core.validation_ia import agreger, verifier_neutralite

RACINE = Path(__file__).resolve().parent.parent
FICHIER = RACINE / "data" / "validation_ia.json"

client = TestClient(main.app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def _compteurs_a_zero():
    main.limiteur_donnees.reinitialiser()


# === Route ================================================================


def test_route_sert_le_fichier_sans_les_estimations_internes():
    reponse = client.get("/api/validation-ia")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert {"genere_le", "protocole", "global", "biais_connaissance", "crises"} <= set(corps)
    for crise in corps["crises"]:
        assert "estimation" not in crise and "estimation_avec_date" not in crise
        assert crise["actifs"]


def test_route_fichier_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(validation, "FICHIER_VALIDATION", tmp_path / "absent.json")
    reponse = client.get("/api/validation-ia")
    assert reponse.status_code == 502
    assert "pas encore disponibles" in reponse.json()["detail"]


def test_route_fichier_illisible(monkeypatch, tmp_path):
    abime = tmp_path / "abime.json"
    abime.write_text("{pas du json", encoding="utf-8")
    monkeypatch.setattr(validation, "FICHIER_VALIDATION", abime)
    assert client.get("/api/validation-ia").status_code == 502


def test_fichier_relu_quand_il_change(monkeypatch, tmp_path):
    chemin = tmp_path / "v.json"
    monkeypatch.setattr(validation, "FICHIER_VALIDATION", chemin)
    chemin.write_text(json.dumps({"crises": [], "version": 1}), encoding="utf-8")
    assert client.get("/api/validation-ia").json()["version"] == 1
    chemin.write_text(json.dumps({"crises": [], "version": 2}), encoding="utf-8")
    # Date de modification forcee : deux ecritures dans la meme seconde restent distinctes.
    import os
    os.utime(chemin, (chemin.stat().st_atime, chemin.stat().st_mtime + 5))
    assert client.get("/api/validation-ia").json()["version"] == 2


# === Fichier versionné ====================================================


@pytest.fixture(scope="module")
def donnees():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def test_toutes_les_crises_du_catalogue_sont_validees(donnees):
    noms = [c["nom"] for c in donnees["crises"]]
    assert noms == list(market_data.EVENEMENTS_HISTORIQUES)
    for crise in donnees["crises"]:
        infos = market_data.EVENEMENTS_HISTORIQUES[crise["nom"]]
        assert (crise["debut"], crise["fin"]) == (infos["debut"], infos["fin"])


def test_descriptions_envoyees_neutres(donnees):
    for crise in donnees["crises"]:
        assert verifier_neutralite(crise["description_neutre"], crise["nom"]) is None
        assert crise["estimation"]["scenario"] == crise["scenario_envoye"]


def test_protocole_trace(donnees):
    p = donnees["protocole"]
    assert p["modele"] and p["version_prompt"] and p["version"]
    assert p["calibration_historique"] is False
    datetime.fromisoformat(donnees["genere_le"])


def test_scores_globaux_coherents_avec_le_detail(donnees):
    recalcul = agreger(c["actifs"] for c in donnees["crises"])
    g = donnees["global"]
    assert g["nb_actifs"] == recalcul["nb_actifs"]
    assert g["nb_sens_corrects"] == recalcul["nb_sens_corrects"]
    assert g["erreur_moyenne_pts"] == pytest.approx(recalcul["erreur_moyenne_pts"], abs=0.02)
    assert g["correlation"] == pytest.approx(recalcul["correlation"], abs=0.005)


def test_estimations_dans_les_bornes(donnees):
    for crise in donnees["crises"]:
        for actif in crise["actifs"]:
            assert -100 < actif["estime_pct"] < 600
            assert actif["ecart_pts"] == pytest.approx(actif["estime_pct"] - actif["reel_pct"], abs=0.02)


# === Script (sans réseau) =================================================


def _charger_script():
    spec = importlib.util.spec_from_file_location(
        "valider_ia_historique", RACINE / "scripts" / "valider_ia_historique.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def script(monkeypatch, tmp_path):
    module = _charger_script()
    monkeypatch.setattr(module, "FICHIER_SORTIE", tmp_path / "validation_ia.json")
    monkeypatch.setattr(module.ia_bot, "_cle_api", lambda: "cle-de-test")

    def historique(actifs, debut, fin, convertir_eur=True, avec_dates=False):
        dates = pd.bdate_range(debut, periods=40)
        rng = np.random.default_rng(len(actifs) + (1 if convertir_eur else 0))
        cotes = [a for a in actifs if a not in ("Solana", "XRP")]  # pas encore cotes
        prix = 100 * np.cumprod(1 + rng.normal(0, 0.01, (len(dates), len(cotes))), axis=0)
        return pd.DataFrame(prix, index=dates, columns=cotes)

    monkeypatch.setattr(module.market_data, "get_historique", historique)
    appels = []

    def fausse_ia(prompt, scenario, compteur):
        compteur.reserver()
        appels.append(prompt)
        chocs = {cle: -0.1 for cle in module.BORNES_ACTIFS}
        return {"empreinte": module.empreinte(prompt), "date": "2026-11-13T00:00:00",
                "modele": "modele-de-test", "reglages": {}, "scenario": scenario,
                "chocs": chocs, "chocs_bruts": dict(chocs), "evenement_cite": "Crise test",
                "fourchettes": {c: {"bas": v - 0.1, "central": v, "haut": v + 0.1} for c, v in chocs.items()},
                "references": [], "explication": "Comme en 2008."}

    monkeypatch.setattr(module, "appeler_ia", fausse_ia)
    module.appels = appels
    return module


def test_script_complet_puis_reutilise_les_estimations(script):
    nb_crises = len(market_data.EVENEMENTS_HISTORIQUES)
    assert script.main(["--max-appels", "20"]) == 0
    assert len(script.appels) == 2 * nb_crises  # sans date + avec date
    donnees = json.loads(script.FICHIER_SORTIE.read_text(encoding="utf-8"))
    assert len(donnees["crises"]) == nb_crises
    crise = donnees["crises"][0]
    assert {a["cle"] for a in crise["actifs_absents"]} == {"Solana", "XRP"}
    assert "Indice : la période étudiée va du" in crise["estimation_avec_date"]["scenario"]
    assert "PRIORITAIRE SUR L'ETAPE 2" in script.appels[0]
    assert donnees["biais_connaissance"]["nb_crises"] == nb_crises
    assert donnees["global"]["nb_fourchettes"] == donnees["global"]["nb_actifs"]
    assert all("dans_fourchette" in a for a in crise["actifs"])

    # Rien n'a change : aucune nouvelle depense d'IA.
    assert script.main([]) == 0
    assert len(script.appels) == 2 * nb_crises


def test_script_plafond_d_appels(script):
    with pytest.raises(RuntimeError, match="Plafond"):
        script.main(["--max-appels", "3"])


def test_script_sans_ia_sans_fichier(script):
    with pytest.raises(SystemExit):
        script.main(["--sans-ia"])
    assert script.appels == []


def test_script_refuse_une_description_qui_trahit_la_crise(script, monkeypatch):
    nom = next(iter(market_data.EVENEMENTS_HISTORIQUES))
    monkeypatch.setitem(script.DESCRIPTIONS_NEUTRES, nom, "Une pandémie comme en 2020.")
    with pytest.raises(SystemExit, match="non neutre"):
        script.main([])
    assert script.appels == []
