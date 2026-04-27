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
        "explication_courte": "Analyse détaillée et précise en 3-4 phrases minimum.",
        "evenement_reference": "Nom de l'événement historique utilisé, ou null."
    }}

    *** RÈGLES STRICTES SUR LES AMPLITUDES (CRUCIAL) ***
    
    HORIZON : 100 jours de cotation (~5 mois). Les chocs doivent être proportionnés à cette durée.
    
    PLAFONDS ABSOLUS - À RESPECTER IMPÉRATIVEMENT (sauf scénario apocalyptique extrême) :
    - Actions (S&P 500, NASDAQ, CAC 40, MSCI World, Emerging) : entre -50% et +40%
    - Obligations 10Y : entre -25% et +20%
    - EUR/USD, Dollar_Index : entre -15% et +15%
    - VIX : entre -50% et +200% (le VIX peut beaucoup bouger mais rarement +500%)
    - Or : entre -20% et +50% (en 5 mois, +50% c'est ÉNORME)
    - Argent : entre -25% et +60%
    - Pétrole : entre -60% et +80%
    - Cuivre : entre -30% et +40%
    - Terres Rares : entre -30% et +60%
    - ETF Défense : entre -25% et +40%
    - Cryptos (BTC, ETH, XRP, SOL) : entre -75% et +200% (très volatiles mais pas illimités)
    
    INTERDICTIONS FORMELLES :
    - JAMAIS de chocs supérieurs à +500% pour quel que soit l'actif (l'or NE PEUT PAS faire +3000%)
    - JAMAIS -100% (faillite totale - c'est inatteignable même en krach)
    - Une "impression massive de monnaie" → Or maximum +30 à +50%, PAS +3000%
    - Une crise inflation → cryptos peuvent chuter mais pas -100%, max -75%
    
    PLAUSIBILITÉ :
    - Inflation : entre -2% et +20% (au-delà = hyper-inflation, scénario extrême uniquement)
    - Taux directeurs : entre -2% et +5%
    
    *** CALIBRER L'AMPLITUDE SUR LA SÉVÉRITÉ DU SCÉNARIO ***
    - Scénario léger (annonce, ajustement) : variations de 1-5%
    - Scénario moyen (récession, conflit régional) : variations de 5-20%
    - Scénario fort (crise majeure type 2008) : variations de 20-50%
    - Scénario extrême (apocalyptique) : variations max selon plafonds ci-dessus
    
    *** CORRÉLATIONS À RESPECTER ***
    - Hausse taux → obligations baissent, actions baissent, VIX monte, Dollar_Index monte
    - Inflation forte → Or/Argent/Cuivre montent (modérément), obligations baissent
    - Crise géopolitique → VIX monte, Défense monte, Or monte, Émergents baissent
    - Récession → Cuivre/Pétrole/S&P 500 baissent, obligations montent
    - Boom tech → NASDAQ monte plus que S&P 500, cryptos peuvent monter
    - "Impression de monnaie" massive (helicopter money) : USD baisse, Or monte modérément
      (+15 à +35%), actions montent (effet inflation des actifs), cryptos montent modérément (+30 à +80%),
      MAIS PAS d'effondrement crypto (cryptos sont vues comme un hedge anti-monnaie fiat)
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