import os
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key)


def analyser_evenement_macro(evenement_utilisateur, calibration_historique=False):
    instruction_calibration = ""
    if calibration_historique:
        instruction_calibration = """

    CALIBRATION HISTORIQUE (IMPORTANT) :
    Avant d'estimer les chocs, identifie l'événement historique le plus PROCHE du scénario décrit.
    Utilise les amplitudes RÉELLES observées lors de cet événement comme référence.
    Exemples :
    - Krach 2008 (Lehman) : S&P 500 -57%, Or +25%, Bons Trésor US +15%, VIX +400%, Pétrole -75%
    - COVID mars 2020 : S&P 500 -34% en 23 jours, Or +12%, Pétrole -65%, VIX +500%, Bitcoin -50%
    - Choc pétrolier 1973 : S&P 500 -48%, Or +400%, Pétrole +400%, Inflation +15%
    - Bulle internet 2000-2002 : Nasdaq -78%, S&P 500 -49%, Or +20%, Obligations +20%
    - Hausse FED 2022 : S&P 500 -25%, Bonds -15%, Or +0%, Crypto -75%, Dollar +15%
    - Brexit 2016 : Livre -10%, FTSE -10% puis rebond, Or +5%
    - Guerre Russie-Ukraine 2022 : Pétrole +60%, Gaz +400%, Cuivre +20%, Émergents -25%

    Inclus dans 'explication_courte' la mention de l'événement de référence.
    Adapte les chocs à la SÉVÉRITÉ du scénario.
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

    Si valide, réponse en JSON :
    {{
        "macro": {{"inflation": <CHIFFRE>, "taux_directeurs": <CHIFFRE>}},
        "actifs": {{
            "S&P 500": 0.0, "NASDAQ": 0.0, "CAC 40": 0.0, "MSCI_World": 0.0, "Emerging_Markets": 0.0,
            "Bons_Tresor_US_10Y": 0.0, "Bund_10Y": 0.0, "OAT_10Y": 0.0, "JGB_10Y": 0.0, "Gilt_10Y": 0.0,
            "EUR_USD": 0.0, "Dollar_Index": 0.0, "VIX": 0.0,
            "Or": 0.0, "Argent": 0.0, "Petrole": 0.0, "Cuivre": 0.0, "ETF_Terres_Rares": 0.0,
            "ETF_Defense": 0.0,
            "Bitcoin": 0.0, "Ethereum": 0.0, "XRP": 0.0, "Solana": 0.0
        }},
        "explication_courte": "Explication d'une phrase, mentionnant l'événement historique de référence si calibration activée.",
        "evenement_reference": "Nom de l'événement historique utilisé, ou null."
    }}

    IMPORTANT :
    - "inflation" et "taux_directeurs" en pourcentage (ex: 2.5 pour +2.5%).
    - Actifs en décimal (ex: -0.15 pour -15%).
    - Corrélations à respecter :
        * Hausse taux → obligations baissent, actions baissent, VIX monte, Dollar_Index monte
        * Inflation forte → Or/Argent/Cuivre montent, obligations baissent
        * Crise géopolitique → VIX monte, ETF_Defense monte, Or monte, Émergents baissent
        * Dollar fort → Émergents baissent, Or baisse, EUR_USD baisse
        * Récession → Cuivre/Pétrole/S&P 500 baissent, obligations montent
        * Boom tech → NASDAQ monte plus que S&P 500, cryptos peuvent monter
        * Tensions géopolitiques → Terres Rares et Défense montent
    """

    try:
        reponse = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(reponse.choices[0].message.content)
    except Exception as e:
        return {"erreur": f"Erreur de connexion à l'IA : {str(e)}"}


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
