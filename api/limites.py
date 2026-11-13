"""
api/limites.py
==============
Limitation du nombre d'appels par visiteur (fenetre glissante en memoire).

Pourquoi : l'API est publique et chaque analyse declenche un appel OpenAI
facture. Sans limite, un script pourrait vider le credit en quelques minutes.
"""

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict


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
