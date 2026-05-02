"""
core/history_store.py
=====================
Persistance JSON de l'historique des simulations entre les sessions.

Pourquoi : avant, l'historique vivait uniquement dans st.session_state.
Fermer l'onglet du navigateur (ou un simple rerun cold) effacait tout
le travail de l'utilisateur. Maintenant, chaque entree est sauvegardee
sur disque dans le repertoire utilisateur (~/.quant_terminal/historique.json).

Robustesse :
- Si le fichier n'existe pas, retourne [] (premiere utilisation).
- Si le fichier est corrompu (JSON invalide, permission denied), log un
  warning et repart d'une liste vide -- on ne casse jamais l'app pour
  un probleme de cache disque.
- Le repertoire parent est cree automatiquement.

Pour les deploiements ephemeres (Streamlit Cloud), le fichier est ecrase
a chaque cold start -- le comportement est alors equivalent a l'ancien
session_state, donc aucune regression.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from logger import get_logger

log = get_logger("history_store")


def _chemin_fichier_historique(repertoire: Optional[Path] = None) -> Path:
    """Resout le chemin du fichier historique (par defaut : ~/.quant_terminal/)."""
    base = repertoire if repertoire is not None else Path.home() / ".quant_terminal"
    return base / "historique.json"


def charger_historique(repertoire: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Charge l'historique depuis le fichier JSON. Retourne [] si absent ou corrompu.

    Args:
        repertoire: dossier ou chercher le fichier (defaut : ~/.quant_terminal/).
                    Override utile pour les tests.

    Returns:
        Liste des entrees historiques (eventuellement vide).
    """
    fichier = _chemin_fichier_historique(repertoire)
    if not fichier.exists():
        return []

    try:
        with fichier.open("r", encoding="utf-8") as f:
            donnees = json.load(f)
        if not isinstance(donnees, list):
            log.warning("Fichier historique non-conforme (pas une liste), ignore : %s", fichier)
            return []
        return donnees
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Impossible de lire l'historique (%s) : %s", fichier, e)
        return []


def sauvegarder_historique(
    historique: List[Dict[str, Any]],
    repertoire: Optional[Path] = None,
) -> bool:
    """
    Ecrit l'historique sur disque. Retourne True si ok, False sinon.

    Args:
        historique: liste des entrees a persister.
        repertoire: dossier cible (defaut : ~/.quant_terminal/).

    Returns:
        True en cas de succes, False si l'ecriture a echoue (permission,
        disque plein...). On ne leve jamais d'exception : une perte de
        persistance ne doit pas crasher l'app.
    """
    fichier = _chemin_fichier_historique(repertoire)
    try:
        fichier.parent.mkdir(parents=True, exist_ok=True)
        with fichier.open("w", encoding="utf-8") as f:
            json.dump(historique, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        log.warning("Impossible d'ecrire l'historique (%s) : %s", fichier, e)
        return False


def ajouter_entree(
    historique: List[Dict[str, Any]],
    entree: Dict[str, Any],
    taille_max: int,
    repertoire: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Ajoute une entree en tete, tronque a taille_max, persiste sur disque.

    Args:
        historique: liste actuelle (sera modifiee).
        entree: nouvelle entree a inserer en position 0 (plus recente).
        taille_max: longueur maximale conservee.
        repertoire: dossier cible pour la persistance.

    Returns:
        Nouvelle liste tronquee (le caller doit la reassigner).
    """
    nouveau = [entree] + historique
    nouveau = nouveau[:taille_max]
    sauvegarder_historique(nouveau, repertoire)
    return nouveau


def effacer_historique(repertoire: Optional[Path] = None) -> bool:
    """
    Supprime le fichier historique du disque. Retourne True si ok ou si
    le fichier n'existait deja pas.
    """
    fichier = _chemin_fichier_historique(repertoire)
    try:
        fichier.unlink(missing_ok=True)
        return True
    except OSError as e:
        log.warning("Impossible de supprimer l'historique (%s) : %s", fichier, e)
        return False
