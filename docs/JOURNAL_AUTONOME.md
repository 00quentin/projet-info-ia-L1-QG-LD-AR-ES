# Journal du mode autonome

Décisions du superviseur, cycle par cycle (voir `docs/AUTONOME.md`).

## Cycle 1 — décisions

*14/11/2026. État constaté : liste de migration 31/31, 415 tests, benchmark presque entièrement appliqué (pages légales, 404, démo, temps de récupération, méthodologie…). Restent surtout l'idée « portefeuilles d'exemple » (recommandation n° 15), la dérive possible de `donnees.ts` (problème n° 4 du rapport n° 3) et un README encore centré sur Streamlit.*

1. **Portefeuilles d'exemple en un clic (60/40, tout actions monde).** Seule moitié non faite de la recommandation n° 15 du benchmark ; utile au débutant qui ne sait pas composer un portefeuille. Ajout pur (constante `PORTEFEUILLES_EXEMPLE` dans `config.py`, exposée par `/api/catalogue`, boutons dans `ChoixPortefeuille.tsx`) : rien ne disparaît, Streamlit intact.
2. **Test de synchronisation `donnees.ts` ↔ `config.py` / `schemas.py`.** Le rapport n° 3 a déjà trouvé une valeur périmée dans la page Méthodologie. Un test pytest qui lit `donnees.ts` et le compare au moteur bloque toute dérive future, sans endpoint ni appel réseau au chargement de la page (pas de dépendance au réveil de Render). L'endpoint `/parametres` reste possible plus tard.
3. **README orienté démo + schéma d'architecture.** Le README décrit encore l'app Streamlit (« 50 trajectoires » alors que le moteur en tire 1000) et ne présente pas le site Next.js ni l'API. C'est la première chose que lit un jury : support de pitch à faible risque, uniquement de la documentation.

Périmètres disjoints : tâche 1 = `config.py`, `api/services.py`, `tests/test_api.py`, `web/src/lib/api.ts`, `web/src/components/formulaire/ChoixPortefeuille.tsx` ; tâche 2 = `tests/test_donnees_methodologie.py` (nouveau), `web/src/components/methodologie/donnees.ts` ; tâche 3 = `README.md`, `docs/ARCHITECTURE.md` (nouveau).
