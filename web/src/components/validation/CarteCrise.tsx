"use client";

import { ChevronDown, Quote } from "lucide-react";
import type { CriseValidee } from "@/lib/validation";
import { Carte, Pastille } from "@/components/ui/Carte";
import { BarresAppariees } from "./BarresAppariees";
import { coefficient, periode, points } from "./outils";

function Statistique({ libelle, valeur }: { libelle: string; valeur: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-[11px] text-muted">{libelle}</dt>
      <dd className="mt-0.5 text-base font-semibold text-ink">{valeur}</dd>
    </div>
  );
}

/** Une crise : ce qu'on a dit à l'IA, ses scores, et l'estimation face à la réalité, actif par actif. */
export function CarteCrise({ crise }: { crise: CriseValidee }) {
  const m = crise.metriques;
  const ecretes = crise.actifs.filter((a) => a.ecrete);
  const enDeviseLocale = crise.actifs.filter((a) => a.devise && a.devise !== "EUR");
  const titreId = `crise-${crise.nom.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}`;
  return (
    <Carte className="p-4 sm:p-6">
      <header>
        <div className="flex flex-wrap items-start justify-between gap-2">
          <h3 id={titreId} className="text-lg font-semibold tracking-tight text-ink">
            {crise.nom}
          </h3>
          {crise.reconnue ? (
            <Pastille ton="alerte">Reconnue par l’IA</Pastille>
          ) : (
            <Pastille ton="gain">Non reconnue</Pastille>
          )}
        </div>
        <p className="mt-1 text-xs text-muted">
          {periode(crise.premiere_seance, crise.derniere_seance)} · {crise.nb_seances} séances ({crise.duree})
        </p>
      </header>

      <figure className="mt-4 rounded-xl bg-surface-2 px-3.5 py-3">
        <figcaption className="mb-1 flex items-center gap-1.5 text-[11px] font-medium text-ink-2">
          <Quote className="size-3" aria-hidden />
          Ce que l’IA a lu (ni nom ni date)
        </figcaption>
        <blockquote className="text-[13px] leading-relaxed text-ink-2">{crise.description_neutre}</blockquote>
        {crise.evenement_cite && (
          <p className="mt-2 text-[12px] text-muted">
            Événement cité par l’IA : <span className="font-medium text-ink-2">« {crise.evenement_cite} »</span>
          </p>
        )}
      </figure>

      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-4">
        <Statistique libelle="Bon sens" valeur={`${m.nb_sens_corrects} / ${m.nb_sens_comptes}`} />
        <Statistique libelle="Erreur moyenne" valeur={points(m.erreur_moyenne_pts)} />
        <Statistique libelle="Corrélation" valeur={coefficient(m.correlation)} />
        <Statistique libelle="Avec la date" valeur={crise.avec_date ? points(crise.avec_date.metriques.erreur_moyenne_pts) : "—"} />
      </dl>

      <div className="mt-5" aria-labelledby={titreId}>
        <BarresAppariees actifs={crise.actifs} />
      </div>

      <div className="flex flex-col gap-1 pt-4 text-[11px] leading-relaxed text-muted">
        {ecretes.length > 0 && (
          <p>
            * Plafonné par les garde-fous du simulateur : {ecretes.map((a) => `${a.nom_court} (IA ${Math.round(a.estime_devise_pct)} % avant conversion)`).join(", ")}.
          </p>
        )}
        {enDeviseLocale.length > 0 && (
          <p>{enDeviseLocale.map((a) => a.nom_court).join(" et ")} : comparés dans leur devise (l’IA n’estime ni la livre ni le yen).</p>
        )}
        {crise.actifs_absents.length > 0 && <p>Pas encore cotés à l’époque : {crise.actifs_absents.map((a) => a.nom.replace(/\s*\(.*\)$/, "")).join(", ")}.</p>}
      </div>

      {crise.explication && (
        <details className="group mt-3 rounded-xl border border-line">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-3.5 py-2.5 text-sm font-medium text-ink-2 transition-colors hover:text-ink [&::-webkit-details-marker]:hidden">
            Lire l’analyse de l’IA
            <ChevronDown className="size-4 transition-transform group-open:rotate-180" aria-hidden />
          </summary>
          <p className="border-t border-line px-3.5 py-3 text-[13px] leading-relaxed text-ink-2">{crise.explication}</p>
        </details>
      )}
    </Carte>
  );
}
