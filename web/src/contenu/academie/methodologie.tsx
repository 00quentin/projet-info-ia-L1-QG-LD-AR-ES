import { Chapeau, Encadre, G, ListeEncadre, P, Point, Section } from "@/components/academie/blocs";
import { Formule, M } from "@/components/academie/Formule";
import { SynthesePipeline } from "@/components/academie/Syntheses";
import { sectionsDe } from "./modules";

const s = sectionsDe("methodologie");
const R = String.raw;

export function ContenuMethodologie() {
  return (
    <>
      <Chapeau>Pour les utilisateurs exigeants (et les professeurs), voici les formules exactes implémentées dans le terminal.</Chapeau>

      <Section {...s("volatilite")}>
        <Formule tex={R`\sigma_{\text{annuel}} = \sigma_{\text{quotidien}} \times \sqrt{252}`} />
        <P>
          On multiplie l’écart-type des rendements journaliers par √252 (nombre de jours de cotation dans l’année). Pourquoi √252 et pas 252 ? Parce
          que la variance s’additionne linéairement avec le temps, donc l’écart-type croît en √t. C’est une conséquence du théorème central limite.
        </P>
      </Section>

      <Section {...s("sharpe")}>
        <Formule tex={R`\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}`} />
        <P>
          <M tex="R_p" /> = rendement annualisé du portefeuille, <M tex="R_f" /> = taux sans risque (le taux de dépôt de la BCE, lu sur FRED : c’est le
          placement sans risque d’un épargnant en euros ; 2 % si FRED est injoignable), <M tex={R`\sigma_p`} /> = volatilité annualisée.
        </P>
        <P>
          Créé par William Sharpe en 1966 (Prix Nobel 1990). C’est <G>la</G> métrique universellement utilisée par les gérants professionnels. Un
          Sharpe de 1 signifie que pour chaque unité de risque prise, vous avez gagné 1 unité de rendement au-dessus du taux sans risque. En dessous de
          0,5, l’effort de prendre du risque n’en vaut pas la peine.
        </P>
      </Section>

      <Section {...s("drawdown")}>
        <Formule tex={R`DD_{\max} = \max_{t} \left( \frac{\text{Peak}_t - V_t}{\text{Peak}_t} \right)`} />
        <P>
          <M tex={R`\text{Peak}_t`} /> = plus-haut historique au temps <M tex="t" />, <M tex="V_t" /> = valeur au temps <M tex="t" />. C’est la pire
          chute subie depuis un sommet précédent. Mesure cruciale car elle reflète la <G>vraie souffrance</G> psychologique d’un investisseur : voir son
          capital fondre de −30% est bien plus traumatisant qu’une volatilité élevée.
        </P>
        <P>
          Pendant le krach de 1929, le Dow Jones a subi un drawdown de <G>−89%</G> sur 3 ans. Pendant 2008, le S&amp;P 500 a fait <G>−57%</G>. Pendant
          le COVID, <G>−34% en 23 jours</G>.
        </P>
      </Section>

      <Section {...s("var")}>
        <Formule tex={R`VaR_{95\%} = \text{Percentile}_{5\%}(\text{rendements})`} />
        <P>
          La VaR 95% à 1 jour répond à la question : <em>« Quelle est la perte maximale que je ne dépasserai pas dans 95% des cas en une journée ? »</em>.
          C’est le rendement situé au 5e percentile (5% les pires rendements).
        </P>
        <P>
          <G>Attention</G> : la VaR ne dit rien sur ce qui se passe dans les 5% restants — les <em>tail risks</em>. C’est pour ça qu’on la complète
          souvent par la <G>CVaR</G> (Conditional VaR), qui calcule la moyenne des pertes <G>au-delà</G> de la VaR. Beaucoup plus conservateur.
        </P>
      </Section>

      <Section {...s("mbg")}>
        <Formule tex={R`\frac{dS_t}{S_t} = \mu \, dt + \sigma \, dW_t`} />
        <P>En discrétisant sur un pas journalier :</P>
        <Formule tex={R`S_{t+1} = S_t \times \exp(\mu + \sigma \cdot Z_t)`} />
        <P>
          Avec <M tex={R`Z_t \sim \mathcal{N}(0, 1)`} /> un tirage gaussien à chaque pas de temps. C’est exactement la formule utilisée dans le code de
          Quant Terminal pour le modèle « Classique » (Probabiliste).
        </P>
        <P>
          Le <M tex={R`\mu`} /> (drift) vient du choc estimé par notre IA : il est réglé pour que la trajectoire <G>médiane</G> atteigne ce choc à la fin
          de l’horizon. Le <M tex={R`\sigma`} /> (volatilité) est mesuré sur les vrais rendements de chaque actif.
        </P>
        <P>
          Les tirages <M tex="Z_t" /> des différents actifs ne sont <G>pas indépendants</G> : on mesure la matrice de corrélation <M tex="C" /> sur deux
          ans de vrais rendements, puis on corrèle les tirages grâce à sa décomposition de Cholesky (<M tex="C = L L^T" />,{" "}
          <M tex={R`Z = L \cdot \varepsilon`} />
          ). Ainsi, quand les actions chutent dans une simulation, le Nasdaq chute avec le S&amp;P 500 et l’or réagit comme il le fait en réalité.
        </P>
      </Section>

      <Section {...s("euros")}>
        <P>
          Votre capital est en euros, mais le S&amp;P 500, l’or ou le Bitcoin cotent en dollars. La performance réellement vécue par un investisseur
          européen est donc :
        </P>
        <Formule tex={R`1 + r_{EUR} = \frac{1 + r_{USD}}{1 + r_{EUR/USD}}`} />
        <P>
          En simulation, l’EUR/USD est lui-même simulé (choc estimé par l’IA, corrélé aux autres actifs). En backtest, on utilise les{" "}
          <G>taux de référence officiels de la Banque centrale européenne</G>, jour par jour.
        </P>
      </Section>

      <Section {...s("monte-carlo")}>
        <P>
          On simule <M tex={R`N=1\,000`} /> trajectoires. Pour chaque jour <M tex="t" /> et chaque actif :
        </P>
        <Formule tex={R`\text{Médiane}_t = \text{percentile}_{50}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})`} />
        <Formule tex={R`\text{Bas}_t = \text{percentile}_{5}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})`} />
        <Formule tex={R`\text{Haut}_t = \text{percentile}_{95}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})`} />
        <P>
          L’intervalle [Bas, Haut] constitue la <G>bande de confiance à 90%</G> : dans 90% des cas simulés, le prix à l’instant <M tex="t" /> se trouve
          dans cette bande.
        </P>
        <P>
          Les métriques de risque (volatilité, drawdown, VaR) sont calculées <G>sur chaque trajectoire du portefeuille</G>, pas sur la médiane : la
          médiane est une courbe lissée où le hasard s’annule, y mesurer le risque le sous-estimerait fortement.
        </P>
        <P>
          La méthode Monte-Carlo converge en <M tex={R`O(1/\sqrt{N})`} /> : pour doubler la précision, il faut quadrupler le nombre de simulations. Avec
          1 000 simulations, la précision est typiquement de l’ordre de ±1% sur les percentiles — confortable pour un outil éducatif. Les grandes banques
          utilisent couramment 10 000 à 1 000 000 de simulations pour leurs calculs réglementaires (Bâle III, FRTB).
        </P>
      </Section>

      <Section {...s("limites")}>
        <Encadre ton="alerte">
          <p>
            <G>Pour l’honnêteté intellectuelle</G>, voici les limites de Quant Terminal :
          </p>
          <ListeEncadre>
            <Point>
              Les volatilités sont supposées <G>constantes</G>, alors qu’en réalité elles se regroupent en clusters (effet GARCH).
            </Point>
            <Point>
              Les corrélations sont mesurées sur les <G>2 dernières années</G> et supposées stables, alors qu’en crise elles montent toutes vers 1 (voir
              2008).
            </Point>
            <Point>
              L’IA fournit une estimation <G>globale</G> du choc, pas une trajectoire fine dans le temps.
            </Point>
            <Point>
              Les distributions restent <G>gaussiennes</G>, sauf dans le mode Historique (qui rejoue de vraies séances).
            </Point>
            <Point>
              Les obligations sont représentées par des <G>ETF obligataires</G> et les indices MSCI par des ETF : c’est le prix de ces fonds qui est
              suivi.
            </Point>
            <Point>
              En simulation, seule la conversion <G>dollar → euro</G> est modélisée (yen et livre sont convertis uniquement en backtest).
            </Point>
            <Point>
              Pas de prise en compte des <G>coûts de transaction</G>, des <G>spreads bid-ask</G>, ni de la <G>liquidité</G>.
            </Point>
          </ListeEncadre>
          <p>
            Quant Terminal est un outil <G>pédagogique</G>. Pour un usage professionnel réel, il faudrait ajouter ces raffinements et calibrer le modèle
            sur des données de marché en temps réel.
          </p>
        </Encadre>
      </Section>

      <Section {...s("pipeline")} etiquette="Synthèse">
        <SynthesePipeline />
      </Section>
    </>
  );
}
