"""
tests/test_portfolio.py
=======================
Tests du calcul des poids du portefeuille et des allocations finales.
Invariants critiques : la somme des poids = 1.0, les calculs de rendement
sont coherents avec les chocs.
"""

import math
import pytest

from core.portfolio import calculer_poids, construire_allocations_finales


# === calculer_poids =======================================================

def test_profil_predefini_somme_a_1():
    """Tout profil predefini renvoie des poids dont la somme = 1.0."""
    actifs = ["S&P 500", "Or", "Bons_Tresor_US_10Y", "Bitcoin"]
    poids = calculer_poids("Equilibre (Normal)".replace("Equilibre", "Équilibré"),
                           actifs, {})
    assert poids
    assert math.isclose(sum(poids.values()), 1.0, abs_tol=1e-9)


def test_profil_personnalise_normalise_a_1():
    """Un profil personnalise est normalise meme si la somme != 100."""
    poids = calculer_poids("Personnalisé", ["S&P 500", "Or"],
                           {"S&P 500": 60, "Or": 40})
    assert math.isclose(sum(poids.values()), 1.0, abs_tol=1e-9)
    assert math.isclose(poids["S&P 500"], 0.6, abs_tol=1e-9)


def test_profil_personnalise_avec_zero_filtre():
    """Les actifs a 0% sont retires du portefeuille."""
    poids = calculer_poids("Personnalisé", ["S&P 500", "Or", "Bitcoin"],
                           {"S&P 500": 50, "Or": 50, "Bitcoin": 0})
    assert "Bitcoin" not in poids
    assert math.isclose(sum(poids.values()), 1.0, abs_tol=1e-9)


def test_profil_inexistant_donne_equiponderation():
    """Un profil inconnu + actifs selectionnes -> equipondere."""
    poids = calculer_poids("Profil_Bidon", ["S&P 500", "Or", "Bitcoin"], {})
    assert math.isclose(sum(poids.values()), 1.0, abs_tol=1e-9)
    for v in poids.values():
        assert math.isclose(v, 1/3, abs_tol=1e-9)


def test_profil_predefini_filtre_par_actifs_selectionnes():
    """Si on selectionne un sous-ensemble, seuls ces actifs sont presents
    avec une renormalisation a 1.0."""
    actifs = ["S&P 500", "Or"]  # sous-ensemble du profil Equilibre
    poids = calculer_poids("Équilibré (Normal)", actifs, {})
    assert set(poids.keys()).issubset(set(actifs))
    assert math.isclose(sum(poids.values()), 1.0, abs_tol=1e-9)


def test_aucun_actif_renvoie_dict_vide():
    poids = calculer_poids("Équilibré (Normal)", [], {})
    assert poids == {}


def test_profil_predefini_aucun_actif_du_profil_choisi():
    """Si aucun actif du profil predefini n'est dans la selection,
    on tombe sur l'equipondere (fallback)."""
    # ETF_Defense n'est dans aucun profil predefini, donc le profil
    # ne propose rien -> equipondere sur la selection
    poids = calculer_poids("Prudent (Hyper Sécurisé)", ["ETF_Defense"], {})
    assert math.isclose(sum(poids.values()), 1.0, abs_tol=1e-9)
    assert math.isclose(poids["ETF_Defense"], 1.0, abs_tol=1e-9)


# === construire_allocations_finales =======================================

def test_allocations_finales_capital_conserve_si_perf_zero():
    """Si toutes les perfs sont 0%, la valeur finale = capital initial."""
    perfs = {"S&P 500": 0.0, "Or": 0.0}
    poids = {"S&P 500": 0.6, "Or": 0.4}
    allocs, valeur_finale = construire_allocations_finales(perfs, poids, 10000)
    assert math.isclose(valeur_finale, 10000.0, abs_tol=1e-6)
    assert len(allocs) == 2


def test_allocations_finales_perf_positive_augmente_capital():
    """Avec des perfs positives, la valeur finale > capital initial."""
    perfs = {"S&P 500": 10.0, "Or": 20.0}  # +10% et +20%
    poids = {"S&P 500": 0.5, "Or": 0.5}
    _, valeur_finale = construire_allocations_finales(perfs, poids, 10000)
    # 5000*1.10 + 5000*1.20 = 5500 + 6000 = 11500
    assert math.isclose(valeur_finale, 11500.0, abs_tol=1e-6)


def test_allocations_finales_structure_par_actif():
    """Chaque dict allocation contient bien tous les champs attendus."""
    perfs = {"S&P 500": 5.0}
    poids = {"S&P 500": 1.0}
    allocs, _ = construire_allocations_finales(perfs, poids, 10000)
    assert len(allocs) == 1
    a = allocs[0]
    for cle in ("nom", "poids", "investi", "final", "rendement"):
        assert cle in a
    assert math.isclose(a["investi"], 10000.0)
    assert math.isclose(a["final"], 10500.0)
    assert math.isclose(a["rendement"], 0.05)


def test_allocations_finales_perf_manquante_traitee_comme_zero():
    """Si un actif est dans poids mais absent de perfs, perf = 0% (pas de KeyError)."""
    perfs = {"S&P 500": 10.0}  # Or absent
    poids = {"S&P 500": 0.5, "Or": 0.5}
    allocs, valeur_finale = construire_allocations_finales(perfs, poids, 10000)
    # 5000*1.10 + 5000*1.0 = 10500
    assert math.isclose(valeur_finale, 10500.0, abs_tol=1e-6)
    assert len(allocs) == 2


def test_allocations_finales_capital_negatif_impossible():
    """Pas de short -> avec un capital >0 et des perfs > -100%, valeur > 0."""
    perfs = {"S&P 500": -50.0, "Or": -30.0}
    poids = {"S&P 500": 0.5, "Or": 0.5}
    _, valeur_finale = construire_allocations_finales(perfs, poids, 10000)
    assert valeur_finale > 0
