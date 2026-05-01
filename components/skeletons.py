"""
components/skeletons.py
=======================
Skeleton loaders affichés pendant les calculs longs.
Donne un aperçu visuel du contenu à venir au lieu d'un spinner gris.
"""

import streamlit as st


def _skeleton_html() -> str:
    """HTML d'un dashboard fantôme (4 jauges + 2 graphiques + heatmap)."""
    cartes = "".join([
        '<div class="qt-skel-card">'
        '<div class="qt-skel qt-skel-line" style="width:60%;"></div>'
        '<div class="qt-skel qt-skel-num"></div>'
        '<div class="qt-skel qt-skel-bar"></div>'
        '<div class="qt-skel qt-skel-line" style="width:40%;"></div>'
        '</div>'
        for _ in range(4)
    ])

    graphes = (
        '<div class="qt-skel-charts">'
        '<div class="qt-skel qt-skel-chart"></div>'
        '<div class="qt-skel qt-skel-chart"></div>'
        '</div>'
    )

    heatmap = '<div class="qt-skel qt-skel-heatmap"></div>'

    return (
        '<div class="qt-skeleton-wrap">'
        f'<div class="qt-skel-row">{cartes}</div>'
        f'{graphes}'
        f'{heatmap}'
        '</div>'
    )


def render_skeleton_dashboard() -> "st.delta_generator.DeltaGenerator":
    """
    Affiche un skeleton du dashboard dans un placeholder.
    Retourne le placeholder pour que l'appelant puisse l'effacer après calcul :

        ph = render_skeleton_dashboard()
        with st.spinner("..."):
            ...  # calcul lourd
        ph.empty()
    """
    placeholder = st.empty()
    placeholder.markdown(_skeleton_html(), unsafe_allow_html=True)
    return placeholder
