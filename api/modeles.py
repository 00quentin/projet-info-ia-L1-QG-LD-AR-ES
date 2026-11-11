"""
api/modeles.py
==============
Contrats d'entree de l'API (validation Pydantic des demandes du site web).
"""

from datetime import date
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from config import (
    API_ACTIFS_MAX, API_BACKTEST_JOURS_MAX, API_CHAT_LONGUEUR_MAX,
    API_CHAT_MESSAGES_MAX, API_SCENARIO_LONGUEUR_MAX, API_TICKERS_PERSO_MAX,
    CAPITAL_DEFAUT, CAPITAL_MAX, CAPITAL_MIN,
    HORIZON_DEFAUT, HORIZON_MAX, HORIZON_MIN,
    MODELES_SIMULATION, NB_SCENARIOS_MAX, PROFILS, PROFIL_PERSONNALISE,
)

PROFILS_ACCEPTES = list(PROFILS) + [PROFIL_PERSONNALISE]


class DemandePortefeuille(BaseModel):
    """Partie commune : quels actifs, quelle repartition, quel capital."""
    actifs: List[str] = Field(min_length=1, max_length=API_ACTIFS_MAX)
    profil: str
    allocations: Dict[str, float] = Field(default_factory=dict)
    capital: float = Field(default=CAPITAL_DEFAUT, ge=CAPITAL_MIN, le=CAPITAL_MAX)
    tickers_perso: List[str] = Field(default_factory=list, max_length=API_TICKERS_PERSO_MAX)
    convertir_eur: bool = True

    @field_validator("profil")
    @classmethod
    def _profil_connu(cls, v: str) -> str:
        if v not in PROFILS_ACCEPTES:
            raise ValueError(f"Profil inconnu. Choix possibles : {', '.join(PROFILS_ACCEPTES)}")
        return v

    @field_validator("allocations")
    @classmethod
    def _allocations_positives(cls, v: Dict[str, float]) -> Dict[str, float]:
        if any(p < 0 for p in v.values()):
            raise ValueError("Une allocation ne peut pas être négative.")
        return v


class DemandeSimulation(DemandePortefeuille):
    scenarios: List[str] = Field(min_length=1, max_length=NB_SCENARIOS_MAX)
    duree: int = Field(default=HORIZON_DEFAUT, ge=HORIZON_MIN, le=HORIZON_MAX)
    modele: str = MODELES_SIMULATION[0]
    monte_carlo: bool = False
    prix_reels: bool = True
    calibration: bool = True

    @field_validator("scenarios")
    @classmethod
    def _scenarios_bornes(cls, v: List[str]) -> List[str]:
        if any(len(s) > API_SCENARIO_LONGUEUR_MAX for s in v):
            raise ValueError(f"Un scénario ne peut pas dépasser {API_SCENARIO_LONGUEUR_MAX} caractères.")
        return v

    @field_validator("modele")
    @classmethod
    def _modele_connu(cls, v: str) -> str:
        if v not in MODELES_SIMULATION:
            raise ValueError(f"Modèle inconnu. Choix possibles : {', '.join(MODELES_SIMULATION)}")
        return v


class DemandeBacktest(DemandePortefeuille):
    evenement: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None

    @model_validator(mode="after")
    def _periode_coherente(self):
        if self.evenement is None and (self.date_debut is None or self.date_fin is None):
            raise ValueError("Indiquez un événement ou une période (date_debut et date_fin).")
        if self.date_debut and self.date_fin:
            if self.date_fin <= self.date_debut:
                raise ValueError("La date de fin doit être après la date de début.")
            if (self.date_fin - self.date_debut).days > API_BACKTEST_JOURS_MAX:
                raise ValueError("La période d'un backtest est limitée à 10 ans.")
        return self


class MessageChat(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=API_CHAT_LONGUEUR_MAX)


class DemandeChat(BaseModel):
    messages: List[MessageChat] = Field(min_length=1, max_length=API_CHAT_MESSAGES_MAX)


class LignePerformance(BaseModel):
    nom: str = Field(max_length=120)
    performance: float


class LigneAllocation(BaseModel):
    nom: str = Field(max_length=120)
    poids: float
    investi: float
    final: float
    rendement: float


class DemandeRapport(BaseModel):
    """Donnees d'un resultat deja affiche, a mettre en page en PDF."""
    type_rapport: Literal["Simulation", "Backtest"] = "Simulation"
    scenario: str = Field(max_length=API_SCENARIO_LONGUEUR_MAX)
    profil: str = Field(max_length=80)
    capital: float = Field(ge=CAPITAL_MIN, le=CAPITAL_MAX)
    valeur_finale: float = Field(ge=0)
    duree: int = Field(ge=1, le=5000)
    monte_carlo: bool = False
    prix_reels: bool = True
    calibration: bool = False
    nb_actifs: int = Field(ge=1, le=API_ACTIFS_MAX)
    inflation: float = 0.0
    taux_directeurs: float = 0.0
    explication: str = Field(default="", max_length=6000)
    evenement_reference: Optional[str] = Field(default=None, max_length=200)
    performances: List[LignePerformance] = Field(min_length=1, max_length=API_ACTIFS_MAX)
    allocations: List[LigneAllocation] = Field(min_length=1, max_length=API_ACTIFS_MAX)
    vol_ann: float
    sharpe: float
    max_dd: float
    var_95: float
    avec_analyse_ia: bool = True
