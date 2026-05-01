"""
pages/historique.py
===================
Onglet Historique : 10 dernières simulations + backtests.
"""

import streamlit as st


def render_page_historique():
    """Affiche l'historique des simulations."""
    st.markdown('<div class="qt-section-title">Historique des simulations</div>',
                unsafe_allow_html=True)
    st.caption("Vos 10 dernières simulations.")

    if not st.session_state.historique_simus:
        st.info("Aucune simulation. Lancez votre première simulation pour commencer.")
        return

    col_b1, _ = st.columns([1, 5])
    with col_b1:
        if st.button("Effacer l'historique"):
            st.session_state.historique_simus = []
            st.rerun()

    for simu in st.session_state.historique_simus:
        couleur = "#2f855a" if simu["perf"] >= 0 else "#c53030"
        icone = "↑" if simu["perf"] >= 0 else "↓"
        tag_mc = " · Monte-Carlo" if simu["monte_carlo"] else ""
        label = f" · Scénario {simu['label_compare']}" if simu.get("label_compare") else ""
        type_label = simu.get("type", "Simulation")

        with st.expander(f"{icone}  {simu['date']}  ·  [{type_label}]  ·  {simu['profil']}{tag_mc}{label}  ·  {simu['perf']:+.2f}%"):
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