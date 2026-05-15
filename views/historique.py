"""
pages/historique.py
===================
Onglet Historique : 10 dernières simulations + backtests.
"""

import streamlit as st

from components.empty_states import render_empty_historique
from core.history_store import effacer_historique, sauvegarder_historique


def render_page_historique():
    """Affiche l'historique des simulations."""
    if not st.session_state.historique_simus:
        render_empty_historique()
        return

    st.markdown('<div class="qt-section-title">Historique des simulations</div>',
                unsafe_allow_html=True)
    st.caption("Vos 10 dernières simulations (conservées entre les sessions).")

    col_b1, _ = st.columns([1, 5])
    with col_b1:
        if st.button("Effacer l'historique"):
            st.session_state.historique_simus = []
            effacer_historique()
            st.rerun()

    for i, simu in enumerate(st.session_state.historique_simus):
        couleur = "#16c784" if simu["perf"] >= 0 else "#ef454a"
        icone = "↑" if simu["perf"] >= 0 else "↓"
        tag_mc = " · Monte-Carlo" if simu["monte_carlo"] else ""
        label = f" · Scénario {simu['label_compare']}" if simu.get("label_compare") else ""
        type_label = simu.get("type", "Simulation")
        nom_custom = simu.get("nom_custom", "")

        titre_expander = (
            f"📌 {nom_custom}  ·  {simu['date']}  ·  {simu['perf']:+.2f}%"
            if nom_custom else
            f"{icone}  {simu['date']}  ·  [{type_label}]  ·  {simu['profil']}{tag_mc}{label}  ·  {simu['perf']:+.2f}%"
        )

        with st.expander(titre_expander):
            c1, c2, c3 = st.columns([2.5, 1, 1])
            with c1:
                st.markdown(f"**Scénario :** {simu['scenario']}")
                st.markdown(f"**Actifs analysés :** {simu['nb_actifs']}")
            with c2:
                st.metric("Capital initial", f"{simu['capital']:,.0f} €")
                st.metric("Valeur finale", f"{simu['valeur_finale']:,.0f} €")
            with c3:
                gain = simu['valeur_finale'] - simu['capital']
                st.markdown(f"<div style='background:{couleur}; color:white; padding:18px; "
                            f"border-radius:8px; text-align:center; margin-top:10px;'>"
                            f"<div style='font-size:0.8em; opacity:0.9;'>Gain/Perte</div>"
                            f"<div style='font-size:1.5em; font-weight:700;'>{gain:+,.0f} €</div>"
                            f"</div>", unsafe_allow_html=True)

            # Nommage de la simulation
            st.markdown('<hr style="margin:10px 0; border-color:var(--border);">', unsafe_allow_html=True)
            col_nom, col_save = st.columns([4, 1])
            with col_nom:
                nouveau_nom = st.text_input(
                    "Nom de cette simulation",
                    value=nom_custom,
                    key=f"nom_simu_{i}",
                    placeholder='Ex : "Krach 2008 — profil défensif"',
                    label_visibility="collapsed",
                )
            with col_save:
                if st.button("💾 Nommer", key=f"save_nom_{i}", use_container_width=True,
                             help="Enregistre un nom personnalisé pour retrouver cette simulation facilement."):
                    st.session_state.historique_simus[i]["nom_custom"] = nouveau_nom.strip()
                    sauvegarder_historique(st.session_state.historique_simus)
                    st.rerun()