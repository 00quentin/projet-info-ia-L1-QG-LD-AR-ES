import type { ValidationIA } from "@/lib/validation";
import { dateFr, nombre } from "@/lib/format";
import { Encadre, G, ListeEncadre, Point } from "@/components/academie/blocs";
import { Carte } from "@/components/ui/Carte";
import { points } from "./outils";

const ETAPES = [
  {
    titre: "On décrit l’événement sans le nommer",
    texte:
      "Deux ou trois phrases sur le mécanisme (« une grande banque d’affaires fait faillite… ») et sa durée, sur une fenêtre de quelques jours à quelques mois adaptée à chaque événement. Aucune année, aucun mois, aucun chiffre, aucun nom propre : le script le vérifie avant d’envoyer quoi que ce soit.",
  },
  {
    titre: "Même IA, même consigne que le simulateur",
    texte:
      "Le prompt est celui du simulateur, sans calibration historique (sinon l’IA chercherait l’événement le plus proche) et sans la conjoncture du jour. Seul l’horizon change : la durée réelle de la crise au lieu de 100 séances.",
  },
  {
    titre: "On compare aux vrais cours",
    texte:
      "Les vrais mouvements viennent de Yahoo Finance, convertis en euros au taux BCE comme dans le backtest. Les estimations en dollars de l’IA sont converties avec son propre EUR/USD, comme le fait le simulateur.",
  },
  {
    titre: "On mesure, une fois pour toutes",
    texte:
      "Écart en points, bon sens de variation, corrélation, taille des chocs, et part des vrais mouvements tombés dans la fourchette bas–haut donnée par l’IA (convertie en euros comme son estimation centrale). Le calcul est fait une fois par un script et enregistré : votre visite ne déclenche aucun appel à l’IA.",
  },
];

// Crises ajoutées après la rédaction de la consigne (v9) : test hors échantillon.
const NOMS_HORS_ECHANTILLON = ["Crise de la dette en zone euro", "Dévaluation chinoise", "Faillite de SVB"];

export function Methode({ v }: { v: ValidationIA }) {
  const p = v.protocole;
  const local = v.global_devise_locale;
  const ecretes = v.crises.flatMap((c) => c.actifs.filter((a) => a.ecrete).map((a) => `${a.nom_court}, ${c.nom.replace(/\s*\(.*\)$/, "").toLowerCase()}`));
  // Fichier récent : le groupe « hors échantillon » est calculé par le script. Ancien fichier : repli sur les 3 crises citées.
  const groupe = v.hors_echantillon;
  const horsCrises = v.crises.filter((c) => NOMS_HORS_ECHANTILLON.some((n) => c.nom.startsWith(n)));
  const horsEchantillon = groupe && groupe.nb_fourchettes
    ? { nb: groupe.nb_dans_fourchette ?? 0, total: groupe.nb_fourchettes, part: groupe.part_dans_fourchette ?? 0, evenements: groupe.nb_evenements ?? 0 }
    : !groupe && horsCrises.length === NOMS_HORS_ECHANTILLON.length
      ? (() => {
          const nb = horsCrises.reduce((t, c) => t + (c.metriques.nb_dans_fourchette ?? 0), 0);
          const total = horsCrises.reduce((t, c) => t + (c.metriques.nb_fourchettes ?? 0), 0);
          return total > 0 ? { nb, total, part: nb / total, evenements: horsCrises.length } : null;
        })()
      : null;
  const nbHors = horsEchantillon?.evenements ?? 0;
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-start">
      <Carte className="p-5 sm:p-6">
        <h3 className="text-[15px] font-semibold tracking-tight">La méthode en 4 étapes</h3>
        <ol className="mt-4 flex flex-col gap-4">
          {ETAPES.map((e, i) => (
            <li key={e.titre} className="flex gap-3">
              <span className="grid size-7 shrink-0 place-items-center rounded-full bg-accent-soft text-sm font-semibold text-accent-ink">{i + 1}</span>
              <div>
                <p className="text-sm font-semibold text-ink">{e.titre}</p>
                <p className="mt-1 text-sm leading-relaxed text-ink-2">{e.texte}</p>
              </div>
            </li>
          ))}
        </ol>
        <dl className="mt-5 grid grid-cols-1 gap-x-4 gap-y-2 border-t border-line pt-4 text-xs sm:grid-cols-2">
          <div>
            <dt className="text-muted">Calculé le</dt>
            <dd className="font-medium text-ink-2">{dateFr(v.genere_le.slice(0, 10))}</dd>
          </div>
          <div>
            <dt className="text-muted">Modèle</dt>
            <dd className="font-medium text-ink-2">{p.modeles_utilises.join(", ") || p.modele}</dd>
          </div>
          <div>
            <dt className="text-muted">Version du prompt</dt>
            <dd className="font-medium text-ink-2">{p.version_prompt}</dd>
          </div>
          <div>
            <dt className="text-muted">Seuil du « bon sens »</dt>
            <dd className="font-medium text-ink-2">vrai mouvement d’au moins {nombre(p.seuil_sens_pts, 0)} points</dd>
          </div>
        </dl>
      </Carte>

      <Encadre ton="alerte" titre="Limites, en toute honnêteté">
        <ListeEncadre>
          <Point>
            <G>Test à l’aveugle partiel.</G> L’IA a lu l’histoire de ces crises : même sans nom ni date, elle les reconnaît presque toujours. Ce test
            montre qu’elle traduit bien une crise connue en chiffres, pas qu’elle prévoit un événement inédit.
          </Point>
          <Point>
            <G>Consigne réécrite après un premier test.</G> Avec l’ancienne consigne, la fourchette de l’IA ne contenait le vrai mouvement qu’environ
            une fois sur deux. La consigne actuelle demande une fourchette du 10<sup>e</sup> au 90<sup>e</sup> centile et prévient l’IA qu’elle
            sous-estime l’ampleur des crises, un constat tiré des six premières crises : leur score est donc un peu flatteur. Aucun élargissement n’est ajouté après coup.
          </Point>
          {horsEchantillon && (
            <Point>
              <G>Test hors échantillon.</G>{" "}
              {nbHors > 3
                ? `Les ${nbHors} événements qui n’ont pas servi à écrire la consigne (tous sauf les six premières crises)`
                : "Les trois dernières crises (zone euro, Chine, SVB), ajoutées après l’écriture de la consigne,"}{" "}
              donnent une fourchette qui contient le vrai mouvement pour {horsEchantillon.nb} actifs sur {horsEchantillon.total}, soit{" "}
              {nombre(horsEchantillon.part * 100, 0)} %. C’est la mesure la plus honnête{nbHors > 3 ? "" : ", mais sur seulement trois crises"}.
            </Point>
          )}
          <Point>
            <G>Un seul tirage par événement.</G> L’IA n’est pas déterministe : relancée, elle donnerait des chiffres un peu différents.
          </Point>
          <Point>
            <G>Échantillon limité.</G> {v.crises.length} événements et {v.global.nb_actifs} comparaisons ; la corrélation est tirée vers le haut par les
            très gros mouvements (VIX, pétrole). Les scores par catégorie reposent sur peu d’événements chacune : à lire avec prudence.
          </Point>
          <Point>
            <G>Conversion en euros.</G> Une erreur de l’IA sur l’euro-dollar se répercute sur tous les actifs en dollars. En devise d’origine, l’erreur
            moyenne serait de {points(local.erreur_moyenne_pts)}.
          </Point>
          <Point>
            <G>Garde-fous du simulateur.</G> Les chocs sont plafonnés par classe d’actifs, ce qui peut couper une estimation extrême
            {ecretes.length > 0 ? ` (ici : ${ecretes.join(" ; ")})` : ""}.
          </Point>
          <Point>
            <G>Le passé ne garantit pas l’avenir.</G> Bien estimer {v.crises.length} événements connus ne dit pas comment l’IA jugera le prochain.
          </Point>
        </ListeEncadre>
      </Encadre>
    </div>
  );
}
