"use client";

import type { Analyse, FourchetteChoc } from "@/lib/api";
import { pourcentSigne } from "@/lib/format";
import { nomCourt } from "@/contenu/actifs";

// En dessous de 0,05 pt d'ecart, bas et haut sont confondus : pas de vraie fourchette a montrer.
const ECART_MIN = 0.0005;

type Ligne = { cle: string; nom: string; f: FourchetteChoc; aIntervalle: boolean };

/** Fourchette de l'IA par actif ; les anciens resultats sans fourchette retombent sur bas = haut = central. */
function lignesFourchettes(a: Analyse, noms: Map<string, string>): Ligne[] {
  return Object.keys(a.chocs).map((cle) => {
    const central = a.chocs[cle] ?? 0;
    const brut = a.fourchettes?.[cle];
    const f = {
      bas: Math.min(brut?.bas ?? central, central),
      central,
      haut: Math.max(brut?.haut ?? central, central),
    };
    return { cle, nom: nomCourt(cle, noms.get(cle)), f, aIntervalle: f.haut - f.bas > ECART_MIN };
  });
}

/** Chocs estimes par l'IA : valeur centrale + mini-intervalle bas -> haut sur une echelle commune. */
export function FourchettesIA({ a, noms }: { a: Analyse; noms: Map<string, string> }) {
  const lignes = lignesFourchettes(a, noms);
  if (!lignes.length) return null;
  const avecFourchette = lignes.some((l) => l.aIntervalle);
  // Echelle commune a tous les actifs, zero toujours inclus pour situer hausse et baisse.
  const min = Math.min(0, ...lignes.map((l) => l.f.bas));
  const max = Math.max(0, ...lignes.map((l) => l.f.haut));
  const etendue = max - min || 1;
  const pos = (v: number) => `${((v - min) / etendue) * 100}%`;

  return (
    <div className="mt-5 border-t border-line pt-5">
      <span className="text-aide font-medium text-muted">Chocs estimés par actif</span>
      <p className="mt-1 text-aide leading-relaxed text-ink-2">
        {avecFourchette ? (
          <>
            L&apos;IA ne donne pas un chiffre unique mais une <strong className="font-medium text-ink">fourchette</strong> :
            un choc bas, un choc central et un choc haut. En mode Monte-Carlo, chaque trajectoire tire son choc au hasard dans
            cette fourchette ; le choc central sert pour la trajectoire unique.
          </>
        ) : (
          <>Pour ce résultat, l&apos;IA n&apos;a donné qu&apos;un choc central par actif (pas de fourchette bas → haut).</>
        )}
      </p>
      <ul className="mt-3 flex flex-col">
        {lignes.map((l) => (
          <li key={l.cle} className="border-t border-line py-2.5 first:border-t-0 first:pt-0">
            <div className="flex items-baseline justify-between gap-3 text-sm">
              <span className="min-w-0 truncate">{l.nom}</span>
              <strong className="shrink-0 font-semibold tabular-nums">{pourcentSigne(l.f.central * 100)}</strong>
            </div>
            <div className="mt-1.5 flex items-center gap-3">
              <span className="relative h-1.5 min-w-0 flex-1 rounded-full bg-surface-2" aria-hidden>
                <span className="absolute -inset-y-0.5 w-px bg-line-strong" style={{ left: pos(0) }} />
                {l.aIntervalle && (
                  <span
                    className="absolute inset-y-0 rounded-full bg-accent/35"
                    style={{ left: pos(l.f.bas), width: `${((l.f.haut - l.f.bas) / etendue) * 100}%` }}
                  />
                )}
                <span
                  className="absolute top-1/2 size-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-accent"
                  style={{ left: pos(l.f.central) }}
                />
              </span>
              <span className="shrink-0 text-xs text-muted tabular-nums">
                {l.aIntervalle ? (
                  <>
                    <span className="sr-only">Fourchette de </span>
                    {pourcentSigne(l.f.bas * 100)} → {pourcentSigne(l.f.haut * 100)}
                  </>
                ) : (
                  <span title="Pas de fourchette fournie">—</span>
                )}
              </span>
            </div>
          </li>
        ))}
      </ul>
      {avecFourchette && (
        <p className="mt-2 text-xs text-muted">
          Point : choc central · bande : fourchette bas → haut · trait vertical : 0 %.
        </p>
      )}
    </div>
  );
}
