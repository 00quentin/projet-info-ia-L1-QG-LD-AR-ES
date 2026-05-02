"""
app.py — Router principal de Quant Terminal
============================================
Ce fichier orchestre l'application : initialise l'état, charge les styles,
construit la sidebar et délègue chaque onglet à son module dédié dans pages/.

Toute la logique métier est dans core/, l'UI réutilisable dans components/,
les pages dans pages/, et les flots de lancement dans handlers.py.
"""

import streamlit as st

# --- Configuration de la page (DOIT être en premier) ---
st.set_page_config(page_title="Quant Terminal", page_icon="◆", layout="wide")

# --- Imports locaux ---
from config import SCENARIO_A_DEFAUT, SCENARIO_B_DEFAUT
from logger import get_logger

from core.history_store import charger_historique
from handlers import handler_simulation, handler_backtest

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

    # Historique : recharge depuis disque uniquement la 1ere fois (cold start)
    if "historique_simus" not in st.session_state:
        st.session_state.historique_simus = charger_historique()


init_session_state()
appliquer_styles()


# ==========================================
# 2. EN-TÊTE + SIDEBAR
# ==========================================

render_header_complet()
config = render_sidebar()

# Auto-launch déclenché depuis l'empty state du Dashboard (clic sur preset).
if st.session_state.pop("_auto_launch", False) and config["mode_app"] == "Simulation prospective":
    config["lancer"] = True


# ==========================================
# 3. ONGLETS (dépend du mode)
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
# 4. LANCEMENT (delegue a handlers.py)
# ==========================================

if config["lancer"]:
    if config["mode_app"] == "Simulation prospective":
        handler_simulation(config)
    else:
        handler_backtest(config)


# ==========================================
# 5. RENDU DES ONGLETS
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
# 6. FOOTER + TOASTS
# ==========================================

render_footer()
render_toasts()
