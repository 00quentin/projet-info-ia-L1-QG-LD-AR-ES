"""
api/services.py
===============
Orchestration des demandes de l'API : memes etapes que handlers.py (validation,
donnees de marche, moteur, mise en forme), sans rien de Streamlit, et avec des
resultats serialisables en JSON pour le site web.
"""

import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

import numpy as np
import pandas as pd

import ia_bot
import market_data
from api.modeles import DemandeBacktest, DemandePortefeuille, DemandeRapport, DemandeSimulation
from config import (
    ACTIF_TAUX_EUR_USD, ACTIFS_DISPONIBLES, ACTIFS_PAR_DEFAUT, BENCHMARKS,
    CAPITAL_DEFAUT, CAPITAL_MAX, CAPITAL_MIN, CAPITAL_STEP, DEVISE_ACTIF,
    EVENEMENTS_PRESETS, HORIZON_DEFAUT, HORIZON_MAX, HORIZON_MIN, HORIZON_STEP,
    LABELS_SCENARIOS, MODELES_SIMULATION, NB_SIMULATIONS_MONTE_CARLO,
    NOM_AFFICHAGE, PROFILS, PROFIL_PERSONNALISE,
    SCENARIO_A_DEFAUT, SCENARIO_B_DEFAUT, SCENARIO_C_DEFAUT,
)
from core.cache import cache_ttl
from core.custom_assets import PREFIXE_CUSTOM, cle_simulation, valider_et_calibrer
from core.metrics import (
    bandes_portefeuille_monte_carlo, calculer_metriques_risque,
    evaluer_qualite_sharpe, metriques_du_resultat,
)
from core.portfolio import (
    calculer_poids, calculer_valeur_portefeuille, construire_allocations_finales,
)
from core.risk_alerts import evaluer_alertes_risque
from core.runner import lancer_backtest, lancer_simulation_scenario
from core.validation import valider_actifs_et_allocation, valider_scenarios_textes
from logger import get_logger
from pdf_generator import generer_rapport_pdf

log = get_logger("api")

_CHIFFRES_SIGNIFICATIFS = 6


class DemandeInvalide(Exception):
    """La demande est bien formee mais refusee par une regle metier (-> HTTP 422)."""


class ServiceIndisponible(Exception):
    """Une source externe (IA, Yahoo) n'a pas pu repondre (-> HTTP 502)."""


# === Mise en forme JSON ====================================================


def _nombre(x: Any) -> Optional[float]:
    """Float JSON-compatible : NaN/inf -> None, arrondi a 6 chiffres significatifs."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    return float(f"{v:.{_CHIFFRES_SIGNIFICATIFS}g}")


def _liste(valeurs) -> List[Optional[float]]:
    return [_nombre(v) for v in np.asarray(valeurs, dtype=float)]


def _nom(sim_key: str, noms_perso: Dict[str, str]) -> str:
    if sim_key in noms_perso:
        return noms_perso[sim_key]
    if sim_key.startswith(PREFIXE_CUSTOM):
        return sim_key[len(PREFIXE_CUSTOM):]
    return NOM_AFFICHAGE.get(sim_key, sim_key)


def _categorie(sim_key: str) -> str:
    for categorie, actifs in ACTIFS_DISPONIBLES.items():
        if sim_key in actifs.values():
            return categorie
    return "Actifs personnalisés"


# === Catalogue et marches ==================================================


def catalogue() -> Dict[str, Any]:
    """Tout ce que le site doit connaitre pour construire ses formulaires."""
    return {
        "categories": [
            {
                "nom": categorie,
                "actifs": [
                    {"cle": cle, "nom": nom, "devise": DEVISE_ACTIF.get(cle),
                     "ticker": market_data.TICKERS_YAHOO.get(cle),
                     "par_defaut": cle in ACTIFS_PAR_DEFAUT}
                    for nom, cle in actifs.items()
                ],
            }
            for categorie, actifs in ACTIFS_DISPONIBLES.items()
        ],
        "profils": [
            {"nom": nom, "poids": poids} for nom, poids in PROFILS.items()
        ] + [{"nom": PROFIL_PERSONNALISE, "poids": None}],
        "scenarios_rapides": [
            {"titre": titre, "texte": texte} for titre, texte in EVENEMENTS_PRESETS.items()
        ],
        "scenarios_par_defaut": [SCENARIO_A_DEFAUT, SCENARIO_B_DEFAUT, SCENARIO_C_DEFAUT],
        "labels_scenarios": LABELS_SCENARIOS,
        "modeles": MODELES_SIMULATION,
        "evenements_historiques": [
            {"nom": nom, **infos} for nom, infos in market_data.EVENEMENTS_HISTORIQUES.items()
        ],
        "horizon": {"min": HORIZON_MIN, "max": HORIZON_MAX,
                    "defaut": HORIZON_DEFAUT, "pas": HORIZON_STEP},
        "capital": {"min": CAPITAL_MIN, "max": CAPITAL_MAX,
                    "defaut": CAPITAL_DEFAUT, "pas": CAPITAL_STEP},
        "nb_simulations_monte_carlo": NB_SIMULATIONS_MONTE_CARLO,
        "benchmarks": [{"cle": b, "nom": NOM_AFFICHAGE.get(b, b)} for b in BENCHMARKS],
    }


def marches() -> Dict[str, Any]:
    """Derniere cloture de tous les actifs du catalogue, avec source et date."""
    donnees = market_data.get_prix_avec_variation(list(market_data.TICKERS_YAHOO))
    actifs = [
        {
            "cle": cle, "nom": NOM_AFFICHAGE.get(cle, cle),
            "categorie": _categorie(cle), "devise": DEVISE_ACTIF.get(cle),
            "prix": _nombre(d["prix"]), "variation_pct": _nombre(d["variation_pct"]),
            "sparkline": _liste(d.get("sparkline", [])),
            "source": d.get("source"), "date": d.get("date"),
        }
        for cle, d in donnees.items()
    ]
    sources = {a["source"] for a in actifs}
    dates = [a["date"] for a in actifs if a["date"]]
    return {
        "actifs": actifs,
        "en_direct": sources == {"yahoo"},
        "date": max(dates) if dates else None,
    }


@cache_ttl(3600, garder=lambda resultat: resultat[0] is not None)
def calibrer_ticker(ticker: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Valide un ticker Yahoo personnalise (memorise 1h s'il existe)."""
    return valider_et_calibrer(ticker)


def actif_perso(ticker: str) -> Dict[str, Any]:
    info, erreur = calibrer_ticker(ticker)
    if erreur:
        raise DemandeInvalide(erreur)
    return {
        "cle": cle_simulation(info["ticker"]), "ticker": info["ticker"],
        "nom": info["nom"], "devise": info.get("devise"),
        "prix": _nombre(info["prix"]), "volatilite": _nombre(info["volatilite"]),
    }


# === Preparation commune ===================================================


def _preparer_portefeuille(demande: DemandePortefeuille) -> Tuple[Dict[str, Dict], Dict[str, int]]:
    """Calibre les actifs personnalises et valide actifs + allocation.

    Returns:
        (actifs_perso {sim_key: infos}, allocations en pourcentages entiers)
    """
    actifs_perso: Dict[str, Dict] = {}
    for ticker in demande.tickers_perso:
        info, erreur = calibrer_ticker(ticker)
        if erreur:
            raise DemandeInvalide(erreur)
        actifs_perso[cle_simulation(info["ticker"])] = info

    inconnus = [a for a in demande.actifs
                if a not in NOM_AFFICHAGE and a not in actifs_perso]
    if inconnus:
        raise DemandeInvalide(f"Actifs inconnus : {', '.join(inconnus[:5])}.")

    allocations = {k: int(round(v)) for k, v in demande.allocations.items()
                   if k in demande.actifs}
    erreur = valider_actifs_et_allocation(demande.actifs, demande.profil, allocations)
    if erreur:
        raise DemandeInvalide(erreur)
    return actifs_perso, allocations


def _bloc_portefeuille(df: pd.DataFrame, perf: pd.Series, poids: Dict[str, float],
                       capital: float, noms_perso: Dict[str, str],
                       resultat: Optional[Dict] = None) -> Dict[str, Any]:
    """Partie commune simulation/backtest : valeur, metriques, alertes, lignes par actif."""
    valeur_port = calculer_valeur_portefeuille(df, poids, capital)
    metriques = (metriques_du_resultat(resultat, valeur_port, poids, capital)
                 if resultat is not None else calculer_metriques_risque(valeur_port))
    _, valeur_finale = construire_allocations_finales(perf, poids, capital)

    lignes = []
    for cle, part in poids.items():
        rendement = float(perf.get(cle, 0.0)) / 100
        lignes.append({
            "cle": cle, "nom": _nom(cle, noms_perso), "categorie": _categorie(cle),
            "poids": _nombre(part), "investi": _nombre(capital * part),
            "final": _nombre(capital * part * (1 + rendement)),
            "performance_pct": _nombre(rendement * 100),
        })

    return {
        "portefeuille": {
            "capital": _nombre(capital),
            "valeur_finale": _nombre(valeur_finale),
            "performance_pct": _nombre((valeur_finale - capital) / capital * 100),
            "valeurs": _liste(valeur_port.values),
        },
        "metriques": {
            **{k: _nombre(v) for k, v in metriques.items()},
            "qualite_sharpe": evaluer_qualite_sharpe(metriques["sharpe"]),
        },
        "alertes": [
            {"severite": a.severite, "titre": a.titre, "message": a.message,
             "metrique": a.metrique}
            for a in evaluer_alertes_risque(metriques)
        ],
        "allocations": lignes,
    }


def _series_actifs(df: pd.DataFrame, cles: List[str], noms_perso: Dict[str, str],
                   perf: pd.Series, mc: Optional[Dict] = None) -> List[Dict[str, Any]]:
    series = []
    for cle in cles:
        if cle not in df.columns:
            continue
        serie = {
            "cle": cle, "nom": _nom(cle, noms_perso), "categorie": _categorie(cle),
            "performance_pct": _nombre(perf.get(cle, 0.0)),
            "prix": _liste(df[cle].values),
        }
        if mc is not None:
            serie["prix_bas"] = _liste(mc["bas"][cle].values)
            serie["prix_haut"] = _liste(mc["haut"][cle].values)
        series.append(serie)
    return series


def _benchmarks(df: pd.DataFrame, capital: float) -> List[Dict[str, Any]]:
    """Benchmarks ramenes au capital de depart, pour comparer au portefeuille."""
    sortie = []
    for cle in BENCHMARKS:
        if cle in df.columns and df[cle].iloc[0] > 0:
            sortie.append({
                "cle": cle, "nom": NOM_AFFICHAGE.get(cle, cle),
                "valeurs": _liste(df[cle].values / df[cle].iloc[0] * capital),
            })
    return sortie


# === Simulation prospective ================================================


def _formater_simulation(label: str, res: Dict, demande: DemandeSimulation,
                         poids: Dict[str, float], noms_perso: Dict[str, str]) -> Dict[str, Any]:
    chocs = res["chocs_ia"]
    df, mc = res["df"], res["mc_data"]
    sortie = {
        "label": label,
        "scenario": res["scenario"],
        "erreur": None,
        "analyse": {
            "explication": chocs.get("explication_courte"),
            "inflation": _nombre((chocs.get("macro") or {}).get("inflation", 0.0)),
            "taux_directeurs": _nombre((chocs.get("macro") or {}).get("taux_directeurs", 0.0)),
            "evenement_reference": chocs.get("evenement_reference"),
            "references_historiques": chocs.get("references_historiques") or [],
            "fiabilite": chocs.get("fiabilite_calibration"),
            "chocs": {k: _nombre(v) for k, v in (chocs.get("actifs") or {}).items()
                      if k in demande.actifs},
            "chocs_sans_calibration": (
                {k: _nombre(v) for k, v in (res["chocs_libre"].get("actifs") or {}).items()
                 if k in demande.actifs}
                if res.get("chocs_libre") else None
            ),
            "macro_sans_calibration": (
                {"inflation": _nombre((res["chocs_libre"].get("macro") or {}).get("inflation", 0.0)),
                 "taux_directeurs": _nombre((res["chocs_libre"].get("macro") or {}).get("taux_directeurs", 0.0))}
                if res.get("chocs_libre") else None
            ),
        },
        **_bloc_portefeuille(df, res["perf"], poids, demande.capital, noms_perso, res),
        "actifs": _series_actifs(df, demande.actifs, noms_perso, res["perf"], mc),
        "benchmarks": _benchmarks(df, demande.capital),
        "converti_eur": res["converti_eur"],
    }
    if mc is not None:
        bandes = bandes_portefeuille_monte_carlo(
            mc["chemins"], list(mc["colonnes"]), poids, demande.capital)
        if bandes is not None:
            sortie["portefeuille"]["valeurs_bas"] = _liste(bandes["bas"])
            sortie["portefeuille"]["valeurs_haut"] = _liste(bandes["haut"])
    return sortie


def executer_simulation(demande: DemandeSimulation) -> Dict[str, Any]:
    """Simule 1 a 3 scenarios sur le meme portefeuille."""
    textes = dict(zip(LABELS_SCENARIOS, demande.scenarios))
    erreur = valider_scenarios_textes(textes)
    if erreur:
        raise DemandeInvalide(erreur[1])
    actifs_perso, allocations = _preparer_portefeuille(demande)
    noms_perso = {k: v.get("nom", v["ticker"]) for k, v in actifs_perso.items()}

    actifs_extras = {
        k: {"prix": v["prix"], "volatilite": v["volatilite"], "devise": v.get("devise")}
        for k, v in actifs_perso.items()
    } or None
    custom_tickers = [
        {"sim_key": k, "ticker": v["ticker"], "nom": v.get("nom", v["ticker"])}
        for k, v in actifs_perso.items() if k in demande.actifs
    ] or None

    prix_reels = vols_reelles = rendements = None
    prix_de_secours: List[str] = []
    if demande.prix_reels:
        standards = [a for a in demande.actifs if a not in actifs_perso]
        actifs_marche = sorted(set(standards) | set(BENCHMARKS) | {ACTIF_TAUX_EUR_USD})
        prix_reels, erreurs_yahoo = market_data.get_prix_actuels(actifs_marche)
        vols_reelles = market_data.get_volatilites_historiques(actifs_marche)
        rendements = market_data.get_rendements_historiques(actifs_marche)
        prix_de_secours = [e for e in erreurs_yahoo if e in standards]

    def _lancer(scenario: str):
        return lancer_simulation_scenario(
            scenario, demande.actifs, demande.duree, demande.modele,
            demande.monte_carlo, prix_reels, vols_reelles, demande.calibration,
            actifs_extras=actifs_extras, custom_tickers=custom_tickers,
            rendements_historiques=rendements, convertir_eur=demande.convertir_eur,
        )

    # Les scenarios sont independants : on les lance en parallele (l'essentiel
    # du temps est l'attente de l'IA).
    with ThreadPoolExecutor(max_workers=len(textes)) as pool:
        bruts = list(pool.map(_lancer, textes.values()))

    poids = calculer_poids(demande.profil, demande.actifs, allocations)
    scenarios = []
    for (label, texte), (res, err) in zip(textes.items(), bruts):
        if err:
            scenarios.append({"label": label, "scenario": texte, "erreur": err})
        else:
            scenarios.append(_formater_simulation(label, res, demande, poids, noms_perso))

    if all(s["erreur"] for s in scenarios):
        raise ServiceIndisponible(scenarios[0]["erreur"])

    return {
        "date": datetime.now().isoformat(timespec="seconds"),
        "parametres": {
            "profil": demande.profil, "capital": demande.capital, "duree": demande.duree,
            "modele": demande.modele, "monte_carlo": demande.monte_carlo,
            "prix_reels": demande.prix_reels, "calibration": demande.calibration,
            "convertir_eur": demande.convertir_eur, "nb_actifs": len(demande.actifs),
            "nb_simulations": NB_SIMULATIONS_MONTE_CARLO if demande.monte_carlo else 1,
        },
        "prix_de_secours": [
            {"cle": cle, "nom": NOM_AFFICHAGE.get(cle, cle),
             "date": market_data.source_fallback(cle)["date"]}
            for cle in prix_de_secours
        ],
        "scenarios": scenarios,
    }


# === Backtest historique ===================================================


def executer_backtest(demande: DemandeBacktest) -> Dict[str, Any]:
    """Rejoue le portefeuille sur une vraie periode passee."""
    _, allocations = _preparer_portefeuille(demande)

    description = None
    debut, fin = demande.date_debut, demande.date_fin
    if demande.evenement is not None:
        infos = market_data.EVENEMENTS_HISTORIQUES.get(demande.evenement)
        if infos is None:
            raise DemandeInvalide("Événement historique inconnu.")
        description = infos["description"]
        debut = debut or datetime.strptime(infos["debut"], "%Y-%m-%d").date()
        fin = fin or datetime.strptime(infos["fin"], "%Y-%m-%d").date()
        if fin <= debut:
            raise DemandeInvalide("La date de fin doit être après la date de début.")

    a_charger = sorted(set(demande.actifs) | set(BENCHMARKS))
    df_complet = market_data.get_historique(
        a_charger, debut.isoformat(), fin.isoformat(),
        convertir_eur=demande.convertir_eur, avec_dates=True,
    )
    choisis = [c for c in df_complet.columns if c in demande.actifs]
    if df_complet.empty or not choisis:
        raise ServiceIndisponible("Aucune donnée disponible pour ces actifs sur cette période.")

    bt = lancer_backtest(df_complet[choisis], demande.actifs)
    poids = calculer_poids(demande.profil, choisis, allocations)
    return {
        "date": datetime.now().isoformat(timespec="seconds"),
        "evenement": demande.evenement,
        "description": description,
        "date_debut": debut.isoformat(),
        "date_fin": fin.isoformat(),
        "dates": [d.strftime("%Y-%m-%d") for d in pd.DatetimeIndex(df_complet.index)],
        "parametres": {
            "profil": demande.profil, "capital": demande.capital,
            "duree": len(df_complet), "convertir_eur": demande.convertir_eur,
            "nb_actifs": len(choisis),
        },
        "actifs_indisponibles": [
            {"cle": a, "nom": _nom(a, {})} for a in bt["actifs_indisponibles"]
        ],
        **_bloc_portefeuille(bt["df"], bt["perf"], poids, demande.capital, {}),
        "actifs": _series_actifs(bt["df"], choisis, {}, bt["perf"]),
        "benchmarks": _benchmarks(df_complet, demande.capital),
        "converti_eur": demande.convertir_eur,
    }


# === Chat et rapport PDF ===================================================


def repondre_chat(messages: List[Dict[str, str]]) -> str:
    return ia_bot.discuter_avec_ia(messages)


def generer_pdf(demande: DemandeRapport) -> bytes:
    """Met en page en PDF un resultat deja affiche sur le site."""
    perf_df = pd.DataFrame({
        "Actif": [escape(l.nom) for l in demande.performances],
        "Performance (%)": [l.performance for l in demande.performances],
    }).sort_values("Performance (%)")
    metriques = {"vol_ann": demande.vol_ann, "sharpe": demande.sharpe,
                 "max_dd": demande.max_dd, "var_95": demande.var_95}
    chocs = {
        "explication_courte": escape(demande.explication),
        "macro": {"inflation": demande.inflation, "taux_directeurs": demande.taux_directeurs},
        "evenement_reference": escape(demande.evenement_reference or "") or None,
    }
    scenario = escape(demande.scenario)

    analyse_senior = None
    if demande.avec_analyse_ia:
        analyse_senior = ia_bot.generer_rapport_complet_ia(
            scenario=demande.scenario, chocs_ia={"explication_courte": demande.explication},
            perf_par_actif=perf_df, metriques=metriques,
            valeur_initiale=demande.capital, valeur_finale=demande.valeur_finale,
            profil=demande.profil,
        )

    return generer_rapport_pdf(
        simu={"scenario": scenario, "chocs_ia": chocs, "perf_df": perf_df},
        params={"capital": demande.capital, "profil": escape(demande.profil),
                "actifs_sim": [None] * demande.nb_actifs, "duree": demande.duree,
                "mc": demande.monte_carlo, "prix_reels": demande.prix_reels,
                "calib": demande.calibration},
        metriques=metriques,
        allocations_finales=[
            {"nom": escape(l.nom), "poids": l.poids, "investi": l.investi,
             "final": l.final, "rendement": l.rendement}
            for l in demande.allocations
        ],
        valeur_finale=demande.valeur_finale,
        type_rapport=demande.type_rapport,
        analyse_senior=analyse_senior,
    )
