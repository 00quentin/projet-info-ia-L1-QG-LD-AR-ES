"""
components/empty_states.py
==========================
Empty states riches pour les onglets vides.
Évite les "Lancez une simulation..." plats et propose des actions en 1 clic.
"""

import streamlit as st

from config import EVENEMENTS_PRESETS


# Icônes par scénario (emojis pour ne pas dépendre de Material Icons)
ICONES_SCENARIOS = {
    "Guerre mondiale":     "⚔️",
    "Pandémie mondiale":   "🦠",
    "Révolution IA":       "🤖",
    "Krach 2008 bis":      "📉",
    "Fusion nucléaire":    "⚛️",
    "Choc pétrolier":      "🛢️",
    "Hausse brutale FED":  "🏦",
    "Crise Chine-Taïwan":  "🌏",
}


def _hero_empty(icone: str, titre: str, sous_titre: str):
    """Bandeau d'entête pour tous les empty states."""
    st.markdown(
        f'<div class="qt-empty-state">'
        f'<div class="qt-empty-state-icon">{icone}</div>'
        f'<h2 class="qt-empty-state-title">{titre}</h2>'
        f'<p class="qt-empty-state-subtitle">{sous_titre}</p>'
        f'</div>',
        unsafe_allow_html=True
    )


def _on_preset_click(texte: str):
    """Callback exécuté AVANT le rerun, donc avant que le widget event_text_A
    soit re-instancié dans la sidebar (sinon Streamlit lève StreamlitAPIException)."""
    st.session_state.event_text_A = texte
    st.session_state["_auto_launch"] = True


def render_empty_dashboard():
    """Empty state du Dashboard : 8 cartes de scénarios cliquables."""
    _hero_empty(
        "📊",
        "Lancez votre première simulation",
        "Choisissez un scénario prédéfini pour démarrer en 1 clic — "
        "ou rédigez le vôtre dans la barre latérale à gauche."
    )

    st.markdown('<div class="qt-section-title">Scénarios prêts à l\'emploi</div>',
                unsafe_allow_html=True)
    st.caption("Cliquez sur un scénario : il sera chargé et la simulation démarrera automatiquement avec les paramètres par défaut.")

    presets = list(EVENEMENTS_PRESETS.items())

    # Grille 4 colonnes × 2 lignes
    for row in range(0, len(presets), 4):
        cols = st.columns(4, gap="medium")
        for col_idx in range(4):
            i = row + col_idx
            if i >= len(presets):
                break
            nom, texte = presets[i]
            icone = ICONES_SCENARIOS.get(nom, "📊")
            with cols[col_idx]:
                st.markdown(
                    f'<div class="qt-preset-card">'
                    f'<div class="qt-preset-icon">{icone}</div>'
                    f'<div class="qt-preset-title">{nom}</div>'
                    f'<div class="qt-preset-desc">{texte}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.button(
                    "Lancer →",
                    key=f"empty_preset_{i}",
                    use_container_width=True,
                    on_click=_on_preset_click,
                    args=(texte,),
                )


def render_empty_backtest():
    """Empty state du Backtest : invite à choisir un événement à gauche."""
    _hero_empty(
        "🕰️",
        "Rejouez l'histoire avec les vraies données de marché",
        "Sélectionnez un événement historique à gauche (Krach 2008, COVID-19, "
        "Subprimes…) pour mesurer la performance qu'aurait eu votre portefeuille."
    )

    st.markdown('<div class="qt-callout" style="margin-top:24px;">'
                '<strong>💡 Comment ça marche ?</strong><br>'
                '1. Choisissez un événement à gauche · '
                '2. Ajustez la période si besoin · '
                '3. Cliquez sur <strong>"Lancer le backtest"</strong>'
                '</div>',
                unsafe_allow_html=True)


def render_empty_portefeuille():
    """Empty state du Portefeuille."""
    _hero_empty(
        "💼",
        "Aucun portefeuille à afficher",
        "Lancez une simulation depuis l'onglet Dashboard pour voir "
        "la répartition détaillée et le bilan de votre portefeuille."
    )


def render_empty_comparaison():
    """Empty state de la Comparaison multi-scenarios."""
    _hero_empty(
        "⚖️",
        "Comparez 2 ou 3 scénarios côte à côte",
        "Réglez le curseur <strong>Nombre de scénarios à comparer</strong> "
        "dans la barre latérale (2 ou 3), rédigez vos scénarios, puis lancez "
        "la simulation. Vous verrez ici les courbes superposées, un comparatif "
        "des métriques de risque et le classement."
    )


def render_empty_historique():
    """Empty state de l'Historique."""
    _hero_empty(
        "📂",
        "Aucune simulation dans l'historique",
        "Vos 10 dernières simulations et backtests apparaîtront ici "
        "automatiquement. Lancez votre première analyse pour commencer."
    )
