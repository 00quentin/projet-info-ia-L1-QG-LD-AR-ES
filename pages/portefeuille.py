"""
pages/portefeuille.py
=====================
Onglet Portefeuille : détail composition + bilan.
"""

import streamlit as st

from config import NOM_AFFICHAGE
from core.portfolio import calculer_poids
from components.charts import fig_camembert_repartition


def afficher_portefeuille(res, params, key_prefix="main"):
    """Affiche le détail du portefeuille pour un résultat de simulation."""
    cap = params["capital"]
    profil = params["profil"]
    actifs_sim = params["actifs_sim"]
    poids = calculer_poids(profil, actifs_sim, params["allocations"])

    st.markdown(f"<h3 style='text-align:center; color:#1a365d;'>Portefeuille de {cap:,.0f} €</h3>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#718096; margin-bottom:28px;'>Profil : <strong>{profil}</strong></p>",
                unsafe_allow_html=True)

    valeur_finale = 0
    cols_port = st.columns(4)
    for i, (sk, pct) in enumerate(poids.items()):
        nom = NOM_AFFICHAGE.get(sk, sk.replace("_", " ").replace("EUR USD", "EUR/USD"))
        montant = cap * pct
        rend = (res["perf"].get(sk, 0)) / 100
        final = montant * (1 + rend)
        valeur_finale += final
        with cols_port[i % 4]:
            st.metric(f"{nom} ({pct*100:.1f}%)", f"{final:,.0f} €", f"{rend*100:+.2f}%")

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)

    if poids:
        col_pie, col_bilan = st.columns(2)
        with col_pie:
            fig_pie = fig_camembert_repartition(poids)
            st.plotly_chart(fig_pie, use_container_width=True, key=f"{key_prefix}_pie")

        with col_bilan:
            st.markdown("<br><br>", unsafe_allow_html=True)
            gains = valeur_finale - cap
            st.metric("Bilan net du portefeuille", f"{valeur_finale:,.2f} €",
                      f"{gains:,.2f} € (gains/pertes)")
            perf_g = (gains / cap) * 100 if cap > 0 else 0
            st.metric("Performance globale", f"{perf_g:+.2f} %")

    return valeur_finale


def render_page_portefeuille():
    """Point d'entrée de la page Portefeuille."""
    if st.session_state.simu_A is None:
        st.info("Lancez d'abord une simulation.")
        return

    if st.session_state.mode_comparaison and st.session_state.simu_B:
        sub_A, sub_B = st.tabs(["Scénario A", "Scénario B"])
        with sub_A:
            afficher_portefeuille(st.session_state.simu_A,
                                   st.session_state.params_sim, key_prefix="port_A")
        with sub_B:
            afficher_portefeuille(st.session_state.simu_B,
                                   st.session_state.params_sim, key_prefix="port_B")
    else:
        afficher_portefeuille(st.session_state.simu_A,
                               st.session_state.params_sim, key_prefix="port_main")