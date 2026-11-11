# Rapport d'avancement — migration Streamlit → site web

*Rapport n° 1 — 11/11/2026 — branche `claude/site-analysis-redesign-k1pqb4` (dernier commit `729a44b`)*

## En une phrase
Le nouveau site reprend **toutes** les fonctions de l'app Streamlit et il est techniquement sain (tests, types, lint et build au vert, aucune erreur dans les pages) ; il ne reste que la **mise en ligne** (API sur Render, site sur Vercel) et **2 relectures de contenu** avant de pouvoir couper Streamlit.

## Avancement (lignes ✅ dans `docs/MIGRATION.md`)
| Section | ✅ | Total | % |
|---|---|---|---|
| Simulation prospective | 17 | 17 | 100 % |
| Backtest historique | 4 | 4 | 100 % |
| Autres onglets et éléments | 6 | 6 | 100 % |
| Reste à faire avant de couper Streamlit | 0 | 4 | 0 % |
| **Total** | **27** | **31** | **87 %** |

Aucun état n'a été changé : la liste correspond à ce que j'ai constaté. J'ai seulement précisé les 2 lignes de relecture (fichier et ligne concernés).

## Santé technique
| Vérification | Résultat |
|---|---|
| `pytest` (racine) | ✅ 272 tests réussis, 0 échec (4,3 s) |
| Moteur sans Streamlit (`market_data`, `ia_bot`, `api.main`) | ✅ affiche `False` |
| TypeScript (`npx tsc --noEmit`) | ✅ 0 erreur |
| ESLint (`npx eslint src`) | ✅ 0 erreur, 0 avertissement |
| Build Next.js (`npm run build`) | ✅ 6 routes générées en statique |
| API (port 8010) | ✅ `/api/catalogue`, `/api/marches`, `/api/conjoncture`, `/api/backtests` répondent 200 (vrais cours Yahoo du 11/11) |
| Pages `/`, `/backtest`, `/historique`, `/academie`, `/a-propos` en 1440×900 et 390×844 | ✅ 10/10 chargées (HTTP 200), 0 erreur console, 0 requête en échec, 0 débordement horizontal |
| Backtest complet dans le navigateur (COVID-19, profil Équilibré) | ✅ résultat en 4 à 6 s sur ordinateur et mobile : synthèse, risque, alertes, perf par actif, courbes par classe, détail, export CSV/PDF |
| Simulation prospective, chat, PDF | non testés : ils appellent l'IA (payant) |

Seul message dans la console : un avertissement Next.js (« CSS préchargé mais pas utilisé tout de suite »), sans effet visible.

## Ce qui a changé (15 derniers commits, premier rapport)
- **Page Historique** sur le site, avec exports CSV / PDF et lien de partage (`5d4e4bf`).
- **Bulle « Analyste IA »** : discussion animée, conversation gardée dans le navigateur (`d78ba97`).
- **Page Backtest** : crises réelles, période libre, résultats complets (`0385aae`), puis fusion avec le chat (`ad53dbe`).
- **Relancer depuis l'historique**, PDF sans double échappement, erreurs du chat mieux gérées (`6c72d1c`).
- **L'Analyste IA connaît le résultat affiché** (simulation, comparaison, backtest) (`51e3e46`).
- **Accessibilité** : contrastes WCAG AA, `aria-controls` corrigé (`588491c`).
- **Pages Académie (9 onglets, formules KaTeX) et À propos** complètes (`9cdfd7f`, `2df3297`) ; la page provisoire « En construction » a été supprimée, elle ne sert plus.
- **Sélecteur d'actifs** : étiquettes, recherche, catégories, cours du jour, et fenêtre affichée au premier plan (`18017d4`, `2df3297`).
- **Agent superviseur** et liste de contrôle `docs/MIGRATION.md` (`729a44b`).
- Les 4 autres commits sont des fusions de branches de travail des agents.

## Problèmes trouvés (du plus grave au moins grave)
1. **Site et API pas encore en ligne** — `render.yaml` est prêt pour l'API, mais rien n'est encore déployé (pour Vercel, aucun fichier n'est nécessaire : il suffit de régler `NEXT_PUBLIC_API_URL`). Tant que ce n'est pas fait, on ne peut pas couper Streamlit.
2. **Phrase fausse dans l'Académie, module 3.3** — `web/src/contenu/academie/macro.tsx` l. 111 : « indicateur a 100% de précision sur 60 ans ». Aucun indicateur n'est fiable à 100 % (il y a eu de fausses alertes, par exemple en 1966 et en 2022-2023) : à nuancer.
3. **Dates qui se chevauchent sous les graphiques** — `web/src/components/charts/GraphiqueLignes.tsx` l. 82-85. On lit « 17 févr. 202024 févr. 2020 » sur le graphique d'évolution et « 17 févr. 2020mars 2020 » sur les petits graphiques par classe d'actifs (vu sur la page Backtest, en 1440 et en 390). La largeur des étiquettes est sous-estimée (6,4 px par caractère) et l'écart entre deux dates voisines n'est pas vérifié (seulement l'écart avec la dernière date).
4. **Photos de l'Académie non vérifiées** — les 8 images viennent de Wikimedia (`web/src/components/academie/Photo.tsx`). Wikimedia ne répondait pas depuis mon environnement : il faut les vérifier une fois le site en ligne (s'il y a un problème, une image de remplacement s'affiche à la place).
5. **Accessibilité (mineur)** — la page d'accueil n'a pas de titre `<h1>` (les 4 autres pages en ont un), et seule la page d'accueil a une zone `<main>`. Ça gêne un peu les lecteurs d'écran.

## Prochaines étapes recommandées
1. **Déployer** l'API sur Render (clé OpenAI + `QT_ORIGINES_AUTORISEES`), puis le site sur Vercel (`NEXT_PUBLIC_API_URL`), et vérifier les photos de l'Académie en ligne.
2. **Corriger le module 3.3** (« 100 % de précision ») et l'**axe des dates** de `GraphiqueLignes.tsx`.
3. Une fois en ligne, **faire une simulation complète avec l'IA** (simulation, comparaison de 3 scénarios, chat, PDF) pour valider les parties que je n'ai pas pu tester ici.
