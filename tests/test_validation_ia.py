"""
tests/test_validation_ia.py
===========================
Calculs purs de « L'IA à l'épreuve de l'histoire » (core/validation_ia.py).
"""

import math
from datetime import date

import pandas as pd
import pytest

from core.validation_ia import (
    agreger, arrondir, comparer_actifs, convertir_estimations_en_euros, correlation,
    correlation_rangs, crise_reconnue, date_en_toutes_lettres, duree_en_mots, indice_date,
    metriques_ecart, performances_reelles, sens, sens_correct, verifier_neutralite,
)


def _ligne(cle, estime, reel):
    return comparer_actifs({cle: estime}, {cle: reel})[0]


class TestPerformancesReelles:
    def test_variation_premiere_derniere_ligne(self):
        df = pd.DataFrame({"A": [100.0, 90.0, 120.0], "B": [50.0, 50.0, 25.0]})
        perfs = performances_reelles(df)
        assert perfs["A"] == pytest.approx(20.0)
        assert perfs["B"] == pytest.approx(-50.0)

    def test_prix_de_depart_nul_ignore(self):
        df = pd.DataFrame({"A": [0.0, 10.0], "B": [10.0, 11.0]})
        assert set(performances_reelles(df)) == {"B"}

    def test_trous_de_cotation_ignores(self):
        df = pd.DataFrame({"A": [float("nan"), 10.0, 15.0]})
        assert performances_reelles(df)["A"] == pytest.approx(50.0)

    def test_dataframe_vide(self):
        assert performances_reelles(pd.DataFrame()) == {}


class TestConversionEuros:
    def test_actif_en_dollars_converti_avec_l_eur_usd_estime(self):
        # L'euro perd 10 % : un actif stable en dollars gagne 11,1 % en euros.
        chocs = {"S&P 500": 0.0, "CAC 40": -0.05, "VIX": 0.8, "EUR_USD": -0.10}
        devises = {"S&P 500": "USD", "CAC 40": "EUR", "VIX": None, "EUR_USD": None}
        eur = convertir_estimations_en_euros(chocs, devises, chocs["EUR_USD"])
        assert eur["S&P 500"] == pytest.approx(1 / 0.9 - 1)
        assert eur["CAC 40"] == -0.05
        assert eur["VIX"] == 0.8
        assert eur["EUR_USD"] == -0.10

    def test_eur_usd_aberrant_ne_casse_rien(self):
        assert convertir_estimations_en_euros({"Or": 0.1}, {"Or": "USD"}, -1.0) == {"Or": 0.1}


class TestSens:
    def test_sens_avec_seuil(self):
        assert sens(3.0, 2.0) == 1
        assert sens(-3.0, 2.0) == -1
        assert sens(1.5, 2.0) == 0
        assert sens(0.0) == 0

    def test_bon_et_mauvais_sens(self):
        assert sens_correct(-10.0, -25.0) is True
        assert sens_correct(5.0, -25.0) is False

    def test_estimation_nulle_compte_comme_faux(self):
        assert sens_correct(0.0, 12.0) is False

    def test_mouvement_reel_trop_faible_non_compte(self):
        assert sens_correct(8.0, 1.2) is None
        assert sens_correct(8.0, -1.9, seuil=2.0) is None


class TestComparerActifs:
    def test_lignes_dans_l_ordre_des_vrais_cours(self):
        lignes = comparer_actifs({"B": 5.0, "A": -10.0, "Z": 1.0}, {"A": -20.0, "B": 3.0, "C": 4.0})
        assert [l["cle"] for l in lignes] == ["A", "B"]
        assert lignes[0]["ecart_pts"] == pytest.approx(10.0)
        assert lignes[0]["sens_correct"] is True


class TestCorrelations:
    def test_pearson_parfaite_et_inverse(self):
        assert correlation([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
        assert correlation([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)

    def test_pearson_indefinie(self):
        assert correlation([1, 2], [1, 2]) is None
        assert correlation([1, 1, 1], [1, 2, 3]) is None
        assert correlation([1, 2, 3], [1, 2]) is None

    def test_spearman_insensible_a_l_echelle(self):
        assert correlation_rangs([1, 2, 3, 4], [1, 10, 100, 10000]) == pytest.approx(1.0)

    def test_spearman_ex_aequo(self):
        rho = correlation_rangs([1, 2, 2, 3], [1, 2, 3, 4])
        assert 0.9 < rho < 1.0


class TestMetriques:
    def test_valeurs_connues(self):
        lignes = [_ligne("A", -10.0, -20.0), _ligne("B", 10.0, 5.0), _ligne("C", 3.0, -1.0)]
        m = metriques_ecart(lignes)
        assert m["nb_actifs"] == 3
        assert m["erreur_moyenne_pts"] == pytest.approx((10 + 5 + 4) / 3)
        assert m["erreur_mediane_pts"] == pytest.approx(5.0)
        assert m["biais_moyen_pts"] == pytest.approx((10 + 5 + 4) / 3)
        # C : mouvement réel de 1 point, trop faible pour compter dans le sens.
        assert (m["nb_sens_comptes"], m["nb_sens_corrects"]) == (2, 2)
        assert m["part_sens_correct"] == 1.0
        assert m["ratio_amplitude"] == pytest.approx(23 / 26)
        assert m["correlation"] > 0.9

    def test_liste_vide(self):
        m = metriques_ecart([])
        assert m["nb_actifs"] == 0
        assert m["erreur_moyenne_pts"] is None
        assert m["part_sens_correct"] is None
        assert m["correlation"] is None

    def test_agreger_regroupe_toutes_les_comparaisons(self):
        crise_1 = [_ligne("A", -10.0, -20.0), _ligne("B", 10.0, 5.0)]
        crise_2 = [_ligne("A", 5.0, -5.0)]
        g = agreger([crise_1, crise_2, []])
        assert g["nb_crises"] == 2
        assert g["nb_actifs"] == 3
        assert g["erreur_moyenne_pts"] == pytest.approx(25 / 3)
        assert (g["nb_sens_comptes"], g["nb_sens_corrects"]) == (3, 2)


def test_arrondir_recursif():
    donnees = {"a": 1.23456, "b": [2.34567, None, True], "c": {"d": float("nan")}, "e": 3}
    assert arrondir(donnees, 2) == {"a": 1.23, "b": [2.35, None, True], "c": {"d": None}, "e": 3}


class TestTextes:
    @pytest.mark.parametrize("debut, fin, attendu", [
        (date(2020, 2, 15), date(2020, 4, 15), "environ 2 mois"),
        (date(2008, 9, 1), date(2009, 3, 9), "environ 6 mois"),
        (date(2014, 6, 1), date(2016, 2, 11), "environ 1 an et 8 mois"),
        (date(2000, 3, 10), date(2002, 10, 9), "environ 2 ans et 7 mois"),
        (date(2020, 1, 1), date(2021, 1, 1), "environ 1 an"),
        (date(2020, 1, 1), date(2020, 1, 5), "environ 1 mois"),
    ])
    def test_duree_en_mots(self, debut, fin, attendu):
        assert duree_en_mots(debut, fin) == attendu

    def test_dates_en_francais(self):
        assert date_en_toutes_lettres(date(2008, 9, 1)) == "1er septembre 2008"
        assert date_en_toutes_lettres(date(2016, 12, 31)) == "31 décembre 2016"
        assert indice_date(date(2016, 6, 23), date(2016, 12, 31)) == (
            "Indice : la période étudiée va du 23 juin 2016 au 31 décembre 2016.")


class TestNeutralite:
    def test_description_neutre_acceptee(self):
        texte = "Une crise bancaire américaine : une grande banque d'affaires fait faillite."
        assert verifier_neutralite(texte, "Krach 2008 (Lehman)") is None

    def test_annee_refusee(self):
        assert "année" in verifier_neutralite("Comme en 2008, les banques…", "Krach 2008 (Lehman)")

    def test_mois_refuse_meme_sans_accent(self):
        assert "mois" in verifier_neutralite("Un choc en fevrier.", "Brexit (2016)")

    def test_nom_de_la_crise_refuse(self):
        message = verifier_neutralite("La faillite de lehman brothers.", "Krach 2008 (Lehman)")
        assert "lehman" in message
        assert verifier_neutralite("Une épidémie de Covid.", "COVID-19 (mars 2020)") is not None

    def test_mots_generiques_du_nom_autorises(self):
        assert verifier_neutralite("Une crise pétrolière, puis un krach.", "Krach pétrolier (2014-2016)") is None

    def test_description_vide(self):
        assert verifier_neutralite("  ", "Brexit (2016)") == "Description vide."

    def test_crise_reconnue_si_annee_de_la_periode_citee(self):
        debut, fin = date(2014, 6, 1), date(2016, 2, 11)
        assert crise_reconnue(["Le contre-choc de 2015 sert de référence."], debut, fin)
        assert not crise_reconnue(["Comme le contre-choc de 1986.", None], debut, fin)
        assert not crise_reconnue([], debut, fin)


def test_correlation_resiste_aux_flottants():
    xs = [0.1 * i for i in range(10)]
    assert math.isclose(correlation(xs, [2 * x + 1 for x in xs]), 1.0)
