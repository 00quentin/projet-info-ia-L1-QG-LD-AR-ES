import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Chargement des variables d'environnement (clé API)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def analyser_evenement_macro(evenement_utilisateur):
    # Le prompt est enrichi pour gérer les textes absurdes ou hors-sujet
    prompt = f"""Tu es un analyste quantitatif institutionnel travaillant pour Quant Terminal. 
    Ton rôle est d'évaluer l'impact macro-économique du scénario suivant : "{evenement_utilisateur}".
    
    CRITÈRE DE VALIDATION :
   - L'événement doit avoir un impact plausible sur : la production, la consommation, la confiance des investisseurs, les ressources naturelles, la monnaie ou la stabilité politique.
   - Si le scénario est totalement absurde, magique ou sans aucun lien logique avec le monde réel (ex: "Il pleut des bonbons"), tu dois impérativement renvoyer un dictionnaire avec une erreur.
    TOLÉRANCE :
   - Accepte les scénarios prospectifs sérieux (ex: "Fusion nucléaire maîtrisée", "Guerre civile dans un pays producteur de pétrole", "IA remplaçant 50% des emplois").
    {{
        "erreur": "Ce scénario ne semble pas lié à l'économie ou à la géopolitique. Veuillez formuler un événement cohérent (ex: 'Hausse brutale des taux de la FED', 'Découverte d'une nouvelle énergie', etc.)."
    }}
    
    Si le scénario est valide, fournis ta réponse UNIQUEMENT au format JSON valide avec la structure suivante :
    {{
        "macro": {{"inflation": <VRAI CHIFFRE>, "taux_directeurs": <VRAI CHIFFRE>}},
        "actifs": {{"S&P 500": 0.0, "CAC 40": 0.0, "Bons_Tresor_US_10Y": 0.0, "Or": 0.0, "Petrole": 0.0, "EUR_USD": 0.0, "Bitcoin": 0.0, "Ethereum": 0.0}},
        "explication_courte": "Explication technique et précise d'une ligne."
    }}
    
    IMPORTANT POUR LES SCÉNARIOS VALIDES : 
    - Pour "inflation" et "taux_directeurs", tu DOIS estimer une vraie variation réaliste en pourcentage (ex: 2.5 pour +2.5%, -0.75 pour -0.75%). Ne laisse pas 0 si l'événement a un impact.
    - Pour les actifs, donne la variation en décimale (ex: -0.15 pour -15%, 0.08 pour +8%).
    """

    try:
        reponse = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={ "type": "json_object" }
        )
        return json.loads(reponse.choices[0].message.content)
    except Exception as e:
        # En cas d'erreur de connexion ou d'API, on renvoie la clé "erreur"
        # que notre fichier app.py (Streamlit) va intercepter pour afficher un beau message rouge.
        return {"erreur": f"Erreur de connexion aux serveurs de l'Intelligence Artificielle : {str(e)}"}

def discuter_avec_ia(historique_messages):
    # Amélioration du persona de l'IA pour correspondre au standing "Pro" de Quant Terminal
    messages = [{
        "role": "system", 
        "content": "Tu es un Analyste Financier Senior travaillant pour le terminal institutionnel 'Quant Terminal'. Tu as un ton professoral, extrêmement précis et professionnel. Tu utilises un vocabulaire financier expert (Bull market, hawkish, dovish, PnL, Flight to quality, etc.) mais tu prends toujours le temps de bien vulgariser tes conclusions pour que l'utilisateur (le client) comprenne parfaitement la mécanique des marchés."
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
        return f"❌ Erreur de communication avec le bureau de l'analyste : {str(e)}"