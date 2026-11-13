import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowRight, Bot, Database, Dices, FlaskConical, ShieldCheck, TriangleAlert, type LucideIcon } from "lucide-react";
import { Carte } from "@/components/ui/Carte";
import { ContenuMethodologie } from "@/contenu/academie/methodologie";
import { BORNES_IA, MODELES, PARAMETRES, SOURCES } from "@/components/methodologie/donnees";
import { nomCourt } from "@/contenu/actifs";
import { pourcentSigne } from "@/lib/format";

export const metadata: Metadata = {
  title: "Méthodologie",
  description:
    "D'où viennent les données (Yahoo Finance, BCE, FRED), comment fonctionne la simulation Monte-Carlo, comment l'IA est encadrée et quelles sont les limites de Quant Terminal.",
};

// Ancres stables : la FAQ, le contact et le pied de page pointent dessus.
const PLAN = [
  { id: "sources", titre: "Sources des données" },
  { id: "simulation", titre: "Modèle de simulation" },
  { id: "monte-carlo", titre: "Monte-Carlo" },
  { id: "euros", titre: "Conversion en euros" },
  { id: "ia", titre: "Calibration de l'IA" },
  { id: "bornes", titre: "Bornes par actif" },
  { id: "limites", titre: "Limites" },
  { id: "formules", titre: "Formules exactes" },
];

function Rubrique({ id, icone: Icone, titre, children }: { id: string; icone?: LucideIcon; titre: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-titre`} className="scroll-mt-6 lg:scroll-mt-36">
      <h2 id={`${id}-titre`} className="flex items-center gap-2.5 text-section font-semibold tracking-tight text-ink">
        {Icone && (
          <span className="grid size-8 place-items-center rounded-tuile bg-accent-soft text-accent-ink">
            <Icone className="size-4" aria-hidden />
          </span>
        )}
        {titre}
      </h2>
      <div className="mt-4 flex flex-col gap-4 text-sm leading-relaxed text-ink-2 sm:text-titre sm:leading-relaxed">{children}</div>
    </section>
  );
}

const G = ({ children }: { children: ReactNode }) => <strong className="font-semibold text-ink">{children}</strong>;

export default function Page() {
  return (
    <div className="mx-auto max-w-4xl px-4 pb-20 pt-10 sm:px-6 sm:pt-14">
      <header>
        <p className="text-aide font-medium text-accent-ink">Méthodologie</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-ink sm:text-4xl">Comment Quant Terminal calcule ses résultats</h1>
        <p className="mt-4 max-w-[40rem] text-titre leading-relaxed text-ink-2">
          Une IA estime le choc d&apos;un événement sur chaque actif ; un moteur Python simule ensuite 1 000 trajectoires autour de ce choc, avec les
          vraies volatilités et corrélations des marchés. Voici d&apos;où viennent les chiffres, comment l&apos;IA est encadrée, et ce que l&apos;outil
          ne sait pas faire.
        </p>
        <nav aria-label="Sommaire de la méthodologie" className="mt-6">
          <ul className="flex flex-wrap gap-1.5">
            {PLAN.map((p) => (
              <li key={p.id}>
                <a href={`#${p.id}`} className="block rounded-controle border border-line bg-surface px-2.5 py-1.5 text-aide font-medium text-ink-2 transition-colors hover:border-line-strong hover:text-ink">
                  {p.titre}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <div className="mt-12 flex flex-col gap-14">
        <Rubrique id="sources" icone={Database} titre="Sources des données">
          <p>Toutes les sources sont publiques. Chaque donnée est gardée en mémoire un temps limité pour ne pas surcharger les fournisseurs.</p>
          <div className="overflow-x-auto rounded-tuile border border-line bg-surface">
            <table className="w-full min-w-[34rem] text-left text-sm">
              <caption className="sr-only">Sources des données, usage et fraîcheur</caption>
              <thead className="bg-surface-2 text-xs text-muted">
                <tr>
                  <th scope="col" className="px-4 py-2.5 font-medium">Source</th>
                  <th scope="col" className="px-4 py-2.5 font-medium">Ce qu&apos;on en tire</th>
                  <th scope="col" className="px-4 py-2.5 font-medium">Fraîcheur</th>
                </tr>
              </thead>
              <tbody>
                {SOURCES.map((s) => (
                  <tr key={s.nom} className="border-t border-line align-top">
                    <th scope="row" className="px-4 py-3 font-semibold text-ink">{s.nom}</th>
                    <td className="px-4 py-3 text-ink-2">{s.usage}</td>
                    <td className="px-4 py-3 text-ink-2">{s.fraicheur}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>
            Si Yahoo Finance ne répond pas, le moteur reprend le <G>dernier prix connu</G> (enregistré à chaque récupération réussie), puis en dernier
            recours une valeur de secours datée. Les résultats le signalent alors par un bandeau, actif par actif. Les dates de chaque indicateur FRED sont
            affichées dans l&apos;analyse de l&apos;IA.
          </p>
        </Rubrique>

        <Rubrique id="simulation" icone={FlaskConical} titre="Modèle de simulation">
          <p>
            Pour chaque actif, l&apos;IA donne un <G>choc</G> : la variation attendue sur l&apos;horizon (par exemple −18 % pour le S&amp;P 500). Le moteur
            tire des trajectoires jour par jour autour de ce choc : leur dérive est réglée pour que la trajectoire <G>médiane</G> finisse exactement sur
            le choc estimé, et leur agitation suit la volatilité réelle de l&apos;actif, mesurée sur {PARAMETRES.joursVolatilite} séances.
          </p>
          <p>
            Les actifs ne bougent pas chacun de leur côté : leurs tirages sont <G>corrélés</G> avec la matrice de corrélation mesurée sur les{" "}
            {PARAMETRES.anneesCorrelation} dernières années de rendements réels (décomposition de Cholesky). Si l&apos;historique manque, des ordres de
            grandeur de long terme entre classes d&apos;actifs prennent le relais. Garde-fou : un actif ne peut pas perdre plus de{" "}
            {PARAMETRES.perteMaxQuotidiennePct} % en une seule séance.
          </p>
          <p>Trois modèles d&apos;aléa sont proposés :</p>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {MODELES.map((m) => (
              <Carte key={m.nom} taille="compacte">
                <h3 className="text-titre font-semibold text-ink">{m.nom}</h3>
                <p className="mt-0.5 text-xs text-muted">{m.nomMoteur}</p>
                <p className="mt-2 text-aide leading-relaxed text-ink-2">{m.description}</p>
              </Carte>
            ))}
          </div>
        </Rubrique>

        <Rubrique id="monte-carlo" icone={Dices} titre="Monte-Carlo : 1 000 futurs possibles">
          <p>
            Avec Monte-Carlo, le moteur simule <G>{PARAMETRES.nbSimulations.toLocaleString("fr-FR")} trajectoires</G>. La courbe affichée est la médiane ;
            la zone claire va du 5<sup>e</sup> au 95<sup>e</sup> centile, soit 90 % des trajectoires. La « probabilité de finir en perte » est la part des
            trajectoires qui terminent sous le capital de départ.
          </p>
          <p>
            Les métriques de risque (volatilité, Sharpe, perte maximale, VaR) sont calculées <G>sur les trajectoires elles-mêmes</G> (un échantillon de{" "}
            {PARAMETRES.cheminsConserves} chemins), puis on garde la médiane : la courbe médiane est lissée, y mesurer le risque le sous-estimerait. Le
            ratio de Sharpe se calcule au-delà du taux de dépôt de la BCE (taux sans risque d&apos;un épargnant en euros, lu sur FRED ; 2 % si FRED est
            injoignable). Le temps de retour au capital, lui, est lu sur la trajectoire médiane.
          </p>
          <p>
            Sans Monte-Carlo, une seule trajectoire est tirée : c&apos;est un futur possible parmi d&apos;autres, pas une prévision. En backtest, rien
            n&apos;est simulé : ce sont les vrais cours de la période.
          </p>
        </Rubrique>

        <Rubrique id="euros" titre="Conversion en euros">
          <p>
            Le capital est en euros, mais beaucoup d&apos;actifs cotent en dollars. En <G>simulation</G>, l&apos;euro/dollar est simulé comme les autres
            actifs (son choc vient de l&apos;IA, ses mouvements sont corrélés au reste) et chaque actif en dollars est divisé par ce taux, jour par jour. En{" "}
            <G>backtest</G>, on utilise les taux de référence officiels de la BCE de chaque séance (disponibles depuis janvier 1999), y compris pour le yen
            et la livre.
          </p>
        </Rubrique>

        <Rubrique id="ia" icone={Bot} titre="Calibration de l'IA">
          <p>
            L&apos;analyse est confiée à un modèle d&apos;OpenAI ({PARAMETRES.modeleIa}, avec {PARAMETRES.modeleIaSecours} en secours). Il reçoit le
            scénario, la conjoncture réelle du moment (taux et inflation FRED) et une méthode imposée : classer la sévérité, raisonner sur l&apos;horizon,
            respecter les corrélations économiques connues, puis vérifier chaque chiffre avant de répondre. La consigne rappelle que les marchés anticipent
            une partie des nouvelles : en cas d&apos;hésitation, l&apos;amplitude la plus modeste l&apos;emporte.
          </p>
          <p>
            Avec la <G>calibration historique</G>, l&apos;IA choisit les 2 ou 3 crises passées les plus proches dans une liste d&apos;une vingtaine
            d&apos;événements chiffrés (krach de 1929, choc pétrolier de 1973, 2008, COVID 2020, guerre en Ukraine…), leur donne un poids (somme = 1) et
            applique leurs amplitudes réelles. Elle note sa propre <G>fiabilité</G> : élevée si le scénario ressemble à une crise connue, faible s&apos;il
            est inédit. Une seconde estimation, sans ancrage historique, est demandée en parallèle : un grand écart entre les deux signale un scénario
            peu couvert par l&apos;histoire (détail dépliable dans la carte « Analyse de l&apos;IA »).
          </p>
        </Rubrique>

        <Rubrique id="bornes" icone={ShieldCheck} titre="Bornes par actif : l'IA ne peut pas tout dire">
          <p>
            Chaque réponse est validée par un schéma strict (bibliothèque Pydantic) avant d&apos;entrer dans la simulation. Un pourcentage mal écrit (25 au
            lieu de 0,25) est corrigé, puis chaque choc est <G>borné</G> par actif, à partir des pires et meilleurs mouvements historiques observés sur
            environ 100 séances. Les variations d&apos;inflation sont limitées à [−10 ; +30] points et celles des taux directeurs à [−5 ; +10] points ; un
            actif personnalisé est borné entre −80 % et +200 %. Ces garde-fous existent depuis un bug resté célèbre dans l&apos;équipe : l&apos;or à
            +1 222 891 %.
          </p>
          <div className="overflow-x-auto rounded-tuile border border-line bg-surface">
            <table className="w-full min-w-[30rem] text-sm tabular-nums">
              <caption className="sr-only">Bornes des chocs acceptés pour chaque actif</caption>
              <thead className="bg-surface-2 text-xs text-muted">
                <tr>
                  <th scope="col" className="px-4 py-2.5 text-left font-medium">Actif</th>
                  <th scope="col" className="px-4 py-2.5 text-right font-medium">Pire choc accepté</th>
                  <th scope="col" className="px-4 py-2.5 text-right font-medium">Meilleur choc accepté</th>
                </tr>
              </thead>
              <tbody>
                {BORNES_IA.map(([cle, min, max]) => (
                  <tr key={cle} className="border-t border-line">
                    <th scope="row" className="px-4 py-2 text-left font-medium text-ink">{nomCourt(cle)}</th>
                    <td className="px-4 py-2 text-right text-loss">{pourcentSigne(min * 100, 0)}</td>
                    <td className="px-4 py-2 text-right text-gain">{pourcentSigne(max * 100, 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Rubrique>

        <Rubrique id="limites" icone={TriangleAlert} titre="Limites honnêtes">
          <ul className="flex flex-col gap-2.5">
            {[
              <>Le choc vient d&apos;une <G>IA</G> : c&apos;est une estimation raisonnée, pas une prévision. Deux lancements du même scénario peuvent différer.</>,
              <>L&apos;IA raisonne sur environ 100 séances ; son choc est appliqué tel quel à l&apos;horizon choisi (de 30 à 250 séances).</>,
              <>Volatilités et corrélations sont supposées <G>constantes</G> sur l&apos;horizon, alors qu&apos;en crise elles montent (effet GARCH, corrélations qui tendent vers 1).</>,
              <>Le modèle Classique suppose des rendements gaussiens : les krachs extrêmes y sont plus rares que dans la réalité (le modèle Crises réelles corrige en partie).</>,
              <>Obligations et indices MSCI sont suivis via des <G>ETF</G> : c&apos;est le prix de ces fonds qui est modélisé.</>,
              <>En simulation, seule la conversion dollar → euro est modélisée ; yen et livre ne sont convertis qu&apos;en backtest.</>,
              <>Pas de frais, de fiscalité, de spreads ni de problème de liquidité. Les performances passées ne préjugent pas des performances futures.</>,
            ].map((l, i) => (
              <li key={i} className="relative pl-5">
                <span aria-hidden className="absolute left-0.5 top-[0.6em] size-1.5 rounded-full bg-muted" />
                {l}
              </li>
            ))}
          </ul>
          <p className="rounded-tuile border border-line bg-surface-2 px-4 py-3 text-aide">
            Quant Terminal est un outil pédagogique réalisé par des étudiants de L1. Ce n&apos;est pas un conseil en investissement.
          </p>
        </Rubrique>

        <Rubrique id="formules" titre="Formules exactes">
          <p>
            Volatilité annualisée, ratio de Sharpe, perte maximale, VaR, mouvement brownien géométrique et percentiles Monte-Carlo : les formules
            implémentées, telles que présentées dans l&apos;Académie.{" "}
            <Link href="/academie#methodologie" className="inline-flex items-center gap-0.5 font-medium text-accent-ink hover:underline">
              Ouvrir dans l&apos;Académie
              <ArrowRight className="size-3.5" aria-hidden />
            </Link>
          </p>
          <div className="flex flex-col gap-12">
            <ContenuMethodologie />
          </div>
        </Rubrique>
      </div>
    </div>
  );
}
