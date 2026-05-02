"""
tests/test_history_store.py
===========================
Tests de la persistance JSON de l'historique.

Invariants critiques :
- charger() retourne [] si fichier absent (premier usage, jamais d'erreur)
- charger() retourne [] si fichier corrompu (jamais d'exception qui fait
  crasher l'app au demarrage)
- ajouter() respecte la taille max (troncature)
- ajouter() positionne la nouvelle entree en tete (plus recent en haut)
- effacer() est idempotent (ok si fichier deja absent)
- Les caracteres accentues sont preserves (encodage UTF-8 sans echappement)

Tous les tests utilisent tmp_path pour isoler le filesystem -- on ne
touche jamais a ~/.quant_terminal/ pendant les tests.
"""

import json
from pathlib import Path

import pytest

from core.history_store import (
    charger_historique,
    sauvegarder_historique,
    ajouter_entree,
    effacer_historique,
    _chemin_fichier_historique,
)


# === charger_historique ===================================================


def test_charger_fichier_absent_retourne_liste_vide(tmp_path):
    """Premiere utilisation : pas de fichier -> [] sans erreur."""
    assert charger_historique(repertoire=tmp_path) == []


def test_charger_fichier_valide(tmp_path):
    fichier = tmp_path / "historique.json"
    fichier.write_text('[{"date": "01/01/2024", "perf": 5.2}]', encoding="utf-8")
    assert charger_historique(repertoire=tmp_path) == [
        {"date": "01/01/2024", "perf": 5.2}
    ]


def test_charger_json_corrompu_retourne_liste_vide(tmp_path):
    """Fichier illisible : on ne crashe pas, on repart de [] et on log."""
    fichier = tmp_path / "historique.json"
    fichier.write_text("{ ceci n'est pas du json valide", encoding="utf-8")
    assert charger_historique(repertoire=tmp_path) == []


def test_charger_json_pas_une_liste_retourne_vide(tmp_path):
    """Si on lit un objet ou un nombre au lieu d'une liste, on ignore."""
    fichier = tmp_path / "historique.json"
    fichier.write_text('{"pas": "une liste"}', encoding="utf-8")
    assert charger_historique(repertoire=tmp_path) == []


# === sauvegarder_historique ===============================================


def test_sauvegarder_cree_le_repertoire(tmp_path):
    """Le sous-dossier est cree automatiquement s'il manque."""
    cible = tmp_path / "sous" / "dossier"
    assert sauvegarder_historique([{"a": 1}], repertoire=cible) is True
    assert (cible / "historique.json").exists()


def test_sauvegarder_format_json_valide(tmp_path):
    sauvegarder_historique([{"a": 1}, {"b": 2}], repertoire=tmp_path)
    contenu = (tmp_path / "historique.json").read_text(encoding="utf-8")
    assert json.loads(contenu) == [{"a": 1}, {"b": 2}]


def test_sauvegarder_preserve_caracteres_accentues(tmp_path):
    """Pas d'echappement Unicode : le JSON sur disque reste lisible."""
    entree = [{"scenario": "Crise economique européenne et déflation"}]
    sauvegarder_historique(entree, repertoire=tmp_path)
    contenu = (tmp_path / "historique.json").read_text(encoding="utf-8")
    assert "européenne" in contenu
    assert "déflation" in contenu


def test_sauvegarder_round_trip(tmp_path):
    """Ce qu'on ecrit, on le relit identique."""
    historique = [
        {"date": "01/01/2024 10:00", "scenario": "Test", "perf": 5.2},
        {"date": "02/01/2024 11:00", "scenario": "Autre", "perf": -3.1},
    ]
    sauvegarder_historique(historique, repertoire=tmp_path)
    assert charger_historique(repertoire=tmp_path) == historique


# === ajouter_entree =======================================================


def test_ajouter_insere_en_tete(tmp_path):
    historique = [{"id": 1}, {"id": 2}]
    nouveau = ajouter_entree(historique, {"id": 3}, taille_max=10,
                              repertoire=tmp_path)
    assert nouveau[0] == {"id": 3}
    assert nouveau == [{"id": 3}, {"id": 1}, {"id": 2}]


def test_ajouter_tronque_a_taille_max(tmp_path):
    historique = [{"id": i} for i in range(10)]
    nouveau = ajouter_entree(historique, {"id": "new"}, taille_max=5,
                              repertoire=tmp_path)
    assert len(nouveau) == 5
    assert nouveau[0] == {"id": "new"}
    # Les 4 plus recents (avant troncature) sont conserves
    assert nouveau[1] == {"id": 0}


def test_ajouter_persiste_sur_disque(tmp_path):
    """Apres un ajouter(), un charger() doit retrouver le contenu."""
    ajouter_entree([], {"perf": 12.5}, taille_max=10, repertoire=tmp_path)
    relu = charger_historique(repertoire=tmp_path)
    assert relu == [{"perf": 12.5}]


def test_ajouter_sur_liste_vide(tmp_path):
    nouveau = ajouter_entree([], {"id": 1}, taille_max=10, repertoire=tmp_path)
    assert nouveau == [{"id": 1}]


# === effacer_historique ===================================================


def test_effacer_supprime_le_fichier(tmp_path):
    sauvegarder_historique([{"a": 1}], repertoire=tmp_path)
    fichier = tmp_path / "historique.json"
    assert fichier.exists()
    assert effacer_historique(repertoire=tmp_path) is True
    assert not fichier.exists()


def test_effacer_idempotent_si_fichier_absent(tmp_path):
    """Pas d'erreur si on tente de supprimer un fichier qui n'existe pas."""
    assert effacer_historique(repertoire=tmp_path) is True


# === _chemin_fichier_historique ==========================================


def test_chemin_par_defaut_est_dans_home(monkeypatch, tmp_path):
    """Sans override, on cible bien ~/.quant_terminal/."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))  # Windows
    chemin = _chemin_fichier_historique()
    assert chemin.name == "historique.json"
    assert chemin.parent.name == ".quant_terminal"
