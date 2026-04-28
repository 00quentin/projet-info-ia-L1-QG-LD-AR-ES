import os
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from schemas import valider_reponse_ia
from logger import get_logger

log = get_logger("ia_bot")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key, timeout=20.0, max_retries=1)


def analyser_evenement_macro(evenement_utilisateur, calibration_historique=False):
    instruction_calibration = ""
    if calibration_historique:
        instruction_calibration = """

    CALIBRATION HISTORIQUE (IMPORTANT) :
    Avant d'estimer les chocs, identifie l'événement historique le plus PROCHE du scénario décrit.
    Utilise les amplitudes RÉELLES observées lors de cet événement comme référence.
    Tableau de référence (sur 100 jours environ) :
    - Krach 2008 (Lehman) : S&P 500 -40%, Or +15%, Bons Trésor US +12%, VIX +200%, Pétrole -50%
    - COVID mars 2020 : S&P 500 -34% en 23j, Or +12%, Pétrole -65%, VIX +500%, Bitcoin -50%
    - Choc pétrolier 1973 : S&P 500 -30% (sur 100j), Or +60%, Pétrole +200%, Inflation +5%
    - Bulle internet 2000 : Nasdaq -40% (sur 100j), S&P 500 -25%, Or +5%
    - Hausse FED 2022 (sur 100j) : S&P 500 -15%, Bonds -8%, Crypto -50%, Dollar +8%
    - Brexit 2016 : Livre -10%, FTSE -5% puis rebond, Or +5%
    - Russie-Ukraine 2022 (100 premiers jours) : Pétrole +35%, Cuivre +10%, Émergents -15%
    - Helicopter money / impression massive (cas COVID 2020 + cas années 70) :
        Or +15 à +30%, Cryptos +40 à +100%, Actions +10 à +25% (inflation actifs),
        Dollar -8 à -15%, Pétrole +20 à +40%, Obligations -5 à -15%

    L'événement historique de référence DOIT être mentionné dans 'explication_courte'.
    """

    prompt = f"""Tu es un analyste quantitatif institutionnel travaillant pour Quant Terminal.
    Ton rôle est d'évaluer l'impact macro-économique du scénario suivant : "{evenement_utilisateur}".

    CRITÈRE DE VALIDATION :
    - L'événement doit avoir un impact plausible sur la production, la consommation, la confiance, les ressources, la monnaie ou la stabilité politique.
    - Si totalement absurde, renvoie un dictionnaire avec une erreur.

    TOLÉRANCE :
    - Accepte les scénarios prospectifs sérieux (fusion nucléaire, AGI, guerre, pandémie, etc.).
{instruction_calibration}

    Format erreur :
    {{
        "erreur": "Ce scénario ne semble pas lié à l'économie ou à la géopolitique."
    }}

    *** MÉTHODOLOGIE OBLIGATOIRE EN 4 ÉTAPES ***

    ÉTAPE 1 - CLASSIFIER LA SÉVÉRITÉ :
    Évalue d'abord la sévérité du scénario sur une échelle :
    - Léger (1) : annonce, ajustement marginal, mini-conflit régional → variations 1-5%
    - Modéré (2) : récession, crise sectorielle, conflit régional → variations 5-15%
    - Fort (3) : crise majeure type 2008 ou COVID → variations 15-30%
    - Extrême (4) : guerre mondiale, effondrement systémique → variations 30-50%
    - Apocalyptique (5) : extinction, guerre nucléaire totale → variations 50%+

    ÉTAPE 2 - HORIZON :
    L'horizon est de 100 jours de cotation (~5 mois). Les chocs doivent être
    proportionnés à cette durée. Sur 5 mois, même la crise de 1929 n'a pas fait -89%
    (cette baisse s'est étalée sur 3 ans).

    ÉTAPE 3 - APPLIQUER LES CORRÉLATIONS RÉELLES :
    - Hausse taux → obligations baissent, actions baissent, VIX monte, Dollar monte
    - Inflation forte → Or/Argent montent (modérément), obligations baissent, actions montent légèrement
    - Crise géopolitique → VIX monte, Défense monte, Or monte, Émergents baissent
    - Récession → Cuivre/Pétrole/Actions baissent, obligations montent
    - Boom tech → NASDAQ monte plus que S&P 500, cryptos peuvent monter fort
    - "Impression massive de monnaie" (helicopter money) :
        → Le dollar BAISSE, l'or MONTE modérément (+15 à +35%),
          les CRYPTOS MONTENT (vues comme hedge anti-fiat, +40 à +100%),
          les actions montent (inflation des actifs, +10 à +25%),
          les obligations long terme baissent (-5 à -15%)
        → Les cryptos NE S'EFFONDRENT PAS, c'est l'inverse de leur thèse fondamentale

    ÉTAPE 4 - AUTO-VÉRIFICATION (CRUCIAL) :
    Avant de finaliser, vérifie chaque chiffre :
    a) Est-il cohérent avec un événement historique connu de sévérité comparable ?
    b) Est-il plausible sur 100 jours (et pas sur 10 ans) ?
    c) Respecte-t-il les corrélations économiques ?
    d) Ai-je évité les valeurs aberrantes (>+500% ou <-90%) ?
    Si une réponse est NON, recalibre AVANT de répondre.

    *** REPÈRES D'AMPLITUDE TYPIQUES ***
    Pour t'aider à calibrer (ces ranges couvrent 95% des scénarios sérieux) :
    - Actions : -50% à +40% (au-delà = scénario apocalyptique)
    - Obligations : -25% à +20%
    - Or : -20% à +50% (au-delà = hyper-inflation des années 70 inversée)
    - Pétrole : -65% à +80%
    - Cryptos : -75% à +200%
    - VIX : -50% à +500%
    Ces repères sont des ORDRES DE GRANDEUR. Tu peux dépasser SI le scénario le justifie
    vraiment (guerre nucléaire totale, extinction, etc.) — mais c'est rare.

    Format JSON de réponse :
    {{
        "macro": {{"inflation": <CHIFFRE %>, "taux_directeurs": <CHIFFRE %>}},
        "actifs": {{
            "S&P 500": 0.0, "NASDAQ": 0.0, "CAC 40": 0.0, "MSCI_World": 0.0, "Emerging_Markets": 0.0,
            "Bons_Tresor_US_10Y": 0.0, "Bund_10Y": 0.0, "OAT_10Y": 0.0, "JGB_10Y": 0.0, "Gilt_10Y": 0.0,
            "EUR_USD": 0.0, "Dollar_Index": 0.0, "VIX": 0.0,
            "Or": 0.0, "Argent": 0.0, "Petrole": 0.0, "Cuivre": 0.0, "ETF_Terres_Rares": 0.0,
            "ETF_Defense": 0.0,
            "Bitcoin": 0.0, "Ethereum": 0.0, "XRP": 0.0, "Solana": 0.0
        }},
        "explication_courte": "Analyse en 3-4 phrases minimum : (1) sévérité du scénario et événement historique de référence, (2) mécanisme économique principal, (3) actifs gagnants et raisons, (4) actifs perdants et raisons.",
        "evenement_reference": "Nom de l'événement historique de référence (ex: 'COVID 2020', 'Crise 2008', 'Helicopter money 2020'), ou null."
    }}

    RAPPELS FORMATS :
    - "inflation" et "taux_directeurs" en pourcentage (ex: 2.5 pour +2.5%, -0.75 pour -0.75%)
    - Actifs en décimal (ex: -0.15 pour -15%, 0.30 pour +30%)
    - "explication_courte" DOIT faire au minimum 3-4 phrases
    """

    try:
        log.info("Appel OpenAI pour analyse macro (calibration=%s)", calibration_historique)
        reponse = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        contenu_brut = json.loads(reponse.choices[0].message.content)

        # VALIDATION PYDANTIC : normalise, borne, rejette si invalide
        resultat = valider_reponse_ia(contenu_brut)

        if "erreur" in resultat:
            log.warning("Validation IA rejetée : %s", resultat["erreur"])
        else:
            log.info("Analyse IA validée (event=%s)",
                     resultat.get("evenement_reference"))

        return resultat

    except Exception as e:
        log.error("Erreur appel IA : %s", e, exc_info=True)
        return {"erreur": f"Erreur de connexion à l'IA : {str(e)[:120]}"}


def discuter_avec_ia(historique_messages):
    messages = [{
        "role": "system",
        "content": (
            "Tu es un Analyste Financier Senior travaillant pour le terminal institutionnel 'Quant Terminal'. "
            "Tu as un ton professoral, précis et professionnel. "
            "Tu utilises un vocabulaire financier expert (Bull market, hawkish, dovish, PnL, Flight to quality, "
            "DXY, VIX, spread obligataire, corrélation inter-actifs) mais tu vulgarises tes conclusions. "
            "Tu couvres toutes les classes d'actifs : actions, obligations, matières premières, devises, "
            "volatilité, sectoriels, cryptomonnaies. Tu connais les crises historiques (1929, 1987, 2000, 2008, 2020)."
        )
    }]
    messages.extend(historique_messages)

    try:
        reponse = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.6
        )
        return reponse.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur de communication avec l'analyste : {str(e)}"


def generer_rapport_complet_ia(scenario, chocs_ia, perf_par_actif, metriques,
                                 valeur_initiale, valeur_finale, profil):
    """
    Génère une analyse complète et détaillée pour le rapport PDF,
    rédigée comme un vrai analyste financier senior.
    """
    perf_globale = (valeur_finale - valeur_initiale) / valeur_initiale * 100

    # Construire le résumé de performance par actif
    perfs_text = "\n".join([
        f"- {row['Actif']} : {row['Performance (%)']:+.2f}%"
        for _, row in perf_par_actif.iterrows()
    ])

    prompt = f"""Tu es un Analyste Financier Senior d'une grande banque d'investissement.
Tu rédiges un rapport d'analyse pour un client institutionnel suite à une simulation Quant Terminal.

CONTEXTE DE LA SIMULATION :
- Scénario testé : "{scenario}"
- Profil d'investisseur : {profil}
- Capital initial : {valeur_initiale:,.0f} €
- Valeur finale du portefeuille : {valeur_finale:,.0f} €
- Performance globale : {perf_globale:+.2f}%

ANALYSE MACRO IA (synthèse) :
{chocs_ia.get('explication_courte', 'Non disponible')}

PERFORMANCE PAR ACTIF :
{perfs_text}

MÉTRIQUES DE RISQUE :
- Volatilité annualisée : {metriques['vol_ann']:.2f}%
- Sharpe Ratio : {metriques['sharpe']:.2f}
- Max Drawdown : -{metriques['max_dd']:.2f}%
- VaR 95% (1 jour) : {metriques['var_95']:.2f}%

TA MISSION :
Rédige un rapport d'analyse professionnel, structuré et détaillé, en 4 sections numérotées :

**1. Synthèse exécutive (3-4 phrases)** — Bilan global du portefeuille face à ce scénario, performance vs profil de risque, jugement professionnel sur la solidité.

**2. Mécanique économique (4-5 phrases)** — Explique en détail POURQUOI ce scénario produit ces résultats. Quels canaux de transmission économiques sont à l'œuvre ? Inflation, taux, confiance, liquidité, géopolitique ? Cite des références historiques pertinentes (2008, COVID, 1973, etc.).

**3. Décomposition par classe d'actifs (5-6 phrases)** — Analyse les actifs qui ont le mieux et le moins bien performé. Pourquoi ces écarts ? Quelle logique de marché (flight to quality, rotation sectorielle, prime de risque, etc.) ? Mentionne 2-3 actifs spécifiques avec des chiffres.

**4. Recommandations & implications (3-4 phrases)** — Que devrait faire un investisseur dans cette configuration ? Quelles classes d'actifs renforcer ou alléger ? Quels risques surveiller ? Limites de cette simulation ?

CONTRAINTES :
- Ton institutionnel, professoral, précis.
- Utilise du vocabulaire financier (volatilité réalisée, spread, beta, drawdown, momentum, etc.).
- Mais vulgarise les concepts pour qu'un client comprenne.
- Pas de listes à puces, du texte en paragraphes coulés.
- Utilise du **gras** sur les points clés (avec des étoiles markdown ** **).
- Longueur totale : entre 400 et 600 mots.
"""

    try:
        reponse = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un analyste financier senior expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1200,
        )
        return reponse.choices[0].message.content
    except Exception as e:
        return f"Analyse non disponible (erreur IA : {str(e)})"