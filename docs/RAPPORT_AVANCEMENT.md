# Rapport d'avancement : migration Streamlit → site web

*Rapport n° 3, 13/11/2026, branche `claude/site-analysis-redesign-k1pqb4` (dernier commit `ef135a3`), vérifications en local*

## En une phrase
La liste de contrôle est **complète (31/31)** et la branche est en bonne santé (415 tests, 0 erreur TypeScript/ESLint, 0 violation d'accessibilité). La fourchette de l'IA est désormais **recalée sur les crises passées** : elle contient le vrai mouvement 78 % du temps, contre 53 % avant. Deux limites : la **clé OpenAI locale est refusée**, donc le nouveau prompt v9 n'a pas pu être validé, et cette branche **n'est pas encore fusionnée ni déployée**.

## Avancement (lignes ✅ dans `docs/MIGRATION.md`)
| Section | ✅ | Total | % |
|---|---|---|---|
| Simulation prospective | 17 | 17 | 100 % |
| Backtest historique | 4 | 4 | 100 % |
| Autres onglets et éléments | 6 | 6 | 100 % |
| Reste à faire avant de couper Streamlit | 4 | 4 | 100 % |
| **Total** | **31** | **31** | **100 %** (97 % au rapport n° 2) |

Changements faits dans `docs/MIGRATION.md` : aucun état modifié, seulement la date de vérification. La ligne « Photos de l'Académie » était déjà passée à ✅ (vérifiée en ligne le 13/11 sur téléphone, commit `23998bf`).

## Santé technique

| Vérification | Résultat |
|---|---|
| `pytest` (racine) | ✅ **415 tests réussis**, 0 échec (18,7 s) ; 273 au rapport n° 2 |
| Moteur sans Streamlit (`market_data`, `ia_bot`, `api.main`) | ✅ affiche `False` |
| TypeScript (`npx tsc --noEmit`) | ✅ 0 erreur |
| ESLint (`npx eslint src`) | ✅ 0 erreur, 0 avertissement |
| Build Next.js (`npm run build`) | ✅ vérifié juste avant le commit `ef135a3`. Pas relancé ici, pour ne pas perturber le serveur local qui sert ce build |
| Audit Playwright + axe-core : 14 pages × 2 tailles (1440×900 et 390×844) × 2 thèmes (clair et sombre) = 56 combinaisons | ✅ 0 débordement horizontal ; 0 erreur console (hors 404 attendu) ; **0 violation axe WCAG 2.1 AA** après corrections |

Les 14 pages auditées sont : `/`, `/academie`, `/backtest`, `/historique`, `/validation`, `/methodologie`, `/a-propos`, `/faq`, `/contact`, `/cgu`, `/confidentialite`, `/mentions-legales`, la page 404 et les résultats de la démo. Cet audit a été fait juste avant ce rapport (je ne l'ai pas refait). Aucun appel IA dans ce rapport.

## Ce qui a changé depuis le dernier rapport
35 commits depuis `5163880` (149 fichiers). Les plus importants :

- **Corrections du rapport n° 2** : formules du chat affichées avec KaTeX (`897c1b9`), date en double dans le nom du CSV du backtest corrigée (`a8fea58`, vérifié dans `web/src/components/backtest/outils.ts`), message d'attente pendant le réveil de Render (`ReveilServeur`, `55c933c`), noms courts des actifs (`1ff6ddc`).
- **Nouvelles pages et fonctions** : Protéger mon portefeuille, page `/validation` (l'IA testée sur 6 crises passées), page `/methodologie`, pages légales, FAQ, contact, 404 et SEO. Le formulaire, l'accueil (démo en un clic), les résultats, le backtest, l'historique et le chat ont été refaits avec un style plus sobre.
- **Fourchette de l'IA recalée sur les crises passées** (`ee62207`, `249b808`) : constantes `FOURCHETTE_*` dans `config.py` et fonction `schemas.elargir_fourchette`.
  - Le vrai mouvement tombe dans la fourchette **78 % du temps (80 actifs sur 102)**, contre 53 % avant. La fourchette est plus large : **39 points en moyenne**, contre 24.
  - ⚠ Le recalage a été choisi sur ces mêmes 6 crises. Le score est donc un peu flatteur : il faudra le confirmer sur des crises que le recalage n'a pas vues.
  - Une nouvelle version du prompt (v9, qui demande une fourchette plus large) est prête mais **n'a pas pu être validée** : la clé OpenAI locale est refusée (erreur 401). Le prompt v8 reste en service (`PROMPT_VERSION = "v8-fourchette-2026-11"` dans `ia_bot.py`).
- **Fourchette affichée** (`f24a299`) : sur le site, dans le bloc « Chocs estimés par actif » des résultats, et dans Streamlit, dans un menu dépliant. L'exemple de la démo n'a pas encore de fourchette : il sera régénéré.
- **Textes et style** (`62a591e`, `249b808`) : nouveau jeton CSS `--on-accent` ; l'Académie et la Méthodologie expliquent le profil de crise, la fourchette et son recalage. `web/src/components/methodologie/donnees.ts` a été comparé au code Python : 1 valeur périmée corrigée.
- **Accessibilité** (`ef135a3`) : meilleur contraste des gains, des pertes et des numéros de section ; un nom accessible pour chaque graphique ; les tableaux qui défilent sont atteignables au clavier.

## Problèmes trouvés (du plus grave au moins grave)
1. **Clé OpenAI locale invalide** (erreur 401, fichier `.env`). Elle bloque la validation du prompt v9 et tout test IA en local. Il faut la remplacer, puis relancer `scripts/valider_ia_historique.py`.
2. **Branche ni fusionnée ni déployée.** Le site en ligne (Vercel) et l'API (Render) n'ont pas encore la fourchette recalée, les nouvelles pages ni les corrections d'accessibilité. Après la fusion dans `developpement` et `main`, il faudra refaire un tour rapide en ligne.
3. **Le score de 78 % est un peu flatteur** : le recalage a été réglé sur les 6 crises qui servent aussi à le mesurer (voir `data/validation_ia.json`). Il faut le dire clairement sur `/validation` (c'est déjà expliqué dans la Méthodologie) et le tester sur d'autres crises.
4. **`web/src/components/methodologie/donnees.ts` recopie à la main des constantes de `config.py`.** Une valeur était déjà périmée. Recommandation : un endpoint de paramètres dans l'API (par exemple `/parametres`), que la page Méthodologie lirait.
5. **Mineur** : l'exemple de la démo (`web/src/lib/exemple.ts`) n'a pas de fourchette. Il faudra le régénérer quand l'IA sera de nouveau disponible.

## Prochaines étapes recommandées
1. **Remplacer la clé OpenAI locale**, valider le prompt v9 avec `scripts/valider_ia_historique.py`, puis régénérer l'exemple de la démo.
2. **Fusionner et déployer la branche** (`developpement` puis `main`), puis vérifier en ligne : simulation, backtest, `/validation` et `/methodologie`.
3. **Créer un endpoint de paramètres** pour que `donnees.ts` ne recopie plus `config.py` à la main.
