"""
tests/test_cache.py
===================
Tests du cache TTL independant de Streamlit.
"""

import core.cache as cache_mod
from core.cache import cache_ttl, vider_tous_les_caches


def test_resultat_memorise_par_arguments():
    appels = []

    @cache_ttl(60)
    def f(a, b=0):
        appels.append((a, b))
        return a + b

    assert f(1, b=2) == 3 and f(1, b=2) == 3
    assert f(2) == 2
    assert appels == [(1, 2), (2, 0)]


def test_arguments_non_hashables_acceptes():
    @cache_ttl(60)
    def f(liste, options=None):
        return len(liste)

    assert f(["a", "b"], options={"x": [1, 2]}) == 2
    assert f(["a", "b"], options={"x": [1, 2]}) == 2


def test_expiration(monkeypatch):
    horloge = {"t": 0.0}
    monkeypatch.setattr(cache_mod.time, "monotonic", lambda: horloge["t"])
    appels = []

    @cache_ttl(10)
    def f():
        appels.append(1)
        return len(appels)

    assert f() == 1
    horloge["t"] = 9
    assert f() == 1
    horloge["t"] = 11
    assert f() == 2


def test_copie_protege_la_valeur_en_cache():
    @cache_ttl(60)
    def f():
        return {"prix": [1, 2]}

    f()["prix"].append(99)
    assert f() == {"prix": [1, 2]}


def test_clear_et_vidage_global():
    appels = []

    @cache_ttl(60)
    def f():
        appels.append(1)
        return 1

    f(); f.clear(); f()
    assert len(appels) == 2
    vider_tous_les_caches(); f()
    assert len(appels) == 3


def test_garder_permet_de_ne_pas_memoriser_les_erreurs():
    reponses = [{"erreur": "timeout"}, {"ok": 1}, {"ok": 2}]

    @cache_ttl(60, garder=lambda r: "erreur" not in r)
    def f():
        return reponses.pop(0)

    assert f() == {"erreur": "timeout"}
    assert f() == {"ok": 1}
    assert f() == {"ok": 1}
