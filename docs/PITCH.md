# Quant Terminal : supports de pitch

Outil pédagogique : les résultats ne constituent pas un conseil en investissement.

Sources : `README.md`, `docs/ARCHITECTURE.md`, `data/validation_ia.json`.

---

## 1. Plan du diaporama (7 diapos)

**Diapo 1 : Problème**
- Les outils existants rejouent le passé (backtest) ou prolongent une tendance (projection à rendement fixe).
- Question posée : « Et si ça arrivait demain ? » (`README.md`).

**Diapo 2 : Démo**
- Visuel : page d'accueil, bouton « Essayer avec un exemple ».
- Le résultat est un exemple pré-calculé (`web/public/exemple/simulation.json`) : il s'affiche même si le serveur dort.

**Diapo 3 : Méthode**
- IA (OpenAI) qui traduit un scénario en chocs par actif, inspirés de crises passées.
- Chaque réponse est validée par Pydantic avec des bornes par actif (`schemas.py`).
- 1 000 trajectoires Monte-Carlo sur un horizon de 30 à 250 séances.
- Métriques : volatilité, Sharpe, Max Drawdown, VaR 95 %.

**Diapo 4 : Validation sur 6 crises**
- Crises : COVID 2020, Lehman 2008, bulle internet, krach pétrolier 2014-2016, Russie-Ukraine 2022, Brexit.
- Résultat : le vrai mouvement tombe dans la fourchette de l'IA dans 78 % des cas (80 actifs sur 102).
- Avant recalage : 53 % (chiffre cité dans `README.md`, non recalculé ici).

**Diapo 5 : Architecture**
- Site Next.js (Vercel) → API FastAPI (Render) → moteur Python commun.
- Application Streamlit (Streamlit Community Cloud) qui appelle le moteur directement.
- Sources : Yahoo Finance (cours), OpenAI (analyse).

**Diapo 6 : Limites honnêtes**
- Le score de 78 % est un peu flatteur : le recalage de la fourchette a été choisi sur les mêmes six crises.
- L'IA estime des ordres de grandeur ; la réalité de marché peut fortement diverger.
- Pas de conseil en investissement.

**Diapo 7 : Suite**
- Tester le recalage sur des crises non utilisées pour le choisir (validation hors échantillon). Proposition, pas encore dans le dépôt.

---

## 2. Script vidéo (30 s, environ 70 mots)

| Temps | À l'écran | Texte à dire |
|---|---|---|
| 0 à 8 s | Page d'accueil, titre et sous-titre | « Et si ça arrivait demain ? Décrivez un événement économique : Quant Terminal estime son impact sur votre portefeuille. » |
| 8 à 14 s | Clic sur « Essayer avec un exemple », résultat qui s'affiche | « Le résultat s'affiche tout de suite, à partir des vrais cours Yahoo Finance. » |
| 14 à 21 s | Métriques de risque (volatilité, Sharpe, VaR) | « Une IA bornée, calée sur des crises passées, et mille trajectoires Monte-Carlo mesurent le risque. » |
| 21 à 30 s | Page de validation sur les six crises | « Sur six crises passées, le vrai mouvement tombe dans la fourchette 78 % du temps : un score un peu flatteur. Outil pédagogique, pas un conseil en investissement. » |

Durée totale : 30 s.
