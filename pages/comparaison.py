"""
pages/comparaison.py
====================
Onglet Comparaison : duel scénario A vs scénario B.
"""

from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.metrics import calculer_metriques_risque
from core.portfolio import calculer_poids, calculer_valeur_portefeuille
from components.empty_states import render_empty_comparaison
from components.charts import apply_qt_theme, QT_PALETTE


def render_page_comparaison():
    """Point d'entrée de la page Comparaison."""
    if st.session_state.simu_A is None or st.session_state.simu_B is None:
        render_empty_comparaison()
        return

    params = st.session_state.params_sim
    cap = params["capital"]
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])

    def _valeur_port(res):
        v = 0
        for sk, pct in poids.items():
            rend = res["perf"].get(sk, 0) / 100
            v += cap * pct * (1 + rend)
        return v

    v_A = _valeur_port(st.session_state.simu_A)
    v_B = _valeur_port(st.session_state.simu_B)
    perf_A = (v_A - cap) / cap * 100
    perf_B = (v_B - cap) / cap * 100

    # === Cartes des deux scénarios ===
    st.markdown('<div class="qt-section-title">Duel de scénarios</div>', unsafe_allow_html=True)

    cA, cB = st.columns(2)
    with cA:
        st.markdown(f'<div class="qt-card"><div class="qt-tag">Scénario A</div>'
                    f'<p style="font-size:0.95em; margin:8px 0 14px 0;">{st.session_state.simu_A["scenario"]}</p></div>',
                    unsafe_allow_html=True)
        st.metric("Valeur finale", f"{v_A:,.0f} €", f"{perf_A:+.2f} %")
    with cB:
        st.markdown(f'<div class="qt-card"><div class="qt-tag">Scénario B</div>'
                    f'<p style="font-size:0.95em; margin:8px 0 14px 0;">{st.session_state.simu_B["scenario"]}</p></div>',
                    unsafe_allow_html=True)
        st.metric("Valeur finale", f"{v_B:,.0f} €", f"{perf_B:+.2f} %")

    # === Verdict ===
    ecart = abs(perf_A - perf_B)
    if perf_A > perf_B:
        gagnant, couleur_g = "Scénario A", "#2f855a"
    elif perf_B > perf_A:
        gagnant, couleur_g = "Scénario B", "#2f855a"
    else:
        gagnant, couleur_g = "Égalité parfaite", "#718096"

    st.markdown(f'<div style="background:{couleur_g}; color:white; padding:18px 24px; '
                f'border-radius:10px; text-align:center; margin:24px 0; font-size:1.1em;">'
                f'<strong>{gagnant}</strong> l\'emporte avec un écart de <strong>{ecart:.2f} points</strong>'
                f'</div>', unsafe_allow_html=True)

    # === Évolution comparée ===
    st.markdown('<div class="qt-section-title">Évolution comparée du portefeuille</div>',
                unsafe_allow_html=True)

    s_A = calculer_valeur_portefeuille(st.session_state.simu_A["df"], poids, cap)
    s_B = calculer_valeur_portefeuille(st.session_state.simu_B["df"], poids, cap)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=s_A.index, y=s_A, name="Scénario A",
        line=dict(color=QT_PALETTE[0], width=2.8, shape="spline", smoothing=0.5),
        hovertemplate="<b>Scénario A</b><br>%{y:,.0f} €<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=s_B.index, y=s_B, name="Scénario B",
        line=dict(color=QT_PALETTE[1], width=2.8, shape="spline", smoothing=0.5),
        hovertemplate="<b>Scénario B</b><br>%{y:,.0f} €<extra></extra>",
    ))
    fig.add_hline(
        y=cap, line_dash="dot", line_color="#a0aec0", line_width=1,
        annotation_text=f"Capital initial : {cap:,.0f} €",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#718096"),
    )
    fig.update_layout(
        xaxis_title="Jours de cotation",
        yaxis_title="Valeur du portefeuille (€)",
    )
    apply_qt_theme(fig, height=420)
    st.plotly_chart(fig, use_container_width=True, key="compare_port_chart")

    # === Tableau comparatif des métriques ===
    st.markdown('<div class="qt-section-title">Comparatif des métriques de risque</div>',
                unsafe_allow_html=True)
    m_A = calculer_metriques_risque(s_A)
    m_B = calculer_metriques_risque(s_B)

    comp_df = pd.DataFrame({
        "Métrique": ["Volatilité annualisée (%)", "Sharpe Ratio",
                      "Max Drawdown (%)", "VaR 95% (%)", "Performance (%)"],
        "Scénario A": [f"{m_A['vol_ann']:.2f}", f"{m_A['sharpe']:.2f}",
                       f"-{m_A['max_dd']:.2f}", f"{m_A['var_95']:.2f}", f"{perf_A:+.2f}"],
        "Scénario B": [f"{m_B['vol_ann']:.2f}", f"{m_B['sharpe']:.2f}",
                       f"-{m_B['max_dd']:.2f}", f"{m_B['var_95']:.2f}", f"{perf_B:+.2f}"],
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)