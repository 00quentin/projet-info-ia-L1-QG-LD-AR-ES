# Coupure de Streamlit : checklist

**Décision réservée à Quentin.** Ce document prépare la coupure, il ne la déclenche pas. Rien n'est supprimé ni désactivé à ce stade : le bandeau de migration ajoute seulement une invitation vers le nouveau site.

Référence de parité : `docs/MIGRATION.md` (dernière vérification 13/11/2026).
Nouveau site : https://quant-terminal-qg-team.vercel.app
API (Render) : https://quant-terminal-api-baxq.onrender.com

---

## 1. État d'après docs/MIGRATION.md

Toutes les lignes de la liste de contrôle sont à ✅ (fonctions de simulation prospective, backtest, historique, académie, à propos, analyste IA, bandeau des marchés, guide, thème, pied de page, notifications).

Section « Reste à faire avant de couper Streamlit » :

| Tâche | État |
|---|---|
| Déployer l'API sur Render (`render.yaml`, clé OpenAI) | ✅ en ligne (vérifié le 12/11) |
| Déployer le site sur Vercel (`NEXT_PUBLIC_API_URL`) | ✅ en ligne (vérifié le 12/11) |
| Vérifier les photos de l'Académie (Wikimedia) en ligne | ✅ vérifiées le 13/11 |
| Faire relire 3.3 de l'Académie (courbe des taux) | ✅ corrigé (`41e1b3d`) |

Il reste donc les étapes de coupure elles-mêmes (section 3). La règle de MIGRATION.md s'applique : on ne coupe que si toutes les lignes sont ✅ et si le site est en ligne.

## 2. Prérequis

- [ ] Relire docs/MIGRATION.md : toutes les lignes sont encore ✅ à la date de coupure.
- [ ] Refaire le parcours complet sur le site en ligne (simulation, comparaison, backtest, chat, PDF, CSV, historique).
- [ ] Vérifier où est stocké l'historique utilisateur : côté Streamlit (`core/history_store.py`, JSON sur disque du serveur) ou côté navigateur sur le nouveau site. Si l'historique n'est pas repris, le dire aux utilisateurs avant la coupure.
- [ ] Vérifier que l'API Render a bien sa clé `OPENAI_API_KEY` en variable d'environnement. Note : `ia_bot._cle_api()` lit d'abord la variable d'environnement, puis les secrets Streamlit. La coupure ne change donc pas l'API.

## 3. Étapes, dans l'ordre

1. **Vérifier la parité.** Refaire la checklist de MIGRATION.md sur le site en ligne. Toute régression bloque la suite.
2. **Geler Streamlit.** Plus aucune nouvelle fonction dans `app.py`, `views/`, `components/`, `handlers.py`. Seules les corrections d'urgence sont acceptées.
3. **Message de fin dans l'app.** Remplacer le bandeau `components/bandeau_migration.py` par un message de fin qui pointe vers le nouveau site (texte à rédiger avec Quentin). Streamlit ne sait pas faire une redirection HTTP propre : le message sert de page d'adieu.
4. **Liens.** Mettre à jour les liens vers l'app Streamlit dans `README.md` et `docs/PITCH.md` (chercher `streamlit.app` avec `grep`), pour pointer vers le nouveau site.
5. **Arrêt de l'app sur Streamlit Cloud.** Action manuelle de Quentin dans le tableau de bord Streamlit Cloud (mettre en veille ou arrêter l'app). Ne pas supprimer l'app Cloud avant que le retour arrière ne soit exclu (voir section 5).
6. **Archivage, pas suppression.** Déplacer dans un dossier `archive/` (ou marquer par un tag git) : `app.py`, `handlers.py`, `views/`, `components/` (aucun module de `components/` n'est importé par l'API), `style.css`, `.streamlit/`, et les tests qui ne testent que ces modules. Retirer `streamlit` et `plotly` de `requirements.txt` seulement après cet archivage. `api/requirements.txt` n'a déjà ni l'un ni l'autre.

## 4. Modules à NE PAS supprimer

L'API (`api/`) importe ces modules, directement ou par chaîne d'imports (vérifié par `grep` sur `api/` et sur les imports de chaque module) :

- `api/` (tout le dossier)
- `config.py`, `logger.py`, `schemas.py`, `market_data.py`, `simulation.py`, `pdf_generator.py`
- `ia_bot.py` : importe `streamlit` seulement dans `_cle_api()`, à l'intérieur d'un `try/except`. Ça marche sans Streamlit installé, mais garder ce point en tête si on modifie `ia_bot.py`.
- `core/cache.py`, `core/conjoncture.py`, `core/couverture.py`, `core/custom_assets.py`, `core/devises.py`, `core/metrics.py`, `core/portfolio.py`, `core/risk_alerts.py`, `core/runner.py`, `core/validation.py`

Vérifié : aucun module de `core/` n'importe `streamlit`. Il ne faut pas l'introduire pendant la coupure.

Non vérifiés, à contrôler avant toute suppression : `core/validation_ia.py` et `core/history_store.py` (utilisés par l'app Streamlit, pas par l'API à ce jour).

## 5. Plan de retour arrière

- Le code n'est jamais supprimé, seulement archivé : on peut remettre les fichiers en place.
- Retirer le message de fin = un `git revert` du commit de coupure.
- Relancer l'app Streamlit Cloud : elle reste disponible tant qu'elle n'est pas supprimée. Ne la supprimer qu'en dernier, après une période de stabilité du nouveau site.
- Si l'API tombe : l'app Streamlit n'en dépend pas ; le site Vercel, si. Garder l'API surveillée pendant la transition.

## 6. Points réservés à Quentin

- Le moment de la coupure et le texte du message de fin.
- L'arrêt ou la suppression de l'app sur Streamlit Cloud.
- La gestion de l'historique existant (voir prérequis).
