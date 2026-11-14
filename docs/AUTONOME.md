# Mode autonome — charte du superviseur

Quentin est absent. Le **superviseur** décide seul de ce qu'il faut faire, confie le travail à des
agents, relit leur rendu et décide de le garder ou non. L'orchestrateur (session principale) exécute
fidèlement ses décisions : il lance les agents, fusionne ce qui est accepté, pousse la branche.

## Garde-fous (non négociables)
1. **Branche unique** : tout se fait sur `claude/site-analysis-redesign-k1pqb4`. Aucune poussée sur
   `developpement` ni `main`, aucun déploiement (Render, Vercel, Streamlit Cloud).
2. **Non-régression** (`CLAUDE.md`) : aucune fonction, page, métrique, graphique ou option ne disparaît.
   Couper Streamlit est **interdit** (décision réservée à Quentin).
3. **Pas d'appel à l'IA** (OpenAI) : la clé locale est invalide et les appels coûtent. Pas de nouvelle
   dépendance npm/pip sans l'ajouter au fichier de dépendances et sans vraie nécessité.
4. **Aucun secret** dans le code, les docs ou les messages.
5. **Qualité avant fusion** : `pytest` (racine), `npx tsc --noEmit`, `npm run lint`, `npm run build`
   (dans `web/`) doivent passer. Pour l'UI : pas de débordement à 390 px, clair et sombre lisibles.
6. **Fichiers disjoints** : deux agents d'un même cycle ne touchent jamais les mêmes fichiers.
7. **Petits pas** : 1 à 3 tâches par cycle, chacune livrable en moins d'une heure par un agent.
8. **Conventions** : code et commentaires en français, constantes dans `config.py`, `core/` sans
   `streamlit`, réponses IA validées par `schemas.py`.

## Boucle
1. **Décider** : le superviseur lit `CLAUDE.md`, `docs/RAPPORT_AVANCEMENT.md`, `docs/BENCHMARK.md`,
   ce fichier et `docs/JOURNAL_AUTONOME.md`, inspecte le code, puis choisit les prochaines tâches
   (valeur pour l'utilisateur du site d'abord, pitch hackathon ensuite).
2. **Exécuter** : un agent par tâche, dans un worktree isolé.
3. **Relire** : le superviseur lit chaque diff, relance les vérifications, et décide :
   *accepter*, *refuser* (avec raison) ou *corriger* (nouvelle tâche au cycle suivant).
4. **Consigner** : chaque décision va dans `docs/JOURNAL_AUTONOME.md` (date, tâche, verdict, raison).

## Idées en réserve (le superviseur peut en choisir d'autres)
- Portefeuilles d'exemple en un clic (60/40, tout actions monde) dans le formulaire.
- Endpoint API des paramètres du moteur pour que `donnees.ts` ne recopie plus `config.py` à la main.
- Supports de pitch : README orienté démo, schéma d'architecture, plan de diaporama, script vidéo 30 s.
- Finitions issues du benchmark (`docs/BENCHMARK.md`) et des « Prochaines étapes » du rapport n° 3.
- Tests manquants sur les nouvelles fonctions (`elargir_fourchette`, script de validation).
