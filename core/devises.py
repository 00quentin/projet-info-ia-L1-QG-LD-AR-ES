"""
core/devises.py
===============
Conversion des prix en euros avec les taux de reference officiels de la BCE.

Pourquoi : le portefeuille est en euros mais la plupart des actifs cotent en
dollars. Sans conversion, la performance affichee ignore l'effet de change
(ex : S&P 500 +10% en dollars avec un dollar qui perd 10% = ~0% en euros).
"""

import io
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests

from config import DEVISE_REFERENCE
from logger import get_logger

log = get_logger("devises")

URL_TAUX_BCE = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
_TIMEOUT_SECONDES = 20


def telecharger_taux_bce() -> pd.DataFrame:
    """
    Telecharge l'historique quotidien des taux de reference BCE (depuis 1999).

    Returns:
        DataFrame indexe par date croissante, une colonne par devise, exprimee
        en unites de devise pour 1 euro (ex : USD = 1.12). Vide en cas d'echec.
    """
    try:
        reponse = requests.get(URL_TAUX_BCE, timeout=_TIMEOUT_SECONDES)
        reponse.raise_for_status()
        taux = pd.read_csv(
            io.BytesIO(reponse.content), compression="zip",
            index_col=0, parse_dates=True, na_values=["N/A"],
        )
    except (requests.RequestException, ValueError, OSError) as e:
        log.warning("Taux BCE indisponibles : %s", str(e)[:100])
        return pd.DataFrame()
    taux = taux.dropna(axis=1, how="all").sort_index()
    return taux.apply(pd.to_numeric, errors="coerce")


def convertir_en_eur(
    prix: pd.DataFrame,
    devises: Dict[str, Optional[str]],
    taux: pd.DataFrame,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Convertit en euros les colonnes de `prix` cotees dans une autre devise.

    Args:
        prix: prix par actif, indexes par date.
        devises: {colonne: code devise}. None ou EUR = pas de conversion.
        taux: taux BCE (voir telecharger_taux_bce).

    Returns:
        (prix convertis, colonnes non converties faute de taux sur la periode).
    """
    converti = prix.copy()
    non_convertis: List[str] = []
    if prix.empty:
        return converti, non_convertis

    index_dates = pd.DatetimeIndex(prix.index).tz_localize(None).normalize()
    for colonne in prix.columns:
        devise = devises.get(colonne)
        if devise is None or devise == DEVISE_REFERENCE:
            continue
        if taux.empty or devise not in taux.columns:
            non_convertis.append(colonne)
            continue
        # Dernier taux connu a chaque date de cotation (week-ends, jours feries BCE)
        serie = taux[devise].dropna()
        aligne = serie.reindex(serie.index.union(index_dates)).ffill().reindex(index_dates)
        if aligne.isna().any():
            non_convertis.append(colonne)
            continue
        converti[colonne] = prix[colonne].values / aligne.values
    return converti, non_convertis


def rendements_taux_change(
    taux: pd.DataFrame,
    colonnes: Dict[str, str],
    index: pd.Index,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Rendements quotidiens des taux BCE, alignes sur les seances d'un historique.

    Sert a la simulation : la livre et le yen y sont des taux techniques dont
    l'agitation et les correlations sont mesurees sur ces vrais taux.

    Args:
        taux: taux BCE (voir telecharger_taux_bce).
        colonnes: {code devise: nom de colonne voulu}, ex. {"GBP": "EUR_GBP"}.
        index: dates des seances de l'historique a completer.

    Returns:
        (rendements indexes comme `index`, dernier taux connu par colonne).
        Vides si les taux manquent.
    """
    rendements = pd.DataFrame(index=index)
    derniers: Dict[str, float] = {}
    if taux.empty or len(index) == 0 or not isinstance(index, pd.DatetimeIndex):
        return rendements, derniers
    dates = pd.DatetimeIndex(index).tz_localize(None).normalize()
    for devise, colonne in colonnes.items():
        if devise not in taux.columns:
            continue
        serie = taux[devise].dropna()
        if serie.empty:
            continue
        derniers[colonne] = float(serie.iloc[-1])
        variations = serie.pct_change().reindex(dates)
        rendements[colonne] = variations.values
    return rendements, derniers
