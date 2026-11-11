"""
core/conjoncture.py
===================
Conjoncture economique reelle (taux directeurs, taux longs, inflation) a partir
des series publiques FRED, et taux sans risque du ratio de Sharpe.

Pourquoi : un meme choc n'a pas le meme effet selon le point de depart (une
banque centrale a 0 % ne peut plus baisser ses taux). L'IA recoit donc les
conditions du jour, et le Sharpe utilise le vrai taux sans risque plutot
qu'une constante.
"""

import io
from typing import Dict, List, Optional

import pandas as pd
import requests

from config import SERIES_FRED, TAUX_SANS_RISQUE_ANNUEL
from logger import get_logger

log = get_logger("conjoncture")

URL_FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv"
_TIMEOUT_SECONDES = 20
_MOIS_PAR_AN = 12


def telecharger_serie_fred(identifiant: str, depuis: str) -> pd.Series:
    """Serie FRED (CSV public, sans cle) indexee par date. Vide en cas d'echec."""
    try:
        reponse = requests.get(URL_FRED, params={"id": identifiant, "cosd": depuis}, timeout=_TIMEOUT_SECONDES)
        reponse.raise_for_status()
        df = pd.read_csv(io.StringIO(reponse.text), index_col=0, parse_dates=True, na_values=["."])
    except (requests.RequestException, ValueError, OSError) as e:
        log.warning("Serie FRED %s indisponible : %s", identifiant, str(e)[:100])
        return pd.Series(dtype=float)
    if df.empty:
        return pd.Series(dtype=float)
    return pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().sort_index()


def variation_sur_un_an(indice: pd.Series) -> Optional[tuple]:
    """Variation en % de la derniere valeur d'un indice mensuel par rapport a 12 mois plus tot.

    Returns:
        (variation_pct, date_derniere_valeur) ou None si l'historique est trop court.
    """
    indice = indice.dropna()
    if len(indice) <= _MOIS_PAR_AN:
        return None
    derniere, date = indice.iloc[-1], indice.index[-1]
    reference = indice[indice.index <= date - pd.DateOffset(months=_MOIS_PAR_AN)]
    if reference.empty or reference.iloc[-1] <= 0:
        return None
    return (float(derniere / reference.iloc[-1] - 1) * 100, date)


def construire_conjoncture(series: Dict[str, pd.Series]) -> Dict:
    """
    Met en forme les indicateurs (pur : aucune requete reseau).

    Args:
        series: {cle de SERIES_FRED: serie brute FRED}

    Returns:
        {"indicateurs": [{cle, nom, valeur, unite, date, source}], "date": derniere date}
        Les series vides ou trop courtes sont omises.
    """
    indicateurs: List[Dict] = []
    for cle, (identifiant, nom, nature) in SERIES_FRED.items():
        serie = series.get(cle)
        if serie is None or serie.dropna().empty:
            continue
        if nature == "indice":
            resultat = variation_sur_un_an(serie)
            if resultat is None:
                continue
            valeur, date = resultat
        else:
            serie = serie.dropna()
            valeur, date = float(serie.iloc[-1]), serie.index[-1]
        indicateurs.append({
            "cle": cle, "nom": nom, "valeur": round(valeur, 2), "unite": "%",
            "date": pd.Timestamp(date).strftime("%Y-%m-%d"), "source": f"FRED · {identifiant}",
        })
    dates = [i["date"] for i in indicateurs]
    return {"indicateurs": indicateurs, "date": max(dates) if dates else None}


def taux_sans_risque(serie_taux: Optional[pd.Series], debut=None, fin=None) -> float:
    """
    Taux sans risque annuel (decimal) pour le ratio de Sharpe.

    Sans periode : derniere valeur (simulation de l'avenir). Avec periode : moyenne
    sur la periode (backtest : le taux de l'epoque, pas celui d'aujourd'hui).
    Repli sur la constante de config si la serie ne couvre pas la periode.
    """
    if serie_taux is None or serie_taux.dropna().empty:
        return TAUX_SANS_RISQUE_ANNUEL
    serie = serie_taux.dropna()
    if debut is not None or fin is not None:
        serie = serie.loc[pd.Timestamp(debut) if debut else None:pd.Timestamp(fin) if fin else None]
        if serie.empty:
            return TAUX_SANS_RISQUE_ANNUEL
        return float(serie.mean()) / 100
    return float(serie.iloc[-1]) / 100


def texte_pour_ia(conjoncture: Dict) -> str:
    """Resume compact des indicateurs, a inserer dans le prompt de l'IA."""
    lignes = [f"- {i['nom']} : {i['valeur']:.2f} % (au {i['date']})" for i in conjoncture.get("indicateurs", [])]
    return "\n".join(lignes)
