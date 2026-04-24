import streamlit as st
import pandas as pd
import plotly.express as px
from simulation import simuler_marche_dynamique
from ia_bot import analyser_evenement_macro, discuter_avec_ia


# ==========================================
# 0. CATALOGUE DES ACTIFS
# ==========================================

ACTIFS_DISPONIBLES = {
    "📊 Actions & Indices": {
        "S&P 500":               "S&P 500",
        "NASDAQ 100":            "NASDAQ",
        "CAC 40":                "CAC 40",
        "MSCI World":            "MSCI_World",
        "Marchés Émergents":     "Emerging_Markets",
    },
    "🛡️ Obligations d'État": {
        "Bons Trésor US 10Y":    "Bons_Tresor_US_10Y",
        "Bund Allemagne 10Y":    "Bund_10Y",
        "OAT France 10Y":        "OAT_10Y",
        "JGB Japon 10Y":         "JGB_10Y",
        "Gilt UK 10Y":           "Gilt_10Y",
    },
    "💱 Devises & Volatilité": {
        "EUR/USD":               "EUR_USD",
        "Dollar Index (DXY)":    "Dollar_Index",
        "VIX (Indice de Peur)":  "VIX",
    },
    "🛢️ Matières Premières": {
        "Or":                    "Or",
        "Argent":                "Argent",
        "Pétrole (WTI)":         "Petrole",
        "Cuivre":                "Cuivre",
        "ETF Terres Rares":      "ETF_Terres_Rares",
    },
    "📡 Sectoriels": {
        "ETF Défense":           "ETF_Defense",
    },
    "₿ Cryptomonnaies": {
        "Bitcoin":               "Bitcoin",
        "Ethereum":              "Ethereum",
        "XRP":                   "XRP",
        "Solana":                "Solana",
    },
}

NOM_AFFICHAGE = {v: k for cat in ACTIFS_DISPONIBLES.values() for k, v in cat.items()}

ACTIFS_PAR_DEFAUT = {
    "S&P 500", "CAC 40", "Bons_Tresor_US_10Y",
    "EUR_USD", "Or", "Petrole", "Bitcoin", "Ethereum"
}

CATEGORIES_GRAPHIQUES = {
    "📊 Actions & Indices":     ["S&P 500", "NASDAQ", "CAC 40", "MSCI_World", "Emerging_Markets"],
    "🛡️ Obligations d'État":    ["Bons_Tresor_US_10Y", "Bund_10Y", "OAT_10Y", "JGB_10Y", "Gilt_10Y"],
    "💱 Devises & Volatilité":  ["EUR_USD", "Dollar_Index", "VIX"],
    "🛢️ Matières Premières":   ["Or", "Argent", "Petrole", "Cuivre", "ETF_Terres_Rares"],
    "📡 Sectoriels":            ["ETF_Defense"],
    "₿ Cryptomonnaies":        ["Bitcoin", "Ethereum", "XRP", "Solana"],
}


# ==========================================
# 1. CONFIGURATION DE LA PAGE & CSS
# ==========================================

st.set_page_config(page_title="Quant Terminal", page_icon="💠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9 !important; }
    .stMarkdown, .stText, p, li, h1, h2, h3, h4, h5, h6, label { color: #2c3e50 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; }
    [data-testid="stSidebar"] * { color: #2c3e50 !important; }
    [data-testid="stMetricValue"] { color: #2c3e50 !important; }
    [data-testid="stMetricLabel"] * { color: #7f8c8d !important; }

    .block-container {
        padding-top: 2rem; padding-bottom: 2rem;
        padding-left: 3rem; padding-right: 3rem;
        max-width: 1600px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid #eaedf1 !important;
        padding: 15px; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        border-radius: 8px; padding: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        flex-grow: 1; text-align: center;
        font-weight: 600; color: #2c3e50 !important;
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
            <strong>Comment ça marche ?</strong> Imaginez un scénario économique ou géopolitique, choisissez les actifs à analyser, et définissez votre portefeuille. Notre IA décrypte votre scénario, notre moteur mathématique simule l'impact sur les marchés, et vous voyez comment réagit votre portefeuille — sans risquer un seul euro.
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

    # ---- SÉLECTION DES ACTIFS ----
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #2c3e50 !important;'>🎯 Actifs à Analyser</h3>", unsafe_allow_html=True)
    st.caption("Cochez les actifs à inclure dans la simulation.")

    actifs_selectionnes = []
    for categorie, actifs_cat in ACTIFS_DISPONIBLES.items():
        with st.expander(categorie, expanded=False):
            for nom_affiche, sim_key in actifs_cat.items():
                if st.checkbox(nom_affiche, value=(sim_key in ACTIFS_PAR_DEFAUT), key=f"chk_{sim_key}"):
                    actifs_selectionnes.append(sim_key)

    if not actifs_selectionnes:
        st.warning("⚠️ Sélectionnez au moins un actif.")

    # ---- PORTEFEUILLE ----
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #2c3e50 !important;'>💶 Portefeuille</h3>", unsafe_allow_html=True)

    capital_initial = st.number_input(
        "Capital de départ (€) :",
        min_value=100, max_value=10000000, value=10000, step=500
    )

    profil_risque = st.selectbox(
        "🎯 Profil d'Investisseur :",
        ["Prudent (Hyper Sécurisé)", "Équilibré (Normal)", "Agressif (Risqué)", "Personnalisé"],
        index=1
    )

    # ---- ALLOCATION PERSONNALISÉE ----
    allocations_custom = {}
    if profil_risque == "Personnalisé":
        if actifs_selectionnes:
            st.markdown("**Répartition (%)**")
            st.caption("La somme doit être égale à 100%.")
            total_alloc = 0
            defaut_pct = round(100 / len(actifs_selectionnes))
            for sim_key in actifs_selectionnes:
                label = NOM_AFFICHAGE.get(sim_key, sim_key)
                val = st.number_input(
                    label, min_value=0, max_value=100,
                    value=defaut_pct, step=1,
                    key=f"alloc_{sim_key}"
                )
                allocations_custom[sim_key] = val
                total_alloc += val

            couleur = "#27ae60" if total_alloc == 100 else "#e74c3c"
            icone = "✅" if total_alloc == 100 else "⚠️"
            st.markdown(
                f"<div style='text-align:center; margin-top:8px;'>"
                f"<span style='background:{couleur}; color:white; padding:4px 12px; "
                f"border-radius:12px; font-weight:700;'>{icone} Total : {total_alloc}%</span></div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Sélectionnez d'abord des actifs.")

    st.markdown("<br>", unsafe_allow_html=True)
    lancer = st.button("📊 Lancer la Simulation", use_container_width=True, type="primary")


# ==========================================
# 4. ONGLETS
# ==========================================

tab_dashboard, tab_portefeuille, tab_academie, tab_chat = st.tabs([
    "📈 Dashboard Global",
    "💼 Mon Portefeuille",
    "🎓 Académie Financière",
    "👔 Analyste IA (Chat)"
])

# État de session
if "df_simu" not in st.session_state:
    st.session_state.df_simu = None
    st.session_state.perf_df = None
    st.session_state.chocs_ia = None
    st.session_state.perf_totale = None
    st.session_state.actifs_sim = []
    st.session_state.allocations_sim = {}
    st.session_state.profil_sim = None
    st.session_state.capital_sim = 10000


# ==========================================
# 5. MOTEUR DE SIMULATION
# ==========================================

if lancer:
    st.session_state.df_simu = None

    if len(evenement_libre.strip()) < 10:
        st.warning("⚠️ Votre scénario est trop court. Décrivez un événement économique ou géopolitique plus détaillé.")
    elif not actifs_selectionnes:
        st.warning("⚠️ Veuillez sélectionner au moins un actif à analyser.")
    elif profil_risque == "Personnalisé" and sum(allocations_custom.values()) != 100:
        st.warning(f"⚠️ L'allocation personnalisée doit totaliser 100% (actuellement {sum(allocations_custom.values())}%).")
    else:
        with st.spinner("L'Analyste IA étudie votre scénario et calcule les probabilités..."):
            try:
                chocs_ia_result = analyser_evenement_macro(evenement_libre)

                if isinstance(chocs_ia_result, dict) and "erreur" in chocs_ia_result and len(chocs_ia_result) == 1:
                    st.error(f"❌ **Analyse annulée :** {chocs_ia_result['erreur']}")
                elif not chocs_ia_result or ("actifs" not in chocs_ia_result and "macro" not in chocs_ia_result):
                    st.error("❌ **Scénario Non Valide :** L'IA n'a pas pu lier ce scénario à la finance de marché.")
                else:
                    st.session_state.chocs_ia = chocs_ia_result
                    st.session_state.df_simu = simuler_marche_dynamique(
                        st.session_state.chocs_ia,
                        jours=duree,
                        modele=modele_simu,
                        actifs=actifs_selectionnes
                    )

                    perf = ((st.session_state.df_simu.iloc[-1] - st.session_state.df_simu.iloc[0]) / st.session_state.df_simu.iloc[0]) * 100
                    st.session_state.perf_totale = perf

                    perf_df = perf.reset_index()
                    perf_df.columns = ['Actif', 'Performance (%)']
                    perf_df['Actif'] = perf_df['Actif'].apply(
                        lambda x: NOM_AFFICHAGE.get(x, x.replace("_", " ").replace("EUR USD", "EUR/USD"))
                    )
                    st.session_state.perf_df = perf_df.sort_values(by='Performance (%)', ascending=True)

                    st.session_state.actifs_sim = actifs_selectionnes.copy()
                    st.session_state.allocations_sim = allocations_custom.copy()
                    st.session_state.profil_sim = profil_risque
                    st.session_state.capital_sim = capital_initial

            except Exception as e:
                st.error(f"❌ Erreur technique : {e}")


# ==========================================
# 6. AFFICHAGE RÉSULTATS
# ==========================================

if st.session_state.df_simu is not None:

    # --- DASHBOARD ---
    with tab_dashboard:
        col_m1, col_m2, col_m3 = st.columns(3)
        inflation_estimee = st.session_state.chocs_ia.get('macro', {}).get('inflation', 0)
        taux_estimes      = st.session_state.chocs_ia.get('macro', {}).get('taux_directeurs', 0)
        dynamique         = st.session_state.chocs_ia.get('explication_courte', 'Analyse terminée.')

        col_m1.metric("🔥 Impact Inflation (Estimé)", f"{inflation_estimee:+.2f} %")
        col_m2.metric("🏦 Taux Directeurs (Estimé)", f"{taux_estimes:+.2f} %")
        col_m3.info(f"**Conclusion de l'IA :**\n{dynamique}")
        st.markdown("<hr style='border: 1px solid #eaedf1; margin: 20px 0;'>", unsafe_allow_html=True)

        # Base 100
        df_norm = (st.session_state.df_simu / st.session_state.df_simu.iloc[0]) * 100
        df_norm.columns = [
            NOM_AFFICHAGE.get(c, c.replace("_", " ").replace("EUR USD", "EUR/USD"))
            for c in df_norm.columns
        ]

        # Un graphique par catégorie
        graphiques = []
        for titre_cat, sim_keys_cat in CATEGORIES_GRAPHIQUES.items():
            actifs_dispo = [
                NOM_AFFICHAGE.get(sk, sk.replace("_", " ").replace("EUR USD", "EUR/USD"))
                for sk in sim_keys_cat if sk in st.session_state.actifs_sim
            ]
            actifs_dispo = [a for a in actifs_dispo if a in df_norm.columns]
            if actifs_dispo:
                graphiques.append((titre_cat, actifs_dispo))

        for i in range(0, len(graphiques), 2):
            cols = st.columns(2)
            for j, (titre_cat, actifs_dispo) in enumerate(graphiques[i:i+2]):
                with cols[j]:
                    fig = px.line(df_norm[actifs_dispo], template="plotly_white", title=titre_cat)
                    fig.update_layout(
                        xaxis_title="Jours de cotation",
                        yaxis_title="Évolution (Base 100)",
                        height=340,
                        margin=dict(l=10, r=10, t=45, b=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="center", x=0.5),
                        legend_title_text=""
                    )
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("<hr style='border: 1px solid #eaedf1; margin: 20px 0;'>", unsafe_allow_html=True)

        # Heatmap
        fig_bar = px.bar(
            st.session_state.perf_df,
            x='Performance (%)', y='Actif', orientation='h',
            color='Performance (%)', color_continuous_scale='RdYlGn', text='Performance (%)',
            title="📊 Heatmap : Les Gagnants et les Perdants"
        )
        fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto')
        fig_bar.update_layout(
            template="plotly_white",
            height=max(350, 30 * len(st.session_state.perf_df) + 80),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- PORTEFEUILLE ---
    with tab_portefeuille:
        cap = st.session_state.capital_sim
        profil = st.session_state.profil_sim
        actifs_sim = st.session_state.actifs_sim

        st.markdown(f"<h3 style='text-align: center; color: #2c3e50 !important;'>Votre Portefeuille : {cap:,.0f} €</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #7f8c8d !important; margin-bottom: 30px;'>Profil sélectionné : <strong>{profil}</strong></p>", unsafe_allow_html=True)

        if profil == "Personnalisé":
            alloc = st.session_state.allocations_sim
            total_alloc = sum(alloc.values()) or 1
            poids = {k: v / total_alloc for k, v in alloc.items() if v > 0}

        elif profil == "Prudent (Hyper Sécurisé)":
            poids_bruts = {
                "Bons_Tresor_US_10Y": 0.50, "Or": 0.20,
                "S&P 500": 0.10, "EUR_USD": 0.10,
                "Bund_10Y": 0.05, "OAT_10Y": 0.05,
            }
            poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}

        elif profil == "Agressif (Risqué)":
            poids_bruts = {
                "Bitcoin": 0.20, "Ethereum": 0.10, "XRP": 0.05, "Solana": 0.05,
                "S&P 500": 0.30, "NASDAQ": 0.15,
                "CAC 40": 0.05, "Petrole": 0.05, "ETF_Defense": 0.05,
            }
            poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}

        else:  # Équilibré
            poids_bruts = {
                "S&P 500": 0.25, "CAC 40": 0.08, "NASDAQ": 0.07,
                "Bons_Tresor_US_10Y": 0.25, "Or": 0.12,
                "Petrole": 0.05, "EUR_USD": 0.05,
                "Bitcoin": 0.08, "Ethereum": 0.05,
            }
            poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}

        total_poids = sum(poids.values())
        if total_poids > 0:
            poids = {k: v / total_poids for k, v in poids.items()}
        if not poids and actifs_sim:
            poids = {k: 1 / len(actifs_sim) for k in actifs_sim}

        valeur_finale = 0
        cols_port = st.columns(4)

        for i, (sim_key, pct) in enumerate(poids.items()):
            nom_propre = NOM_AFFICHAGE.get(sim_key, sim_key.replace("_", " ").replace("EUR USD", "EUR/USD"))
            montant_investi = cap * pct
            rendement = (st.session_state.perf_totale.get(sim_key, 0)) / 100
            montant_final = montant_investi * (1 + rendement)
            valeur_finale += montant_final

            with cols_port[i % 4]:
                st.metric(
                    label=f"{nom_propre} ({pct*100:.1f}%)",
                    value=f"{montant_final:,.0f} €",
                    delta=f"{rendement*100:+.2f}%"
                )

        st.markdown("<hr style='border: 1px solid #eaedf1; margin: 30px 0;'>", unsafe_allow_html=True)

        if poids:
            col_pie, col_bilan = st.columns([1, 1])
            with col_pie:
                pie_df = pd.DataFrame({
                    "Actif": [NOM_AFFICHAGE.get(k, k) for k in poids.keys()],
                    "Poids": [v * 100 for v in poids.values()]
                })
                fig_pie = px.pie(
                    pie_df, names="Actif", values="Poids",
                    title="🥧 Répartition du portefeuille",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(
                    template="plotly_white", height=320,
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend=dict(orientation="v", x=1.0, y=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_bilan:
                st.markdown("<br><br>", unsafe_allow_html=True)
                gains_totaux = valeur_finale - cap
                st.metric(
                    label="💰 BILAN NET DU PORTEFEUILLE",
                    value=f"{valeur_finale:,.2f} €",
                    delta=f"{gains_totaux:,.2f} € (Gains/Pertes totaux)"
                )
                perf_globale = (gains_totaux / cap) * 100 if cap > 0 else 0
                st.metric(label="📈 Performance Globale", value=f"{perf_globale:+.2f} %")

else:
    with tab_dashboard:
        st.info("👈 Le terminal est en attente. Configurez votre scénario et cliquez sur 'Lancer la Simulation'.")


# ==========================================
# 7. ACADÉMIE
# ==========================================

with tab_academie:
    st.markdown("<h3 style='color: #2c3e50 !important;'>🎓 Le Cours d'Économie Quant Terminal</h3>", unsafe_allow_html=True)
    st.write("Bienvenue dans l'Académie. Comprenez la mécanique derrière les graphiques — ces concepts sont la base de la finance de marché moderne.")

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
        Pour régler ce problème, les professionnels utilisent la **Base 100**. On divise tous les prix par leur valeur au Jour 0, et on multiplie par 100.
        **Le résultat est magique :** tous les actifs démarrent sur la même ligne (à 100). Si la courbe de l'Or finit à 120 et celle du Bitcoin à 90, vous savez instantanément que l'Or a fait +20% et le Bitcoin -10%.
        """)

        st.markdown("#### 2. La Heatmap (Carte Thermique)")
        st.write("""
        Sur les marchés, l'argent ne disparaît jamais, il se *déplace*. La Heatmap permet de pister l'argent.
        Si le haut est vert foncé (Or, Bons du Trésor) et le bas rouge sang (S&P 500, Bitcoin), cela prouve que les investisseurs ont paniqué : ils ont vendu leurs actifs risqués pour se cacher dans des actifs sûrs. C'est le *Flight to Quality*.
        """)

    with sub_tab_modeles:
        st.markdown("#### Comment une machine peut-elle simuler le hasard ?")
        st.write("""
        La bourse est imprévisible à court terme, mais suit des tendances à long terme. Quant Terminal utilise des **Mathématiques Stochastiques** (qui intègrent le hasard).
        """)

        st.markdown("**A. Le Modèle Probabiliste (Mouvement Brownien)**")
        st.write("""Imaginez un homme ivre qui essaie de marcher droit vers sa maison. La direction de sa maison est la *tendance* (dictée par notre IA). Mais à chaque pas, il trébuche légèrement : c'est la *Volatilité*. L'algorithme crée une courbe réaliste qui tremble au jour le jour tout en suivant la direction macro-économique.""")

        st.markdown("**B. Le Modèle Historique (Les Queues Épaisses)**")
        st.write("""La théorie classique dit qu'un krach de -10% en un jour ne devrait arriver qu'une fois tous les 10 000 ans. Pourtant, cela arrive tous les 10 ans (2001, 2008, 2020...). Ce modèle reproduit cette irrationalité : il est calme en moyenne mais déclenche parfois des "mini-krachs" ou rebonds violents inattendus.""")

    with sub_tab_macro:
        st.markdown("#### Les deux leviers qui contrôlent le monde : Taux et Inflation")

        st.markdown("**🏦 Les Banques Centrales (FED, BCE)**")
        st.write("""
        * **Taux bas (argent gratuit) :** Les entreprises empruntent, les gens font des crédits. La bourse explose à la hausse.
        * **Taux hauts (argent cher) :** Le crédit est bloqué. Les investisseurs préfèrent prêter à l'État (Bons du Trésor) qui rapporte sans risque. La bourse s'effondre.
        """)

        st.markdown("**🔥 L'Inflation (la taxe invisible)**")
        st.write("""
        Avec une inflation à 5%, vos 100€ perdent 5% de pouvoir d'achat cette année. Pour se protéger, on achète des actifs qu'on ne peut pas imprimer : matières premières (Or, Pétrole, Argent, Cuivre), immobilier, ou actions d'entreprises qui peuvent augmenter leurs prix.
        """)

    with sub_tab_lexique:
        st.markdown("#### Parlez comme un vrai professionnel")
        st.markdown("""
        * **Bull Market (Marché Haussier) :** Marché optimiste qui monte (le Taureau attaque de bas en haut).
        * **Bear Market (Marché Baissier) :** Marché pessimiste qui chute (l'Ours attaque de haut en bas).
        * **Hawkish (Faucon) :** Banquier central qui veut monter les taux pour tuer l'inflation.
        * **Dovish (Colombe) :** Banquier central qui veut baisser les taux pour relancer l'économie.
        * **Drawdown :** Perte maximale subie entre un point haut et un point bas. Mesure ultime du risque.
        * **PnL (Profit and Loss) :** Argent net gagné (Profit) ou perdu (Loss).
        * **DXY (Dollar Index) :** Force du dollar face à un panier de 6 devises. DXY haut = dollar fort = pression sur l'or et les émergents.
        * **VIX (Indice de Peur) :** Volatilité attendue du S&P 500. Au-dessus de 30 = panique. En dessous de 15 = euphorie.
        * **ETF (Exchange Traded Fund) :** Fonds coté en bourse qui réplique un indice ou secteur (ex: ETF Défense = panier de sociétés d'armement).
        """)


# ==========================================
# 8. CHATBOT
# ==========================================

with tab_chat:
    st.markdown("<h3 style='text-align: center; color: #2c3e50 !important;'>👔 Bureau de votre Analyste Financier IA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d !important; margin-bottom: 20px;'>Posez vos questions sur le marché, la macro-économie, ou l'impact de votre scénario.</p>", unsafe_allow_html=True)

    for message in st.session_state.messages_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ex: Pourquoi l'Or a réagi comme cela face à la hausse des taux ?")
    if question:
        st.chat_message("user").markdown(question)
        st.session_state.messages_chat.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("L'analyste rédige son rapport..."):
                reponse_ia = discuter_avec_ia(st.session_state.messages_chat)
                st.markdown(reponse_ia)

        st.session_state.messages_chat.append({"role": "assistant", "content": reponse_ia})
