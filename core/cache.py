"""
core/cache.py
=============
Cache memoire avec duree de vie (TTL), independant de Streamlit.

Pourquoi : le moteur (prix Yahoo, taux BCE, reponses IA) est partage entre
l'app Streamlit et l'API web. `st.cache_data` n'existe que dans Streamlit ;
ce decorateur offre le meme service (TTL + `.clear()`) partout.
"""

import copy
import functools
import threading
import time
from typing import Any, Callable, Hashable, List, Optional

# Borne la memoire : au-dela, les entrees les plus anciennes sont evincees.
_TAILLE_MAX_PAR_FONCTION = 256

_caches_enregistres: List[Callable[[], None]] = []


def _figer(valeur: Any) -> Hashable:
    """Transforme un argument en cle hashable (listes, dicts, sets inclus)."""
    if isinstance(valeur, dict):
        return tuple(sorted((k, _figer(v)) for k, v in valeur.items()))
    if isinstance(valeur, (list, tuple)):
        return tuple(_figer(v) for v in valeur)
    if isinstance(valeur, (set, frozenset)):
        return tuple(sorted(_figer(v) for v in valeur))
    return valeur


def cache_ttl(ttl: float, garder: Optional[Callable[[Any], bool]] = None):
    """
    Decorateur : memorise le resultat pendant `ttl` secondes par jeu d'arguments.

    `garder(resultat)` permet de ne pas memoriser certains resultats (ex : une
    erreur passagere, qu'il faut pouvoir retenter tout de suite).

    Le resultat rendu est une copie, pour qu'un appelant qui le modifie
    n'abime pas la valeur en cache. La fonction decoree expose `.clear()`.
    """
    def decorateur(fonction: Callable) -> Callable:
        entrees: dict = {}
        verrou = threading.Lock()

        @functools.wraps(fonction)
        def enveloppe(*args, **kwargs):
            cle = (_figer(args), _figer(kwargs))
            maintenant = time.monotonic()
            with verrou:
                trouve = entrees.get(cle)
                if trouve is not None and trouve[0] > maintenant:
                    return copy.deepcopy(trouve[1])
            # Calcul hors verrou : un telechargement lent ne bloque pas les autres cles
            resultat = fonction(*args, **kwargs)
            if garder is not None and not garder(resultat):
                return resultat
            with verrou:
                if len(entrees) >= _TAILLE_MAX_PAR_FONCTION:
                    for ancienne in sorted(entrees, key=lambda k: entrees[k][0])[
                            :_TAILLE_MAX_PAR_FONCTION // 4]:
                        del entrees[ancienne]
                entrees[cle] = (maintenant + ttl, resultat)
            return copy.deepcopy(resultat)

        def clear() -> None:
            with verrou:
                entrees.clear()

        enveloppe.clear = clear
        _caches_enregistres.append(clear)
        return enveloppe
    return decorateur


def vider_tous_les_caches() -> None:
    """Vide tous les caches declares avec cache_ttl."""
    for clear in _caches_enregistres:
        clear()
