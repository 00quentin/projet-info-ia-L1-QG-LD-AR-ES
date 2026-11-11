import { CarteTexte, Chapeau, Encadre, G, Grille, P, Section } from "@/components/academie/blocs";
import { Formule } from "@/components/academie/Formule";
import { FrontiereEfficiente } from "@/components/academie/illustrations/FrontiereEfficiente";
import { MatriceCorrelations } from "@/components/academie/MatriceCorrelations";
import { SyntheseAllocation } from "@/components/academie/Syntheses";
import { sectionsDe } from "./modules";

const s = sectionsDe("construction");

export function ContenuConstruction() {
  return (
    <>
      <Chapeau>
        Choisir une stratégie ne suffit pas. Il faut savoir <G>assembler</G> les briques pour que le portefeuille total soit plus robuste que la somme
        de ses parties. C’est la grande idée de Markowitz, qui lui a valu le Nobel en 1990.
      </Chapeau>

      <Section {...s("diversification")}>
        <P>
          Harry Markowitz, 1952. Il démontre mathématiquement que <G>diversifier permet de réduire le risque sans réduire le rendement</G> — à condition
          que les actifs ne soient pas parfaitement corrélés. C’est le seul résultat de la finance qui ressemble à un « repas gratuit ».
        </P>
        <P>
          <G>Exemple chiffré</G> : un actif A à vol 20%/an + un actif B à vol 20%/an, avec une corrélation de 0% (donc indépendants), donnent un
          portefeuille 50/50 à vol <G>14,1%</G> (et non 20%). On a réduit le risque de 30% sans rien sacrifier au rendement. La magie vient de :
        </P>
        <Formule tex={String.raw`\sigma_p^2 = w_A^2 \sigma_A^2 + w_B^2 \sigma_B^2 + 2 w_A w_B \rho_{AB} \sigma_A \sigma_B`} />
      </Section>

      <Section {...s("frontiere")}>
        <P>
          En combinant N actifs avec des poids variables, on génère une infinité de portefeuilles possibles. Markowitz montre qu’il existe une{" "}
          <G>frontière</G> : pour chaque niveau de risque, il y a un portefeuille qui maximise le rendement. Tous les portefeuilles <G>en-dessous</G> de
          cette courbe sont sous-optimaux (on peut faire mieux à risque égal).
        </P>
        <P>
          Les gérants institutionnels visent cette frontière. En pratique, c’est compliqué car les rendements futurs sont incertains, et les
          corrélations changent en crise. Mais l’intuition reste : <G>il existe un portefeuille idéal pour chaque profil de risque</G>.
        </P>
        <FrontiereEfficiente />
      </Section>

      <Section {...s("correlations")}>
        <MatriceCorrelations />
        <P>
          <G>Lecture</G> : actions et obligations ont une corrélation <G>négative</G> (−0,30) en régime normal — c’est le fondement du 60/40. Mais en
          2022, cette corrélation est passée <G>positive</G> (+0,50), causant le pire drawdown du 60/40 depuis 1969.
        </P>
        <Encadre ton="alerte">
          <p>
            <G>Le piège des corrélations en crise :</G>
          </p>
          <p>
            En 2008 et en mars 2020, <G>toutes les corrélations sont montées vers 1</G>. Actions, obligations corporate, immobilier, matières premières
            ont chuté ensemble. Seuls l’or, les Treasuries longs et le cash ont protégé.
          </p>
          <p>
            C’est ce qu’on appelle <G>le risque systémique</G> : la diversification protège en régime normal, mais s’effondre exactement quand on en a
            le plus besoin. D’où l’importance d’avoir 5-10% en or physique ou en cash pour les vrais chocs.
          </p>
        </Encadre>
      </Section>

      <Section {...s("rebalancement")}>
        <P>
          Sans intervention, un portefeuille 60/40 dérive. Si les actions montent fort, vous vous retrouvez avec 70/30 sans l’avoir choisi — vous prenez
          plus de risque qu’initialement voulu.
        </P>
        <P>
          <G>Le rebalancement</G> consiste à racheter périodiquement (annuellement ou quand l’écart dépasse 5 points) la cible 60/40. Mécaniquement,
          cela revient à <G>vendre ce qui a monté et acheter ce qui a baissé</G> — l’inverse exact du comportement émotionnel naturel.
        </P>
        <P>
          <G>Effet mesuré</G> : un portefeuille 60/40 rebalancé annuellement bat un portefeuille « laissé courir » d’environ <G>+0,3%/an</G> sur 30
          ans. Modeste mais cumulé sur la vie d’un investisseur, c’est significatif.
        </P>
      </Section>

      <Section {...s("buckets")}>
        <P>
          Une approche pragmatique recommandée par les conseillers : segmenter le patrimoine par <G>horizon de besoin</G> :
        </P>
        <Grille colonnes={3}>
          <CarteTexte etiquette="1" titre="Bucket 1 (0-2 ans)">
            <p>Cash + livrets. Sécurité absolue. Rendement faible mais accessible.</p>
          </CarteTexte>
          <CarteTexte etiquette="2" titre="Bucket 2 (2-7 ans)">
            <p>Obligations courtes + foncier. Stabilité, peu de volatilité.</p>
          </CarteTexte>
          <CarteTexte etiquette="3" titre="Bucket 3 (7+ ans)">
            <p>Actions + actifs risqués. Rendement long terme malgré la volatilité.</p>
          </CarteTexte>
        </Grille>
        <P>
          Le bucket 1 sert à dormir tranquille. Le bucket 3 sert à enrichir. Le bucket 2 fait le pont. Cette structure réduit le{" "}
          <G>risque de séquence</G> (avoir besoin de vendre en bas de cycle).
        </P>
      </Section>

      <Section {...s("synthese")} etiquette="Synthèse">
        <SyntheseAllocation />
      </Section>
    </>
  );
}
