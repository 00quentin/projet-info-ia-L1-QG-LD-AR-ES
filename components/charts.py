"""
components/charts.py
====================
Fabrique de graphiques Plotly réutilisables.
"""

from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import (
    CATEGORIES_GRAPHIQUES, NOM_AFFICHAGE, COULEURS_PLOTLY,
    HAUTEUR_GRAPHIQUE, COULEUR_PRIMAIRE, COULEUR_TEXT,
)


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
        col_c = COULEURS_PLOTLY[idx % len(COULEURS_PLOTLY)]
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
            line=dict(color=col_c, width=2.2)
        ))

    fig.update_layout(
        title=dict(text=titre_cat + suffixe_titre,
                    font=dict(color=COULEUR_PRIMAIRE, size=15)),
        template="plotly_white",
        xaxis_title="Jours de cotation", yaxis_title="Évolution (Base 100)",
        height=HAUTEUR_GRAPHIQUE,
        margin=dict(l=10, r=10, t=45, b=90),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        font=dict(color=COULEUR_TEXT)
    )
    return fig


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
    """Crée la heatmap horizontale (barres colorées) de performance par actif."""
    fig = px.bar(
        perf_df, x='Performance (%)', y='Actif', orientation='h',
        color='Performance (%)',
        color_continuous_scale=['#c53030', '#f7fafc', '#2f855a'],
        text='Performance (%)', title=titre
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='auto')
    fig.update_layout(
        template="plotly_white",
        height=max(350, 30 * len(perf_df) + 80),
        margin=dict(l=10, r=10, t=50, b=10),
        title_font=dict(color=COULEUR_PRIMAIRE),
        font=dict(color=COULEUR_TEXT)
    )
    return fig


def fig_evolution_portefeuille(
    valeur_port: pd.Series,
    capital: float,
    benchmark: Optional[pd.Series] = None,
    titre_benchmark: str = "S&P 500 (benchmark)",
) -> go.Figure:
    """Évolution du portefeuille vs benchmark optionnel."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=valeur_port.index, y=valeur_port,
        name="Votre portefeuille",
        line=dict(color=COULEUR_PRIMAIRE, width=3)
    ))
    if benchmark is not None:
        fig.add_trace(go.Scatter(
            x=benchmark.index, y=benchmark,
            name=titre_benchmark,
            line=dict(color="#319795", width=2, dash="dash")
        ))
    fig.add_hline(
        y=capital, line_dash="dot", line_color="#718096",
        annotation_text=f"Capital initial ({capital:,.0f} €)",
        annotation_position="bottom right"
    )
    fig.update_layout(
        template="plotly_white", height=420,
        xaxis_title="Jours de cotation",
        yaxis_title="Valeur (€)",
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        font=dict(color=COULEUR_TEXT)
    )
    return fig


def html_metriques_jauges(metriques: Dict[str, float]) -> str:
    """Génère le HTML des 4 cartes métriques avec jauges visuelles colorées."""

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

    def _card(label, valeur_fmt, pct, couleur, verdict, aide):
        return (
            f'<div class="qt-metric-gauge" style="border-left:4px solid {couleur};">'
            f'<div class="qt-metric-gauge-label" title="{aide}">{label}</div>'
            f'<div class="qt-metric-gauge-value" style="color:{couleur};">{valeur_fmt}</div>'
            f'<div class="qt-metric-gauge-track">'
            f'<div class="qt-metric-gauge-fill" style="width:{pct:.1f}%;background:{couleur};"></div>'
            f'</div>'
            f'<div class="qt-metric-gauge-verdict" style="color:{couleur};">▲ {verdict}</div>'
            f'</div>'
        )

    return (
        '<div class="qt-metrics-row">'
        + _card("Volatilité annualisée", f"{vol:.2f} %",    vol_pct,    vc, vv,
                "Amplitude des variations. Plus faible = plus stable.")
        + _card("Sharpe Ratio",          f"{sharpe:.2f}",   sharpe_pct, sc, sv,
                ">2 Excellent · >1 Bon · 0–1 Passable · <0 Mauvais")
        + _card("Max Drawdown",          f"−{dd:.2f} %",    dd_pct,     dc, dv,
                "Pire chute depuis un plus-haut historique.")
        + _card("VaR 95% (1 jour)",      f"−{var:.2f} %",   var_pct,    rc, rv,
                "Perte max probable en 1 jour (niveau de confiance 95%).")
        + '</div>'
    )


def fig_camembert_repartition(poids: Dict[str, float]) -> go.Figure:
    """Camembert (donut) de la répartition du portefeuille."""
    pie_df = pd.DataFrame({
        "Actif": [NOM_AFFICHAGE.get(k, k) for k in poids.keys()],
        "Poids": [v * 100 for v in poids.values()]
    })
    fig = px.pie(
        pie_df, names="Actif", values="Poids",
        title="Répartition du portefeuille", hole=0.5,
        color_discrete_sequence=["#1a365d", "#319795", "#d69e2e", "#805ad5",
                                  "#2f855a", "#c53030", "#2c5282", "#4a5568"]
    )
    fig.update_layout(
        template="plotly_white", height=340,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="v", x=1.0, y=0.5),
        title_font=dict(color=COULEUR_PRIMAIRE)
    )
    return fig