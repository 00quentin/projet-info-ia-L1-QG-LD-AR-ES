import { Chapeau, Encadre, G, Liste, ListeEncadre, P, Point, Section, Tableau } from "@/components/academie/blocs";
import { Photo } from "@/components/academie/Photo";
import { SyntheseProfils } from "@/components/academie/Syntheses";
import { Pastille } from "@/components/ui/Carte";
import { sectionsDe } from "./modules";

const s = sectionsDe("strategies");

const niveau = (n: "Basse" | "Haute") => <Pastille ton={n === "Haute" ? "alerte" : "neutre"}>{n}</Pastille>;

export function ContenuStrategies() {
  return (
    <>
      <Chapeau>
        Il existe des centaines de stratégies d’investissement, mais 5 grandes écoles dominent la réflexion institutionnelle. Les comprendre permet de
        choisir sa propre voie.
      </Chapeau>

      <Section {...s("60-40")}>
        <P>
          <G>60% d’actions, 40% d’obligations.</G> C’est le portefeuille de référence depuis les années 1950. L’idée : les actions offrent la
          croissance, les obligations la stabilité. Quand les actions chutent, les obligations montent (flight to quality), ce qui amortit les pertes.
        </P>
        <P>
          <G>Performance historique</G> : environ +8% par an sur 50 ans aux USA, avec des drawdowns maximaux autour de −25%. Raisonnable, peu
          spectaculaire, mais fiable.
        </P>
        <P>
          <G>Limite actuelle :</G> en 2022, actions ET obligations ont chuté en même temps (car les taux ont flambé). Le 60/40 a fait −17%. Certains
          disent qu’il est « mort » — d’autres qu’il reste la base raisonnable pour la plupart des épargnants.
        </P>
      </Section>

      <Section {...s("all-weather")}>
        <P>
          Ray Dalio, fondateur du plus gros hedge fund du monde (Bridgewater, 150 milliards $), a conçu ce portefeuille qui doit fonctionner dans{" "}
          <G>tous les environnements économiques</G>. Il part d’un constat simple : il existe 4 régimes économiques possibles :
        </P>
        <Tableau
          legende="Les 4 régimes économiques selon Ray Dalio"
          entetes={["Régime", "Inflation", "Croissance", "Ce qui marche"]}
          lignes={[
            ["Goldilocks", niveau("Basse"), niveau("Haute"), "Actions, obligations corporate"],
            ["Stagflation", niveau("Haute"), niveau("Basse"), "Or, matières premières"],
            ["Reflation", niveau("Haute"), niveau("Haute"), "Actions, immobilier, matières premières"],
            ["Déflation", niveau("Basse"), niveau("Basse"), "Obligations longues, cash"],
          ]}
        />
        <P>
          <G>Sa recette</G> : 30% actions, 40% obligations longues US, 15% obligations moyennes, 7,5% or, 7,5% matières premières. L’idée : avoir une
          exposition à chaque régime pour ne jamais être totalement perdant.
        </P>
        <P>
          <G>Performance</G> : sur 40 ans, rendement annualisé de 8%, mais avec des drawdowns plus faibles que le 60/40. Moins brillant en bull market,
          plus résilient en crise.
        </P>
      </Section>

      <Section {...s("risk-parity")}>
        <P>
          Stratégie sœur du All Weather, développée dans les années 1990. Au lieu de répartir l’argent en pourcentages (60/40), on répartit le{" "}
          <G>risque</G>. Chaque classe d’actif contribue à parts égales à la volatilité totale du portefeuille.
        </P>
        <P>
          En pratique : comme les obligations sont 4x moins volatiles que les actions, un portefeuille risk parity contient souvent{" "}
          <G>beaucoup plus d’obligations en valeur</G> (avec parfois du levier pour booster leur rendement). Assez contre-intuitif pour un débutant.
        </P>
      </Section>

      <Section {...s("value")}>
        <P>
          Formalisé en 1934 par Benjamin Graham dans <em>Security Analysis</em> et <em>The Intelligent Investor</em>, puis rendu célèbre par son élève
          Warren Buffett.
        </P>
        <P>
          <G>Principe</G> : chaque action a une <G>valeur intrinsèque</G> (basée sur ses profits futurs actualisés). Le marché est parfois irrationnel
          et vend une action bien en-dessous de cette valeur. Le value investor achète alors, attend que le marché redevienne rationnel, et vend quand
          le prix dépasse la valeur intrinsèque.
        </P>
        <P>
          <G>Les critères de Buffett :</G>
        </P>
        <Liste>
          <Point>
            Entreprise avec une <G>« douve économique »</G> durable (brevets, marque forte, effet réseau)
          </Point>
          <Point>Management de qualité</Point>
          <Point>Faible endettement</Point>
          <Point>Historique de profits stables</Point>
          <Point>
            Prix d’achat <G>raisonnable</G> par rapport aux profits (ratio P/E bas)
          </Point>
        </Liste>
        <P>
          <G>Exemples emblématiques</G> : Coca-Cola (acheté en 1988, x20 depuis), Apple (x6 depuis 2016), American Express.
        </P>
        <Photo
          fichier="Warren_Buffett_KU_Visit.jpg"
          alt="Portrait de Warren Buffett"
          legende="Warren Buffett, élève de Benjamin Graham et figure emblématique du value investing. Berkshire Hathaway a fait +20%/an sur 60 ans en achetant des entreprises sous-évaluées avec une « douve économique » durable."
          credit="Wikimedia Commons - CC BY 2.0"
        />
      </Section>

      <Section {...s("momentum")}>
        <P>
          Stratégie opposée au value. L’idée : <em>« the trend is your friend »</em> (la tendance est ton amie). On achète ce qui monte, on vend ce qui
          baisse. Empiriquement, les actifs qui ont monté sur les 6-12 derniers mois ont tendance à continuer à monter sur les 3-6 mois suivants — c’est
          l’<G>effet momentum</G>, documenté par Jegadeesh &amp; Titman (1993).
        </P>
        <P>
          <G>Qui l’utilise ?</G> Les hedge funds systématiques comme <G>AHL (Man Group)</G>, <G>Winton Capital</G>, ou{" "}
          <G>Renaissance Technologies</G> (James Simons, le mathématicien le plus riche du monde). Ils gèrent des centaines de milliards sur ce
          principe.
        </P>
      </Section>

      <Section {...s("indexation")}>
        <P>
          En 1976, <G>John Bogle</G> crée le premier fonds indiciel grand public chez Vanguard. Son idée est radicale pour l’époque :{" "}
          <em>« Si la plupart des gérants actifs sous-performent l’indice après frais, autant juste acheter l’indice. »</em> La recherche académique lui
          a donné raison : sur 20 ans, <G>plus de 85% des gérants actions actifs aux US sous-performent le S&amp;P 500</G> (étude SPIVA 2024).
        </P>
        <P>
          <G>Principe</G> : acheter un ETF qui réplique un large indice (S&amp;P 500, MSCI World) avec des frais de 0,03% à 0,20% par an, contre 1,5% à
          2,5% pour un fonds actif. Sur 30 ans, l’écart de frais composé représente <G>~30% de capital final perdu</G> pour l’investisseur en fonds
          actif.
        </P>
        <P>
          <G>Pourquoi ça marche ?</G> Le marché est globalement efficient à long terme. Battre l’indice demande une information ou un timing
          exceptionnels — et même Buffett conseille à sa femme d’investir 90% en S&amp;P 500 dans son testament.
        </P>
      </Section>

      <Section {...s("dca")}>
        <P>
          Plutôt que d’investir un gros montant d’un coup, on investit <G>une somme fixe à intervalle régulier</G> (chaque mois). L’avantage : on lisse
          mécaniquement le prix d’achat, on achète plus de parts quand le marché est bas et moins quand il est haut.
        </P>
        <P>
          <G>Exemple concret</G> : 200€/mois pendant 20 ans dans un ETF MSCI World à 8% annualisé = <G>environ 118 000€</G> (dont 48 000€ versés et
          70 000€ d’intérêts composés). C’est la stratégie par défaut pour 99% des épargnants particuliers.
        </P>
        <P>
          <G>Limite</G> : sur le long terme (&gt;10 ans), <G>investir d’un coup</G> (« lump sum ») bat le DCA dans ~70% des cas, parce que les marchés
          montent en moyenne. Le DCA est surtout un outil <G>psychologique</G> qui réduit le regret en cas de krach juste après un gros versement.
        </P>
      </Section>

      <Section {...s("facteurs")}>
        <P>
          Initiée par <G>Eugene Fama</G> (Prix Nobel 2013) et <G>Kenneth French</G> dans les années 1990. Ils identifient des{" "}
          <G>facteurs de risque</G> systématiques qui expliquent les rendements au-delà du simple beta de marché :
        </P>
        <Liste>
          <Point>
            <G>Value</G> : actions sous-évaluées (faible P/B, P/E) — surperformance historique +2-4%/an
          </Point>
          <Point>
            <G>Size</G> : petites capitalisations — surperformance +1-3%/an, mais plus volatile
          </Point>
          <Point>
            <G>Momentum</G> : titres en tendance haussière 6-12 mois — +3-5%/an
          </Point>
          <Point>
            <G>Quality</G> : entreprises rentables et peu endettées — +1-2%/an, plus stable en crise
          </Point>
          <Point>
            <G>Low volatility</G> : actions à faible vol surperforment à long terme (paradoxe !)
          </Point>
        </Liste>
        <P>
          En pratique, on construit des portefeuilles « smart beta » en combinant ces facteurs. AQR, Dimensional Fund Advisors et BlackRock sont les
          leaders mondiaux du factor investing.
        </P>
      </Section>

      <Section {...s("choisir")}>
        <Encadre ton="info">
          <p>Il n’y a pas de « meilleure » stratégie dans l’absolu. Tout dépend de :</p>
          <ListeEncadre>
            <Point>
              <G>Votre horizon</G> : 5 ans vs 30 ans, ce n’est pas la même chose.
            </Point>
            <Point>
              <G>Votre tolérance au risque</G> : pouvez-vous dormir si votre portefeuille perd −40% ?
            </Point>
            <Point>
              <G>Vos objectifs</G> : préservation du capital, rendement, héritage ?
            </Point>
            <Point>
              <G>Vos compétences</G> : le value investing demande de savoir analyser un bilan, le momentum d’avoir une discipline de fer.
            </Point>
          </ListeEncadre>
        </Encadre>
      </Section>

      <Section {...s("synthese")} etiquette="Synthèse">
        <SyntheseProfils />
      </Section>
    </>
  );
}
