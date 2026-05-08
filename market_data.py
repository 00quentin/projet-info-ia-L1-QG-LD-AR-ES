"""
market_data.py
==============
Connexion aux données réelles via Yahoo Finance.
"""

import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

from logger import get_logger

log = get_logger("market_data")


TICKERS_YAHOO = {
    "S&P 500":              "^GSPC",
    "NASDAQ":               "^NDX",
    "CAC 40":               "^FCHI",
    "MSCI_World":           "URTH",
    "Emerging_Markets":     "EEM",
    "Bons_Tresor_US_10Y":   "IEF",
    "Bund_10Y":             "IBGM.DE",
    "OAT_10Y":              "OAT.PA",
    "JGB_10Y":              "1482.T",
    "Gilt_10Y":             "IGLT.L",
    "EUR_USD":              "EURUSD=X",
    "Dollar_Index":         "DX-Y.NYB",
    "VIX":                  "^VIX",
    "Or":                   "GC=F",
    "Argent":               "SI=F",
    "Petrole":              "CL=F",
    "Cuivre":               "HG=F",
    "ETF_Terres_Rares":     "REMX",
    "ETF_Defense":          "ITA",
    "Bitcoin":              "BTC-USD",
    "Ethereum":             "ETH-USD",
    "XRP":                  "XRP-USD",
    "Solana":               "SOL-USD",
}


PRIX_FALLBACK = {
    "S&P 500": 5200, "NASDAQ": 18200, "CAC 40": 8100, "MSCI_World": 3500, "Emerging_Markets": 1100,
    "Bons_Tresor_US_10Y": 100, "Bund_10Y": 100, "OAT_10Y": 100, "JGB_10Y": 100, "Gilt_10Y": 100,
    "EUR_USD": 1.08, "Dollar_Index": 104, "VIX": 18,
    "Or": 2350, "Argent": 28, "Petrole": 85, "Cuivre": 4.5, "ETF_Terres_Rares": 55,
    "ETF_Defense": 42,
    "Bitcoin": 65000, "Ethereum": 3300, "XRP": 0.55, "Solana": 160,
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_prix_actuels(actifs_keys=None):
    """Recupere le dernier prix de cloture pour chaque actif demande.

    Optimisation : un seul appel yf.download(...) batch (parallelise par
    yfinance en interne) plutot qu'une boucle sequentielle ticker par ticker.
    """
    if actifs_keys is None:
        actifs_keys = list(TICKERS_YAHOO.keys())

    log.info("Récupération prix Yahoo pour %d actifs (batch)", len(actifs_keys))
    prix = {}
    erreurs = []

    # Mapping ticker -> sim_key, pour reconstruire le dict apres le batch
    ticker_to_sim = {}
    tickers_a_charger = []
    for sim_key in actifs_keys:
        ticker = TICKERS_YAHOO.get(sim_key)
        if ticker is None:
            prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
        else:
            ticker_to_sim[ticker] = sim_key
            tickers_a_charger.append(ticker)

    if not tickers_a_charger:
        return prix, erreurs

    try:
        data = yf.download(
            tickers=tickers_a_charger,
            period="5d",
            interval="1d",
            progress=False,
            group_by="ticker",
            threads=True,
            auto_adjust=True,
        )
    except Exception as e:  # noqa: BLE001 — yfinance leve plusieurs types
        log.warning("Batch yf.download a echoue (%s) : fallback prix par defaut", str(e)[:80])
        for sim_key in [ticker_to_sim[t] for t in tickers_a_charger]:
            prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
            erreurs.append(sim_key)
        return prix, erreurs

    # Format de sortie yf.download :
    # - 1 ticker : DataFrame plat avec colonnes (Open, High, ...)
    # - N tickers : MultiIndex de colonnes (ticker, OHLC)
    multi = len(tickers_a_charger) > 1
    for ticker in tickers_a_charger:
        sim_key = ticker_to_sim[ticker]
        try:
            if multi:
                serie = data[ticker]["Close"].dropna() if ticker in data.columns.get_level_values(0) else None
            else:
                serie = data["Close"].dropna()
            if serie is not None and not serie.empty:
                prix[sim_key] = float(serie.iloc[-1])
            else:
                prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
                erreurs.append(sim_key)
        except (KeyError, IndexError, ValueError) as e:
            log.warning("Yahoo parse failed for %s (%s): %s", sim_key, ticker, str(e)[:60])
            prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
            erreurs.append(sim_key)

    if erreurs:
        log.warning("Indispos Yahoo: %s", erreurs)
    return prix, erreurs


def _telecharger_closes(tickers: list, **kwargs) -> pd.DataFrame:
    """Helper : un seul yf.download() batch et reconstruit un DataFrame de
    series Close indexees par ticker. Renvoie un DF vide en cas d'echec.
    """
    if not tickers:
        return pd.DataFrame()
    try:
        data = yf.download(
            tickers=tickers,
            progress=False,
            group_by="ticker",
            threads=True,
            auto_adjust=True,
            **kwargs,
        )
    except Exception as e:  # noqa: BLE001
        log.warning("yf.download batch failed: %s", str(e)[:80])
        return pd.DataFrame()

    out = pd.DataFrame()
    if len(tickers) == 1:
        if "Close" in data.columns:
            out[tickers[0]] = data["Close"]
        return out
    for ticker in tickers:
        if ticker in data.columns.get_level_values(0):
            try:
                out[ticker] = data[ticker]["Close"]
            except KeyError:
                continue
    return out


@st.cache_data(ttl=21600, show_spinner=False)
def get_historique(actifs_keys, date_debut, date_fin):
    log.info("Backtest Yahoo (batch): %d actifs, %s → %s",
             len(actifs_keys), date_debut, date_fin)
    sim_to_ticker = {sk: TICKERS_YAHOO[sk] for sk in actifs_keys if sk in TICKERS_YAHOO}
    if not sim_to_ticker:
        return pd.DataFrame()

    df_tickers = _telecharger_closes(
        list(sim_to_ticker.values()),
        start=date_debut,
        end=date_fin,
        interval="1d",
    )
    if df_tickers.empty:
        log.error("Aucune donnée historique récupérée")
        return pd.DataFrame()

    # Renomme : ticker -> sim_key
    rename = {tk: sk for sk, tk in sim_to_ticker.items() if tk in df_tickers.columns}
    df_global = df_tickers.rename(columns=rename)
    df_global = df_global[[c for c in df_global.columns if c in sim_to_ticker]]

    # ffill : trous de cotation au milieu de la periode (jours feries / suspension)
    # bfill : trous au DEBUT (asset cote depuis moins longtemps que la fenetre demandee)
    df_global = df_global.ffill().bfill().dropna(how="all")
    df_global = df_global.reset_index(drop=True)
    return df_global


@st.cache_data(ttl=86400, show_spinner=False)
def get_volatilites_historiques(actifs_keys, jours=252):
    fin = datetime.now()
    debut = fin - timedelta(days=jours * 2)

    sim_to_ticker = {sk: TICKERS_YAHOO[sk] for sk in actifs_keys if sk in TICKERS_YAHOO}
    if not sim_to_ticker:
        return {}

    df_tickers = _telecharger_closes(
        list(sim_to_ticker.values()),
        start=debut.strftime("%Y-%m-%d"),
        end=fin.strftime("%Y-%m-%d"),
        interval="1d",
    )
    if df_tickers.empty:
        return {}

    vols = {}
    for sim_key, ticker in sim_to_ticker.items():
        if ticker not in df_tickers.columns:
            continue
        serie = df_tickers[ticker].dropna()
        if len(serie) > 30:
            rendements = serie.pct_change().dropna()
            vols[sim_key] = float(rendements.std())
    return vols


EVENEMENTS_HISTORIQUES = {
    "COVID-19 (mars 2020)": {
        "debut": "2020-02-15", "fin": "2020-04-15",
        "description": "Pandémie mondiale, krach éclair de -34% sur le S&P 500 en 23 jours."
    },
    "Krach 2008 (Lehman)": {
        "debut": "2008-09-01", "fin": "2009-03-09",
        "description": "Crise des subprimes, faillite de Lehman, S&P 500 -57% sur 17 mois."
    },
    "Bulle internet (2000-2002)": {
        "debut": "2000-03-10", "fin": "2002-10-09",
        "description": "Éclatement de la bulle dot-com, Nasdaq -78%."
    },
    "Krach pétrolier (2014-2016)": {
        "debut": "2014-06-01", "fin": "2016-02-11",
        "description": "Pétrole de 110$ à 26$ en 18 mois, choc sur les pays producteurs."
    },
    "Guerre Russie-Ukraine (2022)": {
        "debut": "2022-02-24", "fin": "2022-12-31",
        "description": "Invasion russe, choc énergétique en Europe, hausse brutale des taux FED."
    },
    "Brexit (2016)": {
        "debut": "2016-06-23", "fin": "2016-12-31",
        "description": "Référendum UK, livre sterling -10% en une nuit."
    },
}