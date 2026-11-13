import type { Metadata } from "next";
import { ScrollText } from "lucide-react";
import { Encadre, G, Liste, ListeEncadre, P, Point } from "@/components/academie/blocs";
import { Lien, LienContact, Rubrique } from "@/components/legal/blocs";
import { PageLegale } from "@/components/legal/PageLegale";
import { AVERTISSEMENT_COURT, NOM_SITE } from "@/contenu/legal";

export const metadata: Metadata = {
  title: "Conditions générales d’utilisation",
  description: "Règles d’utilisation de Quant Terminal : accès gratuit, avertissement financier, usage de l’IA, responsabilité et droit applicable.",
  alternates: { canonical: "/cgu" },
};

const SOMMAIRE = [
  { id: "objet", numero: "1.", titre: "Objet et acceptation" },
  { id: "service", numero: "2.", titre: "Le service" },
  { id: "acces", numero: "3.", titre: "Accès gratuit" },
  { id: "avertissement", numero: "4.", titre: "Avertissement financier" },
  { id: "ia", numero: "5.", titre: "Contenus générés par l’IA" },
  { id: "usage", numero: "6.", titre: "Usage acceptable" },
  { id: "responsabilite", numero: "7.", titre: "Responsabilité" },
  { id: "propriete", numero: "8.", titre: "Propriété intellectuelle" },
  { id: "donnees", numero: "9.", titre: "Données personnelles" },
  { id: "evolution", numero: "10.", titre: "Évolution des conditions" },
  { id: "droit", numero: "11.", titre: "Droit applicable et litiges" },
];

const numero = (id: string) => SOMMAIRE.find((s) => s.id === id)?.numero;

export default function Page() {
  return (
    <PageLegale
      icone={ScrollText}
      etiquette="Conditions d’utilisation"
      titre="Conditions générales d’utilisation"
      sommaire={SOMMAIRE}
      chapeau={
        <p>
          Les règles du jeu, en clair : ce que {NOM_SITE} propose, ce qu’il n’est pas — un conseiller financier — et ce que nous attendons de
          chacun pour que le service reste ouvert à tous.
        </p>
      }
    >
      <Rubrique id="objet" numero={numero("objet")} titre="Objet et acceptation">
        <P>
          Les présentes conditions générales d’utilisation (CGU) encadrent l’utilisation du site {NOM_SITE}, édité par une équipe d’étudiants (voir
          les <Lien href="/mentions-legales">mentions légales</Lien>). En utilisant le site, vous acceptez ces conditions. Si vous ne les acceptez pas,
          merci de ne pas utiliser le service.
        </P>
      </Rubrique>

      <Rubrique id="service" numero={numero("service")} titre="Le service">
        <P>{NOM_SITE} est un outil pédagogique qui permet de :</P>
        <Liste>
          <Point>
            <G>simuler</G> l’effet d’un scénario économique fictif, décrit en quelques mots, sur un portefeuille d’actifs (mode simple, comparaison de
            scénarios, Monte-Carlo) ;
          </Point>
          <Point>
            <G>rejouer</G> un portefeuille sur une vraie période passée (backtest) ;
          </Point>
          <Point>
            <G>apprendre</G> les bases de la finance de marché avec l’Académie et poser des questions à un analyste IA ;
          </Point>
          <Point>
            <G>exporter</G> ses résultats (rapport PDF, fichier CSV, lien de partage).
          </Point>
        </Liste>
        <P>
          Les cours viennent de Yahoo Finance, les taux de change de la BCE, la conjoncture de la FRED ; l’impact des scénarios est estimé par des
          modèles d’OpenAI puis simulé par notre moteur. La <Lien href="/methodologie">Méthodologie</Lien> détaille les calculs.
        </P>
      </Rubrique>

      <Rubrique id="acces" numero={numero("acces")} titre="Accès gratuit">
        <P>
          Le site est <G>gratuit</G>, sans inscription ni publicité. Il est accessible à toute personne disposant d’une connexion à Internet ; les frais
          de connexion restent à votre charge.
        </P>
        <P>
          S’agissant d’un projet étudiant, aucune disponibilité n’est garantie. Le service peut être lent au réveil du serveur, interrompu pour
          maintenance, modifié ou arrêté à tout moment, sans préavis ni indemnité. Pour protéger le service, le nombre de demandes par minute est
          limité ; au-delà, il suffit de patienter un instant.
        </P>
      </Rubrique>

      <Rubrique id="avertissement" numero={numero("avertissement")} titre="Avertissement financier">
        <Encadre ton="alerte" titre={AVERTISSEMENT_COURT}>
          <ListeEncadre>
            <Point>
              Les simulations, backtests, analyses, réponses du chat, rapports et contenus de l’Académie ont une vocation <G>exclusivement pédagogique</G>.
              Ils ne constituent <G>ni un conseil en investissement</G> au sens de l’article L. 321-1 du Code monétaire et financier,{" "}
              <G>ni une recommandation</G> d’acheter, de vendre ou de conserver un instrument financier, ni une incitation à investir.
            </Point>
            <Point>
              Les éditeurs ne sont <G>ni conseillers en investissements financiers, ni prestataires de services d’investissement</G>. Ils ne sont ni
              agréés ni enregistrés auprès de l’Autorité des marchés financiers (AMF) ou de l’ORIAS.
            </Point>
            <Point>
              Les résultats sont des <G>estimations</G> produites par un modèle mathématique simplifié et par une intelligence artificielle, à partir
              d’hypothèses (volatilités et corrélations constantes, absence de frais…) qui ne se vérifient pas toujours. Ils peuvent être faux et
              varient d’une simulation à l’autre.
            </Point>
            <Point>
              Un backtest décrit le passé : <G>les performances passées ne préjugent pas des performances futures</G>. Tout investissement comporte un
              risque de perte en capital.
            </Point>
            <Point>
              Avant toute décision, informez-vous auprès d’un professionnel habilité (conseiller en investissements financiers enregistré à l’ORIAS,
              banque ou entreprise d’investissement agréée). Vous restez <G>seul responsable</G> de vos décisions d’investissement.
            </Point>
          </ListeEncadre>
        </Encadre>
      </Rubrique>

      <Rubrique id="ia" numero={numero("ia")} titre="Contenus générés par l’IA">
        <P>
          Les analyses de scénarios, les réponses de l’analyste et le commentaire des rapports PDF sont <G>rédigés automatiquement</G> par des modèles
          d’OpenAI, sans relecture humaine. Ils peuvent contenir des erreurs, des chiffres approximatifs, des références historiques inexactes ou des
          affirmations inventées. Vérifiez toute information importante auprès d’une source fiable.
        </P>
        <P>
          Les chocs estimés par l’IA sont bornés par notre moteur pour écarter les valeurs aberrantes, et un niveau de fiabilité est affiché avec chaque
          analyse : ces garde-fous limitent les erreurs, ils ne les suppriment pas.
        </P>
        <P>
          Le texte que vous saisissez est transmis à OpenAI pour produire la réponse : n’y indiquez <G>aucune donnée personnelle</G> ni information
          confidentielle (voir la <Lien href="/confidentialite#serveur">politique de confidentialité</Lien>).
        </P>
      </Rubrique>

      <Rubrique id="usage" numero={numero("usage")} titre="Usage acceptable">
        <P>
          Chaque analyse déclenche un appel payant à un service d’IA, financé par l’équipe. Pour que le site reste gratuit et disponible, vous vous
          engagez à ne pas :
        </P>
        <Liste>
          <Point>interroger le service de manière automatisée ou massive (scripts, robots), ni chercher à contourner les limites de demandes ;</Point>
          <Point>
            détourner l’IA de son objet : tentatives de lui faire ignorer ses consignes, de lui faire produire des contenus sans rapport avec la finance
            ou de l’utiliser comme assistant gratuit pour d’autres usages ;
          </Point>
          <Point>saisir des contenus illicites, haineux, diffamatoires, violents ou portant atteinte aux droits d’autrui ;</Point>
          <Point>saisir des données personnelles concernant des tiers ;</Point>
          <Point>
            porter atteinte au fonctionnement ou à la sécurité du site et de son API (intrusion, surcharge volontaire, recherche de failles hors
            signalement responsable) ;
          </Point>
          <Point>présenter les résultats du site comme un conseil professionnel ou les utiliser pour tromper autrui.</Point>
        </Liste>
        <P>
          En cas d’abus, l’accès peut être limité ou bloqué, sans préjudice d’éventuelles poursuites. Si vous découvrez une faille, merci de nous la
          signaler discrètement à <LienContact />.
        </P>
      </Rubrique>

      <Rubrique id="responsabilite" numero={numero("responsabilite")} titre="Responsabilité">
        <P>
          Les éditeurs s’efforcent de fournir un service exact et à jour, sans pouvoir le garantir : le site est fourni <G>« en l’état »</G>. Dans les
          limites permises par la loi, leur responsabilité ne saurait être engagée pour :
        </P>
        <Liste>
          <Point>une décision d’investissement, une perte ou un manque à gagner liés à l’utilisation des résultats ;</Point>
          <Point>des données inexactes, incomplètes ou différées provenant des sources tierces (Yahoo Finance, BCE, FRED, OpenAI…) ;</Point>
          <Point>une interruption, une lenteur ou une erreur du service, ou la perte de l’historique conservé dans votre navigateur ;</Point>
          <Point>le contenu des sites tiers vers lesquels pointent des liens.</Point>
        </Liste>
        <P>Vous êtes responsable de l’usage que vous faites du site et des textes que vous y saisissez.</P>
      </Rubrique>

      <Rubrique id="propriete" numero={numero("propriete")} titre="Propriété intellectuelle">
        <P>
          Les contenus du site sont protégés par le droit d’auteur. Les règles applicables, ainsi que les éléments appartenant à des tiers (photos,
          police, icônes, marques), sont détaillés dans les <Lien href="/mentions-legales#propriete">mentions légales</Lien>.
        </P>
      </Rubrique>

      <Rubrique id="donnees" numero={numero("donnees")} titre="Données personnelles">
        <P>
          Le site fonctionne sans compte. Le traitement des textes saisis, le stockage dans votre navigateur et vos droits sont décrits dans la{" "}
          <Lien href="/confidentialite">politique de confidentialité</Lien>.
        </P>
      </Rubrique>

      <Rubrique id="evolution" numero={numero("evolution")} titre="Évolution des conditions">
        <P>
          Ces conditions peuvent évoluer avec le site. La version en vigueur est celle publiée sur cette page, à la date indiquée en haut ; continuer à
          utiliser le site après une modification vaut acceptation de la nouvelle version.
        </P>
      </Rubrique>

      <Rubrique id="droit" numero={numero("droit")} titre="Droit applicable et litiges">
        <P>
          Les présentes conditions sont régies par le <G>droit français</G>. En cas de difficulté, contactez-nous d’abord à <LienContact /> : nous
          chercherons une solution amiable. À défaut, le litige sera porté devant les juridictions françaises compétentes, sous réserve des règles
          impératives qui protègent les consommateurs.
        </P>
      </Rubrique>
    </PageLegale>
  );
}
