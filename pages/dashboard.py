"""
pages/dashboard.py
==================
Onglet Dashboard pour le mode Simulation prospective.
"""

from datetime import datetime
import pandas as pd
import streamlit as st

from config import NOM_AFFICHAGE, COULEUR_PRIMAIRE
from core.metrics import calculer_metriques_risque
from core.portfolio import calculer_poids, construire_allocations_finales, calculer_valeur_portefeuille
from components.charts import (
    fig_courbes_categorie, construire_graphiques_par_categorie,
    fig_heatmap_performance, html_metriques_jauges,
)
from components.empty_states import render_empty_dashboard
from components.notifications import notify_error, notify_success
from ia_bot import generer_rapport_complet_ia
from pdf_generator import generer_rapport_pdf
from logger import get_logger

log = get_logger("page_dashboard")


def afficher_dashboard(res, params, key_prefix="main"):
    """Affiche le dashboard complet pour un résultat de simulation."""
    chocs = res["chocs_ia"]
    df = res["df"]
    mc = res["mc_data"]

    # === Badges (prix réels, calibration) ===
    badges = ""
    if params.get("prix_reels"):
        badges += '<span class="qt-live-badge">PRIX RÉELS</span>'
    if params.get("calib") and chocs.get("evenement_reference"):
        badges += f'<span class="qt-live-badge" style="background:#805ad5;">CALIBRÉ : {chocs["evenement_reference"]}</span>'
    if badges:
        st.markdown(f'<div style="margin-bottom:14px;">{badges}</div>', unsafe_allow_html=True)

    # === Macro IA ===
    col1, col2 = st.columns(2)
    col1.metric("Impact Inflation (Estimé)",
                f"{chocs.get('macro', {}).get('inflation', 0):+.2f} %")
    col2.metric("Taux Directeurs (Estimé)",
                f"{chocs.get('macro', {}).get('taux_directeurs', 0):+.2f} %")

    explication = chocs.get('explication_courte', 'Analyse non disponible.')
    st.markdown(
        f'<div class="qt-callout" style="margin-top:18px; line-height:1.6;">'
        f'<strong style="color:{COULEUR_PRIMAIRE}; font-size:1.05em;">📊 Analyse de l\'IA</strong><br><br>'
        f'<span style="font-size:0.97em;">{explication}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    # === Métriques de risque ===
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    valeur_port = calculer_valeur_portefeuille(df, poids, params["capital"])
    metriques = calculer_metriques_risque(valeur_port)

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Métriques de risque du portefeuille</div>',
                unsafe_allow_html=True)
    st.caption("Indicateurs utilisés par les gérants de fonds professionnels.")

    st.markdown(html_metriques_jauges(metriques), unsafe_allow_html=True)

    # === Graphiques par catégorie ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    df_norm = (df / df.iloc[0]) * 100
    df_norm.columns = [NOM_AFFICHAGE.get(c, c.replace("_", " ").replace("EUR USD", "EUR/USD"))
                        for c in df_norm.columns]

    mc_bas_norm = mc_haut_norm = None
    if mc is not None:
        mc_bas_norm = (mc["bas"] / df.iloc[0]) * 100
        mc_haut_norm = (mc["haut"] / df.iloc[0]) * 100
        mc_bas_norm.columns = df_norm.columns
        mc_haut_norm.columns = df_norm.columns

    graphiques = construire_graphiques_par_categorie(df_norm, params["actifs_sim"])
    suffixe = " · Monte-Carlo" if mc is not None else ""

    for i in range(0, len(graphiques), 2):
        cols = st.columns(2)
        for j, (titre_cat, actifs_dispo) in enumerate(graphiques[i:i+2]):
            with cols[j]:
                fig = fig_courbes_categorie(
                    titre_cat, actifs_dispo, df_norm,
                    mc_bas_norm, mc_haut_norm, suffixe
                )
                st.plotly_chart(fig, use_container_width=True,
                                key=f"{key_prefix}_cat_{titre_cat}")

    # === Heatmap performance ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    fig_bar = fig_heatmap_performance(res["perf_df"])
    st.plotly_chart(fig_bar, use_container_width=True, key=f"{key_prefix}_heatmap")

    # === Bouton PDF ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Exporter le rapport</div>', unsafe_allow_html=True)
    st.caption("Le rapport PDF inclut une analyse approfondie rédigée par l'analyste IA dans le style d'un professionnel institutionnel.")

    allocs, valeur_fin = construire_allocations_finales(res["perf"], poids, params["capital"])

    if st.button("🔬 Préparer le rapport PDF complet", key=f"{key_prefix}_prep_pdf",
                 use_container_width=True):
        st.session_state[f"{key_prefix}_pdf_ready"] = False
        with st.spinner("L'analyste IA rédige son rapport approfondi... (15-30 secondes)"):
            try:
                analyse_senior = generer_rapport_complet_ia(
                    scenario=res["scenario"], chocs_ia=res["chocs_ia"],
                    perf_par_actif=res["perf_df"], metriques=metriques,
                    valeur_initiale=params["capital"], valeur_finale=valeur_fin,
                    profil=params["profil"]
                )
                pdf_bytes = generer_rapport_pdf(
                    simu=res, params=params, metriques=metriques,
                    allocations_finales=allocs, valeur_finale=valeur_fin,
                    type_rapport="Simulation",
                    analyse_senior=analyse_senior
                )
                st.session_state[f"{key_prefix}_pdf_bytes"] = pdf_bytes
                st.session_state[f"{key_prefix}_pdf_ready"] = True
                log.info("PDF généré (key=%s, taille=%d bytes)", key_prefix, len(pdf_bytes))
            except Exception as e:
                log.error("Erreur génération PDF : %s", e, exc_info=True)
                notify_error(f"Génération PDF impossible : {e}")

    if st.session_state.get(f"{key_prefix}_pdf_ready", False):
        notify_success("Rapport prêt — cliquez ci-dessous pour le télécharger.")
        st.download_button(
            label="📄 Télécharger le rapport PDF",
            data=st.session_state[f"{key_prefix}_pdf_bytes"],
            file_name=f"quant_terminal_rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"{key_prefix}_pdf_dl"
        )


def render_page_dashboard():
    """Point d'entrée de la page Dashboard."""
    if st.session_state.simu_A is None:
        render_empty_dashboard()
        return

    if st.session_state.mode_comparaison and st.session_state.simu_B:
        sub_A, sub_B = st.tabs(["Scénario A", "Scénario B"])
        with sub_A:
            st.markdown(f'<div class="qt-callout"><strong>Scénario A :</strong> {st.session_state.simu_A["scenario"]}</div>',
                        unsafe_allow_html=True)
            afficher_dashboard(st.session_state.simu_A, st.session_state.params_sim, key_prefix="dash_A")
        with sub_B:
            st.markdown(f'<div class="qt-callout"><strong>Scénario B :</strong> {st.session_state.simu_B["scenario"]}</div>',
                        unsafe_allow_html=True)
            afficher_dashboard(st.session_state.simu_B, st.session_state.params_sim, key_prefix="dash_B")
    else:
        afficher_dashboard(st.session_state.simu_A, st.session_state.params_sim, key_prefix="dash_main")