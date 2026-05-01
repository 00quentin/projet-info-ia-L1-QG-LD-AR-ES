"""
app.py — Router principal de Quant Terminal
============================================
Ce fichier orchestre l'application : initialise l'état, charge les styles,
construit la sidebar et délègue chaque onglet à son module dédié dans pages/.

Toute la logique métier est dans core/, l'UI réutilisable dans components/,
et les pages dans pages/.
"""

import streamlit as st
from datetime import datetime

# --- Configuration de la page (DOIT être en premier) ---
st.set_page_config(page_title="Quant Terminal", page_icon="◆", layout="wide")

# --- Imports locaux ---
from config import SCENARIO_A_DEFAUT, SCENARIO_B_DEFAUT, HISTORIQUE_TAILLE_MAX, NOM_AFFICHAGE
from logger import get_logger

from market_data import get_prix_actuels, get_volatilites_historiques, get_historique, EVENEMENTS_HISTORIQUES
from core.runner import lancer_simulation_scenario, lancer_backtest
from core.portfolio import calculer_poids

from components.styling import appliquer_styles
from components.header import render_header_complet
from components.sidebar import render_sidebar
from components.footer import render_footer, render_toasts

from pages.dashboard import render_page_dashboard
from pages.portefeuille import render_page_portefeuille
from pages.comparaison import render_page_comparaison
from pages.backtest import render_page_backtest_dashboard, render_page_backtest_detail
from pages.historique import render_page_historique
from pages.academie import render_page_academie
from pages.chat import render_page_chat
from pages.apropos import render_page_apropos

log = get_logger("app")


# ==========================================
# 1. ÉTAT DE SESSION (initialisation)
# ==========================================

def init_session_state():
    """Initialise toutes les variables de session si elles n'existent pas."""
    defaults = {
        "messages_chat": [],
        "event_text_A": SCENARIO_A_DEFAUT,
        "event_text_B": SCENARIO_B_DEFAUT,
        "historique_simus": [],
        "simu_A": None,
        "simu_B": None,
        "mode_comparaison": False,
        "params_sim": {},
        "backtest_data": None,
        "dark_mode": False,
        "show_onboarding": True,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


init_session_state()
appliquer_styles()


# ==========================================
# 2. EN-TÊTE
# ==========================================

render_header_complet()


# ==========================================
# 3. SIDEBAR
# ==========================================

config = render_sidebar()


# ==========================================
# 4. ONGLETS (dépend du mode)
# ==========================================

if config["mode_app"] == "Simulation prospective":
    if st.session_state.mode_comparaison:
        tab_dashboard, tab_portefeuille, tab_compare, tab_hist, tab_academie, tab_chat, tab_apropos = st.tabs([
            "Dashboard", "Portefeuille", "Comparaison A vs B", "Historique", "Académie", "Analyste IA", "À propos"
        ])
    else:
        tab_dashboard, tab_portefeuille, tab_hist, tab_academie, tab_chat, tab_apropos = st.tabs([
            "Dashboard", "Portefeuille", "Historique", "Académie", "Analyste IA", "À propos"
        ])
        tab_compare = None
    tab_backtest = None
else:
    tab_dashboard, tab_backtest, tab_hist, tab_academie, tab_chat, tab_apropos = st.tabs([
        "Dashboard", "Backtest", "Historique", "Académie", "Analyste IA", "À propos"
    ])
    tab_portefeuille = None
    tab_compare = None


# ==========================================
# 5. LANCEMENT — Simulation prospective
# ==========================================

if config["lancer"] and config["mode_app"] == "Simulation prospective":
    st.session_state.simu_A = None
    st.session_state.simu_B = None

    scenario_A = st.session_state.event_text_A
    scenario_B = st.session_state.event_text_B if st.session_state.mode_comparaison else None

    if len(scenario_A.strip()) < 10 or (st.session_state.mode_comparaison and len(scenario_B.strip()) < 10):
        st.warning("Scénario trop court.")
    elif not config["actifs_selectionnes"]:
        st.warning("Sélectionnez au moins un actif.")
    elif config["profil_risque"] == "Personnalisé" and sum(config["allocations_custom"].values()) != 100:
        total = sum(config["allocations_custom"].values())
        st.warning(f"Allocation = 100% requis (actuellement {total}%).")
    else:
        prix_reels = None
        vols_reelles = None
        erreurs_yahoo = []

        if config["utiliser_prix_reels"]:
            with st.spinner("Connexion à Yahoo Finance..."):
                prix_reels, erreurs_yahoo = get_prix_actuels(config["actifs_selectionnes"])
                vols_reelles = get_volatilites_historiques(config["actifs_selectionnes"])
            if erreurs_yahoo:
                st.warning(f"Indisponibles : {', '.join([NOM_AFFICHAGE.get(e, e) for e in erreurs_yahoo])}.")

        msg = "L'analyste IA étudie votre scénario... (cela peut prendre quelques secondes)"
        if config["calibration_historique"]:
            msg = "L'IA recherche des analogies historiques... (cela peut prendre quelques secondes)"
        if config["mode_monte_carlo"]:
            msg = "Mode Monte-Carlo : 50 simulations en cours... (cela peut prendre 15-30 secondes)"
        if st.session_state.mode_comparaison:
            msg = "Analyse comparative de 2 scénarios en cours... (cela peut prendre 30-60 secondes)"

        with st.spinner(msg):
            try:
                result_A, err_A = lancer_simulation_scenario(
                    scenario_A, config["actifs_selectionnes"], config["duree"],
                    config["modele_simu"], config["mode_monte_carlo"],
                    prix_reels, vols_reelles, config["calibration_historique"]
                )
                if err_A:
                    st.error(f"Scénario A : {err_A}")
                else:
                    st.session_state.simu_A = result_A

                if st.session_state.mode_comparaison:
                    result_B, err_B = lancer_simulation_scenario(
                        scenario_B, config["actifs_selectionnes"], config["duree"],
                        config["modele_simu"], config["mode_monte_carlo"],
                        prix_reels, vols_reelles, config["calibration_historique"]
                    )
                    if err_B:
                        st.error(f"Scénario B : {err_B}")
                    else:
                        st.session_state.simu_B = result_B

                st.session_state.params_sim = {
                    "actifs_sim":   config["actifs_selectionnes"].copy(),
                    "allocations":  config["allocations_custom"].copy(),
                    "profil":       config["profil_risque"],
                    "capital":      config["capital_initial"],
                    "duree":        config["duree"],
                    "mc":           config["mode_monte_carlo"],
                    "comparaison":  st.session_state.mode_comparaison,
                    "prix_reels":   config["utiliser_prix_reels"],
                    "calib":        config["calibration_historique"],
                }

                # Historique
                if st.session_state.simu_A:
                    poids_h = calculer_poids(config["profil_risque"],
                                              config["actifs_selectionnes"],
                                              config["allocations_custom"])
                    pairs = [("A", st.session_state.simu_A)]
                    if st.session_state.mode_comparaison:
                        pairs.append(("B", st.session_state.simu_B))

                    for label, res in pairs:
                        if res is None:
                            continue
                        valeur_finale = 0
                        for sk, pct in poids_h.items():
                            rend = res["perf"].get(sk, 0) / 100
                            valeur_finale += config["capital_initial"] * pct * (1 + rend)
                        perf_p = (valeur_finale - config["capital_initial"]) / config["capital_initial"] * 100
                        st.session_state.historique_simus.insert(0, {
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "scenario": res["scenario"][:80] + ("..." if len(res["scenario"]) > 80 else ""),
                            "profil": config["profil_risque"],
                            "capital": config["capital_initial"],
                            "valeur_finale": valeur_finale,
                            "perf": perf_p,
                            "monte_carlo": config["mode_monte_carlo"],
                            "nb_actifs": len(config["actifs_selectionnes"]),
                            "label_compare": label if st.session_state.mode_comparaison else None,
                            "type": "Simulation",
                        })
                    st.session_state.historique_simus = st.session_state.historique_simus[:HISTORIQUE_TAILLE_MAX]
                    st.session_state["_just_simulated"] = True

            except Exception as e:
                log.error("Erreur simulation : %s", e, exc_info=True)
                st.error(f"Erreur technique : {e}")


# ==========================================
# 6. LANCEMENT — Backtest historique
# ==========================================

if config["lancer"] and config["mode_app"] == "Backtest historique":
    if not config["actifs_selectionnes"]:
        st.warning("Sélectionnez au moins un actif.")
    elif config["profil_risque"] == "Personnalisé" and sum(config["allocations_custom"].values()) != 100:
        total = sum(config["allocations_custom"].values())
        st.warning(f"Allocation = 100% requis (actuellement {total}%).")
    else:
        with st.spinner(f"Récupération des données historiques pour {config['event_choisi']}..."):
            try:
                df_histo = get_historique(
                    config["actifs_selectionnes"],
                    config["date_debut_custom"].strftime("%Y-%m-%d"),
                    config["date_fin_custom"].strftime("%Y-%m-%d")
                )

                if df_histo.empty:
                    st.error("Aucune donnée disponible pour cette période.")
                else:
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

                    poids_h = calculer_poids(config["profil_risque"], list(df_histo.columns),
                                              config["allocations_custom"])
                    valeur_finale = 0
                    for sk, pct in poids_h.items():
                        rend = bt_result["perf"].get(sk, 0) / 100
                        valeur_finale += config["capital_initial"] * pct * (1 + rend)
                    perf_p = (valeur_finale - config["capital_initial"]) / config["capital_initial"] * 100
                    st.session_state.historique_simus.insert(0, {
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "scenario": f"Backtest : {config['event_choisi']}",
                        "profil": config["profil_risque"],
                        "capital": config["capital_initial"],
                        "valeur_finale": valeur_finale,
                        "perf": perf_p,
                        "monte_carlo": False,
                        "nb_actifs": len(df_histo.columns),
                        "label_compare": None,
                        "type": "Backtest",
                    })
                    st.session_state.historique_simus = st.session_state.historique_simus[:HISTORIQUE_TAILLE_MAX]
                    st.session_state["_just_backtested"] = True

            except Exception as e:
                log.error("Erreur backtest : %s", e, exc_info=True)
                st.error(f"Erreur backtest : {e}")


# ==========================================
# 7. RENDU DES ONGLETS
# ==========================================

with tab_dashboard:
    if config["mode_app"] == "Simulation prospective":
        render_page_dashboard()
    else:
        render_page_backtest_dashboard()

if tab_portefeuille is not None:
    with tab_portefeuille:
        render_page_portefeuille()

if tab_backtest is not None:
    with tab_backtest:
        render_page_backtest_detail()

if tab_compare is not None:
    with tab_compare:
        render_page_comparaison()

with tab_hist:
    render_page_historique()

with tab_academie:
    render_page_academie()

with tab_chat:
    render_page_chat()

with tab_apropos:
    render_page_apropos()


# ==========================================
# 8. FOOTER + TOASTS
# ==========================================

render_footer()
render_toasts()