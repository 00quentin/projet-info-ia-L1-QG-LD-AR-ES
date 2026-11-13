"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ArrowDownRight, ArrowUpRight, Check, CircleAlert, RotateCw, ShieldCheck, Sparkles, Star } from "lucide-react";
import { ErreurApi, type ReponseSimulation, type ResultatScenario } from "@/lib/api";
import { demandeCouverture, demanderCouverture, type MetriquesCouverture, type ReponseCouverture } from "@/lib/couverture";
import { euros, eurosCompacts, pourcent } from "@/lib/format";
import { Carte, Pastille, TitreCarte } from "@/components/ui/Carte";
import { GraphiqueLignes, Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { Apparition, Cascade, ElementCascade, LigneCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

type Props = {
  reponse: ReponseSimulation;
  /** Le scénario affiché : ses chocs IA, son portefeuille et ses paramètres servent au calcul. */
  scenario: ResultatScenario;
  /** Reçoit la nouvelle répartition : % entiers de somme 100, une clé par actif sélectionné (0 compris). */
  onAppliquer: (allocations: Record<string, number>) => void;
};

type Etat =
  | { phase: "repos" }
  | { phase: "attente" }
  | { phase: "erreur"; message: string }
  | { phase: "resultat"; donnees: ReponseCouverture };

const ETAPES_ATTENTE = [
  "Test de centaines de répartitions sur 400 trajectoires",
  "Vérification sur 1 000 nouvelles trajectoires",
  "Rédaction des justifications par l'IA",
];
const DUREE_ETAPE_MS = 1600;
const COULEUR_APRES = "var(--series-1)";
const COULEUR_AVANT = "var(--series-2)";
const SEUIL_EGALITE = 1e-6;

const nomCourt = (nom: string) => nom.split(" (")[0];
const etiquettesJours = (n: number) => Array.from({ length: n }, (_, i) => (i === 0 ? "Aujourd'hui" : `Jour ${i}`));
const points = (v: number, decimales = 1) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toLocaleString("fr-FR", { maximumFractionDigits: decimales })} pt${Math.abs(v) >= 2 ? "s" : ""}`;
const eurosSignes = (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${euros(Math.abs(v))}`;

type LigneMetrique = {
  nom: string;
  aide: string;
  valeur: (m: MetriquesCouverture) => number;
  format: (v: number) => string;
  ecart: (v: number) => string;
  plusGrandEstMieux: boolean;
};

const METRIQUES: LigneMetrique[] = [
  { nom: "Valeur finale", aide: "Trajectoire médiane", valeur: (m) => m.valeur_finale, format: (v) => euros(v), ecart: eurosSignes, plusGrandEstMieux: true },
  { nom: "Scénario défavorable", aide: "5 % des cas finissent plus bas", valeur: (m) => m.valeur_p5, format: (v) => euros(v), ecart: eurosSignes, plusGrandEstMieux: true },
  { nom: "Perte maximale", aide: "Pire chute en cours de route", valeur: (m) => m.max_dd, format: (v) => `−${pourcent(v)}`, ecart: (v) => points(-v), plusGrandEstMieux: false },
  { nom: "Probabilité de perte", aide: "Finir sous le capital de départ", valeur: (m) => m.proba_perte, format: (v) => pourcent(v, 0), ecart: (v) => points(v, 0), plusGrandEstMieux: false },
  { nom: "Volatilité annualisée", aide: "Ampleur des variations", valeur: (m) => m.vol_ann, format: (v) => pourcent(v), ecart: (v) => points(v), plusGrandEstMieux: false },
  { nom: "VaR 95 % sur 1 jour", aide: "Perte d'un mauvais jour", valeur: (m) => Math.abs(m.var_95), format: (v) => `−${pourcent(v, 2)}`, ecart: (v) => points(-v, 2), plusGrandEstMieux: false },
];

/** Etapes du calcul, au rythme indicatif de la reponse (2 a 6 s). */
function Attente() {
  const [etape, setEtape] = useState(0);
  useEffect(() => {
    const minuterie = setInterval(() => setEtape((e) => Math.min(e + 1, ETAPES_ATTENTE.length - 1)), DUREE_ETAPE_MS);
    return () => clearInterval(minuterie);
  }, []);
  return (
    <div role="status" aria-live="polite" className="flex flex-col gap-4">
      <ol className="flex flex-col gap-2.5">
        {ETAPES_ATTENTE.map((texte, i) => {
          const faite = i < etape;
          const enCours = i === etape;
          return (
            <motion.li key={texte} initial={{ opacity: 0, x: -8 }} animate={{ opacity: i <= etape ? 1 : 0.4, x: 0 }} transition={{ delay: i * 0.05, duration: DUREE.normale }} className="flex items-center gap-3 text-sm">
              <span className="relative grid size-5 shrink-0 place-items-center">
                <AnimatePresence mode="wait" initial={false}>
                  {faite ? (
                    <motion.span key="ok" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={RESSORT} className="grid size-5 place-items-center rounded-full bg-gain text-white">
                      <Check className="size-3" strokeWidth={3} aria-hidden />
                    </motion.span>
                  ) : enCours ? (
                    <motion.span key="encours" className="relative flex size-3">
                      <span className="absolute inline-flex size-full animate-ping rounded-full bg-accent opacity-60" />
                      <span className="relative inline-flex size-3 rounded-full bg-accent" />
                    </motion.span>
                  ) : (
                    <motion.span key="attente" className="size-2 rounded-full bg-line-strong" />
                  )}
                </AnimatePresence>
              </span>
              <span className={enCours ? "font-medium text-ink" : faite ? "text-ink-2" : "text-muted"}>{texte}</span>
            </motion.li>
          );
        })}
      </ol>
      <div className="h-1 overflow-hidden rounded-full bg-surface-2">
        <motion.div className="h-full origin-left rounded-full bg-accent" initial={{ scaleX: 0.04 }} animate={{ scaleX: 0.92 }} transition={{ duration: 6, ease: [0.1, 0.6, 0.3, 1] }} />
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="chargement h-24 rounded-xl" />
        ))}
      </div>
      <div className="chargement h-48 rounded-xl" />
    </div>
  );
}

/** Indicateur cle : la valeur glisse de « avant » a « apres ». */
function TuileAvantApres({ titre, avant, apres, format, mieux }: { titre: string; avant: number; apres: number; format: (v: number) => string; mieux: boolean }) {
  return (
    <ElementCascade>
      <motion.div whileHover={{ y: -3 }} transition={RESSORT} className={`h-full rounded-xl border p-4 transition-shadow hover:shadow-card ${mieux ? "border-gain/30 bg-gain-soft/40" : "border-line bg-surface"}`}>
        <div className="text-xs font-medium text-muted">{titre}</div>
        <NombreAnime valeur={apres} depuis={avant} format={format} duree={1.3} className="mt-1.5 block text-2xl font-semibold tracking-tight" />
        <div className="mt-1 flex flex-wrap items-center gap-x-2 text-xs text-ink-2">
          <span>avant : {format(avant)}</span>
          {mieux && (
            <span className="inline-flex items-center gap-0.5 font-medium text-gain">
              <Check className="size-3" strokeWidth={3} aria-hidden />
              amélioré
            </span>
          )}
        </div>
      </motion.div>
    </ElementCascade>
  );
}

function TableauAvantApres({ d }: { d: ReponseCouverture }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm tabular-nums">
        <caption className="sr-only">Métriques du portefeuille avant et après protection ; la meilleure valeur de chaque ligne est marquée d&apos;une étoile.</caption>
        <thead className="text-xs text-muted">
          <tr>
            <th className="pb-2 text-left font-medium">Métrique</th>
            <th className="pb-2 text-right font-medium">Avant</th>
            <th className="pb-2 text-right font-medium">Après</th>
            <th className="hidden pb-2 text-right font-medium sm:table-cell">Écart</th>
          </tr>
        </thead>
        <tbody>
          {METRIQUES.map((m) => {
            const avant = m.valeur(d.avant.metriques);
            const apres = m.valeur(d.apres.metriques);
            const egalite = Math.abs(apres - avant) < SEUIL_EGALITE * Math.max(1, Math.abs(avant));
            const apresGagne = !egalite && (m.plusGrandEstMieux ? apres > avant : apres < avant);
            const cellule = (v: number, meilleure: boolean) => (
              <span className={`inline-flex items-center gap-1 whitespace-nowrap rounded-md px-2 py-0.5 ${meilleure ? "bg-gain-soft font-semibold text-gain" : "text-ink"}`}>
                {meilleure && <Star className="size-3 fill-current" aria-label="Meilleure valeur" />}
                {m.format(v)}
              </span>
            );
            return (
              <tr key={m.nom} className="border-t border-line">
                <td className="py-2.5 pr-3">
                  <span className="block">{m.nom}</span>
                  <span className="block text-xs text-muted">{m.aide}</span>
                </td>
                <td className="py-2.5 text-right">{cellule(avant, !egalite && !apresGagne)}</td>
                <td className="py-2.5 text-right">{cellule(apres, apresGagne)}</td>
                <td className={`hidden whitespace-nowrap py-2.5 text-right text-xs font-medium sm:table-cell ${egalite ? "text-muted" : apresGagne ? "text-gain" : "text-loss"}`}>
                  {egalite ? "=" : m.ecart(apres - avant)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function GraphiqueAvantApres({ d }: { d: ReponseCouverture }) {
  const series: SerieLigne[] = [
    { nom: "Après protection", couleur: COULEUR_APRES, valeurs: d.apres.valeurs, principale: true, bande: { bas: d.apres.valeurs_bas, haut: d.apres.valeurs_haut } },
    { nom: "Avant", couleur: COULEUR_AVANT, valeurs: d.avant.valeurs, bande: { bas: d.avant.valeurs_bas, haut: d.avant.valeurs_haut } },
  ];
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
        <TitreCarte aide="Trajectoire médiane de chaque portefeuille ; les zones claires contiennent 90 % des trajectoires.">Évolution des deux portefeuilles</TitreCarte>
        <Legende series={series} reference="Capital de départ" />
      </div>
      <GraphiqueLignes
        series={series}
        etiquettesX={etiquettesJours(d.apres.valeurs.length)}
        formatY={eurosCompacts}
        formatValeur={(v) => euros(v)}
        reference={{ valeur: d.capital, nom: "Capital de départ" }}
        hauteur={280}
        description={`Valeur médiane du portefeuille sur ${d.duree} jours : ${euros(d.avant.metriques.valeur_finale)} avant protection, ${euros(d.apres.metriques.valeur_finale)} après.`}
      />
    </div>
  );
}

/** Barre de poids : l'ancien en gris, le nouveau en couleur, sur une echelle 0 a 40 %. */
function BarrePoids({ avant, apres, max }: { avant: number; apres: number; max: number }) {
  return (
    <div className="relative mt-2 h-1.5 w-full max-w-56 overflow-hidden rounded-full bg-surface-2" aria-hidden>
      <div className="absolute inset-y-0 left-0 rounded-full bg-line-strong" style={{ width: `${(avant / max) * 100}%` }} />
      <motion.div
        className="absolute inset-y-0 left-0 rounded-full bg-accent"
        initial={{ width: `${(avant / max) * 100}%` }}
        whileInView={{ width: `${(apres / max) * 100}%` }}
        viewport={{ once: true }}
        transition={{ duration: 0.9, ease: EASE_SORTIE, delay: 0.25 }}
      />
    </div>
  );
}

function ListeChangements({ d }: { d: ReponseCouverture }) {
  const max = Math.max(d.methode.poids_max_ligne_pct, ...d.changements.map((c) => Math.max(c.avant_pct, c.apres_pct)));
  return (
    <div>
      <TitreCarte aide="Chaque transfert a été retenu parce qu'il réduit le risque dans ce scénario.">Ce qui change, et pourquoi</TitreCarte>
      <Cascade auDefilement>
        <ul className="flex flex-col gap-2">
          {d.changements.map((c) => {
            const hausse = c.ecart_pct > 0;
            const Icone = hausse ? ArrowUpRight : ArrowDownRight;
            return (
              <LigneCascade key={c.cle} className="flex gap-3 rounded-xl border border-line px-4 py-3">
                <span className={`mt-0.5 grid size-7 shrink-0 place-items-center rounded-full ${hausse ? "bg-accent-soft text-accent-ink" : "bg-surface-2 text-ink-2"}`}>
                  <Icone className="size-4" aria-hidden />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="text-sm font-semibold">{nomCourt(c.nom)}</span>
                    <span className="text-xs tabular-nums text-ink-2">
                      {c.avant_pct} % → <strong className="font-semibold text-ink">{c.apres_pct} %</strong>
                    </span>
                    <Pastille ton={hausse ? "accent" : "neutre"}>
                      <span className="tabular-nums">{points(c.ecart_pct, 0)}</span>
                    </Pastille>
                  </div>
                  <BarrePoids avant={c.avant_pct} apres={c.apres_pct} max={max} />
                  <p className="mt-2 text-sm leading-relaxed text-ink-2">{c.justification}</p>
                </div>
              </LigneCascade>
            );
          })}
        </ul>
      </Cascade>
      {!d.justifications_ia && (
        <p className="mt-2 text-xs text-muted">
          {d.changements.some((c) => c.justification_ia) ? "Certaines phrases" : "Les phrases"} ont été générées automatiquement à partir des chiffres (l&apos;IA n&apos;a pas répondu).
        </p>
      )}
    </div>
  );
}

function Methode({ d }: { d: ReponseCouverture }) {
  const m = d.methode;
  return (
    <details className="text-sm">
      <summary className="cursor-pointer text-xs font-medium text-accent-ink">Comment ce portefeuille est-il calculé ?</summary>
      <ul className="mt-2 flex list-disc flex-col gap-1 pl-5 text-xs leading-relaxed text-ink-2">
        <li>
          Le moteur rejoue le scénario avec les chocs estimés par l&apos;IA et les vraies volatilités et corrélations ({m.nb_trajectoires_recherche} trajectoires).
        </li>
        <li>
          Pas à pas, il teste tous les transferts de {m.pas_transfert_pct} points d&apos;un actif vers un autre et garde le plus utile : celui qui réduit le plus la perte maximale et la probabilité de perte ({m.nb_portefeuilles_testes.toLocaleString("fr-FR")} répartitions testées, {m.nb_etapes} transfert{m.nb_etapes > 1 ? "s" : ""} retenu{m.nb_etapes > 1 ? "s" : ""}).
        </li>
        <li>
          Règles : aucune ligne au-dessus de {m.poids_max_ligne_pct} %, chaque ligne bouge d&apos;au plus {m.ecart_max_ligne_pct} points, au plus {m.rotation_max_pct} % du portefeuille change de main (ici {pourcent(m.rotation_pct, 0)}), seulement vos actifs sélectionnés.
        </li>
        <li>
          Avant et après sont ensuite comparés sur {m.nb_trajectoires_verification.toLocaleString("fr-FR")} nouvelles trajectoires, communes aux deux portefeuilles : les chiffres « avant » peuvent donc différer un peu de ceux affichés plus haut.
        </li>
      </ul>
    </details>
  );
}

function Resultat({ d, onAppliquer }: { d: ReponseCouverture; onAppliquer: Props["onAppliquer"] }) {
  const [applique, setApplique] = useState(false);
  const av = d.avant.metriques;
  const ap = d.apres.metriques;

  if (d.deja_protege) {
    return (
      <Apparition className="flex flex-col gap-4">
        <div className="flex gap-3 rounded-xl border border-gain/30 bg-gain-soft px-4 py-3 text-sm">
          <ShieldCheck className="mt-0.5 size-4 shrink-0 text-gain" aria-hidden />
          <span className="text-ink">
            <strong className="font-semibold">Votre portefeuille résiste déjà bien à ce scénario.</strong> Aucun des {d.methode.nb_portefeuilles_testes.toLocaleString("fr-FR")} transferts testés ne réduit nettement le risque avec vos actifs. Pour aller plus loin, ajoutez à votre sélection des actifs défensifs (obligations d&apos;État, or).
          </span>
        </div>
        <Methode d={d} />
      </Apparition>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {d.synthese && (
        <Apparition className="flex gap-3 rounded-xl border border-accent/25 bg-accent-soft/50 px-4 py-3 text-sm leading-relaxed">
          <Sparkles className="mt-0.5 size-4 shrink-0 text-accent-ink" aria-hidden />
          <span className="text-ink">{d.synthese}</span>
        </Apparition>
      )}

      <Cascade className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <TuileAvantApres titre="Perte maximale" avant={av.max_dd} apres={ap.max_dd} format={(v) => `−${pourcent(v)}`} mieux={ap.max_dd < av.max_dd} />
        <TuileAvantApres titre="Probabilité de perte" avant={av.proba_perte} apres={ap.proba_perte} format={(v) => pourcent(v, 0)} mieux={ap.proba_perte < av.proba_perte} />
        <TuileAvantApres titre="Valeur finale médiane" avant={av.valeur_finale} apres={ap.valeur_finale} format={(v) => euros(v)} mieux={ap.valeur_finale > av.valeur_finale} />
      </Cascade>

      <Apparition delai={0.1}>
        <TitreCarte aide="La valeur la plus favorable de chaque ligne est marquée d'une étoile.">Avant / après</TitreCarte>
        <TableauAvantApres d={d} />
      </Apparition>

      <Apparition auDefilement>
        <GraphiqueAvantApres d={d} />
      </Apparition>

      <ListeChangements d={d} />

      <Apparition auDefilement className="flex flex-col gap-3 border-t border-line pt-5 sm:flex-row sm:items-center sm:justify-between">
        <Methode d={d} />
        <motion.button
          type="button"
          onClick={() => {
            onAppliquer(d.allocations);
            setApplique(true);
          }}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          className="flex h-10 shrink-0 items-center justify-center gap-2 self-start rounded-xl bg-accent px-4 text-sm font-semibold text-white shadow-[0_6px_20px_-6px_var(--accent)] transition-[filter] hover:brightness-110 sm:self-auto"
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.span key={applique ? "fait" : "repos"} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: DUREE.rapide }} className="flex items-center gap-2">
              {applique ? <Check className="size-4" strokeWidth={3} aria-hidden /> : <ShieldCheck className="size-4" aria-hidden />}
              {applique ? "Répartition appliquée" : "Appliquer ce portefeuille"}
            </motion.span>
          </AnimatePresence>
        </motion.button>
      </Apparition>
    </div>
  );
}

const transitionEtat = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } },
  exit: { opacity: 0, y: -6, transition: { duration: DUREE.rapide } },
};

/**
 * « Comment protéger mon portefeuille ? » : propose une répartition plus résistante
 * au scénario affiché (calculée, puis justifiée ligne par ligne) et la compare à l'actuelle.
 */
export function Protection({ reponse, scenario, onAppliquer }: Props) {
  const cle = `${reponse.date}-${scenario.label}`;
  const [suivi, setSuivi] = useState<{ cle: string; etat: Etat }>({ cle, etat: { phase: "repos" } });
  const etat: Etat = suivi.cle === cle ? suivi.etat : { phase: "repos" };
  const annulation = useRef<AbortController | null>(null);

  useEffect(() => () => annulation.current?.abort(), []);

  async function proteger() {
    annulation.current?.abort();
    const controle = new AbortController();
    annulation.current = controle;
    setSuivi({ cle, etat: { phase: "attente" } });
    try {
      const donnees = await demanderCouverture(demandeCouverture(scenario, reponse.parametres), controle.signal);
      setSuivi({ cle, etat: { phase: "resultat", donnees } });
    } catch (e) {
      if (controle.signal.aborted) return;
      setSuivi({ cle, etat: { phase: "erreur", message: e instanceof ErreurApi ? e.message : "La protection n'a pas pu être calculée." } });
    }
  }

  return (
    <Carte className="relative overflow-hidden p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex gap-3">
          <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent-ink">
            <ShieldCheck className="size-5" aria-hidden />
          </span>
          <div>
            <h3 className="text-[15px] font-semibold tracking-tight">Comment protéger mon portefeuille ?</h3>
            <p className="mt-1 max-w-2xl text-sm leading-relaxed text-ink-2">
              {etat.phase === "resultat" && !etat.donnees.deja_protege
                ? `Une répartition plus résistante à ce scénario, vérifiée sur ${etat.donnees.methode.nb_trajectoires_verification.toLocaleString("fr-FR")} trajectoires.`
                : "Le calcul cherche une répartition de vos actifs plus résistante à ce scénario, puis compare avant et après sur les mêmes trajectoires."}
            </p>
          </div>
        </div>
        {etat.phase === "repos" && (
          <motion.button
            type="button"
            onClick={proteger}
            initial="repos"
            whileHover="survol"
            whileTap={{ scale: 0.98 }}
            variants={{ repos: { scale: 1 }, survol: { scale: 1.02 } }}
            transition={RESSORT}
            className="group relative flex h-10 shrink-0 items-center justify-center gap-2 self-start overflow-hidden rounded-xl bg-accent px-4 text-sm font-semibold text-white shadow-[0_6px_20px_-6px_var(--accent)] transition-[filter] hover:brightness-110"
          >
            {/* Reflet qui traverse le bouton au survol */}
            <span aria-hidden className="pointer-events-none absolute inset-y-0 -left-1/2 w-1/2 -skew-x-12 bg-gradient-to-r from-transparent via-white/25 to-transparent transition-transform duration-700 ease-out group-hover:translate-x-[300%]" />
            <motion.span variants={{ repos: { rotate: 0 }, survol: { rotate: [0, -12, 10, 0] } }} transition={{ duration: 0.5 }} className="relative flex">
              <ShieldCheck className="size-4" aria-hidden />
            </motion.span>
            <span className="relative">Protéger mon portefeuille</span>
          </motion.button>
        )}
      </div>

      <AnimatePresence mode="wait" initial={false}>
        {etat.phase === "attente" && (
          <motion.div key="attente" {...transitionEtat} className="mt-5">
            <Attente />
          </motion.div>
        )}
        {etat.phase === "erreur" && (
          <motion.div key="erreur" {...transitionEtat} role="alert" className="mt-5 flex flex-col gap-3 rounded-xl border border-loss/30 bg-loss-soft px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between">
            <span className="flex gap-2 text-ink">
              <CircleAlert className="mt-0.5 size-4 shrink-0 text-loss" aria-hidden />
              {etat.message}
            </span>
            <button type="button" onClick={proteger} className="flex shrink-0 items-center gap-1.5 self-start rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-2 transition-colors hover:border-accent hover:text-accent-ink">
              <RotateCw className="size-3.5" aria-hidden />
              Réessayer
            </button>
          </motion.div>
        )}
        {etat.phase === "resultat" && (
          <motion.div key="resultat" {...transitionEtat} className="mt-6">
            <Resultat d={etat.donnees} onAppliquer={onAppliquer} />
          </motion.div>
        )}
      </AnimatePresence>
    </Carte>
  );
}
