"""
tests/conftest.py
=================
Configuration partagee pour tous les tests pytest.
"""

import sys
from pathlib import Path

# Ajoute la racine du projet au sys.path pour permettre les imports
# `from core.metrics import ...` depuis les tests sans installer le package.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
