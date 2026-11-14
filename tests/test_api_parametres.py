"""
tests/test_api_parametres.py
============================
GET /api/parametres doit rester aligné sur donnees.ts (page Méthodologie).
"""

import math

import pytest
from fastapi.testclient import TestClient

from api import main
from tests import test_donnees_methodologie as td

client = TestClient(main.app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def corps():
    main.limiteur_donnees.reinitialiser()
    r = client.get("/api/parametres")
    assert r.status_code == 200
    return r.json()


def test_json_stable(corps):
    assert client.get("/api/parametres").json() == corps


def test_memes_cles_que_donnees_ts(corps):
    cles_ts = set(td._entrees_parametres())
    assert set(corps["parametres"]) | set(corps["modeles_ia"]) == cles_ts
    assert set(corps["bornes_autres"]) == set(td._entrees_bornes_autres())
    assert set(corps["bornes_ia"]) == set(td._entrees_bornes_ia())


def test_valeurs_egales_a_donnees_ts(corps):
    ts = td._entrees_parametres()
    for cle, valeur in corps["parametres"].items():
        assert math.isclose(valeur, ts[cle][0], rel_tol=1e-9, abs_tol=1e-9), cle
    autres = td._entrees_bornes_autres()
    for cle, (mn, mx) in corps["bornes_autres"].items():
        (amn, amx), _ = autres[cle]
        assert math.isclose(mn, amn, abs_tol=1e-9) and math.isclose(mx, amx, abs_tol=1e-9), cle
    bornes_ia = td._entrees_bornes_ia()
    for actif, (mn, mx) in corps["bornes_ia"].items():
        amn, amx = bornes_ia[actif]
        assert math.isclose(mn, amn, abs_tol=1e-9) and math.isclose(mx, amx, abs_tol=1e-9), actif
    for cle, modele in corps["modeles_ia"].items():
        assert td._normaliser_modele(modele) == td._normaliser_modele(ts[cle][0]), cle
