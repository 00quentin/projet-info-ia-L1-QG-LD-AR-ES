"""
handlers.py
===========
Orchestration des deux flots de lancement (Simulation prospective et
Backtest historique). Extrait d'app.py pour garder le router lisible.

Pourquoi pas dans core/ : ces handlers couplent st.session_state, les
spinners, les notifications et les skeletons. core/ reste pur logique
metier (pas d'import streamlit).
"""

from datetime import datetime
from typing import Dict, Any

import streamlit as st

from config import HISTORIQUE_TAILLE_MAX, NOM_AFFICHAGE, LABELS_SCENARIOS
from logger import get_logger
from market_data import (
    get_prix_actuels, get_volatilites_historiques, get_historique,
    EVENEMENTS_HISTORIQUES,
)
from core.runner import lancer_simulation_scenario, lancer_backtest
from core.portfolio import calculer_poids, construire_allocations_finales
from core.history_store import ajouter_entree
from core.custom_assets import SESSION_KEY as ACTIFS_PERSO_KEY, vers_actifs_extras
from components.skeletons import render_skeleton_dashboard
from components.notifications import notify_warn, notify_error

log = get_logger("handlers")


# === Helpers internes =====================================================


def _enregistrer_historique(scenario: str, profil: str, capital: float,
                            valeur_finale: float, monte_carlo: bool,
                            nb_actifs: int, type_op: str,
                            label_compare: str = None) -> None:
    """Insere une nouvelle entree dans l'historique, tronque, et persiste."""
    perf = (valeur_finale - capital) / capital * 100 if capital else 0.0
    entree = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "scenario": scenario[:80] + ("..." if len(scenario) > 80 else ""),
        "profil": profil,
        "capital": capital,
        "valeur_finale": valeur_finale,
        "perf": perf,
        "monte_carlo": monte_carlo,
        "nb_actifs": nb_actifs,
        "label_compare": label_compare,
        "type": type_op,
    }
    st.session_state.historique_simus = ajouter_entree(
        st.session_state.historique_simus, entree, HISTORIQUE_TAILLE_MAX,
    )


def _valider_actifs_et_allocation(config: Dict[str, Any]) -> bool:
    """
    Garde-fou commun aux 2 modes : au moins un actif et, si profil
    Personnalise, allocation totalisant 100%.

    Returns:
        True si la config est valide pour lancer ; False sinon (notification
        deja affichee).
    """
    if not config["actifs_selectionnes"]:
        notify_warn("Sélectionnez au moins un actif dans la barre latérale.")
        return False
    if config["profil_risque"] == "Personnalisé":
        total = sum(config["allocations_custom"].values())
        if total != 100:
            notify_warn(f"L'allocation doit totaliser 100% (actuellement {total}%).")
            return False
    return True


def _message_attente_simulation(config: Dict[str, Any]) -> str:
    """Choisit le message de spinner adapte au mode (MC, calibration, comparaison)."""
    nb = st.session_state.nb_scenarios
    if nb > 1:
        return f"Analyse comparative de {nb} scénarios en cours... (cela peut prendre {30*nb}-{60*nb} secondes)"
    if config["mode_monte_carlo"]:
        return "Mode Monte-Carlo : 50 simulations en cours... (cela peut prendre 15-30 secondes)"
    if config["calibration_historique"]:
        return "L'IA recherche des analogies historiques... (cela peut prendre quelques secondes)"
    return "L'analyste IA étudie votre scénario... (cela peut prendre quelques secondes)"


# === Handlers publics =====================================================


def handler_simulation(config: Dict[str, Any]) -> None:
    """
    Execute le flot de Simulation prospective : validation, fetch prix
    Yahoo si demande, simulation pour chaque label actif, enregistrement
    dans l'historique. Les erreurs sont notifiees, jamais propagees.
    """
    nb = st.session_state.nb_scenarios
    labels_actifs = LABELS_SCENARIOS[:nb]

    # Reset toutes les simulations en cours
    st.session_state.simulations = {label: None for label in LABELS_SCENARIOS}

    # Recupere les textes de scenario par label
    textes = {label: st.session_state[f"event_text_{label}"] for label in labels_actifs}

    # Validation : chaque scenario doit faire >= 10 caracteres
    for label, txt in textes.items():
        if len(txt.strip()) < 10:
            notify_warn(f"Scénario {label} trop court (au moins 10 caractères).")
            return

    if not _valider_actifs_et_allocation(config):
        return

    # Actifs personnalises ajoutes par l'utilisateur (deja calibres a l'ajout)
    actifs_perso = st.session_state.get(ACTIFS_PERSO_KEY, {})
    actifs_extras = vers_actifs_extras(actifs_perso) if actifs_perso else None

    # Liste pour l'IA : on ne lui passe que les customs effectivement coches
    custom_tickers_ia = [
        {"sim_key": sim_key, "ticker": v["ticker"], "nom": v.get("nom", v["ticker"])}
        for sim_key, v in actifs_perso.items()
        if sim_key in config["actifs_selectionnes"]
    ] or None

    prix_reels = vols_reelles = None
    if config["utiliser_prix_reels"]:
        # Pour Yahoo, on ne demande que les actifs du catalogue standard ;
        # les customs ont deja leur prix/vol calibres a l'ajout.
        actifs_standards = [
            a for a in config["actifs_selectionnes"]
            if a not in (actifs_perso or {})
        ]
        with st.spinner("Connexion à Yahoo Finance..."):
            prix_reels, erreurs_yahoo = get_prix_actuels(actifs_standards)
            vols_reelles = get_volatilites_historiques(actifs_standards)
        if erreurs_yahoo:
            noms = ", ".join(NOM_AFFICHAGE.get(e, e) for e in erreurs_yahoo)
            notify_warn(f"Données Yahoo Finance indisponibles pour : {noms}.")

    skeleton_ph = render_skeleton_dashboard()
    with st.spinner(_message_attente_simulation(config)):
        try:
            for label, scenario_txt in textes.items():
                result, err = lancer_simulation_scenario(
                    scenario_txt, config["actifs_selectionnes"], config["duree"],
                    config["modele_simu"], config["mode_monte_carlo"],
                    prix_reels, vols_reelles, config["calibration_historique"],
                    actifs_extras=actifs_extras,
                    custom_tickers=custom_tickers_ia,
                )
                if err:
                    notify_error(f"Scénario {label} : {err}")
                else:
                    st.session_state.simulations[label] = result

            st.session_state.params_sim = {
                "actifs_sim":   config["actifs_selectionnes"].copy(),
                "allocations":  config["allocations_custom"].copy(),
                "profil":       config["profil_risque"],
                "capital":      config["capital_initial"],
                "duree":        config["duree"],
                "mc":           config["mode_monte_carlo"],
                "nb_scenarios": nb,
                "prix_reels":   config["utiliser_prix_reels"],
                "calib":        config["calibration_historique"],
            }

            poids_h = calculer_poids(
                config["profil_risque"], config["actifs_selectionnes"],
                config["allocations_custom"],
            )
            for label in labels_actifs:
                res = st.session_state.simulations[label]
                if res is None:
                    continue
                _, valeur_finale = construire_allocations_finales(
                    res["perf"], poids_h, config["capital_initial"],
                )
                _enregistrer_historique(
                    scenario=res["scenario"],
                    profil=config["profil_risque"],
                    capital=config["capital_initial"],
                    valeur_finale=valeur_finale,
                    monte_carlo=config["mode_monte_carlo"],
                    nb_actifs=len(config["actifs_selectionnes"]),
                    type_op="Simulation",
                    label_compare=label if nb > 1 else None,
                )
            if any(st.session_state.simulations[lab] for lab in labels_actifs):
                st.session_state["_just_simulated"] = True

        except Exception as e:
            log.error("Erreur simulation : %s", e, exc_info=True)
            notify_error(f"Erreur technique : {e}")
        finally:
            skeleton_ph.empty()


def handler_backtest(config: Dict[str, Any]) -> None:
    """
    Execute le flot de Backtest historique : validation, fetch Yahoo
    sur la periode choisie, calcul, enregistrement dans l'historique.
    """
    if not _valider_actifs_et_allocation(config):
        return

    skeleton_ph_bt = render_skeleton_dashboard()
    with st.spinner(f"Récupération des données historiques pour {config['event_choisi']}..."):
        try:
            df_histo = get_historique(
                config["actifs_selectionnes"],
                config["date_debut_custom"].strftime("%Y-%m-%d"),
                config["date_fin_custom"].strftime("%Y-%m-%d"),
            )

            if df_histo.empty:
                notify_error("Aucune donnée disponible pour cette période.")
                return

            bt_result = lancer_backtest(df_histo, config["actifs_selectionnes"])
            bt_result["evenement"] = config["event_choisi"]
            bt_result["description"] = EVENEMENTS_HISTORIQUES[config["event_choisi"]]["description"]
            bt_result["date_debut"] = config["date_debut_custom"]
            bt_result["date_fin"] = config["date_fin_custom"]
            st.session_state.backtest_data = bt_result

            st.session_state.params_sim = {
                "actifs_sim":   list(df_histo.columns),
                "allocations":  config["allocations_custom"].copy(),
                "profil":       config["profil_risque"],
                "capital":      config["capital_initial"],
            }

            poids_h = calculer_poids(
                config["profil_risque"], list(df_histo.columns),
                config["allocations_custom"],
            )
            _, valeur_finale = construire_allocations_finales(
                bt_result["perf"], poids_h, config["capital_initial"],
            )
            _enregistrer_historique(
                scenario=f"Backtest : {config['event_choisi']}",
                profil=config["profil_risque"],
                capital=config["capital_initial"],
                valeur_finale=valeur_finale,
                monte_carlo=False,
                nb_actifs=len(df_histo.columns),
                type_op="Backtest",
            )
            st.session_state["_just_backtested"] = True

        except Exception as e:
            log.error("Erreur backtest : %s", e, exc_info=True)
            notify_error(f"Erreur backtest : {e}")
        finally:
            skeleton_ph_bt.empty()
