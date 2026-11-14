"use client";

import { useEffect, useRef, useState } from "react";
import { GitCompareArrows, Loader2, Play } from "lucide-react";
import { comparerPortefeuilles, ErreurApi, lireCatalogue, type Catalogue, type ReponseComparaison } from "@/lib/api";
import { nombreSigne } from "@/lib/format";
import { Carte, TitreSection } from "@/components/ui/Carte";
import { ReveilServeur, serveurEndormi } from "@/components/ui/ReveilServeur";
import { Erreur } from "@/components/backtest/EtatsBacktest";
import { PROFIL_PERSONNALISE, portefeuilleInitial, validerPortefeuille, type ValeurPortefeuille } from "@/components/formulaire/ChoixPortefeuille";
import { boutonPrincipal, champ, puce, titreSection } from "@/components/formulaire/styles";
import { COULEUR_A, COULEUR_B, GraphiqueDuel } from "./GraphiqueDuel";
import { SelecteurPortefeuille } from "./SelecteurPortefeuille";
import { TableauEcarts } from "./TableauEcarts";

const SCENARIO_LONGUEUR_MIN = 10;
const SCENARIO_LONGUEUR_MAX = 1000;
const SCENARIOS_RAPIDES_VISIBLES = 4;

/** B part d'un profil different de A, pour que la comparaison ait du sens des le depart. */
function portefeuilleB(catalogue: Catalogue): ValeurPortefeuille {
  const base = portefeuilleInitial(catalogue);
  const autre = catalogue.profils.find((p) => p.nom !== base.profil && p.poids && p.nom !== PROFIL_PERSONNALISE);
  return autre?.poids ? { ...base, profil: autre.nom, actifs: Object.keys(autre.poids) } : base;
}

function memePortefeuille(a: ValeurPortefeuille, b: ValeurPortefeuille): boolean {
  if (a.profil !== b.profil || a.capital !== b.capital || a.actifs.length !== b.actifs.length) return false;
  if (!a.actifs.every((x) => b.actifs.includes(x))) return false;
  return a.profil !== PROFIL_PERSONNALISE || a.actifs.every((x) => (a.allocations[x] ?? 0) === (b.allocations[x] ?? 0));
}

function demande(p: ValeurPortefeuille) {
  return { actifs: p.actifs, profil: p.profil, allocations: p.allocations, capital: p.capital, tickers_perso: [], convertir_eur: true };
}

function verdict(r: ReponseComparaison): string {
  const e = r.ecarts.perf_pts;
  if (e === null || Math.abs(e) < 0.005) return "Les deux portefeuilles terminent à égalité sous ce scénario.";
  const gagnant = e > 0 ? "B" : "A";
  return `Le portefeuille ${gagnant} résiste le mieux à ce scénario, avec ${nombreSigne(Math.abs(e)).replace("−", "")} point${Math.abs(e) >= 2 ? "s" : ""} de performance d'avance.`;
}

export function PageComparaison() {
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [erreurCatalogue, setErreurCatalogue] = useState<string | null>(null);
  const [essai, setEssai] = useState(0);
  const [serveurEnVeille, setServeurEnVeille] = useState(false);
  const [scenario, setScenario] = useState("");
  const [a, setA] = useState<ValeurPortefeuille | null>(null);
  const [b, setB] = useState<ValeurPortefeuille | null>(null);
  const [duree, setDuree] = useState(0);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [resultat, setResultat] = useState<ReponseComparaison | null>(null);
  const zoneResultat = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let actif = true;
    lireCatalogue()
      .then((c) => {
        if (!actif) return;
        setErreurCatalogue(null);
        setServeurEnVeille(false);
        setCatalogue(c);
        setScenario((s) => s || c.scenarios_par_defaut[0] || "");
        setA((v) => v ?? portefeuilleInitial(c));
        setB((v) => v ?? portefeuilleB(c));
        setDuree((d) => d || c.horizon.defaut);
      })
      .catch((e: unknown) => {
        if (!actif) return;
        if (serveurEndormi(e)) setServeurEnVeille(true);
        else setErreurCatalogue(e instanceof ErreurApi ? e.message : "Chargement impossible.");
      });
    return () => {
      actif = false;
    };
  }, [essai]);

  if (erreurCatalogue) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <Erreur titre="La comparaison n'a pas pu se charger" message={erreurCatalogue} onReessayer={() => setEssai((n) => n + 1)} />
      </div>
    );
  }
  if (!catalogue || !a || !b) {
    return (
      <div className="mx-auto max-w-[1100px] px-4 py-8 sm:px-6">
        {serveurEnVeille ? (
          <ReveilServeur onPret={() => setEssai((n) => n + 1)} />
        ) : (
          <div className="flex flex-col gap-3" aria-label="Chargement de la page">
            <div className="chargement h-24 rounded-xl" />
            <div className="chargement h-80 rounded-xl" />
          </div>
        )}
      </div>
    );
  }

  const cat = catalogue;
  const pa = a;
  const pb = b;
  const probleme =
    scenario.trim().length < SCENARIO_LONGUEUR_MIN
      ? "Décrivez votre scénario en au moins 10 caractères."
      : validerPortefeuille(pa, cat)?.replace(/^/, "Portefeuille A : ") ??
        validerPortefeuille(pb, cat)?.replace(/^/, "Portefeuille B : ") ??
        (memePortefeuille(pa, pb) ? "Les portefeuilles A et B sont identiques : modifiez l'un des deux pour les comparer." : null);

  async function lancer() {
    if (probleme || enCours) return;
    setEnCours(true);
    setErreur(null);
    setServeurEnVeille(false);
    requestAnimationFrame(() => zoneResultat.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
    try {
      setResultat(
        await comparerPortefeuilles({
          scenario: scenario.trim(),
          portefeuille_a: demande(pa),
          portefeuille_b: demande(pb),
          duree,
          modele: cat.modeles[0],
          monte_carlo: false,
          prix_reels: true,
          calibration: true,
          convertir_eur: true,
        }),
      );
    } catch (e) {
      if (serveurEndormi(e)) setServeurEnVeille(true);
      else setErreur(e instanceof ErreurApi ? e.message : "Une erreur est survenue.");
    } finally {
      setEnCours(false);
    }
  }

  const rapides = cat.scenarios_rapides.slice(0, SCENARIOS_RAPIDES_VISIBLES);

  return (
    <div className="mx-auto flex max-w-[1100px] flex-col gap-6 px-4 py-6 sm:px-6">
      <header>
        <h1 className="flex items-center gap-2.5 text-2xl font-semibold tracking-tight">
          <GitCompareArrows className="size-6 text-accent-ink" aria-hidden />
          Comparer deux portefeuilles
        </h1>
        <p className="mt-2 max-w-[44rem] text-[15px] leading-relaxed text-ink-2">
          Même scénario, même analyse de l&apos;IA, deux répartitions : voyez lequel résiste le mieux. L&apos;analyse n&apos;est faite qu&apos;une fois pour les deux.
        </p>
      </header>

      <Carte taille="normale">
        <label htmlFor="scenario-duel" className={`${titreSection} mb-2 block`}>
          Votre scénario
        </label>
        <textarea
          id="scenario-duel"
          rows={3}
          maxLength={SCENARIO_LONGUEUR_MAX}
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          placeholder="Ex. : la BCE baisse ses taux de 1 point par surprise pour relancer l'économie…"
          className={`${champ} block resize-y leading-relaxed`}
        />
        <div role="group" aria-label="Idées de scénarios" className="mt-3 flex flex-wrap gap-1.5">
          {rapides.map((s) => (
            <button key={s.titre} type="button" aria-pressed={scenario === s.texte} onClick={() => setScenario(s.texte)} className={puce}>
              {s.titre}
            </button>
          ))}
        </div>
        <div className="mt-5">
          <label htmlFor="duree-duel" className="mb-2 flex items-baseline justify-between gap-2 text-sm font-medium">
            Horizon
            <span className="font-normal text-ink-2 tabular-nums">{duree} jours de bourse</span>
          </label>
          <input
            id="duree-duel"
            type="range"
            min={cat.horizon.min}
            max={cat.horizon.max}
            step={cat.horizon.pas}
            value={duree}
            onChange={(e) => setDuree(Number(e.target.value))}
            className="w-full accent-(--accent)"
          />
        </div>
      </Carte>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-start">
        <SelecteurPortefeuille etiquette="A" couleur={COULEUR_A} catalogue={cat} valeur={pa} onChange={setA} />
        <SelecteurPortefeuille etiquette="B" couleur={COULEUR_B} catalogue={cat} valeur={pb} onChange={setB} />
      </div>

      <div className="flex flex-col gap-2">
        {probleme && (
          <p role="alert" className="text-aide text-warn">
            {probleme}
          </p>
        )}
        <button type="button" onClick={lancer} disabled={!!probleme || enCours} className={`${boutonPrincipal} sm:w-72`}>
          {enCours ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Play className="size-4" aria-hidden />}
          {enCours ? "Comparaison en cours…" : "Comparer les portefeuilles"}
        </button>
      </div>

      <div ref={zoneResultat} className="min-w-0 scroll-mt-4" aria-busy={enCours} aria-live="polite">
        {serveurEnVeille ? (
          <ReveilServeur
            onPret={() => {
              setServeurEnVeille(false);
              void lancer();
            }}
          />
        ) : enCours ? (
          <Carte taille="normale">
            <p role="status" className="text-sm text-ink-2">
              Analyse du scénario par l&apos;IA, puis simulation des deux portefeuilles… (compter jusqu&apos;à une minute)
            </p>
          </Carte>
        ) : erreur ? (
          <Erreur message={erreur} onReessayer={lancer} />
        ) : resultat ? (
          <div className="flex flex-col gap-4">
            <TitreSection>Résultat</TitreSection>
            <p className="rounded-tuile border border-line bg-surface-2/60 px-4 py-3 text-sm">
              <strong className="font-semibold">{verdict(resultat)}</strong>
            </p>
            <TableauEcarts a={resultat.a} b={resultat.b} />
            <GraphiqueDuel a={resultat.a} b={resultat.b} />
            {resultat.a.analyse.explication && (
              <Carte taille="normale">
                <h3 className="text-titre font-semibold tracking-tight">Analyse de l&apos;IA (commune aux deux)</h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-2">{resultat.a.analyse.explication}</p>
              </Carte>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
