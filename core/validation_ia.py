"""
core/validation_ia.py
=====================
L'IA à l'épreuve de l'histoire : compare les chocs estimés par l'IA (crise
décrite sans être nommée ni datée) aux vraies performances des actifs.

Calculs purs, sans réseau : écarts en points, sens de variation, corrélation,
agrégats, et garde-fous sur la neutralité des descriptions envoyées à l'IA.
Utilisé par scripts/valider_ia_historique.py.
"""

import math
import re
import unicodedata
from datetime import date
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Sequence

import pandas as pd


# --- Constantes propres à la validation (à déplacer dans config.py si besoin) ---
# Sous ce mouvement réel (en points de %), le sens de variation n'est pas net :
# l'actif n'entre pas dans le score « bon sens » (il reste dans l'erreur moyenne).
SEUIL_SENS_PTS = 2.0
# Taille minimale d'un échantillon pour calculer une corrélation.
MIN_POINTS_CORRELATION = 3
# Mots des noms de crises qui ne trahissent pas l'événement : tous les autres
# mots du nom (Lehman, Brexit, COVID, Ukraine…) sont interdits dans la description.
MOTS_GENERIQUES = {"krach", "crise", "bulle", "guerre", "petrolier", "petroliere"}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
_JOURS_PAR_MOIS = 365.25 / 12
_ANNEE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")


# === Performances réelles et estimations ===================================


def performances_reelles(df: pd.DataFrame) -> Dict[str, float]:
    """Variation de chaque colonne entre la première et la dernière ligne, en %.
    Même calcul défensif que lancer_backtest (prix de départ nul ou absent → ignoré)."""
    if df is None or df.empty:
        return {}
    perfs = {}
    for cle in df.columns:
        serie = df[cle].dropna()
        if len(serie) < 2:
            continue
        depart, arrivee = float(serie.iloc[0]), float(serie.iloc[-1])
        if depart == 0 or not math.isfinite(depart) or not math.isfinite(arrivee):
            continue
        perfs[cle] = (arrivee / depart - 1) * 100
    return perfs


def convertir_estimations_en_euros(chocs: Dict[str, float], devises: Dict[str, Optional[str]],
                                   choc_eur_usd: float) -> Dict[str, float]:
    """Exprime en euros les chocs (décimaux) des actifs cotés en dollars, avec
    l'EUR/USD estimé par l'IA elle-même : comme le simulateur en mode « euros ».
    Les autres actifs gardent leur choc tel quel."""
    base = 1 + (choc_eur_usd or 0.0)
    if base <= 0:
        return dict(chocs)
    return {
        cle: ((1 + choc) / base - 1) if devises.get(cle) == "USD" else choc
        for cle, choc in chocs.items()
    }


# === Comparaison actif par actif ===========================================


def sens(valeur: float, seuil: float = 0.0) -> int:
    """+1 hausse, -1 baisse, 0 si le mouvement ne dépasse pas le seuil."""
    if valeur > seuil:
        return 1
    if valeur < -seuil:
        return -1
    return 0


def sens_correct(estime_pct: float, reel_pct: float,
                 seuil: float = SEUIL_SENS_PTS) -> Optional[bool]:
    """L'IA a-t-elle vu la bonne direction ? None si le vrai mouvement est trop
    faible (moins de `seuil` points) pour avoir un sens net."""
    sens_reel = sens(reel_pct, seuil)
    if sens_reel == 0:
        return None
    return sens(estime_pct) == sens_reel


def comparer_actifs(estimes_pct: Dict[str, float], reels_pct: Dict[str, float],
                    seuil: float = SEUIL_SENS_PTS) -> List[Dict]:
    """Une ligne par actif présent des deux côtés (ordre de `reels_pct`)."""
    lignes = []
    for cle, reel in reels_pct.items():
        if cle not in estimes_pct:
            continue
        estime = estimes_pct[cle]
        lignes.append({
            "cle": cle,
            "estime_pct": estime,
            "reel_pct": reel,
            "ecart_pts": estime - reel,
            "sens_correct": sens_correct(estime, reel, seuil),
        })
    return lignes


# === Statistiques ==========================================================


def correlation(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    """Corrélation de Pearson. None si trop peu de points ou série constante."""
    if len(xs) != len(ys) or len(xs) < MIN_POINTS_CORRELATION:
        return None
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    norme = math.sqrt(sum(a * a for a in dx) * sum(b * b for b in dy))
    if norme == 0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / norme


def _rangs(valeurs: Sequence[float]) -> List[float]:
    """Rangs (1 = plus petit), ex aequo au rang moyen."""
    ordre = sorted(range(len(valeurs)), key=lambda i: valeurs[i])
    rangs = [0.0] * len(valeurs)
    i = 0
    while i < len(ordre):
        j = i
        while j + 1 < len(ordre) and valeurs[ordre[j + 1]] == valeurs[ordre[i]]:
            j += 1
        for k in range(i, j + 1):
            rangs[ordre[k]] = (i + j) / 2 + 1
        i = j + 1
    return rangs


def correlation_rangs(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    """Corrélation de Spearman : peu sensible aux valeurs extrêmes (VIX)."""
    if len(xs) != len(ys) or len(xs) < MIN_POINTS_CORRELATION:
        return None
    return correlation(_rangs(xs), _rangs(ys))


def metriques_ecart(lignes: Iterable[Dict]) -> Dict:
    """Résumé d'une série de comparaisons (une crise, ou toutes)."""
    lignes = list(lignes)
    estimes = [l["estime_pct"] for l in lignes]
    reels = [l["reel_pct"] for l in lignes]
    ecarts = [abs(l["ecart_pts"]) for l in lignes]
    comptes = [l["sens_correct"] for l in lignes if l["sens_correct"] is not None]
    nb_corrects = sum(1 for c in comptes if c)
    amplitude_reelle = sum(abs(r) for r in reels)
    return {
        "nb_actifs": len(lignes),
        "erreur_moyenne_pts": mean(ecarts) if ecarts else None,
        "erreur_mediane_pts": median(ecarts) if ecarts else None,
        # > 0 : l'IA est en moyenne trop optimiste ; < 0 : trop pessimiste.
        "biais_moyen_pts": mean(l["ecart_pts"] for l in lignes) if lignes else None,
        "nb_sens_comptes": len(comptes),
        "nb_sens_corrects": nb_corrects,
        "part_sens_correct": nb_corrects / len(comptes) if comptes else None,
        "correlation": correlation(estimes, reels),
        "correlation_rangs": correlation_rangs(estimes, reels),
        # < 1 : les chocs de l'IA sont plus petits que les vrais mouvements.
        "ratio_amplitude": (sum(abs(e) for e in estimes) / amplitude_reelle
                            if amplitude_reelle else None),
    }


def agreger(listes_de_lignes: Iterable[Iterable[Dict]]) -> Dict:
    """Métriques sur toutes les comparaisons réunies (chaque actif de chaque crise
    pèse autant), plus le nombre de crises."""
    listes = [list(l) for l in listes_de_lignes]
    resultat = metriques_ecart(ligne for liste in listes for ligne in liste)
    resultat["nb_crises"] = sum(1 for liste in listes if liste)
    return resultat


def arrondir(valeur, decimales: int = 2):
    """Arrondi pour le JSON (récursif sur dict/list, None et booléens intacts)."""
    if isinstance(valeur, dict):
        return {k: arrondir(v, decimales) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [arrondir(v, decimales) for v in valeur]
    if isinstance(valeur, float):
        return round(valeur, decimales) if math.isfinite(valeur) else None
    return valeur


# === Textes envoyés à l'IA =================================================


def nombre_de_mois(debut: date, fin: date) -> int:
    """Durée arrondie au mois le plus proche (au moins 1)."""
    return max(1, round((fin - debut).days / _JOURS_PAR_MOIS))


def duree_en_mots(debut: date, fin: date) -> str:
    """« environ 6 mois », « environ 1 an et 8 mois », « environ 2 ans »."""
    mois = nombre_de_mois(debut, fin)
    if mois < 12:
        return f"environ {mois} mois"
    ans, reste = divmod(mois, 12)
    texte_ans = f"{ans} an{'s' if ans > 1 else ''}"
    return f"environ {texte_ans}" + (f" et {reste} mois" if reste else "")


def date_en_toutes_lettres(d: date) -> str:
    """date(2008, 9, 1) → « 1er septembre 2008 »."""
    jour = "1er" if d.day == 1 else str(d.day)
    return f"{jour} {MOIS[d.month - 1]} {d.year}"


def indice_date(debut: date, fin: date) -> str:
    """Phrase ajoutée à la description pour la variante « avec date » (mesure du biais)."""
    return (f"Indice : la période étudiée va du {date_en_toutes_lettres(debut)} "
            f"au {date_en_toutes_lettres(fin)}.")


def _sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def _mots(texte: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", _sans_accents(texte))


def verifier_neutralite(description: str, nom_crise: str) -> Optional[str]:
    """Message d'erreur si la description trahit la crise (année, mois, nom propre
    tiré de son nom) ; None si elle est neutre."""
    if not description or not description.strip():
        return "Description vide."
    annee = _ANNEE.search(description)
    if annee:
        return f"La description contient une année ({annee.group(0)})."
    mots = set(_mots(description))
    mois_trouves = [m for m in MOIS if _sans_accents(m) in mots]
    if mois_trouves:
        return f"La description contient un nom de mois ({mois_trouves[0]})."
    interdits = {m for m in _mots(nom_crise)
                 if len(m) >= 4 and not m.isdigit() and m not in MOTS_GENERIQUES}
    trouves = sorted(interdits & mots)
    if trouves:
        return f"La description reprend le nom de la crise ({', '.join(trouves)})."
    return None


def crise_reconnue(textes: Iterable[Optional[str]], debut: date, fin: date) -> bool:
    """L'IA a-t-elle reconnu la crise ? Oui si sa réponse cite une année de la période."""
    annees = set(range(debut.year, fin.year + 1))
    for texte in textes:
        if not texte:
            continue
        if any(int(a) in annees for a in _ANNEE.findall(str(texte))):
            return True
    return False
