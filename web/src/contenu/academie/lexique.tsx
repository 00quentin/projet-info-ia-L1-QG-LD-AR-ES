import { Glossaire, Section, Terme } from "@/components/academie/blocs";
import { SyntheseLexique } from "@/components/academie/Syntheses";
import { sectionsDe } from "./modules";

const s = sectionsDe("lexique");

export function ContenuLexique() {
  return (
    <>
      <Section {...s("marches")}>
        <Glossaire>
          <Terme nom="Bull Market">Marché haussier (image du taureau qui attaque de bas en haut).</Terme>
          <Terme nom="Bear Market">Marché baissier (−20% minimum depuis le pic). L’ours attaque de haut en bas.</Terme>
          <Terme nom="Correction">Baisse entre −10% et −20%. Saine et fréquente.</Terme>
          <Terme nom="Krach">Chute brutale et rapide (&gt;−10% en quelques jours).</Terme>
          <Terme nom="Rally">Hausse rapide après une baisse.</Terme>
          <Terme nom="Melt-up">Hausse euphorique et irrationnelle (comme fin 2020-2021).</Terme>
        </Glossaire>
      </Section>

      <Section {...s("banques-centrales")}>
        <Glossaire>
          <Terme nom="Hawkish" precision="faucon">
            Banquier central qui veut monter les taux pour combattre l’inflation.
          </Terme>
          <Terme nom="Dovish" precision="colombe">
            Banquier central qui veut baisser les taux pour stimuler l’économie.
          </Terme>
          <Terme nom="Quantitative Easing (QE)">Impression de monnaie par la banque centrale pour acheter des actifs. Stimule l’économie.</Terme>
          <Terme nom="Quantitative Tightening (QT)">Opération inverse : la banque centrale réduit son bilan. Resserre.</Terme>
          <Terme nom="Forward guidance">Communication sur la trajectoire future des taux pour guider les anticipations.</Terme>
        </Glossaire>
      </Section>

      <Section {...s("risque")}>
        <Glossaire>
          <Terme nom="Volatilité (σ)">Écart-type des rendements. Mesure l’amplitude des variations.</Terme>
          <Terme nom="Sharpe Ratio">Rendement par unité de risque. &gt;1 = bon, &gt;2 = excellent, &lt;0 = mauvais.</Terme>
          <Terme nom="Sortino Ratio">Version du Sharpe qui ne pénalise que la volatilité baissière.</Terme>
          <Terme nom="Beta (β)">Sensibilité d’un actif au marché. β=1 bouge comme le marché, β=2 amplifie x2.</Terme>
          <Terme nom="Alpha (α)">Surperformance par rapport au benchmark. L’alpha pur = talent du gérant.</Terme>
          <Terme nom="Drawdown">Chute depuis un plus-haut. Mesure ultime du stress d’un portefeuille.</Terme>
          <Terme nom="VaR" precision="Value at Risk">
            Perte maximale probable avec un niveau de confiance (ex : 95%).
          </Terme>
          <Terme nom="CVaR / Expected Shortfall">Moyenne des pertes au-delà de la VaR. Plus conservateur.</Terme>
        </Glossaire>
      </Section>

      <Section {...s("derives")}>
        <Glossaire>
          <Terme nom="Call">Option d’achat. Donne le droit d’acheter à un prix fixé.</Terme>
          <Terme nom="Put">Option de vente. Donne le droit de vendre à un prix fixé.</Terme>
          <Terme nom="Strike">Prix d’exercice d’une option.</Terme>
          <Terme nom="Maturité">Date d’échéance d’une option ou d’une obligation.</Terme>
          <Terme nom="Delta (Δ)">Sensibilité du prix d’une option au prix du sous-jacent.</Terme>
          <Terme nom="Gamma (Γ)">Sensibilité du delta au prix du sous-jacent.</Terme>
          <Terme nom="Theta (Θ)">Perte de valeur d’une option due au temps qui passe.</Terme>
          <Terme nom="Vega">Sensibilité du prix d’une option à la volatilité.</Terme>
        </Glossaire>
      </Section>

      <Section {...s("obligations")}>
        <Glossaire>
          <Terme nom="Yield">Rendement d’une obligation à l’échéance.</Terme>
          <Terme nom="Spread">Écart de rendement entre deux obligations. Ex : spread Italie-Allemagne = prime de risque italienne.</Terme>
          <Terme nom="Duration">
            Sensibilité du prix d’une obligation à une variation des taux. Duration 10 = −10% si les taux montent de 1%.
          </Terme>
          <Terme nom="Convexité">Raffinement de la duration pour les gros mouvements de taux.</Terme>
          <Terme nom="Investment Grade">Obligations notées BBB- ou mieux. Risque faible.</Terme>
          <Terme nom="High Yield / Junk Bonds">Obligations notées en-dessous de BBB-. Rendement élevé mais risque de défaut réel.</Terme>
        </Glossaire>
      </Section>

      <Section {...s("trading")}>
        <Glossaire>
          <Terme nom="Long">Position à la hausse (on achète en espérant que ça monte).</Terme>
          <Terme nom="Short">Position à la baisse (on vend à découvert en espérant racheter moins cher).</Terme>
          <Terme nom="Hedge">Couverture. Position prise pour réduire le risque d’une autre.</Terme>
          <Terme nom="Leverage / Levier">Emprunt pour amplifier les gains (et les pertes).</Terme>
          <Terme nom="Carry trade">Emprunter dans une devise à taux bas, investir dans une devise à taux haut.</Terme>
          <Terme nom="Arbitrage">Exploiter une différence de prix entre deux marchés pour un gain sans risque (théoriquement).</Terme>
          <Terme nom="Flight to quality">Fuite vers la qualité : vente massive d’actifs risqués, achat d’actifs sûrs.</Terme>
          <Terme nom="Risk-on / Risk-off">Période où les investisseurs prennent du risque (risk-on) ou le fuient (risk-off).</Terme>
        </Glossaire>
      </Section>

      <Section {...s("comptabilite")}>
        <Glossaire>
          <Terme nom="PnL" precision="Profit and Loss">
            Compte de résultat. Bénéfice ou perte.
          </Terme>
          <Terme nom="EBITDA">Bénéfice avant intérêts, impôts, dépréciation et amortissement. Mesure opérationnelle.</Terme>
          <Terme nom="Cash-flow libre (FCF)">Trésorerie générée par l’activité, disponible pour les actionnaires.</Terme>
          <Terme nom="P/E ratio">Cours / Bénéfice par action. Plus c’est haut, plus l’action est « chère » (ou en forte croissance).</Terme>
          <Terme nom="ROE">Return on Equity. Rentabilité des fonds propres.</Terme>
          <Terme nom="Dilution">Quand une entreprise émet de nouvelles actions, chaque actionnaire possède un pourcentage plus petit.</Terme>
        </Glossaire>
      </Section>

      <Section {...s("synthese")} etiquette="Synthèse">
        <SyntheseLexique />
      </Section>
    </>
  );
}
