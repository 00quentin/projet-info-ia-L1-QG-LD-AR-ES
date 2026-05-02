"""
components/sidebar.py
=====================
Sidebar de configuration : mode, scénarios, actifs, profil portefeuille.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Tuple, Any

from market_data import get_prix_actuels, get_volatilites_historiques, EVENEMENTS_HISTORIQUES
from config import (
    ACTIFS_DISPONIBLES, ACTIFS_PAR_DEFAUT, EVENEMENTS_PRESETS, NOM_AFFICHAGE,
    HORIZON_MIN, HORIZON_MAX, HORIZON_DEFAUT, HORIZON_STEP,
    CAPITAL_MIN, CAPITAL_MAX, CAPITAL_DEFAUT, CAPITAL_STEP,
    LABELS_SCENARIOS, NB_SCENARIOS_MAX,
)
from components.notifications import notify_warn, notify_info


def _set_event_A(t: str):
    st.session_state.event_text_A = t


def _render_bouton_recharger():
    """Bouton 🔄 pour vider le cache Yahoo Finance."""
    st.markdown(
        '<style>'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {'
        '    background-color: #ebf8ff !important;'
        '    color: #1a365d !important;'
        '    border: 1px solid #319795 !important;'
        '    font-weight: 600 !important;'
        '}'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {'
        '    background-color: #319795 !important;'
        '    color: white !important;'
        '    border-color: #319795 !important;'
        '}'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) p {'
        '    color: #1a365d !important;'
        '    font-weight: 600 !important;'
        '}'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover p {'
        '    color: white !important;'
        '}'
        '</style>',
        unsafe_allow_html=True
    )
    if st.button("🔄 Recharger les prix Yahoo", use_container_width=True,
                 help="Force un rafraîchissement des prix de marché (cache 1h sinon)."):
        get_prix_actuels.clear()
        get_volatilites_historiques.clear()
        st.rerun()


def _render_section_simulation() -> Dict[str, Any]:
    """Section Simulation prospective : scénarios, modèle, options."""
    options = {}

    nb_scenarios = st.select_slider(
        "Nombre de scénarios à comparer",
        options=list(range(1, NB_SCENARIOS_MAX + 1)),
        value=st.session_state.nb_scenarios,
        help="Comparez jusqu'à 3 scénarios cote à cote sur le meme portefeuille.",
    )
    st.session_state.nb_scenarios = nb_scenarios
    options["nb_scenarios"] = nb_scenarios

    if nb_scenarios > 1:
        st.caption("💡 Conseil : soyez précis et détaillé. Mentionnez le pays, le secteur, l'ampleur.")
        for label in LABELS_SCENARIOS[:nb_scenarios]:
            st.markdown(f"**Scénario {label}**")
            st.text_area(f"Scénario {label}", height=100,
                         key=f"event_text_{label}", label_visibility="collapsed")
    else:
        st.markdown("**Scénarios rapides**")
        preset_keys = list(EVENEMENTS_PRESETS.keys())
        for i in range(0, len(preset_keys), 2):
            col1, col2 = st.columns(2)
            with col1:
                if i < len(preset_keys):
                    st.button(preset_keys[i], key=f"preset_{i}",
                              on_click=_set_event_A,
                              args=(EVENEMENTS_PRESETS[preset_keys[i]],),
                              use_container_width=True)
            with col2:
                if i + 1 < len(preset_keys):
                    st.button(preset_keys[i + 1], key=f"preset_{i+1}",
                              on_click=_set_event_A,
                              args=(EVENEMENTS_PRESETS[preset_keys[i + 1]],),
                              use_container_width=True)
        st.markdown("**Événement à simuler**")
        st.caption("💡 Conseil : soyez précis et détaillé pour que l'analyste IA soit performant. "
                   "Mentionnez le pays, le secteur, l'ampleur, la durée si possible.")
        st.text_area("Événement", height=120, key="event_text_A", label_visibility="collapsed")

    st.markdown("---")
    with st.expander("⚙️ Options avancées", expanded=False):
        options["modele_simu"] = st.selectbox(
            "Comportement du marché",
            ["Probabiliste (Réaliste)", "Historique (Chocs violents)", "Machine Learning (Tendance)"]
        )
        options["duree"] = st.slider("Horizon (jours de cotation)",
                                      HORIZON_MIN, HORIZON_MAX, HORIZON_DEFAUT, HORIZON_STEP)
        options["mode_monte_carlo"] = st.checkbox("Mode Monte-Carlo (50 simulations)", value=False)
        options["utiliser_prix_reels"] = st.checkbox(
            "Utiliser les prix de marché actuels", value=True,
            help="Récupère les prix réels via Yahoo Finance comme point de départ."
        )
        options["calibration_historique"] = st.checkbox(
            "Calibration historique (IA)", value=True,
            help="L'IA s'inspire des amplitudes réelles de 2008, COVID, etc."
        )
    return options


def _render_section_backtest() -> Dict[str, Any]:
    """Section Backtest historique : choix événement, dates."""
    options = {}
    st.markdown("**Sélectionnez un événement historique**")
    event_choisi = st.selectbox("Événement", list(EVENEMENTS_HISTORIQUES.keys()))
    info_event = EVENEMENTS_HISTORIQUES[event_choisi]

    st.markdown(f'<div class="qt-callout"><strong>{event_choisi}</strong><br>'
                f'<span style="font-size:0.9em;">{info_event["description"]}</span></div>',
                unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Période personnalisée (optionnel)**")
    options["event_choisi"] = event_choisi
    options["date_debut_custom"] = st.date_input(
        "Date début", value=datetime.strptime(info_event["debut"], "%Y-%m-%d")
    )
    options["date_fin_custom"] = st.date_input(
        "Date fin", value=datetime.strptime(info_event["fin"], "%Y-%m-%d")
    )
    return options


def _render_selection_actifs() -> List[str]:
    """Cases à cocher des actifs à inclure (regroupées dans un accordéon parent)."""
    st.markdown("---")

    # Pré-comptage pour le badge dans le titre de l'expander
    nb_total = sum(len(c) for c in ACTIFS_DISPONIBLES.values())
    nb_coches = sum(
        1 for cat in ACTIFS_DISPONIBLES.values()
        for sim_key in cat.values()
        if st.session_state.get(f"chk_{sim_key}", sim_key in ACTIFS_PAR_DEFAUT)
    )

    actifs_selectionnes = []
    with st.expander(f"📊 Actifs à analyser  ·  {nb_coches}/{nb_total}", expanded=False):
        st.caption("Cochez les actifs à inclure.")
        for categorie, actifs_cat in ACTIFS_DISPONIBLES.items():
            st.markdown(f'<div class="qt-sidebar-subhead">{categorie}</div>',
                        unsafe_allow_html=True)
            for nom_affiche, sim_key in actifs_cat.items():
                if st.checkbox(nom_affiche,
                                value=(sim_key in ACTIFS_PAR_DEFAUT),
                                key=f"chk_{sim_key}"):
                    actifs_selectionnes.append(sim_key)

    if not actifs_selectionnes:
        notify_warn("Sélectionnez au moins un actif.")

    return actifs_selectionnes


def _render_portefeuille(actifs_selectionnes: List[str]) -> Tuple[float, str, Dict[str, int]]:
    """Section Portefeuille : capital, profil, allocation custom."""
    st.markdown("---")
    st.markdown('<div class="qt-sidebar-section">💼 Portefeuille</div>',
                unsafe_allow_html=True)

    capital_initial = st.number_input(
        "Capital de départ (€)",
        min_value=CAPITAL_MIN, max_value=CAPITAL_MAX,
        value=CAPITAL_DEFAUT, step=CAPITAL_STEP
    )
    profil_risque = st.selectbox(
        "Profil d'investisseur",
        ["Prudent (Hyper Sécurisé)", "Équilibré (Normal)", "Agressif (Risqué)", "Personnalisé"],
        index=1
    )

    allocations_custom = {}
    if profil_risque == "Personnalisé":
        if actifs_selectionnes:
            st.markdown("**Répartition (%)**")
            st.caption("La somme doit être égale à 100%.")
            total_alloc = 0
            defaut_pct = round(100 / len(actifs_selectionnes))
            for sim_key in actifs_selectionnes:
                val = st.number_input(
                    NOM_AFFICHAGE.get(sim_key, sim_key),
                    min_value=0, max_value=100, value=defaut_pct, step=1,
                    key=f"alloc_{sim_key}"
                )
                allocations_custom[sim_key] = val
                total_alloc += val
            couleur = "#2f855a" if total_alloc == 100 else "#c53030"
            icone = "✓" if total_alloc == 100 else "!"
            st.markdown(
                f"<div style='text-align:center; margin-top:8px;'>"
                f"<span style='background:{couleur}; color:white; padding:4px 14px; "
                f"border-radius:12px; font-weight:700; font-size:0.88em;'>{icone} Total : {total_alloc}%</span></div>",
                unsafe_allow_html=True
            )
        else:
            notify_info("Sélectionnez d'abord des actifs.")

    return capital_initial, profil_risque, allocations_custom


def render_sidebar() -> Dict[str, Any]:
    """
    Rend la sidebar complète et retourne un dict avec tous les paramètres choisis.

    Clés du dict retourné :
    - mode_app : "Simulation prospective" | "Backtest historique"
    - + clés selon le mode (voir _render_section_simulation/_render_section_backtest)
    - actifs_selectionnes, capital_initial, profil_risque, allocations_custom
    - lancer : bool (True si bouton cliqué)
    """
    with st.sidebar:
        st.markdown("### Paramètres")
        _render_bouton_recharger()
        st.markdown("---")

        mode_app = st.radio(
            "Mode du terminal",
            ["Simulation prospective", "Backtest historique"],
            help="Simulation : teste un scénario fictif. Backtest : rejoue les vraies données passées."
        )
        st.markdown("---")

        if mode_app == "Simulation prospective":
            options = _render_section_simulation()
        else:
            options = _render_section_backtest()

        actifs_selectionnes = _render_selection_actifs()
        capital_initial, profil_risque, allocations_custom = _render_portefeuille(actifs_selectionnes)

        st.markdown("<br>", unsafe_allow_html=True)
        bouton_label = (
            "Lancer la simulation" if mode_app == "Simulation prospective"
            else "Lancer le backtest"
        )
        lancer = st.button(bouton_label, use_container_width=True, type="primary")

    return {
        "mode_app": mode_app,
        "actifs_selectionnes": actifs_selectionnes,
        "capital_initial": capital_initial,
        "profil_risque": profil_risque,
        "allocations_custom": allocations_custom,
        "lancer": lancer,
        **options,
    }