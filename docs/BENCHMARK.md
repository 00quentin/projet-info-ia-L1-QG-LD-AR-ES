# Benchmark produit et design : Quant Terminal

Veille du 13/11/2026 pour rendre le site présentable en hackathon et crédible comme produit.
Base de travail : le code de `web/src/` (lu fichier par fichier), `docs/MIGRATION.md`, le site en ligne
(vérifié par requêtes HTTP) et une recherche web. Les sites concurrents n'ont pas pu être ouverts depuis
cet environnement : leurs descriptions viennent de leur documentation et d'articles, cités en lien.

> **Règle de non-régression (CLAUDE.md).** Toutes les propositions ci-dessous **déplacent** ou **reformulent**
> de l'information, elles n'en suppriment pas. Quand un texte d'aide « disparaît » de l'écran, il part dans une
> infobulle, un bloc dépliable ou l'Académie. Chaque retrait visible est à valider par Quentin avant le commit.

---

## 0. En bref

1. **Le différenciateur est fort et rare.** Aucun outil grand public trouvé ne fait « je décris un événement en
   français, l'IA estime l'impact sur *mon* portefeuille à partir des vrais cours, avec la fourchette Monte-Carlo ».
   Les autres font du backtest (passé) ou des projections à rendement fixe. Il faut le dire en une phrase,
   en haut de la page.
2. **Ce qui fait amateur, ce n'est pas le style, c'est le contenu technique qui dépasse** : tickers Yahoo bruts
   (`^GSPC`, `GC=F`, `DX-Y.NYB`, `1482.T`) sous chaque actif, badge « dans le profil » en 10 px, noms d'actifs
   mi-français mi-anglais (« Or (Gold Spot, $/oz) »), et des phrases d'aide sous presque chaque titre.
3. **Le système visuel est presque là**, mais sans échelle fixe : 18 tailles de texte (dont 8 tailles arbitraires de 10 à 32 px),
   7 rayons d'angle, 6 marges intérieures de cartes différentes. Il faut fixer ces valeurs une fois, puis s'y tenir.
4. **Il manque les pages d'un « vrai » site** : mentions légales (obligatoires), confidentialité, 404 en français
   (la 404 en ligne est la page anglaise par défaut de Next.js : « This page could not be found »),
   page méthodologie, FAQ et contact. Il manque aussi l'image de partage, le sitemap, `robots.txt` et le manifeste,
   tous absents en ligne (404).
5. **Il y a trop d'animations par endroits** : 11 nombres qui comptent en même temps sur la page de résultats, des cartes non
   cliquables qui se soulèvent au survol, un logo qui tourne, des blocs qui apparaissent avec un flou pendant 0,6 s.
   En retirer rendra le site plus propre.
6. **Pour le hackathon, la plus grosse menace est l'attente** : l'API Render gratuite se met en veille après
   15 min et met de 30 à 60 s à repartir, puis l'IA met environ 15 s à répondre. Une démo en un clic avec un résultat
   déjà calculé, plus un ping régulier qui garde l'API éveillée, évitent un écran d'erreur devant le jury.

---

## 1. Concurrents et sites proches

### 1.1 Vue d'ensemble

| Outil | Catégorie | Ce qu'il fait le mieux | À reprendre pour Quant Terminal |
|---|---|---|---|
| Portfolio Visualizer | Backtest et Monte-Carlo (US) | Profondeur : allocation, flux, rééquilibrage, Monte-Carlo | Comparer à des portefeuilles « paresseux » de référence |
| testfol.io | Backtest gratuit | Rapidité, bandes de rééquilibrage, export CSV | Une page = un formulaire + un résultat, sans compte |
| Curvo Backtest | Backtest pour l'Europe, en € | Données en euros, portefeuilles d'exemple, FAQ claire | Portefeuilles d'exemple nommés, présentation « pour l'investisseur européen » |
| PortfoliosLab | Analyse de risque | Pertes maximales : profondeur, durée, **temps de récupération** | Ajouter « temps pour revenir au capital de départ » |
| PortfolioPilot | Stress-test grand public | Rejoue 2008 et 2020 sur le portefeuille, gratuit | Formulation « combien je perds, combien de temps pour m'en remettre » |
| Nitrogen, Vanguard | Stress-tests pour conseillers | Bibliothèque de scénarios historiques et hypothétiques | Bibliothèque de scénarios classés (géopolitique, taux, tech…) |
| Composer | Stratégies sans code, avec IA | L'IA traduit un objectif en stratégie visible et modifiable | Montrer la logique de l'IA de façon modifiable, « rien ne se fait sans vous » |
| Finary | Patrimoine (France) | Interface fluide, simulateur de patrimoine, ton français | Ton grand public, hypothèses visibles et réglables |
| Koyfin | Terminal de données | Tableaux de bord denses mais soignés | Densité maîtrisée : étiquettes discrètes, chiffres en avant |
| Simply Wall St | Analyse d'actions | Le « Snowflake » : 5 critères en une forme | Un résumé visuel unique du risque au lieu de 4 tuiles chargées |
| Stockopedia | Analyse d'actions | Notes en centiles + « feux » comparés aux pairs | Situer chaque métrique sur une échelle simple (faible → élevé) |
| Trade Republic | Courtier mobile | Graphique minimal (1J, 1S, 1M, 1A, Max), lecture au doigt | Graphique épuré, valeur lue en glissant |
| Revolut | Néobanque, actions | Fiche d'actif : prix, graphique, « À propos », chiffres clés | Fiche d'actif courte : nom clair, une ligne de description |
| BoursoBank (Boursorama) | Banque, portefeuille virtuel | Portefeuille fictif gratuit pour s'entraîner | Message « s'entraîner sans risque » très parlant pour les débutants |
| Wealthfront | Robo-conseiller | Projections présentées comme « hypothétiques », méthodologie publiée | Vocabulaire juridique prudent, page de méthode |
| Investopedia Simulator, La finance pour tous, Mes questions d'argent | Pédagogie | Lexique, simulateurs simples, ton neutre et institutionnel | Lexique relié depuis les résultats, ton neutre, liens vers ces sources publiques |

### 1.2 Détail par outil

**Portfolio Visualizer** : la référence du backtest gratuit pour les particuliers. Sources :
[guide AAII](https://www.aaii.com/investingideas/article/536490-using-portfolio-visualizer-to-test-allocation-strategies),
[Oblivious Investor](https://obliviousinvestor.com/calculator-for-backtesting-a-portfolio-or-asset-allocation-also-monte-carlo-simulations/),
[revue DEV](https://dev.to/pickuma/portfolio-visualizer-review-backtesting-that-goes-beyond-the-equity-curve-28n2).
- Points forts : un outil par question (backtest, Monte-Carlo, corrélations), une comparaison systématique à des
  portefeuilles de référence, un Monte-Carlo avec retraits et inflation.
- Point faible souvent cité : l'interface est austère et dense, et le Monte-Carlo suppose une loi normale.
- **À reprendre** : comparer le portefeuille à 2 ou 3 portefeuilles types nommés (« 60/40 », « 100 % actions monde »),
  pas seulement au S&P 500 et au MSCI World. Écrire honnêtement la limite « loi normale » dans la page Méthode, comme ces revues le reprochent.

**testfol.io** : backtest gratuit, sans compte, avec export CSV ([comparatif FindMyMoat](https://www.findmymoat.com/vs/curvo-backtest-vs-testfol-io)).
- **À reprendre** : la simplicité « une page, aucun compte ». Quant Terminal la respecte déjà, c'est un argument à afficher
  (« Gratuit, sans inscription »).

**Curvo Backtest** : le concurrent le plus proche culturellement : européen, en euros, traduit en français
([page outil](https://curvo.eu/backtest), [FAQ](https://curvo.eu/backtest/en/faq), [article FR](https://curvo.eu/fr/article/comprends-ton-portefeuille-detf-avec-backtest)).
- Points forts : « fait pour l'investisseur européen », données en euros, **portefeuilles d'exemple** prêts à analyser,
  FAQ publique.
- **À reprendre** : (1) des portefeuilles d'exemple à côté des profils (« Portefeuille 60/40 », « Tout or et obligations »),
  (2) l'argument « en euros, comme le vivrait un investisseur européen », déjà dans les options mais caché, (3) une FAQ.

**PortfoliosLab** : outils de pertes maximales et ratios
([outil Drawdowns](https://portfolioslab.com/tools/drawdowns), [doc](https://portfolioslab.com/docs/risk-analysis/drawdown-analysis)).
- Point fort : pour chaque chute, il affiche **la profondeur, la durée et le temps de récupération**. Le temps de récupération parle beaucoup
  plus à un débutant que le Sharpe.
- **À reprendre** : dans la tuile « Perte maximale », ajouter « jour du creux » et « retour au capital : jour N / jamais
  sur l'horizon ». Le calcul se fait à partir des valeurs déjà renvoyées par l'API, sans nouvelle donnée.

**PortfolioPilot** : stress-test grand public, gratuit pour 2008 et 2020
([page stress test](https://portfoliopilot.com/portfolio-management/portfolio-stress-test),
[FAQ](https://portfoliopilot.com/help/faqs/how-do-i-stress-test-my-portfolio-for-a-market-downturn-or-crisis-scenario)).
- Point fort : un discours simple, « perte totale + temps de récupération », et une transparence sur la méthode
  (approximation du portefeuille par ses expositions).
- **À reprendre** : la même franchise sur la méthode. La page Backtest de Quant Terminal rejoue de vrais cours,
  ce qui est **plus précis** que l'approximation de PortfolioPilot : il faut le dire.

**Nitrogen et Vanguard** : stress-tests pour conseillers ([Nitrogen](https://nitrogenwealth.com/features/stress-tests/),
[Vanguard](https://advisors.vanguard.com/strategies/portfolio-strategies/portfolio-analytics/stress-testing)).
- Point fort : une **bibliothèque de scénarios** (historiques et hypothétiques) tenue à jour.
- **À reprendre** : classer les 8 scénarios rapides en familles (Géopolitique, Banques centrales, Technologie, Crises)
  et en afficher 4 par défaut, avec un lien « Plus d'idées ».

**Composer** : stratégies sans code avec « Trade with AI »
([aide Composer](https://help.composer.trade/article/254-what-is-trade-with-ai), [revue](https://daytradereview.com/composer-trade-review)).
- Point fort : l'IA produit une stratégie **lisible et modifiable** dans l'éditeur visuel, et « rien ne s'exécute sans
  votre validation ».
- **À reprendre** : montrer les chocs estimés par l'IA (déjà présents dans « Calibrée ou libre ? ») comme une liste
  lisible « Ce que l'IA a supposé : actions −18 %, or +9 %… », placée **avant** le détail technique. À terme, permettre
  de corriger un choc et de relancer : c'est pédagogique et rassurant.

**Finary** : patrimoine, outil français ([simulateur](https://finary.com/fr/simulateur-de-patrimoine),
[avis Avenue des Investisseurs](https://avenuedesinvestisseurs.fr/avis-finary-agregateur-suivi-patrimoine)).
- Points forts : une interface jugée fluide et intuitive, des hypothèses (rendement, versements, inflation)
  visibles et réglables, un ton chaleureux en français.
- **À reprendre** : le ton (« votre patrimoine », phrases courtes), et des hypothèses affichées en clair au-dessus
  du résultat plutôt qu'en pastilles techniques.

**Koyfin** : terminal de données au design soigné ([revue DEV](https://dev.to/pickuma/koyfin-review-a-financial-data-terminal-that-costs-a-fraction-of-bloomberg-1mn1),
[comparatif Stock Rover](https://www.stockrover.com/?p=46603)).
- Point fort : une densité forte mais lisible, avec des libellés petits et discrets et des chiffres mis en avant.
- Point faible : certains tableaux de bord sont jugés encombrés, et l'affichage devient étroit sous la largeur d'une tablette.
- **À reprendre** : la règle « étiquette discrète, valeur forte » (voir aussi
  [Refactoring UI, « Labels are a last resort »](https://refactoringui.com/previews/labels-are-a-last-resort/)).

**Simply Wall St** : le « Snowflake » résume 5 critères en une forme colorée
([aide officielle](https://support.simplywall.st/hc/en-us/articles/360001740916-How-does-the-Snowflake-work)).
- Point fort : une seule image que l'on comprend d'un coup d'œil. La forme est protégée par un dessin déposé : il ne faut pas la copier.
- **À reprendre** : l'idée d'un **résumé visuel unique du risque**, par exemple une jauge à 4 crans (volatilité, perte
  maximale, VaR, Sharpe) au-dessus des 4 tuiles, dont les explications deviennent dépliables.

**Stockopedia** : notes en centiles et « feux » comparés aux pairs
([StockReports](https://www.stockopedia.com/learn/stockreports/about-the-stockreports-463018),
[feux](https://www.stockopedia.com/learn/stockreports/the-traffic-lights-463023)).
- Point fort : chaque ratio est **situé** par rapport aux autres (largeur et couleur selon le centile), et le site rappelle
  qu'une bonne note ne garantit rien.
- **À reprendre** : dans les tuiles de risque, remplacer la phrase d'explication par une petite échelle à 4 crans
  (Modérée → Très élevée) où la valeur est placée. C'est plus visuel et demande moins de texte.

**Trade Republic** : courtier mobile ([support : nouveau design](https://support.traderepublic.com/en-sk/1602-What-has-changed-in-the-new-app-design-),
[revue](https://northern.finance/en/review/traderepublic-review/)).
- Points forts : un graphique minimal (1J, 1S, 1M, 1A, Max) et une valeur que l'on lit en glissant le doigt sur la courbe.
- Point faible : la refonte a retiré des informations sous le graphique, ce que les utilisateurs ont regretté. La sobriété ne doit pas
  faire disparaître les données.
- **À reprendre** : sur mobile, lire la valeur au doigt sur `GraphiqueLignes` (le survol existe déjà, il faut vérifier
  le geste « appui + glisser »).

**Revolut** : fiche d'action ([page actions](https://www.revolut.com/stocks/), [exemple NVIDIA](https://revolut.com/stocks/nvda/)).
- Point fort : la fiche présente un nom clair, le prix, le graphique, puis « À propos » et quelques chiffres clés. Le ticker apparaît en petit, à côté du nom,
  jamais à la place d'une description.
- **À reprendre** : la hiérarchie **nom → une ligne de description → données**. Voir l'audit, point A1.

**BoursoBank (Boursorama)** : portefeuille virtuel gratuit
([aide](https://www.boursobank.com/aide-en-ligne/bourse/espace-membres/question/comment-acceder-a-mon-portefeuille-virtuel-516)).
- Point fort : l'argument « s'entraîner sans risque », compris par tous.
- **À reprendre** : une accroche du même genre, par exemple « Testez vos idées sur un portefeuille, sans risquer un euro ».

**Wealthfront** : projections et méthodologie
([précision des projections](https://support.wealthfront.com/hc/en-us/articles/209352866-How-accurate-are-Wealthfront-s-projections),
[mentions](https://www.wealthfront.com/disclosures)).
- Point fort : chaque projection est qualifiée d'**hypothétique**, avec ses hypothèses (médiane, frais compris, composition
  stable) et une page de méthode.
- **À reprendre** : écrire « simulation hypothétique » sous la valeur estimée, et une page `/methodologie`.

**Pédagogie publique** : [La finance pour tous (IEFP)](https://www.lafinancepourtous.com/),
[Mes questions d'argent (Banque de France)](https://www.tresor.economie.gouv.fr/Articles/2019/02/07/des-questions-d-argent-le-portail-mesquestionsdargent-fr-vous-accompagne),
Investopedia Simulator.
- Points forts : un lexique, un ton neutre, des sources institutionnelles.
- **À reprendre** : citer ces portails dans l'Académie (« Pour aller plus loin »). Le lien avec une source publique rassure.

### 1.3 Positionnement à afficher

- **Ce que les autres font** : rejouer le passé (backtest) ou prolonger une tendance (projection à rendement fixe).
- **Ce que fait Quant Terminal** : *et si… ?* Un événement décrit en français, traduit par une IA bornée (bornes par actif
  validées par Pydantic, ancrage sur des crises réelles), appliqué aux vrais cours avec 1 000 trajectoires.
- Accroche proposée (H1) : **« Et si ça arrivait demain ? »**, déjà présente dans l'écran vide et très bonne.
  Sous-titre : « Décrivez un événement économique. Quant Terminal estime son impact sur votre portefeuille, à partir des
  vrais cours de marché et des grandes crises passées. »
- Trois preuves sous l'accroche : « Vrais cours Yahoo Finance · 1 000 trajectoires Monte-Carlo · IA calibrée sur 2008,
  COVID, 2022 ».

---

## 2. Ce qu'il faut à un site « réel » et crédible

Légende : **O** = obligatoire · **R** = fortement recommandé · **B** = bonus.

### 2.1 Pages légales (France et UE)

Situation de Quant Terminal : pas de compte, pas de cookie, pas de publicité. Le navigateur garde l'historique, la conversation,
le thème et « guide vu » (`localStorage`), ainsi que le contexte du chat (`sessionStorage`). Côté serveur,
l'API garde **l'adresse IP en mémoire** pour limiter le nombre d'appels (`api/limites.py`), Vercel et Render tiennent des
journaux techniques, et les textes de scénario et du chat partent chez OpenAI, aux États-Unis.

| Élément | Niveau | Ce qu'il doit contenir pour Quant Terminal |
|---|---|---|
| **Mentions légales** (`/mentions-legales`) | **O** | Éditeur : les 4 étudiants (personnes physiques). La loi permet à un éditeur **non professionnel** de ne publier que le nom et l'adresse de l'hébergeur, à condition de lui avoir donné son identité. Pour la crédibilité, mieux vaut afficher les noms et un e-mail de contact. Directeur de la publication (ex. Quentin Geldreich). **Hébergeurs** : nom, adresse et téléphone de Vercel Inc. (site ; adresse la plus citée : 440 N Barranca Ave #4133, Covina, CA 91723, USA, à vérifier sur vercel.com) et de Render Services, Inc. (API, San Francisco ; adresse à vérifier sur render.com). Propriété intellectuelle, crédits des photos Wikimedia (déjà affichés), marques citées. Base : LCEN, article 1-1 depuis la loi SREN de 2024 ; sanction jusqu'à 1 an et 75 000 € ([Simonnet Avocat](https://www.simonnetavocat.fr/?p=278538), [Legalplace](https://www.legalplace.fr/guides/mentions-legales/), [Legiscope](https://www.legiscope.com/blog/modele-mentions-legales-site.html)). Si le projet devient commercial : raison sociale, forme, SIREN, siège, TVA. |
| **Politique de confidentialité** (`/confidentialite`) | **O** | Elle est due dès qu'une donnée personnelle est traitée, et l'adresse IP en est une ([service-public.fr F24270](https://entreprendre.service-public.gouv.fr/vosdroits/F24270?profil=tout), [Leto](https://www.leto.legal/guides/creer-une-politique-de-confidentialite-rgpd-regles-a-suivre)). Pour chaque traitement, indiquer la finalité, la base légale, la durée et les destinataires : (1) l'IP pour limiter les appels, en mémoire, effacée après la fenêtre (intérêt légitime : protéger le service) ; (2) les journaux techniques de Vercel et Render ; (3) les textes envoyés à OpenAI, **à ne pas y mettre de données personnelles**, conservés jusqu'à 30 jours par OpenAI pour la lutte contre les abus selon sa politique API ([résumé](https://companyscope.io/vendors/openai)), transfert hors UE encadré par des clauses types ; (4) le stockage local, qui ne quitte jamais l'appareil, sauf les messages du chat au moment de l'envoi. Rappeler les droits (accès, effacement, opposition, plainte à la CNIL) et le contact. |
| **Cookies et traceurs** | **O** : information seulement, pas de bandeau | La CNIL raisonne en « traceurs » : `localStorage` est concerné au même titre qu'un cookie. Sont **exemptés de consentement** les traceurs strictement nécessaires au service demandé par l'utilisateur et ceux qui mémorisent un choix de l'utilisateur ([CNIL, FAQ cookies](https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies/FAQ?lang=en), [Legiscope](https://www.legiscope.com/blog/cookies-traceurs-rgpd-conformite.html)). L'historique, la conversation, le thème et « guide vu » entrent dans ce cas : **pas de bandeau nécessaire**. Il suffit d'un paragraphe « Stockage local » dans la page confidentialité, avec la liste des clés (`qt-theme`, `qt-guide-vu`, historique, conversation) et le moyen de les effacer (les boutons « Effacer » existent déjà). Un outil de mesure d'audience ajouté plus tard devra respecter les conditions d'exemption de la CNIL, sinon il faudra un bandeau. Le statut des outils « sans cookie » comme Vercel Analytics est débattu ([ConsentStack](https://www.consentstack.io/vendors/vercel-analytics)). |
| **Transparence IA** (AI Act, art. 50) | **O** depuis le 2 août 2026 | Toute personne qui discute avec une IA doit en être informée **dans l'interface du chat**, pas seulement par un nom de marque ([guide Article 50](https://artificialintelligenceact.eu/?p=6131), [Jorijn](https://jorijn.com/en/blog/eu-ai-act-website-chatbot-disclosure-august-2026/)). Le panneau s'appelle « Analyste IA », c'est un bon début. Ajouter sous le titre ou au-dessus de la saisie : « Vous échangez avec une IA (modèle OpenAI). Ses réponses peuvent être inexactes et ne sont pas des conseils. » Garder « Analyse de l'IA » sur le texte généré. |
| **Avertissement financier** | **O** en pratique | Le site ne donne pas de recommandation personnalisée, donc pas besoin du statut de conseiller (CIF). Mais l'ESMA rappelle que dire à quelqu'un dans quoi investir peut être qualifié de conseil, même dans un contenu pédagogique ([fiche ESMA-AMF FR](https://esma.europa.eu/sites/default/files/2026-01/FR_France_fr_-_Finfluencers_factsheet.pdf), [AMF](https://www.amf-france.org/fr/actualites-publications/actualites/lesma-et-lamf-publient-lattention-des-finfluenceurs-des-conseils-pour-une-promotion-responsable-sur)). Garder le texte du pied de page, ajouter « simulation hypothétique » sous la valeur estimée, vérifier que le chat refuse les « achète X » personnalisés, éviter « meilleur placement » et « recommandé ». Dans Comparaison, « Le scénario A est le plus favorable » est acceptable : on compare des scénarios, pas des produits. |
| **CGU** (`/conditions`) | **R** | Rien n'oblige à en publier pour un site gratuit sans compte, mais c'est utile : usage pédagogique, pas de garantie sur les données, usage acceptable du chat (pas de données personnelles, pas d'abus), limitation de responsabilité, propriété du code. |
| **Données de marché** | **O si le projet devient commercial** | yfinance n'est pas une API officielle : son auteur la présente « à des fins de recherche et d'éducation » et renvoie aux conditions de Yahoo ([README yfinance](https://cdn.jsdelivr.net/gh/ranaroussi/yfinance@main/README.md), [PyPI](https://pypi.org/project/yfinance/0.2.49)). Pour un projet étudiant, il suffit de citer la source. Pour un produit commercial, il faudra un fournisseur de données sous licence. |
| **Déclaration d'accessibilité** | **B** | L'Acte européen sur l'accessibilité s'applique depuis le 28/06/2025 à certains services (commerce en ligne, banque), et les microentreprises en sont exemptées ([Taylor Wessing](https://www.taylorwessing.com/en/interface/2025/accessibility/key-eu-accessibility-act-exemptions-and-the-challenges-they-pose), [handicap.fr](https://informations.handicap.fr/a-eaa-l-accessibilite-numerique-une-obligation-en-2025-38167.php)). Quant Terminal n'est pas concerné, mais le site est déjà soigné sur ce point (lien « Aller au contenu », rôles ARIA, tableaux de valeurs, réduction des animations) : une page « Accessibilité » qui le dit est un vrai signal de qualité. |

### 2.2 Pages et éléments de confiance

| Élément | Niveau | État actuel | À faire |
|---|---|---|---|
| **Page 404 en français** (`app/not-found.tsx`) | **O** | Page anglaise par défaut de Next.js (vérifié en ligne) | Titre « Cette page n'existe pas », lien vers le simulateur et l'Académie, même en-tête et même pied de page |
| **Page d'erreur** (`app/error.tsx`, `global-error.tsx`) | **R** | Absente (seules des erreurs locales existent) | « Quelque chose s'est mal passé », bouton Réessayer |
| **Méthodologie et sources** (`/methodologie`) | **R** (crédibilité) | Éparpillée entre l'Académie, À propos et le pied de page | Une page : sources (Yahoo, BCE, FRED, OpenAI) avec la date des données ; modèle (volatilités et corrélations réelles, 3 comportements de marché, 1 000 trajectoires) ; calibration ; **bornes de l'IA par actif** (l'anecdote « Or +1 222 891 % » corrigée est un excellent argument) ; limites (loi normale, horizon, IA faillible) ; versions des modèles |
| **FAQ** (`/faq` ou section) | **R** | Absente | 8 à 10 questions : C'est gratuit ? Mes données ? D'où viennent les prix ? Pourquoi 15 s ? L'IA peut-elle se tromper ? C'est un conseil ? Pourquoi le résultat change d'une fois à l'autre ? Puis-je ajouter une action ? Quelle différence avec le backtest ? |
| **Contact** | **R** | Absent | Un e-mail dédié (`contact@…` ou adresse universitaire) et un lien vers les « issues » GitHub si le code est public |
| **Signaux de confiance** | **R** | Équipe et université présentes | Photos ou avatars et liens LinkedIn de l'équipe ; lien vers le code source ; « Données mises à jour le… » ; mention « projet universitaire encadré » (le logo de l'université demande une autorisation) ; nombre de simulations lancées (bonus, demande un compteur côté API) |
| **Image de partage** (Open Graph et Twitter) | **R** | Absente (`/opengraph-image` en 404) | `app/opengraph-image.tsx` (1200×630) : accroche, courbe, logo. Indispensable : le lien sera partagé sur LinkedIn ou Discord au hackathon |
| **Métadonnées** | **R** | Titre et description globaux ; titres de pages au format « X — Quant Terminal » | `metadataBase`, modèle de titre `%s · Quant Terminal`, description par page, `alternates.canonical`, `openGraph.locale: "fr_FR"` ([doc Next.js](https://nextjs.org/docs/app/getting-started/metadata-and-og-images)) |
| **Sitemap et robots** | **R** | 404 tous les deux | `app/sitemap.ts` et `app/robots.ts` ([convention de fichiers](https://nextjs.org/docs/app/api-reference/file-conventions/metadata)) |
| **Icônes et manifeste** | **R** | Seulement `favicon.ico` | `app/icon.svg`, `app/apple-icon.png` (180 px), `app/manifest.ts` (nom, nom court, couleurs, icônes 192 et 512 px dont une version « maskable ») |
| **H1 visible et contenu servi par le serveur** | **R** | H1 masqué (`sr-only`), page d'accueil rendue côté client | Afficher l'accroche en H1 visible, servie par le serveur (meilleur référencement, meilleure première impression) |
| **Données structurées** | **B** | — | JSON-LD `WebApplication` (gratuit, catégorie « Finance », langue fr) |
| **Démo vidéo** | **B** | — | Voir 3.10 |
| **Nouveautés** (changelog) | **B** | `docs/RAPPORT_AVANCEMENT.md` interne | Page « Nouveautés » courte : montre que le projet vit |
| **Version anglaise** | **B** | — | Utile pour un jury international ; Next.js gère l'internationalisation, mais c'est un gros chantier |

### 2.3 Page d'accueil marketing ou outil direct ?

| Option | Pour | Contre |
|---|---|---|
| A. Outil direct en `/` (actuel) | On essaie tout de suite, ce qui est idéal pour une démo | Rien n'explique le produit ; le H1 est masqué ; l'image de partage est vide |
| B. Page marketing en `/`, outil en `/simulateur` | Pitch clair, référencement, captures | Un clic de plus ; tous les liens de partage (`/?s=…`) seraient à rediriger |
| **C. Recommandé : outil en `/` avec un bandeau d'accroche compact** | Garde l'essai immédiat **et** explique le produit | Demande un peu de travail de mise en page |

Option C en pratique : au-dessus des deux colonnes, un bandeau de 120 à 160 px avec le H1 « Et si ça arrivait demain ? »,
une phrase, le bouton **« Essayer avec un exemple »** et les 3 preuves. Le bandeau se replie (sans être retiré) dès qu'un
résultat est affiché. Une vraie page de présentation `/decouvrir` (captures, « Comment ça marche », FAQ, équipe)
pourra venir plus tard. Les sites SaaS de 2026 s'en tiennent à une phrase et une vraie capture du produit, sans vidéo de fond
([SaaSFrame 2026](https://www.saasframe.io/blog/10-saas-landing-page-trends-for-2026-with-real-examples),
[Redefine Web](https://redefineweb.com/blog/best-saas-website-designs-proven-convert-2026/)).

---

## 3. Tendances design et motion 2025-2026

### 3.1 Ce que font les sites qui marchent

- **Linear** : thèmes calculés en **LCH**, ce qui donne une clarté perçue égale d'une teinte à l'autre. Les thèmes partent de 3 variables seulement (base, accent, contraste),
  avec moins de bleu pour un rendu plus neutre. Les titres sont en **Inter Display**, le texte en Inter. La refonte de mars 2026 vise une interface
  « plus calme et plus cohérente » ([Linear, refonte de l'interface](https://linear.app/now/how-we-redesigned-the-linear-ui),
  [« Behind the latest design refresh »](https://linear.app/now/behind-the-latest-design-refresh),
  [changelog du 12/03/2026](https://linear.app/changelog/2026-03-12-ui-refresh)).
- **Vercel (Geist)** : une famille sans empattement et une famille mono, des styles de texte nommés par taille (`label-13`, `copy-14`…),
  des **chiffres tabulaires** pour toutes les valeurs, et la police mono réservée au code ([Geist Typography](https://vercel.com/geist/typography)).
- **Stripe** : une grotesque (Söhne) en graisse légère (300) pour les grands titres. Le dégradé maillé est animé très lentement
  et seulement dans le haut de page. Les animations des cartes sont subtiles et volontaires
  ([Lee Robinson, « How Stripe designs beautiful websites »](https://archive.leerob.io/blog/how-stripe-designs-beautiful-websites)).
- **Raycast** : fond presque noir légèrement bleuté, **un accent rare** (le rouge sert de ponctuation, sans dominer),
  bordures blanches à 6-10 % d'opacité, lueur chaude très faible ([analyse de son système de design, non officielle](https://open-design.ai/systems/raycast/)).
- **Mercury** : sombre d'abord, polices maison (Arcadia et Arcadia Display) en graisses intermédiaires (420 à 480), accent indigo
  ([analyse Blake Crosley](https://blakecrosley.com/de/guides/design/mercury), [Instrument](https://www.instrument.com/work/mercury)).
- **Tendance générale 2026** : une phrase et une vraie capture du produit dans le haut de page, beaucoup de blanc, des démos réelles
  plutôt que des illustrations ([SaaSFrame](https://www.saasframe.io/blog/10-saas-landing-page-trends-for-2026-with-real-examples),
  [Merge](https://merge.rocks/blog/best-saas-websites-2026-when-it-comes-to-design-and-what-to-copy)).

**Bilan pour Quant Terminal** : la palette (neutres + indigo `#5b5fe3`), Inter, `tabular-nums`, le thème sombre et les
jetons de couleur vont déjà dans ce sens. **Il ne manque pas de style : il manque de la retenue et de la régularité.**

### 3.2 Typographie : règles concrètes

| Rôle | Taille / interligne | Graisse | Remarques |
|---|---|---|---|
| Chiffre héros (valeur estimée) | 48 à 60 px / 1 | 600 | `tabular-nums`, interlettrage −0,02 em |
| H1 de page | 32 à 40 px / 1,15 | 600 | Interlettrage −0,02 em ; Inter Display possible (`opsz` d'Inter Variable) |
| Titre de section | 20 px / 1,3 | 600 | Une seule taille pour toutes les sections |
| Titre de carte | 15 px / 1,4 | 600 | Taille déjà utilisée : la garder |
| Texte courant | 14 à 15 px / 1,6 | 400 | 60 à 75 caractères par ligne au maximum |
| Libellé ou aide | 13 px / 1,45 | 400-500 | Couleur `muted` |
| Minimum absolu | **12 px** | 500 | **Jamais 10 ou 11 px** (aujourd'hui 12 occurrences) |

- Une seule famille (Inter), 3 graisses (400, 500, 600). Les majuscules espacées (« 1 · VOTRE SCÉNARIO ») sont à garder pour **un seul**
  niveau de libellé, pas plus.
- `font-variant-numeric: tabular-nums` sur **tous** les nombres qui changent ou s'alignent (déjà bien fait).
- La police mono est réservée aux tickers que l'utilisateur tape lui-même et au code de l'Académie.

### 3.3 Espacement

- Grille de 4 px. Écarts autorisés : 4, 8, 12, 16, 24, 32, 48, 64.
- **Une marge intérieure de carte** : 24 px sur ordinateur, 16 px sur mobile, et 32 px pour la carte héros seulement.
- Entre deux cartes d'une même section, 16 px ; entre deux sections, 32 à 48 px, pour que les groupes se voient.
- Un écran = une idée. Ne pas empiler plus de 4 ou 5 cartes sans repère (onglets, sommaire collant ou titre de section).

### 3.4 Couleurs

- **Un accent** (indigo), réservé à l'action principale, à la sélection et au focus. Un bouton secondaire ne doit pas être indigo.
- **Le vert et le rouge sont réservés à la performance.** Un statut (« Prix réels », « Total 100 % », « Fiabilité élevée ») passe en neutre
  ou en accent : sinon l'œil lit « gain » là où il n'y en a pas.
- Fonds sombres : presque noir, jamais `#000` (c'est le cas). Bordures à faible contraste, peu d'ombres (c'est le cas).
- Jamais de couleur hexadécimale écrite en dur (règle de CLAUDE.md) : `Repartition.tsx` et `Equipe.tsx` l'enfreignent aujourd'hui.

### 3.5 Micro-interactions

| Interaction | Règle | Durée |
|---|---|---|
| Survol d'un élément **cliquable** | Changement de couleur, de fond ou de bordure. Pas de déplacement | 120 à 150 ms |
| Survol d'un élément **non cliquable** | **Rien** (une carte qui se soulève fait croire qu'elle est cliquable) | — |
| Appui sur un bouton | Échelle 0,97 à 0,98, sur les boutons seulement | 100 à 160 ms |
| Interrupteur, onglet, segment | Ressort vif (rigidité ≈ 400, amortissement ≈ 30-35) : le réglage `RESSORT` actuel est bon | ≈ 200 ms |
| Copier, télécharger | L'icône devient une coche puis revient (déjà fait : `CocheAnimee`) | 1,5 à 2,2 s de confirmation |
| Focus clavier | Contour visible, **pas d'animation** des actions faites au clavier | 0 |

Sources : règles d'Emil Kowalski (animations d'interface **sous 300 ms**, accélération en sortie par défaut, pas d'animation des
actions au clavier ; [compétence « emil-design-eng »](https://tessl.io/registry/skills/github/emilkowalski/skill/emil-design-eng),
[résumé](https://skills.cat/skills/mrmps/smry/emilkowal-animations)) et Rauno Freiberg, sur les détails invisibles et la prévisibilité des gestes
([« Invisible Details of Interaction Design »](https://rauno.me/craft/interaction-design)).

### 3.6 Transitions : durées et courbes

| Type | Durée | Courbe |
|---|---|---|
| Retour visuel immédiat (appui, coche) | 100 à 160 ms | sortie douce |
| Infobulle, petit menu | 150 à 200 ms | sortie douce |
| Fenêtre, feuille mobile, panneau | 200 à 300 ms (sortie ≈ 70 % de l'entrée) | ressort ou sortie douce |
| Changement de page | 150 à 200 ms, fondu seul, **ou rien** | sortie douce |
| Apparition d'un bloc au défilement | 250 à 400 ms, décalage de 8 px, **sans flou** | sortie douce |
| Tracé de graphique, remplissage de barres | 600 à 1 000 ms, **une seule fois** | sortie douce |

- Courbe de sortie douce : `cubic-bezier(0.22, 1, 0.36, 1)`, déjà dans `EASE_SORTIE`. Pour un déplacement sur l'écran :
  `cubic-bezier(0.2, 0, 0, 1)` (style Material « emphasized » ; les valeurs varient selon les versions,
  [voir](https://docs.rs/crate/bevy_material_ui/latest/source/src/motion.rs)). **Jamais d'accélération en entrée (`ease-in`)** pour un élément qui arrive.
- Proposition pour `motion/transitions.ts` : `DUREE = { rapide: 0.15, normale: 0.25, lente: 0.45 }`, et `DUREE.donnees = 0.8`
  pour les graphiques.

### 3.7 Nombres animés

- **Un seul compteur par écran** : le chiffre héros, en 0,8 à 1,2 s, depuis le capital de départ (déjà bien fait dans `Synthese`).
- Les autres chiffres apparaissent en fondu, **sans compter**. Onze compteurs en même temps donnent un effet machine à sous.
- Quand une valeur **change** (passage d'un scénario à l'autre), un défilement des chiffres façon compteur kilométrique
  (bibliothèque [NumberFlow](https://github.com/barvian/number-flow), qui respecte la réduction des animations) fait plus « produit »
  qu'un comptage depuis zéro.
- Jamais de nombre animé dans un tableau. Chiffres tabulaires obligatoires, sinon le texte tremble pendant l'animation.

### 3.8 Défilement

- Apparition au défilement **une seule fois** (`once: true`, déjà fait), avec un petit décalage, et sans flou sur les longs blocs de texte.
- Pas de parallaxe ni de défilement détourné. Le défilement doux (`scroll-behavior: smooth`) est déjà désactivé si l'utilisateur réduit les animations.
- Sur une page longue (les résultats), un **sommaire collant** ou des onglets valent mieux que des animations de plus.

### 3.9 Ce qui fait propre, ce qui fait amateur

| Fait propre | Fait amateur |
|---|---|
| Libellés courts, valeurs fortes | Une phrase d'aide sous chaque titre |
| Une seule échelle de tailles, de rayons et de marges | 18 tailles de texte, des marges de carte de 20 à 32 px |
| Noms d'actifs humains (« Or », « Obligations d'État françaises ») | Codes techniques (`GC=F`, `IFRB.AS`, « dans le profil ») |
| Vert et rouge réservés aux gains et aux pertes | Une pastille verte pour « Prix réels » |
| Animation au service d'un changement d'état | Logo qui tourne, cartes qui sautent, boucles infinies |
| Icônes d'une seule famille (Lucide) | Mélange d'icônes et de symboles texte (▲ ▼ ● ✓ ↻) |
| Pied de page fait de liens | Colonnes de texte non cliquable qui ressemblent à des liens |
| Page 404 et pages légales soignées | Page 404 anglaise par défaut |
| Infobulles maison discrètes, ou aucune | Infobulles natives du navigateur (`title=`, 17 occurrences) |
| Ton constant (sobre partout) | « Duel » et « Tournoi » avec couronne à côté de « VaR 95 % » |

### 3.10 Vidéo de présentation (YouTube, TikTok, Instagram)

Ce qui marche en 2026, d'après une analyse de 100 vidéos d'animation d'interface ([ADVIDS](https://advids.co/blog/ui-animation-motion-design-trends)) et des revues de démos
([Vidpros](https://vidpros.com/best-product-demo-videos/), [Superside](https://www.superside.com/blog/saas-video-examples)) :
- **De vraies captures d'écran** plutôt que des animations dessinées (les captures sont devenues majoritaires en 2026).
- **Zoom qui suit le curseur**, coins arrondis, ombre et fond, à la manière de Screen Studio
  ([description](https://www.contentbeta.com/blog/best-product-demo-video-examples/)).
- Format court : **15 à 30 s** pour le teaser, la version longue (60 à 90 s) va sur YouTube ou sur la page.
- **Texte animé à l'écran** : la plupart des vidéos courtes sont regardées sans le son. Sous-titres incrustés.
- Le ton change selon la plateforme : Reels tolère le léché, Shorts veut de la vitesse, TikTok préfère le brut.

**Scénario de 30 s en vertical (9:16) pour Quant Terminal :**

| Temps | Image | Texte à l'écran |
|---|---|---|
| 0 à 2 s | On tape dans le champ du scénario (zoom) | « Et si la Chine bloquait Taïwan demain ? » |
| 2 à 5 s | Clic sur la puce, puis sur « Lancer » | « 10 000 € investis. Que se passe-t-il ? » |
| 5 à 8 s | Étapes d'attente en accéléré ×4 | « L'IA cherche des crises comparables… » |
| 8 à 14 s | Le chiffre héros compte de 10 000 € vers la valeur finale | La valeur finale et sa variation |
| 14 à 20 s | Courbe et bande Monte-Carlo ; le curseur parcourt la courbe | « 1 000 futurs possibles » |
| 20 à 26 s | Coupe sur le duel de scénarios ou le backtest 2008 | « Comparez. Rejouez 2008. » |
| 26 à 30 s | Logo et adresse du site | « Gratuit · projet étudiant · quant-terminal… » |

Conseils de tournage : fenêtre de 1440×900 à densité ×2, barre du navigateur masquée, données propres (scénario soigné,
capital rond), thème sombre (qui rend mieux en vidéo), bulle de chat masquée pendant la capture, curseur agrandi, musique à 100-120 BPM
avec des coupes sur le temps. Sans Mac, Screen Studio n'est pas disponible : enregistrer avec OBS, puis faire les zooms dans CapCut ou DaVinci Resolve.

---

## 4. Audit de Quant Terminal (code `web/src/`)

Mesures relevées dans le code : **18 tailles de texte** (`text-xs` à `text-6xl` et 8 tailles arbitraires : 10, 11, 13, 15, 17, 22, 28,
32 px) · **7 rayons** (`rounded` 4 px, `sm`, `md`, `lg`, `xl`, `2xl`, `full`) · **6 marges intérieures de cartes** (`p-5`, `p-6`,
`p-6 sm:p-7`, `p-7`, `p-8`, `px-6 py-12`) · **11 titres de carte et 6 interrupteurs avec une phrase d'aide** · **31 effets au survol (`whileHover`)** · **17 infobulles natives (`title=`)**
· symboles ▲ ▼ dans **11 fichiers** · **5 animations infinies**.

### 4.1 Sélecteur d'actifs (`components/formulaire/SelecteurActifs.tsx`), la plainte n° 1

| # | Constat | Pourquoi ça fait amateur | Correction |
|---|---|---|---|
| A1 | **Sous-titre = ticker Yahoo brut en police mono** (l. 181) : `^GSPC`, `^NDX`, `GC=F`, `CL=F`, `EURUSD=X`, `DX-Y.NYB`, `IS0L.DE`, `IFRB.AS`, `1482.T`, `IGLT.L`… | Incompréhensible pour un débutant, et parfois **trompeur** : « OAT France 10Y » affiche `IFRB.AS` (un fonds coté à Amsterdam), « U.S. Treasury 10Y » affiche `IEF` (un ETF à 7-10 ans), « MSCI World » affiche `URTH`. La police mono ajoute du bruit. | Remplacer par **une ligne de description en français** (tableau ci-dessous). N'afficher le ticker que pour les **actifs personnalisés** (l'utilisateur l'a tapé), ou au survol dans un détail. Ajouter dans `config.py` un dictionnaire `PRESENTATION_ACTIFS = {cle: {"nom_court", "description"}}` exposé par `api/services.catalogue()`. On garde `nom` tel quel pour Streamlit et le PDF (non-régression). |
| A2 | **Badge « dans le profil »** en 10 px sur fond gris (l. 182) | Jargon interne, trop petit (c'est la seule taille de 10 px du site), on dirait une étiquette de débogage | Afficher à droite **la part du profil** (« 25 % ») en accent, ou un point accent avec une légende unique en tête de fenêtre : « ● = dans votre profil ». |
| A3 | **Noms hétérogènes** (`config.py`, l. 12-48) : « S&P 500 (USA) », « Or (Gold Spot, $/oz) », « Pétrole WTI (Crude Oil) », « Cuivre (Copper Futures) », « VIX (CBOE Volatility Index) », « U.S. Treasury 10Y », « Gilt Royaume-Uni 10Y » | Mélange de français et d'anglais, parenthèses partout, unités de cotation dans le nom | Nom court en français + description (tableau ci-dessous). Utiliser le **même nom court partout** : étiquettes, résultats, tableaux, graphiques (voir R9). |
| A4 | **Prix sans unité** (l. 187) : « 73 312 », « 1,1169 », « 2 650 » | On ne sait pas si c'est en $, en € ou en points | Ajouter l'unité en petit (`$`, `€`, `pts`), à partir de `devise`, déjà dans le catalogue. Écrire une fois en tête de liste « Cours de clôture · variation du jour ». |
| A5 | Catégories : « Matières Premières » (majuscule à l'anglaise), « Devises & Volatilité » (deux choses différentes), « Sectoriels » (un seul actif), « Obligations d'État (10 ans) » (alors que certains supports ne sont pas à 10 ans) | Incohérences visibles dans les filtres | « Actions », « Obligations d'État », « Matières premières », « Devises », « Volatilité », « Thématiques » (Défense, Terres rares), « Cryptomonnaies ». |
| A6 | Bloc « Ajouter n'importe quelle action… » (l. 267-268) : deux lignes, cinq exemples de tickers, « calibrés sur un an » | Texte technique et long dans la fenêtre | « Une action, un ETF ou une crypto absent de la liste ? » + champ « Ticker Yahoo (ex. TSLA, MC.PA) ». Le reste va dans l'infobulle ou la FAQ. Plus tard : recherche par nom. |
| A7 | Grille à deux colonnes avec des noms coupés (`truncate`) | Les noms longs (« ETF Aérospatiale & Défense (ITA) ») sont tronqués | Les noms courts du tableau tiennent sur une ligne. |

**Noms et descriptions proposés** (à faire relire par l'équipe) :

| Clé | Nom actuel | Nom court proposé | Description (sous-titre) |
|---|---|---|---|
| `S&P 500` | S&P 500 (USA) | S&P 500 | 500 grandes entreprises américaines |
| `NASDAQ` | NASDAQ 100 (Tech US) | Nasdaq 100 | Les géants de la tech américaine |
| `CAC 40` | CAC 40 (France) | CAC 40 | 40 grandes entreprises françaises |
| `MSCI_World` | MSCI World (Global) | Actions monde | Grandes entreprises des pays développés |
| `Emerging_Markets` | MSCI Emerging Markets | Pays émergents | Chine, Inde, Taïwan, Brésil… |
| `Bons_Tresor_US_10Y` | U.S. Treasury 10Y | Emprunts d'État américains | Prêter à l'État américain |
| `Bund_10Y` | Bund Allemagne 10Y | Emprunts d'État allemands | La valeur refuge de la zone euro |
| `OAT_10Y` | OAT France 10Y | Emprunts d'État français | Les OAT, la dette de la France |
| `JGB_10Y` | JGB Japon 10Y | Emprunts d'État japonais | Taux parmi les plus bas du monde |
| `Gilt_10Y` | Gilt Royaume-Uni 10Y | Emprunts d'État britanniques | Les « gilts » du Trésor britannique |
| `EUR_USD` | EUR/USD (Euro-Dollar) | Euro / dollar | Combien de dollars vaut 1 € |
| `Dollar_Index` | DXY (US Dollar Index) | Indice du dollar | Le dollar face à 6 grandes devises |
| `VIX` | VIX (CBOE Volatility Index) | Indice de la peur (VIX) | Nervosité attendue sur le S&P 500 |
| `Or` | Or (Gold Spot, $/oz) | Or | Valeur refuge, en dollars l'once |
| `Argent` | Argent (Silver Spot, $/oz) | Argent | Métal précieux et industriel |
| `Petrole` | Pétrole WTI (Crude Oil) | Pétrole | Baril de brut américain (WTI) |
| `Cuivre` | Cuivre (Copper Futures) | Cuivre | Thermomètre de l'industrie mondiale |
| `ETF_Terres_Rares` | ETF Terres Rares (REMX) | Terres rares | Métaux des batteries et des aimants |
| `ETF_Defense` | ETF Aérospatiale & Défense (ITA) | Défense et aéronautique | Industriels américains de la défense |
| `Bitcoin` | Bitcoin (BTC) | Bitcoin | La première cryptomonnaie |
| `Ethereum` | Ethereum (ETH) | Ethereum | Crypto des applications décentralisées |
| `XRP` | XRP (Ripple) | XRP | Crypto des paiements internationaux |
| `Solana` | Solana (SOL) | Solana | Blockchain rapide et peu chère |

### 4.2 Choix du portefeuille (`components/formulaire/ChoixPortefeuille.tsx`)

| # | Constat | Correction |
|---|---|---|
| P1 | Note de 11 px : « Les étiquettes sans pourcentage ne font pas partie du profil : elles sont analysées à titre de comparaison. » (l. 266-268). Le concept est difficile et l'explication est petite. | **Deux groupes titrés** : « Investis » (étiquettes en accent avec %) et « Suivis, sans investissement » (étiquettes neutres, « 0 % » en gris). La phrase devient inutile ; garder une infobulle (i) sur le second titre. |
| P2 | Deux styles d'étiquettes mélangés dans la même ligne (accent et neutre) + infobulles natives (l. 247-248) | Réglé par P1 ; supprimer `title=` ou passer à une infobulle maison. |
| P3 | Profils : 4 descriptions de 12 px (l. 24-29) | Remplacer la phrase par une **mini-barre de répartition** à 3 ou 4 couleurs (actions, obligations, or, crypto), à partir de `profil.poids`. Plus visuel et sans texte. Garder la phrase en `aria-label` et dans l'infobulle. |
| P4 | Capital en `type="number"` (l. 88-97) : affichage « 10000 » sans espace, petites flèches du navigateur | Champ texte formaté « 10 000 », `inputMode="numeric"`, et 3 puces rapides : 1 000 € · 10 000 € · 100 000 €. |
| P5 | Le bouton « Choisir les actifs » en fond accent (l. 183-191) concurrence le bouton principal « Lancer » | Bouton secondaire (bordure neutre) libellé « Modifier ». |
| P6 | « Total : 100 % ✓ » / « (doit faire 100 %) » (l. 226-227) : symbole texte, couleur verte pour un statut | Petite barre qui se remplit jusqu'à 100 %, en accent ; le message d'erreur reste. Icône Lucide à la place de « ✓ ». |
| P7 | Le compteur « Actifs · 8 » s'anime à chaque changement (l. 178) | Pas besoin d'animer : un nombre statique suffit. |

### 4.3 Formulaire de simulation (`components/FormulaireSimulation.tsx`)

| # | Constat | Correction |
|---|---|---|
| F1 | **Trop de textes d'aide** : « Comparer plusieurs scénarios » (l. 104-106), la phrase sous le champ (l. 190-194), une aide sous chacun des 4 interrupteurs (l. 280-288), la description du modèle (l. 273-277) | Garder la phrase sous le champ (elle est utile) ; mettre les aides des options en infobulle (i) ou les garder dans le panneau replié, mais en 1 ligne de 13 px. |
| F2 | Le sélecteur « 1 · 2 · 3 » ne se comprend pas tout de suite (on peut choisir « 1 » à côté de « Comparer plusieurs scénarios ») | Libellé « Nombre de scénarios », ou mieux : un lien « + Comparer avec un autre scénario » sous le champ (le bouton d'ajout existe déjà à partir de 2 scénarios). |
| F3 | Titres « 1 · VOTRE SCÉNARIO » en majuscules, et « 3 · Options avancées » est un bouton **stylé comme un titre** (l. 228-230) | Titres de section en minuscules, 14 px, graisse 600, couleur `ink`. Les options deviennent une ligne repliable distincte (icône réglages + chevron, bordure en haut). |
| F4 | 8 puces sur 3 lignes, titres irréguliers (« Hausse brutale FED », « Krach 2008 bis », « Révolution IA ») | 4 puces visibles + « Plus d'idées » ; titres réguliers : « Guerre mondiale », « Pandémie », « Percée de l'IA », « Krach bancaire », « Fusion nucléaire », « Choc pétrolier », « Hausse des taux de la Fed », « Blocus de Taïwan ». |
| F5 | Fautes dans les textes par défaut (`config.py`) : « geopolitique » sans accent (l. 90), « FED », « +2% » et « 30% » sans espace (l. 79-80) | Corriger : « géopolitique », « la Fed », « +2 % », « 30 % ». |
| F6 | « Horizon : 100 jours de bourse » | Ajouter l'équivalence : « 100 jours de bourse · ≈ 5 mois ». |
| F7 | Le modèle est un `<select>` natif au milieu de contrôles maison (l. 266) ; « Machine » est obscur | Trois cartes radio comme les profils : « Classique », « Crises réelles », « Emballement ». La description reste en dessous. |
| F8 | La barre collante du bouton utilise des marges négatives (`-mx-5 -mb-5`, l. 296) liées à la marge de la carte | À reprendre une fois la marge des cartes unifiée (G3), sinon ça cassera. |

### 4.4 Résultats (`components/Resultats.tsx` et `components/resultats/*`)

| # | Constat | Correction |
|---|---|---|
| R1 | **Ordre** : Synthèse → Analyse de l'IA (long texte) → Graphique (`Resultats.tsx`, l. 188-196). Le visuel le plus parlant arrive en troisième. | Synthèse → **Évolution (graphique)** → Analyse de l'IA → Risque → Répartition → Détail → Exports. |
| R2 | **Page très longue** (11 blocs empilés) | Sommaire collant (« Vue d'ensemble · Risque · Détail · Méthode · Exporter »), ou onglets dans les résultats. |
| R3 | **Phrase d'aide sous 11 titres de carte**, en `text-sm` et `ink-2`, soit la même taille que le texte courant (`ui/Carte.tsx`, l. 11) | Supprimer celles que le titre suffit à expliquer (« Répartition du portefeuille », « Détail du portefeuille », « Exporter et partager ») ; pour les autres, passer en 13 px `muted` sur une ligne, ou en infobulle (i) avec un lien vers l'Académie (`LienAcademie` existe). |
| R4 | **Pastilles techniques dans la carte héros** (`Synthese.tsx`, l. 70-73) : « ● Prix réels » (puce texte, en **vert**), « Calibré sur : … », « Converti en € », « Monte-Carlo · 1 000 trajectoires » | Une seule ligne discrète sous la valeur : « Simulation hypothétique · cours du 12/11 · en euros · 1 000 trajectoires », et l'événement de calibration dans la carte IA. Plus de vert pour un statut. |
| R5 | **11 nombres qui comptent en même temps** : 4 dans la Synthèse, 3 cartes finales (`Resultats.tsx`, l. 60) et 4 tuiles de risque | Seul le chiffre héros compte ; les autres apparaissent en fondu (3.7). |
| R6 | **Cartes non cliquables qui se soulèvent au survol** : tuiles de risque (`Risque.tsx`, l. 40), cartes de scénario de la comparaison (`Comparaison.tsx`, l. 64 ; seul « Voir le détail » est cliquable) | Retirer le soulèvement. Dans la comparaison, rendre **toute la carte** cliquable vers le détail et garder un survol discret (bordure). |
| R7 | **▲ ▼ en plus du signe « + / − »** dans 11 fichiers, et des symboles texte à côté des icônes Lucide | Signe et couleur suffisent (pas d'information par la seule couleur, grâce au signe). Garder une seule icône Lucide (`TrendingUp` ou `TrendingDown`) dans le badge du chiffre héros. |
| R8 | **Deux styles de titres de section** : « Le risque de ce portefeuille » (`Resultats.tsx`, l. 199) et « Évolution par classe d'actifs » (`CourbesCategories.tsx`, l. 40) sont des h3 de 15 px **hors carte**, alors que les autres titres sont dans des cartes | Un seul modèle : titre de section de 20 px au-dessus d'un groupe de cartes, titre de carte de 15 px à l'intérieur. |
| R9 | **Noms d'actifs longs dans les résultats** (« Or (Gold Spot, $/oz) » dans Performance par actif, Détail, Calibrée ou libre ?), alors que les étiquettes du formulaire utilisent la forme courte | Nom court partout (A3). |
| R10 | **« Calibrée ou libre ? »** (`AnalyseIA.tsx`, l. 36-94) : 2 paragraphes, 2 encadrés, un tableau et une note : dense et réservé aux experts | Repliable « Comment l'IA a calibré son estimation », fermé par défaut. Garder visibles la pastille de fiabilité et les précédents historiques. |
| R11 | **Tuiles de risque** : pastille + valeur + 2 lignes d'explication, et une phrase de plus pour le Sharpe (`Risque.tsx`, l. 54-57) | Une ligne courte (≤ 60 caractères) + l'échelle à 4 crans façon Stockopedia ; la phrase complète en infobulle ou dans l'Académie. |
| R12 | Couleurs écrites en dur `#fff` et `#0b0b0b` (`Repartition.tsx`, l. 11) et dégradé `#4338ca` → `#6366f1` (`apropos/Equipe.tsx`, l. 29) | Jetons `--on-series-1…5` et `--accent` dans `globals.css`. |
| R13 | Avertissement en bas des résultats (l. 239-241) **et** encadré orange dans le pied de page | Garder une ligne courte près du résultat (« Simulation hypothétique, pas un conseil »), le texte complet dans le pied de page et dans les mentions. |
| R14 | Ton de la comparaison : « Duel » et « Tournoi », couronne, étoiles (`Comparaison.tsx`, l. 51, 71, 159) | Choisir un ton. Pour la crédibilité : « Comparaison de 2 scénarios », « 1er », sans couronne ; l'étoile « meilleure valeur » peut rester. |
| R15 | Pas de **temps de récupération** sur la perte maximale | Ajouter « Retour au capital : jour N / pas sur l'horizon », calculé à partir de `portefeuille.valeurs` (idée de PortfoliosLab). |

### 4.5 En-tête (`components/EnTete.tsx`)

| # | Constat | Correction |
|---|---|---|
| H1 | Le logo tourne et grossit au survol (l. 66) | Retirer : un logo ne bouge pas. |
| H2 | Logo en PNG de 28 px | Version SVG nette (et réutilisable pour l'icône du site et l'image de partage). |
| H3 | En-tête **et** bandeau des cours collants sur ordinateur (`app/layout.tsx`, l. 39), soit environ 100 px pris en haut ; la colonne du formulaire doit compenser (`Simulateur.tsx`, l. 389 : `top-[7.75rem]`) | Seul l'en-tête reste collant ; le bandeau défile avec la page. On gagne de la hauteur pour le formulaire. |
| H4 | Le bouton thème tourne de 20° à l'appui | Acceptable ; un fondu entre lune et soleil suffit. |

### 4.6 Bandeau des marchés (`components/BandeMarches.tsx`)

| # | Constat | Correction |
|---|---|---|
| B1 | Prix sans unité (l. 39) | Unité en petit (pts, $, €) ; « EUR/USD 1,1169 » se passe d'unité. |
| B2 | Défilement continu sur 45 s, même quand tout tient à l'écran | Sur grand écran (≥ 1280 px), les 7 cours tiennent : affichage fixe. Le défilement seulement si ça déborde. La pause au survol est déjà bien faite. |
| B3 | La date « Clôture du … » est cachée sur mobile | Petite pastille « 12/11 » à gauche, toujours visible. |

### 4.7 Pied de page (`components/PiedDePage.tsx`)

| # | Constat | Correction |
|---|---|---|
| Pi1 | **5 colonnes de texte non cliquable** qui ressemblent à des liens (l. 3-9) | De vrais liens : Produit (Simulateur, Backtest, Historique, Académie), Ressources (Méthodologie, FAQ, Lexique), Projet (À propos, Code source, Contact), Légal (Mentions légales, Confidentialité, Conditions). |
| Pi2 | La colonne « Mentions » ne contient pas les mentions légales | Voir 2.1. |
| Pi3 | La liste de l'équipe est dans le pied de page | Elle va dans À propos (elle y est déjà) ; en bas de page : « © 2026 Quant Terminal · Projet étudiant, Université Paris Nanterre ». |
| Pi4 | Encadré d'avertissement orange (l. 27-32) : lourd sur chaque page | Texte neutre en 13 px, même contenu, avec un lien « En savoir plus » vers les mentions. |
| Pi5 | « Monte-Carlo (1 000 trajectoires) » et « 23 actifs · 6 catégories » écrits en dur | Les lire dans le catalogue ou `config.py` (règle « pas de nombres magiques »). |

### 4.8 Système visuel (`app/globals.css`, `motion/*`, `ui/Carte.tsx`)

| # | Constat | Correction |
|---|---|---|
| G1 | Pas d'échelle typographique : 18 tailles, dont 8 arbitraires | Définir dans `@theme` : `--text-xs: 12px`, `--text-sm: 13px`, `--text-base: 14px`, `--text-md: 15px`, `--text-lg: 20px`, `--text-xl: 24px`, `--text-2xl: 32px`, `--text-hero: 56px`, puis remplacer les `text-[11px]`, `text-[13px]`… |
| G2 | Rayons des boutons au hasard : bouton principal `xl`, « Choisir les actifs » `lg`, Annuler et Valider `xl`, Réessayer `lg`, en-tête `lg` | Jetons : `--radius-controle: 8px` (boutons, champs), `--radius-tuile: 12px`, `--radius-carte: 16px`, `full` pour les puces. |
| G3 | Marges intérieures de cartes : `p-5`, `p-6`, `sm:p-7`, `p-7`, `p-8` | `Carte` prend un réglage `taille="normale" \| "hero"` (24 ou 32 px) et 16 px sur mobile. |
| G4 | `Apparition` : flou de 4 px, 12 px de décalage, 0,6 s sur chaque bloc (`motion/Apparition.tsx`, l. 17-20) | Sans flou (coûteux et lent sur les grands blocs), 8 px, 0,3 à 0,4 s. |
| G5 | Changement de page : glissement + fondu de 0,35 s rejoué à chaque navigation (`app/template.tsx`) | Fondu seul de 0,15 à 0,2 s, ou rien. |
| G6 | L'illustration de l'accueil tourne en boucle infinie (`Simulateur.tsx`, l. 116, 126, 137) | La jouer une fois puis la laisser au repos, ou la relancer toutes les 8 à 10 s au minimum. |
| G7 | 17 infobulles natives `title=` | Composant `Infobulle` (accessible au clavier) ou rien. |
| G8 | Symboles texte utilisés comme icônes : ● ✓ ▲ ▼ et ↻ (dans le guide) | Icônes Lucide partout (`Circle`, `Check`, `TrendingUp`, `RotateCw`). |

### 4.9 Parcours général

| # | Constat | Correction |
|---|---|---|
| U1 | **Le guide s'ouvre tout seul** à la première visite (`Guide.tsx`, l. 68-72) : une fenêtre devant le jury, alors que l'écran vide explique déjà les 3 étapes | Ne plus l'ouvrir automatiquement ; bouton « Visite guidée » dans l'écran vide, et le bouton ? reste dans l'en-tête. |
| U2 | **Réveil de l'API** : la première visite peut afficher « Le serveur se réveille peut-être » (`Simulateur.tsx`, l. 374). Le plan gratuit de Render s'endort après 15 min et met 30 à 60 s à repartir ([communauté Render](https://community.render.com/t/cold-boot-start-of-the-server-for-first-request/15911)) | (1) Ping toutes les 10 à 14 min pendant le hackathon (tâche planifiée ou service de surveillance gratuit) ; (2) à la place de l'erreur, un écran d'attente honnête : « Démarrage du serveur (≈ 30 s)… » avec relance automatique. |
| U3 | Aucune démo instantanée | Bouton **« Essayer avec un exemple »** : charge un résultat pré-calculé (fichier JSON dans `web/public/`), affiché tout de suite, avec la mention « exemple pré-calculé » et un bouton « Relancer en direct ». |
| U4 | H1 masqué et accroche cachée dans l'écran vide | Accroche en H1 visible (2.3, option C). |
| U5 | 404 en anglais | `app/not-found.tsx` (2.2). |

---

## 5. Recommandations priorisées (les 15 changements les plus rentables)

Effort : **S** = moins de 2 h · **M** = une demi-journée à une journée · **L** = 2 jours ou plus. Impact : ★ à ★★★.

| # | Type | Quoi | Pourquoi | Effort | Impact |
|---|---|---|---|---|---|
| 1 | Contenu | **Remplacer les tickers par une description française** et unifier les **noms courts** des 23 actifs (`PRESENTATION_ACTIFS` dans `config.py`, exposé par le catalogue, utilisé partout sur le site) | C'est la plainte n° 1 et ce qui saute aux yeux en premier ; ça corrige aussi des tickers trompeurs | M | ★★★ |
| 2 | Visuel | Retirer le badge « dans le profil » et la note de 11 px ; grouper les étiquettes en « Investis » et « Suivis » | Supprime deux textes de moins de 12 px et clarifie un concept confus | S | ★★★ |
| 3 | Page | **Mentions légales + Confidentialité** (stockage local compris) + liens dans le pied de page | **Obligatoire** (LCEN, RGPD) ; un jury ou un partenaire les cherche | S | ★★★ |
| 4 | Fonction | **Démo en un clic** (résultat pré-calculé) + **ping anti-veille** de l'API + écran « démarrage du serveur » | Évite l'attente et l'erreur devant le jury ; montre le produit en 2 s | M | ★★★ |
| 5 | Visuel | **Jetons de taille, de rayon et de marge** (G1-G3) et suppression des tailles de 10 et 11 px | Régularité visuelle partout, base de tout le reste | M | ★★★ |
| 6 | Visuel | Résultats : **graphique juste après la synthèse**, aides de cartes allégées (R3), pastilles techniques réduites à une ligne (R4), « Calibrée ou libre ? » repliable | La page la plus regardée devient lisible d'un coup d'œil | M | ★★★ |
| 7 | Visuel | **Motion plus sobre** : un seul compteur, plus de soulèvement sur les cartes non cliquables, `Apparition` sans flou et plus courte, illustration non infinie, logo fixe, transition de page plus courte | Fait passer le site d'« effets » à « produit » ; peu de code à changer | S | ★★ |
| 8 | Page | **`/methodologie`** : sources et dates, modèle, calibration, bornes de l'IA, limites | Principal signal de confiance pour un outil qui utilise une IA | M | ★★★ |
| 9 | Contenu | **Mention IA dans le chat** (AI Act art. 50) + « simulation hypothétique » sous la valeur + avertissement harmonisé | Obligation depuis le 02/08/2026 ; c'est aussi un signal de sérieux | S | ★★ |
| 10 | Page | **404 et page d'erreur en français** | La 404 anglaise par défaut est l'indice d'amateurisme le plus facile à corriger | S | ★★ |
| 11 | Page | **Référencement et partage** : `metadataBase`, modèle de titre, image Open Graph dynamique, `sitemap.ts`, `robots.ts`, `manifest.ts`, icônes SVG et Apple | Le lien partagé au hackathon affichera une belle carte | S | ★★ |
| 12 | Page | **Accueil option C** : H1 visible « Et si ça arrivait demain ? », une phrase, 3 preuves, bouton exemple, bandeau qui se replie après un résultat | Explique la proposition de valeur en 5 s sans ajouter de clic | M | ★★★ |
| 13 | Visuel | **Pied de page en vrais liens** + FAQ (8-10 questions) + contact | Fini les colonnes de faux liens ; répond aux questions du jury | S | ★★ |
| 14 | Visuel | Formulaire : **profils avec mini-barre de répartition**, capital formaté avec puces, options en ligne repliable distincte, modèles en cartes radio, 4 scénarios rapides + « Plus d'idées » | Moins de texte, plus de visuel dans la colonne la plus utilisée | M | ★★ |
| 15 | Fonction | **Temps de récupération** sur la perte maximale + **portefeuilles d'exemple** (60/40, tout actions monde) en plus des profils | Deux idées des concurrents (PortfoliosLab, Curvo), compréhensibles par un débutant | M | ★★ |

**Ordre conseillé avant le hackathon** : 3 → 10 → 9 → 2 → 1 → 7 → 4 → 11 → 6 → 12 (environ 4 à 5 jours de travail en tout).
Le reste (5, 8, 13, 14, 15) consolide le produit ensuite. Le point 5 (jetons) est le plus structurant : si le temps le permet,
le faire **avant** les points 6 et 14 évite de retoucher deux fois les mêmes fichiers.

**Points de vigilance (non-régression)** :
- Points 1 et 9 : garder `nom` dans le catalogue (utilisé par Streamlit, le PDF et les messages à l'IA) et **ajouter** `nom_court` et
  `description`, sans rien renommer dans `ACTIFS_DISPONIBLES`.
- Points 2, 6 et 14 : chaque texte retiré de l'écran doit rester accessible (infobulle, bloc dépliable, Académie, `aria-label`).
- Point 4 : le résultat pré-calculé doit être signalé comme tel, pour ne pas laisser croire à une simulation en direct.
