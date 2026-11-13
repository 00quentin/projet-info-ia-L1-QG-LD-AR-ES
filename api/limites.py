"""
api/limites.py
==============
Limitation du nombre d'appels : par visiteur (fenetre glissante en memoire) et
plafond global d'appels IA par jour.

Pourquoi : l'API est publique et chaque analyse declenche un appel OpenAI
facture. Sans limite, un script pourrait vider le credit en quelques minutes ;
et meme limite par adresse, un afflux de visiteurs (ou d'adresses) le pourrait
en une journee : le plafond quotidien borne la depense totale.
"""

import os
import threading
import time
from collections import defaultdict, deque
from datetime import date, datetime, timezone
from typing import Callable, Deque, Dict, Optional

from config import API_PLAFOND_APPELS_IA_JOUR
from logger import get_logger

log = get_logger("api")

VARIABLE_PLAFOND_IA = "QT_PLAFOND_IA_JOUR"


class LimiteurAppels:
    """Autorise au plus `maximum` appels par `fenetre` secondes et par cle."""

    def __init__(self, maximum: int, fenetre: float):
        self.maximum = maximum
        self.fenetre = fenetre
        self._appels: Dict[str, Deque[float]] = defaultdict(deque)
        self._verrou = threading.Lock()

    def autoriser(self, cle: str) -> bool:
        """Enregistre un appel ; False si la cle a depasse son quota."""
        maintenant = time.monotonic()
        with self._verrou:
            file = self._appels[cle]
            while file and file[0] <= maintenant - self.fenetre:
                file.popleft()
            if len(file) >= self.maximum:
                return False
            file.append(maintenant)
            # Menage : on oublie les visiteurs inactifs pour borner la memoire
            if len(self._appels) > 10_000:
                for k in [k for k, f in self._appels.items() if not f]:
                    del self._appels[k]
            return True

    def reinitialiser(self) -> None:
        with self._verrou:
            self._appels.clear()


def _date_utc() -> date:
    return datetime.now(timezone.utc).date()


class PlafondJournalier:
    """Autorise au plus `maximum` appels par jour (UTC), tous visiteurs confondus.

    Le compteur vit en memoire : il repart a zero au changement de jour et au
    redemarrage du serveur (Render n'en fait tourner qu'un seul processus).
    """

    def __init__(self, maximum: int, aujourd_hui: Callable[[], date] = _date_utc):
        self.maximum = maximum
        self._aujourd_hui = aujourd_hui
        self._jour: Optional[date] = None
        self._compte = 0
        self._verrou = threading.Lock()

    def autoriser(self) -> bool:
        """Enregistre un appel ; False si le plafond du jour est atteint."""
        with self._verrou:
            jour = self._aujourd_hui()
            if jour != self._jour:
                self._jour, self._compte = jour, 0
            if self._compte >= self.maximum:
                return False
            self._compte += 1
            if self._compte == self.maximum:
                log.warning("Plafond quotidien d'appels IA atteint (%d)", self.maximum)
            return True

    def reinitialiser(self) -> None:
        with self._verrou:
            self._jour, self._compte = None, 0


def plafond_ia_du_jour() -> int:
    """Plafond quotidien d'appels IA : QT_PLAFOND_IA_JOUR (entier >= 0) s'il est
    renseigne, sinon la valeur de config.py."""
    brut = os.getenv(VARIABLE_PLAFOND_IA, "").strip()
    if not brut:
        return API_PLAFOND_APPELS_IA_JOUR
    try:
        valeur = int(brut)
    except ValueError:
        valeur = -1
    if valeur < 0:
        log.warning("%s=%r invalide : plafond par defaut (%d)",
                    VARIABLE_PLAFOND_IA, brut, API_PLAFOND_APPELS_IA_JOUR)
        return API_PLAFOND_APPELS_IA_JOUR
    return valeur
