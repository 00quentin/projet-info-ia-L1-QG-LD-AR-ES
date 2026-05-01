"""
components/header.py
====================
Composants de l'en-tête : toggle dark mode, hero, bande live, onboarding.
"""

import streamlit as st
from market_data import get_prix_actuels


def render_dark_mode_toggle():
    """Boutons toggle mode sombre + bouton aide."""
    col_h1, col_h2, col_h3 = st.columns([10, 1, 1])
    with col_h2:
        if st.button("☀️" if st.session_state.dark_mode else "🌙",
                     help="Basculer en mode " + ("clair" if st.session_state.dark_mode else "sombre"),
                     key="toggle_dark"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with col_h3:
        if st.button("❓", help="Afficher le guide d'utilisation", key="show_help"):
            st.session_state.show_onboarding = True
            st.rerun()


def render_hero():
    """Hero compact orienté business : logo + tagline + stats inline."""
    st.markdown("""
    <div class="qt-hero">
        <div class="qt-hero-grid">
            <div class="qt-hero-left">
                <div class="qt-hero-brand">
                    <div class="qt-hero-logo">QT</div>
                    <div>
                        <div class="qt-hero-eyebrow">Institutional-Grade Risk Lab</div>
                        <h1 class="qt-hero-title">Quant Terminal</h1>
                    </div>
                </div>
                <p class="qt-hero-tagline">
                    Stress-testez votre portefeuille face à n'importe quel scénario économique ou géopolitique.
                    Prix de marché en direct, IA calibrée sur les crises historiques, métriques institutionnelles.
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


def render_onboarding():
    """Pop-up d'onboarding 3 étapes (si activé)."""
    if not st.session_state.show_onboarding:
        return

    st.markdown("""
    <div class="qt-onboarding">
        <h3 style="margin-top:0;">👋 Bienvenue sur Quant Terminal !</h3>
        <p style="margin-bottom:0; color:var(--text-muted);">Voici comment utiliser le terminal en 3 étapes simples :</p>
        <div class="qt-onboarding-steps">
            <div class="qt-onboarding-step">
                <div class="qt-onboarding-step-num">1</div>
                <strong style="color:var(--primary);">Choisissez un scénario</strong>
                <p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">
                    Cliquez sur un bouton de scénario rapide (à gauche) ou écrivez le vôtre.
                </p>
            </div>
            <div class="qt-onboarding-step">
                <div class="qt-onboarding-step-num">2</div>
                <strong style="color:var(--primary);">Définissez votre portefeuille</strong>
                <p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">
                    Choisissez les actifs à inclure et votre profil d'investisseur (Prudent, Équilibré, Agressif…).
                </p>
            </div>
            <div class="qt-onboarding-step">
                <div class="qt-onboarding-step-num">3</div>
                <strong style="color:var(--primary);">Lancez et explorez</strong>
                <p style="font-size:0.88em; color:var(--text-muted); margin:8px 0 0 0;">
                    Cliquez sur "Lancer la simulation" puis explorez les onglets Dashboard, Portefeuille, Académie…
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✓ J'ai compris, masquer ce guide", key="hide_onboarding", use_container_width=True):
        st.session_state.show_onboarding = False
        st.rerun()


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