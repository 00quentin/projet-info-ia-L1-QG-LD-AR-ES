"use client";

import { ChevronDown, Play, Sparkles } from "lucide-react";
import type { Catalogue } from "@/lib/api";
import { Interrupteur } from "@/components/ui/Carte";

export type Reglages = {
  scenarios: string[];
  capital: number;
  profil: string;
  actifs: string[];
  allocations: Record<string, number>;
  duree: number;
  modele: string;
  monteCarlo: boolean;
  prixReels: boolean;
  calibration: boolean;
  convertirEur: boolean;
};

export const PROFIL_PERSONNALISE = "Personnalisé";
const SCENARIO_LONGUEUR_MIN = 10;
const SCENARIO_LONGUEUR_MAX = 1000;

const DESCRIPTIONS_PROFIL: Record<string, string> = {
  Prudent: "Surtout des obligations et de l'or",
  Équilibré: "Actions, obligations, un peu de crypto",
  Agressif: "Actions et cryptomonnaies",
  Personnalisé: "Vous fixez chaque part",
};
const DESCRIPTIONS_MODELE: Record<string, string> = {
  Probabiliste: "Variations quotidiennes classiques (loi normale)",
  Historique: "Rejoue de vraies séances de bourse, chocs violents inclus",
  Machine: "Tendance qui s'auto-entretient et s'accélère",
};

const nomCourt = (profil: string) => profil.split(" (")[0];

export function reglagesInitiaux(catalogue: Catalogue): Reglages {
  const equilibre = catalogue.profils.find((p) => p.nom.startsWith("Équilibré")) ?? catalogue.profils[0];
  return {
    scenarios: [catalogue.scenarios_par_defaut[0]],
    capital: catalogue.capital.defaut,
    profil: equilibre.nom,
    actifs: catalogue.categories.flatMap((c) => c.actifs.filter((a) => a.par_defaut).map((a) => a.cle)),
    allocations: {},
    duree: catalogue.horizon.defaut,
    modele: catalogue.modeles[0],
    monteCarlo: true,
    prixReels: true,
    calibration: true,
    convertirEur: true,
  };
}

/** Message d'erreur a afficher, ou null si la demande peut partir. */
export function validerReglages(r: Reglages): string | null {
  if (r.scenarios.some((s) => s.trim().length < SCENARIO_LONGUEUR_MIN)) return "Décrivez votre scénario en au moins 10 caractères.";
  if (r.actifs.length === 0) return "Sélectionnez au moins un actif.";
  if (r.profil === PROFIL_PERSONNALISE) {
    const total = r.actifs.reduce((s, a) => s + (r.allocations[a] ?? 0), 0);
    if (total !== 100) return `La répartition doit totaliser 100 % (actuellement ${total} %).`;
  }
  return null;
}

type Props = {
  catalogue: Catalogue;
  reglages: Reglages;
  onChange: (r: Reglages) => void;
  onLancer: () => void;
  enCours: boolean;
};

const titreSection = "text-xs font-semibold uppercase tracking-wider text-muted";
const champ =
  "w-full rounded-xl border border-line bg-surface px-3.5 py-2.5 text-sm outline-none transition placeholder:text-muted focus:border-accent focus:ring-2 focus:ring-accent/20";

export function FormulaireSimulation({ catalogue, reglages: r, onChange, onLancer, enCours }: Props) {
  const maj = (partiel: Partial<Reglages>) => onChange({ ...r, ...partiel });
  const erreur = validerReglages(r);
  const totalPerso = r.actifs.reduce((s, a) => s + (r.allocations[a] ?? 0), 0);

  function choisirProfil(nom: string) {
    const profil = catalogue.profils.find((p) => p.nom === nom);
    // On ajoute les actifs du profil a la selection : sinon une partie du profil serait ignoree.
    const actifs = profil?.poids ? Array.from(new Set([...r.actifs, ...Object.keys(profil.poids)])) : r.actifs;
    maj({ profil: nom, actifs });
  }

  function basculerActif(cle: string) {
    const actifs = r.actifs.includes(cle) ? r.actifs.filter((a) => a !== cle) : [...r.actifs, cle];
    maj({ actifs });
  }

  function repartirEgalement() {
    const n = r.actifs.length;
    if (n === 0) return;
    const base = Math.floor(100 / n);
    const allocations = Object.fromEntries(r.actifs.map((a, i) => [a, base + (i < 100 - base * n ? 1 : 0)]));
    maj({ allocations });
  }

  return (
    <form
      noValidate
      className="flex flex-col gap-7"
      onSubmit={(e) => {
        e.preventDefault();
        if (!erreur && !enCours) onLancer();
      }}
    >
      {/* 1. Scenario */}
      <fieldset className="flex flex-col gap-3">
        <legend className={titreSection}>1 · Votre scénario</legend>
        <label htmlFor="scenario" className="sr-only">
          Événement économique à simuler
        </label>
        <textarea
          id="scenario"
          rows={4}
          maxLength={SCENARIO_LONGUEUR_MAX}
          value={r.scenarios[0]}
          onChange={(e) => maj({ scenarios: [e.target.value] })}
          placeholder="Ex. : la BCE baisse ses taux de 1 point par surprise pour relancer l'économie…"
          className={`${champ} mt-3 resize-y leading-relaxed`}
        />
        <p className="text-xs leading-relaxed text-muted">Plus vous êtes précis (pays, secteur, ampleur, durée), plus l&apos;analyse est pertinente.</p>
        <div className="flex flex-wrap gap-1.5">
          {catalogue.scenarios_rapides.map((s) => (
            <button
              key={s.titre}
              type="button"
              onClick={() => maj({ scenarios: [s.texte] })}
              aria-pressed={r.scenarios[0] === s.texte}
              className="rounded-full border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-2 transition hover:border-accent hover:text-accent-ink aria-pressed:border-accent aria-pressed:bg-accent-soft aria-pressed:text-accent-ink"
            >
              {s.titre}
            </button>
          ))}
        </div>
      </fieldset>

      {/* 2. Portefeuille */}
      <fieldset className="flex flex-col gap-3">
        <legend className={titreSection}>2 · Votre portefeuille</legend>
        <div className="mt-3">
          <label htmlFor="capital" className="mb-1.5 block text-sm font-medium">
            Capital de départ
          </label>
          <div className="relative">
            <input
              id="capital"
              type="number"
              inputMode="numeric"
              min={catalogue.capital.min}
              max={catalogue.capital.max}
              step={catalogue.capital.pas}
              value={r.capital}
              onChange={(e) => maj({ capital: Math.min(catalogue.capital.max, Math.max(0, Number(e.target.value))) })}
              onBlur={() => maj({ capital: Math.max(catalogue.capital.min, r.capital) })}
              className={`${champ} pr-9 tabular-nums`}
            />
            <span className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-sm text-muted">€</span>
          </div>
        </div>

        <div role="radiogroup" aria-label="Profil d'investisseur" className="grid grid-cols-2 gap-2">
          {catalogue.profils.map((p) => {
            const choisi = r.profil === p.nom;
            return (
              <button
                key={p.nom}
                type="button"
                role="radio"
                aria-checked={choisi}
                onClick={() => choisirProfil(p.nom)}
                className={`rounded-xl border px-3 py-2.5 text-left transition ${
                  choisi ? "border-accent bg-accent-soft" : "border-line bg-surface hover:border-line-strong"
                }`}
              >
                <span className={`block text-sm font-semibold ${choisi ? "text-accent-ink" : ""}`}>{nomCourt(p.nom)}</span>
                <span className="mt-0.5 block text-xs leading-snug text-muted">{DESCRIPTIONS_PROFIL[nomCourt(p.nom)]}</span>
              </button>
            );
          })}
        </div>

        <details className="group rounded-xl border border-line bg-surface" open={r.profil === PROFIL_PERSONNALISE || undefined}>
          <summary className="flex cursor-pointer list-none items-center justify-between px-3.5 py-2.5 text-sm font-medium">
            <span>
              Actifs <span className="font-normal text-muted">· {r.actifs.length} sélectionné{r.actifs.length > 1 ? "s" : ""}</span>
            </span>
            <ChevronDown className="size-4 text-muted transition group-open:rotate-180" aria-hidden />
          </summary>
          <div className="flex flex-col gap-4 border-t border-line px-3.5 py-3">
            {catalogue.categories.map((c) => (
              <div key={c.nom}>
                <div className="mb-1.5 text-xs font-medium text-muted">{c.nom}</div>
                <div className="flex flex-col">
                  {c.actifs.map((a) => {
                    const coche = r.actifs.includes(a.cle);
                    return (
                      <div key={a.cle} className="flex items-center justify-between gap-2 py-1">
                        <label className="flex min-w-0 cursor-pointer items-center gap-2.5 text-sm">
                          <input type="checkbox" checked={coche} onChange={() => basculerActif(a.cle)} className="size-4 shrink-0 accent-(--accent)" />
                          <span className="truncate">{a.nom}</span>
                        </label>
                        {r.profil === PROFIL_PERSONNALISE && coche && (
                          <span className="flex shrink-0 items-center gap-1 text-sm text-muted">
                            <input
                              type="number"
                              min={0}
                              max={100}
                              aria-label={`Part de ${a.nom} en pourcentage`}
                              value={r.allocations[a.cle] ?? 0}
                              onChange={(e) =>
                                maj({ allocations: { ...r.allocations, [a.cle]: Math.min(100, Math.max(0, Math.round(Number(e.target.value)))) } })
                              }
                              className="w-16 rounded-lg border border-line bg-surface px-2 py-1 text-right text-sm text-ink tabular-nums outline-none focus:border-accent"
                            />
                            %
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
            {r.profil === PROFIL_PERSONNALISE && (
              <div className="flex items-center justify-between border-t border-line pt-3 text-sm">
                <span className={totalPerso === 100 ? "text-gain" : "text-warn"}>
                  Total : <strong className="tabular-nums">{totalPerso} %</strong> {totalPerso === 100 ? "✓" : "(doit faire 100 %)"}
                </span>
                <button type="button" onClick={repartirEgalement} className="text-sm font-medium text-accent-ink hover:underline">
                  Répartir également
                </button>
              </div>
            )}
          </div>
        </details>
        {r.profil !== PROFIL_PERSONNALISE && (
          <p className="text-xs leading-relaxed text-muted">
            Le capital est réparti selon le profil choisi. Les autres actifs cochés sont analysés à titre de comparaison.
          </p>
        )}
      </fieldset>

      {/* 3. Options */}
      <details className="group">
        <summary className={`flex cursor-pointer list-none items-center justify-between ${titreSection}`}>
          3 · Options avancées
          <ChevronDown className="size-4 transition group-open:rotate-180" aria-hidden />
        </summary>
        <div className="mt-4 flex flex-col gap-4">
          <div>
            <label htmlFor="duree" className="mb-1.5 flex items-center justify-between text-sm font-medium">
              Horizon
              <span className="font-normal text-ink-2 tabular-nums">{r.duree} jours de bourse</span>
            </label>
            <input
              id="duree"
              type="range"
              min={catalogue.horizon.min}
              max={catalogue.horizon.max}
              step={catalogue.horizon.pas}
              value={r.duree}
              onChange={(e) => maj({ duree: Number(e.target.value) })}
              className="w-full accent-(--accent)"
            />
          </div>
          <div>
            <label htmlFor="modele" className="mb-1.5 block text-sm font-medium">
              Comportement du marché
            </label>
            <select id="modele" value={r.modele} onChange={(e) => maj({ modele: e.target.value })} className={champ}>
              {catalogue.modeles.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <p className="mt-1.5 text-xs text-muted">{DESCRIPTIONS_MODELE[r.modele.split(" ")[0]]}</p>
          </div>
          <div className="divide-y divide-line">
            <Interrupteur
              actif={r.monteCarlo}
              onChange={(v) => maj({ monteCarlo: v })}
              libelle={`Monte-Carlo (${catalogue.nb_simulations_monte_carlo.toLocaleString("fr-FR")} trajectoires)`}
              aide="Affiche la fourchette des issues possibles et la probabilité de perte."
            />
            <Interrupteur actif={r.convertirEur} onChange={(v) => maj({ convertirEur: v })} libelle="Convertir en euros" aide="Tient compte du taux de change, comme le vivrait un investisseur européen." />
            <Interrupteur actif={r.calibration} onChange={(v) => maj({ calibration: v })} libelle="Calibration historique" aide="L'IA s'ancre sur les amplitudes de crises réelles (2008, COVID, 2022…)." />
            <Interrupteur actif={r.prixReels} onChange={(v) => maj({ prixReels: v })} libelle="Prix de marché actuels" aide="Part des dernières clôtures et des volatilités réelles (Yahoo Finance)." />
          </div>
        </div>
      </details>

      <div className="sticky bottom-0 z-10 -mx-5 -mb-5 flex flex-col gap-2 rounded-b-2xl border-t border-line bg-surface/95 px-5 py-4 backdrop-blur">
        {erreur && (
          <p role="alert" className="text-xs text-warn">
            {erreur}
          </p>
        )}
        <button
          type="submit"
          disabled={!!erreur || enCours}
          className="flex h-11 items-center justify-center gap-2 rounded-xl bg-accent text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {enCours ? <Sparkles className="size-4 animate-pulse" aria-hidden /> : <Play className="size-4" aria-hidden />}
          {enCours ? "Analyse en cours…" : "Lancer la simulation"}
        </button>
      </div>
    </form>
  );
}
