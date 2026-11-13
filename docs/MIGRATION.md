# Migration Streamlit → nouveau site (web/)

Liste de contrôle de non-régression : chaque fonction de l'app Streamlit et son équivalent
sur le nouveau site. Tenue à jour par l'agent `superviseur` (voir `.claude/agents/superviseur.md`).
Légende : ✅ fait et vérifié · 🟡 partiel · ❌ manquant.
Dernière vérification : 13/11/2026 (rapport n° 3, branche `claude/site-analysis-redesign-k1pqb4`, commit `ef135a3`, en local ; pas encore déployée). Voir `docs/RAPPORT_AVANCEMENT.md`.

**Règle** : on ne coupe l'app Streamlit que lorsque toutes les lignes sont ✅ et que le site est en ligne.

## Simulation prospective
| Fonction Streamlit | Nouveau site | État |
|---|---|---|
| Scénario libre + 8 scénarios rapides | Formulaire, puces animées | ✅ |
| Comparaison de 1 à 3 scénarios (onglet Comparaison) | Sélecteur 1·2·3, vue Duel/Tournoi, classement, métriques comparées | ✅ |
| Choix des actifs par catégorie (23 actifs) | Sélecteur : recherche, catégories, cours du jour | ✅ |
| Actifs personnalisés (ticker Yahoo) | Dans le sélecteur d'actifs | ✅ |
| Capital, profils Prudent / Équilibré / Agressif / Personnalisé | Cartes de profil, parts affichées sur les étiquettes | ✅ |
| Options : horizon, modèle, Monte-Carlo, prix réels, calibration, conversion € | Options avancées | ✅ |
| Valeur finale + variation, badges | Synthèse + jauge de fourchette Monte-Carlo | ✅ |
| Inflation et taux directeurs estimés, analyse IA | Carte Analyse de l'IA (+ conjoncture réelle FRED) | ✅ |
| Calibration : précédents, fiabilité, calibrée vs libre | Carte Analyse de l'IA | ✅ |
| 4 métriques de risque + alertes | Tuiles de risque + alertes | ✅ |
| Évolution vs S&P 500 / MSCI World + cartes de performance | Graphique + 3 cartes finales + tableau | ✅ |
| Graphiques par classe d'actifs (base 100, bandes MC) | Courbes par classe d'actifs | ✅ |
| Heatmap de performance par actif | Barres de performance | ✅ |
| Onglet Portefeuille (camembert, détail) | Répartition par classe + détail du portefeuille | ✅ |
| Export CSV | Exporter et partager | ✅ |
| Rapport PDF avec analyse IA | Exporter et partager | ✅ |
| Lien de partage | Adresse de la page + bouton copier | ✅ |

## Backtest historique
| Fonction Streamlit | Nouveau site | État |
|---|---|---|
| 6 événements + période personnalisée | Cartes d'événements + période libre | ✅ |
| Conversion € (taux BCE), actifs indisponibles signalés | Interrupteur + encadré | ✅ |
| Métriques réelles, évolution vs indices, graphiques par catégorie, perf par actif | Page /backtest | ✅ |
| Export CSV + PDF | Exporter et partager | ✅ |

## Autres onglets et éléments
| Fonction Streamlit | Nouveau site | État |
|---|---|---|
| Historique (liste, détail, renommage, effacer) | /historique (+ filtres, suppression, Relancer) | ✅ |
| Académie (7 modules + lexique + méthodologie) | /academie (9 onglets, KaTeX) | ✅ |
| À propos | /a-propos | ✅ |
| Analyste IA (bulle de chat) | Bulle de chat (+ contexte du résultat affiché) | ✅ |
| Bandeau des marchés, rechargement des prix | Bandeau défilant + bouton ↻ | ✅ |
| Guide d'utilisation, mode sombre, pied de page, notifications | Guide (?), thème, pied de page, notifications | ✅ |

## Reste à faire avant de couper Streamlit
| Tâche | État |
|---|---|
| Déployer l'API sur Render (`render.yaml`, clé OpenAI) | ✅ en ligne sur https://quant-terminal-api-baxq.onrender.com (vérifié le 12/11 : clé OpenAI active, CORS limité au site) |
| Déployer le site sur Vercel (`NEXT_PUBLIC_API_URL`) | ✅ en ligne sur https://quant-terminal-qg-team.vercel.app (vérifié le 12/11 : simulation, comparaison, backtest, chat, PDF, CSV, historique) |
| Vérifier les photos de l'Académie (Wikimedia) en ligne (8 fichiers, `web/src/components/academie/Photo.tsx`) | ✅ vérifiées en ligne le 13/11 (téléphone) |
| Faire relire 3.3 de l'Académie (courbe des taux : « 100 % de précision », `web/src/contenu/academie/macro.tsx` l. 111) | ✅ corrigé (phrase nuancée, `41e1b3d`, visible en ligne) |
