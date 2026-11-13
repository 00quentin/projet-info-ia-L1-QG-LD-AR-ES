import type { ReactNode } from "react";
import { TrendingDown, TrendingUp } from "lucide-react";
import { CarteTexte, Chapeau, G, Grille, Liste, P, Point, Section, SousTitre } from "@/components/academie/blocs";
import { EchelleVix } from "@/components/academie/EchelleVix";
import { Photo } from "@/components/academie/Photo";
import { sectionsDe } from "./modules";

const s = sectionsDe("macro");

function ListeCarte({ children }: { children: ReactNode }) {
  return <ul className="flex flex-col gap-2">{children}</ul>;
}

export function ContenuMacro() {
  return (
    <>
      <Chapeau>
        Il y a des milliers d’actions cotées, des dizaines de devises, des centaines de matières premières. Mais <G>trois forces invisibles</G>{" "}
        déterminent la direction globale de tout cela : les taux d’intérêt, l’inflation, et la confiance des investisseurs.
      </Chapeau>

      <Section {...s("banques-centrales")}>
        <P>
          La Réserve Fédérale américaine (FED), la Banque Centrale Européenne (BCE), la Banque du Japon (BoJ), la Banque Populaire de Chine (PBoC) — ces
          quatre institutions contrôlent l’essentiel de la liquidité mondiale. Leur outil principal : le <G>taux directeur</G>, qui fixe le prix auquel
          les banques commerciales peuvent emprunter de l’argent.
        </P>
        <Grille>
          <CarteTexte icone={<TrendingUp className="size-5 shrink-0 text-gain" aria-hidden />} titre="Quand les taux sont bas (argent gratuit) :">
            <ListeCarte>
              <Point>Les entreprises empruntent massivement pour investir, innover, racheter leurs concurrents.</Point>
              <Point>Les ménages empruntent pour acheter des maisons, des voitures.</Point>
              <Point>
                Les investisseurs, ne trouvant plus de rendement dans les obligations (qui paient peu), se ruent sur les <G>actions</G> et les actifs
                risqués. La Bourse explose.
              </Point>
              <Point>Les cryptos, les valeurs tech non rentables, l’immobilier, tout gonfle.</Point>
              <Point>
                Période emblématique : <G>2009-2021</G>, avec des taux proches de zéro après la crise de 2008.
              </Point>
            </ListeCarte>
          </CarteTexte>
          <CarteTexte icone={<TrendingDown className="size-5 shrink-0 text-loss" aria-hidden />} titre="Quand les taux sont hauts (argent cher) :">
            <ListeCarte>
              <Point>Les crédits deviennent difficiles. Les projets d’investissement sont reportés.</Point>
              <Point>Les entreprises endettées peinent à refinancer leur dette.</Point>
              <Point>
                Les investisseurs peuvent placer leur argent <G>sans risque</G> dans des Bons du Trésor à 5% — pourquoi prendre du risque sur des actions
                quand on peut gagner 5% en dormant ?
              </Point>
              <Point>Résultat : rotation massive vers les obligations, chute des actions et des cryptos.</Point>
              <Point>
                Période emblématique : <G>1979-1982</G> (Paul Volcker à la FED, taux à 20%), et <G>2022-2024</G> (Jerome Powell face à l’inflation
                post-COVID).
              </Point>
            </ListeCarte>
          </CarteTexte>
        </Grille>
        <Photo
          fichier="Marriner_S._Eccles_Federal_Reserve_Board_Building.jpg"
          alt="Le siège de la Réserve fédérale à Washington"
          legende="Le siège de la Federal Reserve à Washington D.C. C’est ici que se décident les taux directeurs qui orientent toute la liquidité mondiale."
          credit="Wikimedia Commons - Public domain"
        />
      </Section>

      <Section {...s("inflation")}>
        <P>
          Quand l’inflation est à 5%, cela signifie que le niveau général des prix augmente de 5% par an. Vos 100€ sur votre compte en banque conservent
          leur valeur nominale, mais perdent <G>5% de leur pouvoir d’achat</G> réel chaque année.
        </P>
        <P>
          Sur 10 ans avec 5% d’inflation constante, votre argent perd <G>40%</G> de sa valeur réelle. C’est pour cela qu’on dit que{" "}
          <em>« le cash est poubelle en période inflationniste »</em>.
        </P>
        <SousTitre>Comment se protéger de l’inflation ?</SousTitre>
        <P>
          On achète des choses <G>qu’on ne peut pas imprimer à l’infini</G> :
        </P>
        <Liste>
          <Point>
            <G>Or</G> : quantité physique limitée dans la croûte terrestre, actif refuge depuis 5000 ans. Pendant la crise des années 70 (inflation à 15%
            aux USA), l’or a été multiplié par 20.
          </Point>
          <Point>
            <G>Matières premières</G> (pétrole, cuivre, blé) : leur prix monte avec le coût de la vie.
          </Point>
          <Point>
            <G>Immobilier</G> : les loyers peuvent être indexés sur l’inflation.
          </Point>
          <Point>
            <G>Actions d’entreprises avec pricing power</G> : entreprises capables d’augmenter leurs prix sans perdre de clients (LVMH, Apple,
            Coca-Cola). On dit qu’elles ont une « douve » (<em>moat</em>) selon Warren Buffett.
          </Point>
          <Point>
            <G>Crypto</G> : Bitcoin a été inventé comme une réserve de valeur limitée à 21 millions d’unités. En théorie, c’est un hedge contre
            l’inflation — en pratique, c’est beaucoup plus corrélé au Nasdaq qu’on ne le pensait.
          </Point>
        </Liste>
        <Photo
          fichier="Line_at_a_gas_station,_June_15,_1979.jpg"
          alt="File de voitures devant une station-service en 1979"
          legende="Files d’attente aux stations-service pendant le choc pétrolier (ici en juin 1979). L’embargo OPEP a quadruplé le prix du baril en quelques mois, provoquant une stagflation mondiale."
          credit="Wikimedia Commons - Public domain (US Federal Govt)"
        />
      </Section>

      <Section {...s("courbe-taux")}>
        <P>
          Depuis 1960 aux États-Unis, <G>chaque récession a été précédée par une inversion de la courbe des taux</G>. C&apos;est l&apos;un des
          meilleurs signaux d&apos;alerte connus, mais pas un oracle : il a aussi donné de fausses alertes (en 1966, et l&apos;inversion de 2022-2023 n&apos;a
          pas été suivie d&apos;une récession dans les délais habituels). Le délai entre inversion et récession varie lui aussi beaucoup.
        </P>
        <P>
          <G>La courbe des taux</G>, c’est le graphique qui montre le rendement des obligations d’État à différentes maturités (3 mois, 2 ans, 5 ans, 10
          ans, 30 ans). En temps normal, plus on prête longtemps, plus on exige un rendement élevé (pour compenser le risque de long terme). La courbe
          monte donc de gauche à droite.
        </P>
        <P>
          <G>Quand la courbe s’inverse</G> (les taux courts deviennent plus hauts que les taux longs), c’est que le marché anticipe une baisse future des
          taux — donc une récession. C’est arrivé en 2000, 2006, 2019, et mi-2022. À chaque fois, récession 6 à 18 mois plus tard.
        </P>
      </Section>

      <Section {...s("dollar")}>
        <P>
          80% des transactions commerciales internationales se font en dollars. 60% des réserves de change des banques centrales du monde sont en
          dollars. C’est ce qu’on appelle le <G>privilège exorbitant</G> du dollar, formulé par Valéry Giscard d’Estaing en 1965.
        </P>
        <P>
          <G>Quand le dollar monte</G> (Dollar Index DXY en hausse) :
        </P>
        <Liste>
          <Point>Les pays émergents souffrent : leur dette est souvent en dollars, et il leur en coûte plus cher de la rembourser.</Point>
          <Point>L’or baisse mécaniquement (il est coté en dollars).</Point>
          <Point>Les matières premières deviennent plus chères pour le reste du monde → ralentissement de la demande.</Point>
        </Liste>
        <P>
          <G>Quand le dollar baisse</G> : effet inverse, les émergents respirent, l’or brille.
        </P>
      </Section>

      <Section {...s("vix")}>
        <P>
          Le <G>VIX</G> (Volatility Index), calculé par le CBOE de Chicago, mesure la volatilité <G>attendue</G> du S&amp;P 500 sur les 30 prochains
          jours, extraite du prix des options. On l’appelle aussi <em>« Fear Index »</em> (indice de la peur).
        </P>
        <EchelleVix />
        <P>
          <G>Utilité pratique :</G> si vous pensez qu’une crise arrive, acheter du VIX (via des ETF comme VXX) est une assurance contre les krachs
          boursiers.
        </P>
      </Section>
    </>
  );
}
