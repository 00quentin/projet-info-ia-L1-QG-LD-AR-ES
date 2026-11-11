import type { ReactNode } from "react";
import { Chapeau, Chronologie, Encadre, Etape, G, ListeEncadre, Point, Section } from "@/components/academie/blocs";
import { BlackMonday } from "@/components/academie/illustrations/BlackMonday";
import { Photo } from "@/components/academie/Photo";
import { SyntheseCrises } from "@/components/academie/Syntheses";
import { sectionsDe } from "./modules";

const s = sectionsDe("cas");

function Liste({ children }: { children: ReactNode }) {
  return <ul className="flex flex-col gap-2">{children}</ul>;
}

export function ContenuCas() {
  return (
    <>
      <Chapeau>
        L’histoire boursière n’est pas une succession d’événements aléatoires. Chaque crise a sa logique, ses victimes, et ses gagnants. Les
        comprendre, c’est mieux anticiper la prochaine.
      </Chapeau>

      <Section {...s("krach-1929")}>
        <Chronologie>
          <Etape titre="Contexte">
            <p>
              Les années 1920 furent les « Roaring Twenties » — une décennie d’euphorie, de spéculation effrénée, d’achats d’actions à crédit (
              <em>margin trading</em>) jusqu’à 90% de levier.
            </p>
          </Etape>
          <Etape titre="Le déclenchement" ton="perte">
            <p>
              Le jeudi noir, 24 octobre 1929. Le Dow Jones perd 11% en une journée. Puis le mardi 29 octobre, −12% supplémentaires. En quelques semaines,
              −50%. Le marché ne retrouvera son niveau de 1929 qu’en <G>1954</G> — soit 25 ans plus tard.
            </p>
          </Etape>
          <Etape titre="Enseignements" ton="accent">
            <Liste>
              <Point>L’effet de levier excessif est une bombe à retardement.</Point>
              <Point>
                Les banques centrales peuvent aggraver une crise par leurs erreurs (la FED a resserré au pire moment en 1931, ce qui a transformé un krach
                boursier en dépression mondiale).
              </Point>
              <Point>
                Ce qui a sauvé les USA : le <G>New Deal</G> de Roosevelt (1933) et les dépenses publiques massives.
              </Point>
            </Liste>
          </Etape>
        </Chronologie>
        <Photo
          fichier="Crowd_outside_nyse.jpg"
          alt="Foule devant le New York Stock Exchange en octobre 1929"
          legende="Foule paniquée devant le New York Stock Exchange, 24 octobre 1929. Le krach effacera 89% de la valeur du Dow Jones sur 3 ans."
          credit="Wikimedia Commons - Public domain"
        />
      </Section>

      <Section {...s("black-monday")}>
        <Chronologie>
          <Etape titre="Contexte">
            <p>
              Les bourses montent fort depuis 5 ans, nouvelles techniques de <em>program trading</em> (algorithmes), portefeuilles dits « assurés » via
              des options.
            </p>
          </Etape>
          <Etape titre="Le déclenchement" ton="perte">
            <p>
              Le 19 octobre 1987, le Dow Jones perd <G>−22,6% en une seule séance</G>. Record absolu jamais égalé. Cause probable : les algorithmes de
              vente automatique ont déclenché une cascade de ventes, sans intervention humaine pour l’arrêter.
            </p>
          </Etape>
          <Etape titre="Enseignement clé" ton="accent">
            <p>
              Les systèmes automatisés peuvent créer des <G>boucles de rétroaction</G> catastrophiques. C’est ce qui a mené à l’introduction des{" "}
              <G>coupe-circuits</G> (circuit breakers) à Wall Street : la Bourse s’arrête automatiquement si ça baisse de trop.
            </p>
          </Etape>
        </Chronologie>
        <BlackMonday />
      </Section>

      <Section {...s("bulle-internet")}>
        <Chronologie>
          <Etape titre="Contexte">
            <p>
              Internet se démocratise. Toute entreprise avec « .com » dans son nom voit sa valorisation multipliée par 10. Des sociétés sans chiffre
              d’affaires valent des milliards. Exemple emblématique : <G>Pets.com</G>, valorisée 300M$ en 2000, en faillite en 2001.
            </p>
          </Etape>
          <Etape titre="Le pic" ton="gain">
            <p>
              Le Nasdaq atteint 5048 points en mars 2000. Il ne reviendra à ce niveau qu’en <G>2015</G> — quinze ans de stagnation.
            </p>
          </Etape>
          <Etape titre="La chute" ton="perte">
            <p>−78% sur le Nasdaq entre 2000 et 2002. Destruction de 5 trillions de dollars de capitalisation boursière.</p>
          </Etape>
          <Etape titre="Enseignement clé" ton="accent">
            <p>
              Une technologie révolutionnaire peut être <G>réelle</G> (internet était bien révolutionnaire) mais les <G>valorisations</G> peuvent être
              totalement délirantes. La question n’est pas « cette technologie va-t-elle changer le monde ? » mais « à quel prix est-ce que je l’achète ? ».
            </p>
          </Etape>
        </Chronologie>
      </Section>

      <Section {...s("subprimes")}>
        <Chronologie>
          <Etape titre="Contexte">
            <p>
              Les banques américaines ont accordé pendant des années des crédits immobiliers à des ménages qui ne pouvaient pas rembourser (les{" "}
              <em>subprimes</em>). Ces crédits ont été « titrisés » (transformés en produits financiers complexes, les CDO) et revendus dans le monde
              entier comme s’ils étaient sûrs.
            </p>
          </Etape>
          <Etape titre="Le déclenchement" ton="perte">
            <p>
              En 2007, les prix de l’immobilier US commencent à baisser. Les ménages ne remboursent plus. Les CDO perdent leur valeur. En septembre 2008,{" "}
              <G>Lehman Brothers</G> fait faillite — la 4e plus grosse banque d’investissement américaine. Panique mondiale.
            </p>
          </Etape>
          <Etape titre="La chute" ton="perte">
            <p>
              S&amp;P 500 −57% entre octobre 2007 et mars 2009. Or : <G>+25%</G> sur la même période (flight to quality). Bons du Trésor US 10 ans :
              rendement de 5% à 2%, prix des obligations explose.
            </p>
          </Etape>
          <Etape titre="Enseignement clé" ton="accent">
            <p>
              La complexité financière est une arme à double tranchant. Quand personne ne comprend les produits qu’il détient, la confiance s’effondre en
              quelques jours. Warren Buffett avait qualifié les dérivés d’<em>« armes de destruction massive financière »</em> dès 2003.
            </p>
          </Etape>
        </Chronologie>
        <Photo
          fichier="Lehman_Brothers_Times_Square_by_David_Shankbone.jpg"
          alt="Le siège de Lehman Brothers à Times Square"
          legende="Le siège de Lehman Brothers à Times Square, peu après sa faillite en septembre 2008. La 4e plus grosse banque d’investissement américaine s’est écroulée en un week-end."
          credit="Wikimedia - David Shankbone, CC BY 3.0"
        />
      </Section>

      <Section {...s("covid")}>
        <Chronologie>
          <Etape titre="Contexte">
            <p>Marchés au plus haut, chômage US au plus bas depuis 50 ans, les investisseurs pensent que rien ne peut arriver.</p>
          </Etape>
          <Etape titre="Le déclenchement" ton="perte">
            <p>
              Le 11 mars 2020, l’OMS déclare une pandémie. En 23 jours, le S&amp;P 500 perd <G>−34%</G>. Record de vitesse historique — plus rapide que
              1929, 1987 ou 2008.
            </p>
          </Etape>
          <Etape titre="Le rebond" ton="gain">
            <p>
              En moins de 6 mois, le marché a récupéré toutes ses pertes. Pourquoi ? Parce que les banques centrales ont injecté{" "}
              <G>plus de 10 000 milliards de dollars</G> dans l’économie mondiale. La FED a baissé ses taux à zéro en une semaine.
            </p>
          </Etape>
          <Etape titre="Enseignement clé" ton="accent">
            <p>
              En 2020, on a appris qu’il y a désormais un <G>« put implicite » des banques centrales</G> sous les marchés. Quoi qu’il arrive, elles
              interviendront. Cela explique pourquoi le marché a quasiment ignoré les mauvaises nouvelles de 2020-2021 : tout le monde parie sur le
              sauvetage.
            </p>
          </Etape>
        </Chronologie>
      </Section>

      <Section {...s("lecons")}>
        <Encadre ton="info">
          <ListeEncadre>
            <Point>
              Les krachs arrivent tous les 8-12 ans en moyenne. C’est un <G>fait statistique</G>.
            </Point>
            <Point>Chaque fois, les investisseurs disent « cette fois c’est différent ». Ce ne l’est jamais vraiment.</Point>
            <Point>Le meilleur moment pour acheter est souvent le plus inconfortable (mars 2009, mars 2020).</Point>
            <Point>Diversifier à travers des actifs décorrélés (actions, obligations, or, cash) reste la seule défense sérieuse.</Point>
            <Point>Les liquidités disponibles (cash) sont aussi une position : elles permettent d’acheter quand tout est bradé.</Point>
          </ListeEncadre>
        </Encadre>
      </Section>

      <Section {...s("synthese")} etiquette="Synthèse">
        <SyntheseCrises />
      </Section>
    </>
  );
}
