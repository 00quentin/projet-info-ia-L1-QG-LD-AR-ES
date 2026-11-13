"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "motion/react";
import { Check, ChartLine, ChevronDown, ChevronUp, CircleAlert, Compass, FlaskConical, History, Link2, Loader2, Play, RotateCw, Shuffle } from "lucide-react";
import {
  ErreurApi, estReussi, lancerSimulation, lireCatalogue, lireConjoncture,
  type Catalogue, type Conjoncture as TypeConjoncture, type ReponseSimulation, type ResultatScenario,
} from "@/lib/api";
import { Conjoncture } from "@/components/resultats/Conjoncture";
import { ajouterEntree } from "@/lib/historique";
import { contexteSimulation, definirContexteChat } from "@/lib/contexteChat";
import { chargerExemple } from "@/lib/exemple";
import { dateFr } from "@/lib/format";
import { decoderReglages, encoderReglages, lienDePartage, type ReglagesPartages } from "@/lib/partage";
import { nomCourt } from "@/contenu/actifs";
import { Carte } from "@/components/ui/Carte";
import { notifier } from "@/components/ui/Notifications";
import { ReveilServeur, serveurEndormi } from "@/components/ui/ReveilServeur";
import { FormulaireSimulation, reglagesInitiaux, type Reglages } from "@/components/FormulaireSimulation";
import { PROFIL_PERSONNALISE } from "@/components/formulaire/ChoixPortefeuille";
import { ouvrirGuide } from "@/components/Guide";
import { Resultats } from "@/components/Resultats";
import { Comparaison } from "@/components/resultats/Comparaison";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

const ETAPES_ATTENTE = [
  "L'IA lit votre scénario",
  "Recherche de précédents historiques",
  "Estimation de l'impact sur chaque actif",
  "Simulation des trajectoires de marché",
  "Calcul du risque du portefeuille",
];
const DUREE_ETAPE_MS = 3200;
/** Au-dela, le catalogue tarde : le serveur gratuit est sans doute en train de se reveiller. */
const DELAI_SERVEUR_LENT_MS = 4000;

const transitionEtat = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } },
  exit: { opacity: 0, y: -6, transition: { duration: DUREE.rapide } },
};

const boutonSecondaire =
  "inline-flex items-center justify-center gap-2 rounded-controle border border-line bg-surface px-3.5 py-2 text-sm font-medium text-ink transition-colors hover:border-line-strong disabled:cursor-not-allowed disabled:opacity-60";

function Attente({ nbScenarios }: { nbScenarios: number }) {
  const [etape, setEtape] = useState(0);
  useEffect(() => {
    const minuterie = setInterval(() => setEtape((e) => Math.min(e + 1, ETAPES_ATTENTE.length - 1)), DUREE_ETAPE_MS);
    return () => clearInterval(minuterie);
  }, []);
  return (
    <div className="flex flex-col gap-4" role="status" aria-live="polite">
      <Carte taille="normale" className="overflow-hidden">
        <h2 className="text-titre font-semibold">{nbScenarios > 1 ? `Analyse de ${nbScenarios} scénarios en parallèle` : "Analyse en cours"}</h2>
        <p className="mt-1 text-sm text-muted">Comptez une quinzaine de secondes : l&apos;IA raisonne sur des crises réelles avant de répondre.</p>
        <ol className="mt-5 flex flex-col gap-2.5">
          {ETAPES_ATTENTE.map((texte, i) => {
            const faite = i < etape;
            const enCours = i === etape;
            return (
              <motion.li
                key={texte}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: i <= etape ? 1 : 0.45, x: 0 }}
                transition={{ delay: i * 0.05, duration: DUREE.normale, ease: EASE_SORTIE }}
                className="flex items-center gap-3 text-sm"
              >
                <span className="grid size-5 shrink-0 place-items-center">
                  <AnimatePresence mode="wait" initial={false}>
                    {faite ? (
                      <motion.span key="ok" initial={{ scale: 0.6, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={RESSORT} className="grid size-5 place-items-center rounded-full bg-accent text-on-accent">
                        <Check className="size-3" strokeWidth={3} aria-hidden />
                      </motion.span>
                    ) : enCours ? (
                      <Loader2 key="encours" className="size-4 animate-spin text-accent" aria-hidden />
                    ) : (
                      <span key="attente" className="size-2 rounded-full bg-line-strong" />
                    )}
                  </AnimatePresence>
                </span>
                <span className={enCours ? "font-medium text-ink" : faite ? "text-ink-2" : "text-muted"}>{texte}</span>
              </motion.li>
            );
          })}
        </ol>
        <div className="mt-6 h-1 overflow-hidden rounded-full bg-surface-2">
          {/* Progression indicative : tend vers 92 % sans jamais pretendre avoir fini */}
          <motion.div className="h-full origin-left rounded-full bg-accent" initial={{ scaleX: 0.04 }} animate={{ scaleX: 0.92 }} transition={{ duration: 18, ease: [0.1, 0.6, 0.3, 1] }} />
        </div>
      </Carte>
      <div className="chargement h-40 rounded-carte" />
      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="chargement h-28 rounded-tuile" />
        ))}
      </div>
    </div>
  );
}

/** Petite courbe qui se dessine une seule fois : illustre « simuler l'avenir ». */
function IllustrationAccueil() {
  const trace = "M4 70 C 30 66, 42 40, 64 46 S 98 72, 118 52 S 150 18, 176 24 S 206 10, 220 8";
  return (
    <svg viewBox="0 0 224 84" className="mx-auto h-20 w-56" aria-hidden>
      <defs>
        <linearGradient id="degrade-accueil" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.22" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[20, 42, 64].map((y) => (
        <line key={y} x1="0" x2="224" y1={y} y2={y} stroke="var(--line)" strokeWidth="1" />
      ))}
      <motion.path d={`${trace} L 220 84 L 4 84 Z`} fill="url(#degrade-accueil)" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: DUREE.lente, delay: DUREE.donnees * 0.8 }} />
      <motion.path
        d={trace}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="2.5"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: DUREE.donnees * 1.4, ease: EASE_SORTIE, delay: 0.15 }}
      />
      <motion.circle
        r="4.5"
        fill="var(--accent)"
        stroke="var(--surface)"
        strokeWidth="2"
        cx="220"
        cy="8"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ ...RESSORT, delay: DUREE.donnees * 1.4 }}
        style={{ transformBox: "fill-box", transformOrigin: "center" }}
      />
    </svg>
  );
}

function EtatVide() {
  const [conjoncture, setConjoncture] = useState<TypeConjoncture | null>(null);
  useEffect(() => {
    let actif = true;
    lireConjoncture()
      .then((c) => actif && setConjoncture(c))
      .catch(() => undefined); // facultatif : l'accueil reste complet sans
    return () => {
      actif = false;
    };
  }, []);
  const etapes = [
    ["Décrivez", "un événement : krach, guerre, percée technologique, décision d'une banque centrale…"],
    ["Composez", "votre portefeuille : un profil type ou votre propre répartition."],
    ["Analysez", "l'impact estimé par l'IA sur les vrais prix de marché, et le risque pris."],
  ];
  return (
    <Carte taille="hero" className="grid min-h-[26rem] place-items-center text-center">
      <div className="max-w-lg">
        <IllustrationAccueil />
        <h2 className="mt-4 text-section font-semibold tracking-tight">Votre analyse s&apos;affichera ici</h2>
        <ol className="mt-6 grid gap-3 text-left sm:grid-cols-3">
          {etapes.map(([titre, texte], i) => (
            <motion.li
              key={titre}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.08, duration: DUREE.normale, ease: EASE_SORTIE }}
              className="rounded-tuile border border-line bg-surface-2/50 p-3"
            >
              <span className="grid size-6 place-items-center rounded-full bg-accent-soft text-xs font-semibold text-accent-ink">{i + 1}</span>
              <span className="mt-2 block text-sm font-semibold">{titre}</span>
              <span className="mt-0.5 block text-xs leading-relaxed text-muted">{texte}</span>
            </motion.li>
          ))}
        </ol>
        <button type="button" onClick={ouvrirGuide} className={`${boutonSecondaire} mt-6`}>
          <Compass className="size-4 text-muted" aria-hidden />
          Visite guidée
        </button>
        {conjoncture && (
          <div className="mt-7 border-t border-line pt-5 text-left">
            <Conjoncture conjoncture={conjoncture} titre="Conjoncture du jour" compacte />
          </div>
        )}
      </div>
    </Carte>
  );
}

function Erreur({ message, titre = "La simulation n'a pas abouti", onReessayer }: { message: string; titre?: string; onReessayer?: () => void }) {
  return (
    <Carte taille="normale">
      <div className="flex gap-3">
        <CircleAlert className="mt-0.5 size-5 shrink-0 text-loss" aria-hidden />
        <div>
          <h2 className="text-titre font-semibold">{titre}</h2>
          <p className="mt-1 text-sm leading-relaxed text-ink-2">{message}</p>
          {onReessayer && (
            <motion.button whileTap={{ scale: 0.97 }} type="button" onClick={onReessayer} className={`${boutonSecondaire} mt-4`}>
              <RotateCw className="size-4" aria-hidden />
              Réessayer
            </motion.button>
          )}
        </div>
      </div>
    </Carte>
  );
}

/**
 * Accroche de la page (option C de docs/BENCHMARK.md 2.3) : titre, une phrase, trois preuves et la demo.
 * Se replie en une ligne des qu'un resultat est affiche, sans disparaitre.
 */
function Bandeau({
  replie,
  avecResultat,
  onBasculer,
  onExemple,
  chargement,
  desactive,
  nbTrajectoires,
}: {
  replie: boolean;
  avecResultat: boolean;
  onBasculer: () => void;
  onExemple: () => void;
  chargement: boolean;
  desactive: boolean;
  nbTrajectoires?: number;
}) {
  const preuves = [
    { icone: ChartLine, texte: "Vrais cours Yahoo Finance" },
    { icone: Shuffle, texte: `${nbTrajectoires ? `${nbTrajectoires.toLocaleString("fr-FR")} trajectoires` : "Trajectoires"} Monte-Carlo` },
    { icone: History, texte: "IA calibrée sur 2008, COVID, 2022" },
  ];
  return (
    <section aria-labelledby="titre-accueil" className="lg:col-span-2">
      <AnimatePresence mode="wait" initial={false}>
        {replie ? (
          <motion.div key="replie" {...transitionEtat} className="flex items-center justify-between gap-3">
            <h1 id="titre-accueil" className="text-titre font-semibold tracking-tight">
              Et si ça arrivait demain ?
            </h1>
            <button type="button" aria-expanded={false} onClick={onBasculer} className="flex items-center gap-1 rounded-controle px-2 py-1 text-aide font-medium text-muted transition-colors hover:bg-surface-2 hover:text-ink">
              Présentation
              <ChevronDown className="size-3.5" aria-hidden />
            </button>
          </motion.div>
        ) : (
          <motion.div key="deplie" {...transitionEtat} className="flex flex-col gap-5 pb-1 lg:flex-row lg:items-end lg:justify-between lg:gap-10">
            <div className="max-w-3xl">
              <h1 id="titre-accueil" className="text-3xl font-semibold tracking-tight sm:text-4xl">
                Et si ça arrivait demain ?
              </h1>
              <p className="mt-2.5 max-w-2xl text-titre leading-relaxed text-ink-2">
                Décrivez un événement économique. Quant Terminal estime son impact sur votre portefeuille, à partir des vrais cours de marché et des grandes crises passées.
              </p>
              <ul className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-aide text-ink-2" aria-label="Ce qui fonde l'estimation">
                {preuves.map(({ icone: Icone, texte }) => (
                  <li key={texte} className="flex items-center gap-1.5">
                    <Icone className="size-4 text-accent-ink" aria-hidden />
                    {texte}
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-2">
              <motion.button
                type="button"
                onClick={onExemple}
                onPointerEnter={() => void chargerExemple().catch(() => undefined)}
                disabled={desactive || chargement}
                whileTap={{ scale: 0.98 }}
                className="inline-flex h-11 items-center gap-2 rounded-controle bg-ink px-4 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {chargement ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Play className="size-4" aria-hidden />}
                Essayer avec un exemple
              </motion.button>
              {avecResultat && (
                <button type="button" aria-expanded onClick={onBasculer} className="flex h-11 items-center gap-1 rounded-controle px-3 text-aide font-medium text-muted transition-colors hover:bg-surface-2 hover:text-ink">
                  Replier
                  <ChevronUp className="size-3.5" aria-hidden />
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}

/** Applique les reglages d'un lien de partage, en ignorant tout ce que le catalogue ne connait pas. */
function appliquerPartage(base: Reglages, partage: ReglagesPartages, catalogue: Catalogue): Reglages {
  const connus = new Set(catalogue.categories.flatMap((c) => c.actifs.map((a) => a.cle)));
  const actifs = partage.actifs?.filter((a) => connus.has(a));
  const profil = catalogue.profils.some((p) => p.nom === partage.profil) ? partage.profil! : base.portefeuille.profil;
  const borne = (v: number | undefined, b: { min: number; max: number }, defaut: number) => (v == null ? defaut : Math.min(b.max, Math.max(b.min, v)));
  return {
    ...base,
    scenarios: partage.scenarios.filter((s, i) => i === 0 || s).slice(0, catalogue.labels_scenarios.length),
    portefeuille: {
      ...base.portefeuille,
      profil,
      capital: borne(partage.capital, catalogue.capital, base.portefeuille.capital),
      actifs: actifs?.length ? actifs : base.portefeuille.actifs,
      allocations: profil === PROFIL_PERSONNALISE ? Object.fromEntries(Object.entries(partage.allocations ?? {}).filter(([k]) => connus.has(k))) : {},
    },
    duree: borne(partage.duree, catalogue.horizon, base.duree),
    modele: catalogue.modeles.includes(partage.modele ?? "") ? partage.modele! : base.modele,
    monteCarlo: partage.monteCarlo ?? base.monteCarlo,
    convertirEur: partage.convertirEur ?? base.convertirEur,
    calibration: partage.calibration ?? base.calibration,
    prixReels: partage.prixReels ?? base.prixReels,
  };
}

function versPartage(r: Reglages): ReglagesPartages {
  return {
    scenarios: r.scenarios,
    profil: r.portefeuille.profil,
    capital: r.portefeuille.capital,
    actifs: r.portefeuille.actifs.filter((a) => !a.startsWith("PERSO_")),
    allocations: r.portefeuille.profil === PROFIL_PERSONNALISE ? r.portefeuille.allocations : undefined,
    duree: r.duree,
    modele: r.modele,
    monteCarlo: r.monteCarlo,
    convertirEur: r.convertirEur,
    calibration: r.calibration,
    prixReels: r.prixReels,
  };
}

export function Simulateur() {
  const params = useSearchParams();
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [erreurCatalogue, setErreurCatalogue] = useState<string | null>(null);
  const [serveurEnVeille, setServeurEnVeille] = useState(false);
  const [essai, setEssai] = useState(0);
  const [reglages, setReglages] = useState<Reglages | null>(null);
  const [prerempli, setPrerempli] = useState(false);
  const [chaineVue, setChaineVue] = useState<string | null>(null);
  const [chaineEcrite, setChaineEcrite] = useState<string | null>(null);
  const [reponse, setReponse] = useState<ReponseSimulation | null>(null);
  const [exemple, setExemple] = useState(false);
  const [chargementExemple, setChargementExemple] = useState(false);
  // Reglages de l'exemple, appliques au formulaire des que le catalogue est la (le serveur peut dormir).
  const [reglagesEnAttente, setReglagesEnAttente] = useState<ReglagesPartages | null>(null);
  const [bandeauDeplie, setBandeauDeplie] = useState(false);
  const [lien, setLien] = useState<string | undefined>();
  const [onglet, setOnglet] = useState<string>("comparaison");
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const zoneResultats = useRef<HTMLDivElement>(null);
  const [nbEnCours, setNbEnCours] = useState(1);

  useEffect(() => {
    let actif = true;
    const lent = setTimeout(() => actif && setServeurEnVeille(true), DELAI_SERVEUR_LENT_MS);
    lireCatalogue()
      .then((c) => {
        if (!actif) return;
        setErreurCatalogue(null);
        setServeurEnVeille(false);
        setCatalogue(c);
        setReglages((r) => r ?? reglagesInitiaux(c));
      })
      .catch((e: unknown) => {
        if (!actif) return;
        if (serveurEndormi(e)) setServeurEnVeille(true);
        else setErreurCatalogue(e instanceof ErreurApi ? e.message : "Chargement impossible.");
      })
      .finally(() => clearTimeout(lent));
    return () => {
      actif = false;
      clearTimeout(lent);
    };
  }, [essai]);

  // Lien de partage ou bouton « Relancer » de l'historique : on applique les reglages
  // de l'adresse a chaque fois qu'elle change (la page reste montee entre deux visites),
  // sauf quand c'est nous qui venons de l'ecrire apres une simulation.
  const chaine = params.toString();
  if (catalogue && reglages && chaine !== chaineVue) {
    setChaineVue(chaine);
    const partage = chaine && chaine !== chaineEcrite ? decoderReglages(new URLSearchParams(chaine)) : null;
    if (partage) {
      setReglages(appliquerPartage(reglagesInitiaux(catalogue), partage, catalogue));
      setPrerempli(true);
    }
  }
  if (catalogue && reglages && reglagesEnAttente) {
    setReglages(appliquerPartage(reglagesInitiaux(catalogue), reglagesEnAttente, catalogue));
    setReglagesEnAttente(null);
  }

  // Noms courts d'affichage ; ceux de la reponse servent quand le catalogue n'est pas encore charge (exemple).
  const noms = useMemo(() => {
    const m = new Map<string, string>();
    reponse?.scenarios.forEach((s) => estReussi(s) && s.actifs.forEach((a) => m.set(a.cle, nomCourt(a.cle, a.nom))));
    catalogue?.categories.forEach((c) => c.actifs.forEach((a) => m.set(a.cle, nomCourt(a.cle, a.nom))));
    reglages?.portefeuille.actifsPerso.forEach((a) => m.set(a.cle, a.nom));
    return m;
  }, [catalogue, reglages?.portefeuille.actifsPerso, reponse]);

  function amenerResultats() {
    // Sur mobile le formulaire est au-dessus : on amene les resultats a l'ecran.
    if (window.matchMedia("(max-width: 1023px)").matches)
      requestAnimationFrame(() => zoneResultats.current?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }));
  }

  async function lancer() {
    if (!reglages) return;
    const r = reglages;
    setNbEnCours(r.scenarios.length);
    setEnCours(true);
    setErreur(null);
    setPrerempli(false);
    amenerResultats();
    try {
      const rep = await lancerSimulation({
        scenarios: r.scenarios.map((s) => s.trim()),
        actifs: r.portefeuille.actifs,
        profil: r.portefeuille.profil,
        allocations: r.portefeuille.allocations,
        capital: r.portefeuille.capital,
        tickers_perso: r.portefeuille.actifsPerso.filter((a) => r.portefeuille.actifs.includes(a.cle)).map((a) => a.ticker),
        convertir_eur: r.convertirEur,
        duree: r.duree,
        modele: r.modele,
        monte_carlo: r.monteCarlo,
        prix_reels: r.prixReels,
        calibration: r.calibration,
      });
      // L'adresse de la page devient le lien de partage de cette simulation.
      const partage = versPartage(r);
      const encode = encoderReglages(partage);
      setChaineEcrite(encode);
      window.history.replaceState(null, "", `?${encode}`);
      const lienCourant = lienDePartage(partage);
      setLien(lienCourant);
      setReponse(rep);
      setExemple(false);
      setBandeauDeplie(false);
      setOnglet(rep.scenarios.length > 1 ? "comparaison" : rep.scenarios[0].label);
      const nb = rep.scenarios.length;
      const nbReussis = rep.scenarios.filter(estReussi).length;
      if (nbReussis > 0) definirContexteChat(contexteSimulation(rep.scenarios.filter(estReussi), rep.parametres.profil, rep.parametres.duree));
      if (nbReussis > 0) notifier(nb > 1 ? `Comparaison terminée : ${nbReussis} scénarios analysés.` : "Simulation terminée avec succès.");
      for (const s of rep.scenarios) {
        if (!estReussi(s)) continue;
        ajouterEntree({
          type: "Simulation",
          scenario: s.scenario,
          profil: rep.parametres.profil,
          capital: s.portefeuille.capital,
          valeur_finale: s.portefeuille.valeur_finale,
          performance_pct: s.portefeuille.performance_pct,
          monte_carlo: rep.parametres.monte_carlo,
          nb_actifs: rep.parametres.nb_actifs,
          label_comparaison: nb > 1 ? s.label : null,
          lien: lienCourant,
        });
      }
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Une erreur est survenue.");
    } finally {
      setEnCours(false);
    }
  }

  /** Demo en un clic : resultat reel pre-calcule, affiche par le meme rendu que les vrais resultats. */
  async function afficherExemple() {
    setChargementExemple(true);
    try {
      const ex = await chargerExemple();
      setErreur(null);
      setPrerempli(false);
      setReponse(ex.reponse);
      setExemple(true);
      setBandeauDeplie(false);
      setOnglet(ex.reponse.scenarios.length > 1 ? "comparaison" : ex.reponse.scenarios[0].label);
      setLien(lienDePartage(ex.reglages));
      // Le formulaire reprend les reglages de l'exemple : « Relancer en direct » refait exactement la meme demande.
      if (catalogue) setReglages(appliquerPartage(reglagesInitiaux(catalogue), ex.reglages, catalogue));
      else setReglagesEnAttente(ex.reglages);
      const reussis = ex.reponse.scenarios.filter(estReussi);
      if (reussis.length) definirContexteChat(contexteSimulation(reussis, ex.reponse.parametres.profil, ex.reponse.parametres.duree));
      amenerResultats();
    } catch {
      notifier("L'exemple n'a pas pu être chargé. Réessayez dans un instant.", "erreur");
    } finally {
      setChargementExemple(false);
    }
  }

  /** « Proteger mon portefeuille » : passe en profil Personnalise avec la repartition proposee. */
  function appliquerProtection(allocations: Record<string, number>) {
    if (!reglages) return;
    setReglages({ ...reglages, portefeuille: { ...reglages.portefeuille, profil: PROFIL_PERSONNALISE, actifs: Object.keys(allocations), allocations } });
    notifier("Nouvelle répartition appliquée au formulaire : relancez la simulation pour la vérifier.");
    requestAnimationFrame(() => document.getElementById("formulaire-simulation")?.scrollIntoView({ behavior: "smooth", block: "start" }));
  }

  function comparer() {
    if (!reglages || !catalogue) return;
    setReglages({ ...reglages, scenarios: [reglages.scenarios[0], catalogue.scenarios_par_defaut[1] ?? ""] });
    requestAnimationFrame(() => document.getElementById("scenario-1")?.focus());
  }

  const reussis = (reponse?.scenarios.filter(estReussi) ?? []) as ResultatScenario[];
  const echecs = reponse?.scenarios.filter((s) => !estReussi(s)) ?? [];
  const comparaison = reussis.length > 1;
  const ongletCourant = comparaison && onglet === "comparaison" ? "comparaison" : (reussis.find((s) => s.label === onglet) ?? reussis[0])?.label;
  const scenarioAffiche = reussis.find((s) => s.label === ongletCourant);
  const etat = enCours ? "attente" : erreur ? "erreur" : reponse ? (reussis.length ? "resultats" : "echec") : "vide";
  const avecResultat = etat === "resultats";

  return (
    <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[23.5rem_minmax(0,1fr)] lg:items-start">
      <Bandeau
        replie={avecResultat && !bandeauDeplie}
        avecResultat={avecResultat}
        onBasculer={() => setBandeauDeplie((d) => !d)}
        onExemple={afficherExemple}
        chargement={chargementExemple}
        desactive={enCours}
        nbTrajectoires={catalogue?.nb_simulations_monte_carlo}
      />

      <aside id="formulaire-simulation" aria-label="Paramètres" className="scroll-mt-4 lg:sticky lg:top-(--haut-colle) lg:max-h-[calc(100dvh-var(--haut-colle)-1.5rem)] lg:overflow-y-auto lg:rounded-carte">
        {catalogue && reglages ? (
          <Carte className="p-(--marge-carte) [--marge-carte:1rem] sm:[--marge-carte:1.5rem]">
            <AnimatePresence>
              {prerempli && (
                <motion.p initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mb-5 flex gap-2 overflow-hidden rounded-tuile bg-accent-soft px-3 py-2.5 text-aide leading-relaxed text-accent-ink">
                  <Link2 className="mt-0.5 size-3.5 shrink-0" aria-hidden />
                  Simulation partagée : les réglages sont pré-remplis, il ne reste qu&apos;à la lancer.
                </motion.p>
              )}
            </AnimatePresence>
            <FormulaireSimulation catalogue={catalogue} reglages={reglages} onChange={setReglages} onLancer={lancer} enCours={enCours} />
          </Carte>
        ) : erreurCatalogue ? (
          <Erreur
            titre="Le formulaire n'a pas pu se charger"
            message={erreurCatalogue}
            onReessayer={() => {
              setErreurCatalogue(null);
              setEssai((n) => n + 1);
            }}
          />
        ) : serveurEnVeille ? (
          <ReveilServeur onPret={() => setEssai((n) => n + 1)} />
        ) : (
          <Carte taille="normale">
            <div className="flex flex-col gap-4" aria-label="Chargement du formulaire">
              <div className="chargement h-28 rounded-tuile" />
              <div className="chargement h-10 rounded-tuile" />
              <div className="chargement h-40 rounded-tuile" />
            </div>
          </Carte>
        )}
      </aside>

      <section ref={zoneResultats} aria-label="Résultats de la simulation" className="min-w-0 scroll-mt-4">
        <AnimatePresence mode="wait">
          {etat === "attente" && (
            <motion.div key="attente" {...transitionEtat}>
              <Attente nbScenarios={nbEnCours} />
            </motion.div>
          )}
          {etat === "erreur" && (
            <motion.div key="erreur" {...transitionEtat}>
              <Erreur message={erreur!} onReessayer={lancer} />
            </motion.div>
          )}
          {etat === "echec" && (
            <motion.div key="echec" {...transitionEtat}>
              <Erreur message={echecs[0]?.erreur ?? "Une erreur est survenue."} onReessayer={lancer} />
            </motion.div>
          )}
          {etat === "vide" && (
            <motion.div key="vide" {...transitionEtat}>
              <EtatVide />
            </motion.div>
          )}
          {etat === "resultats" && reponse && (
            <motion.div key={`resultats-${reponse.date}`} {...transitionEtat} className="flex flex-col gap-4">
              {exemple && (
                <div role="status" className="flex flex-col gap-3 rounded-tuile border border-accent/30 bg-accent-soft/40 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="flex items-start gap-2.5 text-aide leading-relaxed text-ink-2">
                    <FlaskConical className="mt-0.5 size-4 shrink-0 text-accent-ink" aria-hidden />
                    <span>
                      <strong className="font-semibold text-ink">Exemple pré-calculé</strong> · une vraie simulation enregistrée le {dateFr(reponse.date.slice(0, 10))}. Relancez-la pour l&apos;obtenir avec les cours du jour.
                    </span>
                  </p>
                  <button type="button" onClick={lancer} disabled={!catalogue || !reglages} className={`${boutonSecondaire} shrink-0 self-start sm:self-auto`}>
                    {catalogue ? <RotateCw className="size-4" aria-hidden /> : <Loader2 className="size-4 animate-spin" aria-hidden />}
                    {catalogue ? "Relancer en direct" : "Démarrage du serveur…"}
                  </button>
                </div>
              )}
              {comparaison && (
                <div role="tablist" aria-label="Vue des résultats" className="flex w-full gap-1 overflow-x-auto rounded-tuile border border-line bg-surface p-1 [scrollbar-width:none] sm:w-fit">
                  {["comparaison", ...reussis.map((s) => s.label)].map((cle) => {
                    const actif = ongletCourant === cle;
                    return (
                      <button
                        key={cle}
                        type="button"
                        role="tab"
                        aria-selected={actif}
                        onClick={() => setOnglet(cle)}
                        className={`relative shrink-0 rounded-controle px-3.5 py-1.5 text-sm font-medium transition-colors ${actif ? "text-ink" : "text-muted hover:text-ink"}`}
                      >
                        {actif && <motion.span layoutId="onglet-resultats" className="absolute inset-0 rounded-controle bg-surface-2" transition={RESSORT} />}
                        <span className="relative">{cle === "comparaison" ? "Comparaison" : `Scénario ${cle}`}</span>
                      </button>
                    );
                  })}
                </div>
              )}
              {echecs.length > 0 && (
                <p role="status" className="rounded-tuile border border-warn/30 bg-warn-soft px-4 py-3 text-sm">
                  {echecs.map((e) => `Scénario ${e.label} : ${e.erreur}`).join(" · ")}
                </p>
              )}
              <AnimatePresence mode="wait">
                <motion.div key={ongletCourant} role={comparaison ? "tabpanel" : undefined} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}>
                  {ongletCourant === "comparaison" ? (
                    <Comparaison scenarios={reussis} parametres={reponse.parametres} lienPartage={lien} onVoirDetail={setOnglet} />
                  ) : (
                    scenarioAffiche && <Resultats reponse={reponse} scenario={scenarioAffiche} noms={noms} lienPartage={lien} onComparer={comparaison || !catalogue ? undefined : comparer} onAppliquerProtection={appliquerProtection} />
                  )}
                </motion.div>
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </div>
  );
}
