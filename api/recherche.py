"""
api/recherche.py
================
Recherche d'actifs par nom (« Total », « Apple »...) via Yahoo Finance.
Ne leve jamais d'exception : en cas de panne, repli sur une liste vide + message.
"""
import re
import unicodedata
from typing import Any, Dict, List

import requests

from config import (
    RECHERCHE_ALIAS, RECHERCHE_LONGUEUR_MAX, RECHERCHE_LONGUEUR_MIN, RECHERCHE_RESULTATS_MAX, RECHERCHE_TIMEOUT_S,
    RECHERCHE_TTL_S, RECHERCHE_TYPES, RECHERCHE_URL_YAHOO,
)
from core.cache import cache_ttl
from logger import get_logger

log = get_logger("recherche")

_INTERDITS = re.compile(r"[^\w\s.&\-]", re.UNICODE)
_MESSAGE_PANNE = "La recherche est momentanément indisponible. Saisissez le symbole Yahoo directement."


def nettoyer_requete(q: Any) -> str:
    """Garde lettres, chiffres, espaces et . - & ; renvoie "" si hors bornes."""
    if not isinstance(q, str):
        return ""
    texte = " ".join(_INTERDITS.sub(" ", q.replace("_", " ")).split())
    if not (RECHERCHE_LONGUEUR_MIN <= len(texte) <= RECHERCHE_LONGUEUR_MAX):
        return ""
    return texte


def _normaliser(brut: List[dict]) -> List[Dict[str, Any]]:
    """Ne garde que actions/ETF/indices/cryptos/fonds (pas de futures ni d'options)."""
    sortie: List[Dict[str, Any]] = []
    vus = set()
    for r in brut or []:
        if not isinstance(r, dict):
            continue
        symbole = str(r.get("symbol") or "").strip().upper()
        type_ = RECHERCHE_TYPES.get(str(r.get("quoteType") or r.get("typeDisp") or "").upper())
        if not symbole or type_ is None or symbole in vus or "=F" in symbole:
            continue
        vus.add(symbole)
        nom = str(r.get("longname") or r.get("shortname") or r.get("longName") or r.get("shortName") or symbole).strip()
        sortie.append({
            "symbole": symbole,
            "nom": nom[:80],
            "type": type_,
            "bourse": str(r.get("exchDisp") or r.get("exchange") or "") or None,
            "devise": r.get("currency") or None,
        })
        if len(sortie) >= RECHERCHE_RESULTATS_MAX:
            break
    return sortie


def _interroger_yahoo(q: str) -> List[dict]:
    """yfinance.Search si disponible, sinon l'endpoint public de recherche Yahoo."""
    try:
        import yfinance as yf
        if hasattr(yf, "Search"):
            return list(yf.Search(q, max_results=RECHERCHE_RESULTATS_MAX * 2, news_count=0, timeout=RECHERCHE_TIMEOUT_S).quotes)
    except Exception as e:
        log.warning("yfinance.Search indisponible pour %r : %s", q, e)
    r = requests.get(
        RECHERCHE_URL_YAHOO,
        params={"q": q, "quotesCount": RECHERCHE_RESULTATS_MAX * 2, "newsCount": 0},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=RECHERCHE_TIMEOUT_S,
    )
    r.raise_for_status()
    return r.json().get("quotes", [])


def _sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte.lower()) if unicodedata.category(c) != "Mn")


def _alias(q: str) -> List[Dict[str, Any]]:
    """Grandes valeurs françaises que Yahoo ne trouve pas par leur nom courant."""
    cle = _sans_accents(q).strip()
    if len(cle) < 3:
        return []
    trouves = []
    for noms, (symbole, nom) in RECHERCHE_ALIAS.items():
        if any(n.startswith(cle) or cle in n for n in noms.split()) or cle in noms:
            trouves.append({"symbole": symbole, "nom": nom, "type": "action", "bourse": "Paris", "devise": "EUR"})
    return trouves


def _fusionner(premiers: List[Dict[str, Any]], suivants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    vus, sortie = set(), []
    for r in premiers + suivants:
        if r["symbole"] not in vus:
            vus.add(r["symbole"])
            sortie.append(r)
    return sortie[:RECHERCHE_RESULTATS_MAX]


@cache_ttl(RECHERCHE_TTL_S, garder=lambda res: res.get("message") is None)
def _rechercher(q: str) -> Dict[str, Any]:
    alias = _alias(q)
    try:
        resultats = _normaliser(_interroger_yahoo(q))
    except Exception as e:
        log.warning("Recherche Yahoo en echec pour %r : %s", q, e)
        if alias:
            return {"resultats": alias[:RECHERCHE_RESULTATS_MAX], "message": None}
        return {"resultats": [], "message": _MESSAGE_PANNE}
    return {"resultats": _fusionner(alias, resultats), "message": None}


def rechercher_actifs(q: str) -> Dict[str, Any]:
    """Renvoie {"resultats": [...], "message": str | None}, sans jamais lever."""
    try:
        propre = nettoyer_requete(q)
        if not propre:
            return {"resultats": [], "message": f"Saisissez entre {RECHERCHE_LONGUEUR_MIN} et {RECHERCHE_LONGUEUR_MAX} caractères (lettres, chiffres, espaces)."}
        return _rechercher(propre)
    except Exception:
        log.error("Recherche d'actifs : erreur inattendue", exc_info=True)
        return {"resultats": [], "message": _MESSAGE_PANNE}
