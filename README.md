# Quant Terminal

> **Et si ça arrivait demain ?** Décrivez un événement économique en français : Quant Terminal estime son impact sur *votre* portefeuille, à partir des vrais cours de marché (Yahoo Finance), d'une IA bornée et ancrée sur les grandes crises passées, et de 1 000 trajectoires Monte-Carlo.

Les autres outils rejouent le passé (backtest) ou prolongent une tendance (projection à rendement fixe). Quant Terminal répond à la question « et si… ? ».

## Essayer la démo

- **Site** : [https://quant-terminal-qg-team.vercel.app](https://quant-terminal-qg-team.vercel.app)
- Sur l'accueil, cliquez sur **« Essayer avec un exemple »** : le résultat s'affiche tout de suite, même si le serveur dort.
  C'est un **exemple pré-calculé** (une vraie simulation enregistrée à l'avance, `web/public/exemple/simulation.json`) ; le bouton « Relancer en direct » refait la même demande avec les cours du jour.
- **Application Streamlit** (première version, toujours en ligne) : [https://quant-terminal-l1.streamlit.app/](https://quant-terminal-l1.streamlit.app/)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://quant-terminal-l1.streamlit.app/)

## Points forts

- **Une IA testée sur l'histoire.** Sur 6 crises passées (COVID 2020, Lehman 2008, bulle internet, krach pétrolier 2014-2016, Russie-Ukraine 2022, Brexit), le vrai mouvement tombe dans la fourchette de l'IA **78 % du temps (80 actifs sur 102)**, contre 53 % avant recalage. Ce score est **un peu flatteur** : le recalage de la fourchette a été choisi sur ces mêmes crises. Résultats détaillés sur la page `/validation` (données : `data/validation_ia.json`, script : `scripts/valider_ia_historique.py`).
- **Une méthode expliquée.** La page `/methodologie` détaille le moteur ; chaque réponse de l'IA est validée par Pydantic avec des bornes par actif (`schemas.py`) avant d'être simulée.
- **Apprendre en manipulant.** Une Académie (volatilité, Sharpe, drawdown, VaR…) et un backtest qui rejoue une vraie crise sur votre portefeuille.
- **Un analyste IA intégré**, en bulle de chat, qui annonce clairement être une IA (OpenAI) et rappelle que ce n'est pas un conseil en investissement.
- **Des résultats réutilisables** : export CSV, rapport PDF et lien de partage.

---

## Ce que fait Quant Terminal

Vous décrivez un scénario (*« krach boursier façon 2008 »*, *« guerre majeure au Moyen-Orient »*, *« révolution IA et gains de productivité massifs »*) et le terminal estime son impact sur votre portefeuille.

- **Prix réels** : récupérés via Yahoo Finance (S&P 500, NASDAQ, or, pétrole, Bitcoin, obligations, etc.), avec cache d'une heure et instantané de secours si Yahoo ne répond pas. Catalogue de 23 actifs en 6 catégories (`config.py`), plus n'importe quel ticker Yahoo (TSLA, NVDA, BTC-USD…).
- **Analyse IA** : un modèle OpenAI (`gpt-6.1-terra`, réglé dans `config.py`) traduit le scénario en chocs par actif, en s'inspirant des grandes crises historiques (1973, 2000, 2008, COVID 2020, hausse de la FED 2022…).
- **Moteur de simulation** : chocs appliqués sur un horizon de 30 à 250 jours de cotation (100 par défaut), avec 1 000 trajectoires Monte-Carlo et trois modèles d'aléa : Probabiliste, Historique, Machine Learning.
- **Métriques de risque** : volatilité annualisée, ratio de Sharpe, Max Drawdown, VaR 95 %.
- **Comparaison** : jusqu'à 3 scénarios côte à côte sur le même portefeuille.
- **Backtest historique** : rejouez les vraies données passées (2008, COVID, Brexit…).

---

## Lancer en local

Prérequis : Python 3.10+, Node.js (pour le site) et une clé API OpenAI dans un fichier `.env` à la racine :

```bash
git clone https://github.com/00quentin/projet-info-ia-L1-QG-LD-AR-ES.git
cd projet-info-ia-L1-QG-LD-AR-ES
echo "OPENAI_API_KEY=sk-..." > .env
```

### 1. Application Streamlit

```bash
pip install -r requirements.txt
streamlit run app.py          # http://localhost:8501
```

### 2. API FastAPI (moteur pour le site)

```bash
pip install -r requirements-dev.txt     # requirements.txt + FastAPI, uvicorn, pytest, httpx
uvicorn api.main:app --reload --port 8000
```

Documentation interactive : `http://localhost:8000/docs`. Principales routes : `/api/catalogue`, `/api/marches`, `/api/simulations`, `/api/backtests`, `/api/chat`, `/api/rapports/pdf`, `/api/couverture`, `/api/validation-ia`, `/api/sante`.

### 3. Site Next.js

Dans un second terminal, l'API étant lancée :

```bash
cd web
npm install
npm run dev                   # http://localhost:3000
```

L'adresse de l'API se règle avec la variable `NEXT_PUBLIC_API_URL` (par défaut `http://localhost:8000`).

### Tests et vérifications

```bash
pytest                        # 415 tests Python (moteur, core/, API)

cd web
npx tsc --noEmit              # types TypeScript
npm run lint                  # ESLint
npm run build                 # build de production
```

Ces vérifications tournent aussi sur GitHub Actions (`.github/workflows/verifications.yml`).

---

## Déploiement

| Partie | Hébergeur | Configuration |
|---|---|---|
| Site Next.js (`web/`) | Vercel | dossier racine `web`, variable `NEXT_PUBLIC_API_URL` = adresse de l'API |
| API FastAPI (`api/`) | Render (offre gratuite) | `render.yaml` : `pip install -r api/requirements.txt` puis `uvicorn api.main:app --host 0.0.0.0 --port $PORT` ; clés `OPENAI_API_KEY` et `QT_ORIGINES_AUTORISEES` saisies dans le tableau de bord Render |
| Application Streamlit | Streamlit Community Cloud | `requirements.txt` |

Deux tâches GitHub Actions gardent les services éveillés : `reveil_api.yml` (appel de `/api/sante` toutes les 10 minutes, car Render endort l'API après 15 minutes) et `keep_alive.yml` (Streamlit).

Architecture détaillée et chemin d'une simulation : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Onglets de l'application Streamlit

| Onglet | Ce que vous y faites |
|---|---|
| **Dashboard** | Analyse IA + métriques de risque + graphiques par classe d'actifs |
| **Portefeuille** | Répartition (camembert) et performance détaillée par actif |
| **Comparaison** | Confrontez jusqu'à 3 scénarios côte à côte sur le même portefeuille |
| **Backtest** | Rejouez une vraie crise historique sur votre portefeuille |
| **Historique** | Retrouvez vos anciennes simulations |
| **Académie** | Explications pédagogiques (volatilité, Sharpe, drawdown…) |
| **À propos** | Présentation du projet et de l'équipe |

**Analyste IA** : accessible via la bulle de chat en bas à droite, chat libre avec un expert financier IA, questions exemples incluses, sans quitter la page.

Profils d'investisseur disponibles : *Prudent*, *Équilibré*, *Agressif*, *Personnalisé*.

### Nouveautés V2.0 (Streamlit)

- Interface entièrement redesignée (palette Linear/Vercel, mode sombre)
- Bande de marchés en direct avec sparklines et variations en temps réel
- Analyste IA en bulle flottante (plus ergonomique qu'un onglet dédié)
- Onglets pleine largeur, navigation améliorée
- Comparaison multi-scénarios jusqu'à 3 portefeuilles simultanés

---

## Stack technique

- **Site** : [Next.js](https://nextjs.org/) 16 + React 19 + Tailwind CSS 4 + Motion, graphiques d3 (`web/package.json`)
- **API** : [FastAPI](https://fastapi.tiangolo.com/) + uvicorn
- **Application historique** : [Streamlit](https://streamlit.io/) + CSS custom (design system Linear/Vercel), graphiques [Plotly](https://plotly.com/python/)
- **Données de marché** : [yfinance](https://github.com/ranaroussi/yfinance) (cache 1 h + instantané de secours)
- **IA** : OpenAI `gpt-6.1-terra` (analyse macro) et `gpt-5.4-mini` (secours, chat, rapport), validation Pydantic v2
- **Export** : ReportLab (rapports PDF), CSV
- **Déploiement** : Vercel (site), Render (API), Streamlit Community Cloud, GitHub Actions (vérifications et réveil automatique)

---

## Équipe

Projet réalisé en L1 MIASHS à l'**Université Paris Nanterre** (2025-2026) :

- **Quentin Geldreich**
- **Lukha Doazan**
- **Evan Saadi**
- **Alex Ruimy**

---

## Avertissement

Quant Terminal est un **outil pédagogique**. Les résultats produits **ne constituent pas un conseil en investissement**. L'IA estime des ordres de grandeur en s'inspirant de crises historiques : la réalité de marché peut fortement diverger.
