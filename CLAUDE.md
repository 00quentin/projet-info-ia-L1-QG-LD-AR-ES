# Quant Terminal — Guide pour Claude

Application Streamlit pédagogique qui simule l'impact d'événements économiques sur un portefeuille (vrais prix Yahoo Finance + IA OpenAI). Projet L1 MIASHS.

---

## Commandes essentielles

```bash
# Lancer l'app en local (port 8501)
streamlit run app.py

# Lancer tous les tests
pytest

# Lancer un test précis
pytest tests/test_runner.py -v

# Vérifier qu'un fichier Python compile (avant commit)
python -m py_compile views/dashboard.py
```

Pré-requis : Python 3.10+, fichier `.env` avec `OPENAI_API_KEY=sk-...` à la racine.

---

## Architecture en 1 minute

```
app.py              → Router principal (orchestration onglets, ne contient pas de logique métier)
handlers.py         → Flots de lancement (couple session_state + spinners + notifications)
config.py           → TOUTES les constantes (actifs, profils, couleurs, bornes)
schemas.py          → Validation Pydantic des réponses IA (bornes par actif)

core/               → Logique métier PURE (zéro import streamlit)
├── runner.py       → lancer_simulation_scenario(), lancer_backtest()
├── portfolio.py    → calcul poids, valeur, allocations
├── metrics.py      → Sharpe, VaR, Max Drawdown, volatilité
├── history_store.py→ persistance historique (JSON disque)
├── validation.py   → validations actifs/scénarios
├── risk_alerts.py  → alertes automatiques sur métriques
├── custom_assets.py→ ajout d'actifs personnalisés (tickers Yahoo)
└── export_csv.py   → export CSV

components/         → UI réutilisable Streamlit
├── header.py, sidebar.py, footer.py
├── charts.py       → figures Plotly
├── notifications.py→ toasts, alertes
├── styling.py      → injection CSS
├── empty_states.py, skeletons.py
└── *_illustrations.py → blocs visuels pédagogiques

views/              → 1 fichier par onglet (dashboard, portefeuille, comparaison, backtest, historique, academie, chat, apropos)

ia_bot.py           → Appels OpenAI (cache, sanitization anti-injection, validation Pydantic)
market_data.py      → Yahoo Finance via yfinance (cache 1h, fallback snapshot JSON)
simulation.py       → Moteur de simulation (probabiliste, historique, ML)
pdf_generator.py    → Rapports PDF via ReportLab
logger.py           → get_logger(nom_module)

tests/              → pytest, 1 fichier par module core/
.streamlit/         → theme + config Streamlit
style.css           → CSS custom (palette neutre Linear/Vercel, indigo #6366f1)
```

**Règle d'or** : `core/` ne doit JAMAIS importer `streamlit`. Toute interaction UI passe par `handlers.py`, `components/` ou `views/`.

---

## Conventions de code

- **Langue** : code et commentaires en **français** (noms de fonctions/variables en français aussi : `lancer_simulation_scenario`, `actifs_selectionnes`, etc.)
- **Docstrings** : courtes, en haut de chaque module avec séparateurs `===`. Exemple :
  ```python
  """
  core/portfolio.py
  =================
  Calculs de pondération et valeur du portefeuille.
  """
  ```
- **Commentaires** : minimaux, uniquement pour le **pourquoi** non-évident (workaround, contrainte, choix surprenant). Pas de comment pour expliquer le quoi.
- **Imports** : groupés (stdlib → tiers → locaux), avec ligne vide entre groupes.
- **Types** : annotations utilisées dans `core/` et signatures publiques. Pas obligatoire partout.
- **Cache Streamlit** : `@st.cache_data` pour données, `@st.cache_resource` pour clients (OpenAI, etc.).

---

## Patterns importants

1. **Validation côté pure puis notification côté UI**
   `core/validation.py` retourne un message d'erreur (str ou None). `handlers.py` appelle puis `notify_warn()` si erreur. Ne jamais lever d'exception métier dans `core/`.

2. **Pydantic pour les réponses IA**
   Toute réponse de `ia_bot.py` est validée via `schemas.py`. Les bornes par actif (ex: S&P 500 entre -55% et +45%) empêchent les valeurs aberrantes.

3. **session_state init centralisé**
   Voir `init_session_state()` dans `app.py`. Ajoute une clé là si tu en crées une nouvelle.

4. **Constantes dans `config.py`**
   Jamais de magic numbers dans le code. Si tu ajoutes un seuil, une couleur, un horizon → dans `config.py`.

5. **Logger plutôt que print**
   `log = get_logger("nom_module")` puis `log.info(...)`, `log.error(..., exc_info=True)`.

---

## ⚠ Règle de non-régression (CRITIQUE)

**Chaque commit doit être au moins aussi complet que le précédent.** Le site ne doit JAMAIS perdre de valeur ajoutée entre deux versions.

Concrètement, avant tout commit :
- ✅ Toutes les fonctionnalités existantes doivent rester accessibles et fonctionnelles.
- ✅ Aucun onglet, métrique, graphique, ou option ne disparaît sans remplacement équivalent (ou supérieur).
- ✅ Si on remplace un composant, le nouveau doit couvrir **au minimum** le même périmètre que l'ancien.
- ✅ Si une simplification supprime du contenu, demander confirmation avant.
- ❌ Pas de "fix" qui casse une fonctionnalité ailleurs.
- ❌ Pas de refactor qui réduit le scope visible pour l'utilisateur.

En cas de doute → demander avant de retirer quoi que ce soit.

---

## Pièges à éviter

- ❌ **Importer `streamlit` dans `core/`** → casse l'isolation logique/UI et les tests.
- ❌ **Modifier `session_state` depuis `core/`** → seul `handlers.py`/`views/`/`components/` le font.
- ❌ **Hardcoder un prix/volatilité** → toujours passer par `market_data.py` (cache + fallback gérés).
- ❌ **Bypasser la validation Pydantic** → si l'IA renvoie un truc bizarre, ça casse la simulation (cf. bug historique "Or +1 222 891%").
- ❌ **Ajouter une dépendance sans la mettre dans `requirements.txt`** → casse le déploiement Streamlit Cloud.
- ❌ **Mocker la DB / les vraies données dans les tests** → utiliser les fixtures `tests/conftest.py`.

---

## Workflow recommandé

1. **Avant de modifier** : lire le module concerné + ses tests (`tests/test_xxx.py`).
2. **Pendant** : préférer Edit sur des fichiers existants plutôt qu'en créer de nouveaux.
3. **Après une modif Python** : `python -m py_compile <fichier>` pour valider la syntaxe.
4. **Avant un commit demandé** : lancer `pytest` si la modif touche `core/` ou `handlers.py`.
5. **Pour les changements UI** : signaler explicitement quand un test visuel manuel est nécessaire (Claude ne peut pas voir le rendu Streamlit).

---

## Branches & commits

- Branche principale : `developpement` (pas `main`).
- Style de commit : court titre français, sans préfixe conventionnel obligatoire. Ex : `Fix scenario non affiche + boutons presets redondants`.
- Ne pas committer sans demande explicite.

---

## Profil utilisateur

Quentin est **débutant** (L1). Pour communiquer efficacement :
- Réponses **courtes et concrètes**, pas de paragraphes théoriques.
- Quand tu modifies du code, **dis ce que tu as changé** et pourquoi en 1-2 phrases.
- Si une décision a un trade-off non-évident, mentionne-le en 1 ligne.
- Préfère **proposer** plutôt qu'implémenter directement sur des choix d'architecture importants.
