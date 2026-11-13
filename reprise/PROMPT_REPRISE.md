# Prompt de reprise (à coller dans une nouvelle session)

Projet « Quant Terminal » (dépôt `00quentin/projet-info-ia-L1-QG-LD-AR-ES`). Travaille sur la branche `claude/site-analysis-redesign-k1pqb4` (pars de son dernier commit) et pousse uniquement dessus. Lis d'abord `CLAUDE.md`, `docs/BENCHMARK.md` (veille design/concurrents) et ce fichier. Utilise aussi le plugin que je viens d'installer partout où il aide : vérifie d'abord qu'il est bien chargé et dis-moi en une ligne ce qu'il apporte. Confie les grosses tâches à des agents en worktrees isolés (fichiers disjoints), relis leur travail, puis fusionne.

## Contexte
Refonte « hackathon / commercialisable » du site Next.js (`web/`) + API FastAPI (`api/`).
- Site en ligne : https://quant-terminal-qg-team.vercel.app (Vercel, projet `prj_xVwyT1yWQBc5tIQxqhSsT5YA7c0o`, team `team_fJMrGR6dsua8UnkGUkeWEiS9`, repoId `1219913212`). La branche de production Vercel est encore `main` : après fusion dans `developpement`, déclencher la production via `POST /v13/deployments` avec `gitSource.ref = developpement`.
- API : https://quant-terminal-api-baxq.onrender.com (Render, service `srv-dbqg4rei0phs73citd8g`, suit `developpement`, déploiement auto).
- Clés OpenAI / Render / Vercel injectées par le proxy (`Authorization: Bearer proxy-injected`, `OPENAI_API_KEY=proxy-injected`). Si une clé manque : `request_credential`, jamais dans le chat.

## Déjà fait sur la branche (rien à refaire)
Fondations visuelles (échelle typo, rayons, motion sobre, noms courts des actifs), moteur fiabilisé (profil de crise, fourchette bas/central/haut de l'IA, plafond IA journalier, CI + réveil de l'API), « Protéger mon portefeuille » branché dans les résultats, pages légales / CGU / confidentialité / FAQ / contact / 404 / SEO, page `/validation` (l'IA face à 6 crises passées), page `/methodologie`, refonte du formulaire, du sélecteur d'actifs, de l'accueil (démo en un clic, écran de réveil du serveur), des résultats, du backtest, de l'historique et du chat (mention IA). 410 tests pytest OK, tsc/eslint/build OK.

## À faire
1. **Fourchette de l'IA trop étroite** (constat de `/validation` : le vrai mouvement n'y tombe que dans 53 % des cas, l'IA sous-estime l'ampleur d'environ 40 %). Élargir la fourchette dans le prompt de `ia_bot.py` (nouvelle `PROMPT_VERSION`), éventuellement recaler les bornes avec les crises passées, puis relancer `scripts/valider_ia_historique.py` (≤ 14 appels IA) pour viser ~80 % de couverture, régénérer `data/validation_ia.json`, tests. Objectif : de meilleures simulations, puisque chaque trajectoire Monte-Carlo pioche son choc dans cette fourchette.
2. **Afficher la fourchette de l'IA** (`analyse.fourchettes`) dans le bloc Analyse de l'IA des résultats (et dans le tableau des chocs), et dans Streamlit (`views/dashboard.py`) si simple.
3. Mettre à jour les textes de l'Académie et `components/methodologie/donnees.ts` (profil de crise, fourchette ; `donnees.ts` recopie des valeurs de `config.py`/`schemas.py` : vérifier qu'elles sont à jour ou les exposer via l'API).
4. Petit jeton `--on-accent` dans `globals.css` pour remplacer les `text-white` sur `bg-accent`.
5. Audit Playwright de toutes les pages (desktop 1440 et mobile 390, clair et sombre) : aucun débordement, aucune erreur console ; corriger ce qui n'est pas propre. Audit d'accessibilité axe-core.
6. Agent `superviseur` : rapport d'avancement n° 3 (`docs/RAPPORT_AVANCEMENT.md`).
7. Supprimer le dossier `reprise/`, créer la PR vers `developpement`, la fusionner, vérifier le déploiement Render (`/api/sante`, `/api/validation-ia`, `/api/couverture`), déclencher la production Vercel, tester le site en ligne.
8. À me proposer ensuite (sans le lancer) : « Simuler l'actualité du jour », couper Streamlit (non-régression : demander d'abord), supports de pitch (README, schéma, diaporama, vidéo 30 s), portefeuilles d'exemple (60/40, tout actions monde).

Travaille en autonomie au moins 30 minutes, relis-toi, réponses courtes en français (je suis débutant). Ne retire aucune fonction (non-régression, CLAUDE.md).
