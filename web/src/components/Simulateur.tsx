"use client";

import { useEffect, useRef, useState } from "react";
import { CircleAlert, LineChart, RotateCw } from "lucide-react";
import { ErreurApi, estReussi, lancerSimulation, lireCatalogue, type Catalogue, type ReponseSimulation } from "@/lib/api";
import { Carte } from "@/components/ui/Carte";
import { FormulaireSimulation, reglagesInitiaux, type Reglages } from "@/components/FormulaireSimulation";
import { Resultats } from "@/components/Resultats";

const ETAPES_ATTENTE = [
  "L'IA lit votre scénario…",
  "Recherche de précédents historiques…",
  "Estimation de l'impact sur chaque actif…",
  "Simulation des trajectoires de marché…",
  "Calcul du risque du portefeuille…",
];

function Attente() {
  const [etape, setEtape] = useState(0);
  useEffect(() => {
    const minuterie = setInterval(() => setEtape((e) => Math.min(e + 1, ETAPES_ATTENTE.length - 1)), 3200);
    return () => clearInterval(minuterie);
  }, []);
  return (
    <div className="flex flex-col gap-4" role="status" aria-live="polite">
      <Carte className="p-7">
        <div className="flex items-center gap-3">
          <span className="relative flex size-3">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-accent opacity-60" />
            <span className="relative inline-flex size-3 rounded-full bg-accent" />
          </span>
          <span className="text-[15px] font-medium">{ETAPES_ATTENTE[etape]}</span>
        </div>
        <p className="mt-2 text-sm text-muted">Comptez une quinzaine de secondes : l&apos;IA raisonne sur des crises réelles avant de répondre.</p>
        <div className="mt-6 h-14 w-64 max-w-full animate-pulse rounded-xl bg-surface-2" />
      </Carte>
      <div className="h-72 animate-pulse rounded-2xl border border-line bg-surface" />
    </div>
  );
}

function EtatVide() {
  return (
    <Carte className="grid min-h-[26rem] place-items-center p-8 text-center">
      <div className="max-w-md">
        <span className="mx-auto grid size-12 place-items-center rounded-2xl bg-accent-soft text-accent-ink">
          <LineChart className="size-6" aria-hidden />
        </span>
        <h2 className="mt-5 text-xl font-semibold tracking-tight">Et si ça arrivait demain ?</h2>
        <p className="mt-2 text-[15px] leading-relaxed text-ink-2">
          Décrivez un événement économique, choisissez votre portefeuille, puis lancez la simulation. L&apos;IA estime l&apos;impact sur chaque actif à partir des vrais prix de marché et de crises passées.
        </p>
      </div>
    </Carte>
  );
}

function Erreur({ message, onReessayer }: { message: string; onReessayer?: () => void }) {
  return (
    <Carte className="p-7">
      <div className="flex gap-3">
        <CircleAlert className="mt-0.5 size-5 shrink-0 text-loss" aria-hidden />
        <div>
          <h2 className="text-[15px] font-semibold">La simulation n&apos;a pas abouti</h2>
          <p className="mt-1 text-sm leading-relaxed text-ink-2">{message}</p>
          {onReessayer && (
            <button type="button" onClick={onReessayer} className="mt-4 inline-flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm font-medium transition hover:border-line-strong">
              <RotateCw className="size-4" aria-hidden />
              Réessayer
            </button>
          )}
        </div>
      </div>
    </Carte>
  );
}

export function Simulateur() {
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [erreurCatalogue, setErreurCatalogue] = useState<string | null>(null);
  const [reglages, setReglages] = useState<Reglages | null>(null);
  const [reponse, setReponse] = useState<ReponseSimulation | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const zoneResultats = useRef<HTMLDivElement>(null);

  const [essai, setEssai] = useState(0);

  useEffect(() => {
    let actif = true;
    lireCatalogue()
      .then((c) => {
        if (!actif) return;
        setErreurCatalogue(null);
        setCatalogue(c);
        setReglages((r) => r ?? reglagesInitiaux(c));
      })
      .catch((e: unknown) => actif && setErreurCatalogue(e instanceof ErreurApi ? e.message : "Chargement impossible."));
    return () => {
      actif = false;
    };
  }, [essai]);

  async function lancer() {
    if (!reglages) return;
    setEnCours(true);
    setErreur(null);
    // Sur mobile le formulaire est au-dessus : on amene les resultats a l'ecran.
    if (window.matchMedia("(max-width: 1023px)").matches) zoneResultats.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    try {
      const r = await lancerSimulation({
        scenarios: reglages.scenarios.map((s) => s.trim()),
        actifs: reglages.actifs,
        profil: reglages.profil,
        allocations: reglages.allocations,
        capital: reglages.capital,
        tickers_perso: [],
        convertir_eur: reglages.convertirEur,
        duree: reglages.duree,
        modele: reglages.modele,
        monte_carlo: reglages.monteCarlo,
        prix_reels: reglages.prixReels,
        calibration: reglages.calibration,
      });
      setReponse(r);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Une erreur est survenue.");
    } finally {
      setEnCours(false);
    }
  }

  if (erreurCatalogue) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <Erreur message={`${erreurCatalogue} Le serveur se réveille peut-être : patientez quelques secondes.`} onReessayer={() => setEssai((n) => n + 1)} />
      </div>
    );
  }

  const premier = reponse?.scenarios[0];

  return (
    <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[23.5rem_minmax(0,1fr)] lg:items-start">
      <aside className="lg:sticky lg:top-[7.75rem] lg:max-h-[calc(100dvh-9.25rem)] lg:overflow-y-auto lg:rounded-2xl">
        <Carte className="p-5">
          {catalogue && reglages ? (
            <FormulaireSimulation catalogue={catalogue} reglages={reglages} onChange={setReglages} onLancer={lancer} enCours={enCours} />
          ) : (
            <div className="flex flex-col gap-4" aria-label="Chargement du formulaire">
              <div className="h-28 animate-pulse rounded-xl bg-surface-2" />
              <div className="h-10 animate-pulse rounded-xl bg-surface-2" />
              <div className="h-40 animate-pulse rounded-xl bg-surface-2" />
            </div>
          )}
        </Carte>
      </aside>

      <main ref={zoneResultats} className="min-w-0 scroll-mt-4">
        {enCours ? (
          <Attente />
        ) : erreur ? (
          <Erreur message={erreur} onReessayer={lancer} />
        ) : reponse && premier ? (
          estReussi(premier) ? (
            <Resultats reponse={reponse} scenario={premier} />
          ) : (
            <Erreur message={premier.erreur} onReessayer={lancer} />
          )
        ) : (
          <EtatVide />
        )}
      </main>
    </div>
  );
}
