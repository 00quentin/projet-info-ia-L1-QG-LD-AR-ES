"""
pages/backtest.py
=================
Onglets pour le mode Backtest historique.
- render_page_backtest_dashboard : équivalent du dashboard mais avec données réelles
- render_page_backtest_detail : évolution portefeuille + alpha vs benchmark
"""

from datetime import datetime
import pandas as pd
import streamlit as st

from config import NOM_AFFICHAGE
from core.metrics import calculer_metriques_risque
from core.portfolio import calculer_poids, construire_allocations_finales
from components.charts import (
    fig_courbes_categorie, construire_graphiques_par_categorie,
    fig_heatmap_performance, fig_evolution_portefeuille, html_metriques_jauges,
)
from components.empty_states import render_empty_backtest
from components.notifications import notify_warn, notify_error, notify_success
from ia_bot import generer_rapport_complet_ia
from pdf_generator import generer_rapport_pdf
from logger import get_logger

log = get_logger("page_backtest")


def render_page_backtest_dashboard():
    """Dashboard pour le mode Backtest (données réelles Yahoo)."""
    if st.session_state.backtest_data is None:
        render_empty_backtest()
        return

    bt = st.session_state.backtest_data
    params = st.session_state.params_sim
    df = bt["df"]

    # === Bandeau d'info ===
    st.markdown(f'<div class="qt-callout"><strong>Backtest : {bt["evenement"]}</strong><br>'
                f'<span style="font-size:0.9em;">{bt["description"]}<br>'
                f'Période : {bt["date_debut"]} → {bt["date_fin"]} · {len(bt["df"])} jours de cotation</span></div>',
                unsafe_allow_html=True)

    if bt["actifs_indisponibles"]:
        noms_indispo = [NOM_AFFICHAGE.get(a, a) for a in bt["actifs_indisponibles"]]
        notify_warn(f"Actifs indisponibles à cette époque : {', '.join(noms_indispo)}")

    # === Métriques de risque ===
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    valeur_port = pd.Series(0.0, index=df.index)
    for sk, pct in poids.items():
        if sk in df.columns:
            valeur_port += pct * (df[sk] / df[sk].iloc[0]) * params["capital"]
    metriques = calculer_metriques_risque(valeur_port)

    st.markdown('<div class="qt-section-title">Métriques de risque (données réelles)</div>',
                unsafe_allow_html=True)
    st.markdown(html_metriques_jauges(metriques), unsafe_allow_html=True)

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)

    # === Graphiques par catégorie ===
    df_norm = (df / df.iloc[0]) * 100
    df_norm.columns = [NOM_AFFICHAGE.get(c, c) for c in df_norm.columns]

    graphiques = construire_graphiques_par_categorie(df_norm, bt["actifs_disponibles"])
    for i in range(0, len(graphiques), 2):
        cols = st.columns(2)
        for j, (titre_cat, actifs_dispo) in enumerate(graphiques[i:i+2]):
            with cols[j]:
                fig = fig_courbes_categorie(
                    titre_cat, actifs_dispo, df_norm,
                    suffixe_titre=" · Données réelles"
                )
                st.plotly_chart(fig, use_container_width=True, key=f"bt_cat_{titre_cat}")

    # === Heatmap ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    fig_bar = fig_heatmap_performance(bt["perf_df"], titre="Performance réelle par actif")
    st.plotly_chart(fig_bar, use_container_width=True, key="bt_heatmap")

    # === PDF ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Exporter le rapport</div>',
                unsafe_allow_html=True)
    st.caption("Le rapport PDF inclut une analyse approfondie rédigée par l'analyste IA.")

    res_bt = {
        "scenario": f"Backtest : {bt['evenement']} — {bt['description']}",
        "chocs_ia": {
            "explication_courte": f"Période réelle : {bt['date_debut']} → {bt['date_fin']}",
            "macro": {"inflation": 0, "taux_directeurs": 0},
            "evenement_reference": bt["evenement"]
        },
        "perf_df": bt["perf_df"],
        "perf": bt["perf"],
    }
    params_bt = {**params, "duree": len(bt["df"]), "mc": False, "prix_reels": True, "calib": True}
    allocs_bt, valeur_fin_bt = construire_allocations_finales(
        bt["perf"], poids, params["capital"]
    )

    if st.button("🔬 Préparer le rapport PDF complet", key="bt_prep_pdf",
                 use_container_width=True):
        st.session_state["bt_pdf_ready"] = False
        with st.spinner("L'analyste IA rédige son rapport approfondi... (15-30 secondes)"):
            try:
                analyse_senior = generer_rapport_complet_ia(
                    scenario=res_bt["scenario"], chocs_ia=res_bt["chocs_ia"],
                    perf_par_actif=bt["perf_df"], metriques=metriques,
                    valeur_initiale=params["capital"], valeur_finale=valeur_fin_bt,
                    profil=params["profil"]
                )
                pdf_bytes = generer_rapport_pdf(
                    simu=res_bt, params=params_bt, metriques=metriques,
                    allocations_finales=allocs_bt, valeur_finale=valeur_fin_bt,
                    type_rapport="Backtest",
                    analyse_senior=analyse_senior
                )
                st.session_state["bt_pdf_bytes"] = pdf_bytes
                st.session_state["bt_pdf_ready"] = True
                log.info("PDF backtest généré (%d bytes)", len(pdf_bytes))
            except Exception as e:
                log.error("Erreur génération PDF backtest : %s", e, exc_info=True)
                notify_error(f"Génération PDF impossible : {e}")

    if st.session_state.get("bt_pdf_ready", False):
        notify_success("Rapport prêt — cliquez ci-dessous pour le télécharger.")
        st.download_button(
            label="📄 Télécharger le rapport PDF",
            data=st.session_state["bt_pdf_bytes"],
            file_name=f"quant_terminal_backtest_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="bt_pdf_dl"
        )


def render_page_backtest_detail():
    """Onglet Backtest : évolution du portefeuille avec benchmark + alpha."""
    if st.session_state.backtest_data is None:
        render_empty_backtest()
        return

    bt = st.session_state.backtest_data
    params = st.session_state.params_sim
    df = bt["df"]
    cap = params["capital"]
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])

    st.markdown(f'<div class="qt-section-title">Évolution du portefeuille — {bt["evenement"]}</div>',
                unsafe_allow_html=True)
    st.caption("Comment votre portefeuille aurait réellement évolué pendant cette crise.")

    # Calcul de la valeur jour par jour
    valeur_port = pd.Series(0.0, index=df.index)
    for sk, pct in poids.items():
        if sk in df.columns:
            valeur_port += pct * (df[sk] / df[sk].iloc[0]) * cap

    benchmark = None
    if "S&P 500" in df.columns:
        benchmark = (df["S&P 500"] / df["S&P 500"].iloc[0]) * cap

    fig = fig_evolution_portefeuille(valeur_port, cap, benchmark)
    st.plotly_chart(fig, use_container_width=True, key="bt_evolution")

    # Bilan
    valeur_finale = float(valeur_port.iloc[-1])
    gains = valeur_finale - cap
    perf_g = (gains / cap) * 100 if cap > 0 else 0

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Capital initial", f"{cap:,.0f} €")
    c2.metric("Valeur finale", f"{valeur_finale:,.2f} €", f"{gains:,.0f} €")
    c3.metric("Performance globale", f"{perf_g:+.2f} %")

    # Alpha vs benchmark
    if benchmark is not None:
        perf_bench = (float(benchmark.iloc[-1]) - cap) / cap * 100
        alpha = perf_g - perf_bench
        couleur_alpha = "#2f855a" if alpha >= 0 else "#c53030"
        st.markdown(
            f'<div style="background:{couleur_alpha}; color:white; padding:18px 24px; '
            f'border-radius:10px; text-align:center; margin:24px 0; font-size:1.05em;">'
            f'Votre alpha vs S&P 500 : <strong>{alpha:+.2f} points</strong>'
            f' ({"surperformance" if alpha >= 0 else "sous-performance"})</div>',
            unsafe_allow_html=True
        )

    # Détail par actif
    st.markdown('<div class="qt-section-title">Performance par actif</div>',
                unsafe_allow_html=True)
    cols_port = st.columns(4)
    i = 0
    for sk, pct in poids.items():
        if sk in df.columns:
            nom = NOM_AFFICHAGE.get(sk, sk)
            rend = bt["perf"].get(sk, 0) / 100
            montant = cap * pct
            final = montant * (1 + rend)
            with cols_port[i % 4]:
                st.metric(f"{nom} ({pct*100:.1f}%)",
                          f"{final:,.0f} €", f"{rend*100:+.2f}%")
            i += 1