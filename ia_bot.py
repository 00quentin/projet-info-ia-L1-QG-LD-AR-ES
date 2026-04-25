import os
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key)


def analyser_evenement_macro(evenement_utilisateur, calibration_historique=False):
    """
    Analyse un scénario macro et retourne les chocs sur les actifs.
    
    - calibration_historique : si True, l'IA s'inspire de crises historiques connues
      (2008, COVID, 1973, etc.) pour calibrer ses chocs avec des amplitudes réalistes.
    """
    
    instruction_calibration = ""
    if calibration_historique:
        instruction_calibration = """
    
    CALIBRATION HISTORIQUE (IMPORTANT) :
    Avant d'estimer les chocs, identifie l'événement historique le plus PROCHE du scénario décrit.
    Utilise les amplitudes RÉELLES observées lors de cet événement comme référence.
    Exemples de calibration :
    - Krach 2008 (Lehman) : S&P 500 -57%, Or +25%, Bons Trésor US +15%, VIX +400%, Pétrole -75%
    - COVID mars 2020 : S&P 500 -34% en 23 jours, Or +12%, Pétrole -65%, VIX +500%, Bitcoin -50%
    - Choc pétrolier 1973 : S&P 500 -48%, Or +400%, Pétrole +400%, Inflation +15%
    - Bulle internet 2000-2002 : Nasdaq -78%, S&P 500 -49%, Or +20%, Obligations +20%
    - Hausse FED 2022 : S&P 500 -25%, Bonds -15%, Or +0%, Crypto -75%, Dollar +15%
    - Brexit 2016 : Livre -10% en 1 jour, FTSE -10% puis rebond, Or +5%
    - Guerre Russie-Ukraine 2022 : Pétrole +60%, Gaz +400%, Cuivre +20%, Émergents -25%
    
    Inclus dans 'explication_courte' la mention de l'événement de référence utilisé.
    Adapte les chocs à la SÉVÉRITÉ du scénario : un mini-conflit régional ne fait pas COVID.
    """
    
    prompt = f"""Tu es un analyste quantitatif institutionnel travaillant pour Quant Terminal.
    Ton rôle est d'évaluer l'impact macro-économique du scénario suivant : "{evenement_utilisateur}".

    CRITÈRE DE VALIDATION :
    - L'événement doit avoir un impact plausible sur : la production, la consommation, la confiance des investisseurs, les ressources naturelles, la monnaie ou la stabilité politique.
    - Si le scénario est totalement absurde, magique ou sans aucun lien logique avec le monde réel, renvoie un dictionnaire avec une erreur.

    TOLÉRANCE :
    - Accepte les scénarios prospectifs sérieux (fusion nucléaire, AGI, guerre, crise sanitaire, etc.).
{instruction_calibration}

    Format erreur :
    {{
        "erreur": "Ce scénario ne semble pas lié à l'économie ou à la géopolitique. Veuillez formuler un événement cohérent."
    }}

    Si le scénario est valide, fournis ta réponse UNIQUEMENT au format JSON valide :
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
        "evenement_reference": "Nom de l'événement historique utilisé pour calibrer (ex: 'Krach 2008'), ou null si pas de calibration."
    }}

    IMPORTANT :
    - "inflation" et "taux_directeurs" en pourcentage (ex: 2.5 pour +2.5%, -0.75 pour -0.75%).
    - Actifs en décimal (ex: -0.15 pour -15%, 0.08 pour +8%).
    - Respecte les corrélations économiques :
        * Hausse des taux → obligations baissent, actions baissent, VIX monte, Dollar_Index monte
        * Inflation forte → Or/Argent/Cuivre montent, obligations baissent
        * Crise géopolitique → VIX monte, ETF_Defense monte, Or monte, Emerging_Markets baissent
        * Dollar fort → Emerging_Markets baissent, Or baisse légèrement, EUR_USD baisse
        * Récession → Cuivre/Pétrole/S&P 500 baissent, obligations montent
        * Boom tech → NASDAQ monte plus que S&P 500, cryptos peuvent monter
        * Tensions géopolitiques → ETF_Terres_Rares et ETF_Defense montent
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
            "DXY, VIX, spread obligataire, corrélation inter-actifs, etc.) mais tu vulgarises tes conclusions "
            "pour que le client comprenne parfaitement la mécanique des marchés. "
            "Tu couvres toutes les classes d'actifs de Quant Terminal : actions (S&P 500, NASDAQ, CAC 40, "
            "MSCI World, Marchés Émergents), obligations (Bons du Trésor US, Bund, OAT, JGB, Gilt), "
            "matières premières (Or, Argent, Pétrole, Cuivre, Terres Rares), devises et volatilité (EUR/USD, "
            "Dollar Index, VIX), sectoriels (ETF Défense), et cryptomonnaies (Bitcoin, Ethereum, XRP, Solana). "
            "Tu connais bien les crises historiques (1929, 1987, 2000, 2008, 2020) et tu peux les utiliser "
            "comme références pour répondre aux questions."
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
