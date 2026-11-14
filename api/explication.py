"""
api/explication.py
==================
« Pourquoi ces mouvements ? » : une phrase par actif (logique : ia_explication.py).
"""

from typing import Dict

from pydantic import BaseModel, Field, field_validator

import ia_explication
from api.services import ServiceIndisponible, _verifier_ia_configuree
from config import (
    API_ACTIFS_MAX, API_SCENARIO_LONGUEUR_MAX, EXPLICATION_CHOC_MAX_PCT, EXPLICATION_CHOC_MIN_PCT,
    IA_ANALYSE_SECOURS,
)


class DemandeExplication(BaseModel):
    scenario: str = Field(min_length=1, max_length=API_SCENARIO_LONGUEUR_MAX)
    # Variation estimée par actif, en % (ex : -12.3).
    chocs: Dict[str, float] = Field(min_length=1, max_length=API_ACTIFS_MAX)

    @field_validator("chocs")
    @classmethod
    def _chocs_bornes(cls, v: Dict[str, float]) -> Dict[str, float]:
        for cle, choc in v.items():
            if not EXPLICATION_CHOC_MIN_PCT <= choc <= EXPLICATION_CHOC_MAX_PCT:
                raise ValueError(f"Variation hors bornes pour {cle}")
        return v


def expliquer(demande: DemandeExplication) -> dict:
    _verifier_ia_configuree()
    erreurs: list = []
    explications = ia_explication.expliquer_actifs(demande.scenario, demande.chocs, erreurs)
    if not explications:
        raise ServiceIndisponible("Aucun actif reconnu à expliquer.")
    if erreurs:
        raise ServiceIndisponible("L'explication par IA est momentanément indisponible. Réessayez dans un instant.")
    return {"explications": explications, "modele": IA_ANALYSE_SECOURS["model"]}
