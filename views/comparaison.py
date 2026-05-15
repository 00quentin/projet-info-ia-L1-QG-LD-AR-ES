"""
pages/comparaison.py
====================
Onglet Comparaison : duel ou tournoi entre 2 ou 3 scenarios.

Generalise depuis l'ancienne version A vs B en N=1..3 scenarios. Le
classement designe le scenario gagnant en absolu et affiche l'ecart
avec le second.
"""

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from config import LABELS_SCENARIOS
from core.metrics import calculer_metriques_risque
from core.portfolio import calculer_poids, calculer_valeur_portefeuille
from core.export_csv import generer_csv_comparaison
from components.empty_states import render_empty_comparaison
from components.charts import apply_qt_theme, QT_PALETTE, get_theme_colors


def _libelle_classement(idx: int) -> str:
    return ["1er", "2e", "3e"][idx] if idx < 3 else f"{idx+1}e"


def render_page_comparaison():
    """Point d'entrée de la page Comparaison."""
    simulations = st.session_state.simulations
    labels_dispo = [lab for lab in LABELS_SCENARIOS if simulations.get(lab) is not None]

    if len(labels_dispo) < 2:
        render_empty_comparaison()
        return

    params = st.session_state.params_sim
    cap = params["capital"]
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])

    # === Series quotidiennes + metriques pour chaque scenario ===
    series = {lab: calculer_valeur_portefeuille(simulations[lab]["df"], poids, cap)
              for lab in labels_dispo}
    metriques = {lab: calculer_metriques_risque(series[lab]) for lab in labels_dispo}
    valeurs = {lab: float(series[lab].iloc[-1]) for lab in labels_dispo}
    perfs = {lab: (valeurs[lab] - cap) / cap * 100 for lab in labels_dispo}

    # === Cartes ===
    titre_section = "Tournoi" if len(labels_dispo) >= 3 else "Duel"
    st.markdown(f'<div class="qt-section-title">{titre_section} de scénarios</div>',
                unsafe_allow_html=True)

    cols = st.columns(len(labels_dispo))
    for col, label in zip(cols, labels_dispo):
        with col:
            st.markdown(
                f'<div class="qt-card"><div class="qt-tag">Scénario {label}</div>'
                f'<p style="font-size:0.95em; margin:8px 0 14px 0;">{simulations[label]["scenario"]}</p></div>',
                unsafe_allow_html=True
            )
            st.metric("Valeur finale", f"{valeurs[label]:,.0f} €",
                       f"{perfs[label]:+.2f} %")

    # === Classement / verdict ===
    classement = sorted(labels_dispo, key=lambda lab: perfs[lab], reverse=True)
    gagnant = classement[0]
    second = classement[1]
    ecart = perfs[gagnant] - perfs[second]

    if ecart < 0.01:
        couleur_g = "#718096"
        message_g = f"Égalité parfaite entre {len(labels_dispo)} scénarios"
    else:
        couleur_g = "#16c784"
        message_g = (f"Scénario {gagnant} l'emporte avec un écart de "
                     f"<strong>{ecart:.2f} points</strong> sur le scénario {second}")

    st.markdown(
        f'<div style="background:{couleur_g}; color:white; padding:18px 24px; '
        f'border-radius:10px; text-align:center; margin:24px 0; font-size:1.1em;">'
        f'{message_g}</div>',
        unsafe_allow_html=True
    )

    # === Evolution comparee ===
    st.markdown('<div class="qt-section-title">Évolution comparée du portefeuille</div>',
                unsafe_allow_html=True)
    fig = go.Figure()
    for i, label in enumerate(labels_dispo):
        s = series[label]
        fig.add_trace(go.Scatter(
            x=s.index, y=s, name=f"Scénario {label}",
            line=dict(color=QT_PALETTE[i % len(QT_PALETTE)], width=2.8,
                       shape="spline", smoothing=0.5),
            hovertemplate=f"<b>Scénario {label}</b><br>%{{y:,.0f}} €<extra></extra>",
        ))
    c_th = get_theme_colors()
    fig.add_hline(
        y=cap, line_dash="dot", line_color=c_th["axis"], line_width=1,
        annotation_text=f"Capital initial : {cap:,.0f} €",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color=c_th["annot"]),
    )
    fig.update_layout(xaxis_title="Jours de cotation",
                      yaxis_title="Valeur du portefeuille (€)")
    apply_qt_theme(fig, height=440)
    st.plotly_chart(fig, use_container_width=True, key="compare_port_chart",
                    config={"scrollZoom": False})

    # === Tableau comparatif des metriques (HTML, meilleur surligné) ===
    st.markdown('<div class="qt-section-title">Comparatif des métriques de risque</div>',
                unsafe_allow_html=True)
    st.caption("La valeur la plus favorable de chaque ligne est surlignée en vert.")

    # (label, valeurs brutes par scénario, format, plus_grand_est_mieux)
    lignes_def = [
        ("Volatilité annualisée", {l: metriques[l]["vol_ann"] for l in labels_dispo},
         lambda v: f"{v:.2f}%", False),
        ("Sharpe Ratio", {l: metriques[l]["sharpe"] for l in labels_dispo},
         lambda v: f"{v:.2f}", True),
        ("Max Drawdown", {l: metriques[l]["max_dd"] for l in labels_dispo},
         lambda v: f"−{v:.2f}%", False),
        ("VaR 95%", {l: abs(metriques[l]["var_95"]) for l in labels_dispo},
         lambda v: f"−{v:.2f}%", False),
        ("Performance", {l: perfs[l] for l in labels_dispo},
         lambda v: f"{v:+.2f}%", True),
    ]

    h_style = ('padding:10px 14px; font-size:0.78em; font-weight:600; '
               'text-transform:uppercase; letter-spacing:0.05em; '
               'color:var(--text-muted); background:var(--card); '
               'border-bottom:2px solid var(--border);')
    entetes = (f'<th style="{h_style} text-align:left;">Métrique</th>'
               + "".join(f'<th style="{h_style} text-align:center;">Scénario {l}</th>'
                         for l in labels_dispo))

    lignes_html = ""
    for label, vals, fmt, plus_haut_mieux in lignes_def:
        meilleur = (max(vals.values()) if plus_haut_mieux else min(vals.values()))
        cells = (f'<td style="padding:11px 14px; font-weight:500; color:var(--text); '
                 f'border-bottom:1px solid var(--border);">{label}</td>')
        for l in labels_dispo:
            est_best = abs(vals[l] - meilleur) < 1e-9
            base = ('padding:11px 14px; text-align:center; '
                    'border-bottom:1px solid var(--border);')
            if est_best and len(labels_dispo) > 1:
                cells += (f'<td style="{base} background:rgba(22,199,132,0.1);">'
                          f'<strong style="color:#16c784;">{fmt(vals[l])}</strong></td>')
            else:
                cells += f'<td style="{base} color:var(--text);">{fmt(vals[l])}</td>'
        lignes_html += f'<tr>{cells}</tr>'

    st.markdown(
        '<div style="border-radius:12px; overflow:hidden; border:1px solid var(--border);">'
        '<table style="width:100%; border-collapse:collapse; background:var(--bg);">'
        f'<thead><tr>{entetes}</tr></thead><tbody>{lignes_html}</tbody>'
        '</table></div>',
        unsafe_allow_html=True
    )

    # === Classement detaille (uniquement si N>=3) ===
    if len(labels_dispo) >= 3:
        st.markdown('<div class="qt-section-title">Classement</div>',
                    unsafe_allow_html=True)
        for idx, label in enumerate(classement):
            ecart_vs_premier = perfs[label] - perfs[classement[0]]
            suffixe = ("" if idx == 0
                       else f" · {ecart_vs_premier:+.2f} pts vs 1er")
            st.markdown(
                f'<div style="padding:12px 20px; margin:8px 0; border-radius:8px; '
                f'background:rgba(99,102,241,0.08); border-left:4px solid #6366f1;">'
                f'<strong>{_libelle_classement(idx)} · Scénario {label}</strong> '
                f'— performance {perfs[label]:+.2f}%{suffixe}</div>',
                unsafe_allow_html=True
            )

    # === Export CSV ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Exporter</div>', unsafe_allow_html=True)
    st.caption("Une colonne par scénario : valeur quotidienne du portefeuille en euros, "
               "alignée sur le même axe temporel pour comparaison directe dans Excel.")
    csv_bytes = generer_csv_comparaison(simulations, poids, cap)
    st.download_button(
        label=f"📊 Télécharger la comparaison ({len(labels_dispo)} scénarios, CSV)",
        data=csv_bytes,
        file_name=f"quant_terminal_comparaison_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
        key="compare_csv_dl",
    )
