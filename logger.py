"""
logger.py
=========
Configuration centralisée du logging pour Quant Terminal.
Permet de tracer les erreurs et événements importants sans polluer l'UI.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str = "quant_terminal") -> logging.Logger:
    """
    Retourne un logger configuré.

    En production (Streamlit Cloud), les logs vont sur stdout (visibles dans
    "Manage app" > "Logs"). En local, ils s'affichent dans le terminal.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Déjà configuré

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger