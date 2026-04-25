import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from simulation import simuler_marche_dynamique, simuler_monte_carlo
from ia_bot import analyser_evenement_macro, discuter_avec_ia
from market_data import (
    get_prix_actuels, get_historique, get_volatilites_historiques,
    EVENEMENTS_HISTORIQUES, TICKERS_YAHOO
)
from pdf_generator import generer_rapport_pdf


# ==========================================
# 0. CATALOGUE DES ACTIFS
# ==========================================

ACTIFS_DISPONIBLES = {
    "Actions & Indices": {
        "S&P 500":               "S&P 500",
        "NASDAQ 100":            "NASDAQ",
        "CAC 40":                "CAC 40",
        "MSCI World":            "MSCI_World",
        "Marchés Émergents":     "Emerging_Markets",
    },
    "Obligations d'État": {
        "Bons Trésor US 10Y":    "Bons_Tresor_US_10Y",
        "Bund Allemagne 10Y":    "Bund_10Y",
        "OAT France 10Y":        "OAT_10Y",
        "JGB Japon 10Y":         "JGB_10Y",
        "Gilt UK 10Y":           "Gilt_10Y",
    },
    "Devises & Volatilité": {
        "EUR/USD":               "EUR_USD",
        "Dollar Index (DXY)":    "Dollar_Index",
        "VIX (Indice de Peur)":  "VIX",
    },
    "Matières Premières": {
        "Or":                    "Or",
        "Argent":                "Argent",
        "Pétrole (WTI)":         "Petrole",
        "Cuivre":                "Cuivre",
        "ETF Terres Rares":      "ETF_Terres_Rares",
    },
    "Sectoriels": {
        "ETF Défense":           "ETF_Defense",
    },
    "Cryptomonnaies": {
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
    "Actions & Indices":     ["S&P 500", "NASDAQ", "CAC 40", "MSCI_World", "Emerging_Markets"],
    "Obligations d'État":    ["Bons_Tresor_US_10Y", "Bund_10Y", "OAT_10Y", "JGB_10Y", "Gilt_10Y"],
    "Devises & Volatilité":  ["EUR_USD", "Dollar_Index", "VIX"],
    "Matières Premières":    ["Or", "Argent", "Petrole", "Cuivre", "ETF_Terres_Rares"],
    "Sectoriels":            ["ETF_Defense"],
    "Cryptomonnaies":        ["Bitcoin", "Ethereum", "XRP", "Solana"],
}

EVENEMENTS_PRESETS = {
    "Guerre mondiale":       "Une guerre majeure éclate entre plusieurs grandes puissances, provoquant une mobilisation mondiale et une explosion des dépenses militaires.",
    "Pandémie mondiale":     "Un nouveau virus très contagieux se propage rapidement dans le monde, entraînant des confinements massifs et un arrêt partiel de l'économie mondiale.",
    "Révolution IA":         "Une intelligence artificielle générale (AGI) est annoncée par une grande entreprise tech, remplaçant une large part des emplois intellectuels en quelques années.",
    "Krach 2008 bis":        "Une crise bancaire majeure éclate aux États-Unis avec la faillite de plusieurs grandes banques, provoquant une panique financière mondiale.",
    "Fusion nucléaire":      "Des chercheurs annoncent la maîtrise industrielle de la fusion nucléaire, promettant une énergie illimitée et bon marché d'ici 5 ans.",
    "Choc pétrolier":        "Un conflit au Moyen-Orient coupe 30% de la production mondiale de pétrole, faisant exploser les prix de l'énergie.",
    "Hausse brutale FED":    "La FED annonce une hausse surprise des taux directeurs de +2% pour combattre une inflation hors de contrôle.",
    "Crise Chine-Taïwan":    "La Chine impose un blocus militaire autour de Taïwan, paralysant la production mondiale de semi-conducteurs.",
}


# ==========================================
# 1. CONFIG & CSS (avec corrections contraste)
# ==========================================

st.set_page_config(page_title="Quant Terminal", page_icon="◆", layout="wide")

st.markdown("""
<style>
:root {
    --primary:   #1a365d;
    --secondary: #2c5282;
    --accent:    #319795;
    --bg:        #f7fafc;
    --card:      #ffffff;
    --border:    #cbd5e0;       /* ⬅ plus foncé pour mieux voir les cadres */
    --border-strong: #a0aec0;   /* ⬅ pour les bords plus marqués */
    --text:      #2d3748;
    --muted:     #718096;
    --success:   #2f855a;
    --danger:    #c53030;
}

.stApp { background-color: var(--bg) !important; }
.stMarkdown, .stText, p, li, label, span, div { color: var(--text); }
h1, h2, h3, h4, h5, h6 { color: var(--primary) !important; font-weight: 700; }

[data-testid="stSidebar"] {
    background-color: var(--card) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--primary) !important;
}

[data-testid="stMetricValue"] { color: var(--primary) !important; font-weight: 700; }
[data-testid="stMetricLabel"] * { color: var(--muted) !important; font-weight: 500; }
[data-testid="stMetricDelta"] { font-weight: 600; }

div[data-testid="metric-container"] {
    background-color: var(--card) !important;
    border: 1px solid var(--border-strong) !important;   /* ⬅ bordure plus visible */
    padding: 16px 18px;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);              /* ⬅ ombre plus marquée */
    transition: all 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 4px 14px rgba(49,151,149,0.15);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1600px;
}
#MainMenu, footer { visibility: hidden; }

.stTabs [data-baseweb="tab-list"] {
    background-color: var(--card) !important;
    border-radius: 10px;
    padding: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 24px;
    border: 1px solid var(--border-strong);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    flex-grow: 1;
    text-align: center;
    font-weight: 600;
    color: var(--muted) !important;
    border-radius: 6px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background-color: var(--primary) !important;
    color: white !important;
}
.stTabs [aria-selected="true"] p { color: white !important; }

.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s;
    border: 1px solid var(--border-strong);
}
.stButton > button[kind="primary"] {
    background: var(--primary) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--secondary) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(26,54,93,0.25);
}

.streamlit-expanderHeader {
    font-weight: 600;
    color: var(--text) !important;
    background-color: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Inputs avec contraste correct */
.stTextArea textarea, .stTextInput input, .stNumberInput input {
    border-radius: 8px;
    border: 1px solid var(--border-strong) !important;
    color: var(--text) !important;
    background-color: #ffffff !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder {
    color: #a0aec0 !important;
}
.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1px solid var(--border-strong) !important;
    background-color: #ffffff !important;
    color: var(--text) !important;
}
.stSelectbox > div > div * { color: var(--text) !important; }

[data-baseweb="popover"] li,
[data-baseweb="popover"] div {
    color: var(--text) !important;
}
[data-baseweb="popover"] [aria-selected="true"] {
    background-color: #ebf8ff !important;
    color: var(--primary) !important;
}

.stSlider [data-baseweb="slider"] { color: var(--text) !important; }
.stSlider label, .stSlider span { color: var(--text) !important; }

.stCheckbox label, .stCheckbox label p { color: var(--text) !important; }

/* CHAT INPUT — fix curseur visible */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input,
.stChatInput textarea,
.stChatInputContainer textarea {
    color: var(--text) !important;
    background-color: #ffffff !important;
    caret-color: var(--primary) !important;       /* ⬅ curseur visible */
    border: 2px solid var(--accent) !important;   /* ⬅ bordure colorée pour repérer */
    border-radius: 8px !important;
}
[data-testid="stChatInput"] textarea:focus,
.stChatInput textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(49,151,149,0.15) !important;
    outline: none !important;
}
[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {
    color: #718096 !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    color: var(--text) !important;
    background-color: #ffffff !important;
}

/* Cards — bordures plus visibles */
.qt-card {
    background: var(--card);
    border: 1px solid var(--border-strong);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.qt-card-intro {
    background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
    border-left: 4px solid var(--accent);
    border-top: 1px solid var(--border-strong);
    border-right: 1px solid var(--border-strong);
    border-bottom: 1px solid var(--border-strong);
    padding: 28px 32px;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 24px;
    color: var(--text);
    line-height: 1.7;
}
.qt-card-intro p { color: var(--text); }
.qt-tag {
    font-size: 0.75em;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 12px;
}
.qt-section-title {
    color: var(--primary) !important;
    font-weight: 700;
    font-size: 1.25em;
    margin-top: 8px;
    margin-bottom: 4px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border-strong);
}
.qt-divider {
    border: none;
    border-top: 1px solid var(--border-strong);
    margin: 28px 0;
}
.qt-callout {
    background: #ebf8ff;
    border: 1px solid #90cdf4;
    border-left: 4px solid var(--accent);
    padding: 14px 18px;
    border-radius: 8px;
    margin: 12px 0;
    color: var(--text);
}
.qt-callout-warn {
    background: #fffaf0;
    border: 1px solid #f6ad55;
    border-left: 4px solid #d69e2e;
    padding: 14px 18px;
    border-radius: 8px;
    margin: 12px 0;
    color: var(--text);
}
.qt-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78em;
    font-weight: 600;
    background: #edf2f7;
    color: var(--primary);
    margin-right: 6px;
}
.qt-live-badge {
    display: inline-block;
    background: #2f855a;
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-left: 8px;
}

/* Bande santé du marché */
.market-strip {
    background: linear-gradient(90deg, #1a365d 0%, #2c5282 100%);
    border-radius: 10px;
    padding: 12px 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(26,54,93,0.2);
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
    color: white;
    font-size: 0.9em;
}
.market-strip-item {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 110px;
}
.market-strip-label {
    font-size: 0.7em;
    opacity: 0.75;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}
.market-strip-value {
    font-size: 1.05em;
    font-weight: 700;
    color: white;
}
.market-strip-tag {
    background: rgba(255,255,255,0.15);
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.7em;
    font-weight: 700;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. ÉTAT DE SESSION
# ==========================================

if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []
if "event_text_A" not in st.session_state:
    st.session_state.event_text_A = "Les États-Unis annoncent une impression massive de monnaie face à une crise soudaine."
if "event_text_B" not in st.session_state:
    st.session_state.event_text_B = "Une percée majeure dans l'intelligence artificielle dope la productivité mondiale."
if "historique_simus" not in st.session_state:
    st.session_state.historique_simus = []
if "simu_A" not in st.session_state:
    st.session_state.simu_A = None
if "simu_B" not in st.session_state:
    st.session_state.simu_B = None
if "mode_comparaison" not in st.session_state:
    st.session_state.mode_comparaison = False
if "params_sim" not in st.session_state:
    st.session_state.params_sim = {}
if "backtest_data" not in st.session_state:
    st.session_state.backtest_data = None


def set_event_A(t): st.session_state.event_text_A = t
def set_event_B(t): st.session_state.event_text_B = t


# ==========================================
# 3. EN-TÊTE + BANDE SANTÉ MARCHÉ
# ==========================================

st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 14px;">
    <div style="width: 52px; height: 52px; background: linear-gradient(135deg, #1a365d, #319795); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; font-weight: 800; box-shadow: 0 4px 14px rgba(26,54,93,0.2);">
        QT
    </div>
    <h1 style="margin: 0; padding: 0; font-size: 2.4em; color: #1a365d !important; font-weight: 800; letter-spacing: -0.5px;">Quant Terminal</h1>
</div>
<p style="text-align:center; color:#718096; font-size:0.95em; margin-bottom:20px; letter-spacing:0.5px;">
    Simulation de marché pilotée par IA · Connecté aux marchés en direct
</p>
""", unsafe_allow_html=True)


# Bande santé du marché (live tickers)
def afficher_bande_marche():
    """Affiche une bande horizontale avec les principaux indicateurs live."""
    try:
        actifs_strip = ["S&P 500", "VIX", "Or", "Petrole", "Bitcoin", "EUR_USD"]
        prix, _ = get_prix_actuels(actifs_strip)

        items_html = '<div class="market-strip-tag">⬤ LIVE</div>'
        labels_courts = {
            "S&P 500": "S&P 500",
            "VIX": "VIX",
            "Or": "OR ($/oz)",
            "Petrole": "PÉTROLE ($)",
            "Bitcoin": "BTC ($)",
            "EUR_USD": "EUR/USD",
        }
        formats = {
            "S&P 500": "{:,.0f}",
            "VIX": "{:.2f}",
            "Or": "{:,.0f}",
            "Petrole": "{:.2f}",
            "Bitcoin": "{:,.0f}",
            "EUR_USD": "{:.4f}",
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

afficher_bande_marche()


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


# ==========================================
# 4. SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("### Paramètres")

    # Bouton recharger les prix
    if st.button("🔄 Recharger les prix Yahoo", use_container_width=True,
                 help="Force un rafraîchissement des prix de marché (cache 1h sinon)."):
        get_prix_actuels.clear()
        get_volatilites_historiques.clear()
        st.rerun()

    st.markdown("---")

    mode_app = st.radio(
        "Mode du terminal",
        ["Simulation prospective", "Backtest historique"],
        help="Simulation : teste un scénario fictif. Backtest : rejoue les vraies données passées."
    )
    st.markdown("---")

    if mode_app == "Simulation prospective":
        mode_comparaison = st.toggle(
            "Mode Comparaison (2 scénarios)",
            value=st.session_state.mode_comparaison
        )
        st.session_state.mode_comparaison = mode_comparaison

        if mode_comparaison:
            st.markdown("**Scénario A**")
            st.text_area("Scénario A", height=100, key="event_text_A", label_visibility="collapsed")
            st.markdown("**Scénario B**")
            st.text_area("Scénario B", height=100, key="event_text_B", label_visibility="collapsed")
        else:
            st.markdown("**Scénarios rapides**")
            preset_keys = list(EVENEMENTS_PRESETS.keys())
            for i in range(0, len(preset_keys), 2):
                col1, col2 = st.columns(2)
                with col1:
                    if i < len(preset_keys):
                        st.button(preset_keys[i], key=f"preset_{i}",
                                  on_click=set_event_A,
                                  args=(EVENEMENTS_PRESETS[preset_keys[i]],),
                                  use_container_width=True)
                with col2:
                    if i + 1 < len(preset_keys):
                        st.button(preset_keys[i + 1], key=f"preset_{i+1}",
                                  on_click=set_event_A,
                                  args=(EVENEMENTS_PRESETS[preset_keys[i + 1]],),
                                  use_container_width=True)
            st.markdown("**Événement à simuler**")
            st.text_area("Événement", height=120, key="event_text_A", label_visibility="collapsed")

        st.markdown("---")
        modele_simu = st.selectbox(
            "Comportement du marché",
            ["Probabiliste (Réaliste)", "Historique (Chocs violents)", "Machine Learning (Tendance)"]
        )
        duree = st.slider("Horizon (jours de cotation)", 30, 250, 100, 10)
        mode_monte_carlo = st.checkbox("Mode Monte-Carlo (50 simulations)", value=False)
        utiliser_prix_reels = st.checkbox(
            "Utiliser les prix de marché actuels", value=True,
            help="Récupère les prix réels via Yahoo Finance comme point de départ."
        )
        calibration_historique = st.checkbox(
            "Calibration historique (IA)", value=True,
            help="L'IA s'inspire des amplitudes réelles de 2008, COVID, etc."
        )

    else:  # Backtest
        st.markdown("**Sélectionnez un événement historique**")
        event_choisi = st.selectbox("Événement", list(EVENEMENTS_HISTORIQUES.keys()))
        info_event = EVENEMENTS_HISTORIQUES[event_choisi]
        st.markdown(f'<div class="qt-callout"><strong>{event_choisi}</strong><br>'
                    f'<span style="font-size:0.9em;">{info_event["description"]}</span></div>',
                    unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Période personnalisée (optionnel)**")
        date_debut_custom = st.date_input("Date début", value=datetime.strptime(info_event["debut"], "%Y-%m-%d"))
        date_fin_custom = st.date_input("Date fin", value=datetime.strptime(info_event["fin"], "%Y-%m-%d"))

    st.markdown("---")
    st.markdown("### Actifs à analyser")
    st.caption("Cochez les actifs à inclure.")

    actifs_selectionnes = []
    for categorie, actifs_cat in ACTIFS_DISPONIBLES.items():
        with st.expander(categorie, expanded=False):
            for nom_affiche, sim_key in actifs_cat.items():
                if st.checkbox(nom_affiche, value=(sim_key in ACTIFS_PAR_DEFAUT), key=f"chk_{sim_key}"):
                    actifs_selectionnes.append(sim_key)

    if not actifs_selectionnes:
        st.warning("Sélectionnez au moins un actif.")

    st.markdown("---")
    st.markdown("### Portefeuille")

    capital_initial = st.number_input(
        "Capital de départ (€)", min_value=100, max_value=10000000, value=10000, step=500
    )
    profil_risque = st.selectbox(
        "Profil d'investisseur",
        ["Prudent (Hyper Sécurisé)", "Équilibré (Normal)", "Agressif (Risqué)", "Personnalisé"],
        index=1
    )

    allocations_custom = {}
    if profil_risque == "Personnalisé":
        if actifs_selectionnes:
            st.markdown("**Répartition (%)**")
            st.caption("La somme doit être égale à 100%.")
            total_alloc = 0
            defaut_pct = round(100 / len(actifs_selectionnes))
            for sim_key in actifs_selectionnes:
                val = st.number_input(
                    NOM_AFFICHAGE.get(sim_key, sim_key),
                    min_value=0, max_value=100, value=defaut_pct, step=1,
                    key=f"alloc_{sim_key}"
                )
                allocations_custom[sim_key] = val
                total_alloc += val
            couleur = "#2f855a" if total_alloc == 100 else "#c53030"
            icone = "✓" if total_alloc == 100 else "!"
            st.markdown(
                f"<div style='text-align:center; margin-top:8px;'>"
                f"<span style='background:{couleur}; color:white; padding:4px 14px; "
                f"border-radius:12px; font-weight:700; font-size:0.88em;'>{icone} Total : {total_alloc}%</span></div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Sélectionnez d'abord des actifs.")

    st.markdown("<br>", unsafe_allow_html=True)
    bouton_label = "Lancer la simulation" if mode_app == "Simulation prospective" else "Lancer le backtest"
    lancer = st.button(bouton_label, use_container_width=True, type="primary")


# ==========================================
# 5. ONGLETS
# ==========================================

if mode_app == "Simulation prospective":
    if st.session_state.mode_comparaison:
        tab_dashboard, tab_portefeuille, tab_compare, tab_hist, tab_academie, tab_chat, tab_apropos = st.tabs([
            "Dashboard", "Portefeuille", "Comparaison A vs B", "Historique", "Académie", "Analyste IA", "À propos"
        ])
    else:
        tab_dashboard, tab_portefeuille, tab_hist, tab_academie, tab_chat, tab_apropos = st.tabs([
            "Dashboard", "Portefeuille", "Historique", "Académie", "Analyste IA", "À propos"
        ])
        tab_compare = None
    tab_backtest = None
else:
    tab_dashboard, tab_backtest, tab_hist, tab_academie, tab_chat, tab_apropos = st.tabs([
        "Dashboard", "Backtest", "Historique", "Académie", "Analyste IA", "À propos"
    ])
    tab_portefeuille = None
    tab_compare = None


# ==========================================
# 6. HELPERS
# ==========================================

def calculer_metriques_risque(valeur_portefeuille):
    serie = pd.Series(valeur_portefeuille).astype(float)
    rendements = serie.pct_change().dropna()
    if len(rendements) == 0 or rendements.std() == 0:
        return {"vol_ann": 0, "sharpe": 0, "max_dd": 0, "var_95": 0}
    vol_ann = rendements.std() * np.sqrt(252) * 100
    rendement_moyen_ann = rendements.mean() * 252
    sharpe = (rendement_moyen_ann - 0.02) / (rendements.std() * np.sqrt(252))
    cummax = serie.cummax()
    drawdown = (cummax - serie) / cummax
    max_dd = drawdown.max() * 100
    var_95 = np.percentile(rendements, 5) * 100
    return {"vol_ann": vol_ann, "sharpe": sharpe, "max_dd": max_dd, "var_95": var_95}


def calculer_poids(profil, actifs_sim, allocations):
    if profil == "Personnalisé":
        total_alloc = sum(allocations.values()) or 1
        poids = {k: v / total_alloc for k, v in allocations.items() if v > 0}
    elif profil == "Prudent (Hyper Sécurisé)":
        poids_bruts = {"Bons_Tresor_US_10Y": 0.50, "Or": 0.20, "S&P 500": 0.10,
                       "EUR_USD": 0.10, "Bund_10Y": 0.05, "OAT_10Y": 0.05}
        poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}
    elif profil == "Agressif (Risqué)":
        poids_bruts = {"Bitcoin": 0.20, "Ethereum": 0.10, "XRP": 0.05, "Solana": 0.05,
                       "S&P 500": 0.30, "NASDAQ": 0.15, "CAC 40": 0.05,
                       "Petrole": 0.05, "ETF_Defense": 0.05}
        poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}
    else:
        poids_bruts = {"S&P 500": 0.25, "CAC 40": 0.08, "NASDAQ": 0.07,
                       "Bons_Tresor_US_10Y": 0.25, "Or": 0.12, "Petrole": 0.05,
                       "EUR_USD": 0.05, "Bitcoin": 0.08, "Ethereum": 0.05}
        poids = {k: v for k, v in poids_bruts.items() if v > 0 and k in actifs_sim}

    total_poids = sum(poids.values())
    if total_poids > 0:
        poids = {k: v / total_poids for k, v in poids.items()}
    if not poids and actifs_sim:
        poids = {k: 1 / len(actifs_sim) for k in actifs_sim}
    return poids


def lancer_une_simulation(scenario, actifs_sel, duree_j, modele, mc, prix_reels, vols_reelles, calib_histo):
    chocs = analyser_evenement_macro(scenario, calibration_historique=calib_histo)
    if isinstance(chocs, dict) and "erreur" in chocs and len(chocs) == 1:
        return None, chocs["erreur"]
    if not chocs or ("actifs" not in chocs and "macro" not in chocs):
        return None, "L'IA n'a pas pu lier ce scénario à la finance."

    mc_data = None
    if mc:
        mc_data = simuler_monte_carlo(chocs, jours=duree_j, modele=modele,
                                       actifs=actifs_sel, nb_simulations=50,
                                       prix_reels=prix_reels, vols_reelles=vols_reelles)
        df = mc_data["mediane"]
    else:
        df = simuler_marche_dynamique(chocs, jours=duree_j, modele=modele,
                                       actifs=actifs_sel, prix_reels=prix_reels,
                                       vols_reelles=vols_reelles)

    perf = ((df.iloc[-1] - df.iloc[0]) / df.iloc[0]) * 100
    perf_df = perf.reset_index()
    perf_df.columns = ['Actif', 'Performance (%)']
    perf_df['Actif'] = perf_df['Actif'].apply(
        lambda x: NOM_AFFICHAGE.get(x, x.replace("_", " ").replace("EUR USD", "EUR/USD"))
    )
    perf_df = perf_df.sort_values(by='Performance (%)', ascending=True)

    return {
        "scenario":  scenario,
        "chocs_ia":  chocs,
        "df":        df,
        "mc_data":   mc_data,
        "perf":      perf,
        "perf_df":   perf_df,
    }, None


def construire_allocations_finales(res, params):
    """Construit la liste pour le PDF."""
    cap = params["capital"]
    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    allocations_finales = []
    valeur_finale = 0
    for sk, pct in poids.items():
        nom = NOM_AFFICHAGE.get(sk, sk.replace("_", " ").replace("EUR USD", "EUR/USD"))
        rend = res["perf"].get(sk, 0) / 100
        invest = cap * pct
        final = invest * (1 + rend)
        valeur_finale += final
        allocations_finales.append({
            "nom": nom, "poids": pct, "investi": invest,
            "final": final, "rendement": rend
        })
    return allocations_finales, valeur_finale


# ==========================================
# 7. LANCEMENT — SIMULATION
# ==========================================

if lancer and mode_app == "Simulation prospective":
    st.session_state.simu_A = None
    st.session_state.simu_B = None

    scenario_A = st.session_state.event_text_A
    scenario_B = st.session_state.event_text_B if st.session_state.mode_comparaison else None

    if len(scenario_A.strip()) < 10 or (st.session_state.mode_comparaison and len(scenario_B.strip()) < 10):
        st.warning("Scénario trop court.")
    elif not actifs_selectionnes:
        st.warning("Sélectionnez au moins un actif.")
    elif profil_risque == "Personnalisé" and sum(allocations_custom.values()) != 100:
        st.warning(f"Allocation = 100% requis (actuellement {sum(allocations_custom.values())}%).")
    else:
        prix_reels = None
        vols_reelles = None
        erreurs_yahoo = []

        if utiliser_prix_reels:
            with st.spinner("Connexion à Yahoo Finance..."):
                prix_reels, erreurs_yahoo = get_prix_actuels(actifs_selectionnes)
                vols_reelles = get_volatilites_historiques(actifs_selectionnes)
            if erreurs_yahoo:
                st.warning(f"Indisponibles : {', '.join([NOM_AFFICHAGE.get(e, e) for e in erreurs_yahoo])}.")

        msg = "L'analyste IA étudie votre scénario..."
        if calibration_historique:
            msg = "L'IA recherche des analogies historiques..."
        if mode_monte_carlo:
            msg = "Monte-Carlo : 50 simulations..."

        with st.spinner(msg):
            try:
                result_A, err_A = lancer_une_simulation(
                    scenario_A, actifs_selectionnes, duree, modele_simu,
                    mode_monte_carlo, prix_reels, vols_reelles, calibration_historique
                )
                if err_A:
                    st.error(f"Scénario A : {err_A}")
                else:
                    st.session_state.simu_A = result_A

                if st.session_state.mode_comparaison:
                    result_B, err_B = lancer_une_simulation(
                        scenario_B, actifs_selectionnes, duree, modele_simu,
                        mode_monte_carlo, prix_reels, vols_reelles, calibration_historique
                    )
                    if err_B:
                        st.error(f"Scénario B : {err_B}")
                    else:
                        st.session_state.simu_B = result_B

                st.session_state.params_sim = {
                    "actifs_sim":   actifs_selectionnes.copy(),
                    "allocations":  allocations_custom.copy(),
                    "profil":       profil_risque,
                    "capital":      capital_initial,
                    "duree":        duree,
                    "mc":           mode_monte_carlo,
                    "comparaison":  st.session_state.mode_comparaison,
                    "prix_reels":   utiliser_prix_reels,
                    "calib":        calibration_historique,
                }

                if st.session_state.simu_A:
                    poids_h = calculer_poids(profil_risque, actifs_selectionnes, allocations_custom)
                    for label, res in [("A", st.session_state.simu_A),
                                        ("B", st.session_state.simu_B) if st.session_state.mode_comparaison else (None, None)]:
                        if res is None:
                            continue
                        valeur_finale = 0
                        for sk, pct in poids_h.items():
                            rend = res["perf"].get(sk, 0) / 100
                            valeur_finale += capital_initial * pct * (1 + rend)
                        perf_p = (valeur_finale - capital_initial) / capital_initial * 100
                        st.session_state.historique_simus.insert(0, {
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "scenario": res["scenario"][:80] + ("..." if len(res["scenario"]) > 80 else ""),
                            "profil": profil_risque,
                            "capital": capital_initial,
                            "valeur_finale": valeur_finale,
                            "perf": perf_p,
                            "monte_carlo": mode_monte_carlo,
                            "nb_actifs": len(actifs_selectionnes),
                            "label_compare": label if st.session_state.mode_comparaison else None,
                            "type": "Simulation",
                        })
                    st.session_state.historique_simus = st.session_state.historique_simus[:10]

            except Exception as e:
                st.error(f"Erreur technique : {e}")


# ==========================================
# 8. LANCEMENT — BACKTEST
# ==========================================

if lancer and mode_app == "Backtest historique":
    if not actifs_selectionnes:
        st.warning("Sélectionnez au moins un actif.")
    elif profil_risque == "Personnalisé" and sum(allocations_custom.values()) != 100:
        st.warning(f"Allocation = 100% requis (actuellement {sum(allocations_custom.values())}%).")
    else:
        with st.spinner(f"Récupération des données historiques pour {event_choisi}..."):
            try:
                df_histo = get_historique(
                    actifs_selectionnes,
                    date_debut_custom.strftime("%Y-%m-%d"),
                    date_fin_custom.strftime("%Y-%m-%d")
                )

                if df_histo.empty:
                    st.error("Aucune donnée disponible pour cette période.")
                else:
                    perf = ((df_histo.iloc[-1] - df_histo.iloc[0]) / df_histo.iloc[0]) * 100
                    perf_df = perf.reset_index()
                    perf_df.columns = ['Actif', 'Performance (%)']
                    perf_df['Actif'] = perf_df['Actif'].apply(
                        lambda x: NOM_AFFICHAGE.get(x, x.replace("_", " ").replace("EUR USD", "EUR/USD"))
                    )
                    perf_df = perf_df.sort_values(by='Performance (%)', ascending=True)

                    st.session_state.backtest_data = {
                        "evenement": event_choisi,
                        "description": EVENEMENTS_HISTORIQUES[event_choisi]["description"],
                        "date_debut": date_debut_custom,
                        "date_fin": date_fin_custom,
                        "df": df_histo,
                        "perf": perf,
                        "perf_df": perf_df,
                        "actifs_disponibles": list(df_histo.columns),
                        "actifs_indisponibles": [a for a in actifs_selectionnes if a not in df_histo.columns],
                    }

                    st.session_state.params_sim = {
                        "actifs_sim":   list(df_histo.columns),
                        "allocations":  allocations_custom.copy(),
                        "profil":       profil_risque,
                        "capital":      capital_initial,
                    }

                    poids_h = calculer_poids(profil_risque, list(df_histo.columns), allocations_custom)
                    valeur_finale = 0
                    for sk, pct in poids_h.items():
                        rend = perf.get(sk, 0) / 100
                        valeur_finale += capital_initial * pct * (1 + rend)
                    perf_p = (valeur_finale - capital_initial) / capital_initial * 100
                    st.session_state.historique_simus.insert(0, {
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "scenario": f"Backtest : {event_choisi}",
                        "profil": profil_risque,
                        "capital": capital_initial,
                        "valeur_finale": valeur_finale,
                        "perf": perf_p,
                        "monte_carlo": False,
                        "nb_actifs": len(df_histo.columns),
                        "label_compare": None,
                        "type": "Backtest",
                    })
                    st.session_state.historique_simus = st.session_state.historique_simus[:10]
            except Exception as e:
                st.error(f"Erreur backtest : {e}")


# ==========================================
# 9. AFFICHAGE — DASHBOARD & PORTEFEUILLE
# ==========================================

def hauteur_graphique(nb_actifs):
    """Retourne une hauteur adaptée selon le nombre d'actifs (pour la légende)."""
    if nb_actifs <= 1:
        return 320
    elif nb_actifs <= 3:
        return 360
    else:
        return 400


def afficher_dashboard(res, params, key_prefix="main"):
    chocs = res["chocs_ia"]
    df = res["df"]
    mc = res["mc_data"]

    badges = ""
    if params.get("prix_reels"):
        badges += '<span class="qt-live-badge">PRIX RÉELS</span>'
    if params.get("calib") and chocs.get("evenement_reference"):
        badges += f'<span class="qt-live-badge" style="background:#805ad5;">CALIBRÉ : {chocs["evenement_reference"]}</span>'
    if badges:
        st.markdown(f'<div style="margin-bottom:14px;">{badges}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Impact Inflation (Estimé)", f"{chocs.get('macro', {}).get('inflation', 0):+.2f} %")
    col2.metric("Taux Directeurs (Estimé)", f"{chocs.get('macro', {}).get('taux_directeurs', 0):+.2f} %")
    col3.info(f"**Analyse IA :** {chocs.get('explication_courte', '—')}")

    poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
    valeur_port = pd.Series(0.0, index=df.index)
    for sk, pct in poids.items():
        if sk in df.columns:
            valeur_port += pct * (df[sk] / df[sk].iloc[0]) * params["capital"]
    metriques = calculer_metriques_risque(valeur_port)

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Métriques de risque du portefeuille</div>', unsafe_allow_html=True)
    st.caption("Indicateurs utilisés par les gérants de fonds professionnels.")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Volatilité annualisée", f"{metriques['vol_ann']:.2f} %",
              help="Amplitude des variations.")
    r2.metric("Sharpe Ratio", f"{metriques['sharpe']:.2f}",
              help=">1 = bon | >2 = excellent | <0 = mauvais.")
    r3.metric("Max Drawdown", f"-{metriques['max_dd']:.2f} %",
              help="Pire chute depuis un plus-haut.")
    r4.metric("VaR 95% (1 jour)", f"{metriques['var_95']:.2f} %",
              help="Perte max probable en 1 jour avec 95% de confiance.")

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)

    df_norm = (df / df.iloc[0]) * 100
    df_norm.columns = [NOM_AFFICHAGE.get(c, c.replace("_", " ").replace("EUR USD", "EUR/USD")) for c in df_norm.columns]

    mc_bas_norm = mc_haut_norm = None
    if mc is not None:
        mc_bas_norm = (mc["bas"] / df.iloc[0]) * 100
        mc_haut_norm = (mc["haut"] / df.iloc[0]) * 100
        mc_bas_norm.columns = df_norm.columns
        mc_haut_norm.columns = df_norm.columns

    graphiques = []
    for titre_cat, sim_keys_cat in CATEGORIES_GRAPHIQUES.items():
        actifs_dispo = [NOM_AFFICHAGE.get(sk, sk) for sk in sim_keys_cat if sk in params["actifs_sim"]]
        actifs_dispo = [a for a in actifs_dispo if a in df_norm.columns]
        if actifs_dispo:
            graphiques.append((titre_cat, actifs_dispo))

    for i in range(0, len(graphiques), 2):
        cols = st.columns(2)
        for j, (titre_cat, actifs_dispo) in enumerate(graphiques[i:i+2]):
            with cols[j]:
                fig = go.Figure()
                couleurs = ["#1a365d", "#319795", "#d69e2e", "#c53030", "#805ad5", "#2f855a"]
                for idx, actif in enumerate(actifs_dispo):
                    col_c = couleurs[idx % len(couleurs)]
                    if mc_bas_norm is not None:
                        fig.add_trace(go.Scatter(x=df_norm.index, y=mc_haut_norm[actif],
                                                 mode='lines', line=dict(width=0),
                                                 showlegend=False, hoverinfo='skip'))
                        fig.add_trace(go.Scatter(x=df_norm.index, y=mc_bas_norm[actif],
                                                 mode='lines', line=dict(width=0), fill='tonexty',
                                                 fillcolor=f'rgba({int(col_c[1:3],16)},{int(col_c[3:5],16)},{int(col_c[5:7],16)},0.12)',
                                                 showlegend=False, hoverinfo='skip'))
                    fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[actif],
                                             mode='lines', name=actif,
                                             line=dict(color=col_c, width=2.2)))

                # Hauteur adaptée + plus de marge basse pour la légende
                nb = len(actifs_dispo)
                hauteur = hauteur_graphique(nb)
                fig.update_layout(
                    title=dict(text=titre_cat + (" · Monte-Carlo" if mc_bas_norm is not None else ""),
                               font=dict(color="#1a365d", size=15)),
                    template="plotly_white",
                    xaxis_title="Jours de cotation", yaxis_title="Évolution (Base 100)",
                    height=hauteur,
                    margin=dict(l=10, r=10, t=45, b=90),  # ⬅ b=90 pour aérer
                    legend=dict(
                        orientation="h",
                        yanchor="top", y=-0.25,            # ⬅ légende plus loin de l'axe
                        xanchor="center", x=0.5
                    ),
                    font=dict(color="#2d3748")
                )
                st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_cat_{titre_cat}")

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    fig_bar = px.bar(res["perf_df"], x='Performance (%)', y='Actif', orientation='h',
                     color='Performance (%)', color_continuous_scale=['#c53030', '#f7fafc', '#2f855a'],
                     text='Performance (%)', title="Performance par actif")
    fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto')
    fig_bar.update_layout(template="plotly_white",
                          height=max(350, 30 * len(res["perf_df"]) + 80),
                          margin=dict(l=10, r=10, t=50, b=10),
                          title_font=dict(color="#1a365d"),
                          font=dict(color="#2d3748"))
    st.plotly_chart(fig_bar, use_container_width=True, key=f"{key_prefix}_heatmap")

    # ---- BOUTON PDF (NOUVEAU) ----
    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
    st.markdown('<div class="qt-section-title">Exporter le rapport</div>', unsafe_allow_html=True)
    allocs, valeur_fin = construire_allocations_finales(res, params)
    try:
        pdf_bytes = generer_rapport_pdf(
            simu=res, params=params, metriques=metriques,
            allocations_finales=allocs, valeur_finale=valeur_fin,
            type_rapport="Simulation"
        )
        st.download_button(
            label="📄 Télécharger le rapport PDF",
            data=pdf_bytes,
            file_name=f"quant_terminal_rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"{key_prefix}_pdf"
        )
    except Exception as e:
        st.error(f"Génération PDF impossible : {e}")


def afficher_portefeuille(res, params, key_prefix="main"):
    cap = params["capital"]
    profil = params["profil"]
    actifs_sim = params["actifs_sim"]
    poids = calculer_poids(profil, actifs_sim, params["allocations"])

    st.markdown(f"<h3 style='text-align:center; color:#1a365d;'>Portefeuille de {cap:,.0f} €</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#718096; margin-bottom:28px;'>Profil : <strong>{profil}</strong></p>", unsafe_allow_html=True)

    valeur_finale = 0
    cols_port = st.columns(4)
    for i, (sk, pct) in enumerate(poids.items()):
        nom = NOM_AFFICHAGE.get(sk, sk.replace("_", " ").replace("EUR USD", "EUR/USD"))
        montant = cap * pct
        rend = (res["perf"].get(sk, 0)) / 100
        final = montant * (1 + rend)
        valeur_finale += final
        with cols_port[i % 4]:
            st.metric(f"{nom} ({pct*100:.1f}%)", f"{final:,.0f} €", f"{rend*100:+.2f}%")

    st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)

    if poids:
        col_pie, col_bilan = st.columns(2)
        with col_pie:
            pie_df = pd.DataFrame({
                "Actif": [NOM_AFFICHAGE.get(k, k) for k in poids.keys()],
                "Poids": [v * 100 for v in poids.values()]
            })
            fig_pie = px.pie(pie_df, names="Actif", values="Poids",
                             title="Répartition du portefeuille", hole=0.5,
                             color_discrete_sequence=["#1a365d", "#319795", "#d69e2e", "#805ad5",
                                                      "#2f855a", "#c53030", "#2c5282", "#4a5568"])
            fig_pie.update_layout(template="plotly_white", height=340,
                                  margin=dict(l=10, r=10, t=50, b=10),
                                  legend=dict(orientation="v", x=1.0, y=0.5),
                                  title_font=dict(color="#1a365d"))
            st.plotly_chart(fig_pie, use_container_width=True, key=f"{key_prefix}_pie")

        with col_bilan:
            st.markdown("<br><br>", unsafe_allow_html=True)
            gains = valeur_finale - cap
            st.metric("Bilan net du portefeuille", f"{valeur_finale:,.2f} €",
                      f"{gains:,.2f} € (gains/pertes)")
            perf_g = (gains / cap) * 100 if cap > 0 else 0
            st.metric("Performance globale", f"{perf_g:+.2f} %")
    return valeur_finale


# ==========================================
# 10. ONGLETS — Dashboard
# ==========================================

with tab_dashboard:
    if mode_app == "Simulation prospective":
        if st.session_state.simu_A is None:
            st.info("Configurez votre scénario à gauche et cliquez sur 'Lancer la simulation'.")
        else:
            if st.session_state.mode_comparaison and st.session_state.simu_B:
                sub_A, sub_B = st.tabs(["Scénario A", "Scénario B"])
                with sub_A:
                    st.markdown(f'<div class="qt-callout"><strong>Scénario A :</strong> {st.session_state.simu_A["scenario"]}</div>', unsafe_allow_html=True)
                    afficher_dashboard(st.session_state.simu_A, st.session_state.params_sim, key_prefix="dash_A")
                with sub_B:
                    st.markdown(f'<div class="qt-callout"><strong>Scénario B :</strong> {st.session_state.simu_B["scenario"]}</div>', unsafe_allow_html=True)
                    afficher_dashboard(st.session_state.simu_B, st.session_state.params_sim, key_prefix="dash_B")
            else:
                afficher_dashboard(st.session_state.simu_A, st.session_state.params_sim, key_prefix="dash_main")
    else:
        if st.session_state.backtest_data is None:
            st.info("Sélectionnez un événement historique à gauche et cliquez sur 'Lancer le backtest'.")
        else:
            bt = st.session_state.backtest_data
            st.markdown(f'<div class="qt-callout"><strong>Backtest : {bt["evenement"]}</strong><br>'
                        f'<span style="font-size:0.9em;">{bt["description"]}<br>'
                        f'Période : {bt["date_debut"]} → {bt["date_fin"]} · {len(bt["df"])} jours de cotation</span></div>',
                        unsafe_allow_html=True)
            if bt["actifs_indisponibles"]:
                noms_indispo = [NOM_AFFICHAGE.get(a, a) for a in bt["actifs_indisponibles"]]
                st.warning(f"Indisponibles à cette époque : {', '.join(noms_indispo)}")

            df = bt["df"]
            params = st.session_state.params_sim

            poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])
            valeur_port = pd.Series(0.0, index=df.index)
            for sk, pct in poids.items():
                if sk in df.columns:
                    valeur_port += pct * (df[sk] / df[sk].iloc[0]) * params["capital"]
            metriques = calculer_metriques_risque(valeur_port)

            st.markdown('<div class="qt-section-title">Métriques de risque (données réelles)</div>', unsafe_allow_html=True)
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Volatilité annualisée", f"{metriques['vol_ann']:.2f} %")
            r2.metric("Sharpe Ratio", f"{metriques['sharpe']:.2f}")
            r3.metric("Max Drawdown", f"-{metriques['max_dd']:.2f} %")
            r4.metric("VaR 95% (1 jour)", f"{metriques['var_95']:.2f} %")

            st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)

            df_norm = (df / df.iloc[0]) * 100
            df_norm.columns = [NOM_AFFICHAGE.get(c, c) for c in df_norm.columns]

            graphiques = []
            for titre_cat, sim_keys_cat in CATEGORIES_GRAPHIQUES.items():
                actifs_dispo = [NOM_AFFICHAGE.get(sk, sk) for sk in sim_keys_cat if sk in bt["actifs_disponibles"]]
                actifs_dispo = [a for a in actifs_dispo if a in df_norm.columns]
                if actifs_dispo:
                    graphiques.append((titre_cat, actifs_dispo))

            for i in range(0, len(graphiques), 2):
                cols = st.columns(2)
                for j, (titre_cat, actifs_dispo) in enumerate(graphiques[i:i+2]):
                    with cols[j]:
                        fig = go.Figure()
                        couleurs = ["#1a365d", "#319795", "#d69e2e", "#c53030", "#805ad5", "#2f855a"]
                        for idx, actif in enumerate(actifs_dispo):
                            fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[actif],
                                                     mode='lines', name=actif,
                                                     line=dict(color=couleurs[idx % len(couleurs)], width=2.2)))
                        nb = len(actifs_dispo)
                        hauteur = hauteur_graphique(nb)
                        fig.update_layout(
                            title=dict(text=titre_cat + " · Données réelles", font=dict(color="#1a365d", size=15)),
                            template="plotly_white",
                            xaxis_title="Jours de cotation", yaxis_title="Évolution (Base 100)",
                            height=hauteur, margin=dict(l=10, r=10, t=45, b=90),
                            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
                            font=dict(color="#2d3748")
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"bt_cat_{titre_cat}")

            st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
            fig_bar = px.bar(bt["perf_df"], x='Performance (%)', y='Actif', orientation='h',
                             color='Performance (%)', color_continuous_scale=['#c53030', '#f7fafc', '#2f855a'],
                             text='Performance (%)', title="Performance réelle par actif")
            fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='auto')
            fig_bar.update_layout(template="plotly_white",
                                  height=max(350, 30 * len(bt["perf_df"]) + 80),
                                  margin=dict(l=10, r=10, t=50, b=10),
                                  title_font=dict(color="#1a365d"),
                                  font=dict(color="#2d3748"))
            st.plotly_chart(fig_bar, use_container_width=True, key="bt_heatmap")

            # PDF backtest
            st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
            st.markdown('<div class="qt-section-title">Exporter le rapport</div>', unsafe_allow_html=True)
            try:
                # construire un res factice pour le PDF
                res_bt = {
                    "scenario": f"Backtest : {bt['evenement']} — {bt['description']}",
                    "chocs_ia": {"explication_courte": f"Période réelle : {bt['date_debut']} → {bt['date_fin']}",
                                 "macro": {"inflation": 0, "taux_directeurs": 0},
                                 "evenement_reference": bt["evenement"]},
                    "perf_df": bt["perf_df"],
                    "perf": bt["perf"],
                }
                params_bt = {**params, "duree": len(bt["df"]), "mc": False, "prix_reels": True, "calib": True}
                allocs_bt, valeur_fin_bt = construire_allocations_finales(res_bt, params_bt)
                pdf_bytes = generer_rapport_pdf(
                    simu=res_bt, params=params_bt, metriques=metriques,
                    allocations_finales=allocs_bt, valeur_finale=valeur_fin_bt,
                    type_rapport="Backtest"
                )
                st.download_button(
                    label="📄 Télécharger le rapport PDF",
                    data=pdf_bytes,
                    file_name=f"quant_terminal_backtest_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="bt_pdf"
                )
            except Exception as e:
                st.error(f"Génération PDF impossible : {e}")


# ==========================================
# 11. ONGLET — Portefeuille
# ==========================================

if tab_portefeuille is not None:
    with tab_portefeuille:
        if st.session_state.simu_A is None:
            st.info("Lancez d'abord une simulation.")
        else:
            if st.session_state.mode_comparaison and st.session_state.simu_B:
                sub_A, sub_B = st.tabs(["Scénario A", "Scénario B"])
                with sub_A:
                    afficher_portefeuille(st.session_state.simu_A, st.session_state.params_sim, key_prefix="port_A")
                with sub_B:
                    afficher_portefeuille(st.session_state.simu_B, st.session_state.params_sim, key_prefix="port_B")
            else:
                afficher_portefeuille(st.session_state.simu_A, st.session_state.params_sim, key_prefix="port_main")


# ==========================================
# 12. ONGLET — Backtest (détail)
# ==========================================

if tab_backtest is not None:
    with tab_backtest:
        if st.session_state.backtest_data is None:
            st.info("Lancez un backtest pour voir le détail.")
        else:
            bt = st.session_state.backtest_data
            params = st.session_state.params_sim
            df = bt["df"]
            cap = params["capital"]
            poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])

            st.markdown(f'<div class="qt-section-title">Évolution du portefeuille — {bt["evenement"]}</div>',
                        unsafe_allow_html=True)
            st.caption("Comment votre portefeuille aurait réellement évolué pendant cette crise.")

            valeur_port = pd.Series(0.0, index=df.index)
            for sk, pct in poids.items():
                if sk in df.columns:
                    valeur_port += pct * (df[sk] / df[sk].iloc[0]) * cap

            benchmark = None
            if "S&P 500" in df.columns:
                benchmark = (df["S&P 500"] / df["S&P 500"].iloc[0]) * cap

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=valeur_port.index, y=valeur_port,
                                     name="Votre portefeuille",
                                     line=dict(color="#1a365d", width=3)))
            if benchmark is not None:
                fig.add_trace(go.Scatter(x=benchmark.index, y=benchmark,
                                         name="S&P 500 (benchmark)",
                                         line=dict(color="#319795", width=2, dash="dash")))
            fig.add_hline(y=cap, line_dash="dot", line_color="#718096",
                          annotation_text=f"Capital initial ({cap:,.0f} €)",
                          annotation_position="bottom right")
            fig.update_layout(template="plotly_white", height=420,
                              xaxis_title="Jours de cotation",
                              yaxis_title="Valeur (€)",
                              margin=dict(l=10, r=10, t=30, b=10),
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                              font=dict(color="#2d3748"))
            st.plotly_chart(fig, use_container_width=True, key="bt_evolution")

            valeur_finale = float(valeur_port.iloc[-1])
            gains = valeur_finale - cap
            perf_g = (gains / cap) * 100 if cap > 0 else 0

            st.markdown('<hr class="qt-divider">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital initial", f"{cap:,.0f} €")
            c2.metric("Valeur finale", f"{valeur_finale:,.2f} €", f"{gains:,.0f} €")
            c3.metric("Performance globale", f"{perf_g:+.2f} %")

            if benchmark is not None:
                perf_bench = (float(benchmark.iloc[-1]) - cap) / cap * 100
                alpha = perf_g - perf_bench
                couleur_alpha = "#2f855a" if alpha >= 0 else "#c53030"
                st.markdown(
                    f'<div style="background:{couleur_alpha}; color:white; padding:18px 24px; '
                    f'border-radius:10px; text-align:center; margin:24px 0; font-size:1.05em;">'
                    f'Votre alpha vs S&P 500 : <strong>{alpha:+.2f} points</strong>'
                    f' ({"surperformance" if alpha >= 0 else "sous-performance"})</div>',
                    unsafe_allow_html=True
                )

            st.markdown('<div class="qt-section-title">Performance par actif</div>', unsafe_allow_html=True)
            cols_port = st.columns(4)
            i = 0
            for sk, pct in poids.items():
                if sk in df.columns:
                    nom = NOM_AFFICHAGE.get(sk, sk)
                    rend = bt["perf"].get(sk, 0) / 100
                    montant = cap * pct
                    final = montant * (1 + rend)
                    with cols_port[i % 4]:
                        st.metric(f"{nom} ({pct*100:.1f}%)",
                                  f"{final:,.0f} €", f"{rend*100:+.2f}%")
                    i += 1


# ==========================================
# 13. ONGLET COMPARAISON
# ==========================================

if tab_compare is not None:
    with tab_compare:
        if st.session_state.simu_A is None or st.session_state.simu_B is None:
            st.info("Lancez une simulation en mode comparaison pour afficher cet onglet.")
        else:
            params = st.session_state.params_sim
            cap = params["capital"]
            poids = calculer_poids(params["profil"], params["actifs_sim"], params["allocations"])

            def valeur_port(res):
                v = 0
                for sk, pct in poids.items():
                    rend = res["perf"].get(sk, 0) / 100
                    v += cap * pct * (1 + rend)
                return v

            v_A = valeur_port(st.session_state.simu_A)
            v_B = valeur_port(st.session_state.simu_B)
            perf_A = (v_A - cap) / cap * 100
            perf_B = (v_B - cap) / cap * 100

            st.markdown('<div class="qt-section-title">Duel de scénarios</div>', unsafe_allow_html=True)

            cA, cB = st.columns(2)
            with cA:
                st.markdown(f'<div class="qt-card"><div class="qt-tag">Scénario A</div>'
                            f'<p style="font-size:0.95em; margin:8px 0 14px 0;">{st.session_state.simu_A["scenario"]}</p></div>',
                            unsafe_allow_html=True)
                st.metric("Valeur finale", f"{v_A:,.0f} €", f"{perf_A:+.2f} %")
            with cB:
                st.markdown(f'<div class="qt-card"><div class="qt-tag">Scénario B</div>'
                            f'<p style="font-size:0.95em; margin:8px 0 14px 0;">{st.session_state.simu_B["scenario"]}</p></div>',
                            unsafe_allow_html=True)
                st.metric("Valeur finale", f"{v_B:,.0f} €", f"{perf_B:+.2f} %")

            ecart = abs(perf_A - perf_B)
            if perf_A > perf_B:
                gagnant, couleur_g = "Scénario A", "#2f855a"
            elif perf_B > perf_A:
                gagnant, couleur_g = "Scénario B", "#2f855a"
            else:
                gagnant, couleur_g = "Égalité parfaite", "#718096"

            st.markdown(f'<div style="background:{couleur_g}; color:white; padding:18px 24px; '
                        f'border-radius:10px; text-align:center; margin:24px 0; font-size:1.1em;">'
                        f'<strong>{gagnant}</strong> l\'emporte avec un écart de <strong>{ecart:.2f} points</strong>'
                        f'</div>', unsafe_allow_html=True)

            st.markdown('<div class="qt-section-title">Évolution comparée du portefeuille</div>', unsafe_allow_html=True)

            def serie_portefeuille(res):
                df = res["df"]
                v = pd.Series(0.0, index=df.index)
                for sk, pct in poids.items():
                    if sk in df.columns:
                        v += pct * (df[sk] / df[sk].iloc[0]) * cap
                return v

            s_A = serie_portefeuille(st.session_state.simu_A)
            s_B = serie_portefeuille(st.session_state.simu_B)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s_A.index, y=s_A, name="Scénario A",
                                     line=dict(color="#1a365d", width=2.8)))
            fig.add_trace(go.Scatter(x=s_B.index, y=s_B, name="Scénario B",
                                     line=dict(color="#319795", width=2.8)))
            fig.add_hline(y=cap, line_dash="dash", line_color="#718096",
                          annotation_text=f"Capital initial ({cap:,.0f} €)",
                          annotation_position="bottom right")
            fig.update_layout(template="plotly_white", height=420,
                              margin=dict(l=10, r=10, t=30, b=10),
                              xaxis_title="Jours de cotation",
                              yaxis_title="Valeur du portefeuille (€)",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                              font=dict(color="#2d3748"))
            st.plotly_chart(fig, use_container_width=True, key="compare_port_chart")

            st.markdown('<div class="qt-section-title">Comparatif des métriques de risque</div>', unsafe_allow_html=True)
            m_A = calculer_metriques_risque(s_A)
            m_B = calculer_metriques_risque(s_B)

            comp_df = pd.DataFrame({
                "Métrique": ["Volatilité annualisée (%)", "Sharpe Ratio", "Max Drawdown (%)", "VaR 95% (%)", "Performance (%)"],
                "Scénario A": [f"{m_A['vol_ann']:.2f}", f"{m_A['sharpe']:.2f}",
                               f"-{m_A['max_dd']:.2f}", f"{m_A['var_95']:.2f}", f"{perf_A:+.2f}"],
                "Scénario B": [f"{m_B['vol_ann']:.2f}", f"{m_B['sharpe']:.2f}",
                               f"-{m_B['max_dd']:.2f}", f"{m_B['var_95']:.2f}", f"{perf_B:+.2f}"],
            })
            st.dataframe(comp_df, use_container_width=True, hide_index=True)


# ==========================================
# 14. HISTORIQUE
# ==========================================

with tab_hist:
    st.markdown('<div class="qt-section-title">Historique des simulations</div>', unsafe_allow_html=True)
    st.caption("Vos 10 dernières simulations.")

    if not st.session_state.historique_simus:
        st.info("Aucune simulation. Lancez votre première simulation pour commencer.")
    else:
        col_b1, _ = st.columns([1, 5])
        with col_b1:
            if st.button("Effacer l'historique"):
                st.session_state.historique_simus = []
                st.rerun()

        for simu in st.session_state.historique_simus:
            couleur = "#2f855a" if simu["perf"] >= 0 else "#c53030"
            icone = "↑" if simu["perf"] >= 0 else "↓"
            tag_mc = " · Monte-Carlo" if simu["monte_carlo"] else ""
            label = f" · Scénario {simu['label_compare']}" if simu.get("label_compare") else ""
            type_label = simu.get("type", "Simulation")

            with st.expander(f"{icone}  {simu['date']}  ·  [{type_label}]  ·  {simu['profil']}{tag_mc}{label}  ·  {simu['perf']:+.2f}%"):
                c1, c2, c3 = st.columns([2.5, 1, 1])
                with c1:
                    st.markdown(f"**Scénario :** {simu['scenario']}")
                    st.markdown(f"**Actifs analysés :** {simu['nb_actifs']}")
                with c2:
                    st.metric("Capital initial", f"{simu['capital']:,.0f} €")
                    st.metric("Valeur finale", f"{simu['valeur_finale']:,.0f} €")
                with c3:
                    gain = simu['valeur_finale'] - simu['capital']
                    st.markdown(f"<div style='background:{couleur}; color:white; padding:18px; "
                                f"border-radius:8px; text-align:center; margin-top:10px;'>"
                                f"<div style='font-size:0.8em; opacity:0.9;'>Gain/Perte</div>"
                                f"<div style='font-size:1.5em; font-weight:700;'>{gain:+,.0f} €</div>"
                                f"</div>", unsafe_allow_html=True)


# ==========================================
# 15. ACADÉMIE
# ==========================================

with tab_academie:
    st.markdown('<div class="qt-section-title">Académie Quant Terminal</div>', unsafe_allow_html=True)
    st.markdown("""
    Bienvenue dans l'Académie. Ici, on ne récite pas des définitions : on cherche à **comprendre** 
    pourquoi les marchés se comportent comme ils le font.
    """)

    st_outils, st_modeles, st_macro, st_cas, st_strat, st_lex, st_methodo = st.tabs([
        "1. Lire les données", "2. Modèles & maths", "3. Macro-économie",
        "4. Cas historiques", "5. Stratégies", "6. Lexique", "7. Méthodologie",
    ])

    with st_outils:
        st.markdown("### Apprendre à lire un graphique de marché")
        st.write("Un graphique financier est le résultat de millions d'ordres et de décisions. Savoir le lire, c'est savoir lire la psychologie du marché.")
        st.markdown("#### 1.1 — L'illusion des prix absolus")
        st.write("Comparer Apple à 170$ et une biotech à 3$ ne dit rien sur leur performance. Seules les variations relatives comptent.")
        st.markdown('<div class="qt-callout"><strong>La règle :</strong> les prix bruts ne disent rien. Seules les <strong>variations relatives</strong> comptent.</div>', unsafe_allow_html=True)
        st.markdown("#### 1.2 — La base 100")
        st.write("On divise chaque prix par celui du jour 0, puis on multiplie par 100. Tous les actifs partent de 100, et on lit directement les pourcentages.")
        st.markdown("#### 1.3 — La heatmap de performance")
        st.write("Vert foncé = gros gain, rouge foncé = grosse perte. Permet de voir le **flight to quality** : en crise, l'argent migre des actions vers l'or et les obligations.")

    with st_modeles:
        st.markdown("### Comment simuler l'avenir avec des mathématiques")
        st.markdown("#### Bachelier et le mouvement brownien")
        st.write("En 1900, Louis Bachelier propose à la Sorbonne que les cours suivent un mouvement brownien. Einstein (1905), Itō (1940), puis Black-Scholes (Nobel 1997).")
        st.latex(r"S_{t+1} = S_t \times (1 + \mu \, \Delta t + \sigma \, \sqrt{\Delta t} \, Z)")
        st.markdown("#### Mandelbrot et les queues épaisses")
        st.write("Le brownien sous-estime les krachs. Mandelbrot a montré que les vrais marchés ont des **queues épaisses** : événements extrêmes plus fréquents que prévu.")
        st.markdown("#### Monte-Carlo")
        st.write("Inventée à Los Alamos en 1944. On lance N simulations aléatoires et on regarde la distribution. Quant Terminal utilise N=50.")

    with st_macro:
        st.markdown("### Les 3 forces qui contrôlent les marchés")
        st.markdown("#### 3.1 — Banques centrales")
        st.write("FED, BCE, BoJ, PBoC. Outil principal : le taux directeur. Taux bas = euphorie. Taux hauts = chute.")
        st.markdown("#### 3.2 — Inflation")
        st.write("Avec 5% d'inflation, vos 100€ perdent 40% de pouvoir d'achat sur 10 ans. Protection : Or, matières premières, immobilier, actions à pricing power.")
        st.markdown("#### 3.3 — Courbe des taux")
        st.write("**Indicateur 100% précis depuis 1960** : chaque récession US a été précédée par une inversion de la courbe des taux.")
        st.markdown("#### 3.4 — VIX")
        st.write("VIX < 15 : complaisance. VIX > 40 : panique. Records : 82 en 2020 (COVID), 80 en 2008 (Lehman).")

    with st_cas:
        st.markdown("### Les grandes crises expliquées")
        st.write("""
        - **1929** : Krach après spéculation sur marge. -89% sur 3 ans. Récupéré en 1954.
        - **1987 (Black Monday)** : -22.6% en 1 jour. Algorithmes en cause.
        - **2000-2002 (dot-com)** : Nasdaq -78%.
        - **2008 (subprimes)** : S&P -57%. Or +25%.
        - **2020 (COVID)** : -34% en 23 jours, plus rapide krach historique. Récupéré en 6 mois.
        """)

    with st_strat:
        st.markdown("### Les grandes stratégies d'allocation")
        st.markdown("#### 60/40 classique")
        st.write("60% actions, 40% obligations. ~8%/an sur 50 ans, drawdown ~25%. Pire année : -17% en 2022.")
        st.markdown("#### All Weather (Ray Dalio)")
        st.write("Conçu pour 4 régimes économiques. 30% actions, 40% obligations longues, 15% obligations moyennes, 7.5% or, 7.5% matières premières.")
        st.markdown("#### Value investing (Buffett, Graham)")
        st.write("Acheter sous la valeur intrinsèque. Critères : douve économique, management, faible dette, P/E raisonnable.")
        st.markdown("#### Momentum (Renaissance, AQR)")
        st.write('"The trend is your friend." Effet documenté par Jegadeesh & Titman (1993).')

    with st_lex:
        st.markdown("### Lexique professionnel")
        st.markdown("""
        - **Bull/Bear Market** — Marché haussier/baissier.
        - **Hawkish/Dovish** — Banquier central agressif/accommodant.
        - **Sharpe Ratio** — Rendement par unité de risque. >1 bon, >2 excellent.
        - **Drawdown** — Pire chute depuis un plus-haut.
        - **VaR** — Perte max probable avec un niveau de confiance.
        - **Beta (β)** — Sensibilité au marché.
        - **Alpha (α)** — Surperformance vs benchmark.
        - **Long/Short** — Position acheteuse/vendeuse.
        - **Hedge** — Couverture.
        - **DXY** — Dollar Index.
        - **VIX** — Indice de la peur.
        - **EBITDA** — Bénéfice avant intérêts/impôts/amortissements.
        - **P/E** — Cours / Bénéfice par action.
        - **Duration** — Sensibilité d'une obligation aux taux.
        """)

    with st_methodo:
        st.markdown("### Méthodologie mathématique")
        st.markdown("#### Volatilité annualisée")
        st.latex(r"\sigma_{annuel} = \sigma_{quotidien} \times \sqrt{252}")
        st.markdown("#### Sharpe Ratio")
        st.latex(r"Sharpe = \frac{R_p - R_f}{\sigma_p}")
        st.markdown("#### Max Drawdown")
        st.latex(r"DD_{max} = \max_t \left( \frac{Peak_t - V_t}{Peak_t} \right)")
        st.markdown("#### VaR 95%")
        st.latex(r"VaR_{95\%} = \text{Percentile}_{5\%}(\text{rendements})")
        st.markdown("#### Mouvement Brownien Géométrique")
        st.latex(r"\frac{dS_t}{S_t} = \mu \, dt + \sigma \, dW_t")
        st.markdown('<div class="qt-callout-warn"><strong>Limites :</strong> volatilités constantes, actifs indépendants, distributions gaussiennes (sauf mode Historique), pas de coûts de transaction. Outil pédagogique.</div>', unsafe_allow_html=True)


# ==========================================
# 16. CHATBOT
# ==========================================

with tab_chat:
    st.markdown('<div class="qt-section-title">Bureau de votre analyste financier IA</div>', unsafe_allow_html=True)
    st.caption("Posez vos questions sur le marché, la macro-économie, ou l'impact de votre scénario.")
    st.markdown('<div class="qt-callout">💬 <strong>Tapez votre question dans la barre en bas de cette page</strong> — l\'analyste IA vous répondra avec un vocabulaire professionnel et pédagogue.</div>', unsafe_allow_html=True)

    for message in st.session_state.messages_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("✍️ Tapez votre question ici (ex : Pourquoi l'Or a-t-il monté pendant la crise de 2008 ?)")
    if question:
        st.chat_message("user").markdown(question)
        st.session_state.messages_chat.append({"role": "user", "content": question})
        with st.chat_message("assistant"):
            with st.spinner("L'analyste rédige son rapport..."):
                reponse_ia = discuter_avec_ia(st.session_state.messages_chat)
                st.markdown(reponse_ia)
        st.session_state.messages_chat.append({"role": "assistant", "content": reponse_ia})


# ==========================================
# 17. À PROPOS (NOUVEAU)
# ==========================================

with tab_apropos:
    st.markdown('<div class="qt-section-title">À propos de Quant Terminal</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="qt-section-title">L\'équipe</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    membres = [
        ("Quentin Geldreich", "Étudiant en MIASHS et Économie & Gestion"),
        ("Lucas Doazan",      "Étudiant en MIASHS et Économie & Gestion"),
        ("Evan Saadi",        "Étudiant en MIASHS et Économie & Gestion"),
        ("Alex Ruimy",        "Étudiant en MIASHS et Économie & Gestion"),
    ]
    for col, (nom, desc) in zip(cols, membres):
        with col:
            st.markdown(f"""
            <div class="qt-card" style="text-align:center; height:180px; display:flex; flex-direction:column; justify-content:center;">
                <div style="width:60px; height:60px; background:linear-gradient(135deg, #1a365d, #319795); border-radius:50%; margin:0 auto 12px auto; display:flex; align-items:center; justify-content:center; color:white; font-weight:800; font-size:18px;">
                    {nom.split()[0][0]}{nom.split()[1][0]}
                </div>
                <strong style="color:#1a365d; font-size:1.05em;">{nom}</strong>
                <span style="font-size:0.85em; color:#718096; margin-top:6px; line-height:1.4;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

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

    st.markdown('<div class="qt-section-title">Ambitions</div>', unsafe_allow_html=True)
    st.write("""
    Au-delà de l'aspect scolaire, notre ambition est de **poursuivre le développement** de cette application afin d'en 
    faire un outil réellement utilisable, avec une utilité concrète pour les utilisateurs. L'idée est donc de faire 
    évoluer ce projet vers quelque chose de plus abouti et potentiellement utile à un public plus large.
    """)

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
                    '<span class="qt-pill">NumPy</span></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="qt-card"><strong>Hébergement</strong><br><br>'
                    '<span class="qt-pill">Streamlit Cloud</span><span class="qt-pill">GitHub</span>'
                    '<span class="qt-pill">ReportLab (PDF)</span></div>',
                    unsafe_allow_html=True)

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

    st.markdown('<div class="qt-section-title">Sources & limites assumées</div>', unsafe_allow_html=True)
    st.markdown('<div class="qt-callout-warn">'
                '<strong>Quant Terminal est un outil pédagogique.</strong> Les simulations utilisent un mouvement brownien '
                'géométrique standard, calibré par une IA. Les volatilités sont calculées sur 12 mois Yahoo Finance. '
                'Limites : volatilités supposées constantes, actifs indépendants, pas de coûts de transaction. '
                'Pour un usage professionnel, il faudrait calibrer le modèle sur des données institutionnelles '
                'et ajouter la modélisation des corrélations et des queues épaisses.'
                '</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#718096; margin-top:30px; padding:20px; '
                'border-top: 1px solid #cbd5e0; font-size:0.85em;">'
                '© 2026 · Quant Terminal · Université Paris Nanterre · MIASHS'
                '</div>', unsafe_allow_html=True)
