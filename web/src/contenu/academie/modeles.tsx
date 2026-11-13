import { CarteTexte, Chapeau, Encadre, G, Liste, P, Point, Section } from "@/components/academie/blocs";
import { Formule, M } from "@/components/academie/Formule";
import { Gaussienne } from "@/components/academie/illustrations/Gaussienne";
import Link from "next/link";
import { PARAMETRES } from "@/components/methodologie/donnees";
import { sectionsDe } from "./modules";

const s = sectionsDe("modeles");

export function ContenuModeles() {
  return (
    <>
      <Chapeau>
        Personne ne peut prédire le marché. Mais on peut <G>modéliser les lois statistiques</G> qui le régissent. C’est exactement ce que font les
        banques d’investissement, les hedge funds, et ce que fait Quant Terminal en arrière-plan.
      </Chapeau>

      <Section {...s("bachelier")}>
        <P>
          En 1900, un étudiant français nommé Louis Bachelier soutient une thèse révolutionnaire à la Sorbonne : « La théorie de la spéculation ». Il
          propose que les cours de Bourse se comportent comme des particules de pollen sous un microscope — un mouvement chaotique, le{" "}
          <G>mouvement brownien</G>.
        </P>
        <P>
          Ce modèle, approfondi ensuite par Einstein (1905) et formalisé par Itō (1940), est devenu le socle de toute la finance moderne. L’idée est
          simple : chaque jour, le prix varie d’une quantité tirée au hasard selon une loi normale (courbe en cloche de Gauss).
        </P>
        <Formule tex={String.raw`S_{t+1} = S_t \times (1 + \mu \, \Delta t + \sigma \, \sqrt{\Delta t} \, Z)`} />
        <P>Où :</P>
        <Liste>
          <Point>
            <M tex="S_t" /> = prix à l’instant <M tex="t" />
          </Point>
          <Point>
            <M tex={String.raw`\mu`} /> = tendance (drift) — estimée ici par notre IA à partir du scénario macro
          </Point>
          <Point>
            <M tex={String.raw`\sigma`} /> = volatilité — calibrée à partir des données historiques de l’actif
          </Point>
          <Point>
            <M tex="Z" /> = tirage aléatoire dans une loi normale centrée réduite <M tex={String.raw`\mathcal{N}(0,1)`} />
          </Point>
        </Liste>
        <P>
          C’est précisément la formule utilisée par le <G>modèle Black-Scholes</G> (Prix Nobel 1997) pour pricer les options, et par toutes les grandes
          banques pour leurs calculs de risque.
        </P>
      </Section>

      <Section {...s("loi-normale")}>
        <P>
          Le modèle brownien a un défaut majeur : il sous-estime <G>gravement</G> la probabilité des événements extrêmes. Selon une loi normale pure, un
          krach de −10% en un jour devrait arriver <G>une fois tous les 10 000 ans</G>. Pourtant, ça s’est produit plusieurs fois au cours des 40
          dernières années (1987, 2008, 2020).
        </P>
        <P>
          C’est ce que Benoît Mandelbrot a appelé les <G>queues épaisses</G> (<em>fat tails</em>) : la réalité des marchés n’est pas gaussienne, elle
          contient beaucoup plus d’événements extrêmes que ne le prédit la théorie classique. C’est ce qui a mené à l’effondrement du fonds{" "}
          <G>LTCM</G> en 1998 — deux prix Nobel au conseil, et pourtant ils ont fait faillite parce qu’ils avaient sous-estimé les queues épaisses du
          risque russe.
        </P>
        <Encadre ton="alerte">
          <p>
            <G>Leçon retenue :</G> en finance, les événements « impossibles » arrivent tous les 10 ans.
          </p>
          <p>Un bon modèle doit en tenir compte.</p>
        </Encadre>
        <Gaussienne />
      </Section>

      <Section {...s("trois-modeles")}>
        <div className="flex max-w-[46rem] flex-col gap-3">
          <CarteTexte etiquette="A" titre="Modèle Probabiliste (Brownien classique)">
            <p>
              Le plus courant. Chaque jour, variation = tendance + bruit gaussien. Bon pour les périodes calmes et les actifs stables (obligations, grands
              indices). Mais il rate les krachs.
            </p>
            <p>
              Le choc suit un <G>profil de crise</G> : il arrive vite, va trop loin, puis se résorbe en partie. Le point le plus bas tombe à{" "}
              {PARAMETRES.criseCreuxPctHorizon} % de l’horizon et va {PARAMETRES.criseDepassementPct} % plus loin que le choc final. C’est ce qu’on a vu
              en 1987, 2008 et 2020.
            </p>
          </CarteTexte>
          <CarteTexte etiquette="B" titre="Modèle Historique (queues épaisses)">
            <p>
              Au lieu de tirer des variations dans une loi théorique, on <G>rejoue de vraies séances de bourse</G> des deux dernières années, par blocs
              de 5 jours consécutifs piochés au hasard (<em>block bootstrap</em>). Les mouvements brusques et les jours où tout baisse en même temps sont
              donc ceux réellement observés — les <em>fat tails</em> de Mandelbrot sans avoir à les inventer. Idéal pour tester la résilience d’un
              portefeuille. (Si l’historique Yahoo manque, on utilise une loi de Student à queues épaisses.)
            </p>
            <p>Même profil de crise que le modèle Probabiliste : chute rapide, point extrême, reprise partielle.</p>
          </CarteTexte>
          <CarteTexte etiquette="C" titre="Modèle Machine Learning (momentum)">
            <p>
              Inspiré des stratégies <em>trend-following</em> des hedge funds comme Renaissance Technologies ou AQR. L’idée : quand une tendance est
              identifiée, elle s’auto-renforce (les investisseurs suivent le mouvement). Mathématiquement, chaque variation dépend un peu de celle de la
              veille (autocorrélation) et le choc estimé par l’IA se réalise de plus en plus vite avec le temps.
            </p>
          </CarteTexte>
        </div>
      </Section>

      <Section {...s("monte-carlo")}>
        <P>
          Nommée d’après le casino de Monaco, cette méthode a été inventée par Stanislaw Ulam et John von Neumann dans les années 1940, pendant le
          projet Manhattan (bombe atomique). L’idée est géniale : au lieu de résoudre analytiquement un problème impossible, on{" "}
          <G>lance des milliers de simulations aléatoires</G> et on regarde les résultats.
        </P>
        <P>
          Exemple concret : on veut savoir ce que donne 100 € investis dans notre portefeuille si on refait l’histoire 50 fois. On obtient 50 valeurs
          finales différentes. On calcule :
        </P>
        <Liste>
          <Point>
            La <G>médiane</G> (valeur centrale, 25 au-dessus et 25 en-dessous)
          </Point>
          <Point>
            Le <G>percentile 5%</G> (seulement 5% des fois on a fait pire)
          </Point>
          <Point>
            Le <G>percentile 95%</G> (seulement 5% des fois on a fait mieux)
          </Point>
        </Liste>
        <P>
          Ces 3 valeurs définissent la <G>bande de confiance à 90%</G>. C’est exactement ce que font les actuaires, les ingénieurs nucléaires, et les
          banquiers d’investissement chaque jour.
        </P>
        <P>
          Dans Quant Terminal, deux hasards se combinent. Le <G>bruit du marché</G> : chaque jour, un tirage au hasard. Le <G>doute de l’IA</G> :
          l’IA ne donne pas un seul choc, mais une fourchette (un choc bas, un choc central, un choc haut). Chaque simulation pioche son propre choc
          dans cette fourchette. Dans certaines, la crise est plus douce ; dans d’autres, plus dure. Et quand elle est plus dure, elle l’est pour
          presque tous les actifs à la fois ({PARAMETRES.incertitudePartCommunePct} % du tirage est commun).
        </P>
        <Encadre>
          <p>
            Une fourchette n’a de valeur que si elle contient souvent la réalité. On le vérifie sur des crises passées :{" "}
            <Link href="/validation" className="font-medium text-accent-ink hover:underline">
              voir la page Validation
            </Link>
            .
          </p>
        </Encadre>
      </Section>

      <Section {...s("rendements")}>
        <P>
          Petit point technique pour les puristes. Quand un prix passe de 100 à 110, on dit que le rendement est +10%. C’est le{" "}
          <G>rendement simple</G> : <M tex={String.raw`r = \frac{P_1 - P_0}{P_0}`} />.
        </P>
        <P>
          Mais quand on chaîne les rendements sur plusieurs périodes, les simples ne s’additionnent pas proprement (+10% puis −10% ne fait pas 0, mais
          −1%). C’est pour ça que les professionnels utilisent les <G>rendements logarithmiques</G> : <M tex={String.raw`r_{log} = \ln(P_1 / P_0)`} />.
          Ils s’additionnent parfaitement et suivent plus proprement une loi normale.
        </P>
      </Section>
    </>
  );
}
