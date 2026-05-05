"""
pages/dashboard.py
==================
Onglet Dashboard pour le mode Simulation prospective.
"""

from datetime import datetime
import pandas as pd
import streamlit as st

from config import NOM_AFFICHAGE, LABELS_SCENARIOS
from core.metrics import calculer_metriques_risque
from core.portfolio import calculer_poids, construire_allocations_finales, calculer_valeur_portefeuille
from core.export_csv import generer_csv_simulation
from core.risk_alerts import evaluer_alertes_risque
from components.charts import (
    fig_courbes_categorie, construire_graphiques_par_categorie,
    fig_heatmap_performance, html_metriques_jauges,
    fig_evolution_portefeuille,
)
from components.empty_states import render_empty_dashboard
from components.notifications import notify_error, notify_success, render_alerte_risque
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
        f'<strong style="color:var(--primary); font-size:1.05em;">📊 Analyse de l\'IA</strong><br><br>'
        f'<span style="font-size:0.97em;">{explication}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    # === Calibration historique : mix d'evenements + score de fiabilite ===
    if params.get("calib"):
        refs = chocs.get("references_historiques") or []
        fiab = chocs.get("fiabilite_calibration") or {}
        niveau = fiab.get("niveau", "moyenne")
        couleurs_fiab = {
            "elevee":  ("#2f855a", "Fiabilité élevée"),
            "moyenne": ("#d69e2e", "Fiabilité moyenne"),
            "faible":  ("#c53030", "Fiabilité faible"),
        }
        couleur, label = couleurs_fiab.get(niveau, couleurs_fiab["moyenne"])

        if refs:
            def _ligne_ref(r):
                nom = r.get("evenement", "?")
                annee = r.get("annee")
                titre = f"{nom} ({annee})" if annee else nom
                poids_pct = r.get("poids", 0)
                raison = r.get("raison", "")
                return (
                    f'<li style="margin-bottom:6px;">'
                    f'<strong>{titre}</strong>'
                    f' — poids <strong>{poids_pct:.0%}</strong>'
                    f'<br><span style="opacity:0.85; font-size:0.92em;">{raison}</span>'
                    f'</li>'
                )
            lignes_refs = "".join(_ligne_ref(r) for r in refs)
            html_refs = (
                f'<div class="qt-callout" style="margin-top:14px; border-left:4px solid {couleur};">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">'
                f'<strong style="color:var(--primary); font-size:1.02em;">🎯 Calibration historique (mix)</strong>'
                f'<span style="background:{couleur}; color:white; padding:3px 10px; border-radius:6px; '
                f'font-size:0.85em; font-weight:600;">{label}</span>'
                f'</div>'
                f'<ul style="margin:0; padding-left:20px;">{lignes_refs}</ul>'
            )
            if fiab.get("raison"):
                html_refs += (
                    f'<div style="margin-top:10px; font-size:0.88em; opacity:0.85; font-style:italic;">'
                    f'{fiab["raison"]}</div>'
                )
            html_refs += "</div>"
            st.markdown(html_refs, unsafe_allow_html=True)

    # === Métriques de risque ===
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    valeur_port = calculer_valeur_portefeuille(df, poids, params["capital"])
    metriques = calculer_metriques_risque(valeur_port)

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Métriques de risque du portefeuille</div>',
                unsafe_allow_html=True)
    st.caption("Indicateurs utilisés par les gérants de fonds professionnels.")

    st.markdown(html_metriques_jauges(metriques), unsafe_allow_html=True)

    # Alertes automatiques sur les metriques (drawdown severe, Sharpe negatif...)
    for alerte in evaluer_alertes_risque(metriques):
        render_alerte_risque(alerte.severite, alerte.titre, alerte.message)

    # === Évolution du portefeuille vs benchmark S&P 500 ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Évolution du portefeuille vs marché</div>',
                unsafe_allow_html=True)
    st.caption("Votre portefeuille comparé au S&P 500 sur la même période simulée. "
               "L'alpha mesure votre surperformance par rapport au marché.")

    cap = params["capital"]
    benchmark = None
    if "S&P 500" in df.columns:
        benchmark = (df["S&P 500"] / df["S&P 500"].iloc[0]) * cap

    fig_evo = fig_evolution_portefeuille(valeur_port, cap, benchmark)
    st.plotly_chart(fig_evo, use_container_width=True, key=f"{key_prefix}_evolution")

    if benchmark is not None:
        valeur_finale = float(valeur_port.iloc[-1])
        perf_p = (valeur_finale - cap) / cap * 100 if cap > 0 else 0
        perf_b = (float(benchmark.iloc[-1]) - cap) / cap * 100 if cap > 0 else 0
        alpha = perf_p - perf_b
        couleur_alpha = "#2f855a" if alpha >= 0 else "#c53030"
        st.markdown(
            f'<div style="background:{couleur_alpha}; color:white; padding:14px 20px; '
            f'border-radius:10px; text-align:center; margin:18px 0; font-size:1em;">'
            f'Alpha vs S&P 500 : <strong>{alpha:+.2f} points</strong>'
            f' ({"surperformance" if alpha >= 0 else "sous-performance"})'
            f'</div>',
            unsafe_allow_html=True
        )

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

    # === Exports ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Exporter</div>', unsafe_allow_html=True)
    st.caption("Le PDF contient une analyse rédigée par l'IA. Le CSV contient la série journalière brute (valeur du portefeuille + valeur de chaque poche en euros) pour ré-exploitation dans Excel ou Python.")

    allocs, valeur_fin = construire_allocations_finales(res["perf"], poids, params["capital"])

    csv_bytes = generer_csv_simulation(df, poids, params["capital"])
    st.download_button(
        label="📊 Télécharger les données (CSV)",
        data=csv_bytes,
        file_name=f"quant_terminal_donnees_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"{key_prefix}_csv_dl",
    )

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
    simulations = st.session_state.simulations
    labels_disponibles = [lab for lab in LABELS_SCENARIOS if simulations.get(lab) is not None]

    if not labels_disponibles:
        render_empty_dashboard()
        return

    if len(labels_disponibles) == 1:
        afficher_dashboard(simulations[labels_disponibles[0]],
                           st.session_state.params_sim, key_prefix="dash_main")
        return

    # Multi-scenarios : un sous-onglet par label
    sub_tabs = st.tabs([f"Scénario {lab}" for lab in labels_disponibles])
    for tab, label in zip(sub_tabs, labels_disponibles):
        with tab:
            res = simulations[label]
            st.markdown(
                f'<div class="qt-callout"><strong>Scénario {label} :</strong> {res["scenario"]}</div>',
                unsafe_allow_html=True
            )
            afficher_dashboard(res, st.session_state.params_sim,
                               key_prefix=f"dash_{label}")