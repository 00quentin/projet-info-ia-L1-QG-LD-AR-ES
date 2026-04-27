import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from simulation import simuler_marche_dynamique, simuler_monte_carlo
from ia_bot import analyser_evenement_macro, discuter_avec_ia, generer_rapport_complet_ia
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
        "S&P 500 (USA)":                            "S&P 500",
        "NASDAQ 100 (Tech US)":                     "NASDAQ",
        "CAC 40 (France)":                          "CAC 40",
        "MSCI World (Global)":                      "MSCI_World",
        "MSCI Emerging Markets":                    "Emerging_Markets",
    },
    "Obligations d'État (10 ans)": {
        "U.S. Treasury 10Y":                        "Bons_Tresor_US_10Y",
        "Bund Allemagne 10Y":                       "Bund_10Y",
        "OAT France 10Y":                           "OAT_10Y",
        "JGB Japon 10Y":                            "JGB_10Y",
        "Gilt Royaume-Uni 10Y":                     "Gilt_10Y",
    },
    "Devises & Volatilité": {
        "EUR/USD (Euro-Dollar)":                    "EUR_USD",
        "DXY (US Dollar Index)":                    "Dollar_Index",
        "VIX (CBOE Volatility Index)":              "VIX",
    },
    "Matières Premières": {
        "Or (Gold Spot, $/oz)":                     "Or",
        "Argent (Silver Spot, $/oz)":               "Argent",
        "Pétrole WTI (Crude Oil)":                  "Petrole",
        "Cuivre (Copper Futures)":                  "Cuivre",
        "ETF Terres Rares (REMX)":                  "ETF_Terres_Rares",
    },
    "Sectoriels": {
        "ETF Aérospatiale & Défense (ITA)":         "ETF_Defense",
    },
    "Cryptomonnaies": {
        "Bitcoin (BTC)":                            "Bitcoin",
        "Ethereum (ETH)":                           "Ethereum",
        "XRP (Ripple)":                             "XRP",
        "Solana (SOL)":                             "Solana",
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

# Initialise le mode sombre
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Initialise l'onboarding (1ère visite)
if "show_onboarding" not in st.session_state:
    st.session_state.show_onboarding = True

# Variables CSS selon le mode (injectées séparément)
if st.session_state.dark_mode:
    css_vars_block = """
    <style>
    :root {
        --primary:   #63b3ed;
        --secondary: #4299e1;
        --accent:    #4fd1c5;
        --bg:        #1a202c;
        --bg-2:      #2d3748;
        --card:      #2d3748;
        --border:    #4a5568;
        --border-strong: #718096;
        --text:      #e2e8f0;
        --text-muted:#cbd5e0;
        --muted:     #a0aec0;
        --success:   #48bb78;
        --danger:    #fc8181;
    }
    </style>
    """
else:
    css_vars_block = """
    <style>
    :root {
        --primary:   #1a365d;
        --secondary: #2c5282;
        --accent:    #319795;
        --bg:        #f7fafc;
        --bg-2:      #ffffff;
        --card:      #ffffff;
        --border:    #cbd5e0;
        --border-strong: #a0aec0;
        --text:      #2d3748;
        --text-muted:#4a5568;
        --muted:     #718096;
        --success:   #2f855a;
        --danger:    #c53030;
    }
    </style>
    """

# Inject les variables d'abord
st.markdown(css_vars_block, unsafe_allow_html=True)

# Charger le gros CSS depuis le fichier style.css (évite le bug markdown)
try:
    with open("style.css", "r", encoding="utf-8") as f:
        css_content = f.read()
    # Injection via <style> en concaténant un texte non-markdown
    st.markdown(
        "<style>\n" + css_content + "\n</style>"
        + "\n<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">",
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning("Fichier style.css introuvable - le design ne s'appliquera pas correctement.")


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
# 3. EN-TÊTE + BANDE SANTÉ MARCHÉ + ONBOARDING
# ==========================================

# --- Toggle Mode sombre (en haut à droite) ---
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

# --- HERO SECTION (page d'accueil) ---
st.markdown("""
<div class="qt-hero">
    <div style="display:flex; justify-content:center; align-items:center; gap:18px; margin-bottom:14px;">
        <div style="width:60px; height:60px; background:rgba(255,255,255,0.15); border-radius:14px; display:flex; align-items:center; justify-content:center; color:white !important; font-size:26px; font-weight:800;">QT</div>
        <h1 style="margin:0;">Quant Terminal</h1>
    </div>
    <p>Simulez l'impact d'un événement économique ou géopolitique sur votre portefeuille — 
    avec les vrais prix de marché et une IA calibrée sur les grandes crises historiques.</p>
    <div class="qt-hero-stats">
        <div class="qt-hero-stat">
            <div class="qt-hero-stat-value">23</div>
            <div class="qt-hero-stat-label">Actifs analysés</div>
        </div>
        <div class="qt-hero-stat">
            <div class="qt-hero-stat-value">6</div>
            <div class="qt-hero-stat-label">Crises backtestables</div>
        </div>
        <div class="qt-hero-stat">
            <div class="qt-hero-stat-value">4</div>
            <div class="qt-hero-stat-label">Métriques de risque</div>
        </div>
        <div class="qt-hero-stat">
            <div class="qt-hero-stat-value">∞</div>
            <div class="qt-hero-stat-label">Scénarios possibles</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- ONBOARDING (1ère visite ou si demandé) ---
if st.session_state.show_onboarding:
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

    # Bouton recharger les prix - style amélioré
    st.markdown(
        '<style>'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {'
        '    background-color: #ebf8ff !important;'
        '    color: #1a365d !important;'
        '    border: 1px solid #319795 !important;'
        '    font-weight: 600 !important;'
        '}'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {'
        '    background-color: #319795 !important;'
        '    color: white !important;'
        '    border-color: #319795 !important;'
        '}'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) p {'
        '    color: #1a365d !important;'
        '    font-weight: 600 !important;'
        '}'
        '[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover p {'
        '    color: white !important;'
        '}'
        '</style>',
        unsafe_allow_html=True
    )

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
            st.caption("💡 Conseil : soyez précis et détaillé. Mentionnez le pays, le secteur, l'ampleur.")
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
            st.caption("💡 Conseil : soyez précis et détaillé pour que l'analyste IA soit performant. "
                       "Mentionnez le pays, le secteur, l'ampleur, la durée si possible.")
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

        msg = "L'analyste IA étudie votre scénario... (cela peut prendre quelques secondes)"
        if calibration_historique:
            msg = "L'IA recherche des analogies historiques... (cela peut prendre quelques secondes)"
        if mode_monte_carlo:
            msg = "Mode Monte-Carlo : 50 simulations en cours... (cela peut prendre 15-30 secondes)"
        if st.session_state.mode_comparaison:
            msg = "Analyse comparative de 2 scénarios en cours... (cela peut prendre 30-60 secondes)"

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
                    st.session_state["_just_simulated"] = True

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
                    st.session_state["_just_backtested"] = True
            except Exception as e:
                st.error(f"Erreur backtest : {e}")


# ==========================================
# 9. AFFICHAGE — DASHBOARD & PORTEFEUILLE
# ==========================================

def hauteur_graphique(nb_actifs):
    """Retourne une hauteur FIXE identique pour tous les graphiques (cohérence visuelle)."""
    return 380


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

    col1, col2 = st.columns(2)
    col1.metric("Impact Inflation (Estimé)", f"{chocs.get('macro', {}).get('inflation', 0):+.2f} %")
    col2.metric("Taux Directeurs (Estimé)", f"{chocs.get('macro', {}).get('taux_directeurs', 0):+.2f} %")

    # Analyse IA — bloc dédié, beaucoup plus visible
    explication = chocs.get('explication_courte', 'Analyse non disponible.')
    st.markdown(
        f'<div class="qt-callout" style="margin-top:18px; line-height:1.6;">'
        f'<strong style="color:#1a365d; font-size:1.05em;">📊 Analyse de l\'IA</strong><br><br>'
        f'<span style="font-size:0.97em;">{explication}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

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
    st.caption("Le rapport PDF inclut une analyse approfondie rédigée par l'analyste IA dans le style d'un professionnel institutionnel. Cliquez sur le bouton ci-dessous pour le télécharger (génération en quelques secondes).")
    allocs, valeur_fin = construire_allocations_finales(res, params)

    # Bouton qui déclenche la génération
    if st.button(f"🔬 Préparer le rapport PDF complet", key=f"{key_prefix}_prep_pdf",
                 use_container_width=True):
        st.session_state[f"{key_prefix}_pdf_ready"] = False
        with st.spinner("L'analyste IA rédige son rapport approfondi... (15-30 secondes)"):
            try:
                analyse_senior = generer_rapport_complet_ia(
                    scenario=res["scenario"],
                    chocs_ia=res["chocs_ia"],
                    perf_par_actif=res["perf_df"],
                    metriques=metriques,
                    valeur_initiale=params["capital"],
                    valeur_finale=valeur_fin,
                    profil=params["profil"]
                )
                pdf_bytes = generer_rapport_pdf(
                    simu=res, params=params, metriques=metriques,
                    allocations_finales=allocs, valeur_finale=valeur_fin,
                    type_rapport="Simulation",
                    analyse_senior=analyse_senior
                )
                st.session_state[f"{key_prefix}_pdf_bytes"] = pdf_bytes
                st.session_state[f"{key_prefix}_pdf_ready"] = True
            except Exception as e:
                st.error(f"Génération PDF impossible : {e}")

    # Si le PDF est prêt, afficher le bouton de téléchargement
    if st.session_state.get(f"{key_prefix}_pdf_ready", False):
        st.success("✅ Rapport prêt !")
        st.download_button(
            label="📄 Télécharger le rapport PDF",
            data=st.session_state[f"{key_prefix}_pdf_bytes"],
            file_name=f"quant_terminal_rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"{key_prefix}_pdf_dl"
        )


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
            st.caption("Le rapport PDF inclut une analyse approfondie rédigée par l'analyste IA.")

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

            if st.button("🔬 Préparer le rapport PDF complet", key="bt_prep_pdf",
                         use_container_width=True):
                st.session_state["bt_pdf_ready"] = False
                with st.spinner("L'analyste IA rédige son rapport approfondi... (15-30 secondes)"):
                    try:
                        analyse_senior = generer_rapport_complet_ia(
                            scenario=res_bt["scenario"],
                            chocs_ia=res_bt["chocs_ia"],
                            perf_par_actif=bt["perf_df"],
                            metriques=metriques,
                            valeur_initiale=params["capital"],
                            valeur_finale=valeur_fin_bt,
                            profil=params["profil"]
                        )
                        pdf_bytes = generer_rapport_pdf(
                            simu=res_bt, params=params_bt, metriques=metriques,
                            allocations_finales=allocs_bt, valeur_finale=valeur_fin_bt,
                            type_rapport="Backtest",
                            analyse_senior=analyse_senior
                        )
                        st.session_state["bt_pdf_bytes"] = pdf_bytes
                        st.session_state["bt_pdf_ready"] = True
                    except Exception as e:
                        st.error(f"Génération PDF impossible : {e}")

            if st.session_state.get("bt_pdf_ready", False):
                st.success("✅ Rapport prêt !")
                st.download_button(
                    label="📄 Télécharger le rapport PDF",
                    data=st.session_state["bt_pdf_bytes"],
                    file_name=f"quant_terminal_backtest_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="bt_pdf_dl"
                )


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
    pourquoi les marchés se comportent comme ils le font. L'Académie est conçue pour être lue 
    dans l'ordre — chaque partie s'appuie sur la précédente. Prenez votre temps.
    """)

    st_outils, st_modeles, st_macro, st_cas, st_strat, st_lex, st_methodo = st.tabs([
        "1. Lire les données",
        "2. Modèles & maths",
        "3. Macro-économie",
        "4. Cas historiques",
        "5. Stratégies d'investissement",
        "6. Lexique",
        "7. Méthodologie",
    ])

    # ---- 1. LIRE LES DONNÉES ----
    with st_outils:
        st.markdown("### Apprendre à lire un graphique de marché")
        st.write("""
        Un graphique financier n'est pas un simple dessin : c'est le résultat de millions d'ordres 
        d'achat et de vente, de décisions humaines et algorithmiques, de nouvelles macro-économiques 
        et d'émotions collectives. Savoir lire un graphique, c'est savoir lire la psychologie du marché.
        """)

        st.markdown("#### 1.1 — L'illusion des prix absolus")
        st.write("""
        Un piège courant chez les débutants : comparer les prix bruts. Si l'action Apple vaut 170$ 
        et qu'une petite biotech vaut 3$, laquelle performe le mieux sur un an ? Impossible à dire 
        avec les prix absolus. Peut-être que la biotech valait 1$ il y a un an (elle a fait x3), 
        tandis qu'Apple valait 150$ (elle n'a fait que +13%).
        """)

        st.markdown('<div class="qt-callout">'
                    '<strong>La règle professionnelle :</strong> les prix bruts ne disent rien.<br><br>'
                    'Seules les <strong>variations relatives</strong> comptent.<br><br>'
                    'C\'est pour cela que tous les graphiques comparatifs sont affichés en "base 100".'
                    '</div>', unsafe_allow_html=True)

        st.markdown("#### 1.2 — La base 100 et pourquoi elle est magique")
        st.write("""
        On divise chaque prix par le prix du premier jour, puis on multiplie par 100. 
        Résultat : tous les actifs démarrent à 100, et on lit directement les pourcentages sur l'axe.
        
        - Une courbe qui finit à **120** = +20%
        - Une courbe qui finit à **85** = -15%
        - Une courbe qui finit à **250** = +150% (l'actif a été multiplié par 2.5)

        Sur les graphiques de Quant Terminal, toutes les courbes commencent exactement à 100. 
        Celle qui monte le plus a le plus performé. C'est aussi simple que ça.
        """)

        st.markdown("#### 1.3 — La heatmap de performance")
        st.write("""
        La heatmap (ou carte thermique) est un outil de synthèse redoutable. Sur un seul écran, 
        vous voyez d'un coup d'œil qui a gagné et qui a perdu. Vert foncé = gros gain, 
        rouge foncé = grosse perte.

        **Pourquoi c'est crucial ?** Parce que sur les marchés, l'argent ne disparaît jamais : il se 
        **déplace**. Quand les actions s'effondrent, l'argent va quelque part — typiquement dans 
        les obligations d'État et l'or. On appelle cela un *flight to quality* (fuite vers la qualité).
        Une heatmap permet de voir cette rotation en temps réel.
        """)

        st.markdown('<div class="qt-callout-warn">'
                    '<strong>Piège classique :</strong> regarder uniquement la performance d\'un actif.<br><br>'
                    'Un +10% sur une action qui a une volatilité de 40% est bien moins impressionnant '
                    'qu\'un +8% sur une obligation qui a une volatilité de 5%.<br><br>'
                    'La performance doit toujours être mise en relation avec le risque pris '
                    '(voir le Sharpe Ratio en section 7).'
                    '</div>', unsafe_allow_html=True)

        st.markdown("#### 1.4 — Lire une trajectoire stochastique")
        st.write("""
        Une courbe de cours n'est **jamais** lisse. Elle tremble, elle zigzague, elle rebondit. 
        Ce tremblement quotidien s'appelle le **bruit de marché**. Ce qui compte, c'est la **tendance 
        sous-jacente**. Trois signaux à identifier :
        
        - **La pente moyenne** : est-ce que globalement ça monte, descend, ou stagne ?
        - **L'amplitude des oscillations** : est-ce que les variations journalières sont de 0.5%, 
          2%, ou 10% ? Plus elles sont grandes, plus l'actif est risqué.
        - **Les cassures** : les moments où la courbe change brutalement de direction. 
          Ce sont souvent des événements majeurs (décision de banque centrale, résultats d'entreprise, 
          actualité géopolitique).
        """)

        st.markdown("#### 1.5 — Les bandes de confiance Monte-Carlo")
        st.write("""
        Quand vous activez le mode Monte-Carlo, les graphiques affichent non pas **une** trajectoire, 
        mais une **bande colorée** autour de la trajectoire médiane. Cette bande représente l'intervalle 
        dans lequel la vraie trajectoire a 90% de chances de se situer.
        
        **Pourquoi c'est essentiel ?** Parce qu'une simulation unique, c'est un coup de chance (ou de malchance). 
        En moyennant 50 simulations, on obtient une vision **statistiquement robuste** de l'avenir. 
        Plus la bande est large, plus l'incertitude est grande sur cet actif.
        """)

    # ---- 2. MODÈLES & MATHS ----
    with st_modeles:
        st.markdown("### Comment simuler l'avenir avec des mathématiques")
        st.write("""
        Personne ne peut prédire le marché. Mais on peut **modéliser les lois statistiques** qui le régissent. 
        C'est exactement ce que font les banques d'investissement, les hedge funds, et ce que fait 
        Quant Terminal en arrière-plan.
        """)

        st.markdown("#### 2.1 — Le modèle de Bachelier et le mouvement brownien")
        st.write("""
        En 1900, un étudiant français nommé Louis Bachelier soutient une thèse révolutionnaire 
        à la Sorbonne : "La théorie de la spéculation". Il propose que les cours de Bourse 
        se comportent comme des particules de pollen sous un microscope — un mouvement chaotique, 
        le **mouvement brownien**.
        
        Ce modèle, approfondi ensuite par Einstein (1905) et formalisé par Itō (1940), est devenu 
        le socle de toute la finance moderne. L'idée est simple : chaque jour, le prix varie d'une 
        quantité tirée au hasard selon une loi normale (courbe en cloche de Gauss).
        """)

        st.latex(r"S_{t+1} = S_t \times (1 + \mu \, \Delta t + \sigma \, \sqrt{\Delta t} \, Z)")

        st.write("""
        Où :
        - $S_t$ = prix à l'instant $t$
        - $\\mu$ = tendance (drift) — estimée ici par notre IA à partir du scénario macro
        - $\\sigma$ = volatilité — calibrée à partir des données historiques de l'actif
        - $Z$ = tirage aléatoire dans une loi normale centrée réduite $\\mathcal{N}(0,1)$
        
        C'est précisément la formule utilisée par le **modèle Black-Scholes** (Prix Nobel 1997) 
        pour pricer les options, et par toutes les grandes banques pour leurs calculs de risque.
        """)

        st.markdown("#### 2.2 — Pourquoi la loi normale est insuffisante")
        st.write("""
        Le modèle brownien a un défaut majeur : il sous-estime **gravement** la probabilité 
        des événements extrêmes. Selon une loi normale pure, un krach de -10% en un jour devrait 
        arriver **une fois tous les 10 000 ans**. Pourtant, ça s'est produit plusieurs fois 
        au cours des 40 dernières années (1987, 2008, 2020).
        
        C'est ce que Benoît Mandelbrot a appelé les **queues épaisses** (*fat tails*) : la réalité 
        des marchés n'est pas gaussienne, elle contient beaucoup plus d'événements extrêmes 
        que ne le prédit la théorie classique. C'est ce qui a mené à l'effondrement du fonds 
        **LTCM** en 1998 — deux prix Nobel au conseil, et pourtant ils ont fait faillite parce qu'ils 
        avaient sous-estimé les queues épaisses du risque russe.
        """)

        st.markdown('<div class="qt-callout-warn">'
                    '<strong>Leçon retenue :</strong> en finance, les événements "impossibles" '
                    'arrivent tous les 10 ans.<br><br>'
                    'Un bon modèle doit en tenir compte.'
                    '</div>', unsafe_allow_html=True)

        st.markdown("#### 2.3 — Les 3 modèles de Quant Terminal")

        st.markdown("**A. Modèle Probabiliste (Brownien classique)**")
        st.write("""
        Le plus courant. Chaque jour, variation = tendance + bruit gaussien. Bon pour les périodes 
        calmes et les actifs stables (obligations, grands indices). Mais il rate les krachs.
        """)

        st.markdown("**B. Modèle Historique (queues épaisses)**")
        st.write("""
        Ajoute une probabilité de 2% par jour d'un choc violent (x5 la volatilité normale). 
        Le modèle est globalement plus calme, mais déclenche régulièrement des mouvements brusques — 
        c'est une approximation simple des *fat tails* de Mandelbrot. Idéal pour tester la résilience 
        d'un portefeuille face aux cygnes noirs.
        """)

        st.markdown("**C. Modèle Machine Learning (momentum)**")
        st.write("""
        Inspiré des stratégies *trend-following* des hedge funds comme Renaissance Technologies 
        ou AQR. L'idée : quand une tendance est identifiée, elle s'auto-renforce (les investisseurs 
        suivent le mouvement). Mathématiquement, on fait croître l'impact de la tendance avec le temps.
        """)

        st.markdown("#### 2.4 — La méthode Monte-Carlo")
        st.write("""
        Nommée d'après le casino de Monaco, cette méthode a été inventée par Stanislaw Ulam 
        et John von Neumann dans les années 1940, pendant le projet Manhattan (bombe atomique). 
        L'idée est géniale : au lieu de résoudre analytiquement un problème impossible, 
        on **lance des milliers de simulations aléatoires** et on regarde les résultats.
        
        Exemple concret : on veut savoir ce que donne 100 € investis dans notre portefeuille 
        si on refait l'histoire 50 fois. On obtient 50 valeurs finales différentes. 
        On calcule :
        - La **médiane** (valeur centrale, 25 au-dessus et 25 en-dessous)
        - Le **percentile 5%** (seulement 5% des fois on a fait pire)
        - Le **percentile 95%** (seulement 5% des fois on a fait mieux)
        
        Ces 3 valeurs définissent la **bande de confiance à 90%**. C'est exactement ce que 
        font les actuaires, les ingénieurs nucléaires, et les banquiers d'investissement chaque jour.
        """)

        st.markdown("#### 2.5 — Rendements simples vs rendements logarithmiques")
        st.write("""
        Petit point technique pour les puristes. Quand un prix passe de 100 à 110, on dit que 
        le rendement est +10%. C'est le **rendement simple** : $r = \\frac{P_1 - P_0}{P_0}$.
        
        Mais quand on chaîne les rendements sur plusieurs périodes, les simples ne s'additionnent pas 
        proprement (+10% puis -10% ne fait pas 0, mais -1%). C'est pour ça que les professionnels 
        utilisent les **rendements logarithmiques** : $r_{log} = \\ln(P_1 / P_0)$. 
        Ils s'additionnent parfaitement et suivent plus proprement une loi normale.
        """)

    # ---- 3. MACRO-ÉCONOMIE ----
    with st_macro:
        st.markdown("### Les 3 forces qui contrôlent les marchés mondiaux")
        st.write("""
        Il y a des milliers d'actions cotées, des dizaines de devises, des centaines de matières premières. 
        Mais **trois forces invisibles** déterminent la direction globale de tout cela : 
        les taux d'intérêt, l'inflation, et la confiance des investisseurs.
        """)

        st.markdown("#### 3.1 — Les banques centrales : les véritables maîtres du jeu")
        st.write("""
        La Réserve Fédérale américaine (FED), la Banque Centrale Européenne (BCE), la Banque du Japon (BoJ), 
        la Banque Populaire de Chine (PBoC) — ces quatre institutions contrôlent l'essentiel de la liquidité 
        mondiale. Leur outil principal : le **taux directeur**, qui fixe le prix auquel les banques 
        commerciales peuvent emprunter de l'argent.
        """)

        st.markdown("**Quand les taux sont bas (argent gratuit) :**")
        st.write("""
        - Les entreprises empruntent massivement pour investir, innover, racheter leurs concurrents.
        - Les ménages empruntent pour acheter des maisons, des voitures.
        - Les investisseurs, ne trouvant plus de rendement dans les obligations (qui paient peu), 
          se ruent sur les **actions** et les actifs risqués. La Bourse explose.
        - Les cryptos, les valeurs tech non rentables, l'immobilier, tout gonfle.
        - Période emblématique : **2009-2021**, avec des taux proches de zéro après la crise de 2008.
        """)

        st.markdown("**Quand les taux sont hauts (argent cher) :**")
        st.write("""
        - Les crédits deviennent difficiles. Les projets d'investissement sont reportés.
        - Les entreprises endettées peinent à refinancer leur dette.
        - Les investisseurs peuvent placer leur argent **sans risque** dans des Bons du Trésor 
          à 5% — pourquoi prendre du risque sur des actions quand on peut gagner 5% en dormant ?
        - Résultat : rotation massive vers les obligations, chute des actions et des cryptos.
        - Période emblématique : **1979-1982** (Paul Volcker à la FED, taux à 20%), et **2022-2024** 
          (Jerome Powell face à l'inflation post-COVID).
        """)

        st.markdown("#### 3.2 — L'inflation : la taxe invisible qui ronge votre argent")
        st.write("""
        Quand l'inflation est à 5%, cela signifie que le niveau général des prix augmente de 5% 
        par an. Vos 100€ sur votre compte en banque conservent leur valeur nominale, 
        mais perdent **5% de leur pouvoir d'achat** réel chaque année.
        
        Sur 10 ans avec 5% d'inflation constante, votre argent perd **40%** de sa valeur réelle. 
        C'est pour cela qu'on dit que *"le cash est poubelle en période inflationniste"*.
        """)

        st.markdown("**Comment se protéger de l'inflation ?**")
        st.write("""
        On achète des choses **qu'on ne peut pas imprimer à l'infini** :
        
        - **Or** : quantité physique limitée dans la croûte terrestre, actif refuge depuis 5000 ans. 
          Pendant la crise des années 70 (inflation à 15% aux USA), l'or a été multiplié par 20.
        - **Matières premières** (pétrole, cuivre, blé) : leur prix monte avec le coût de la vie.
        - **Immobilier** : les loyers peuvent être indexés sur l'inflation.
        - **Actions d'entreprises avec pricing power** : entreprises capables d'augmenter leurs 
          prix sans perdre de clients (LVMH, Apple, Coca-Cola). On dit qu'elles ont une "douve" 
          (*moat*) selon Warren Buffett.
        - **Crypto** : Bitcoin a été inventé comme une réserve de valeur limitée à 21 millions 
          d'unités. En théorie, c'est un hedge contre l'inflation — en pratique, c'est beaucoup plus 
          corrélé au Nasdaq qu'on ne le pensait.
        """)

        st.markdown("#### 3.3 — La courbe des taux : l'indicateur préféré des récessions")
        st.write("""
        Voici un secret bien gardé : depuis 1960 aux États-Unis, **chaque récession a été précédée 
        par une inversion de la courbe des taux**. Cet indicateur a 100% de précision sur 60 ans.
        
        **La courbe des taux**, c'est le graphique qui montre le rendement des obligations d'État 
        à différentes maturités (3 mois, 2 ans, 5 ans, 10 ans, 30 ans). En temps normal, plus on 
        prête longtemps, plus on exige un rendement élevé (pour compenser le risque de long terme). 
        La courbe monte donc de gauche à droite.
        
        **Quand la courbe s'inverse** (les taux courts deviennent plus hauts que les taux longs), 
        c'est que le marché anticipe une baisse future des taux — donc une récession. C'est arrivé 
        en 2000, 2006, 2019, et mi-2022. À chaque fois, récession 6 à 18 mois plus tard.
        """)

        st.markdown("#### 3.4 — Le dollar américain : le soleil du système financier")
        st.write("""
        80% des transactions commerciales internationales se font en dollars. 60% des réserves 
        de change des banques centrales du monde sont en dollars. C'est ce qu'on appelle le 
        **privilège exorbitant** du dollar, formulé par Valéry Giscard d'Estaing en 1965.
        
        **Quand le dollar monte** (Dollar Index DXY en hausse) :
        - Les pays émergents souffrent : leur dette est souvent en dollars, et il leur en coûte 
          plus cher de la rembourser.
        - L'or baisse mécaniquement (il est coté en dollars).
        - Les matières premières deviennent plus chères pour le reste du monde → ralentissement 
          de la demande.
        
        **Quand le dollar baisse** : effet inverse, les émergents respirent, l'or brille.
        """)

        st.markdown("#### 3.5 — Le VIX : le thermomètre de la peur")
        st.write("""
        Le **VIX** (Volatility Index), calculé par le CBOE de Chicago, mesure la volatilité **attendue** 
        du S&P 500 sur les 30 prochains jours, extraite du prix des options. On l'appelle aussi 
        *"Fear Index"* (indice de la peur).
        
        - VIX < 15 : marché calme, euphorie, complaisance. Danger latent.
        - VIX 15-25 : volatilité normale.
        - VIX 25-40 : marché nerveux, tensions.
        - VIX > 40 : panique. Le VIX a culminé à 82 le 16 mars 2020 (COVID) et à 80 en octobre 2008 
          (Lehman Brothers).
        
        **Utilité pratique :** si vous pensez qu'une crise arrive, acheter du VIX (via des ETF comme VXX) 
        est une assurance contre les krachs boursiers.
        """)

    # ---- 4. CAS HISTORIQUES ----
    with st_cas:
        st.markdown("### Les grandes crises expliquées")
        st.write("""
        L'histoire boursière n'est pas une succession d'événements aléatoires. Chaque crise a sa logique, 
        ses victimes, et ses gagnants. Les comprendre, c'est mieux anticiper la prochaine.
        """)

        st.markdown("#### 4.1 — Le krach de 1929 et la Grande Dépression")
        st.write("""
        **Contexte :** Les années 1920 furent les "Roaring Twenties" — une décennie d'euphorie, 
        de spéculation effrénée, d'achats d'actions à crédit (*margin trading*) jusqu'à 90% de levier.
        
        **Le déclenchement :** le jeudi noir, 24 octobre 1929. Le Dow Jones perd 11% en une journée. 
        Puis le mardi 29 octobre, -12% supplémentaires. En quelques semaines, -50%. 
        Le marché ne retrouvera son niveau de 1929 qu'en **1954** — soit 25 ans plus tard.
        
        **Enseignements :**
        - L'effet de levier excessif est une bombe à retardement.
        - Les banques centrales peuvent aggraver une crise par leurs erreurs (la FED a resserré 
          au pire moment en 1931, ce qui a transformé un krach boursier en dépression mondiale).
        - Ce qui a sauvé les USA : le **New Deal** de Roosevelt (1933) et les dépenses publiques massives.
        """)

        st.markdown("#### 4.2 — Le Black Monday du 19 octobre 1987")
        st.write("""
        **Contexte :** Les bourses montent fort depuis 5 ans, nouvelles techniques de *program trading* 
        (algorithmes), portefeuilles dits "assurés" via des options.
        
        **Le déclenchement :** le 19 octobre 1987, le Dow Jones perd **-22.6% en une seule séance**. 
        Record absolu jamais égalé. Cause probable : les algorithmes de vente automatique ont déclenché 
        une cascade de ventes, sans intervention humaine pour l'arrêter.
        
        **Enseignement clé :** les systèmes automatisés peuvent créer des **boucles de rétroaction** 
        catastrophiques. C'est ce qui a mené à l'introduction des **coupe-circuits** (circuit breakers) 
        à Wall Street : la Bourse s'arrête automatiquement si ça baisse de trop.
        """)

        st.markdown("#### 4.3 — La bulle internet (1995-2002)")
        st.write("""
        **Contexte :** Internet se démocratise. Toute entreprise avec ".com" dans son nom voit sa 
        valorisation multipliée par 10. Des sociétés sans chiffre d'affaires valent des milliards. 
        Exemple emblématique : **Pets.com**, valorisée 300M$ en 2000, en faillite en 2001.
        
        **Le pic :** le Nasdaq atteint 5048 points en mars 2000. Il ne reviendra à ce niveau qu'en **2015** 
        — quinze ans de stagnation.
        
        **La chute :** -78% sur le Nasdaq entre 2000 et 2002. Destruction de 5 trillions de dollars 
        de capitalisation boursière.
        
        **Enseignement clé :** une technologie révolutionnaire peut être **réelle** (internet était bien 
        révolutionnaire) mais les **valorisations** peuvent être totalement délirantes. La question n'est 
        pas "cette technologie va-t-elle changer le monde ?" mais "à quel prix est-ce que je l'achète ?".
        """)

        st.markdown("#### 4.4 — La crise des subprimes (2007-2009)")
        st.write("""
        **Contexte :** les banques américaines ont accordé pendant des années des crédits immobiliers 
        à des ménages qui ne pouvaient pas rembourser (les *subprimes*). Ces crédits ont été 
        "titrisés" (transformés en produits financiers complexes, les CDO) et revendus dans le monde entier 
        comme s'ils étaient sûrs.
        
        **Le déclenchement :** en 2007, les prix de l'immobilier US commencent à baisser. 
        Les ménages ne remboursent plus. Les CDO perdent leur valeur. En septembre 2008, 
        **Lehman Brothers** fait faillite — la 4e plus grosse banque d'investissement américaine. 
        Panique mondiale.
        
        **La chute :** S&P 500 -57% entre octobre 2007 et mars 2009. Or : **+25%** sur la même période 
        (flight to quality). Bons du Trésor US 10 ans : rendement de 5% à 2%, prix des obligations explose.
        
        **Enseignement clé :** la complexité financière est une arme à double tranchant. Quand personne 
        ne comprend les produits qu'il détient, la confiance s'effondre en quelques jours. Warren Buffett 
        avait qualifié les dérivés d'*"armes de destruction massive financière"* dès 2003.
        """)

        st.markdown("#### 4.5 — Le krach COVID de mars 2020")
        st.write("""
        **Contexte :** marchés au plus haut, chômage US au plus bas depuis 50 ans, les investisseurs 
        pensent que rien ne peut arriver.
        
        **Le déclenchement :** le 11 mars 2020, l'OMS déclare une pandémie. En 23 jours, le S&P 500 perd 
        **-34%**. Record de vitesse historique — plus rapide que 1929, 1987 ou 2008.
        
        **Le rebond :** en moins de 6 mois, le marché a récupéré toutes ses pertes. Pourquoi ? 
        Parce que les banques centrales ont injecté **plus de 10 000 milliards de dollars** dans l'économie 
        mondiale. La FED a baissé ses taux à zéro en une semaine.
        
        **Enseignement clé :** en 2020, on a appris qu'il y a désormais un **"put implicite" des banques 
        centrales** sous les marchés. Quoi qu'il arrive, elles interviendront. Cela explique pourquoi 
        le marché a quasiment ignoré les mauvaises nouvelles de 2020-2021 : tout le monde parie sur 
        le sauvetage.
        """)

        st.markdown("#### 4.6 — Ce que l'histoire enseigne")
        st.markdown('<div class="qt-callout">'
                    '• Les krachs arrivent tous les 8-12 ans en moyenne. C\'est un <strong>fait statistique</strong>.<br><br>'
                    '• Chaque fois, les investisseurs disent "cette fois c\'est différent". Ce ne l\'est jamais vraiment.<br><br>'
                    '• Le meilleur moment pour acheter est souvent le plus inconfortable (mars 2009, mars 2020).<br><br>'
                    '• Diversifier à travers des actifs décorrélés (actions, obligations, or, cash) reste la seule défense sérieuse.<br><br>'
                    '• Les liquidités disponibles (cash) sont aussi une position : elles permettent d\'acheter quand tout est bradé.'
                    '</div>', unsafe_allow_html=True)

    # ---- 5. STRATÉGIES ----
    with st_strat:
        st.markdown("### Les grandes stratégies d'allocation d'actifs")
        st.write("""
        Il existe des centaines de stratégies d'investissement, mais 5 grandes écoles dominent 
        la réflexion institutionnelle. Les comprendre permet de choisir sa propre voie.
        """)

        st.markdown("#### 5.1 — Le portefeuille 60/40 (la stratégie classique)")
        st.write("""
        **60% d'actions, 40% d'obligations.** C'est le portefeuille de référence depuis les années 1950.
        L'idée : les actions offrent la croissance, les obligations la stabilité. Quand les actions 
        chutent, les obligations montent (flight to quality), ce qui amortit les pertes.
        
        **Performance historique** : environ +8% par an sur 50 ans aux USA, avec des drawdowns 
        maximaux autour de -25%. Raisonnable, peu spectaculaire, mais fiable.
        
        **Limite actuelle :** en 2022, actions ET obligations ont chuté en même temps (car les taux 
        ont flambé). Le 60/40 a fait -17%. Certains disent qu'il est "mort" — d'autres qu'il reste 
        la base raisonnable pour la plupart des épargnants.
        """)

        st.markdown("#### 5.2 — Le All Weather de Ray Dalio (Bridgewater)")
        st.write("""
        Ray Dalio, fondateur du plus gros hedge fund du monde (Bridgewater, 150 milliards $), 
        a conçu ce portefeuille qui doit fonctionner dans **tous les environnements économiques**. 
        Il part d'un constat simple : il existe 4 régimes économiques possibles :
        """)

        st.markdown("""
        | Régime | Inflation | Croissance | Ce qui marche |
        |---|---|---|---|
        | Goldilocks | Basse | Haute | Actions, obligations corporate |
        | Stagflation | Haute | Basse | Or, matières premières |
        | Reflation | Haute | Haute | Actions, immobilier, matières premières |
        | Déflation | Basse | Basse | Obligations longues, cash |
        """)

        st.write("""
        **Sa recette** : 30% actions, 40% obligations longues US, 15% obligations moyennes, 
        7,5% or, 7,5% matières premières. L'idée : avoir une exposition à chaque régime pour ne 
        jamais être totalement perdant.
        
        **Performance** : sur 40 ans, rendement annualisé de 8%, mais avec des drawdowns plus faibles 
        que le 60/40. Moins brillant en bull market, plus résilient en crise.
        """)

        st.markdown("#### 5.3 — La Risk Parity")
        st.write("""
        Stratégie sœur du All Weather, développée dans les années 1990. Au lieu de répartir l'argent 
        en pourcentages (60/40), on répartit le **risque**. Chaque classe d'actif contribue à parts 
        égales à la volatilité totale du portefeuille.
        
        En pratique : comme les obligations sont 4x moins volatiles que les actions, un portefeuille 
        risk parity contient souvent **beaucoup plus d'obligations en valeur** (avec parfois du levier 
        pour booster leur rendement). Assez contre-intuitif pour un débutant.
        """)

        st.markdown("#### 5.4 — Le value investing (Warren Buffett, Benjamin Graham)")
        st.write("""
        Formalisé en 1934 par Benjamin Graham dans "Security Analysis" et "The Intelligent Investor", 
        puis rendu célèbre par son élève Warren Buffett.
        
        **Principe** : chaque action a une **valeur intrinsèque** (basée sur ses profits futurs actualisés). 
        Le marché est parfois irrationnel et vend une action bien en-dessous de cette valeur. 
        Le value investor achète alors, attend que le marché redevienne rationnel, et vend quand 
        le prix dépasse la valeur intrinsèque.
        
        **Les critères de Buffett :**
        - Entreprise avec une **"douve économique"** durable (brevets, marque forte, effet réseau)
        - Management de qualité
        - Faible endettement
        - Historique de profits stables
        - Prix d'achat **raisonnable** par rapport aux profits (ratio P/E bas)
        
        **Exemples emblématiques** : Coca-Cola (acheté en 1988, x20 depuis), Apple (x6 depuis 2016), 
        American Express.
        """)

        st.markdown("#### 5.5 — Le momentum / trend following")
        st.write("""
        Stratégie opposée au value. L'idée : *"the trend is your friend"* (la tendance est ton amie). 
        On achète ce qui monte, on vend ce qui baisse. Empiriquement, les actifs qui ont monté 
        sur les 6-12 derniers mois ont tendance à continuer à monter sur les 3-6 mois suivants — 
        c'est l'**effet momentum**, documenté par Jegadeesh & Titman (1993).
        
        **Qui l'utilise ?** Les hedge funds systématiques comme **AHL (Man Group)**, **Winton Capital**, 
        ou **Renaissance Technologies** (James Simons, le mathématicien le plus riche du monde). 
        Ils gèrent des centaines de milliards sur ce principe.
        """)

        st.markdown("#### 5.6 — Pour choisir votre stratégie")
        st.markdown('<div class="qt-callout">'
                    'Il n\'y a pas de "meilleure" stratégie dans l\'absolu. Tout dépend de :<br><br>'
                    '• <strong>Votre horizon</strong> : 5 ans vs 30 ans, ce n\'est pas la même chose.<br><br>'
                    '• <strong>Votre tolérance au risque</strong> : pouvez-vous dormir si votre portefeuille perd -40% ?<br><br>'
                    '• <strong>Vos objectifs</strong> : préservation du capital, rendement, héritage ?<br><br>'
                    '• <strong>Vos compétences</strong> : le value investing demande de savoir analyser un bilan, '
                    'le momentum d\'avoir une discipline de fer.'
                    '</div>', unsafe_allow_html=True)

    # ---- 6. LEXIQUE ----
    with st_lex:
        st.markdown("### Le lexique du professionnel")

        st.markdown("#### Marchés & cycles")
        st.markdown("""
        - **Bull Market** — Marché haussier (image du taureau qui attaque de bas en haut).
        - **Bear Market** — Marché baissier (-20% minimum depuis le pic). L'ours attaque de haut en bas.
        - **Correction** — Baisse entre -10% et -20%. Saine et fréquente.
        - **Krach** — Chute brutale et rapide (>-10% en quelques jours).
        - **Rally** — Hausse rapide après une baisse.
        - **Melt-up** — Hausse euphorique et irrationnelle (comme fin 2020-2021).
        """)

        st.markdown("#### Banques centrales")
        st.markdown("""
        - **Hawkish** (faucon) — Banquier central qui veut monter les taux pour combattre l'inflation.
        - **Dovish** (colombe) — Banquier central qui veut baisser les taux pour stimuler l'économie.
        - **Quantitative Easing (QE)** — Impression de monnaie par la banque centrale pour acheter des actifs. Stimule l'économie.
        - **Quantitative Tightening (QT)** — Opération inverse : la banque centrale réduit son bilan. Resserre.
        - **Forward guidance** — Communication sur la trajectoire future des taux pour guider les anticipations.
        """)

        st.markdown("#### Mesures de risque")
        st.markdown("""
        - **Volatilité (σ)** — Écart-type des rendements. Mesure l'amplitude des variations.
        - **Sharpe Ratio** — Rendement par unité de risque. >1 = bon, >2 = excellent, <0 = mauvais.
        - **Sortino Ratio** — Version du Sharpe qui ne pénalise que la volatilité baissière.
        - **Beta (β)** — Sensibilité d'un actif au marché. β=1 bouge comme le marché, β=2 amplifie x2.
        - **Alpha (α)** — Surperformance par rapport au benchmark. L'alpha pur = talent du gérant.
        - **Drawdown** — Chute depuis un plus-haut. Mesure ultime du stress d'un portefeuille.
        - **VaR (Value at Risk)** — Perte maximale probable avec un niveau de confiance (ex: 95%).
        - **CVaR / Expected Shortfall** — Moyenne des pertes au-delà de la VaR. Plus conservateur.
        """)

        st.markdown("#### Produits dérivés")
        st.markdown("""
        - **Call** — Option d'achat. Donne le droit d'acheter à un prix fixé.
        - **Put** — Option de vente. Donne le droit de vendre à un prix fixé.
        - **Strike** — Prix d'exercice d'une option.
        - **Maturité** — Date d'échéance d'une option ou d'une obligation.
        - **Delta (Δ)** — Sensibilité du prix d'une option au prix du sous-jacent.
        - **Gamma (Γ)** — Sensibilité du delta au prix du sous-jacent.
        - **Theta (Θ)** — Perte de valeur d'une option due au temps qui passe.
        - **Vega** — Sensibilité du prix d'une option à la volatilité.
        """)

        st.markdown("#### Obligations")
        st.markdown("""
        - **Yield** — Rendement d'une obligation à l'échéance.
        - **Spread** — Écart de rendement entre deux obligations. Ex: spread Italie-Allemagne = prime de risque italienne.
        - **Duration** — Sensibilité du prix d'une obligation à une variation des taux. Duration 10 = -10% si les taux montent de 1%.
        - **Convexité** — Raffinement de la duration pour les gros mouvements de taux.
        - **Investment Grade** — Obligations notées BBB- ou mieux. Risque faible.
        - **High Yield / Junk Bonds** — Obligations notées en-dessous de BBB-. Rendement élevé mais risque de défaut réel.
        """)

        st.markdown("#### Trading & stratégie")
        st.markdown("""
        - **Long** — Position à la hausse (on achète en espérant que ça monte).
        - **Short** — Position à la baisse (on vend à découvert en espérant racheter moins cher).
        - **Hedge** — Couverture. Position prise pour réduire le risque d'une autre.
        - **Leverage** / Levier — Emprunt pour amplifier les gains (et les pertes).
        - **Carry trade** — Emprunter dans une devise à taux bas, investir dans une devise à taux haut.
        - **Arbitrage** — Exploiter une différence de prix entre deux marchés pour un gain sans risque (théoriquement).
        - **Flight to quality** — Fuite vers la qualité : vente massive d'actifs risqués, achat d'actifs sûrs.
        - **Risk-on / Risk-off** — Période où les investisseurs prennent du risque (risk-on) ou le fuient (risk-off).
        """)

        st.markdown("#### Comptabilité & finance d'entreprise")
        st.markdown("""
        - **PnL** (*Profit and Loss*) — Compte de résultat. Bénéfice ou perte.
        - **EBITDA** — Bénéfice avant intérêts, impôts, dépréciation et amortissement. Mesure opérationnelle.
        - **Cash-flow libre (FCF)** — Trésorerie générée par l'activité, disponible pour les actionnaires.
        - **P/E ratio** — Cours / Bénéfice par action. Plus c'est haut, plus l'action est "chère" (ou en forte croissance).
        - **ROE** — Return on Equity. Rentabilité des fonds propres.
        - **Dilution** — Quand une entreprise émet de nouvelles actions, chaque actionnaire possède un pourcentage plus petit.
        """)

    # ---- 7. MÉTHODOLOGIE ----
    with st_methodo:
        st.markdown("### Méthodologie mathématique de Quant Terminal")
        st.write("""
        Pour les utilisateurs exigeants (et les professeurs), voici les formules exactes 
        implémentées dans le terminal.
        """)

        st.markdown("#### A. Volatilité annualisée")
        st.latex(r"\sigma_{annuel} = \sigma_{quotidien} \times \sqrt{252}")
        st.write("""
        On multiplie l'écart-type des rendements journaliers par √252 (nombre de jours de cotation 
        dans l'année). Pourquoi √252 et pas 252 ? Parce que la variance s'additionne linéairement 
        avec le temps, donc l'écart-type croît en √t. C'est une conséquence du théorème central limite.
        """)

        st.markdown("#### B. Sharpe Ratio")
        st.latex(r"Sharpe = \frac{R_p - R_f}{\sigma_p}")
        st.write("""
        $R_p$ = rendement annualisé du portefeuille, $R_f$ = taux sans risque (2% par défaut, 
        correspondant approximativement au rendement des Bons du Trésor US court terme), 
        $\\sigma_p$ = volatilité annualisée.
        
        Créé par William Sharpe en 1966 (Prix Nobel 1990). C'est **la** métrique universellement utilisée 
        par les gérants professionnels. Un Sharpe de 1 signifie que pour chaque unité de risque prise, 
        vous avez gagné 1 unité de rendement au-dessus du taux sans risque. En dessous de 0.5, 
        l'effort de prendre du risque n'en vaut pas la peine.
        """)

        st.markdown("#### C. Max Drawdown")
        st.latex(r"DD_{max} = \max_{t} \left( \frac{Peak_t - V_t}{Peak_t} \right)")
        st.write("""
        $Peak_t$ = plus-haut historique au temps $t$, $V_t$ = valeur au temps $t$.
        C'est la pire chute subie depuis un sommet précédent. Mesure cruciale car elle reflète 
        la **vraie souffrance** psychologique d'un investisseur : voir son capital fondre de -30% 
        est bien plus traumatisant qu'une volatilité élevée.
        
        Pendant le krach de 1929, le Dow Jones a subi un drawdown de **-89%** sur 3 ans. 
        Pendant 2008, le S&P 500 a fait **-57%**. Pendant le COVID, **-34% en 23 jours**.
        """)

        st.markdown("#### D. Value at Risk (VaR)")
        st.latex(r"VaR_{95\%} = \text{Percentile}_{5\%}(\text{rendements})")
        st.write("""
        La VaR 95% à 1 jour répond à la question : *"Quelle est la perte maximale que je ne dépasserai 
        pas dans 95% des cas en une journée ?"*. C'est le rendement situé au 5e percentile (5% les pires 
        rendements). 
        
        **Attention** : la VaR ne dit rien sur ce qui se passe dans les 5% restants — les *tail risks*. 
        C'est pour ça qu'on la complète souvent par la **CVaR** (Conditional VaR), qui calcule 
        la moyenne des pertes **au-delà** de la VaR. Beaucoup plus conservateur.
        """)

        st.markdown("#### E. Mouvement Brownien Géométrique (modèle Probabiliste)")
        st.latex(r"\frac{dS_t}{S_t} = \mu \, dt + \sigma \, dW_t")
        st.write("""
        En discrétisant sur un pas journalier :
        """)
        st.latex(r"S_{t+1} = S_t \times (1 + \mu + \sigma \cdot Z_t)")
        st.write("""
        Avec $Z_t \\sim \\mathcal{N}(0, 1)$ un tirage gaussien indépendant à chaque pas de temps. 
        C'est exactement la formule utilisée dans le code de Quant Terminal pour le modèle "Probabiliste".
        
        Le $\\mu$ (drift) est estimé par notre IA à partir du scénario macro-économique, tandis que 
        le $\\sigma$ (volatilité) est calibré à partir des données historiques de chaque actif.
        """)

        st.markdown("#### F. Méthode Monte-Carlo")
        st.write("""
        On simule $N=50$ trajectoires indépendantes. Pour chaque jour $t$ et chaque actif, on calcule :
        """)
        st.latex(r"\text{Médiane}_t = \text{percentile}_{50}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})")
        st.latex(r"\text{Bas}_t = \text{percentile}_{5}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})")
        st.latex(r"\text{Haut}_t = \text{percentile}_{95}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})")
        st.write("""
        L'intervalle [Bas, Haut] constitue la **bande de confiance à 90%** : dans 90% des cas simulés, 
        le prix à l'instant $t$ se trouve dans cette bande.
        
        La méthode Monte-Carlo converge en $O(1/\\sqrt{N})$ : pour doubler la précision, il faut 
        quadrupler le nombre de simulations. Avec 50 simulations, la précision est typiquement 
        de ±5% sur les percentiles — suffisant pour un outil éducatif. Les grandes banques utilisent 
        couramment 10 000 à 1 000 000 de simulations pour leurs calculs réglementaires (Bâle III, FRTB).
        """)

        st.markdown("#### G. Limites connues de notre modèle")
        st.markdown('<div class="qt-callout-warn">'
                    '<strong>Pour l\'honnêteté intellectuelle</strong>, voici les limites de Quant Terminal :<br><br>'
                    '• Les volatilités sont supposées <strong>constantes</strong>, alors qu\'en réalité elles '
                    'se regroupent en clusters (effet GARCH).<br><br>'
                    '• Les actifs sont traités <strong>indépendamment</strong>, alors qu\'en crise toutes '
                    'les corrélations montent à 1 (voir 2008).<br><br>'
                    '• L\'IA fournit une estimation <strong>globale</strong> du choc, pas une trajectoire '
                    'fine dans le temps.<br><br>'
                    '• Les distributions restent <strong>gaussiennes</strong>, sauf dans le mode Historique. '
                    'La réalité a des queues encore plus épaisses.<br><br>'
                    '• Pas de prise en compte des <strong>coûts de transaction</strong>, des <strong>spreads bid-ask</strong>, '
                    'ni de la <strong>liquidité</strong>.<br><br>'
                    'Quant Terminal est un outil <strong>pédagogique</strong>. '
                    'Pour un usage professionnel réel, il faudrait ajouter ces raffinements et calibrer '
                    'le modèle sur des données de marché en temps réel.'
                    '</div>', unsafe_allow_html=True)


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
        ("Lukha Doazan",      "Étudiant en MIASHS et Économie & Gestion"),
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


# ==========================================
# 18. FOOTER GLOBAL (toutes pages)
# ==========================================

st.markdown(f"""
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
        © 2026 Quant Terminal · Tous droits réservés ·
        <span style="opacity:0.7;">Outil non destiné à un usage financier professionnel</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 19. TOASTS DE NOTIFICATION (si simulation vient d'aboutir)
# ==========================================

# On utilise un flag pour éviter de re-déclencher le toast à chaque rerun
if st.session_state.get("_just_simulated", False):
    st.toast("✅ Simulation terminée avec succès !", icon="🎉")
    st.session_state["_just_simulated"] = False

if st.session_state.get("_just_backtested", False):
    st.toast("✅ Backtest terminé !", icon="📊")
    st.session_state["_just_backtested"] = False

if st.session_state.get("_just_pdf", False):
    st.toast("📄 Rapport PDF prêt !", icon="✅")
    st.session_state["_just_pdf"] = False