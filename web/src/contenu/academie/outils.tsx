import { Chapeau, Encadre, G, Liste, P, Point, Section } from "@/components/academie/blocs";
import { Chandelier } from "@/components/academie/illustrations/Chandelier";
import { LienAcademie } from "@/components/academie/LienAcademie";
import { sectionsDe } from "./modules";

const s = sectionsDe("outils");

export function ContenuOutils() {
  return (
    <>
      <Chapeau>
        Un graphique financier n’est pas un simple dessin : c’est le résultat de millions d’ordres d’achat et de vente, de décisions humaines et
        algorithmiques, de nouvelles macro-économiques et d’émotions collectives. Savoir lire un graphique, c’est savoir lire la psychologie du marché.
      </Chapeau>

      <Section {...s("prix-absolus")}>
        <P>
          Un piège courant chez les débutants : comparer les prix bruts. Si l’action Apple vaut 170$ et qu’une petite biotech vaut 3$, laquelle performe
          le mieux sur un an ? Impossible à dire avec les prix absolus. Peut-être que la biotech valait 1$ il y a un an (elle a fait x3), tandis qu’Apple
          valait 150$ (elle n’a fait que +13%).
        </P>
        <Encadre ton="info">
          <p>
            <G>La règle professionnelle :</G> les prix bruts ne disent rien.
          </p>
          <p>
            Seules les <G>variations relatives</G> comptent.
          </p>
          <p>C’est pour cela que tous les graphiques comparatifs sont affichés en « base 100 ».</p>
        </Encadre>
      </Section>

      <Section {...s("base-100")}>
        <P>
          On divise chaque prix par le prix du premier jour, puis on multiplie par 100. Résultat : tous les actifs démarrent à 100, et on lit
          directement les pourcentages sur l’axe.
        </P>
        <Liste>
          <Point>
            Une courbe qui finit à <G>120</G> = +20%
          </Point>
          <Point>
            Une courbe qui finit à <G>85</G> = −15%
          </Point>
          <Point>
            Une courbe qui finit à <G>250</G> = +150% (l’actif a été multiplié par 2,5)
          </Point>
        </Liste>
        <P>
          Sur les graphiques de Quant Terminal, toutes les courbes commencent exactement à 100. Celle qui monte le plus a le plus performé. C’est aussi
          simple que ça.
        </P>
      </Section>

      <Section {...s("heatmap")}>
        <P>
          La heatmap (ou carte thermique) est un outil de synthèse redoutable. Sur un seul écran, vous voyez d’un coup d’œil qui a gagné et qui a perdu.
          Vert foncé = gros gain, rouge foncé = grosse perte.
        </P>
        <P>
          <G>Pourquoi c’est crucial ?</G> Parce que sur les marchés, l’argent ne disparaît jamais : il se <G>déplace</G>. Quand les actions
          s’effondrent, l’argent va quelque part — typiquement dans les obligations d’État et l’or. On appelle cela un <em>flight to quality</em> (fuite
          vers la qualité). Une heatmap permet de voir cette rotation en temps réel.
        </P>
        <Encadre ton="alerte">
          <p>
            <G>Piège classique :</G> regarder uniquement la performance d’un actif.
          </p>
          <p>
            Un +10% sur une action qui a une volatilité de 40% est bien moins impressionnant qu’un +8% sur une obligation qui a une volatilité de 5%.
          </p>
          <p>
            La performance doit toujours être mise en relation avec le risque pris (voir le{" "}
            <LienAcademie ancre="methodologie-sharpe">Sharpe Ratio dans la Méthodologie</LienAcademie>).
          </p>
        </Encadre>
      </Section>

      <Section {...s("trajectoire")}>
        <P>
          Une courbe de cours n’est <G>jamais</G> lisse. Elle tremble, elle zigzague, elle rebondit. Ce tremblement quotidien s’appelle le{" "}
          <G>bruit de marché</G>. Ce qui compte, c’est la <G>tendance sous-jacente</G>. Trois signaux à identifier :
        </P>
        <Liste>
          <Point>
            <G>La pente moyenne</G> : est-ce que globalement ça monte, descend, ou stagne ?
          </Point>
          <Point>
            <G>L’amplitude des oscillations</G> : est-ce que les variations journalières sont de 0,5%, 2%, ou 10% ? Plus elles sont grandes, plus
            l’actif est risqué.
          </Point>
          <Point>
            <G>Les cassures</G> : les moments où la courbe change brutalement de direction. Ce sont souvent des événements majeurs (décision de banque
            centrale, résultats d’entreprise, actualité géopolitique).
          </Point>
        </Liste>
        <Chandelier />
      </Section>

      <Section {...s("monte-carlo")}>
        <P>
          Quand vous activez le mode Monte-Carlo, les graphiques affichent non pas <G>une</G> trajectoire, mais une <G>bande colorée</G> autour de la
          trajectoire médiane. Cette bande représente l’intervalle dans lequel la vraie trajectoire a 90% de chances de se situer.
        </P>
        <P>
          <G>Pourquoi c’est essentiel ?</G> Parce qu’une simulation unique, c’est un coup de chance (ou de malchance). En moyennant 1 000 simulations,
          on obtient une vision <G>statistiquement robuste</G> de l’avenir. Plus la bande est large, plus l’incertitude est grande sur cet actif.
        </P>
      </Section>
    </>
  );
}
