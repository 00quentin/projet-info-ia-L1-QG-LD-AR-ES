"""
core/custom_assets.py
=====================
Validation et calibration d'un actif personnalise via Yahoo Finance.

L'utilisateur fournit un ticker (ex: "TSLA", "MSFT", "BTC-USD"). On
recupere le dernier prix et on calibre la volatilite quotidienne sur
~1 an d'historique. Si Yahoo ne renvoie rien, on remonte une erreur
explicite.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

import yfinance as yf

from logger import get_logger

log = get_logger("custom_assets")


# Cle de session_state ou sont stockes les actifs personnalises ajoutes
# par l'utilisateur. Format: { sim_key: {"ticker", "nom", "prix", "volatilite"} }
SESSION_KEY = "actifs_perso"

# Prefixe pour distinguer une cle d'actif personnalise du catalogue standard.
# Permet d'eviter les collisions avec les sim_key existants (ex: "S&P 500").
PREFIXE_CUSTOM = "PERSO_"


def normaliser_ticker(ticker: str) -> str:
    """Nettoie et met en majuscules un ticker saisi par l'utilisateur."""
    return ticker.strip().upper()


def cle_simulation(ticker: str) -> str:
    """Construit la cle interne (sim_key) a partir d'un ticker."""
    return f"{PREFIXE_CUSTOM}{normaliser_ticker(ticker)}"


def valider_et_calibrer(ticker: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Verifie qu'un ticker existe sur Yahoo Finance et calibre prix + vol.

    Returns:
        (info, None) en cas de succes, avec info = {
            "ticker": str (normalise),
            "nom":    str (longName Yahoo, ou ticker en fallback),
            "prix":   float (dernier close),
            "volatilite": float (ecart-type des rendements quotidiens),
        }
        (None, message) en cas d'echec.
    """
    ticker = normaliser_ticker(ticker)
    if not ticker:
        return None, "Ticker vide."
    if len(ticker) > 20:
        return None, "Ticker trop long (max 20 caracteres)."

    log.info("Calibration ticker custom: %s", ticker)

    try:
        yf_ticker = yf.Ticker(ticker)

        fin = datetime.now()
        debut = fin - timedelta(days=400)
        hist = yf_ticker.history(start=debut, end=fin, interval="1d", timeout=8)

        if hist.empty or len(hist) < 30:
            return None, f"Ticker '{ticker}' inconnu ou historique trop court."

        prix = float(hist["Close"].iloc[-1])
        if prix <= 0:
            return None, f"Prix invalide pour '{ticker}'."

        rendements = hist["Close"].pct_change().dropna()
        vol = float(rendements.std())
        if vol <= 0 or vol > 0.5:
            # Vol > 50%/jour est un signal d'erreur (donnees corrompues)
            return None, f"Volatilite anormale pour '{ticker}' (vol={vol:.2%})."

        # longName parfois absent -> fallback ticker
        nom = ticker
        try:
            info_yf = yf_ticker.info or {}
            nom = info_yf.get("longName") or info_yf.get("shortName") or ticker
        except Exception:
            pass

        return {
            "ticker":     ticker,
            "nom":        nom,
            "prix":       prix,
            "volatilite": vol,
        }, None

    except Exception as e:
        log.warning("Echec calibration %s: %s", ticker, str(e)[:80])
        return None, f"Yahoo Finance n'a pas pu calibrer '{ticker}'."


def vers_actifs_extras(actifs_perso: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
    """
    Convertit le dict de session vers le format attendu par simulation.py
    (cle = sim_key, valeur = {"prix", "volatilite"}).
    """
    return {
        sim_key: {"prix": v["prix"], "volatilite": v["volatilite"]}
        for sim_key, v in actifs_perso.items()
    }
