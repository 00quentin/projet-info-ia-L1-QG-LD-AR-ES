"""
components/footer.py
====================
Footer professionnel + disclaimer fintech + toasts de notification.
"""

import streamlit as st


def render_footer():
    """Footer pro 5 colonnes + disclaimer complet."""
    st.markdown("""
    <div class="qt-footer">
        <div class="qt-footer-cols">
            <div>
                <h5>Quant Terminal</h5>
                <ul>
                    <li>Simulation prospective</li>
                    <li>Backtest historique</li>
                    <li>Académie financière</li>
                    <li>Analyste IA</li>
                </ul>
            </div>
            <div>
                <h5>Données & Sources</h5>
                <ul>
                    <li>Yahoo Finance (prix temps réel)</li>
                    <li>OpenAI GPT (analyse IA)</li>
                    <li>Volatilités historiques 12 mois</li>
                    <li>23 actifs · 6 catégories</li>
                </ul>
            </div>
            <div>
                <h5>Méthodologie</h5>
                <ul>
                    <li>Mouvement brownien géométrique</li>
                    <li>Méthode Monte-Carlo (50 sims)</li>
                    <li>Métriques institutionnelles</li>
                    <li>Calibration historique IA</li>
                </ul>
            </div>
            <div>
                <h5>Équipe</h5>
                <ul>
                    <li>Quentin Geldreich</li>
                    <li>Lukha Doazan</li>
                    <li>Evan Saadi</li>
                    <li>Alex Ruimy</li>
                </ul>
            </div>
            <div>
                <h5>Mentions</h5>
                <ul>
                    <li>Outil pédagogique</li>
                    <li>Université Paris Nanterre</li>
                    <li>Licence MIASHS · L1 S2</li>
                    <li>Projet 2026</li>
                </ul>
            </div>
        </div>
        <div class="qt-footer-bottom">
            <div style="background: rgba(214,158,46,0.12); border: 1px solid rgba(214,158,46,0.3); border-radius: 8px; padding: 12px 16px; margin-bottom: 14px; text-align: left; font-size: 0.82em; line-height: 1.6;">
                <strong style="color: #d69e2e;">⚠ Avertissement</strong> — Quant Terminal est un <strong>outil pédagogique</strong> développé dans un cadre universitaire (Université Paris Nanterre, MIASHS L1).
                Les simulations et analyses présentées <strong>ne constituent pas un conseil en investissement</strong>, ni une recommandation d'achat ou de vente d'un quelconque actif financier.
                Les performances passées ne préjugent pas des performances futures. Les utilisateurs sont seuls responsables de leurs décisions d'investissement et sont invités à consulter un conseiller financier agréé avant toute opération.
            </div>
            © 2026 Quant Terminal · Tous droits réservés · Université Paris Nanterre
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_toasts():
    """Affiche les toasts si des flags de session sont activés."""
    if st.session_state.get("_just_simulated", False):
        st.toast("✅ Simulation terminée avec succès !", icon="🎉")
        st.session_state["_just_simulated"] = False

    if st.session_state.get("_just_backtested", False):
        st.toast("✅ Backtest terminé !", icon="📊")
        st.session_state["_just_backtested"] = False

    if st.session_state.get("_just_pdf", False):
        st.toast("📄 Rapport PDF prêt !", icon="✅")
        st.session_state["_just_pdf"] = False