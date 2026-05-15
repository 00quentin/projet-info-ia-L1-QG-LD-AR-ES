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
    fig_evolution_portefeuille, html_cartes_performance, _tip,
)
from components.empty_states import render_empty_dashboard
from components.notifications import notify_error, notify_success, render_alerte_risque
from ia_bot import generer_rapport_complet_ia
from pdf_generator import generer_rapport_pdf
from logger import get_logger

log = get_logger("page_dashboard")


def _section_tip(titre: str, aide: str) -> str:
    """Titre de section avec icône ℹ tooltip au hover."""
    return f'<div class="qt-section-title">{titre}{_tip(aide)}</div>'


def _render_hero_dashboard(res, params):
    """Hero TradingView : grande valeur finale + variation coloree + badges."""
    chocs = res["chocs_ia"]
    df = res["df"]
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    valeur_port = calculer_valeur_portefeuille(df, poids, params["capital"])
    valeur_finale = float(valeur_port.iloc[-1])
    capital = params["capital"]
    variation = valeur_finale - capital
    variation_pct = (variation / capital * 100) if capital > 0 else 0.0
    up = variation >= 0
    classe = "up" if up else "down"
    arrow = "▲" if up else "▼"

    # Formatage : separateur d'espaces, 2 decimales en EUR
    val_str = f"{valeur_finale:,.2f}".replace(",", " ").replace(".", ",")
    var_str = f"{abs(variation):,.2f}".replace(",", " ").replace(".", ",")
    pct_str = f"{abs(variation_pct):.2f}".replace(".", ",")

    # Badges contextuels
    badges_html = ""
    if params.get("prix_reels"):
        badges_html += '<span class="qt-dash-hero-chip qt-dash-hero-chip-live">● Prix réels</span>'
    if params.get("calib") and chocs.get("evenement_reference"):
        ref = chocs["evenement_reference"]
        badges_html += f'<span class="qt-dash-hero-chip qt-dash-hero-chip-calib">Calibré : {ref}</span>'
    if params.get("monte_carlo"):
        badges_html += '<span class="qt-dash-hero-chip qt-dash-hero-chip-mc">Monte-Carlo · 50 simulations</span>'

    st.markdown(
        f'<div class="qt-dash-hero">'
        f'<div class="qt-dash-hero-top">'
        f'<div class="qt-dash-hero-label">Valeur finale du portefeuille</div>'
        f'<div class="qt-dash-hero-chips">{badges_html}</div>'
        f'</div>'
        f'<div class="qt-dash-hero-row">'
        f'<span class="qt-dash-hero-value">{val_str}</span>'
        f'<span class="qt-dash-hero-unit">€</span>'
        f'<span class="qt-dash-hero-variation {classe}">'
        f'<span class="qt-dash-hero-arrow">{arrow}</span>'
        f'{var_str} € · {pct_str}%'
        f'</span>'
        f'</div>'
        f'<div class="qt-dash-hero-sub">'
        f'Capital initial : <strong>{capital:,.0f} €</strong>'.replace(",", " ")
        + f' &middot; Horizon : <strong>{len(df)} jours</strong>'
        + f' &middot; {len(params["actifs_sim"])} actifs'
        + '</div>'
        + '</div>',
        unsafe_allow_html=True
    )


def afficher_dashboard(res, params, key_prefix="main"):
    """Affiche le dashboard complet pour un résultat de simulation."""
    chocs = res["chocs_ia"]
    df = res["df"]
    mc = res["mc_data"]

    # === Hero TradingView : valeur finale + variation ===
    _render_hero_dashboard(res, params)

    # === Macro IA ===
    col1, col2 = st.columns(2)
    col1.metric("Impact Inflation (Estimé)",
                f"{chocs.get('macro', {}).get('inflation', 0):+.2f} %",
                help="Variation estimée du niveau général des prix suite au scénario. "
                     "Une inflation forte (> +5 %) érode le pouvoir d'achat, pénalise "
                     "les obligations et pousse souvent l'or à la hausse.")
    col2.metric("Taux Directeurs (Estimé)",
                f"{chocs.get('macro', {}).get('taux_directeurs', 0):+.2f} %",
                help="Variation estimée du taux fixé par les banques centrales (FED, BCE). "
                     "Une hausse renchérit le crédit et fait généralement baisser "
                     "actions ET obligations en même temps.")

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
            "elevee":  ("#16c784", "Fiabilité élevée"),
            "moyenne": ("#f59e0b", "Fiabilité moyenne"),
            "faible":  ("#ef454a", "Fiabilité faible"),
        }
        couleur, label = couleurs_fiab.get(niveau, couleurs_fiab["moyenne"])

        # Fallback : si l'IA n'a pas renvoye de mix mais juste un evenement
        # principal, on construit un mix degenere a 1 element pour eclairer
        # quand meme l'utilisateur (cas reponse cache ancienne ou IA legere).
        if not refs and chocs.get("evenement_reference"):
            refs = [{
                "evenement": chocs["evenement_reference"],
                "annee": None,
                "poids": 1.0,
                "raison": "Événement de référence unique (l'IA n'a pas renvoyé de mix pondéré).",
            }]

        # Si on a vraiment rien (ni mix, ni evenement), on affiche quand meme
        # le bloc avec un placeholder pour que l'utilisateur sache que la
        # calibration est active mais que l'IA a echoue a structurer la reponse.
        if not refs:
            st.markdown(
                '<div class="qt-callout" style="margin-top:14px; border-left:4px solid #f59e0b;">'
                '<strong style="color:#f59e0b;">⚠️ Calibration historique activée</strong><br>'
                '<span style="font-size:0.92em;">L\'IA n\'a pas extrait d\'événement de référence '
                'structuré pour ce scénario (réponse JSON incomplète). '
                'Réessaye avec une formulation un peu différente, ou décoche la calibration '
                'pour une projection libre.</span>'
                '</div>',
                unsafe_allow_html=True
            )
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

        # === Comparaison Calibree vs Libre ===
        chocs_libre = res.get("chocs_libre")
        if chocs_libre:
            st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
            st.markdown(_section_tip(
                "Calibrée vs estimation libre",
                "Calibrée = l'IA ancre ses chocs sur des crises historiques similaires "
                "(ex : 2008, COVID). Libre = projection pure sans contrainte. "
                "Un grand écart entre les deux = ce scénario est peu couvert par l'histoire."
            ), unsafe_allow_html=True)

            macro_c = chocs.get("macro", {}) or {}
            macro_l = chocs_libre.get("macro", {}) or {}
            actifs_c = chocs.get("actifs", {}) or {}
            actifs_l = chocs_libre.get("actifs", {}) or {}

            # Carte côte à côte Calibrée / Libre — HTML compact
            def _macro_val(v: float) -> str:
                col = "#16c784" if v >= 0 else "#ef454a"
                sign = "+" if v >= 0 else ""
                return (f'<span style="color:{col}; font-weight:700; '
                        f'font-size:1.35em;">{sign}{v:.2f}%</span>')

            def _macro_row(label: str, val: float) -> str:
                return (
                    f'<div style="display:flex; justify-content:space-between; '
                    f'align-items:center; padding:10px 0; '
                    f'border-bottom:1px solid var(--border);">'
                    f'<span style="font-size:0.88em; color:var(--text-muted);">{label}</span>'
                    f'{_macro_val(val)}</div>'
                )

            infl_c = macro_c.get("inflation", 0)
            taux_c = macro_c.get("taux_directeurs", 0)
            infl_l = macro_l.get("inflation", 0)
            taux_l = macro_l.get("taux_directeurs", 0)

            # Badge VS flottant entre les deux colonnes
            card_style = (
                'flex:1; padding:20px 24px; border-radius:14px; '
                'border:1px solid var(--border);'
            )
            label_style = (
                'font-size:0.72em; font-weight:700; text-transform:uppercase; '
                'letter-spacing:0.07em; margin-bottom:14px; '
                'display:flex; align-items:center; gap:6px;'
            )
            html_macro = (
                '<div style="display:flex; align-items:stretch; gap:0; '
                'margin-top:8px; position:relative;">'
                # Colonne Calibrée
                f'<div style="{card_style} background:rgba(139,92,246,0.07);">'
                f'<div style="{label_style} color:#8b5cf6;">🎯 Calibrée — ancrage historique</div>'
                + _macro_row("Inflation", infl_c)
                + _macro_row("Taux directeurs", taux_c) +
                '</div>'
                # Badge VS centré
                '<div style="display:flex; align-items:center; justify-content:center; '
                'padding:0 14px; flex-shrink:0;">'
                '<div style="background:var(--card); border:1px solid var(--border); '
                'border-radius:999px; padding:6px 10px; font-size:0.72em; font-weight:800; '
                'color:var(--text-muted); letter-spacing:0.04em;">VS</div>'
                '</div>'
                # Colonne Libre
                f'<div style="{card_style} background:rgba(59,130,246,0.07);">'
                f'<div style="{label_style} color:#3b82f6;">🤖 Libre — projection IA pure</div>'
                + _macro_row("Inflation", infl_l)
                + _macro_row("Taux directeurs", taux_l) +
                '</div>'
                '</div>'
            )
            st.markdown(html_macro, unsafe_allow_html=True)

            # Tableau comparatif des actifs : on prend les actifs du portefeuille
            # uniquement (sinon trop bruyant), et on calcule l'ecart absolu en points.
            actifs_compa = [a for a in params["actifs_sim"] if a in actifs_c or a in actifs_l]
            if actifs_compa:
                lignes = []
                for a in actifs_compa:
                    v_c = actifs_c.get(a, 0) * 100
                    v_l = actifs_l.get(a, 0) * 100
                    ecart = v_l - v_c
                    nom = NOM_AFFICHAGE.get(a, a.replace("_", " "))
                    lignes.append({"Actif": nom, "Calibrée (%)": v_c,
                                    "Libre (%)": v_l, "Écart (pts)": ecart})
                df_compa = pd.DataFrame(lignes)
                df_compa = df_compa.reindex(
                    df_compa["Écart (pts)"].abs().sort_values(ascending=False).index
                )
                # Tableau HTML custom : plus lisible que st.dataframe styled
                def _chip_pct(val: float, ref_color: str = "var(--accent)") -> str:
                    col = "#16c784" if val >= 0 else "#ef454a"
                    sign = "+" if val >= 0 else ""
                    return (f'<span style="display:inline-block; padding:2px 9px; '
                            f'border-radius:6px; background:{"rgba(22,199,132,0.12)" if val >= 0 else "rgba(239,69,74,0.12)"}; '
                            f'color:{col}; font-weight:600; font-size:0.9em;">'
                            f'{sign}{val:.2f}%</span>')

                def _chip_ecart(val: float) -> str:
                    abs_v = abs(val)
                    if abs_v < 5:
                        bg, fg = "rgba(22,199,132,0.13)", "#16c784"
                    elif abs_v < 15:
                        bg, fg = "rgba(245,158,11,0.13)", "#f59e0b"
                    else:
                        bg, fg = "rgba(239,69,74,0.13)", "#ef454a"
                    sign = "+" if val >= 0 else ""
                    return (f'<span style="display:inline-block; padding:2px 9px; '
                            f'border-radius:6px; background:{bg}; color:{fg}; '
                            f'font-weight:700; font-size:0.9em;">{sign}{val:.1f} pts</span>')

                lignes_html = ""
                for _, row in df_compa.iterrows():
                    lignes_html += (
                        f'<tr>'
                        f'<td style="padding:10px 14px; font-weight:500; '
                        f'color:var(--text); border-bottom:1px solid var(--border);">'
                        f'{row["Actif"]}</td>'
                        f'<td style="padding:10px 14px; text-align:right; '
                        f'border-bottom:1px solid var(--border);">'
                        f'{_chip_pct(row["Calibrée (%)"])}</td>'
                        f'<td style="padding:10px 14px; text-align:right; '
                        f'border-bottom:1px solid var(--border);">'
                        f'{_chip_pct(row["Libre (%)"])}</td>'
                        f'<td style="padding:10px 14px; text-align:right; '
                        f'border-bottom:1px solid var(--border);">'
                        f'{_chip_ecart(row["Écart (pts)"])}</td>'
                        f'</tr>'
                    )

                header_style = (
                    'padding:9px 14px; font-size:0.78em; font-weight:600; '
                    'text-transform:uppercase; letter-spacing:0.05em; '
                    'color:var(--text-muted); background:var(--card); '
                    'border-bottom:2px solid var(--border);'
                )
                table_html = (
                    '<div style="margin-top:16px; border-radius:12px; overflow:hidden; '
                    'border:1px solid var(--border);">'
                    '<table style="width:100%; border-collapse:collapse; '
                    'background:var(--bg);">'
                    '<thead><tr>'
                    f'<th style="{header_style} text-align:left;">Actif</th>'
                    f'<th style="{header_style} text-align:right;">Calibrée</th>'
                    f'<th style="{header_style} text-align:right;">Libre</th>'
                    f'<th style="{header_style} text-align:right;">Écart</th>'
                    '</tr></thead>'
                    f'<tbody>{lignes_html}</tbody>'
                    '</table></div>'
                )
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown(
                    '<div style="margin-top:10px; padding:10px 14px; '
                    'background:rgba(99,102,241,0.06); border-radius:8px; '
                    'border-left:3px solid var(--accent); '
                    'font-size:0.84em; color:var(--text-muted);">'
                    '💡 <strong>Écart &lt; 5 pts</strong> = l\'ancrage historique confirme la projection. '
                    '<strong>Écart &gt; 15 pts</strong> = scénario peu couvert par l\'histoire.'
                    '</div>',
                    unsafe_allow_html=True
                )

    # === Métriques de risque ===
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    valeur_port = calculer_valeur_portefeuille(df, poids, params["capital"])
    metriques = calculer_metriques_risque(valeur_port)

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown(_section_tip(
        "Métriques de risque du portefeuille",
        "4 indicateurs utilisés par les gérants de fonds professionnels pour "
        "évaluer le risque d'un portefeuille, indépendamment de sa performance absolue. "
        "Hover sur le i de chaque jauge pour comprendre chaque métrique."
    ), unsafe_allow_html=True)

    st.markdown(html_metriques_jauges(metriques), unsafe_allow_html=True)

    # Alertes automatiques sur les metriques (drawdown severe, Sharpe negatif...)
    for alerte in evaluer_alertes_risque(metriques):
        render_alerte_risque(alerte.severite, alerte.titre, alerte.message)

    # === Évolution du portefeuille vs benchmarks ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown(_section_tip(
        "Évolution du portefeuille vs marché",
        "Simulation jour par jour de votre portefeuille comparé aux indices de référence. "
        "Courbe au-dessus du S&P 500 = vous surperformez le marché sur cette période."
    ), unsafe_allow_html=True)

    cap = params["capital"]
    valeur_finale = float(valeur_port.iloc[-1])
    perf_p = (valeur_finale - cap) / cap * 100 if cap > 0 else 0

    benchmark_sp = None
    if "S&P 500" in df.columns:
        benchmark_sp = (df["S&P 500"] / df["S&P 500"].iloc[0]) * cap

    benchmark_msci = None
    if "MSCI_World" in df.columns:
        benchmark_msci = (df["MSCI_World"] / df["MSCI_World"].iloc[0]) * cap

    fig_evo = fig_evolution_portefeuille(
        valeur_port, cap, benchmark_sp,
        benchmarks_extra={"MSCI World": benchmark_msci} if benchmark_msci is not None else None,
    )
    st.plotly_chart(fig_evo, use_container_width=True, key=f"{key_prefix}_evolution",
                    config={"scrollZoom": False})

    # Cartes de comparaison des performances côte à côte (helper partagé)
    items_perf = [{"nom": "Mon portefeuille", "valeur_finale": valeur_finale,
                   "emoji": "💼", "principal": True}]
    if benchmark_sp is not None:
        items_perf.append({"nom": "S&P 500", "emoji": "🇺🇸",
                           "valeur_finale": float(benchmark_sp.iloc[-1])})
    if benchmark_msci is not None:
        items_perf.append({"nom": "MSCI World", "emoji": "🌍",
                           "valeur_finale": float(benchmark_msci.iloc[-1])})
    st.markdown(html_cartes_performance(items_perf, cap), unsafe_allow_html=True)

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
                                key=f"{key_prefix}_cat_{titre_cat}",
                                config={"scrollZoom": False})

    # === Heatmap performance ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown(_section_tip(
        "Performance par actif",
        "Gain ou perte simulée de chaque actif sur l'horizon. "
        "Vert = actif gagnant dans ce scénario, rouge = actif perdant. "
        "Trié du plus faible au plus fort pour repérer immédiatement les points faibles."
    ), unsafe_allow_html=True)
    fig_bar = fig_heatmap_performance(res["perf_df"])
    st.plotly_chart(fig_bar, use_container_width=True, key=f"{key_prefix}_heatmap",
                    config={"scrollZoom": False})

    # === Exports ===
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown(
        '<div class="qt-section-title">Exporter les résultats</div>'
        '<div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.18); '
        'border-radius:10px; padding:12px 16px; margin-bottom:16px; font-size:0.88em; '
        'color:var(--text-muted); line-height:1.6;">'
        '📊 <strong>CSV</strong> — série journalière brute (valeur portefeuille + chaque poche en €). '
        'Idéal pour Excel ou Python.<br>'
        '📄 <strong>PDF</strong> — rapport complet rédigé par l\'IA avec analyse, métriques et recommandations.'
        '</div>',
        unsafe_allow_html=True
    )

    allocs, valeur_fin = construire_allocations_finales(res["perf"], poids, params["capital"])

    csv_bytes = generer_csv_simulation(df, poids, params["capital"])
    st.download_button(
        label="📊 Télécharger les données (CSV)",
        data=csv_bytes,
        file_name=f"quant_terminal_donnees_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary",
        key=f"{key_prefix}_csv_dl",
    )

    if st.button("Préparer le rapport PDF", key=f"{key_prefix}_prep_pdf",
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
        res = simulations[labels_disponibles[0]]
        st.markdown(
            f'<div class="qt-callout"><strong>Scénario :</strong> {res["scenario"]}</div>',
            unsafe_allow_html=True
        )
        afficher_dashboard(res, st.session_state.params_sim, key_prefix="dash_main")
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