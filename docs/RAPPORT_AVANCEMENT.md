# Rapport d'avancement : migration Streamlit → site web

*Rapport n° 2, 12/11/2026, branche `claude/site-analysis-redesign-k1pqb4` (dernier commit `5163880`), avec vérification de la version en ligne*

## En une phrase
Le site (https://quant-terminal-qg-team.vercel.app) et l'API (https://quant-terminal-api-baxq.onrender.com) sont **en ligne et fonctionnent de bout en bout** : simulation, comparaison, backtest, chat, PDF, CSV et historique. Avant de couper Streamlit, il ne reste qu'une chose : **regarder les photos de l'Académie dans un navigateur normal**. Un défaut d'affichage est aussi à corriger dans le chat : les formules apparaissent en code brut.

## Avancement (lignes ✅ dans `docs/MIGRATION.md`)
| Section | ✅ | Total | % |
|---|---|---|---|
| Simulation prospective | 17 | 17 | 100 % |
| Backtest historique | 4 | 4 | 100 % |
| Autres onglets et éléments | 6 | 6 | 100 % |
| Reste à faire avant de couper Streamlit | 3 | 4 | 75 % |
| **Total** | **30** | **31** | **97 %** (87 % au rapport n° 1) |

Changements d'état faits dans `docs/MIGRATION.md` :
- **Déployer l'API sur Render** : ❌ → ✅. L'API répond. La clé OpenAI marche : simulation, chat et PDF ont tous abouti. Le CORS n'accepte que le site : une autre origine ne reçoit pas d'en-tête `access-control-allow-origin`.
- **Déployer le site sur Vercel** : ❌ → ✅. Les 5 pages se chargent, le site appelle bien l'API Render et le parcours complet fonctionne.
- **Photos de l'Académie** : ❌ → 🟡. Le repli (légende + icône « image indisponible ») s'affiche bien en ligne. Par contre, je n'ai pas pu voir les photos elles-mêmes : **mon réseau bloque Wikimedia** (le proxy répond `403` à `commons.wikimedia.org`, le navigateur affiche `ERR_TUNNEL_CONNECTION_FAILED`). Ça ne veut **pas** dire qu'elles sont cassées.

## Santé technique

### Dépôt
| Vérification | Résultat |
|---|---|
| `pytest` (racine) | ✅ 273 tests réussis, 0 échec (5,9 s) ; +1 test depuis le rapport n° 1 |
| Moteur sans Streamlit (`market_data`, `ia_bot`, `api.main`) | ✅ affiche `False` |
| TypeScript (`npx tsc --noEmit`) | ✅ 0 erreur |
| ESLint (`npx eslint src`) | ✅ 0 erreur, 0 avertissement |
| Build Next.js (`npm run build`) | ✅ 6 routes statiques |
| Site local (API 8010 + site 3010) : 5 pages × 2 tailles | ✅ 10/10 en HTTP 200 ; 0 erreur console ; 0 requête en échec ; 0 débordement ; 1 `<h1>` et 1 `<main>` sur chaque page |

### Version en ligne (navigateur Playwright)
| Vérification | Résultat |
|---|---|
| 5 pages × 2 tailles (1440×900 et 390×844) | ✅ 10/10 en HTTP 200 ; 0 erreur console ; 0 requête en échec ; 0 débordement horizontal |
| Simulation « Choc pétrolier », Monte-Carlo (1 000 trajectoires, activé par défaut) | ✅ **13,5 s**. Tout s'affiche : synthèse et fourchette, analyse IA, conjoncture FRED, précédents, comparaison calibrée/libre, évolution vs S&P 500 / MSCI World, 4 tuiles de risque, répartition, perf par actif, courbes par classe, détail, exports. 0 débordement |
| Comparaison de 2 scénarios (Choc pétrolier + Hausse brutale FED) | ✅ **12,1 s**. Les onglets Comparaison / Scénario A / Scénario B s'affichent, chaque scénario a ses résultats complets |
| Backtest « COVID-19 (mars 2020) » | ✅ **3,4 s** (0,3 s au 2e lancement, grâce au cache). Résultats complets et CSV de 44 lignes. Aucun chevauchement des dates sous les graphiques, ni sur ordinateur ni sur mobile |
| Chat : question d'exemple (ratio de Sharpe) | ✅ réponse en 7,2 s ; l'IA reprend les chiffres affichés (« votre Sharpe est de 0,35 »). ⚠ La formule s'affiche en code brut (voir Problème 1) |
| Chat : « Explique-moi le résultat que j'ai sous les yeux » | ✅ réponse en 13,8 s ; l'IA parle bien du scénario affiché (pétrole −30 %, 100 jours, précédent de 1973) |
| Rapport PDF | ✅ **10,5 s** entre le clic et le téléchargement ; fichier `rapport-quant-terminal-2026-11-12.pdf` de 12 Ko, qui commence bien par `%PDF-` |
| Export CSV de la simulation | ✅ 102 lignes, 10 colonnes, séparateur `;` |
| Historique | ✅ 4 entrées : 1 simulation, 2 de la comparaison (A et B) et 1 backtest |
| « Relancer » depuis l'historique | ✅ ouvre `/?s=…&s2=…` ; les 2 scénarios sont pré-remplis et le bandeau « les réglages sont pré-remplis » s'affiche. Rien n'est lancé tout seul, donc aucun appel IA |
| Photos de l'Académie | 🟡 non vérifiables ici (Wikimedia bloqué par mon réseau) ; le repli s'affiche correctement, sans débordement |
| Temps de réponse de l'API (routes de données) | ✅ 0,2 à 0,6 s. Je n'ai pas vu de réveil lent de Render : l'API était déjà active |

Appels IA payants utilisés : **5 requêtes** (1 simulation, 1 comparaison, 2 messages de chat, 1 PDF), comptées 6 par sécurité car la comparaison contient 2 scénarios. Le scénario A était sans doute déjà en cache sur le serveur. Le budget de 6 est respecté.

Seul message dans la console : l'avertissement Next.js « CSS préchargé mais pas utilisé tout de suite », sans effet visible (déjà signalé au rapport n° 1).

## Ce qui a changé depuis le dernier rapport
- **Corrections du rapport n° 1** (`41e1b3d`). Les 3 sont vérifiées, en local et en ligne :
  - axe des dates sans chevauchement ;
  - Académie 3.3 nuancée (« pas un oracle ») ;
  - un `<h1>` et une seule zone `<main>` sur toutes les pages.
- **API : message clair si la clé OpenAI manque** (`5163880`), avec 1 test de plus.
- **Mise en ligne** (rien dans `git`) : API sur Render et site sur Vercel. La version en ligne contient bien les corrections ci-dessus.

## Problèmes trouvés (du plus grave au moins grave)
1. **Formules mathématiques illisibles dans le chat.** L'IA écrit ses formules en LaTeX (`\[ … \]`, `\( … \)`). La bulle les affiche telles quelles, par exemple « [ \text{Sharpe} = \frac{R_p - R_f}{\sigma_p} ] » ou « (\sigma_p) ». Pour un étudiant, c'est illisible. Fichier : `web/src/components/chat/Message.tsx` (le texte passe par `react-markdown` sans gestion des maths ; KaTeX est déjà installé pour l'Académie). Autre solution : demander à l'IA de ne pas utiliser de LaTeX, dans le message système de `discuter_avec_ia()` (`ia_bot.py`).
2. **Photos de l'Académie toujours pas vues.** Le code de repli marche, mais quelqu'un doit ouvrir https://quant-terminal-qg-team.vercel.app/academie dans un navigateur normal. Il faut regarder les onglets 3 (Macro), 4 (Cas historiques), 5 (Stratégies) et 7 (Biais), plus les synthèses. Fichier : `web/src/components/academie/Photo.tsx`.
3. **Date en double dans le nom du CSV du backtest** : `quant_terminal_backtest_covid_19_mars_2020_20261112_20261112_0030.csv`. La date est ajoutée une fois dans `web/src/components/backtest/outils.ts` (l. 107-109, `_${jour}`), puis une seconde fois par `nomFichierCsv()` dans `web/src/components/exports/csv.ts` (l. 58-60). C'est sans gravité : seul le nom du fichier est touché.
4. **Réveil de Render (offre gratuite)** : non observé ce soir, mais le premier visiteur après une pause peut attendre 30 à 60 s. Il faudra vérifier que le site affiche alors un message d'attente clair.
5. **Mineur** : sur mobile, les noms d'actifs longs sont coupés dans « Performance par actif » (« Or (Gold Spot, $/… », « EUR/USD (Euro-… »). L'avertissement CSS de Next.js est toujours là, sans effet visible.

Remarque sur la procédure (pas sur le site) : `NEXT_PUBLIC_API_URL` est **figée au moment du build**. La passer à `next start`, comme le dit l'étape 3 de `.claude/agents/superviseur.md`, ne change rien. Il faut la donner à `npm run build` (sans ça, le site local appelle `localhost:8000`). Je ne peux pas modifier ce fichier ; c'est à la session principale de corriger la consigne.

## Prochaines étapes recommandées
1. **Ouvrir l'Académie en ligne dans un vrai navigateur** pour voir les 8 photos. Si elles s'affichent, la liste de contrôle est complète et on peut prévoir l'arrêt de Streamlit.
2. **Afficher les formules du chat** (KaTeX dans `Message.tsx`, ou consigne « pas de LaTeX » dans `ia_bot.py`), puis corriger le nom du CSV du backtest.
3. **Tester le réveil de Render** : après 15 min sans visite, ouvrir le site et noter le temps d'attente et le message affiché.
