"""
components/empty_states.py
==========================
Empty states riches pour les onglets vides.
Évite les "Lancez une simulation..." plats et propose des actions en 1 clic.
"""

import streamlit as st

from config import EVENEMENTS_PRESETS
from components.scenario_illustrations import get_illustration


# Icônes "minimal" affichées dans le titre (à côté du nom). Petits SVG en ligne
# pour rester cohérents avec le style Linear/Vercel (pas d'emojis criards).
ICONES_SCENARIOS = {
    "Guerre mondiale":     "⚔",
    "Pandémie mondiale":   "🧬",
    "Révolution IA":       "◆",
    "Krach 2008 bis":      "▼",
    "Fusion nucléaire":    "⚛",
    "Choc pétrolier":      "▲",
    "Hausse brutale FED":  "%",
    "Crise Chine-Taïwan":  "◉",
}


def _hero_svg(kind: str) -> str:
    """Renvoie un SVG illustratif par type d'empty state (~140x100)."""
    svgs = {
        "dashboard": (
            # Petit dashboard stylisé : 3 cartes + une courbe centrale
            '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
            '<defs><linearGradient id="hg_d" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0%" stop-color="#6366f1"/>'
            '<stop offset="100%" stop-color="#4338ca"/></linearGradient></defs>'
            '<rect x="10" y="20" width="50" height="60" rx="6" fill="#e2e8f0"/>'
            '<rect x="14" y="26" width="30" height="3" rx="1" fill="#94a3b8"/>'
            '<rect x="14" y="34" width="40" height="3" rx="1" fill="#cbd5e1"/>'
            '<polyline points="14,68 22,60 30,64 38,52 46,56 54,46" '
            'fill="none" stroke="url(#hg_d)" stroke-width="2" stroke-linecap="round"/>'
            '<rect x="75" y="20" width="50" height="60" rx="6" fill="#e0f2fe"/>'
            '<circle cx="100" cy="50" r="20" fill="none" stroke="#06b6d4" stroke-width="3"'
            ' stroke-dasharray="90 35" transform="rotate(-90 100 50)">'
            '<animate attributeName="stroke-dashoffset" values="0;-125" dur="3s" repeatCount="indefinite"/>'
            '</circle>'
            '<text x="100" y="54" text-anchor="middle" font-size="9" font-weight="700" fill="#06b6d4">72%</text>'
            '<rect x="140" y="20" width="50" height="60" rx="6" fill="#fef3c7"/>'
            '<g fill="#f59e0b">'
            '<rect x="146" y="60" width="6" height="14"><animate attributeName="height" values="14;22;14" dur="2s" repeatCount="indefinite"/><animate attributeName="y" values="60;52;60" dur="2s" repeatCount="indefinite"/></rect>'
            '<rect x="156" y="50" width="6" height="24"><animate attributeName="height" values="24;14;24" dur="2s" begin="0.3s" repeatCount="indefinite"/><animate attributeName="y" values="50;60;50" dur="2s" begin="0.3s" repeatCount="indefinite"/></rect>'
            '<rect x="166" y="40" width="6" height="34"><animate attributeName="height" values="34;26;34" dur="2s" begin="0.6s" repeatCount="indefinite"/><animate attributeName="y" values="40;48;40" dur="2s" begin="0.6s" repeatCount="indefinite"/></rect>'
            '<rect x="176" y="30" width="6" height="44"><animate attributeName="height" values="44;38;44" dur="2s" begin="0.9s" repeatCount="indefinite"/><animate attributeName="y" values="30;36;30" dur="2s" begin="0.9s" repeatCount="indefinite"/></rect>'
            '</g>'
            '</svg>'
        ),
        "backtest": (
            # Horloge + courbe historique
            '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
            '<defs><linearGradient id="hg_b" x1="0" y1="1" x2="0" y2="0">'
            '<stop offset="0%" stop-color="#ef454a" stop-opacity="0.2"/>'
            '<stop offset="100%" stop-color="#ef454a" stop-opacity="0"/></linearGradient></defs>'
            '<circle cx="40" cy="50" r="30" fill="none" stroke="#4f46e5" stroke-width="3"/>'
            '<circle cx="40" cy="50" r="2" fill="#4f46e5"/>'
            '<line x1="40" y1="50" x2="40" y2="28" stroke="#4f46e5" stroke-width="2" stroke-linecap="round">'
            '<animateTransform attributeName="transform" type="rotate" from="0 40 50" to="360 40 50" dur="6s" repeatCount="indefinite"/>'
            '</line>'
            '<line x1="40" y1="50" x2="56" y2="50" stroke="#06b6d4" stroke-width="1.5" stroke-linecap="round">'
            '<animateTransform attributeName="transform" type="rotate" from="0 40 50" to="360 40 50" dur="60s" repeatCount="indefinite"/>'
            '</line>'
            '<g stroke="#4f46e5" stroke-width="1.5" stroke-linecap="round">'
            '<line x1="40" y1="22" x2="40" y2="26"/><line x1="40" y1="74" x2="40" y2="78"/>'
            '<line x1="12" y1="50" x2="16" y2="50"/><line x1="64" y1="50" x2="68" y2="50"/></g>'
            # Courbe avec aire à droite
            '<path d="M 90 70 L 105 60 L 120 65 L 135 50 L 150 55 L 165 35 L 180 40 L 195 25 L 195 80 L 90 80 Z" '
            'fill="url(#hg_b)"/>'
            '<polyline points="90,70 105,60 120,65 135,50 150,55 165,35 180,40 195,25" '
            'fill="none" stroke="#ef454a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="195" cy="25" r="3" fill="#ef454a">'
            '<animate attributeName="r" values="3;5;3" dur="1.5s" repeatCount="indefinite"/></circle>'
            '</svg>'
        ),
        "portefeuille": (
            # Donut camembert animé
            '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
            '<g transform="translate(100 50)">'
            '<circle r="34" fill="none" stroke="#3b82f6" stroke-width="14" stroke-dasharray="60 154" transform="rotate(-90)"/>'
            '<circle r="34" fill="none" stroke="#16c784" stroke-width="14" stroke-dasharray="50 164" stroke-dashoffset="-60" transform="rotate(-90)"/>'
            '<circle r="34" fill="none" stroke="#f59e0b" stroke-width="14" stroke-dasharray="40 174" stroke-dashoffset="-110" transform="rotate(-90)"/>'
            '<circle r="34" fill="none" stroke="#8b5cf6" stroke-width="14" stroke-dasharray="64 150" stroke-dashoffset="-150" transform="rotate(-90)"/>'
            '<text x="0" y="6" text-anchor="middle" font-size="14" font-weight="800" fill="#1e293b">€</text>'
            '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="20s" repeatCount="indefinite" additive="sum"/>'
            '</g>'
            '<rect x="20" y="30" width="50" height="6" rx="2" fill="#3b82f6"/>'
            '<rect x="20" y="42" width="35" height="6" rx="2" fill="#16c784"/>'
            '<rect x="20" y="54" width="40" height="6" rx="2" fill="#f59e0b"/>'
            '<rect x="20" y="66" width="30" height="6" rx="2" fill="#8b5cf6"/>'
            '</svg>'
        ),
        "comparaison": (
            # Deux courbes superposées
            '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
            '<line x1="10" y1="80" x2="190" y2="80" stroke="#cbd5e1" stroke-width="1"/>'
            '<line x1="10" y1="20" x2="10" y2="80" stroke="#cbd5e1" stroke-width="1"/>'
            '<polyline points="10,70 30,55 55,60 85,40 115,45 145,30 175,35 190,25" '
            'fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
            '<polyline points="10,70 30,72 55,65 85,68 115,55 145,58 175,50 190,48" '
            'fill="none" stroke="#ef454a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
            'stroke-dasharray="4 3"/>'
            '<circle cx="190" cy="25" r="3.5" fill="#6366f1"><animate attributeName="r" values="3.5;5;3.5" dur="2s" repeatCount="indefinite"/></circle>'
            '<circle cx="190" cy="48" r="3.5" fill="#ef454a"><animate attributeName="r" values="3.5;5;3.5" dur="2s" begin="0.5s" repeatCount="indefinite"/></circle>'
            # Légende
            '<rect x="80" y="88" width="10" height="3" rx="1" fill="#6366f1"/>'
            '<text x="93" y="92" font-size="7" fill="#64748b">Scénario A</text>'
            '<rect x="135" y="88" width="10" height="3" rx="1" fill="#ef454a"/>'
            '<text x="148" y="92" font-size="7" fill="#64748b">Scénario B</text>'
            '</svg>'
        ),
        "historique": (
            # Pile de cartes (registres) avec icônes
            '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
            '<rect x="50" y="25" width="100" height="55" rx="6" fill="#e2e8f0" transform="rotate(-3 100 52)"/>'
            '<rect x="50" y="22" width="100" height="55" rx="6" fill="#f1f5f9" transform="rotate(0 100 50)" stroke="#cbd5e1"/>'
            '<rect x="50" y="20" width="100" height="55" rx="6" fill="#ffffff" transform="rotate(3 100 48)" stroke="#94a3b8"/>'
            '<g transform="translate(53 23) rotate(3 47 25)">'
            '<rect x="6" y="6" width="22" height="3" rx="1" fill="#94a3b8"/>'
            '<rect x="6" y="14" width="35" height="2" rx="1" fill="#cbd5e1"/>'
            '<rect x="6" y="20" width="30" height="2" rx="1" fill="#cbd5e1"/>'
            '<polyline points="60,40 70,32 80,36 90,28" stroke="#6366f1" stroke-width="2" fill="none" stroke-linecap="round"/>'
            '<circle cx="90" cy="28" r="2.5" fill="#6366f1"><animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite"/></circle>'
            '</g>'
            '</svg>'
        ),
    }
    return svgs.get(kind, svgs["dashboard"])


def _hero_empty(icone: str, titre: str, sous_titre: str, illu_kind: str = "dashboard"):
    """Bandeau d'entête pour tous les empty states (avec illustration SVG)."""
    illustration = _hero_svg(illu_kind)
    st.markdown(
        f'<div class="qt-empty-state">'
        f'<div class="qt-empty-state-illu">{illustration}</div>'
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


def _on_launch_defaut():
    """Déclenche la simulation avec le scénario déjà saisi (ou le défaut)."""
    st.session_state["_auto_launch"] = True


def render_empty_dashboard():
    """Empty state du Dashboard : 8 cartes de scénarios avec illustrations SVG animées."""
    _hero_empty(
        "📊",
        "Lancez votre première simulation",
        "Choisissez un scénario prédéfini pour démarrer en 1 clic — "
        "ou rédigez le vôtre dans la barre latérale à gauche.",
        illu_kind="dashboard",
    )

    # CTA principal visible dans la zone de contenu (utile sur mobile où la sidebar est cachée)
    col_cta, col_hint = st.columns([1, 2])
    with col_cta:
        st.button(
            "🚀 Lancer la simulation",
            key="empty_launch_defaut",
            use_container_width=True,
            type="primary",
            on_click=_on_launch_defaut,
            help="Lance la simulation avec le scénario actuellement saisi dans la sidebar.",
        )
    with col_hint:
        st.markdown(
            '<p style="color:var(--text-muted); font-size:0.85em; '
            'margin:10px 0 0 0; line-height:1.5;">'
            '← Sur mobile : tapez <strong>☰</strong> en haut à gauche '
            'pour accéder aux paramètres.</p>',
            unsafe_allow_html=True,
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
            icone = ICONES_SCENARIOS.get(nom, "◆")
            illustration_html = get_illustration(nom)
            with cols[col_idx]:
                # st.markdown(unsafe_allow_html=True) — st.html sanitize
                # certains attributs SVG (animate, animateMotion) ce qui
                # casse les illustrations.
                st.markdown(
                    f'<div class="qt-preset-card">'
                    f'{illustration_html}'
                    f'<div class="qt-preset-body">'
                    f'<div class="qt-preset-title">'
                    f'<span class="qt-preset-icon-inline">{icone}</span>{nom}'
                    f'</div>'
                    f'<div class="qt-preset-desc">{texte}</div>'
                    f'<div class="qt-preset-meta">'
                    f'<span class="qt-preset-time">~ 2 min</span>'
                    f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.button(
                    "▶  Lancer",
                    key=f"empty_preset_{i}",
                    use_container_width=True,
                    on_click=_on_preset_click,
                    args=(texte,),
                    type="primary",
                    help=f"Lance la simulation du scénario : {nom}",
                )


def render_empty_backtest():
    """Empty state du Backtest : invite à choisir un événement à gauche."""
    _hero_empty(
        "🕰️",
        "Rejouez l'histoire avec les vraies données de marché",
        "Sélectionnez un événement historique à gauche (Krach 2008, COVID-19, "
        "Subprimes…) pour mesurer la performance qu'aurait eu votre portefeuille.",
        illu_kind="backtest",
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
        "la répartition détaillée et le bilan de votre portefeuille.",
        illu_kind="portefeuille",
    )


def _on_activer_comparaison(nb: int):
    """Active le mode comparaison en réglant le nombre de scénarios."""
    st.session_state.nb_scenarios = nb


def render_empty_comparaison():
    """Empty state de la Comparaison multi-scenarios."""
    _hero_empty(
        "⚖️",
        "Comparez 2 ou 3 scénarios côte à côte",
        "Lancez la simulation avec 2 ou 3 scénarios différents pour voir "
        "les courbes superposées, le comparatif de métriques et le classement.",
        illu_kind="comparaison",
    )

    # Guide 3 étapes + boutons d'activation rapide
    st.markdown(
        '<div style="background:var(--card); border:1px solid var(--border); '
        'border-radius:14px; padding:20px 24px; margin:16px 0;">'
        '<div style="font-weight:700; font-size:1em; color:var(--primary); margin-bottom:14px;">'
        '📋 Comment activer la comparaison ?</div>'
        '<div style="display:flex; gap:0; flex-wrap:wrap;">'

        '<div style="flex:1; min-width:160px; padding:10px 14px; '
        'border-left:3px solid var(--accent);">'
        '<div style="font-weight:700; color:var(--accent); margin-bottom:4px;">① Sidebar</div>'
        '<div style="font-size:0.86em; color:var(--text-muted);">'
        'Réglez le curseur <strong>"Nombre de scénarios"</strong> sur 2 ou 3.</div></div>'

        '<div style="flex:1; min-width:160px; padding:10px 14px; '
        'border-left:3px solid #06b6d4;">'
        '<div style="font-weight:700; color:#06b6d4; margin-bottom:4px;">② Scénarios</div>'
        '<div style="font-size:0.86em; color:var(--text-muted);">'
        'Rédigez un scénario <strong>différent</strong> pour chaque lettre (A, B, C).</div></div>'

        '<div style="flex:1; min-width:160px; padding:10px 14px; '
        'border-left:3px solid #16c784;">'
        '<div style="font-weight:700; color:#16c784; margin-bottom:4px;">③ Lancer</div>'
        '<div style="font-size:0.86em; color:var(--text-muted);">'
        'Cliquez sur <strong>"Lancer la simulation"</strong> — les résultats s\'affichent ici.</div></div>'

        '</div></div>',
        unsafe_allow_html=True
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("⚔ Comparer 2 scénarios", use_container_width=True,
                     on_click=_on_activer_comparaison, args=(2,), type="primary"):
            pass
    with col_b:
        if st.button("🏆 Tournoi 3 scénarios", use_container_width=True,
                     on_click=_on_activer_comparaison, args=(3,)):
            pass
    with col_c:
        st.markdown(
            '<p style="font-size:0.82em; color:var(--text-muted); '
            'margin:10px 0 0 0; text-align:center;">'
            'Ces boutons règlent le curseur sidebar et affichent les champs de texte.</p>',
            unsafe_allow_html=True
        )


def render_empty_historique():
    """Empty state de l'Historique."""
    _hero_empty(
        "📂",
        "Aucune simulation dans l'historique",
        "Vos 10 dernières simulations et backtests apparaîtront ici "
        "automatiquement. Lancez votre première analyse pour commencer.",
        illu_kind="historique",
    )
