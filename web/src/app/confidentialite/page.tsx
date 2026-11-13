import type { Metadata } from "next";
import { ShieldCheck } from "lucide-react";
import { Encadre, G, Liste, ListeEncadre, P, Point } from "@/components/academie/blocs";
import { Fiche, Lien, LienContact, Rubrique } from "@/components/legal/blocs";
import { PageLegale } from "@/components/legal/PageLegale";
import { EQUIPE, HEBERGEURS, NOM_SITE, OPENAI, RESPONSABLE_PUBLICATION, STOCKAGE_NAVIGATEUR, WIKIMEDIA } from "@/contenu/legal";

export const metadata: Metadata = {
  title: "Politique de confidentialité",
  description:
    "Quelles données Quant Terminal traite (et surtout lesquelles il ne garde pas) : stockage dans votre navigateur, envoi des textes à l’IA, hébergeurs, droits RGPD.",
  alternates: { canonical: "/confidentialite" },
};

const SOMMAIRE = [
  { id: "en-bref", titre: "En bref" },
  { id: "responsable", numero: "1.", titre: "Responsable du traitement" },
  { id: "navigateur", numero: "2.", titre: "Ce qui reste dans votre navigateur" },
  { id: "serveur", numero: "3.", titre: "Ce qui est envoyé au serveur et à l’IA" },
  { id: "journaux", numero: "4.", titre: "Journaux techniques" },
  { id: "tiers", numero: "5.", titre: "Prestataires et transferts" },
  { id: "bases", numero: "6.", titre: "Bases légales" },
  { id: "durees", numero: "7.", titre: "Durées de conservation" },
  { id: "droits", numero: "8.", titre: "Vos droits" },
  { id: "evolution", numero: "9.", titre: "Modifications" },
];

const numero = (id: string) => SOMMAIRE.find((s) => s.id === id)?.numero;

const PRESTATAIRES = [
  ...HEBERGEURS.map((h) => ({ ...h, donnees: "Adresse IP, requêtes techniques ; pour l’API, contenu des demandes le temps de les traiter" })),
  { ...OPENAI, donnees: "Textes de scénario, messages du chat, résumé chiffré des résultats" },
  { ...WIKIMEDIA, donnees: "Adresse IP et navigateur, au chargement des photos de l’Académie" },
];

export default function Page() {
  return (
    <PageLegale
      icone={ShieldCheck}
      etiquette="Vie privée"
      titre="Politique de confidentialité"
      sommaire={SOMMAIRE}
      chapeau={
        <p>
          {NOM_SITE} est conçu pour fonctionner sans vous connaître : pas de compte, pas de traceur publicitaire. Voici, sans jargon, ce qui circule
          quand vous l’utilisez, conformément au Règlement général sur la protection des données (RGPD) et à la loi Informatique et Libertés.
        </p>
      }
    >
      <section id="en-bref" aria-labelledby="en-bref-titre" className="scroll-mt-6 lg:scroll-mt-36">
        <h2 id="en-bref-titre" className="sr-only">
          En bref
        </h2>
        <Encadre titre="L’essentiel en cinq points">
          <ListeEncadre>
            <Point>
              <G>Aucun compte</G> : nous ne vous demandons ni nom, ni adresse e-mail, ni mot de passe.
            </Point>
            <Point>
              <G>Votre historique, votre conversation et vos préférences restent dans votre navigateur</G>, pas sur nos serveurs.
            </Point>
            <Point>
              Les <G>textes de scénario et les questions au chat</G> sont envoyés à notre API puis à OpenAI pour générer la réponse ; nous ne les
              enregistrons dans aucune base de données.
            </Point>
            <Point>
              <G>Ni cookie publicitaire, ni mesure d’audience</G>, ni bouton de réseau social : rien ne vous suit d’un site à l’autre.
            </Point>
            <Point>
              Nous ne vendons ni ne louons aucune donnée. Une question ? Écrivez à <LienContact />.
            </Point>
          </ListeEncadre>
        </Encadre>
      </section>

      <Rubrique id="responsable" numero={numero("responsable")} titre="Responsable du traitement">
        <P>
          Le responsable du traitement est l’équipe éditrice de {NOM_SITE} ({EQUIPE.join(", ")}), représentée par {RESPONSABLE_PUBLICATION}. Il s’agit
          d’un projet étudiant sans but commercial (voir les <Lien href="/mentions-legales">mentions légales</Lien>).
        </P>
        <Fiche
          lignes={[
            ["Contact", <LienContact key="contact" />],
            ["Délégué à la protection des données", "Aucun (non obligatoire pour ce projet) : écrivez à l’adresse ci-dessus"],
          ]}
        />
      </Rubrique>

      <Rubrique id="navigateur" numero={numero("navigateur")} titre="Ce qui reste dans votre navigateur">
        <P>
          Pour vous éviter de créer un compte, le site range quelques informations dans le stockage local de votre navigateur (
          <code className="rounded bg-surface-2 px-1 py-0.5 text-[0.9em]">localStorage</code> et{" "}
          <code className="rounded bg-surface-2 px-1 py-0.5 text-[0.9em]">sessionStorage</code>). Elles ne quittent votre appareil que lorsque vous
          posez vous-même une question à l’analyste (voir la partie suivante). Le site lui-même ne dépose <G>aucun cookie</G>.
        </P>
        <ul className="flex max-w-[40rem] flex-col divide-y divide-line rounded-2xl border border-line bg-surface shadow-card">
          {STOCKAGE_NAVIGATEUR.map((s) => (
            <li key={s.cle} className="flex flex-col gap-1 px-4 py-3 sm:px-5">
              <p className="text-[15px] leading-relaxed text-ink">{s.contenu}</p>
              <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
                <code className="rounded bg-surface-2 px-1.5 py-0.5 text-ink-2">{s.cle}</code>
                <span>{s.lieu}</span>
                <span aria-hidden>·</span>
                <span>{s.duree}</span>
              </p>
            </li>
          ))}
        </ul>
        <P>
          Ces informations servent uniquement à faire fonctionner des fonctions que vous utilisez : elles sont dispensées de consentement (article 82
          de la loi Informatique et Libertés). Pour les supprimer : bouton <G>Effacer</G> de la page <Lien href="/historique">Historique</Lien>, bouton
          d’effacement de la conversation dans le chat, ou suppression des « données de site » dans les réglages de votre navigateur. En navigation
          privée, tout disparaît à la fermeture de la fenêtre.
        </P>
        <P>
          Le <G>lien de partage</G> d’une simulation contient vos réglages en clair dans l’adresse (scénario, actifs, capital) : toute personne qui
          reçoit le lien peut les lire.
        </P>
      </Rubrique>

      <Rubrique id="serveur" numero={numero("serveur")} titre="Ce qui est envoyé au serveur et à l’IA">
        <P>Certaines actions nécessitent un calcul sur notre API, qui peut elle-même faire appel à OpenAI :</P>
        <Liste>
          <Point>
            <G>Simulation</G> : vos scénarios (1 000 caractères au plus chacun) et les réglages du portefeuille (actifs, répartition, capital, horizon,
            options). Le texte des scénarios, débarrassé des tentatives de manipulation de l’IA, est transmis à OpenAI avec la conjoncture du moment
            et les éventuels tickers personnalisés. Le montant de votre capital n’est pas transmis à OpenAI.
          </Point>
          <Point>
            <G>Chat</G> : les derniers messages de la conversation (30 au plus) et, si vous le laissez attaché, le résumé chiffré du résultat que vous
            regardez. L’ensemble est transmis à OpenAI pour rédiger la réponse.
          </Point>
          <Point>
            <G>Rapport PDF</G> : les chiffres du résultat affiché et le texte du scénario. OpenAI rédige le commentaire, l’API assemble le PDF et vous
            le renvoie sans le conserver.
          </Point>
          <Point>
            <G>Backtest, cours et actifs personnalisés</G> : les réglages du portefeuille et les symboles boursiers saisis. Aucun appel à l’IA ; c’est
            notre serveur, et non votre navigateur, qui interroge Yahoo Finance.
          </Point>
        </Liste>
        <P>
          L’API traite ces demandes en mémoire et <G>ne les enregistre dans aucune base de données ni aucun fichier</G>. Seule exception : l’analyse
          d’un scénario est gardée jusqu’à 24 heures dans la mémoire vive du serveur, afin qu’un même texte ne soit pas réanalysé (et refacturé)
          plusieurs fois ; cette mémoire est vidée à chaque redémarrage.
        </P>
        <P>
          Chez OpenAI, les données transmises par API ne servent pas, par défaut, à entraîner ses modèles et peuvent être conservées un temps limité
          (de l’ordre de 30 jours) pour détecter les abus, selon les{" "}
          <Lien href="https://openai.com/enterprise-privacy/">engagements publiés par OpenAI</Lien> pour son API.
        </P>
        <Encadre ton="alerte" titre="Ne saisissez pas de données personnelles">
          <p>
            Un scénario ou une question n’a pas besoin de votre nom, de vos coordonnées ou de votre situation patrimoniale réelle. Évitez d’y écrire
            des informations qui permettent de vous identifier, vous ou un tiers.
          </p>
        </Encadre>
      </Rubrique>

      <Rubrique id="journaux" numero={numero("journaux")} titre="Journaux techniques">
        <P>
          Comme tout site web, nos hébergeurs reçoivent à chaque visite des informations techniques : <G>adresse IP</G>, date et heure, page ou
          service demandé, type de navigateur. Ils les consignent dans des journaux utilisés pour faire fonctionner le service, diagnostiquer les
          pannes et se protéger des attaques, pendant une durée limitée fixée par chacun d’eux.
        </P>
        <P>
          Notre API utilise aussi votre adresse IP, en mémoire vive uniquement, pour <G>limiter le nombre de demandes par minute</G> et empêcher qu’un
          robot épuise le service. Ses propres journaux consignent des événements techniques (erreurs, appels au modèle d’IA) et n’ont pas vocation à
          contenir le texte de vos scénarios ou de vos questions.
        </P>
        <P>
          Le site n’utilise <G>aucun outil de mesure d’audience</G> (pas de Google Analytics ni d’équivalent), aucun cookie publicitaire et ne charge
          pas de police depuis un service externe : la police Inter est servie par le site lui-même.
        </P>
      </Rubrique>

      <Rubrique id="tiers" numero={numero("tiers")} titre="Prestataires et transferts">
        <P>Les seuls destinataires des données décrites ci-dessus sont les prestataires techniques suivants :</P>
        <ul className="flex max-w-[40rem] flex-col divide-y divide-line rounded-2xl border border-line bg-surface shadow-card">
          {PRESTATAIRES.map((p) => (
            <li key={p.nom} className="flex flex-col gap-1 px-4 py-3 sm:px-5">
              <p className="text-[15px] font-semibold text-ink">
                {p.nom} <span className="font-normal text-muted">· {p.adresse.includes("États-Unis") ? "États-Unis" : p.adresse}</span>
              </p>
              <p className="text-sm leading-relaxed text-ink-2">{p.role}.</p>
              <p className="text-sm leading-relaxed text-muted">Données : {p.donnees}.</p>
              <p className="text-sm">
                <Lien href={p.confidentialite}>Sa politique de confidentialité</Lien>
              </p>
            </li>
          ))}
        </ul>
        <P>
          Les photos d’archives de l’Académie sont chargées directement depuis Wikimedia Commons : en les affichant, votre navigateur contacte les
          serveurs de la Wikimedia Foundation, qui reçoit alors votre adresse IP.
        </P>
        <P>
          Ces sociétés sont établies aux <G>États-Unis</G> : des données peuvent donc y être transférées. Ces transferts s’appuient sur les garanties
          prévues par le RGPD — le cadre de protection des données UE–États-Unis (Data Privacy Framework) pour les entreprises qui y adhèrent, ou les
          clauses contractuelles types de la Commission européenne.
        </P>
      </Rubrique>

      <Rubrique id="bases" numero={numero("bases")} titre="Bases légales">
        <Liste>
          <Point>
            <G>Fournir le service que vous demandez</G> (article 6.1.b du RGPD) : calculer une simulation, répondre à une question, générer un
            rapport.
          </Point>
          <Point>
            <G>Intérêt légitime</G> (article 6.1.f) : sécuriser le site, limiter les abus, diagnostiquer les erreurs.
          </Point>
          <Point>
            <G>Stockage dans votre navigateur</G> : strictement nécessaire aux fonctions que vous utilisez, donc sans consentement préalable (article 82
            de la loi Informatique et Libertés).
          </Point>
        </Liste>
      </Rubrique>

      <Rubrique id="durees" numero={numero("durees")} titre="Durées de conservation">
        <Fiche
          lignes={[
            ["Votre navigateur", "Jusqu’à ce que vous effaciez les données (fermeture de l’onglet pour le résumé transmis au chat)"],
            ["Notre API", "Le temps de traiter la demande ; jusqu’à 24 h en mémoire vive pour l’analyse d’un scénario"],
            ["Limitation des demandes", "En mémoire vive uniquement, effacée au redémarrage du serveur"],
            ["Hébergeurs et OpenAI", "Journaux techniques et contrôle des abus, selon leurs politiques (durées limitées)"],
          ]}
        />
      </Rubrique>

      <Rubrique id="droits" numero={numero("droits")} titre="Vos droits">
        <P>
          Vous disposez d’un droit d’<G>accès</G>, de <G>rectification</G>, d’<G>effacement</G>, de <G>limitation</G>, d’<G>opposition</G> et de{" "}
          <G>portabilité</G> sur vos données, ainsi que du droit de définir des directives sur leur sort après votre décès.
        </P>
        <P>
          Comme le site ne crée pas de compte, nous ne détenons en général aucune donnée permettant de vous identifier : l’essentiel est dans votre
          navigateur, où vous pouvez le consulter et l’effacer vous-même à tout moment. Pour toute demande, écrivez à <LienContact /> ; nous
          répondrons dans un délai d’un mois.
        </P>
        <P>
          Si vous estimez que vos droits ne sont pas respectés, vous pouvez introduire une réclamation auprès de la{" "}
          <Lien href="https://www.cnil.fr/fr/adresser-une-plainte">CNIL</Lien> (3 place de Fontenoy, TSA 80715, 75334 Paris Cedex 07).
        </P>
      </Rubrique>

      <Rubrique id="evolution" numero={numero("evolution")} titre="Modifications">
        <P>
          Cette politique suit l’évolution du site : si une nouvelle fonction traite d’autres données, elle sera mise à jour ici, avec sa date en haut
          de page.
        </P>
      </Rubrique>
    </PageLegale>
  );
}
