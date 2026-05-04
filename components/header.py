"""
components/header.py
====================
Composants de l'en-tête : toggle dark mode, hero, bande live, onboarding.
"""

import streamlit as st
from market_data import get_prix_actuels


def _toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode


def _show_onboarding():
    st.session_state.show_onboarding = True


def render_dark_mode_toggle():
    """Boutons toggle mode sombre + bouton aide."""
    col_h1, col_h2, col_h3 = st.columns([8, 2, 2])
    with col_h2:
        label_dark = "☀️ Mode clair" if st.session_state.dark_mode else "🌙 Mode sombre"
        st.button(
            label_dark,
            help="Basculer entre mode clair et mode sombre",
            key="toggle_dark",
            on_click=_toggle_dark_mode,
            use_container_width=True,
        )
    with col_h3:
        st.button(
            "❓ Guide d'utilisation",
            help="Afficher le guide d'utilisation",
            key="show_help",
            on_click=_show_onboarding,
            use_container_width=True,
        )


def render_hero():
    """Hero compact orienté business : logo + tagline + stats inline."""
    st.markdown("""
    <div class="qt-hero">
        <div class="qt-hero-grid">
            <div class="qt-hero-left">
                <div class="qt-hero-brand">
                    <div class="qt-hero-logo">QT</div>
                    <div>
                        <div class="qt-hero-eyebrow">Simulateur d'investissement</div>
                        <h1 class="qt-hero-title">Quant Terminal</h1>
                    </div>
                </div>
                <p class="qt-hero-tagline">
                    Imaginez un événement — krach boursier, guerre, révolution IA — et voyez en direct
                    son impact sur votre portefeuille. Avec les vrais prix de marché et une IA entraînée
                    sur les grandes crises de l'histoire.
                </p>
            </div>
            <div class="qt-hero-right">
                <div class="qt-hero-stat-card">
                    <div class="qt-hero-stat-value">23</div>
                    <div class="qt-hero-stat-label">Actifs</div>
                </div>
                <div class="qt-hero-stat-card">
                    <div class="qt-hero-stat-value">6</div>
                    <div class="qt-hero-stat-label">Crises</div>
                </div>
                <div class="qt-hero-stat-card">
                    <div class="qt-hero-stat-value">4</div>
                    <div class="qt-hero-stat-label">Métriques</div>
                </div>
                <div class="qt-hero-stat-card">
                    <div class="qt-hero-stat-value">∞</div>
                    <div class="qt-hero-stat-label">Scénarios</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _hide_onboarding():
    st.session_state.show_onboarding = False


def render_onboarding():
    """Guide d'utilisation complet (si activé)."""
    if not st.session_state.show_onboarding:
        return

    html = (
        '<div class="qt-onboarding">'
        '<h3 style="margin-top:0;">👋 Bienvenue sur Quant Terminal !</h3>'
        '<p style="margin-bottom:6px; color:var(--text-muted); font-size:0.97em;">'
        'Quant Terminal est un <strong>simulateur d\'investissement pédagogique</strong> : '
        'vous décrivez un événement (krach, guerre, hausse des taux, révolution IA…), '
        'et le terminal estime son impact sur votre portefeuille en utilisant les '
        '<strong>vrais prix de marché</strong> récupérés en direct via Yahoo Finance.'
        '</p>'
        '<p style="margin-bottom:0; color:var(--text-muted); font-size:0.95em;">'
        '<strong style="color:var(--primary);">⏱ Temps pour faire votre première simulation : ~2 minutes.</strong> '
        'Suivez les 4 étapes ci-dessous.'
        '</p>'
        '<div class="qt-onboarding-steps">'
        '<div class="qt-onboarding-step">'
        '<div class="qt-onboarding-step-num">1</div>'
        '<strong style="color:var(--primary);">Choisissez un scénario</strong>'
        '<p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">'
        'Dans la <strong>sidebar à gauche</strong>, cliquez sur un scénario rapide '
        '(ex: "Krach 2008", "COVID 2020") ou écrivez le vôtre dans la zone de texte. '
        'Plus votre scénario est précis (pays, secteur, ampleur), plus l\'IA sera pertinente.'
        '</p></div>'
        '<div class="qt-onboarding-step">'
        '<div class="qt-onboarding-step-num">2</div>'
        '<strong style="color:var(--primary);">Choisissez vos actifs</strong>'
        '<p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">'
        'Ouvrez l\'expander <em>"📊 Actifs à analyser"</em> et cochez les actifs '
        'à inclure (actions, obligations, or, pétrole, cryptos…). '
        'Vous pouvez aussi <strong>ajouter n\'importe quel ticker Yahoo</strong> '
        '(TSLA, NVDA, BTC-USD…) dans la section "Mes actifs personnalisés".'
        '</p></div>'
        '<div class="qt-onboarding-step">'
        '<div class="qt-onboarding-step-num">3</div>'
        '<strong style="color:var(--primary);">Définissez votre portefeuille</strong>'
        '<p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">'
        'Saisissez votre <strong>capital de départ (€)</strong> et choisissez un '
        '<strong>profil d\'investisseur</strong> :<br>'
        '• <em>Prudent</em> = beaucoup d\'obligations & or, peu d\'actions<br>'
        '• <em>Équilibré</em> = mix classique 60/40<br>'
        '• <em>Agressif</em> = forte exposition actions & cryptos<br>'
        '• <em>Personnalisé</em> = vous fixez les % vous-même'
        '</p></div>'
        '<div class="qt-onboarding-step">'
        '<div class="qt-onboarding-step-num">4</div>'
        '<strong style="color:var(--primary);">Lancez &amp; explorez les résultats</strong>'
        '<p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">'
        'Cliquez sur <strong>"Lancer la simulation"</strong> en bas de la sidebar. '
        'Naviguez ensuite entre les onglets en haut :<br>'
        '• <em>Dashboard</em> = analyse IA + métriques de risque + graphiques<br>'
        '• <em>Portefeuille</em> = répartition &amp; performance par actif<br>'
        '• <em>Historique</em> = retrouvez vos anciennes simulations<br>'
        '• <em>Académie</em> = explications des concepts (volatilité, Sharpe…)<br>'
        '• <em>Analyste IA</em> = chat libre avec l\'IA financière'
        '</p></div>'
        '</div>'
        '<div style="margin-top:22px; padding:14px 18px; background:var(--bg); border-radius:10px; border-left:4px solid var(--accent);">'
        '<strong style="color:var(--primary); font-size:0.95em;">💡 Astuces pour bien démarrer</strong>'
        '<ul style="margin:8px 0 0 0; padding-left:20px; font-size:0.88em; color:var(--text-muted); line-height:1.7;">'
        '<li>Le bouton <strong>🔄 Recharger les prix Yahoo</strong> en haut de la sidebar force le rafraîchissement des prix réels (sinon cache de 1h).</li>'
        '<li>Vous pouvez comparer jusqu\'à <strong>3 scénarios côte à côte</strong> via le slider "Nombre de scénarios" en haut de la sidebar.</li>'
        '<li>Cochez <em>"Mode Monte-Carlo"</em> dans les options avancées pour voir une <strong>fourchette de trajectoires</strong> (50 simulations).</li>'
        '<li>Le mode <strong>Backtest historique</strong> rejoue les vraies données passées (2008, COVID…) pour voir comment votre portefeuille s\'en serait sorti.</li>'
        '<li>L\'icône <strong>❓ Guide d\'utilisation</strong> en haut à droite réaffiche ce panneau à tout moment.</li>'
        '<li>Le <strong>mode sombre</strong> (bouton 🌙) est plus reposant pour les yeux en soirée.</li>'
        '</ul></div>'
        '<div style="margin-top:14px; padding:12px 16px; background:rgba(214,158,46,0.08); border-radius:10px; border-left:4px solid var(--warn);">'
        '<span style="color:var(--warn); font-weight:700; font-size:0.92em;">⚠ Important</span>'
        '<p style="margin:6px 0 0 0; font-size:0.86em; color:var(--text-muted); line-height:1.55;">'
        'Quant Terminal est un <strong>outil pédagogique</strong>. Les résultats ne '
        'constituent <strong>pas un conseil en investissement</strong>. L\'IA estime des '
        'ordres de grandeur en s\'inspirant de crises historiques — la réalité peut fortement diverger.'
        '</p></div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    st.button(
        "✓ J'ai compris, masquer ce guide",
        key="hide_onboarding",
        use_container_width=True,
        on_click=_hide_onboarding,
    )


def render_bande_marche():
    """Bande horizontale avec prix live de 6 actifs majeurs."""
    try:
        actifs_strip = ["S&P 500", "VIX", "Or", "Petrole", "Bitcoin", "EUR_USD"]
        prix, _ = get_prix_actuels(actifs_strip)

        items_html = '<div class="market-strip-tag">⬤ LIVE</div>'
        labels_courts = {
            "S&P 500": "S&P 500", "VIX": "VIX",
            "Or": "OR ($/oz)", "Petrole": "PÉTROLE ($)",
            "Bitcoin": "BTC ($)", "EUR_USD": "EUR/USD",
        }
        formats = {
            "S&P 500": "{:,.0f}", "VIX": "{:.2f}",
            "Or": "{:,.0f}", "Petrole": "{:.2f}",
            "Bitcoin": "{:,.0f}", "EUR_USD": "{:.4f}",
        }
        for actif in actifs_strip:
            if actif in prix:
                val = formats[actif].format(prix[actif]).replace(",", " ")
                items_html += (
                    f'<div class="market-strip-item">'
                    f'<span class="market-strip-label">{labels_courts[actif]}</span>'
                    f'<span class="market-strip-value">{val}</span>'
                    f'</div>'
                )

        st.markdown(f'<div class="market-strip">{items_html}</div>', unsafe_allow_html=True)
    except Exception:
        pass


def render_disclaimer_top():
    """Mini-bandeau disclaimer subtil mais visible."""
    st.markdown("""
    <div style="font-size: 0.8em; color: var(--muted); text-align: center; margin: 6px 0 16px 0;">
        <span style="display: inline-block; padding: 3px 14px; background: rgba(214,158,46,0.1); border-radius: 12px; border: 1px solid rgba(214,158,46,0.25);">
            ⓘ Outil pédagogique · Ne constitue pas un conseil en investissement
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_intro_card():
    """Carte d'introduction sous le hero."""
    st.markdown("""
    <div class="qt-card-intro">
        <div class="qt-tag">Projet 2026 · Q. Geldreich, L. Doazan, E. Saadi, A. Ruimy · Université Paris Nanterre</div>
        <p style="font-size: 1.05em; margin-bottom: 0;">
            <strong>Quant Terminal</strong> permet de tester comment un événement économique ou géopolitique impacte un portefeuille — 
            à partir des <strong>vrais prix de marché</strong> récupérés en direct via Yahoo Finance. 
            Une IA interprète votre scénario en s'inspirant des grandes crises historiques, 
            un moteur stochastique simule l'impact, et les métriques institutionnelles évaluent la solidité de votre stratégie.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_header_complet():
    """Affiche tout le header en une seule fonction."""
    render_dark_mode_toggle()
    render_hero()
    render_onboarding()
    render_bande_marche()
    render_disclaimer_top()
    render_intro_card()