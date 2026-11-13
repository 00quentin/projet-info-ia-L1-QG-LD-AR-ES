"""
tests/test_couverture.py
========================
Tests du calcul de protection du portefeuille (core/couverture.py).
Les trajectoires viennent du vrai moteur de simulation (graine fixe).
"""

import numpy as np
import pytest

from core.couverture import (
    COUVERTURE_ECART_MAX_LIGNE, COUVERTURE_POIDS_MAX_LIGNE, COUVERTURE_ROTATION_MAX,
    arrondir_pourcentages, bornes_lignes, comparer_portefeuilles, faits_par_actif,
    justification_par_defaut, lister_changements, mesurer_risque, prix_relatifs,
    proposer_couverture, rotation, score_comparaison,
)
from simulation import generer_chemins

# Krach : actions et cryptos chutent, obligations et or montent.
CHOCS_KRACH = {"S&P 500": -0.30, "CAC 40": -0.25, "Bitcoin": -0.50,
               "Bons_Tresor_US_10Y": 0.06, "Or": 0.12}
POIDS = {"S&P 500": 0.35, "CAC 40": 0.20, "Bitcoin": 0.15, "Bons_Tresor_US_10Y": 0.20, "Or": 0.10}


def _trajectoires(chocs, nb=400, jours=60, graine=7):
    cles, chemins = generer_chemins({"actifs": chocs}, jours=jours, actifs=list(chocs),
                                    nb_simulations=nb, graine=graine)
    return cles, chemins


def _respecte_les_contraintes(initial, propose, figes=()):
    assert sum(propose.values()) == 100
    assert all(isinstance(v, int) and 0 <= v <= COUVERTURE_POIDS_MAX_LIGNE for v in propose.values())
    for k in propose:
        assert abs(propose[k] - initial[k]) <= COUVERTURE_ECART_MAX_LIGNE
        if k in figes:
            assert propose[k] <= initial[k]
    cles = list(initial)
    assert rotation(np.array([propose[k] for k in cles]), np.array([initial[k] for k in cles])) <= COUVERTURE_ROTATION_MAX


def test_arrondir_pourcentages_somme_100():
    assert arrondir_pourcentages({"a": 1, "b": 1, "c": 1}) == {"a": 34, "b": 33, "c": 33}
    p = arrondir_pourcentages({"a": 0.25 / 0.93, "b": 0.08 / 0.93, "c": 0.60 / 0.93})
    assert sum(p.values()) == 100 and p == {"a": 27, "b": 9, "c": 64}
    assert arrondir_pourcentages({"a": 0, "b": 0}) == {"a": 0, "b": 0}


def test_bornes_lignes_plafond_et_actifs_figes():
    bas, haut = bornes_lignes(np.array([50, 30, 20]), np.array([False, False, True]))
    assert list(haut) == [40, 40, 20]          # plafond 40 %, actif fige jamais renforce
    assert list(bas) == [35, 15, 5]
    # 100 % sur un actif : l'ecart maximal est leve pour pouvoir atteindre 100 %
    bas, haut = bornes_lignes(np.array([100, 0, 0]), np.zeros(3, dtype=bool))
    assert list(haut) == [40, 40, 40] and bas[0] == 40


def test_mesurer_risque_coherent_avec_les_metriques():
    cles, chemins = _trajectoires(CHOCS_KRACH)
    rel = prix_relatifs(chemins)
    w = np.array([POIDS[k] for k in cles])
    perte, proba = mesurer_risque(rel, w[None, :])
    assert 0 < perte[0] < 100 and 0 <= proba[0] <= 100
    ref = comparer_portefeuilles(chemins, cles, POIDS, POIDS, 10_000, 0.02)["avant"]["metriques"]
    assert perte[0] == pytest.approx(ref["max_dd"], rel=1e-6)
    assert proba[0] == pytest.approx(ref["proba_perte"], rel=1e-6)


def test_krach_renforce_les_valeurs_refuges_et_reduit_le_risque():
    cles, chemins = _trajectoires(CHOCS_KRACH, nb=1400)
    resultat, erreur = proposer_couverture(prix_relatifs(chemins[:400]), cles, POIDS)
    assert erreur is None
    initial, propose = resultat["initial_pct"], resultat["propose_pct"]
    _respecte_les_contraintes(initial, propose)
    assert propose["Or"] > initial["Or"] and propose["Bons_Tresor_US_10Y"] > initial["Bons_Tresor_US_10Y"]
    assert propose["Bitcoin"] < initial["Bitcoin"]
    assert resultat["score_propose"] < resultat["score_initial"]

    # Verification sur d'autres trajectoires que celles de la recherche
    comp = comparer_portefeuilles(chemins[400:], cles, POIDS, {k: v / 100 for k, v in propose.items()}, 10_000, 0.02)
    avant, apres = comp["avant"]["metriques"], comp["apres"]["metriques"]
    assert apres["max_dd"] < avant["max_dd"]
    assert apres["proba_perte"] <= avant["proba_perte"]
    score_avant, score_apres = score_comparaison(avant, apres)
    assert score_apres < score_avant
    assert len(comp["apres"]["bandes"]["mediane"]) == chemins.shape[1]


def test_ligne_trop_lourde_ramenee_au_plafond():
    poids = {"S&P 500": 0.10, "CAC 40": 0.05, "Bitcoin": 0.05, "Bons_Tresor_US_10Y": 0.70, "Or": 0.10}
    cles, chemins = _trajectoires(CHOCS_KRACH)
    resultat, erreur = proposer_couverture(prix_relatifs(chemins), cles, poids)
    assert erreur is None and resultat["plafond_impose"]
    assert resultat["propose_pct"]["Bons_Tresor_US_10Y"] == COUVERTURE_POIDS_MAX_LIGNE
    assert sum(resultat["propose_pct"].values()) == 100


def test_actif_fige_jamais_renforce():
    chocs = {**CHOCS_KRACH, "Or": -0.02, "Bons_Tresor_US_10Y": -0.02, "PERSO_KO": 0.30}
    cles, chemins = generer_chemins({"actifs": chocs}, jours=60, actifs=list(chocs), nb_simulations=400,
                                    actifs_extras={"PERSO_KO": {"prix": 60.0, "volatilite": 0.006}}, graine=3)
    poids = {**POIDS, "S&P 500": 0.25, "PERSO_KO": 0.10}
    resultat, erreur = proposer_couverture(prix_relatifs(chemins), cles, poids, cles_figees=["PERSO_KO"])
    assert erreur is None
    _respecte_les_contraintes(resultat["initial_pct"], resultat["propose_pct"], figes={"PERSO_KO"})


def test_portefeuille_deja_au_mieux_inchange():
    # Tous les actifs identiques : aucun transfert ne peut reduire le risque.
    chocs = {"A": -0.1, "B": -0.1, "C": -0.1}
    rng = np.random.default_rng(0)
    commun = np.exp(np.cumsum(rng.normal(-0.002, 0.01, size=(200, 59)), axis=1))
    rel = np.ones((200, 60, 3))
    rel[:, 1:, :] = commun[:, :, None]
    resultat, erreur = proposer_couverture(rel, list(chocs), {"A": 0.4, "B": 0.3, "C": 0.3})
    assert erreur is None
    assert resultat["propose_pct"] == resultat["initial_pct"] == {"A": 40, "B": 30, "C": 30}
    assert lister_changements(resultat["initial_pct"], resultat["propose_pct"]) == []


def test_refus_si_trop_peu_d_actifs():
    rel = np.ones((10, 5, 2))
    resultat, erreur = proposer_couverture(rel, ["S&P 500", "Or"], {"S&P 500": 0.5, "Or": 0.5})
    assert resultat is None and "au moins 3 actifs" in erreur
    resultat, erreur = proposer_couverture(np.ones((10, 5, 3)), ["A", "B", "C"], {"A": 0, "B": 0, "C": 0})
    assert resultat is None and "vide" in erreur


def test_lister_changements_tries_par_ampleur():
    lignes = lister_changements({"a": 30, "b": 30, "c": 40}, {"a": 40, "b": 25, "c": 35})
    assert [(l["cle"], l["ecart_pct"]) for l in lignes] == [("a", 10), ("b", -5), ("c", -5)]


def test_faits_par_actif():
    cles, chemins = _trajectoires(CHOCS_KRACH)
    faits = faits_par_actif(prix_relatifs(chemins), cles, POIDS)
    assert set(faits) == set(cles)
    # Les cryptos sont bien plus volatiles que les obligations
    assert faits["Bitcoin"]["volatilite_pct"] > 3 * faits["Bons_Tresor_US_10Y"]["volatilite_pct"]
    assert all(-1 <= f["correlation"] <= 1 for f in faits.values())


def test_justification_par_defaut():
    assert "choc estimé +12 %" in justification_par_defaut(10, 12.0, 15.0, 0.05)
    assert "exposé" in justification_par_defaut(-10, -30.0, 18.0, 0.9)
    assert "volatil" in justification_par_defaut(-5, 2.0, 60.0, 0.5)
    assert "plafond" in justification_par_defaut(-10, 5.0, 5.0, 0.2, plafond=True)
    assert "−2,5 %" in justification_par_defaut(5, -2.5, 6.0, 0.6)
