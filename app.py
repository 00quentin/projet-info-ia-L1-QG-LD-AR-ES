import streamlit as st
import pandas as pd
import plotly.express as px
from simulation import simuler_marche_dynamique
from ia_bot import analyser_evenement_macro, discuter_avec_ia

# ==========================================
# 1. CONFIGURATION DE LA PAGE & CSS (AVEC ANTI MODE-SOMBRE)
# ==========================================
st.set_page_config(page_title="Quant Terminal", page_icon="💠", layout="wide")
st.markdown("""
    <style>
    /* Fond général plus doux */
    .stApp {
        background-color: #f4f6f9 !important;
    }
    
    /* 🔴 BOUCLIER ANTI MODE-SOMBRE (Force le texte en foncé) */
    .stMarkdown, .stText, p, li, h1, h2, h3, h4, h5, h6, label {
        color: #2c3e50 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] * {
        color: #2c3e50 !important;
    }
    /* Les valeurs des métriques */
    [data-testid="stMetricValue"] {
        color: #2c3e50 !important;
    }
    [data-testid="stMetricLabel"] * {
        color: #7f8c8d !important;
    }
    
    /* Réduction des marges mais on GARDE le header */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1600px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style des cartes de métriques : fond blanc pur, ombre très douce */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid #eaedf1 !important;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    
    /* Personnalisation des onglets */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        flex-grow: 1;
        text-align: center;
        font-weight: 600;
        color: #2c3e50 !important;
    }
    </style>
""", unsafe_allow_html=True)

if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []

# ==========================================
# 2. EN-TÊTE & INTRODUCTION
# ==========================================
st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 20px;">
        <div style="width: 55px; height: 55px; background: linear-gradient(135deg, #2c3e50, #3498db); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white !important; font-size: 24px; font-weight: 900; box-shadow: 0 4px 10px rgba(52,152,219,0.3);">
            QT
        </div>
        <h1 style="margin: 0; padding: 0; font-size: 2.8em; color: #2c3e50 !important; font-weight: 800; letter-spacing: -0.5px;">Quant Terminal</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color: #ffffff; border-left: 4px solid #3498db; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); margin-bottom: 35px; color: #4a5568 !important; line-height: 1.6;'>
        <p style='margin-top: 0; font-size: 0.9em; color: #7f8c8d !important; text-transform: uppercase; letter-spacing: 1px;'>
            Créée le 3 avril 2026 par Quentin Geldreich, Lukha Doazan et Evan Saadi
        </p>
        <p style='font-size: 1.1em; margin-bottom: 0;'>
            <strong>Bienvenue sur Quant Terminal !</strong><br>
            Vous vous êtes déjà demandé ce qui se passerait sur vos économies si une nouvelle crise mondiale éclatait, ou à l'inverse, si une invention révolutionnaire dopait l'économie ? C'est exactement ce que nous vous proposons de découvrir.<br><br>
            <strong>Comment ça marche ?</strong> C'est très simple. Imaginez un scénario économique ou géopolitique, même le plus fou, et tapez-le dans le menu de gauche. Notre intelligence artificielle va décrypter votre idée, et notre moteur mathématique va simuler l'impact de cet événement sur les vrais marchés financiers (Bourse, Or, Pétrole, Crypto). Testez vos théories et observez comment réagirait un vrai portefeuille d'investissement, sans risquer un seul euro !
        </p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. PANNEAU DE CONTRÔLE (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #2c3e50 !important;'>⚙️ Paramètres</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    evenement_libre = st.text_area(
        "🌍 Événement à simuler :", 
        "Les États-Unis annoncent une impression massive de monnaie face à une crise soudaine.",
        height=120
    )
    modele_simu = st.selectbox(
        "🧠 Comportement du marché :", 
        ["Probabiliste (Réaliste)", "Historique (Chocs violents)", "Machine Learning (Tendance)"]
    )
    duree = st.slider("📅 Horizon de temps (Jours) :", min_value=30, max_value=250, value=100, step=10)
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #2c3e50 !important;'>💶 Portefeuille</h3>", unsafe_allow_html=True)
    
    capital_initial = st.number_input(
        "Capital de départ (€) :", 
        min_value=100, 
        max_value=10000000, 
        value=10000, 
        step=500
    )
    
    # NOUVEAU : Sélection du profil de risque
    profil_risque = st.selectbox(
        "🎯 Profil d'Investisseur :",
        ["Prudent (Hyper Sécurisé)", "Équilibré (Normal)", "Agressif (Risqué)"],
        index=1
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    lancer = st.button("📊 Lancer la Simulation", use_container_width=True, type="primary")

# ==========================================
# 4. MOTEUR DE CALCUL & ONGLETS
# ==========================================
tab_dashboard, tab_portefeuille, tab_academie, tab_chat = st.tabs([
    "📈 Dashboard Global", 
    "💼 Mon Portefeuille", 
    "🎓 Académie Financière", 
    "👔 Analyste IA (Chat)"
])

# Variables de session
if "df_simu" not in st.session_state:
    st.session_state.df_simu = None
    st.session_state.perf_df = None
    st.session_state.chocs_ia = None
    st.session_state.perf_totale = None

if lancer:
    st.session_state.df_simu = None 
    
    if len(evenement_libre.strip()) < 10:
        st.warning("⚠️ Votre scénario est trop court. Veuillez décrire un événement économique ou géopolitique plus détaillé.")
    else:
        with st.spinner("L'Analyste IA étudie votre scénario et calcule les probabilités..."):
            try:
                chocs_ia_result = analyser_evenement_macro(evenement_libre)
                
                # J'ai rendu cette vérification un peu moins stricte pour éviter que ça ne bloque trop souvent
                if isinstance(chocs_ia_result, dict) and "erreur" in chocs_ia_result and len(chocs_ia_result) == 1:
                    st.error(f"❌ **Analyse annulée :** {chocs_ia_result['erreur']}\n*Astuce : Essayez de reformuler votre événement de manière un peu plus économique.*")
                elif not chocs_ia_result or ("actifs" not in chocs_ia_result and "macro" not in chocs_ia_result):
                    st.error("❌ **Scénario Non Valide :** L'intelligence artificielle n'a pas pu lier ce scénario à la finance de marché. Veuillez formuler une situation géopolitique, technologique ou macro-économique cohérente.")
                else:
                    st.session_state.chocs_ia = chocs_ia_result
                    st.session_state.df_simu = simuler_marche_dynamique(st.session_state.chocs_ia, jours=duree, modele=modele_simu)
                    
                    perf = ((st.session_state.df_simu.iloc[-1] - st.session_state.df_simu.iloc[0]) / st.session_state.df_simu.iloc[0]) * 100
                    st.session_state.perf_totale = perf
                    
                    perf_df = perf.reset_index()
                    perf_df.columns = ['Actif', 'Performance (%)']
                    
                    perf_df['Actif'] = perf_df['Actif'].apply(lambda x: x.replace("_", " ").replace("EUR USD", "EUR/USD"))
                    st.session_state.perf_df = perf_df.sort_values(by='Performance (%)', ascending=True)
            
            except Exception as e:
                st.error(f"❌ Une erreur technique s'est produite lors de la connexion à l'IA : {e}")

# --- AFFICHAGE SEULEMENT SI TOUT A RÉUSSI ---
if st.session_state.df_simu is not None:
    
    # --- ONGLET 1 : DASHBOARD ---
    with tab_dashboard:
        col_m1, col_m2, col_m3 = st.columns(3)
        inflation_estimee = st.session_state.chocs_ia.get('macro', {}).get('inflation', 0)
        taux_estimes = st.session_state.chocs_ia.get('macro', {}).get('taux_directeurs', 0)
        dynamique = st.session_state.chocs_ia.get('explication_courte', 'Analyse structurelle terminée.')
        
        col_m1.metric("🔥 Impact Inflation (Estimé)", f"{inflation_estimee:+.2f} %")
        col_m2.metric("🏦 Taux Directeurs (Estimé)", f"{taux_estimes:+.2f} %")
        col_m3.info(f"**Conclusion de l'IA :**\n{dynamique}")
        st.markdown("<hr style='border: 1px solid #eaedf1; margin: 20px 0;'>", unsafe_allow_html=True)
        
        df_norm = (st.session_state.df_simu / st.session_state.df_simu.iloc[0]) * 100
        df_norm.columns = [c.replace("_", " ").replace("EUR USD", "EUR/USD") for c in df_norm.columns]
        
        categories = {
            "📊 Actions (Risque & Croissance)": ["S&P 500", "CAC 40"],
            "🛡️ Valeurs Refuges & Monnaies": ["Bons Tresor US 10Y", "EUR/USD"],
            "🛢️ Matières Premières": ["Or", "Petrole"],
            "₿ Cryptomonnaies (Spéculatif)": ["Bitcoin", "Ethereum"]
        }
        
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        grid = [row1_col1, row1_col2, row2_col1, row2_col2]
        
        for i, (titre, liste_actifs) in enumerate(categories.items()):
            with grid[i]:
                actifs_presents = [a for a in liste_actifs if a in df_norm.columns]
                if actifs_presents:
                    fig = px.line(df_norm[actifs_presents], template="plotly_white", title=titre)
                    fig.update_layout(
                        xaxis_title="Jours de cotation", 
                        yaxis_title="Évolution (Base 100)", 
                        height=320, 
                        margin=dict(l=10, r=10, t=40, b=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
                        legend_title_text=""
                    )
                    st.plotly_chart(fig, use_container_width=True)
        st.markdown("<hr style='border: 1px solid #eaedf1; margin: 20px 0;'>", unsafe_allow_html=True)
        
        fig_bar = px.bar(
            st.session_state.perf_df, x='Performance (%)', y='Actif', orientation='h',
            color='Performance (%)', color_continuous_scale='RdYlGn', text='Performance (%)',
            title="📊 Heatmap Sectorielle : Les Gagnants et les Perdants"
        )
        fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto')
        fig_bar.update_layout(template="plotly_white", height=400, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- ONGLET 2 : PORTEFEUILLE ---
    with tab_portefeuille:
        st.markdown(f"<h3 style='text-align: center; color: #2c3e50 !important;'>Votre Portefeuille Institutionnel : {capital_initial:,.0f} €</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #7f8c8d !important; margin-bottom: 30px;'>Profil sélectionné : <strong>{profil_risque}</strong></p>", unsafe_allow_html=True)
        
        # NOUVEAU : Logique de répartition selon le profil
        if profil_risque == "Prudent (Hyper Sécurisé)":
            poids_bruts = {
                "Bons_Tresor_US_10Y": 0.60, "Or": 0.20, "S&P 500": 0.10, "EUR_USD": 0.10,
                "CAC 40": 0.0, "Petrole": 0.0, "Bitcoin": 0.0, "Ethereum": 0.0
            }
        elif profil_risque == "Agressif (Risqué)":
            poids_bruts = {
                "Bitcoin": 0.25, "Ethereum": 0.15, "S&P 500": 0.40, "CAC 40": 0.10,
                "Petrole": 0.10, "Or": 0.0, "Bons_Tresor_US_10Y": 0.0, "EUR_USD": 0.0
            }
        else: # Équilibré (Normal)
            poids_bruts = {
                "S&P 500": 0.30, "CAC 40": 0.10, "Bons_Tresor_US_10Y": 0.30, 
                "Or": 0.15, "Petrole": 0.05, "EUR_USD": 0.05, "Bitcoin": 0.03, "Ethereum": 0.02
            }
            
        # Filtre pour ne garder que les actifs avec un % > 0
        poids = {k: v for k, v in poids_bruts.items() if v > 0}
        
        valeur_finale = 0
        
        # Affichage dynamique en colonnes (s'adapte au nombre d'actifs)
        cols = st.columns(4)
        
        for i, (actif_brut, pct) in enumerate(poids.items()):
            actif_propre = actif_brut.replace("_", " ").replace("EUR USD", "EUR/USD")
            montant_investi = capital_initial * pct
            rendement = (st.session_state.perf_totale.get(actif_brut, 0)) / 100 
            montant_final = montant_investi * (1 + rendement)
            valeur_finale += montant_final
            
            with cols[i % 4]: # Répartit joliment sur 4 colonnes
                st.metric(
                    label=f"{actif_propre} ({pct*100:.0f}%)", 
                    value=f"{montant_final:,.0f} €", 
                    delta=f"{rendement*100:+.2f}%"
                )
                
        st.markdown("<hr style='border: 1px solid #eaedf1; margin: 30px 0;'>", unsafe_allow_html=True)
        
        gains_totaux = valeur_finale - capital_initial
        col_res1, col_res2, col_res3 = st.columns([1, 2, 1])
        with col_res2:
            st.metric(
                label="💰 BILAN NET DU PORTEFEUILLE", 
                value=f"{valeur_finale:,.2f} €", 
                delta=f"{gains_totaux:,.2f} € (Gains/Pertes totaux)"
            )
else:
    with tab_dashboard:
        st.info("👈 Le terminal est en attente. Configurez votre scénario à gauche et cliquez sur 'Lancer la Simulation' pour démarrer l'analyse.")

# ==========================================
# ONGLET 3 : ACADÉMIE (MODE PROFESSEUR)
# ==========================================
with tab_academie:
    st.markdown("<h3 style='color: #2c3e50 !important;'>🎓 Le Cours d'Économie Quant Terminal</h3>", unsafe_allow_html=True)
    st.write("Bienvenue dans l'Académie. En tant que futurs analystes, il est crucial de comprendre la mécanique derrière les graphiques. Lisez attentivement ces concepts, ils sont la base de la finance de marché moderne.")
    
    sub_tab_outils, sub_tab_modeles, sub_tab_macro, sub_tab_lexique = st.tabs([
        "📊 Lire les Données", 
        "🧮 Mathématiques du Marché", 
        "🌍 Les Rouages de la Macro", 
        "📖 Le Lexique du Trader"
    ])
    
    with sub_tab_outils:
        st.markdown("#### 1. L'illusion des prix et la 'Base 100'")
        st.write("""
        L'erreur du débutant est de comparer les prix bruts. Si l'action Apple vaut 170$ et qu'une petite entreprise vaut 2$, laquelle performe le mieux ? Le prix ne nous dit rien. 
        Pour régler ce problème, les professionnels utilisent la **Base 100**. Mathématiquement, on divise tous les prix par leur valeur au Jour 0, et on multiplie par 100. 
        **Le résultat est magique :** tous les actifs démarrent exactement sur la même ligne (à 100). Si la courbe de l'Or finit à 120 et celle du Bitcoin à 90, vous savez instantanément que l'Or a fait +20% et le Bitcoin -10%.
        """)
        
        st.markdown("#### 2. La Heatmap (Carte Thermique)")
        st.write("""
        Sur les marchés, l'argent ne disparaît jamais vraiment, il se *déplace*. La Heatmap est l'outil parfait pour pister l'argent. 
        Si le haut de la Heatmap est vert foncé (ex: Or et Bons du Trésor) et le bas est rouge sang (ex: S&P 500 et Bitcoin), cela prouve que les investisseurs ont paniqué : ils ont vendu leurs actifs risqués pour se cacher dans des actifs sûrs. C'est ce qu'on appelle le *Flight to Quality* (Fuite vers la qualité).
        """)
        
    with sub_tab_modeles:
        st.markdown("#### Comment une machine peut-elle simuler le hasard ?")
        st.write("""
        La bourse est imprévisible à court terme, mais suit des tendances à long terme. Pour recréer cela, Quant Terminal utilise ce qu'on appelle des **Mathématiques Stochastiques** (qui intègrent le hasard).
        """)
        
        st.markdown("**A. Le Modèle Probabiliste (Mouvement Brownien)**")
        st.write("""Imaginez un homme ivre qui essaie de marcher droit vers sa maison. La direction de sa maison est la *tendance* (dictée par notre IA). Mais à chaque pas, l'homme trébuche légèrement à gauche ou à droite. Ce trébuchement s'appelle la *Volatilité*. L'algorithme calcule des milliers de "pas aléatoires" pour créer une courbe boursière réaliste qui tremble au jour le jour, tout en suivant la direction macro-économique.""")
        
        st.markdown("**B. Le Modèle Historique (Les Queues Épaisses)**")
        st.write("""La théorie classique dit qu'un krach boursier de -10% en un jour ne devrait arriver qu'une fois tous les 10 000 ans. Pourtant, cela arrive tous les 10 ans (2001, 2008, 2020...). Les marchés sont irrationnels. Ce modèle reproduit cette peur humaine : il est globalement plus calme, mais a été programmé pour déclencher parfois des "mini-krachs" ou des rebonds violents totalement inattendus.""")
        
    with sub_tab_macro:
        st.markdown("#### Les deux leviers qui contrôlent le monde : Taux et Inflation")
        
        st.markdown("**🏦 Les Banques Centrales (FED, BCE)**")
        st.write("""
        Ce sont les "maîtres du jeu". Elles ont le pouvoir d'imprimer de la monnaie et de fixer les **Taux Directeurs** (le prix de l'argent).
        * **Taux bas (L'argent est gratuit) :** Les entreprises empruntent pour innover, les gens font des crédits pour acheter des maisons. La bourse explose à la hausse. C'est l'euphorie.
        * **Taux hauts (L'argent est cher) :** Le crédit est bloqué. Les entreprises licencient. Pire encore pour la bourse : les investisseurs préfèrent vendre leurs actions pour prêter leur argent à l'État (Bons du Trésor) car cela rapporte beaucoup d'intérêts sans aucun risque de faillite. La bourse s'effondre.
        """)
        
        st.markdown("**🔥 L'Inflation (La taxe invisible)**")
        st.write("""
        Quand l'inflation est à 5%, cela veut dire que vos 100€ sur votre compte en banque perdront 5% de leur pouvoir d'achat cette année. L'argent "fond" sous votre matelas. 
        Pour se protéger, les investisseurs achètent des choses qu'on ne peut pas imprimer à l'infini : des matières premières (Pétrole, Or), de l'immobilier, ou des actions d'entreprises capables d'augmenter leurs prix (comme Apple ou LVMH). L'Or est le rempart millénaire par excellence contre l'inflation.
        """)
        
    with sub_tab_lexique:
        st.markdown("#### Parlez comme un vrai professionnel")
        st.markdown("""
        * **Bull Market (Marché Haussier) :** Un marché très optimiste qui monte fort (le Taureau attaque de bas en haut avec ses cornes).
        * **Bear Market (Marché Baissier) :** Un marché pessimiste qui chute (l'Ours attaque de haut en bas avec sa patte).
        * **Hawkish (Faucon) :** Quand un banquier central parle durement et veut monter les taux d'intérêt pour casser l'économie et tuer l'inflation.
        * **Dovish (Colombe) :** Quand un banquier central veut baisser les taux et aider l'économie à repartir.
        * **Drawdown :** La perte maximale subie par un portefeuille entre son point le plus haut et son point le plus bas. C'est la mesure ultime du risque.
        * **PnL (Profit and Loss) :** Tout simplement l'argent net que vous avez gagné (Profit) ou perdu (Loss) à la fin de la journée.
        """)

# ==========================================
# ONGLET 4 : CHATBOT (ANALYSTE SENIOR)
# ==========================================
with tab_chat:
    st.markdown("<h3 style='text-align: center; color: #2c3e50 !important;'>👔 Bureau de votre Analyste Financier IA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d !important; margin-bottom: 20px;'>Bonjour. Je suis votre analyste senior quantitatif. Posez-moi vos questions sur le marché, la macro-économie, ou l'impact de votre scénario actuel.</p>", unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    question = st.chat_input("Ex: Expliquez-moi en détail pourquoi l'Or a réagi comme cela face à la hausse des taux ?")
    if question:
        st.chat_message("user").markdown(question)
        st.session_state.messages_chat.append({"role": "user", "content": question})
        
        with st.chat_message("assistant"):
            with st.spinner("L'analyste rédige son rapport..."):
                reponse_ia = discuter_avec_ia(st.session_state.messages_chat)
                st.markdown(reponse_ia)
                
        st.session_state.messages_chat.append({"role": "assistant", "content": reponse_ia})
