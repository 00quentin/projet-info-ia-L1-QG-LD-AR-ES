# Quant Terminal — V2.0

> Simulateur d'investissement pédagogique — testez l'impact d'un événement économique ou géopolitique sur un portefeuille, à partir des **vrais prix de marché** récupérés en direct via Yahoo Finance.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quant-terminal-l1.streamlit.app/)

### 👉 [Cliquer ici pour ouvrir l'application](https://quant-terminal-l1.streamlit.app/)

---

## Ce que fait Quant Terminal

Vous décrivez un scénario — *"krach boursier façon 2008"*, *"guerre majeure au Moyen-Orient"*, *"révolution IA et gains de productivité massifs"* — et le terminal estime son impact sur votre portefeuille.

Concrètement :

- **Prix réels** : récupération en direct via Yahoo Finance (S&P 500, NASDAQ, or, pétrole, Bitcoin, obligations, etc.) avec bande de cotations live en temps réel.
- **Analyse IA** : un modèle GPT-4o interprète votre scénario en s'inspirant des grandes crises historiques (1973, 2000, 2008, COVID 2020, hausse FED 2022…).
- **Moteur de simulation** : application des chocs estimés sur 100 jours de cotation, avec mode Monte-Carlo (50 trajectoires possibles).
- **Métriques institutionnelles** : Volatilité annualisée, Sharpe Ratio, Max Drawdown, VaR 95% — les indicateurs utilisés par les gérants de fonds.
- **Backtest historique** : rejouez les vraies données passées (2008, COVID, Brexit…) pour voir comment votre portefeuille s'en serait sorti.
- **Analyste IA intégré** : bulle de chat flottante (💬) accessible à tout moment pour poser vos questions financières sans quitter l'interface.

---

## Fonctionnalités principales

| Onglet | Ce que vous y faites |
|---|---|
| **Dashboard** | Analyse IA + métriques de risque + graphiques par classe d'actifs |
| **Portefeuille** | Répartition (camembert) et performance détaillée par actif |
| **Comparaison** | Confrontez jusqu'à 3 scénarios côte à côte sur le même portefeuille |
| **Backtest** | Rejouez une vraie crise historique sur votre portefeuille |
| **Historique** | Retrouvez vos anciennes simulations |
| **Académie** | Explications pédagogiques (volatilité, Sharpe, drawdown…) |
| **À propos** | Présentation du projet et de l'équipe |

**Analyste IA** : accessible via la bulle 💬 en bas à droite — chat libre avec un expert financier IA, questions exemples incluses, sans quitter la page.

Profils d'investisseur disponibles : *Prudent*, *Équilibré*, *Agressif*, *Personnalisé*.  
Vous pouvez aussi ajouter **n'importe quel ticker Yahoo** (TSLA, NVDA, BTC-USD…) à votre portefeuille.

---

## Nouveautés V2.0

- Interface entièrement redesignée (palette Linear/Vercel, mode sombre 🌙)
- Bande de marchés en direct avec sparklines et variations en temps réel
- Analyste IA en bulle flottante (plus ergonomique qu'un onglet dédié)
- Onglets pleine largeur, navigation améliorée
- Comparaison multi-scénarios jusqu'à 3 portefeuilles simultanés

---

## Lancer le projet en local

Prérequis : Python 3.10+ et une clé API OpenAI.

```bash
# 1. Cloner le repo
git clone https://github.com/00quentin/projet-info-ia-L1-QG-LD-AR-ES.git
cd projet-info-ia-L1-QG-LD-AR-ES

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé OpenAI (créer un fichier .env)
echo "OPENAI_API_KEY=sk-..." > .env

# 4. Lancer l'application
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur sur `http://localhost:8501`.

---

## Stack technique

- **Frontend** : [Streamlit](https://streamlit.io/) + CSS custom (design system Linear/Vercel)
- **Graphiques** : [Plotly](https://plotly.com/python/)
- **Données de marché** : [yfinance](https://github.com/ranaroussi/yfinance) (cache 1h + fallback snapshot)
- **IA** : OpenAI GPT-4o-mini (analyse macro + chat) — validation Pydantic v2
- **Export** : ReportLab (rapports PDF)
- **Déploiement** : Streamlit Community Cloud + GitHub Actions (keep-alive automatique)

---

## Équipe

Projet réalisé en L1 MIASHS à l'**Université Paris Nanterre** (2025-2026) :

- **Quentin Geldreich**
- **Lukha Doazan**
- **Evan Saadi**
- **Alex Ruimy**

---

## ⚠ Avertissement

Quant Terminal est un **outil pédagogique**. Les résultats produits **ne constituent pas un conseil en investissement**. L'IA estime des ordres de grandeur en s'inspirant de crises historiques — la réalité de marché peut fortement diverger.
