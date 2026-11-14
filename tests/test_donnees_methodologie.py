"""
tests/test_donnees_methodologie.py
==================================
Garde-fou de synchronisation : la page Méthodologie du site (donnees.ts)
recopie à la main des réglages du moteur Python. Ce test lit le fichier
TypeScript comme du texte et compare chaque valeur aux vraies constantes
de config.py, schemas.py et market_data.py.
"""

import ast
import math
import re
from pathlib import Path

import pytest
from annotated_types import Ge, Le

import config
import schemas

RACINE = Path(__file__).resolve().parent.parent
FICHIER_DONNEES = RACINE / "web" / "src" / "components" / "methodologie" / "donnees.ts"
FICHIER_MARKET_DATA = RACINE / "market_data.py"


# ------------------------------------------------------------------
# Lecture du fichier TypeScript
# ------------------------------------------------------------------

def _texte_donnees() -> str:
    return FICHIER_DONNEES.read_text(encoding="utf-8")


def _bloc(nom: str) -> str:
    """Corps (entre accolades ou crochets) de `export const <nom> ...`."""
    texte = _texte_donnees()
    m = re.search(rf"export const {nom}\b[^=]*=\s*([{{\[])", texte)
    assert m, f"donnees.ts : objet exporté {nom} introuvable"
    ouvrant = m.group(1)
    fermant = "}" if ouvrant == "{" else "]"
    profondeur, debut = 0, m.end(1)
    for i in range(m.start(1), len(texte)):
        if texte[i] == ouvrant:
            profondeur += 1
        elif texte[i] == fermant:
            profondeur -= 1
            if profondeur == 0:
                return texte[debut:i]
    raise AssertionError(f"donnees.ts : fin de {nom} introuvable")


def _lire_valeur(brut: str):
    brut = brut.strip()
    if brut.startswith('"'):
        return brut.strip('"')
    return float(brut)


def _entrees_parametres() -> dict:
    """{cle: (valeur, commentaire)} pour chaque ligne `cle: valeur, // commentaire`."""
    entrees = {}
    motif = re.compile(r'^\s*(\w+)\s*:\s*("[^"]*"|-?[\d.]+)\s*,\s*//\s*(.*)$')
    for ligne in _bloc("PARAMETRES").splitlines():
        m = motif.match(ligne)
        if m:
            entrees[m.group(1)] = (_lire_valeur(m.group(2)), m.group(3).strip())
    return entrees


def _entrees_bornes_autres() -> dict:
    """{cle: ((min, max), commentaire)}."""
    entrees = {}
    motif = re.compile(r"^\s*(\w+)\s*:\s*\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]\s*,\s*//\s*(.*)$")
    for ligne in _bloc("BORNES_AUTRES").splitlines():
        m = motif.match(ligne)
        if m:
            entrees[m.group(1)] = ((float(m.group(2)), float(m.group(3))), m.group(4).strip())
    return entrees


def _entrees_bornes_ia() -> dict:
    """{actif: (pire, meilleur)} depuis BORNES_IA."""
    motif = re.compile(r'\[\s*"([^"]+)"\s*,\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]')
    return {
        m.group(1): (float(m.group(2)), float(m.group(3)))
        for m in motif.finditer(_bloc("BORNES_IA"))
    }


# ------------------------------------------------------------------
# Valeurs du moteur
# ------------------------------------------------------------------

def _jours_volatilite_moteur() -> int:
    """Défaut de `jours` dans market_data.get_volatilites_historiques (lu par ast : pas d'import réseau)."""
    arbre = ast.parse(FICHIER_MARKET_DATA.read_text(encoding="utf-8"))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.FunctionDef) and noeud.name == "get_volatilites_historiques":
            args = noeud.args.args
            defauts = dict(zip([a.arg for a in args[len(args) - len(noeud.args.defaults):]],
                               noeud.args.defaults))
            return ast.literal_eval(defauts["jours"])
    raise AssertionError("market_data.get_volatilites_historiques introuvable")


def _en_pct(x: float) -> float:
    return x * 100


# cle de PARAMETRES -> (nom de la constante attendu dans le commentaire, valeur attendue)
CORRESPONDANCES_PARAMETRES = {
    "nbSimulations": ("NB_SIMULATIONS_MONTE_CARLO", config.NB_SIMULATIONS_MONTE_CARLO),
    "cheminsConserves": ("NB_CHEMINS_CONSERVES", config.NB_CHEMINS_CONSERVES),
    "joursVolatilite": ("get_volatilites_historiques", _jours_volatilite_moteur()),
    "anneesCorrelation": ("FENETRE_CALIBRATION_JOURS", config.FENETRE_CALIBRATION_JOURS / 365),
    "perteMaxQuotidiennePct": ("PERTE_MAX_QUOTIDIENNE", _en_pct(config.PERTE_MAX_QUOTIDIENNE)),
    "horizonMin": ("HORIZON_MIN", config.HORIZON_MIN),
    "horizonMax": ("HORIZON_MAX", config.HORIZON_MAX),
    "horizonDefaut": ("HORIZON_DEFAUT", config.HORIZON_DEFAUT),
    "tauxSansRisqueSecoursPct": ("TAUX_SANS_RISQUE_ANNUEL", _en_pct(config.TAUX_SANS_RISQUE_ANNUEL)),
    "blocBootstrapSeances": ("BOOTSTRAP_TAILLE_BLOC", config.BOOTSTRAP_TAILLE_BLOC),
    "minSeancesBootstrap": ("BOOTSTRAP_MIN_SEANCES", config.BOOTSTRAP_MIN_SEANCES),
    "studentDegresLiberte": ("STUDENT_DEGRES_LIBERTE", config.STUDENT_DEGRES_LIBERTE),
    "autocorrelation": ("MOMENTUM_AUTOCORRELATION", config.MOMENTUM_AUTOCORRELATION),
    "accelerationPct": ("MOMENTUM_ACCELERATION", _en_pct(config.MOMENTUM_ACCELERATION)),
    "criseCreuxPctHorizon": ("CRISE_FRACTION_CREUX", _en_pct(config.CRISE_FRACTION_CREUX)),
    "criseDepassementPct": ("CRISE_DEPASSEMENT", _en_pct(config.CRISE_DEPASSEMENT)),
    "incertitudePartCommunePct": ("INCERTITUDE_IA_CORRELATION", _en_pct(config.INCERTITUDE_IA_CORRELATION)),
    "fourchetteAggravation": ("FOURCHETTE_ELARGISSEMENT_AGGRAVATION", config.FOURCHETTE_ELARGISSEMENT_AGGRAVATION),
    "fourchetteAttenuation": ("FOURCHETTE_ELARGISSEMENT_ATTENUATION", config.FOURCHETTE_ELARGISSEMENT_ATTENUATION),
    "fourchetteDemiLargeurMinPct": ("FOURCHETTE_DEMI_LARGEUR_MIN", _en_pct(config.FOURCHETTE_DEMI_LARGEUR_MIN)),
}

# cle de PARAMETRES -> (nom du réglage IA, identifiant du modèle)
CORRESPONDANCES_MODELES = {
    "modeleIa": ("IA_ANALYSE", config.IA_ANALYSE["model"]),
    "modeleIaSecours": ("IA_ANALYSE_SECOURS", config.IA_ANALYSE_SECOURS["model"]),
}


def _bornes_champ(modele, champ: str) -> tuple:
    """(ge, le) d'un Field pydantic."""
    meta = modele.model_fields[champ].metadata
    ge = next(m.ge for m in meta if isinstance(m, Ge))
    le = next(m.le for m in meta if isinstance(m, Le))
    return ge, le


# cle de BORNES_AUTRES -> (référence attendue dans le commentaire, (min, max) attendus)
CORRESPONDANCES_BORNES_AUTRES = {
    "inflationPoints": ("ChocsMacro.inflation", _bornes_champ(schemas.ChocsMacro, "inflation")),
    "tauxDirecteursPoints": ("ChocsMacro.taux_directeurs", _bornes_champ(schemas.ChocsMacro, "taux_directeurs")),
    "actifPersoPct": ("_BORNE_GENERIQUE_CUSTOM", tuple(_en_pct(x) for x in schemas._BORNE_GENERIQUE_CUSTOM)),
}


def _normaliser_modele(texte: str) -> str:
    """« GPT-6.1 Terra » et « gpt-6.1-terra » -> « gpt-6.1-terra »."""
    return re.sub(r"[\s_-]+", "-", texte.strip().lower())


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_toutes_les_cles_de_parametres_sont_couvertes():
    cles_ts = set(_entrees_parametres())
    cles_test = set(CORRESPONDANCES_PARAMETRES) | set(CORRESPONDANCES_MODELES)
    assert cles_ts == cles_test, (
        "PARAMETRES de donnees.ts et ce test ne couvrent pas les mêmes clés. "
        f"Absentes du test : {sorted(cles_ts - cles_test)} ; "
        f"absentes de donnees.ts : {sorted(cles_test - cles_ts)}"
    )
    assert len(CORRESPONDANCES_PARAMETRES) >= 15


@pytest.mark.parametrize("cle", sorted(CORRESPONDANCES_PARAMETRES))
def test_parametre_synchronise(cle):
    constante, attendu = CORRESPONDANCES_PARAMETRES[cle]
    valeur, commentaire = _entrees_parametres()[cle]
    assert constante in commentaire, (
        f"donnees.ts PARAMETRES.{cle} : le commentaire « {commentaire} » "
        f"devrait nommer {constante}"
    )
    assert math.isclose(valeur, attendu, rel_tol=1e-9, abs_tol=1e-9), (
        f"{constante} a changé côté moteur ({attendu}) mais donnees.ts "
        f"PARAMETRES.{cle} vaut encore {valeur}"
    )


@pytest.mark.parametrize("cle", sorted(CORRESPONDANCES_MODELES))
def test_modele_ia_synchronise(cle):
    reglage, identifiant = CORRESPONDANCES_MODELES[cle]
    libelle, commentaire = _entrees_parametres()[cle]
    assert reglage in commentaire, (
        f"donnees.ts PARAMETRES.{cle} : le commentaire « {commentaire} » devrait nommer {reglage}"
    )
    assert _normaliser_modele(libelle) == _normaliser_modele(identifiant), (
        f'{reglage}["model"] vaut « {identifiant} » mais donnees.ts '
        f"PARAMETRES.{cle} affiche « {libelle} »"
    )


def test_bornes_autres_toutes_couvertes():
    assert set(_entrees_bornes_autres()) == set(CORRESPONDANCES_BORNES_AUTRES)


@pytest.mark.parametrize("cle", sorted(CORRESPONDANCES_BORNES_AUTRES))
def test_borne_autre_synchronisee(cle):
    reference, (mn_attendu, mx_attendu) = CORRESPONDANCES_BORNES_AUTRES[cle]
    (mn, mx), commentaire = _entrees_bornes_autres()[cle]
    assert reference in commentaire, (
        f"donnees.ts BORNES_AUTRES.{cle} : le commentaire « {commentaire} » devrait nommer {reference}"
    )
    assert math.isclose(mn, mn_attendu, abs_tol=1e-9) and math.isclose(mx, mx_attendu, abs_tol=1e-9), (
        f"{reference} vaut [{mn_attendu}, {mx_attendu}] côté moteur mais donnees.ts "
        f"BORNES_AUTRES.{cle} vaut [{mn}, {mx}]"
    )


def test_bornes_ia_memes_actifs():
    actifs_ts = set(_entrees_bornes_ia())
    actifs_moteur = set(schemas.BORNES_ACTIFS)
    assert actifs_ts == actifs_moteur, (
        "BORNES_IA (donnees.ts) et schemas.BORNES_ACTIFS divergent. "
        f"Manquants dans donnees.ts : {sorted(actifs_moteur - actifs_ts)} ; "
        f"en trop : {sorted(actifs_ts - actifs_moteur)}"
    )


@pytest.mark.parametrize("actif", sorted(schemas.BORNES_ACTIFS))
def test_borne_ia_synchronisee(actif):
    bornes_ts = _entrees_bornes_ia()
    if actif not in bornes_ts:
        pytest.skip("absence déjà signalée par test_bornes_ia_memes_actifs")
    mn, mx = bornes_ts[actif]
    mn_attendu, mx_attendu = schemas.BORNES_ACTIFS[actif]
    assert math.isclose(mn, mn_attendu, abs_tol=1e-9) and math.isclose(mx, mx_attendu, abs_tol=1e-9), (
        f'schemas.BORNES_ACTIFS["{actif}"] vaut ({mn_attendu}, {mx_attendu}) '
        f"mais donnees.ts BORNES_IA affiche ({mn}, {mx})"
    )
