"use client";

import { motion } from "motion/react";
import type { CriseValidee, ValidationIA } from "@/lib/validation";
import { nombre } from "@/lib/format";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { EASE_SORTIE } from "@/components/motion/transitions";
import { Cle, COULEUR_IA } from "./BarresAppariees";
import { coefficient, ecartRelatif, part, points } from "./outils";

// La variante « avec date » est grisee : l'attention reste sur le test principal.
const COULEUR_AVEC_DATE = "var(--muted)";

function nomCourt(nom: string) {
  return nom.replace(/\s*\(.*\)$/, "");
}

function BarreErreur({ valeur, max, couleur, delai }: { valeur: number; max: number; couleur: string; delai: number }) {
  return (
    <span className="block h-2.5">
      <motion.span
        className="block h-full origin-left rounded-r"
        style={{ width: `${Math.max((valeur / max) * 100, 1)}%`, background: couleur }}
        initial={{ scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: EASE_SORTIE, delay: delai }}
      />
    </span>
  );
}

function ErreursParCrise({ crises }: { crises: CriseValidee[] }) {
  const avec = crises.filter((c) => c.avec_date);
  const max = Math.max(1, ...avec.flatMap((c) => [c.metriques.erreur_moyenne_pts ?? 0, c.avec_date!.metriques.erreur_moyenne_pts ?? 0]));
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-x-4 gap-y-1">
        <Cle couleur={COULEUR_IA}>Sans date (test principal)</Cle>
        <Cle couleur={COULEUR_AVEC_DATE}>Avec la date en indice</Cle>
      </div>
      <ul className="flex flex-col gap-2.5" aria-label="Erreur moyenne par crise, sans puis avec la date">
        {avec.map((c, i) => {
          const sans = c.metriques.erreur_moyenne_pts ?? 0;
          const date = c.avec_date!.metriques.erreur_moyenne_pts ?? 0;
          return (
            <li key={c.nom} className="grid grid-cols-[minmax(0,6.5rem)_minmax(0,1fr)_4.5rem] items-center gap-x-3 sm:grid-cols-[minmax(0,10rem)_minmax(0,1fr)_5rem]">
              <span className="text-[13px] leading-snug text-ink-2">{nomCourt(c.nom)}</span>
              <span className="flex flex-col gap-0.5" aria-hidden>
                <BarreErreur valeur={sans} max={max} couleur={COULEUR_IA} delai={i * 0.05} />
                <BarreErreur valeur={date} max={max} couleur={COULEUR_AVEC_DATE} delai={i * 0.05 + 0.08} />
              </span>
              <span className="flex flex-col text-right text-xs leading-tight tabular-nums">
                <span className="text-ink">
                  <span className="sr-only">sans date </span>
                  {points(sans)}
                </span>
                <span className="text-muted">
                  <span className="sr-only">avec date </span>
                  {points(date)}
                </span>
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/** Mesure du biais : la même description, avec puis sans la date de la crise. */
export function BiaisConnaissance({ v }: { v: ValidationIA }) {
  const b = v.biais_connaissance;
  if (b.nb_crises === 0) return null;
  const rapport = ecartRelatif(b.sans_date, b.avec_date);
  const lignes = [
    { libelle: "Erreur moyenne", sans: points(b.sans_date.erreur_moyenne_pts), avec: points(b.avec_date.erreur_moyenne_pts) },
    { libelle: "Bon sens de variation", sans: part(b.sans_date.part_sens_correct), avec: part(b.avec_date.part_sens_correct) },
    { libelle: "Corrélation", sans: coefficient(b.sans_date.correlation), avec: coefficient(b.avec_date.correlation) },
    { libelle: "Taille des chocs", sans: `×${nombre(b.sans_date.ratio_amplitude ?? 0, 2)}`, avec: `×${nombre(b.avec_date.ratio_amplitude ?? 0, 2)}` },
    ...(b.sans_date.part_dans_fourchette != null
      ? [
          { libelle: "Dans la fourchette", sans: part(b.sans_date.part_dans_fourchette), avec: part(b.avec_date.part_dans_fourchette ?? null) },
          { libelle: "Largeur de la fourchette", sans: points(b.sans_date.largeur_moyenne_pts ?? null), avec: points(b.avec_date.largeur_moyenne_pts ?? null) },
        ]
      : []),
    { libelle: "Crises reconnues", sans: `${b.nb_reconnues_sans_date} / ${b.nb_crises}`, avec: `${b.nb_reconnues_avec_date} / ${b.nb_crises}` },
  ];
  return (
    <Carte className="p-5 sm:p-6">
      <TitreCarte aide="L’IA a appris sur des textes qui racontent ces crises. Pour mesurer ce biais, on lui repose exactement la même question en ajoutant les dates de début et de fin.">
        Et si on lui donnait la date ?
      </TitreCarte>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
        <div className="self-start overflow-hidden rounded-xl border border-line">
          <table className="w-full text-sm">
            <thead className="bg-surface-2 text-left text-xs text-ink-2">
              <tr>
                <th scope="col" className="px-3 py-2 font-medium">
                  Sur {b.nb_crises} crises
                </th>
                <th scope="col" className="whitespace-nowrap px-3 py-2 text-right font-medium">
                  Sans date
                </th>
                <th scope="col" className="whitespace-nowrap px-3 py-2 text-right font-medium">
                  Avec date
                </th>
              </tr>
            </thead>
            <tbody>
              {lignes.map((l) => (
                <tr key={l.libelle} className="border-t border-line">
                  <th scope="row" className="px-3 py-2 text-left font-normal text-ink-2">
                    {l.libelle}
                  </th>
                  <td className="whitespace-nowrap px-3 py-2 text-right font-semibold text-ink tabular-nums">{l.sans}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-right text-ink-2 tabular-nums">{l.avec}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ErreursParCrise crises={v.crises} />
      </div>
      <p className="mt-5 max-w-[46rem] text-[15px] leading-relaxed text-ink-2">
        {rapport != null && rapport > 1.3
          ? `Avec la date, son erreur est ${nombre(rapport, 1).replace(",0", "")} fois plus petite : l’IA se souvient en partie des vrais chiffres. Sans la date, elle ne les récite donc pas : elle raisonne à partir du mécanisme décrit (en reconnaissant souvent la crise), d’où des chocs plus prudents.`
          : "Donner la date change peu ses estimations : elle raisonne surtout à partir du mécanisme décrit, ou reconnaît déjà la crise sans la date."}
      </p>
    </Carte>
  );
}
