import type { Metadata } from "next";
import { Landmark } from "lucide-react";
import { Encadre, G, Liste, P, Point } from "@/components/academie/blocs";
import { Fiche, FichePrestataire, Lien, LienContact, Rubrique } from "@/components/legal/blocs";
import { PageLegale } from "@/components/legal/PageLegale";
import { DEPOT_GITHUB, DEPOT_ISSUES, EQUIPE, HEBERGEURS, NOM_SITE, RESPONSABLE_PUBLICATION, SITE_URL, SOURCES_DONNEES, UNIVERSITE } from "@/contenu/legal";

export const metadata: Metadata = {
  title: "Mentions légales",
  description: "Éditeur, hébergeurs, propriété intellectuelle et sources des données du site Quant Terminal, projet étudiant de l’Université Paris Nanterre.",
  alternates: { canonical: "/mentions-legales" },
};

const SOMMAIRE = [
  { id: "editeur", numero: "1.", titre: "Éditeur du site" },
  { id: "hebergement", numero: "2.", titre: "Hébergement" },
  { id: "propriete", numero: "3.", titre: "Propriété intellectuelle" },
  { id: "sources", numero: "4.", titre: "Sources des données" },
  { id: "avertissement", numero: "5.", titre: "Avertissement" },
  { id: "donnees", numero: "6.", titre: "Données personnelles" },
  { id: "contact", numero: "7.", titre: "Contact" },
];

const numero = (id: string) => SOMMAIRE.find((s) => s.id === id)?.numero;

export default function Page() {
  return (
    <PageLegale
      icone={Landmark}
      etiquette="Informations légales"
      titre="Mentions légales"
      sommaire={SOMMAIRE}
      chapeau={
        <p>
          Informations prévues par la loi n° 2004-575 du 21 juin 2004 pour la confiance dans l’économie numérique (LCEN) : qui publie {NOM_SITE}, qui
          l’héberge et d’où viennent ses données.
        </p>
      }
    >
      <Rubrique id="editeur" numero={numero("editeur")} titre="Éditeur du site">
        <P>
          Le site <G>{NOM_SITE}</G> (<Lien href={SITE_URL}>{SITE_URL.replace(/^https:\/\//, "")}</Lien>) est un <G>projet étudiant</G>, non commercial,
          réalisé dans le cadre du cours d’informatique de la {UNIVERSITE.formation} de l’{UNIVERSITE.nom}.
        </P>
        <Fiche
          lignes={[
            ["Éditeurs", EQUIPE.join(", ")],
            ["Statut", "Étudiants, personnes physiques agissant à titre non professionnel"],
            ["Responsable de la publication", RESPONSABLE_PUBLICATION],
            ["Cadre", `${UNIVERSITE.nom} — ${UNIVERSITE.formation}`],
            ["Contact", <LienContact key="contact" />],
          ]}
        />
        <P>
          Comme la LCEN le permet aux éditeurs non professionnels, l’adresse personnelle des étudiants n’est pas publiée : l’équipe reste joignable à
          l’adresse de contact ci-dessus et les coordonnées des hébergeurs figurent ci-dessous.
        </P>
        <Encadre titre="Site indépendant">
          <p>
            {NOM_SITE} n’est pas un site officiel de l’{UNIVERSITE.nom}, qui n’en est ni l’éditeur ni l’hébergeur. Les contenus publiés engagent
            uniquement leurs auteurs.
          </p>
        </Encadre>
      </Rubrique>

      <Rubrique id="hebergement" numero={numero("hebergement")} titre="Hébergement">
        <P>Le site est réparti entre deux hébergeurs : l’un sert les pages que vous consultez, l’autre fait tourner le moteur de calcul.</P>
        {HEBERGEURS.map((h) => (
          <FichePrestataire key={h.nom} p={h} />
        ))}
      </Rubrique>

      <Rubrique id="propriete" numero={numero("propriete")} titre="Propriété intellectuelle">
        <P>
          La structure du site, ses textes (notamment ceux de l’Académie), ses illustrations, ses graphiques, son logo et son code sont l’œuvre de
          l’équipe {NOM_SITE}. Le <Lien href={DEPOT_GITHUB}>code source</Lien> est consultable publiquement sur GitHub ; en l’absence de licence libre,
          sa consultation ne vaut pas autorisation de le reproduire ou de le réutiliser. Toute reproduction substantielle du site ou de ses contenus
          nécessite l’accord préalable des auteurs ; les courtes citations accompagnées de la source restent libres.
        </P>
        <P>Certains éléments appartiennent à des tiers et restent soumis à leurs propres conditions :</P>
        <Liste>
          <Point>
            <G>Photos d’archives de l’Académie</G> : issues de Wikimedia Commons, sous leurs licences respectives (domaine public, Creative Commons…).
            L’auteur et la licence sont indiqués sous chaque photo.
          </Point>
          <Point>
            <G>Police Inter</G> (SIL Open Font License 1.1) et <G>icônes Lucide</G> (licence ISC).
          </Point>
          <Point>
            <G>Marques citées</G> (Yahoo Finance, OpenAI, Vercel, Render, GitHub, indices boursiers…) : elles appartiennent à leurs propriétaires
            respectifs. Leur mention sert à indiquer une source ou un outil et n’implique aucun partenariat.
          </Point>
          <Point>
            <G>Textes générés par l’IA</G> (analyses, réponses du chat, rapports) : ils sont produits automatiquement à votre demande et vous pouvez
            les réutiliser, sous votre responsabilité.
          </Point>
        </Liste>
      </Rubrique>

      <Rubrique id="sources" numero={numero("sources")} titre="Sources des données">
        <P>
          Les données affichées proviennent de sources publiques ou de services tiers. Elles sont fournies à titre indicatif, peuvent être différées,
          incomplètes ou inexactes, et restent la propriété de leurs fournisseurs.
        </P>
        <ul className="flex max-w-[40rem] flex-col divide-y divide-line rounded-2xl border border-line bg-surface shadow-card">
          {SOURCES_DONNEES.map((s) => (
            <li key={s.nom} className="px-4 py-3 sm:px-5">
              <p className="text-[15px] font-semibold text-ink">
                <Lien href={s.lien}>{s.nom}</Lien>
              </p>
              <p className="mt-0.5 text-sm leading-relaxed text-ink-2">{s.usage}</p>
            </li>
          ))}
        </ul>
        <P>
          La méthode de calcul (volatilités, corrélations, Monte-Carlo, métriques de risque) est détaillée dans la{" "}
          <Lien href="/methodologie">page Méthodologie</Lien>.
        </P>
      </Rubrique>

      <Rubrique id="avertissement" numero={numero("avertissement")} titre="Avertissement">
        <Encadre ton="alerte" titre="Outil pédagogique — pas un conseil en investissement">
          <p>
            Les simulations, analyses et contenus de {NOM_SITE} ont une vocation exclusivement pédagogique. Ils ne constituent ni un conseil en
            investissement, ni une recommandation d’achat ou de vente. Les éditeurs ne sont pas des professionnels agréés.
          </p>
          <p>
            Le détail figure dans les <Lien href="/cgu#avertissement">conditions générales d’utilisation</Lien>.
          </p>
        </Encadre>
      </Rubrique>

      <Rubrique id="donnees" numero={numero("donnees")} titre="Données personnelles">
        <P>
          {NOM_SITE} ne demande ni compte, ni nom, ni adresse e-mail. Ce que deviennent les textes que vous saisissez, ce qui reste dans votre
          navigateur et vos droits sont expliqués dans la <Lien href="/confidentialite">politique de confidentialité</Lien>.
        </P>
      </Rubrique>

      <Rubrique id="contact" numero={numero("contact")} titre="Contact">
        <P>
          Pour toute question, demande ou signalement concernant le site, écrivez-nous à <LienContact />. Vous pouvez aussi ouvrir un ticket sur le{" "}
          <Lien href={DEPOT_ISSUES}>dépôt GitHub du projet</Lien> (visible publiquement). D’autres moyens sont présentés sur la{" "}
          <Lien href="/contact">page Contact</Lien>.
        </P>
      </Rubrique>
    </PageLegale>
  );
}
