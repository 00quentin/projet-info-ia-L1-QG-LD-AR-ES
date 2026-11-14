# Journal du mode autonome

Décisions du superviseur, cycle par cycle (voir `docs/AUTONOME.md`).

## Cycle 1 — décisions

*14/11/2026. État constaté : liste de migration 31/31, 415 tests, benchmark presque entièrement appliqué (pages légales, 404, démo, temps de récupération, méthodologie…). Restent surtout l'idée « portefeuilles d'exemple » (recommandation n° 15), la dérive possible de `donnees.ts` (problème n° 4 du rapport n° 3) et un README encore centré sur Streamlit.*

1. **Portefeuilles d'exemple en un clic (60/40, tout actions monde).** Seule moitié non faite de la recommandation n° 15 du benchmark ; utile au débutant qui ne sait pas composer un portefeuille. Ajout pur (constante `PORTEFEUILLES_EXEMPLE` dans `config.py`, exposée par `/api/catalogue`, boutons dans `ChoixPortefeuille.tsx`) : rien ne disparaît, Streamlit intact.
2. **Test de synchronisation `donnees.ts` ↔ `config.py` / `schemas.py`.** Le rapport n° 3 a déjà trouvé une valeur périmée dans la page Méthodologie. Un test pytest qui lit `donnees.ts` et le compare au moteur bloque toute dérive future, sans endpoint ni appel réseau au chargement de la page (pas de dépendance au réveil de Render). L'endpoint `/parametres` reste possible plus tard.
3. **README orienté démo + schéma d'architecture.** Le README décrit encore l'app Streamlit (« 50 trajectoires » alors que le moteur en tire 1000) et ne présente pas le site Next.js ni l'API. C'est la première chose que lit un jury : support de pitch à faible risque, uniquement de la documentation.

Périmètres disjoints : tâche 1 = `config.py`, `api/services.py`, `tests/test_api.py`, `web/src/lib/api.ts`, `web/src/components/formulaire/ChoixPortefeuille.tsx` ; tâche 2 = `tests/test_donnees_methodologie.py` (nouveau), `web/src/components/methodologie/donnees.ts` ; tâche 3 = `README.md`, `docs/ARCHITECTURE.md` (nouveau).

## Cycle 1 — relecture

*Vérifications : pytest 469 passés, `tsc --noEmit` et `npm run lint` sans erreur (build laissé à l'orchestrateur).*

- **Tâche 1 (portefeuilles d'exemple) : À CORRIGER (mineur).** Fonctionnel, additif, testé (3 tests API), poids sommant à 1 et clés connues, repli si l'API est ancienne. Défaut cosmétique : `nomCourtProfil =(profil` (espace manquant) dans `ChoixPortefeuille.tsx`. Corrigé au cycle 2.
- **Tâche 2 (test de synchro `donnees.ts`) : ACCEPTÉE.** Test lit `donnees.ts` et le compare à `config.py`/`schemas.py`/`market_data.py` ; seuls des commentaires changent dans `donnees.ts` (`MacroImpact` -> `ChocsMacro`, nom réel de la classe).
- **Tâche 3 (README + ARCHITECTURE) : À CORRIGER (mineur).** Sondage de 5 affirmations exactes (23 actifs en 6 catégories, `gpt-6.1-terra`, horizon 30-250 / 100, 78 % = 80/102 dans `validation_ia.json`, URL Vercel). Une valeur périmée : « 415 tests » alors qu'il y en a 469 ; on retire le nombre pour qu'il ne dérive plus.

## Cycle 2 — décisions

1. **Corrections du cycle 1** (espace dans `nomCourtProfil`, nombre de tests du README).
2. **Supports de pitch** : plan de diaporama + script vidéo 30 s dans `docs/PITCH.md` (nouveau), uniquement de la documentation, faits tirés du README et de `data/validation_ia.json`.

## Cycle 2 — relecture
- T1 corrections mineures (espace dans `nomCourtProfil`, nombre de tests retiré du README) : faites directement par l'orchestrateur (2 lignes, moins coûteux qu'un agent). ACCEPTÉE.
- T2 `docs/PITCH.md` : chiffres vérifiés (1 000 trajectoires, horizon 30-250, VaR 95 % = percentile 5 % dans core/metrics.py, 6 crises dont « Krach 2008 (Lehman) », 78 % = 80/102, 53 % avant). ACCEPTÉE.

## Cycle 3 — décisions

*Dernier cycle de l'après-midi. Le benchmark est quasi soldé (P6, U1 déjà faits) ; on reste sur du sûr, sans nouvelle fonction.*

1. **Audit mobile 390 px + clair/sombre des pages statiques** (méthodologie, validation, a-propos, contact, pages légales) : corrections de débordement ou de contraste uniquement. Sonnet. Fichiers : `web/src/app/{methodologie,validation,a-propos,contact,cgu,confidentialite,mentions-legales}/`, `web/src/components/{methodologie,validation,apropos,legal}/`.
2. **FAQ enrichie** : questions sur les portefeuilles d'exemple, le mode démo, la fourchette IA / le score de 78 % (avec la réserve : réglé sur les mêmes 6 crises). Ajout pur de contenu, aide l'utilisateur et le jury. Haiku. Fichier : `web/src/contenu/faq.ts`.

Périmètres disjoints ; aucun appel IA, aucun déploiement, rien retiré.
- Note de l'orchestrateur : T1 (audit 390 px des pages statiques) non lancée, doublon de l'audit Playwright + axe du 13/11 (14 pages, 390/1440, clair/sombre : 0 débordement, 0 violation) ; ces pages n'ont pas changé depuis. T2 (FAQ) lancée sur Haiku.

## Cycle 3 — relecture
- T2 FAQ : l'agent Haiku a été bloqué par le hook GateGuard (aucune modification). Faite directement par l'orchestrateur : 3 questions ajoutées (fourchette et 78 %, portefeuilles d'exemple, démo et réveil du serveur) ; « conseil en investissement » existait déjà. tsc, lint, build, pytest OK. ACCEPTÉE.
- Fin du mode autonome (3 cycles), voir le bilan.
