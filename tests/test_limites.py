"""
tests/test_limites.py
=====================
Tests des garde-fous de l'API : limite par adresse et plafond quotidien d'appels IA.
"""

from datetime import date

import pytest

from api.limites import LimiteurAppels, PlafondJournalier, plafond_ia_du_jour
from config import API_PLAFOND_APPELS_IA_JOUR


class _Calendrier:
    def __init__(self, jour):
        self.jour = jour

    def __call__(self):
        return self.jour


def test_plafond_bloque_au_dela_du_maximum():
    plafond = PlafondJournalier(3, aujourd_hui=_Calendrier(date(2026, 11, 13)))
    assert [plafond.autoriser() for _ in range(5)] == [True, True, True, False, False]


def test_plafond_repart_a_zero_le_lendemain():
    calendrier = _Calendrier(date(2026, 11, 13))
    plafond = PlafondJournalier(1, aujourd_hui=calendrier)
    assert plafond.autoriser() and not plafond.autoriser()
    calendrier.jour = date(2026, 11, 14)
    assert plafond.autoriser() and not plafond.autoriser()


def test_plafond_zero_coupe_l_ia():
    assert PlafondJournalier(0).autoriser() is False


def test_plafond_reinitialiser():
    plafond = PlafondJournalier(1)
    plafond.autoriser()
    plafond.reinitialiser()
    assert plafond.autoriser()


@pytest.mark.parametrize("valeur, attendu", [
    (None, API_PLAFOND_APPELS_IA_JOUR),      # variable absente : valeur de config.py
    ("", API_PLAFOND_APPELS_IA_JOUR),
    ("500", 500),
    (" 42 ", 42),
    ("0", 0),
    ("beaucoup", API_PLAFOND_APPELS_IA_JOUR),  # illisible : on garde le defaut
    ("-3", API_PLAFOND_APPELS_IA_JOUR),
])
def test_plafond_surchargeable_par_variable_d_environnement(monkeypatch, valeur, attendu):
    if valeur is None:
        monkeypatch.delenv("QT_PLAFOND_IA_JOUR", raising=False)
    else:
        monkeypatch.setenv("QT_PLAFOND_IA_JOUR", valeur)
    assert plafond_ia_du_jour() == attendu


def test_limiteur_par_cle_independant():
    limiteur = LimiteurAppels(1, 60)
    assert limiteur.autoriser("a") and not limiteur.autoriser("a")
    assert limiteur.autoriser("b")
