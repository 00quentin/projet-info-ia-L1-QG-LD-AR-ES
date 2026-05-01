"""
pages/apropos.py
================
Onglet À propos : présentation projet, équipe, stack, sources.
"""

import streamlit as st


MEMBRES_EQUIPE = [
    ("Quentin Geldreich", "Étudiant en MIASHS et Économie & Gestion"),
    ("Lukha Doazan",      "Étudiant en MIASHS et Économie & Gestion"),
    ("Evan Saadi",        "Étudiant en MIASHS et Économie & Gestion"),
    ("Alex Ruimy",        "Étudiant en MIASHS et Économie & Gestion"),
]


def render_page_apropos():
    """Affiche la page À propos complète."""
    st.markdown('<div class="qt-section-title">À propos de Quant Terminal</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="qt-card-intro">
        <div class="qt-tag">Université Paris Nanterre · Licence 1 · Semestre 2</div>
        <p style="font-size: 1.05em; margin-bottom: 0;">
            Quant Terminal est un projet réalisé dans le cadre de notre cours d'<strong>informatique de L1, semestre 2</strong>, 
            au sein de la licence <strong>MIASHS</strong> (Mathématiques et Informatique Appliquées aux Sciences Humaines et Sociales), 
            que nous suivons en <strong>double licence avec Économie et Gestion</strong> à l'Université Paris Nanterre.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Équipe
    st.markdown('<div class="qt-section-title">L\'équipe</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (nom, desc) in zip(cols, MEMBRES_EQUIPE):
        with col:
            initiales = f"{nom.split()[0][0]}{nom.split()[1][0]}"
            st.markdown(f"""
            <div class="qt-card" style="text-align:center; height:180px; display:flex; flex-direction:column; justify-content:center;">
                <div style="width:60px; height:60px; background:linear-gradient(135deg, #1a365d, #319795); border-radius:50%; margin:0 auto 12px auto; display:flex; align-items:center; justify-content:center; color:white; font-weight:800; font-size:18px;">
                    {initiales}
                </div>
                <strong style="color:#1a365d; font-size:1.05em;">{nom}</strong>
                <span style="font-size:0.85em; color:#718096; margin-top:6px; line-height:1.4;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    # Genèse
    st.markdown('<div class="qt-section-title">Genèse du projet</div>', unsafe_allow_html=True)
    st.write("""
    Nous avons choisi de développer un projet centré sur la **finance**, un domaine qui nous intéresse particulièrement, 
    tout comme les **mathématiques**. L'objectif était de combiner ces deux disciplines à travers un outil informatique, 
    afin de créer un projet cohérent et enrichissant.
    
    Ce projet a également une dimension **pédagogique** importante. Il vise à rendre certains concepts financiers plus 
    accessibles et compréhensibles pour un public large, notamment dans un cadre académique. Bien qu'il ne soit pas 
    destiné à être utilisé en l'état par des professionnels de la finance, nous avons cherché à nous rapprocher au 
    maximum d'un outil **réaliste et pertinent**.
    """)

    # Ambitions
    st.markdown('<div class="qt-section-title">Ambitions</div>', unsafe_allow_html=True)
    st.write("""
    Au-delà de l'aspect scolaire, notre ambition est de **poursuivre le développement** de cette application afin d'en 
    faire un outil réellement utilisable, avec une utilité concrète pour les utilisateurs. L'idée est donc de faire 
    évoluer ce projet vers quelque chose de plus abouti et potentiellement utile à un public plus large.
    """)

    # Stack
    st.markdown('<div class="qt-section-title">Stack technique</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="qt-card"><strong>Frontend & Backend</strong><br><br>'
                    '<span class="qt-pill">Python</span><span class="qt-pill">Streamlit</span>'
                    '<span class="qt-pill">Plotly</span><span class="qt-pill">Pandas</span></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="qt-card"><strong>IA & Données</strong><br><br>'
                    '<span class="qt-pill">OpenAI GPT</span><span class="qt-pill">Yahoo Finance</span>'
                    '<span class="qt-pill">NumPy</span><span class="qt-pill">Pydantic</span></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="qt-card"><strong>Hébergement</strong><br><br>'
                    '<span class="qt-pill">Streamlit Cloud</span><span class="qt-pill">GitHub</span>'
                    '<span class="qt-pill">ReportLab (PDF)</span></div>',
                    unsafe_allow_html=True)

    # Fonctionnalités
    st.markdown('<div class="qt-section-title">Fonctionnalités principales</div>', unsafe_allow_html=True)
    st.markdown("""
    - **Simulation prospective** : tester l'impact d'un scénario fictif sur un portefeuille
    - **Backtest historique** : rejouer les vraies données de crises passées (COVID, Lehman, dot-com…)
    - **Mode comparaison** : opposer deux scénarios sur le même portefeuille
    - **Mode Monte-Carlo** : 50 simulations pour une vision statistiquement robuste
    - **Calibration historique IA** : amplitudes calibrées sur les vraies crises
    - **Connexion Yahoo Finance** : prix actuels + volatilités historiques en direct
    - **Métriques institutionnelles** : Volatilité annualisée, Sharpe Ratio, Max Drawdown, VaR 95%
    - **Génération de rapport PDF** professionnel
    - **Analyste IA conversationnel** pour poser toutes vos questions
    - **Académie pédagogique** : 7 modules pour comprendre la finance de marché
    """)

    # Limites
    st.markdown('<div class="qt-section-title">Sources & limites assumées</div>', unsafe_allow_html=True)
    st.markdown('<div class="qt-callout-warn">'
                '<strong>Quant Terminal est un outil pédagogique.</strong><br><br>'
                'Les simulations utilisent un mouvement brownien géométrique standard, calibré par une IA.<br><br>'
                'Les volatilités sont calculées sur 12 mois Yahoo Finance.<br><br>'
                '<strong>Limites :</strong> volatilités supposées constantes, actifs indépendants, '
                'pas de coûts de transaction.<br><br>'
                'Pour un usage professionnel, il faudrait calibrer le modèle sur des données institutionnelles '
                'et ajouter la modélisation des corrélations et des queues épaisses.'
                '</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#718096; margin-top:30px; padding:20px; '
                'border-top: 1px solid #cbd5e0; font-size:0.85em;">'
                '© 2026 · Quant Terminal · Université Paris Nanterre · MIASHS'
                '</div>', unsafe_allow_html=True)