"""
api/validation.py
=================
Sert les résultats de « L'IA à l'épreuve de l'histoire » (data/validation_ia.json).

Le fichier est calculé une fois par scripts/valider_ia_historique.py : une visite
du site ne déclenche aucun appel IA. Il est relu seulement quand il change sur disque.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from api.services import ServiceIndisponible
from logger import get_logger

log = get_logger("api")

FICHIER_VALIDATION = Path(__file__).resolve().parent.parent / "data" / "validation_ia.json"
# Estimations brutes gardées par le script pour ne pas rappeler l'IA : inutiles au site.
_CLES_INTERNES = ("estimation", "estimation_avec_date")

_MESSAGE_ABSENT = ("Les résultats de la validation historique ne sont pas encore disponibles "
                   "sur ce serveur.")


@lru_cache(maxsize=2)
def _lire(chemin: str, date_modification: float) -> Dict[str, Any]:
    """Lecture mise en cache par (chemin, date de modification)."""
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    for crise in donnees.get("crises", []):
        for cle in _CLES_INTERNES:
            crise.pop(cle, None)
    return donnees


def resultats_validation(chemin: Optional[Path] = None) -> Dict[str, Any]:
    """Contenu du fichier de validation, prêt à être renvoyé en JSON."""
    chemin = chemin or FICHIER_VALIDATION
    try:
        date_modification = chemin.stat().st_mtime
        return _lire(str(chemin), date_modification)
    except FileNotFoundError:
        raise ServiceIndisponible(_MESSAGE_ABSENT) from None
    except (OSError, json.JSONDecodeError) as e:
        log.error("Fichier de validation illisible : %s", e)
        raise ServiceIndisponible(_MESSAGE_ABSENT) from None
