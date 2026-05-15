"""
pages/portefeuille.py
=====================
Onglet Portefeuille : détail composition + bilan.
"""

import streamlit as st

from config import NOM_AFFICHAGE, LABELS_SCENARIOS
from core.portfolio import calculer_poids
from components.charts import fig_camembert_repartition
from components.empty_states import render_empty_portefeuille


def _html_grille_actifs(poids: dict, cap: float, perf_par_actif: dict) -> tuple[str, float]:
    """Génère la grille HTML des cartes actifs. Retourne (html, valeur_finale)."""
    cards = []
    valeur_finale = 0.0
    for sk, pct in poids.items():
        nom = NOM_AFFICHAGE.get(sk, sk.replace("_", " ").replace("EUR USD", "EUR/USD"))
        montant = cap * pct
        rend = perf_par_actif.get(sk, 0) / 100
        final = montant * (1 + rend)
        valeur_finale += final
        couleur = "#16c784" if rend >= 0 else "#ea3943"
        signe = "+" if rend >= 0 else ""
        cards.append(
            f'<div class="qt-asset-card">'
            f'<div class="qt-asset-header">'
            f'<span class="qt-asset-name">{nom}</span>'
            f'<span class="qt-asset-pct">{pct*100:.0f}%</span>'
            f'</div>'
            f'<div class="qt-asset-value">{final:,.0f} €</div>'
            f'<div class="qt-asset-rend" style="color:{couleur};">{signe}{rend*100:.2f}%</div>'
            f'<div class="qt-asset-initial">Base · {montant:,.0f} €</div>'
            f'</div>'
        )
    return '<div class="qt-asset-grid">' + "".join(cards) + '</div>', valeur_finale


def afficher_portefeuille(res, params, key_prefix="main"):
    """Affiche le détail du portefeuille pour un résultat de simulation."""
    cap = params["capital"]
    profil = params["profil"]
    actifs_sim = params["actifs_sim"]
    poids = calculer_poids(profil, actifs_sim, params["allocations"])

    st.markdown(f"<h3 style='text-align:center; color:var(--primary);'>Portefeuille de {cap:,.0f} €</h3>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:var(--text-muted); margin-bottom:28px;'>Profil : <strong>{profil}</strong></p>",
                unsafe_allow_html=True)

    html_grille, valeur_finale = _html_grille_actifs(poids, cap, res["perf"])
    st.markdown(html_grille, unsafe_allow_html=True)

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)

    if poids:
        col_pie, col_bilan = st.columns(2)
        with col_pie:
            fig_pie = fig_camembert_repartition(poids)
            st.plotly_chart(fig_pie, use_container_width=True, key=f"{key_prefix}_pie",
                            config={"scrollZoom": False})

        with col_bilan:
            st.markdown("<br><br>", unsafe_allow_html=True)
            gains = valeur_finale - cap
            st.metric("Bilan net du portefeuille", f"{valeur_finale:,.2f} €",
                      f"{gains:,.2f} € (gains/pertes)",
                      help="Valeur totale du portefeuille à la fin de la période simulée, "
                           "et écart en euros par rapport au capital de départ.")
            perf_g = (gains / cap) * 100 if cap > 0 else 0
            st.metric("Performance globale", f"{perf_g:+.2f} %",
                      help="Rendement total en pourcentage : (valeur finale − capital) / capital. "
                           "C'est le gain ou la perte global de votre stratégie.")

    return valeur_finale


def render_page_portefeuille():
    """Point d'entrée de la page Portefeuille."""
    simulations = st.session_state.simulations
    labels_disponibles = [lab for lab in LABELS_SCENARIOS if simulations.get(lab) is not None]

    if not labels_disponibles:
        render_empty_portefeuille()
        return

    if len(labels_disponibles) == 1:
        afficher_portefeuille(simulations[labels_disponibles[0]],
                               st.session_state.params_sim, key_prefix="port_main")
        return

    sub_tabs = st.tabs([f"Scénario {lab}" for lab in labels_disponibles])
    for tab, label in zip(sub_tabs, labels_disponibles):
        with tab:
            afficher_portefeuille(simulations[label],
                                   st.session_state.params_sim,
                                   key_prefix=f"port_{label}")