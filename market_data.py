"""
market_data.py
==============
Connexion aux données réelles via Yahoo Finance.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from config import (
    ACTIFS_SECOURS, ACTIFS_COTES_7J, BACKTEST_TOLERANCE_DEBUT_SEANCES,
    CONJONCTURE_HISTORIQUE_ANNEES, SERIE_TAUX_SANS_RISQUE, SERIES_FRED,
    DATE_PRIX_SECOURS, DEVISE_ACTIF, FENETRE_CALIBRATION_JOURS,
)
from core.cache import cache_ttl
from core.conjoncture import construire_conjoncture, taux_sans_risque, telecharger_serie_fred
from core.devises import convertir_en_eur, telecharger_taux_bce
from logger import get_logger

log = get_logger("market_data")


# Snapshot rafraichi 1x/jour : dernier prix connu pour chaque actif. Sert de
# fallback intelligent quand Yahoo est down (au lieu des constantes hardcodees
# qui se decalent de la realite avec le temps).
_SNAPSHOT_PATH = Path(__file__).resolve().parent / ".prix_snapshot.json"
_SNAPSHOT_TTL_HEURES = 24


TICKERS_YAHOO = {
    "S&P 500":              "^GSPC",
    "NASDAQ":               "^NDX",
    "CAC 40":               "^FCHI",
    "MSCI_World":           "URTH",
    "Emerging_Markets":     "EEM",
    "Bons_Tresor_US_10Y":   "IEF",
    "Bund_10Y":             "IS0L.DE",
    "OAT_10Y":              "IFRB.AS",
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


# Prix de secours (filet de derniere ligne). Utilises uniquement si :
# 1) le snapshot disque est inexistant ET 2) Yahoo plante.
# Mis a jour en code de temps en temps. Au runtime, le snapshot disque
# (rafraichi automatiquement) prend le pas sur ces valeurs.
_PRIX_HARDCODE = {k: v["prix"] for k, v in ACTIFS_SECOURS.items()}


# Date du snapshot disque charge (None si absent) : affichee quand on s'en sert.
_SNAPSHOT_META = {"date": None}


def _charger_snapshot() -> dict:
    """Lit le snapshot disque si present et frais (< 24h)."""
    if not _SNAPSHOT_PATH.exists():
        return {}
    try:
        data = json.loads(_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        ts = datetime.fromisoformat(data.get("timestamp", "1970-01-01"))
        age_h = (datetime.now() - ts).total_seconds() / 3600
        if age_h > _SNAPSHOT_TTL_HEURES:
            log.info("Snapshot fallback périmé (%dh), sera rafraîchi", int(age_h))
        _SNAPSHOT_META["date"] = ts.strftime("%Y-%m-%d")
        return data.get("prix", {})
    except (json.JSONDecodeError, ValueError, OSError) as e:
        log.warning("Snapshot fallback illisible : %s", e)
        return {}


def _ecrire_snapshot(prix: dict) -> None:
    """Persiste les prix sur disque pour servir de fallback la prochaine fois."""
    try:
        payload = {"timestamp": datetime.now().isoformat(), "prix": prix}
        _SNAPSHOT_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError as e:
        log.debug("Snapshot non persiste (%s), pas critique", e)


# Initialisation : on charge le snapshot a l'import. Les prix Yahoo recuperes
# avec succes au runtime mettront le snapshot a jour automatiquement.
_SNAPSHOT_PRIX = _charger_snapshot()


def _prix_fallback(sim_key: str, defaut: float = 100) -> float:
    """Hierarchie de fallback : snapshot disque > hardcode > defaut."""
    if sim_key in _SNAPSHOT_PRIX:
        return _SNAPSHOT_PRIX[sim_key]
    return _PRIX_HARDCODE.get(sim_key, defaut)


def source_fallback(sim_key: str) -> dict:
    """Decrit d'ou vient le prix de secours d'un actif : {"source", "date"}.
    Sert a afficher honnetement que le prix n'est pas en direct."""
    if sim_key in _SNAPSHOT_PRIX:
        return {"source": "snapshot", "date": _SNAPSHOT_META["date"] or DATE_PRIX_SECOURS}
    return {"source": "secours", "date": DATE_PRIX_SECOURS}


# Alias retro-compatible : du code externe peut encore lire PRIX_FALLBACK
# comme un dict. On garde l'API publique stable.
PRIX_FALLBACK = _PRIX_HARDCODE


def _extraire_close(data: pd.DataFrame, ticker: str):
    """Serie Close d'un ticker, que yfinance renvoie des colonnes a plat
    (anciennes versions, 1 ticker) ou un MultiIndex (ticker, champ)."""
    if isinstance(data.columns, pd.MultiIndex):
        if ticker in data.columns.get_level_values(0):
            return data[ticker]["Close"]
        if ticker in data.columns.get_level_values(1):
            return data["Close"][ticker]
        return None
    return data["Close"] if "Close" in data.columns else None


@cache_ttl(3600)
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
            prix[sim_key] = _prix_fallback(sim_key)
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
        log.warning("Batch yf.download a echoue (%s) : fallback snapshot", str(e)[:80])
        for sim_key in [ticker_to_sim[t] for t in tickers_a_charger]:
            prix[sim_key] = _prix_fallback(sim_key)
            erreurs.append(sim_key)
        return prix, erreurs

    for ticker in tickers_a_charger:
        sim_key = ticker_to_sim[ticker]
        try:
            serie = _extraire_close(data, ticker)
            serie = serie.dropna() if serie is not None else None
            if serie is not None and not serie.empty:
                prix[sim_key] = float(serie.iloc[-1])
            else:
                prix[sim_key] = _prix_fallback(sim_key)
                erreurs.append(sim_key)
        except (KeyError, IndexError, ValueError) as e:
            log.warning("Yahoo parse failed for %s (%s): %s", sim_key, ticker, str(e)[:60])
            prix[sim_key] = _prix_fallback(sim_key)
            erreurs.append(sim_key)

    if erreurs:
        log.warning("Indispos Yahoo: %s", erreurs)

    # Persist snapshot des prix recuperes avec succes (sert de fallback futur)
    succes = {k: v for k, v in prix.items() if k not in erreurs and k in TICKERS_YAHOO}
    if succes:
        snapshot_complet = {**_SNAPSHOT_PRIX, **succes}
        _ecrire_snapshot(snapshot_complet)
        _SNAPSHOT_META["date"] = datetime.now().strftime("%Y-%m-%d")
        _SNAPSHOT_PRIX.update(succes)

    return prix, erreurs


def _entree_fallback(sim_key: str) -> dict:
    return {"prix": _prix_fallback(sim_key), "variation_pct": 0.0,
            "sparkline": [], **source_fallback(sim_key)}


@cache_ttl(3600)
def get_prix_avec_variation(actifs_keys=None):
    """Retourne pour chaque actif : {"prix", "variation_pct", "sparkline",
    "source", "date"}.

    source vaut "yahoo" (derniere cloture reelle, datee par "date"),
    "snapshot" (dernier prix Yahoo memorise sur disque) ou "secours"
    (valeur figee de config). L'interface s'en sert pour ne jamais presenter
    un prix de secours comme un prix en direct.
    """
    if actifs_keys is None:
        actifs_keys = list(TICKERS_YAHOO.keys())

    result = {}
    tickers_a_charger = []
    ticker_to_sim = {}
    for sim_key in actifs_keys:
        ticker = TICKERS_YAHOO.get(sim_key)
        if ticker is None:
            result[sim_key] = _entree_fallback(sim_key)
        else:
            ticker_to_sim[ticker] = sim_key
            tickers_a_charger.append(ticker)

    if not tickers_a_charger:
        return result

    try:
        data = yf.download(
            tickers=tickers_a_charger, period="7d", interval="1d",
            progress=False, group_by="ticker", threads=True, auto_adjust=True,
        )
    except Exception as e:  # noqa: BLE001
        log.warning("get_prix_avec_variation: batch echec (%s)", str(e)[:80])
        for ticker in tickers_a_charger:
            sk = ticker_to_sim[ticker]
            result[sk] = _entree_fallback(sk)
        return result

    for ticker in tickers_a_charger:
        sk = ticker_to_sim[ticker]
        try:
            serie = _extraire_close(data, ticker)
            serie = serie.dropna() if serie is not None else None
            if serie is not None and len(serie) >= 2:
                prix_now = float(serie.iloc[-1])
                prix_prev = float(serie.iloc[-2])
                variation = ((prix_now - prix_prev) / prix_prev * 100.0) if prix_prev else 0.0
                spark = [float(v) for v in serie.tail(5).tolist()]
                result[sk] = {"prix": prix_now,
                              "variation_pct": variation, "sparkline": spark,
                              "source": "yahoo",
                              "date": pd.Timestamp(serie.index[-1]).strftime("%Y-%m-%d")}
            else:
                result[sk] = _entree_fallback(sk)
        except (KeyError, IndexError, ValueError):
            result[sk] = _entree_fallback(sk)

    return result


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
    for ticker in tickers:
        try:
            serie = _extraire_close(data, ticker)
        except KeyError:
            continue
        if serie is not None:
            out[ticker] = serie
    return out


def _aligner_jours_de_bourse(df: pd.DataFrame, cles_7j: set) -> pd.DataFrame:
    """Retire les week-ends quand des actifs classiques cotoient des cryptos :
    sinon les samedis/dimanches ajoutent des seances a rendement nul pour les
    actions et ecrasent artificiellement leur volatilite."""
    if df.empty or not isinstance(df.index, pd.DatetimeIndex):
        return df
    if all(c in cles_7j for c in df.columns):
        return df
    return df[df.index.dayofweek < 5]


@cache_ttl(86400)
def get_taux_bce() -> pd.DataFrame:
    """Taux de reference BCE (cache 24h : la BCE publie une fois par jour)."""
    return telecharger_taux_bce()


@cache_ttl(21600)
def get_historique(actifs_keys, date_debut, date_fin, convertir_eur=True,
                   avec_dates=False):
    """Prix historiques reels pour un backtest, en euros par defaut.

    Un actif qui ne cotait pas encore au debut de la periode est ecarte
    (au lieu d'etre prolonge en arriere avec un prix futur) ; lancer_backtest
    le signale alors comme indisponible.

    avec_dates=True conserve l'index de dates (utile pour tracer un axe du temps).
    """
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
    df_global = df_global.dropna(axis=1, how="all")
    df_global = _aligner_jours_de_bourse(df_global, ACTIFS_COTES_7J)

    # ffill : trous de cotation en cours de periode (jours feries / suspension).
    # bfill limite : simple decalage de calendrier en tout debut de periode.
    df_global = df_global.ffill().bfill(limit=BACKTEST_TOLERANCE_DEBUT_SEANCES)
    df_global = df_global.dropna(how="all")
    if df_global.empty:
        return pd.DataFrame()
    trop_recents = [c for c in df_global.columns if pd.isna(df_global[c].iloc[0])]
    if trop_recents:
        log.info("Actifs non cotes au debut de la periode, ecartes : %s", trop_recents)
        df_global = df_global.drop(columns=trop_recents)
    if df_global.empty:
        return pd.DataFrame()

    if convertir_eur and isinstance(df_global.index, pd.DatetimeIndex):
        df_global, non_convertis = convertir_en_eur(df_global, DEVISE_ACTIF, get_taux_bce())
        if non_convertis:
            log.warning("Conversion EUR impossible (taux BCE absents) : %s", non_convertis)

    if not avec_dates:
        df_global = df_global.reset_index(drop=True)
    return df_global


@cache_ttl(86400)
def get_rendements_historiques(actifs_keys, jours_calendaires=FENETRE_CALIBRATION_JOURS):
    """Rendements quotidiens reels (jours de bourse) des actifs demandes.

    Sert a mesurer les vraies correlations entre actifs et a alimenter le
    modele de simulation "Historique". DataFrame vide si Yahoo est indisponible.
    """
    fin = datetime.now()
    debut = fin - timedelta(days=jours_calendaires)
    sim_to_ticker = {sk: TICKERS_YAHOO[sk] for sk in actifs_keys if sk in TICKERS_YAHOO}
    if not sim_to_ticker:
        return pd.DataFrame()

    df_tickers = _telecharger_closes(
        list(sim_to_ticker.values()),
        start=debut.strftime("%Y-%m-%d"),
        end=fin.strftime("%Y-%m-%d"),
        interval="1d",
    )
    if df_tickers.empty:
        return pd.DataFrame()

    rename = {tk: sk for sk, tk in sim_to_ticker.items() if tk in df_tickers.columns}
    prix = df_tickers.rename(columns=rename).dropna(axis=1, how="all")
    prix = _aligner_jours_de_bourse(prix, ACTIFS_COTES_7J)
    # ffill court : un jour ferie local ne doit pas casser la correlation
    return prix.ffill(limit=3).pct_change(fill_method=None).dropna(how="all")


@cache_ttl(86400)
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

    # Jours de bourse uniquement : la simulation avance en seances (252/an),
    # la volatilite des cryptos (cotees 7j/7) doit etre mesuree au meme pas.
    if isinstance(df_tickers.index, pd.DatetimeIndex):
        df_tickers = df_tickers[df_tickers.index.dayofweek < 5]

    vols = {}
    for sim_key, ticker in sim_to_ticker.items():
        if ticker not in df_tickers.columns:
            continue
        serie = df_tickers[ticker].dropna()
        if len(serie) > 30:
            rendements = serie.pct_change().dropna()
            vols[sim_key] = float(rendements.std())
    return vols


def _serie_fred_non_vide(serie) -> bool:
    return serie is not None and not serie.empty


# Une serie vide (FRED injoignable) n'est pas memorisee : on retentera au prochain appel.
@cache_ttl(21600, garder=_serie_fred_non_vide)
def get_serie_fred(identifiant: str, depuis: str) -> pd.Series:
    """Serie FRED en cache 6 h (les taux et l'inflation bougent au plus une fois par jour)."""
    return telecharger_serie_fred(identifiant, depuis)


def _depuis(annees: int) -> str:
    return (datetime.now() - timedelta(days=365 * annees)).strftime("%Y-%m-%d")


def get_conjoncture() -> dict:
    """Taux directeurs, taux longs et inflation du moment (FRED). Indicateurs absents si FRED est injoignable."""
    depuis = _depuis(CONJONCTURE_HISTORIQUE_ANNEES)
    # Telechargements en parallele : 6 petites series, surtout de l'attente reseau.
    with ThreadPoolExecutor(max_workers=len(SERIES_FRED)) as pool:
        futures = {cle: pool.submit(get_serie_fred, identifiant, depuis) for cle, (identifiant, _, _) in SERIES_FRED.items()}
    return construire_conjoncture({cle: f.result() for cle, f in futures.items()})


def get_taux_sans_risque(debut=None, fin=None) -> float:
    """Taux sans risque du Sharpe (decimal) : taux de depot BCE actuel, ou moyen sur une periode passee."""
    identifiant = SERIES_FRED[SERIE_TAUX_SANS_RISQUE][0]
    depuis = "1999-01-01" if debut is not None else _depuis(1)
    return taux_sans_risque(get_serie_fred(identifiant, depuis), debut, fin)


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