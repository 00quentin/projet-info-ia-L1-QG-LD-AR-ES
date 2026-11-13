// Questions fréquentes : affichées en accordéons sur /faq et publiées en données
// structurées (JSON-LD FAQPage). Réponses en texte simple, un paragraphe par entrée.

export type QuestionFaq = {
  id: string;
  question: string;
  reponse: string[];
  /** Pour aller plus loin (pages du site). */
  liens?: { href: string; libelle: string }[];
};

export type ThemeFaq = { id: string; titre: string; questions: QuestionFaq[] };

export const FAQ: ThemeFaq[] = [
  {
    id: "donnees",
    titre: "Données de marché",
    questions: [
      {
        id: "origine-donnees",
        question: "D’où viennent les données ?",
        reponse: [
          "Les cours viennent de Yahoo Finance : ce sont de vrais cours de clôture, récupérés avec la bibliothèque open source yfinance pour les 23 actifs proposés (indices, obligations via des ETF, matières premières, devises, volatilité, ETF sectoriels, cryptomonnaies) et pour les symboles que vous ajoutez vous-même.",
          "Les taux de change viennent de la Banque centrale européenne (taux de référence officiels). Les taux directeurs, les taux à 10 ans et l’inflation viennent de la FRED, la base publique de la Réserve fédérale de Saint-Louis : ils donnent à l’IA les conditions économiques de départ et fournissent le taux sans risque du ratio de Sharpe.",
        ],
        liens: [{ href: "/mentions-legales#sources", libelle: "Toutes les sources" }],
      },
      {
        id: "frequence",
        question: "Les prix sont-ils en temps réel ? À quelle fréquence sont-ils mis à jour ?",
        reponse: [
          "Non, ce ne sont pas des cours en temps réel : le site travaille sur les derniers cours de clôture, dont la date est affichée dans le bandeau des marchés. Le serveur les garde une heure en mémoire, et le bouton de rechargement du bandeau permet de les relire chez Yahoo Finance au plus une fois toutes les cinq minutes.",
          "Les taux et l’inflation (FRED) sont relus toutes les six heures. Si Yahoo Finance ne répond pas, le site utilise les dernières valeurs connues et l’indique par la mention « Données de secours ».",
        ],
      },
      {
        id: "euros",
        question: "Comment les montants sont-ils convertis en euros ?",
        reponse: [
          "Votre capital est en euros, mais beaucoup d’actifs cotent en dollars. Une hausse de 10 % du S&P 500 avec un dollar qui perd 10 % ne rapporte presque rien à un épargnant européen : le site tient donc compte du change.",
          "En simulation, l’euro-dollar est lui-même simulé (son choc est estimé par l’IA et corrélé aux autres actifs). En backtest, le site utilise les taux de référence publiés chaque jour par la BCE. La conversion peut être désactivée dans les options.",
        ],
        liens: [{ href: "/academie#methodologie-euros", libelle: "La formule de conversion" }],
      },
    ],
  },
  {
    id: "simulation",
    titre: "Simulation & IA",
    questions: [
      {
        id: "ia-estimation",
        question: "Comment l’IA estime-t-elle l’impact d’un scénario ?",
        reponse: [
          "Votre scénario est envoyé à un modèle d’OpenAI avec la conjoncture du moment (taux, inflation). L’IA renvoie, pour chaque actif, un choc estimé en pourcentage, ainsi qu’une inflation et des taux directeurs, un précédent historique comparable et un niveau de fiabilité.",
          "Avec la calibration historique, elle pondère les deux ou trois crises passées les plus proches de votre scénario (2008, COVID, choc pétrolier de 1973…) et s’appuie sur leurs vraies amplitudes. Chaque réponse est ensuite contrôlée : un choc hors des bornes réalistes de l’actif (par exemple entre −55 % et +45 % pour le S&P 500) est ramené dans ces bornes.",
        ],
        liens: [{ href: "/academie#methodologie-pipeline", libelle: "Le pipeline complet" }],
      },
      {
        id: "moteur",
        question: "Que fait le moteur de simulation une fois le choc estimé ?",
        reponse: [
          "L’IA donne une destination ; le moteur trace le chemin. Il génère des trajectoires jour par jour autour du choc estimé, en utilisant les volatilités et les corrélations mesurées sur les vrais rendements des deux dernières années.",
          "Trois modèles sont proposés : Probabiliste (mouvement brownien géométrique, le plus réaliste), Historique (rejoue des blocs de vraies séances, avec leurs chocs violents) et Tendance (les mouvements s’auto-entretiennent). Le moteur calcule ensuite la valeur du portefeuille et ses métriques de risque : volatilité, Sharpe, perte maximale, VaR à 95 %.",
        ],
        liens: [{ href: "/academie#modeles-trois-modeles", libelle: "Les trois modèles" }],
      },
      {
        id: "monte-carlo",
        question: "Qu’est-ce que le mode Monte-Carlo ?",
        reponse: [
          "Au lieu d’une seule trajectoire, le moteur en tire 1 000, toutes différentes. Le graphique montre alors la trajectoire médiane et une bande qui contient 90 % des cas (du 5e au 95e centile), et le site calcule la probabilité de finir en perte.",
          "C’est la meilleure façon de voir l’incertitude : un même scénario peut bien ou mal finir selon le hasard des marchés. Les métriques de risque sont calculées sur chaque trajectoire, pas sur la médiane, qui lisse le hasard et sous-estimerait le risque.",
        ],
        liens: [{ href: "/academie#methodologie-monte-carlo", libelle: "La méthode Monte-Carlo" }],
      },
      {
        id: "resultats-changent",
        question: "Pourquoi les chiffres changent-ils d’une simulation à l’autre ?",
        reponse: [
          "C’est voulu : les trajectoires sont tirées au hasard à chaque lancement, comme les marchés qui ne rejouent jamais deux fois la même partition. Sans Monte-Carlo, vous voyez une seule trajectoire possible parmi d’autres ; avec Monte-Carlo, les résultats se stabilisent nettement.",
          "D’autres causes s’ajoutent : les cours évoluent d’un jour à l’autre, et l’IA peut répondre un peu différemment si vous reformulez le scénario. Pour un même texte, son analyse est mémorisée jusqu’à 24 heures sur le serveur afin de rester cohérente.",
        ],
      },
      {
        id: "fiabilite",
        question: "Les résultats sont-ils fiables ?",
        reponse: [
          "Ils donnent des ordres de grandeur pédagogiques, pas des prévisions. Le modèle fait des hypothèses simplificatrices : volatilités et corrélations constantes (alors qu’en crise elles s’envolent), aucun frais de transaction, obligations suivies via des ETF. L’IA, elle, peut se tromper ou inventer une référence.",
          "Le niveau de fiabilité affiché avec chaque analyse et les limites détaillées dans la Méthodologie aident à garder un regard critique. Le backtest, lui, repose sur les vrais cours passés, hors frais.",
        ],
        liens: [{ href: "/academie#methodologie-limites", libelle: "Les limites du modèle" }],
      },
      {
        id: "backtest",
        question: "Quelle différence entre une simulation et un backtest ?",
        reponse: [
          "La simulation regarde vers l’avenir : vous imaginez un événement, l’IA en estime l’impact et le moteur projette des trajectoires possibles.",
          "Le backtest regarde vers le passé : votre portefeuille est rejoué sur une vraie période (krach COVID, crise de 2008, bulle internet, krach pétrolier… ou des dates de votre choix, sur dix ans au plus) avec les cours réels, sans aucune IA pour les chiffres. Il est comparé au S&P 500 et au MSCI World.",
        ],
        liens: [{ href: "/backtest", libelle: "Lancer un backtest" }],
      },
    ],
  },
  {
    id: "usage",
    titre: "Usage, coût & confidentialité",
    questions: [
      {
        id: "conseil",
        question: "Est-ce un conseil en investissement ?",
        reponse: [
          "Non. Quant Terminal est un outil pédagogique conçu par des étudiants. Ses résultats sont des estimations d’un modèle et d’une IA ; ils ne constituent ni un conseil en investissement ni une recommandation d’acheter ou de vendre. L’équipe n’est pas un prestataire agréé par l’AMF.",
          "Pour une vraie décision, adressez-vous à un professionnel habilité (conseiller en investissements financiers enregistré à l’ORIAS, banque, entreprise d’investissement).",
        ],
        liens: [{ href: "/cgu#avertissement", libelle: "L’avertissement complet" }],
      },
      {
        id: "cout",
        question: "Le site est-il gratuit ? Faut-il créer un compte ?",
        reponse: [
          "Oui, c’est gratuit, sans compte et sans publicité. Chaque analyse coûte toutefois un appel à un service d’IA payé par l’équipe : le nombre de demandes par minute est donc limité pour éviter les abus.",
          "Le serveur de calcul se met en veille quand personne ne l’utilise : la toute première simulation peut alors prendre jusqu’à une minute, le temps qu’il se réveille.",
        ],
      },
      {
        id: "donnees-personnelles",
        question: "Que deviennent mes données ?",
        reponse: [
          "Votre historique, votre conversation avec l’analyste et vos préférences restent dans votre navigateur. Les textes de scénario et les questions au chat sont envoyés à notre serveur puis à OpenAI pour produire la réponse, sans être enregistrés dans une base de données.",
          "Le site n’utilise ni cookie publicitaire ni outil de mesure d’audience. N’écrivez pas d’informations personnelles dans vos scénarios ou vos questions.",
        ],
        liens: [{ href: "/confidentialite", libelle: "La politique de confidentialité" }],
      },
      {
        id: "effacer",
        question: "Comment effacer mon historique et ma conversation ?",
        reponse: [
          "La page Historique propose de supprimer une simulation ou de tout effacer, et le chat a son propre bouton d’effacement. Vous pouvez aussi supprimer les données du site dans les réglages de votre navigateur : comme rien n’est gardé sur nos serveurs, il n’y a rien d’autre à demander.",
        ],
        liens: [{ href: "/historique", libelle: "Mon historique" }],
      },
      {
        id: "partage",
        question: "Puis-je partager ou exporter une simulation ?",
        reponse: [
          "Oui. Le lien de partage contient vos réglages (scénario, actifs, options) : la personne qui l’ouvre relance la même simulation — avec un nouveau tirage, donc des chiffres légèrement différents. Vous pouvez aussi télécharger un rapport PDF commenté par l’IA ou les données en CSV.",
        ],
      },
      {
        id: "equipe",
        question: "Qui a créé Quant Terminal ? Comment signaler une erreur ?",
        reponse: [
          "Quatre étudiants de la licence MIASHS de l’Université Paris Nanterre : Quentin Geldreich, Lukha Doazan, Evan Saadi et Alex Ruimy, dans le cadre de leur cours d’informatique de L1.",
          "Une erreur, une idée, une question ? Écrivez-nous ou ouvrez un ticket sur le dépôt GitHub du projet : tout est expliqué sur la page Contact.",
        ],
        liens: [
          { href: "/contact", libelle: "Nous contacter" },
          { href: "/a-propos", libelle: "À propos du projet" },
        ],
      },
    ],
  },
];

export const TOUTES_LES_QUESTIONS = FAQ.flatMap((t) => t.questions);
