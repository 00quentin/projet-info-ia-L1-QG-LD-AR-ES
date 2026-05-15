"""
core/runner.py
==============
Orchestration des simulations et backtests.
Encapsule la logique métier qui était dispersée dans app.py.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple
import pandas as pd

from simulation import simuler_marche_dynamique, simuler_monte_carlo
from ia_bot import analyser_evenement_macro
from config import NOM_AFFICHAGE, NB_SIMULATIONS_MONTE_CARLO
from core.custom_assets import PREFIXE_CUSTOM
from logger import get_logger

log = get_logger("runner")


def _libelle_actif(sim_key: str) -> str:
    """Convertit un sim_key en libelle d'affichage (gere les actifs custom)."""
    if sim_key.startswith(PREFIXE_CUSTOM):
        return sim_key[len(PREFIXE_CUSTOM):]  # PERSO_TSLA -> TSLA
    return NOM_AFFICHAGE.get(
        sim_key,
        sim_key.replace("_", " ").replace("EUR USD", "EUR/USD")
    )


def lancer_simulation_scenario(
    scenario: str,
    actifs_selectionnes: List[str],
    duree: int,
    modele: str,
    monte_carlo: bool,
    prix_reels: Optional[Dict[str, float]],
    vols_reelles: Optional[Dict[str, float]],
    calibration_historique: bool,
    actifs_extras: Optional[Dict[str, Dict[str, float]]] = None,
    custom_tickers: Optional[List[Dict]] = None,
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Lance une simulation complète pour un scénario donné.

    Returns:
        Tuple (resultat, erreur). Si succès, erreur est None.
        resultat contient : scenario, chocs_ia, df, mc_data, perf, perf_df
    """
    log.info("Simulation : scenario='%s...', %d actifs, %d jours, MC=%s",
             scenario[:40], len(actifs_selectionnes), duree, monte_carlo)

    # Mode calibration : on lance EN PARALLELE l'analyse calibree (necessaire) et
    # l'analyse libre (pour la comparaison dashboard). Sans parallelisation, le 2eme
    # appel doublait la latence de la simulation.
    chocs_libre = None
    if calibration_historique:
        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_calib = pool.submit(
                analyser_evenement_macro, scenario,
                calibration_historique=True, custom_tickers=custom_tickers,
            )
            fut_libre = pool.submit(
                analyser_evenement_macro, scenario,
                calibration_historique=False, custom_tickers=custom_tickers,
            )
            chocs = fut_calib.result()
            try:
                chocs_libre_brut = fut_libre.result()
                if (isinstance(chocs_libre_brut, dict)
                        and "erreur" not in chocs_libre_brut
                        and ("actifs" in chocs_libre_brut or "macro" in chocs_libre_brut)):
                    chocs_libre = chocs_libre_brut
            except Exception as e:  # noqa: BLE001
                log.warning("Analyse libre (compa) echouee, on continue sans : %s", e)
    else:
        chocs = analyser_evenement_macro(
            scenario,
            calibration_historique=False,
            custom_tickers=custom_tickers,
        )

    if isinstance(chocs, dict) and "erreur" in chocs and len(chocs) == 1:
        return None, chocs["erreur"]
    if not chocs or ("actifs" not in chocs and "macro" not in chocs):
        return None, "L'IA n'a pas pu lier ce scénario à la finance."

    # MSCI_World benchmark : si l'IA ne l'a pas calibré (choc ≈ 0 par défaut Pydantic),
    # on hérite du choc S&P 500 × 0.85 (corrélation historique ~85%).
    # Sans ça, MSCI_World random-walk autour de 0% pendant que le portefeuille dérive.
    actifs_ia = chocs.get("actifs", {})
    sp500_choc = actifs_ia.get("S&P 500", 0.0)
    msci_choc = actifs_ia.get("MSCI_World", 0.0)
    if abs(msci_choc) < 0.001 and abs(sp500_choc) > 0.001:
        chocs.setdefault("actifs", {})["MSCI_World"] = round(sp500_choc * 0.85, 4)

    # On injecte toujours S&P 500 et MSCI_World comme benchmarks, même si
    # l'utilisateur ne les a pas sélectionnés. Ils sont exclus de perf_df.
    BENCHMARKS_FIXES = ["S&P 500", "MSCI_World"]
    actifs_a_simuler = list(actifs_selectionnes)
    for bm in BENCHMARKS_FIXES:
        if bm not in actifs_a_simuler:
            actifs_a_simuler.append(bm)

    mc_data = None
    if monte_carlo:
        mc_data = simuler_monte_carlo(
            chocs, jours=duree, modele=modele,
            actifs=actifs_a_simuler, nb_simulations=NB_SIMULATIONS_MONTE_CARLO,
            prix_reels=prix_reels, vols_reelles=vols_reelles,
            actifs_extras=actifs_extras,
        )
        df = mc_data["mediane"]
    else:
        df = simuler_marche_dynamique(
            chocs, jours=duree, modele=modele,
            actifs=actifs_a_simuler,
            prix_reels=prix_reels, vols_reelles=vols_reelles,
            actifs_extras=actifs_extras,
        )

    # Calcul de perf defensif : si iloc[0] = 0 ou NaN, fallback 0% au lieu
    # de propager NaN dans l'UI ("+nan%").
    base = df.iloc[0].replace(0, pd.NA)
    perf = ((df.iloc[-1] - df.iloc[0]) / base) * 100
    perf = perf.fillna(0.0).astype(float)

    # perf_df ne doit lister que les actifs réellement choisis par l'utilisateur
    # (sinon le S&P 500 injecté apparaît dans la heatmap alors qu'il n'est pas
    # dans le portefeuille).
    perf_pour_df = perf[perf.index.isin(actifs_selectionnes)]
    perf_df = perf_pour_df.reset_index()
    perf_df.columns = ['Actif', 'Performance (%)']
    perf_df['Actif'] = perf_df['Actif'].apply(_libelle_actif)
    perf_df = perf_df.sort_values(by='Performance (%)', ascending=True)

    return {
        "scenario":   scenario,
        "chocs_ia":   chocs,
        "chocs_libre": chocs_libre,  # None si pas de calibration
        "df":         df,
        "mc_data":    mc_data,
        "perf":       perf,
        "perf_df":    perf_df,
    }, None


def lancer_backtest(
    df_histo: pd.DataFrame,
    actifs_selectionnes: List[str],
) -> Optional[Dict]:
    """
    Construit un dict de résultats à partir d'un DataFrame historique Yahoo.

    Returns:
        Dict avec : df, perf, perf_df, actifs_disponibles, actifs_indisponibles
    """
    if df_histo.empty:
        return None

    # Calcul de perf defensif : si iloc[0] = 0 ou NaN pour un actif, on
    # remplace par 0 plutot que de propager des NaN qui s'affichent "+nan%".
    base = df_histo.iloc[0].replace(0, pd.NA)
    perf = ((df_histo.iloc[-1] - df_histo.iloc[0]) / base) * 100
    perf = perf.fillna(0.0).astype(float)

    perf_df = perf.reset_index()
    perf_df.columns = ['Actif', 'Performance (%)']
    perf_df['Actif'] = perf_df['Actif'].apply(_libelle_actif)
    perf_df = perf_df.sort_values(by='Performance (%)', ascending=True)

    return {
        "df": df_histo,
        "perf": perf,
        "perf_df": perf_df,
        "actifs_disponibles": list(df_histo.columns),
        "actifs_indisponibles": [a for a in actifs_selectionnes if a not in df_histo.columns],
    }