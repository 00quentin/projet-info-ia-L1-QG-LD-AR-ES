"""
tests/test_market_data.py
=========================
Tests de market_data.py avec yfinance MOCKE.

On verifie que :
- get_prix_actuels reconstruit bien le dict {sim_key: prix} a partir d'un DataFrame batch yfinance
- Les actifs absents du download tombent sur PRIX_FALLBACK et sont listes dans erreurs
- Une exception yfinance fait fallback complet (pas de plantage UI)
- get_historique renomme bien ticker -> sim_key et nettoie les NaN
- get_volatilites_historiques calcule un std non nul sur des donnees realistes
"""

from unittest.mock import patch
import pandas as pd
import numpy as np
import pytest

import market_data


# Fixture : on vide le cache Streamlit avant chaque test pour eviter
# que le 1er test pollue les suivants.
@pytest.fixture(autouse=True)
def _clear_streamlit_cache(tmp_path, monkeypatch):
    market_data.get_prix_actuels.clear()
    market_data.get_prix_avec_variation.clear()
    market_data.get_historique.clear()
    market_data.get_rendements_historiques.clear()
    market_data.get_volatilites_historiques.clear()
    market_data.get_taux_bce.clear()
    # Snapshot disque isole : les tests ne doivent ni lire ni ecrire le vrai fichier
    monkeypatch.setattr(market_data, "_SNAPSHOT_PATH", tmp_path / "snapshot.json")
    monkeypatch.setattr(market_data, "_SNAPSHOT_PRIX", {})
    monkeypatch.setattr(market_data, "_SNAPSHOT_META", {"date": None})


def _build_multi_df(tickers_data: dict) -> pd.DataFrame:
    """Construit un DataFrame au format yf.download(group_by='ticker', plusieurs tickers).

    tickers_data: {ticker: liste_de_closes}
    """
    dfs = {}
    for ticker, closes in tickers_data.items():
        idx = pd.date_range("2024-01-01", periods=len(closes))
        dfs[ticker] = pd.DataFrame({
            "Open": closes, "High": closes, "Low": closes,
            "Close": closes, "Volume": [1000] * len(closes),
        }, index=idx)
    return pd.concat(dfs, axis=1)


# === get_prix_actuels =====================================================


def test_get_prix_actuels_renvoie_dernier_close_par_actif():
    fake = _build_multi_df({
        "^GSPC": [5000, 5100, 5200],   # S&P 500
        "GC=F":  [2300, 2340, 2350],   # Or
        "BTC-USD": [60000, 62000, 65000],
    })
    with patch.object(market_data.yf, "download", return_value=fake):
        prix, erreurs = market_data.get_prix_actuels(["S&P 500", "Or", "Bitcoin"])

    assert prix["S&P 500"] == 5200
    assert prix["Or"] == 2350
    assert prix["Bitcoin"] == 65000
    assert erreurs == []


def test_get_prix_actuels_actif_inconnu_utilise_fallback():
    """Une cle absente de TICKERS_YAHOO doit retomber sur PRIX_FALLBACK."""
    fake = _build_multi_df({"^GSPC": [5200]})
    with patch.object(market_data.yf, "download", return_value=fake):
        prix, erreurs = market_data.get_prix_actuels(["S&P 500", "TICKER_INEXISTANT"])

    assert prix["S&P 500"] == 5200
    # TICKER_INEXISTANT n'est pas dans TICKERS_YAHOO -> fallback default 100
    assert prix["TICKER_INEXISTANT"] == 100


def test_get_prix_actuels_yfinance_exception_fallback_complet():
    """Si yf.download leve, on retourne PRIX_FALLBACK pour tous les actifs."""
    with patch.object(market_data.yf, "download", side_effect=ConnectionError("no net")):
        prix, erreurs = market_data.get_prix_actuels(["S&P 500", "Or"])

    # Doit avoir les 2 actifs avec leur valeur fallback
    assert prix["S&P 500"] == market_data.PRIX_FALLBACK["S&P 500"]
    assert prix["Or"] == market_data.PRIX_FALLBACK["Or"]
    # Et les 2 doivent etre dans erreurs
    assert set(erreurs) == {"S&P 500", "Or"}


def test_get_prix_actuels_dataframe_vide_pour_un_actif():
    """Un ticker present mais sans data -> fallback + erreur."""
    fake = _build_multi_df({
        "^GSPC": [5200],
        # GC=F absent du DataFrame -> simule data manquante
    })
    with patch.object(market_data.yf, "download", return_value=fake):
        prix, erreurs = market_data.get_prix_actuels(["S&P 500", "Or"])

    assert prix["S&P 500"] == 5200
    assert prix["Or"] == market_data.PRIX_FALLBACK["Or"]
    assert "Or" in erreurs


def test_get_prix_actuels_sans_argument_charge_tous_les_actifs():
    """Appel sans argument -> tous les actifs du catalogue."""
    fake = _build_multi_df({tk: [100.0] for tk in market_data.TICKERS_YAHOO.values()})
    with patch.object(market_data.yf, "download", return_value=fake):
        prix, _ = market_data.get_prix_actuels()

    # Tous les actifs du catalogue doivent etre dans le dict
    assert set(prix.keys()) == set(market_data.TICKERS_YAHOO.keys())


# === get_historique =======================================================


def test_get_historique_renomme_tickers_en_sim_keys():
    fake = _build_multi_df({
        "^GSPC": [5000, 5100, 5200, 5150],
        "GC=F":  [2300, 2340, 2350, 2360],
    })
    with patch.object(market_data.yf, "download", return_value=fake):
        df = market_data.get_historique(["S&P 500", "Or"], "2024-01-01", "2024-01-04")

    assert "S&P 500" in df.columns
    assert "Or" in df.columns
    # Pas le ticker brut
    assert "^GSPC" not in df.columns


def test_get_historique_dataframe_vide_si_yfinance_echoue():
    with patch.object(market_data.yf, "download", side_effect=Exception("api down")):
        df = market_data.get_historique(["S&P 500"], "2024-01-01", "2024-01-04")
    assert df.empty


def test_get_historique_remplit_les_nan_intermediaires():
    closes_avec_nan = [5000.0, np.nan, 5200.0, 5150.0]
    fake = _build_multi_df({"^GSPC": closes_avec_nan, "GC=F": [2300, 2340, 2350, 2360]})
    with patch.object(market_data.yf, "download", return_value=fake):
        df = market_data.get_historique(["S&P 500", "Or"], "2024-01-01", "2024-01-04")

    # Apres ffill/bfill, plus aucun NaN
    assert not df.isna().any().any()


# === get_volatilites_historiques ==========================================


def test_get_volatilites_historiques_calcule_un_std_realiste():
    # 60 jours de cotation aleatoires sur 2 actifs -> format multi (group_by='ticker')
    np.random.seed(42)
    closes_sp = list(100 + np.cumsum(np.random.randn(60)))
    closes_or = list(2000 + np.cumsum(np.random.randn(60)))
    fake = _build_multi_df({"^GSPC": closes_sp, "GC=F": closes_or})
    with patch.object(market_data.yf, "download", return_value=fake):
        vols = market_data.get_volatilites_historiques(["S&P 500", "Or"])

    assert "S&P 500" in vols
    assert vols["S&P 500"] > 0
    # Une vol journaliere realiste reste sous 10% pour un indice
    assert vols["S&P 500"] < 0.1


def test_get_volatilites_historiques_ignore_les_series_trop_courtes():
    """< 30 jours -> exclu."""
    fake = _build_multi_df({"^GSPC": [100, 101, 102], "GC=F": [2000, 2010, 2020]})
    with patch.object(market_data.yf, "download", return_value=fake):
        vols = market_data.get_volatilites_historiques(["S&P 500", "Or"])
    assert "S&P 500" not in vols
    assert "Or" not in vols


def test_get_volatilites_historiques_dict_vide_si_pas_de_data():
    with patch.object(market_data.yf, "download", side_effect=Exception):
        vols = market_data.get_volatilites_historiques(["S&P 500"])
    assert vols == {}


# === Sanity checks sur le catalogue ======================================


def test_tous_les_actifs_du_catalogue_ont_un_fallback():
    """Garde-fou : un actif sans fallback peut planter en mode offline."""
    for sim_key in market_data.TICKERS_YAHOO:
        assert sim_key in market_data.PRIX_FALLBACK, \
            f"{sim_key} dans TICKERS_YAHOO mais pas dans PRIX_FALLBACK"


def test_evenements_historiques_ont_des_dates_valides():
    """Les bornes des backtests pre-configures sont parsables."""
    for nom, evt in market_data.EVENEMENTS_HISTORIQUES.items():
        debut = pd.to_datetime(evt["debut"])
        fin = pd.to_datetime(evt["fin"])
        assert debut < fin, f"{nom} : debut >= fin"


# === Fiabilite : backtest sans prix inventes, conversion en euros, fraicheur ===


def _build_multi_df_dates(tickers_data: dict, debut: str) -> pd.DataFrame:
    dfs = {}
    for ticker, closes in tickers_data.items():
        idx = pd.bdate_range(debut, periods=len(closes))
        dfs[ticker] = pd.DataFrame({"Close": closes}, index=idx)
    return pd.concat(dfs, axis=1)


def test_get_historique_ecarte_un_actif_pas_encore_cote():
    """Un actif sans cotation au debut de la periode ne doit pas etre prolonge
    en arriere avec un prix futur (biais d'anticipation)."""
    n = 30
    btc = [np.nan] * 20 + [100.0] * 10
    fake = _build_multi_df_dates({"^FCHI": [7000.0] * n, "BTC-USD": btc}, "2024-01-01")
    with patch.object(market_data.yf, "download", return_value=fake):
        df = market_data.get_historique(["CAC 40", "Bitcoin"], "2024-01-01", "2024-02-15",
                                        convertir_eur=False)
    assert list(df.columns) == ["CAC 40"]


def test_get_historique_tolere_un_decalage_de_calendrier():
    n = 30
    or_ = [np.nan, np.nan] + [2300.0] * (n - 2)
    fake = _build_multi_df_dates({"^FCHI": [7000.0] * n, "GC=F": or_}, "2024-01-01")
    with patch.object(market_data.yf, "download", return_value=fake):
        df = market_data.get_historique(["CAC 40", "Or"], "2024-01-01", "2024-02-15",
                                        convertir_eur=False)
    assert "Or" in df.columns
    assert not df.isna().any().any()


def test_get_historique_convertit_les_actifs_dollar_en_euros():
    n = 10
    fake = _build_multi_df_dates({"^GSPC": [5000.0] * n, "^FCHI": [7000.0] * n}, "2024-01-01")
    idx = pd.bdate_range("2023-12-01", periods=60)
    # Le dollar se deprecie : 1 EUR passe de 1.00 a 1.25 USD
    taux = pd.DataFrame({"USD": np.linspace(1.0, 1.25, 60)}, index=idx)
    with patch.object(market_data.yf, "download", return_value=fake), \
         patch.object(market_data, "get_taux_bce", return_value=taux):
        df = market_data.get_historique(["S&P 500", "CAC 40"], "2024-01-01", "2024-01-15")
    # CAC 40 (EUR) inchange ; S&P 500 stable en USD mais en baisse une fois en EUR
    assert df["CAC 40"].iloc[-1] == pytest.approx(7000.0)
    assert df["S&P 500"].iloc[-1] < df["S&P 500"].iloc[0] < 5000.0


def test_get_prix_avec_variation_indique_la_source():
    fake = _build_multi_df({"^GSPC": [5000, 5100], "GC=F": [np.nan, np.nan]})
    with patch.object(market_data.yf, "download", return_value=fake):
        data = market_data.get_prix_avec_variation(["S&P 500", "Or"])
    assert data["S&P 500"]["source"] == "yahoo"
    assert data["S&P 500"]["date"] == "2024-01-02"
    assert data["Or"]["source"] == "secours"
    assert data["Or"]["prix"] == market_data.PRIX_FALLBACK["Or"]


def test_tous_les_actifs_ont_une_devise():
    from config import DEVISE_ACTIF
    for sim_key in market_data.TICKERS_YAHOO:
        assert sim_key in DEVISE_ACTIF
