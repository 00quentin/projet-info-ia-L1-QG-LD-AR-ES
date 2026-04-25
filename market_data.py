"""
market_data.py
==============
Connexion aux données réelles via Yahoo Finance.
"""

import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta


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
    if actifs_keys is None:
        actifs_keys = list(TICKERS_YAHOO.keys())

    prix = {}
    erreurs = []

    for sim_key in actifs_keys:
        ticker = TICKERS_YAHOO.get(sim_key)
        if ticker is None:
            prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
            continue
        try:
            data = yf.Ticker(ticker).history(period="5d", interval="1d")
            if not data.empty:
                prix[sim_key] = float(data["Close"].iloc[-1])
            else:
                prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
                erreurs.append(sim_key)
        except Exception:
            prix[sim_key] = PRIX_FALLBACK.get(sim_key, 100)
            erreurs.append(sim_key)

    return prix, erreurs


@st.cache_data(ttl=21600, show_spinner=False)
def get_historique(actifs_keys, date_debut, date_fin):
    df_global = pd.DataFrame()
    for sim_key in actifs_keys:
        ticker = TICKERS_YAHOO.get(sim_key)
        if ticker is None:
            continue
        try:
            data = yf.Ticker(ticker).history(start=date_debut, end=date_fin, interval="1d")
            if not data.empty:
                df_global[sim_key] = data["Close"]
        except Exception:
            continue

    if df_global.empty:
        return df_global

    df_global = df_global.ffill().dropna(how="all")
    df_global = df_global.reset_index(drop=True)
    return df_global


@st.cache_data(ttl=86400, show_spinner=False)
def get_volatilites_historiques(actifs_keys, jours=252):
    fin = datetime.now()
    debut = fin - timedelta(days=jours * 2)

    vols = {}
    for sim_key in actifs_keys:
        ticker = TICKERS_YAHOO.get(sim_key)
        if ticker is None:
            continue
        try:
            data = yf.Ticker(ticker).history(start=debut, end=fin, interval="1d")
            if not data.empty and len(data) > 30:
                rendements = data["Close"].pct_change().dropna()
                vols[sim_key] = float(rendements.std())
        except Exception:
            continue
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
