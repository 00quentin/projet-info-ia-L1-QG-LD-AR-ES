"""
components/charts.py
====================
Fabrique de graphiques Plotly réutilisables.
"""

from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import CATEGORIES_GRAPHIQUES, NOM_AFFICHAGE, HAUTEUR_GRAPHIQUE


# === THÈME PLOTLY UNIFIÉ ============================================
# Palette alignée sur les design tokens (cf. components/styling.py).
# Si tu changes ces hex, change aussi les --blue/--teal correspondants.
QT_PALETTE = [
    "#1a365d",  # blue-700  (primary)
    "#319795",  # teal-500  (accent)
    "#d69e2e",  # warn-500
    "#805ad5",  # violet
    "#2f855a",  # success-500
    "#c53030",  # danger-500
    "#2c5282",  # blue-600
    "#4a5568",  # gray-600
]


def _is_dark() -> bool:
    """Retourne True si le mode sombre est actif (defaut False)."""
    try:
        return bool(st.session_state.get("dark_mode", False))
    except Exception:
        return False


def get_theme_colors() -> dict:
    """
    Retourne un dict de couleurs adapte au mode (clair/sombre) en cours.
    A utiliser dans les fonctions de chart pour que tout texte/axe reste lisible.
    """
    if _is_dark():
        return {
            "text":         "#e2e8f0",  # gray-200 — bien lisible sur fond sombre
            "text_strong":  "#f7fafc",  # gray-50
            "title":        "#90cdf4",  # blue-200 — primary clair
            "axis":         "#cbd5e0",  # gray-300
            "grid":         "rgba(226,232,240,0.14)",
            "annot":        "#a0aec0",
            "hover_bg":     "rgba(26,32,44,0.96)",   # gray-800
            "hover_border": "#4fd1c5",                # teal-300
            "pie_border":   "#1a202c",                # gray-800
        }
    return {
        "text":         "#2d3748",
        "text_strong":  "#171923",
        "title":        "#1a365d",
        "axis":         "#a0aec0",
        "grid":         "rgba(160,174,192,0.18)",
        "annot":        "#718096",
        "hover_bg":     "rgba(255,255,255,0.96)",
        "hover_border": "#319795",
        "pie_border":   "#ffffff",
    }


# Aliases retro-compat (ne plus utiliser pour les nouveaux charts)
QT_GRID    = "rgba(160,174,192,0.18)"
QT_AXIS    = "#a0aec0"
QT_TEXT    = "#2d3748"
QT_TITLE   = "#1a365d"
QT_HOVER_BG     = "rgba(255,255,255,0.96)"
QT_HOVER_BORDER = "#319795"


def apply_qt_theme(
    fig: go.Figure,
    *,
    height: Optional[int] = None,
    show_legend: bool = True,
    legend_bottom: bool = True,
) -> go.Figure:
    """
    Applique le thème Quant Terminal à une figure Plotly :
    police Inter, axes/grille discrets, hover unifié, marges cohérentes.
    Couleurs adaptees au mode (clair/sombre) en cours.

    À appeler en fin de construction de figure, après update_layout local.
    """
    c = get_theme_colors()
    fig.update_layout(
        template="plotly_white" if not _is_dark() else "plotly_dark",
        font=dict(family="Inter, -apple-system, sans-serif",
                  color=c["text"], size=12),
        # title_font seul sans title.text provoque un "undefined" dans Plotly JS.
        # On force title.text="" pour éviter ce bug.
        title=dict(text="", font=dict(family="Inter, sans-serif",
                                      color=c["title"], size=15)),
        legend_font=dict(color=c["text"], size=11),
        colorway=QT_PALETTE,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        # Marge basse plus large pour eviter que le titre x se chevauche avec la legende
        margin=dict(l=12, r=12, t=46, b=110 if legend_bottom else 50),
        hoverlabel=dict(
            bgcolor=c["hover_bg"],
            bordercolor=c["hover_border"],
            font=dict(family="Inter, sans-serif", color=c["text"], size=12),
        ),
        hovermode="x unified",
        showlegend=show_legend,
    )
    if height is not None:
        fig.update_layout(height=height)
    if show_legend and legend_bottom:
        fig.update_layout(legend=dict(
            orientation="h", yanchor="top", y=-0.32,
            xanchor="center", x=0.5,
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            font=dict(size=11, color=c["text"]),
        ))
    fig.update_xaxes(
        showgrid=True, gridcolor=c["grid"], gridwidth=1,
        zeroline=False, linecolor=c["axis"], linewidth=1,
        ticks="outside", tickcolor=c["axis"],
        tickfont=dict(size=11, color=c["text"]),
        title_font=dict(size=12, color=c["text"]),
        title_standoff=18,
        automargin=True,
        # Crosshair TradingView : ligne verticale au survol
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikecolor=c["axis"], spikethickness=1, spikedash="dot",
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=c["grid"], gridwidth=1,
        zeroline=False, linecolor=c["axis"], linewidth=1,
        ticks="outside", tickcolor=c["axis"],
        tickfont=dict(size=11, color=c["text"]),
        title_font=dict(size=12, color=c["text"]),
        title_standoff=14,
        automargin=True,
        # Crosshair TradingView : ligne horizontale au survol
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikecolor=c["axis"], spikethickness=1, spikedash="dot",
    )
    return fig


def fig_courbes_categorie(
    titre_cat: str,
    actifs_dispo: List[str],
    df_norm: pd.DataFrame,
    mc_bas_norm: Optional[pd.DataFrame] = None,
    mc_haut_norm: Optional[pd.DataFrame] = None,
    suffixe_titre: str = "",
) -> go.Figure:
    """Crée un graphique multi-lignes pour une catégorie d'actifs."""
    fig = go.Figure()

    for idx, actif in enumerate(actifs_dispo):
        col_c = QT_PALETTE[idx % len(QT_PALETTE)]
        # Bande Monte-Carlo si fournie
        if mc_bas_norm is not None and mc_haut_norm is not None:
            fig.add_trace(go.Scatter(
                x=df_norm.index, y=mc_haut_norm[actif],
                mode='lines', line=dict(width=0),
                showlegend=False, hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=df_norm.index, y=mc_bas_norm[actif],
                mode='lines', line=dict(width=0), fill='tonexty',
                fillcolor=f'rgba({int(col_c[1:3],16)},{int(col_c[3:5],16)},{int(col_c[5:7],16)},0.12)',
                showlegend=False, hoverinfo='skip'
            ))
        # Ligne médiane
        fig.add_trace(go.Scatter(
            x=df_norm.index, y=df_norm[actif],
            mode='lines', name=actif,
            line=dict(color=col_c, width=2.4, shape="spline", smoothing=0.6),
            hovertemplate="<b>%{fullData.name}</b><br>Base 100 : %{y:.2f}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=titre_cat + suffixe_titre),
        xaxis_title="Jours de cotation",
        yaxis_title="Évolution (Base 100)",
    )
    return apply_qt_theme(fig, height=HAUTEUR_GRAPHIQUE)


def construire_graphiques_par_categorie(
    df_norm: pd.DataFrame,
    actifs_disponibles_keys: List[str],
) -> List:
    """Liste les (titre_cat, [noms_affichage]) pour chaque catégorie présente."""
    graphiques = []
    for titre_cat, sim_keys_cat in CATEGORIES_GRAPHIQUES.items():
        actifs_dispo = [NOM_AFFICHAGE.get(sk, sk)
                        for sk in sim_keys_cat if sk in actifs_disponibles_keys]
        actifs_dispo = [a for a in actifs_dispo if a in df_norm.columns]
        if actifs_dispo:
            graphiques.append((titre_cat, actifs_dispo))
    return graphiques


def fig_heatmap_performance(perf_df: pd.DataFrame, titre: str = "Performance par actif") -> go.Figure:
    """Crée le graphique horizontal de performance par actif (couleurs nettes)."""
    c = get_theme_colors()
    # Couleur par signe : vert sature pour gains, rouge sature pour pertes.
    couleurs = [
        "#2f855a" if v >= 0 else "#c53030"
        for v in perf_df["Performance (%)"]
    ]
    # On pre-formate les valeurs pour le hover : evite les 20 decimales
    # quand plotly stringifie les floats numpy bruts.
    perfs_formatees = [f"{v:+.2f}%" for v in perf_df["Performance (%)"]]
    fig = go.Figure(go.Bar(
        x=perf_df["Performance (%)"],
        y=perf_df["Actif"],
        orientation='h',
        cliponaxis=False,
        marker=dict(
            color=couleurs,
            line=dict(color=c["pie_border"], width=1),
        ),
        customdata=perfs_formatees,
        hovertemplate="<b>%{y}</b><br>Performance : %{customdata}<extra></extra>",
    ))
    fig.update_layout(title=dict(text=titre))

    # Pas de labels sur les barres : la valeur s'affiche au survol via hovertemplate.
    # Marge minime sur l'axe X pour aerer le rendu.
    if len(perf_df) > 0:
        vmin = float(perf_df["Performance (%)"].min())
        vmax = float(perf_df["Performance (%)"].max())
        amplitude = max(abs(vmin), abs(vmax), 1.0)
        marge = amplitude * 0.06
        fig.update_xaxes(range=[min(0, vmin) - marge, max(0, vmax) + marge])

    apply_qt_theme(
        fig,
        height=max(380, 36 * len(perf_df) + 100),
        show_legend=False,
        legend_bottom=False,
    )
    # Ligne verticale a 0 pour la lisibilite
    fig.add_vline(x=0, line_color=c["axis"], line_width=1)
    fig.update_layout(coloraxis_showscale=False, bargap=0.32)
    return fig


def fig_evolution_portefeuille(
    valeur_port: pd.Series,
    capital: float,
    benchmark: Optional[pd.Series] = None,
    titre_benchmark: str = "S&P 500 (benchmark)",
    benchmarks_extra: Optional[Dict[str, pd.Series]] = None,
) -> go.Figure:
    """Evolution du portefeuille vs un ou plusieurs benchmarks, style TradingView.

    benchmark       : courbe principale (S&P 500 en pointillés gris)
    benchmarks_extra: dict {nom: Series} pour benchmarks additionnels (MSCI World…)
    """
    fig = go.Figure()

    # Couleur dynamique : vert si performance positive, rouge sinon
    valeur_finale = float(valeur_port.iloc[-1])
    up = valeur_finale >= capital
    couleur_courbe = "#16c784" if up else "#ef454a"
    r = int(couleur_courbe[1:3], 16)
    g = int(couleur_courbe[3:5], 16)
    b = int(couleur_courbe[5:7], 16)

    # Calcul du range Y : zoom sur les données réelles, pas depuis 0.
    # Sans ça, un portefeuille à 8k-10k laisse 80% du graphique vide.
    all_vals = list(valeur_port)
    if benchmark is not None:
        all_vals += list(benchmark)
    ymin = min(all_vals)
    ymax = max(all_vals)
    marge = (ymax - ymin) * 0.15 if ymax > ymin else ymax * 0.05
    y_range_min = ymin - marge
    y_range_max = ymax + marge * 0.5

    # Fill style TradingView : trace de sol invisible pour que le fill
    # parte du bas de la zone visible (pas de y=0 qui gaspille l'espace).
    fig.add_trace(go.Scatter(
        x=valeur_port.index,
        y=[y_range_min] * len(valeur_port),
        mode="lines", line_width=0,
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=valeur_port.index, y=valeur_port,
        name="Portefeuille",
        mode="lines",
        line=dict(color=couleur_courbe, width=2.5, shape="spline", smoothing=0.4),
        fill="tonexty",
        fillcolor=f"rgba({r},{g},{b},0.15)",
        hovertemplate="<b>Portefeuille</b><br>%{y:,.0f} €<extra></extra>",
    ))
    if benchmark is not None:
        fig.add_trace(go.Scatter(
            x=benchmark.index, y=benchmark,
            name=titre_benchmark,
            mode="lines",
            line=dict(color="#94a3b8", width=1.8, dash="dot"),
            hovertemplate=f"<b>{titre_benchmark}</b><br>%{{y:,.0f}} €<extra></extra>",
        ))
    # Benchmarks supplémentaires (ex: MSCI World) en tirets colorés
    _extra_colors = ["#f59e0b", "#8b5cf6", "#06b6d4"]
    for idx, (nom_bm, serie_bm) in enumerate((benchmarks_extra or {}).items()):
        col_bm = _extra_colors[idx % len(_extra_colors)]
        fig.add_trace(go.Scatter(
            x=serie_bm.index, y=serie_bm,
            name=nom_bm,
            mode="lines",
            line=dict(color=col_bm, width=1.6, dash="dashdot"),
            hovertemplate=f"<b>{nom_bm}</b><br>%{{y:,.0f}} €<extra></extra>",
        ))
    c = get_theme_colors()
    fig.add_hline(
        y=capital, line_dash="dash", line_color=c["axis"], line_width=1,
        annotation_text=f"Capital initial : {capital:,.0f} €",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color=c["annot"]),
    )
    # Crosshair style TradingView : ligne verticale au survol
    fig.update_xaxes(
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikecolor=c["axis"], spikethickness=1, spikedash="dot",
    )
    fig.update_yaxes(
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikecolor=c["axis"], spikethickness=1, spikedash="dot",
    )
    fig.update_layout(
        xaxis_title="Jours de cotation",
        yaxis_title="Valeur (€)",
        hovermode="x unified",
        yaxis=dict(range=[y_range_min, y_range_max]),
    )
    return apply_qt_theme(fig, height=400)


def html_metriques_jauges(metriques: Dict[str, float]) -> str:
    """Génère le HTML des 4 cartes métriques avec jauges circulaires SVG animées."""

    vol = metriques["vol_ann"]
    sharpe = metriques["sharpe"]
    dd = metriques["max_dd"]
    var = abs(metriques["var_95"])

    def _sharpe_meta(v):
        if v < 0:    return "#c53030", "Mauvais"
        if v < 1:    return "#d69e2e", "Passable"
        if v < 2:    return "#2f855a", "Bon"
        return           "#319795", "Excellent"

    def _vol_meta(v):
        if v < 10:   return "#319795", "Faible"
        if v < 20:   return "#2f855a", "Modérée"
        if v < 35:   return "#d69e2e", "Élevée"
        return           "#c53030", "Très élevée"

    def _dd_meta(v):
        if v < 10:   return "#2f855a", "Limité"
        if v < 25:   return "#d69e2e", "Modéré"
        return           "#c53030", "Sévère"

    def _var_meta(v):
        if v < 2:    return "#319795", "Faible"
        if v < 4:    return "#d69e2e", "Modérée"
        return           "#c53030", "Élevée"

    sc, sv = _sharpe_meta(sharpe)
    vc, vv = _vol_meta(vol)
    dc, dv = _dd_meta(dd)
    rc, rv = _var_meta(var)

    sharpe_pct = max(0.0, min(100.0, (sharpe + 1) / 4 * 100))
    vol_pct    = min(100.0, vol / 50 * 100)
    dd_pct     = min(100.0, dd  / 50 * 100)
    var_pct    = min(100.0, var /  8 * 100)

    def _gauge_svg(pct: float, couleur: str, valeur: str) -> str:
        """Demi-cercle SVG animé : arc qui se remplit depuis la gauche."""
        # Demi-cercle de rayon 38, circumférence pi*r = ~119.4
        circumf = 119.4
        offset = circumf * (1 - pct / 100)
        return (
            f'<svg class="qt-gauge-svg" viewBox="0 0 100 60" '
            f'xmlns="http://www.w3.org/2000/svg">'
            # Track de fond (gris)
            f'<path d="M 10 50 A 40 40 0 0 1 90 50" '
            f'fill="none" stroke="#e2e8f0" stroke-width="8" stroke-linecap="round"/>'
            # Arc rempli (couleur, animé)
            f'<path d="M 10 50 A 40 40 0 0 1 90 50" '
            f'fill="none" stroke="{couleur}" stroke-width="8" stroke-linecap="round" '
            f'stroke-dasharray="{circumf}" stroke-dashoffset="{circumf}" '
            f'style="animation: qtGaugeFill 1.2s cubic-bezier(0.65,0,0.35,1) forwards; '
            f'--gauge-offset:{offset:.1f};"/>'
            # Valeur centrale
            f'<text x="50" y="48" text-anchor="middle" font-size="14" '
            f'font-weight="700" fill="{couleur}" '
            f'font-family="Inter, sans-serif">{valeur}</text>'
            f'</svg>'
        )

    def _card(label, valeur_fmt, pct, couleur, verdict, aide):
        gauge = _gauge_svg(pct, couleur, valeur_fmt)
        return (
            f'<div class="qt-metric-gauge" style="--gauge-color:{couleur};" title="{aide}">'
            f'<div class="qt-metric-gauge-label">{label}</div>'
            f'<div class="qt-metric-gauge-circle">{gauge}</div>'
            f'<div class="qt-metric-gauge-verdict" style="color:{couleur};">'
            f'<span class="qt-gauge-dot" style="background:{couleur};"></span>{verdict}'
            f'</div>'
            f'</div>'
        )

    return (
        '<div class="qt-metrics-row">'
        + _card("Volatilité annualisée", f"{vol:.1f}%",   vol_pct,    vc, vv,
                "Amplitude des variations. Plus faible = plus stable.")
        + _card("Sharpe Ratio",          f"{sharpe:.2f}", sharpe_pct, sc, sv,
                ">2 Excellent · >1 Bon · 0–1 Passable · <0 Mauvais")
        + _card("Max Drawdown",          f"−{dd:.1f}%",   dd_pct,     dc, dv,
                "Pire chute depuis un plus-haut historique.")
        + _card("VaR 95% (1 jour)",      f"−{var:.1f}%",  var_pct,    rc, rv,
                "Perte max probable en 1 jour (niveau de confiance 95%).")
        + '</div>'
    )


def fig_camembert_repartition(poids: Dict[str, float]) -> go.Figure:
    """Camembert (donut) de la répartition du portefeuille."""
    c = get_theme_colors()
    pie_df = pd.DataFrame({
        "Actif": [NOM_AFFICHAGE.get(k, k) for k in poids.keys()],
        "Poids": [v * 100 for v in poids.values()]
    })
    fig = px.pie(
        pie_df, names="Actif", values="Poids",
        title="Répartition du portefeuille", hole=0.55,
        color_discrete_sequence=QT_PALETTE,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont=dict(family="Inter, sans-serif", size=12, color=c["text_strong"]),
        outsidetextfont=dict(family="Inter, sans-serif", size=12, color=c["text_strong"]),
        insidetextfont=dict(family="Inter, sans-serif", size=12, color="#ffffff"),
        marker=dict(line=dict(color=c["pie_border"], width=2)),
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
        automargin=True,
        # Effet "pull" : tranches qui s'écartent légèrement de manière aléatoire
        # pour donner un look 3D dynamique. Pull en valeur par tranche.
        pull=[0.02] * len(poids),
        rotation=90,  # commence en haut pour un look plus moderne
    )
    apply_qt_theme(fig, height=460, legend_bottom=False)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=80, r=80, t=46, b=30),
    )
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)
    return fig