"use client";

import { useId, useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { CalendarRange, ChevronDown, TriangleAlert } from "lucide-react";
import type { Catalogue, ReponseBacktest, SerieActif } from "@/lib/api";
import { euros, eurosCompacts, nombre, pourcentSigne } from "@/lib/format";
import { Carte, Pastille, TitreCarte } from "@/components/ui/Carte";
import { Apparition, Cascade, ElementCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { Legende, type SerieLigne } from "@/components/charts/GraphiqueLignes";
import { BarresPerformance } from "@/components/charts/BarresPerformance";
import { ListeAlertes, TuilesRisque } from "@/components/resultats/Risque";
import { DetailPortefeuille } from "@/components/resultats/DetailPortefeuille";
import { nomCourtProfil, PROFIL_PERSONNALISE } from "@/components/formulaire/ChoixPortefeuille";
import { BoutonsExport } from "@/components/exports/BoutonsExport";
import { GraphiqueDates } from "./GraphiqueDates";
import { dateCourte, dateLongue, demandeRapport, donneesCsv, dureeLisible } from "./outils";

const COULEURS = ["var(--series-1)", "var(--series-2)", "var(--series-3)", "var(--series-4)", "var(--series-5)"];
const SERIES_PAR_GRAPHIQUE = COULEURS.length;

const AIDE_INDICES: Record<string, string> = {
  "S&P 500": "Les 500 plus grandes entreprises américaines.",
  MSCI_World: "Environ 1 400 entreprises de 23 pays développés.",
};

const nomCourt = (nom: string) => nom.split(" (")[0];

function derniereValeur(valeurs: (number | null)[]): number | null {
  for (let i = valeurs.length - 1; i >= 0; i--) if (valeurs[i] != null) return valeurs[i];
  return null;
}

function EnTeteBacktest({ r, ajustee }: { r: ReponseBacktest; ajustee: boolean }) {
  const n = r.dates.length;
  const debut = r.dates[0];
  const fin = r.dates[n - 1];
  return (
    <Carte className="p-6 sm:p-7">
      <div className="flex flex-wrap items-center gap-1.5">
        <Pastille ton="gain">● Cours réels · Yahoo Finance</Pastille>
        {r.converti_eur && <Pastille>Converti en € (taux BCE)</Pastille>}
        {!r.evenement ? <Pastille ton="accent">Période libre</Pastille> : ajustee && <Pastille ton="accent">Période personnalisée</Pastille>}
      </div>
      <h2 className="mt-4 text-2xl font-semibold tracking-tight">{r.evenement ?? "Période libre"}</h2>
      {r.description && <p className="mt-1.5 text-[15px] leading-relaxed text-ink-2">{r.description}</p>}
      <p className="mt-4 flex items-start gap-2 text-sm text-ink-2">
        <CalendarRange className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />
        <span>
          Du <strong className="font-medium text-ink">{dateLongue(debut)}</strong> au <strong className="font-medium text-ink">{dateLongue(fin)}</strong>
          <span className="block text-muted">
            {n} séances de cotation · {dureeLisible(debut, fin)}
          </span>
        </span>
      </p>
    </Carte>
  );
}

function ActifsIndisponibles({ actifs, profil }: { actifs: ReponseBacktest["actifs_indisponibles"]; profil: string }) {
  const pluriel = actifs.length > 1;
  // Avec un profil type, l'API repartit le capital sur les actifs restants ; en Personnalise, la part prevue n'est pas investie.
  const consequence =
    profil === PROFIL_PERSONNALISE ? "la part que vous leur aviez attribuée n'a pas pu être investie" : "votre capital est réparti entre les actifs disponibles";
  return (
    <div role="status" className="flex gap-3 rounded-xl border border-warn/30 bg-warn-soft px-4 py-3.5 text-sm">
      <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
      <div className="min-w-0">
        <p className="font-semibold text-ink">
          {pluriel ? `${actifs.length} actifs indisponibles à cette époque` : "1 actif indisponible à cette époque"}
        </p>
        <p className="mt-0.5 leading-relaxed text-ink-2">
          {pluriel ? "Ils ne cotaient" : "Il ne cotait"} pas encore au début de la période : {pluriel ? "ils sont exclus" : "il est exclu"} du backtest et {consequence}.
        </p>
        <ul className="mt-2.5 flex flex-wrap gap-1.5" aria-label="Actifs indisponibles">
          {actifs.map((a) => (
            <li key={a.cle} className="rounded-full border border-warn/30 bg-surface/70 px-2.5 py-0.5 text-xs font-medium text-ink-2">
              {nomCourt(a.nom)}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

type Comparable = { cle: string; nom: string; aide: string; valeur: number | null; perf: number | null; principal?: boolean };

function CarteComparaison({ c, capital, perfPortefeuille }: { c: Comparable; capital: number; perfPortefeuille: number }) {
  const ecart = c.principal || c.perf == null ? null : perfPortefeuille - c.perf;
  return (
    <ElementCascade className="h-full">
      <motion.div
        whileHover={{ y: -2 }}
        transition={RESSORT}
        className={`flex h-full flex-col rounded-xl border p-4 transition-shadow hover:shadow-card ${c.principal ? "border-accent/40 bg-accent-soft/60" : "border-line bg-surface"}`}
      >
        <span className="text-xs font-semibold uppercase tracking-wider text-muted">{c.nom}</span>
        {c.valeur == null || c.perf == null ? (
          <span className="mt-2 text-sm text-muted">Non disponible sur cette période.</span>
        ) : (
          <>
            <NombreAnime valeur={c.valeur} depuis={capital} format={(v) => euros(v)} className="mt-1.5 block text-2xl font-semibold tracking-tight tabular-nums" />
            <span className={`mt-0.5 text-sm font-semibold tabular-nums ${c.perf >= 0 ? "text-gain" : "text-loss"}`}>
              <span aria-hidden>{c.perf >= 0 ? "▲ " : "▼ "}</span>
              {pourcentSigne(c.perf, 2)}
            </span>
            {ecart != null && (
              <span className="mt-2 text-xs leading-relaxed text-ink-2">
                {Math.abs(ecart) < 0.05
                  ? "Même performance que votre portefeuille."
                  : `Votre portefeuille fait ${ecart > 0 ? "mieux" : "moins bien"} de ${nombre(Math.abs(ecart), 1)} point${Math.abs(ecart) >= 2 ? "s" : ""}.`}
              </span>
            )}
          </>
        )}
        <span className="mt-auto pt-2 text-xs leading-relaxed text-muted">{c.aide}</span>
      </motion.div>
    </ElementCascade>
  );
}

function Synthese({ r, catalogue }: { r: ReponseBacktest; catalogue: Catalogue }) {
  const pf = r.portefeuille;
  const gain = pf.valeur_finale - pf.capital;
  const hausse = gain >= 0;
  const comparables: Comparable[] = [
    { cle: "portefeuille", nom: "Votre portefeuille", aide: "Vos actifs, selon votre répartition.", valeur: pf.valeur_finale, perf: pf.performance_pct, principal: true },
    ...catalogue.benchmarks.map((b) => {
      const serie = r.benchmarks.find((x) => x.cle === b.cle);
      const valeur = serie ? derniereValeur(serie.valeurs) : null;
      return { cle: b.cle, nom: nomCourt(b.nom), aide: AIDE_INDICES[b.cle] ?? "Indice de référence.", valeur, perf: valeur == null ? null : ((valeur - pf.capital) / pf.capital) * 100 };
    }),
  ];

  return (
    <Carte className="p-6 sm:p-7">
      <p className="text-sm text-ink-2">Valeur de votre portefeuille à la fin de la période</p>
      <div className="mt-1.5 flex flex-wrap items-end gap-x-4 gap-y-2">
        <NombreAnime valeur={pf.valeur_finale} depuis={pf.capital} format={(v) => euros(v)} className="text-5xl font-semibold tracking-tight tabular-nums sm:text-6xl" />
        <motion.span
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ ...RESSORT, delay: 0.25 }}
          className={`mb-1.5 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-base font-semibold tabular-nums ${hausse ? "bg-gain-soft text-gain" : "bg-loss-soft text-loss"}`}
        >
          <span aria-hidden>{hausse ? "▲" : "▼"}</span>
          <NombreAnime valeur={pf.performance_pct} depuis={0} format={(v) => pourcentSigne(v)} />
          <span className="font-medium opacity-80">
            ({hausse ? "+" : "−"}
            <NombreAnime valeur={Math.abs(gain)} depuis={0} format={(v) => euros(v)} />)
          </span>
        </motion.span>
      </div>
      <p className="mt-2 text-sm text-muted">
        Capital de départ {euros(pf.capital)} · profil {nomCourtProfil(r.parametres.profil).toLowerCase()} · {r.allocations.length} actif{r.allocations.length > 1 ? "s" : ""} en portefeuille
      </p>

      <div className="mt-6 border-t border-line pt-5">
        <h3 className="text-xs font-medium text-muted">Face aux indices de référence : même capital, même période</h3>
        <Cascade className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
          {comparables.map((c) => (
            <CarteComparaison key={c.cle} c={c} capital={pf.capital} perfPortefeuille={pf.performance_pct} />
          ))}
        </Cascade>
      </div>
    </Carte>
  );
}

function TableauDepliable({ dates, series, format, legende }: { dates: string[]; series: SerieLigne[]; format: (v: number) => string; legende: string }) {
  const [ouvert, setOuvert] = useState(false);
  const id = useId();
  const n = dates.length;
  const pas = Math.max(1, Math.round(n / 12));
  const lignes = dates.map((_, i) => i).filter((i) => i % pas === 0 || i === n - 1);

  return (
    <div className="mt-3">
      <button
        type="button"
        aria-expanded={ouvert}
        aria-controls={id}
        onClick={() => setOuvert((o) => !o)}
        className="inline-flex items-center gap-1 rounded-md text-xs font-medium text-accent-ink hover:underline"
      >
        {ouvert ? "Masquer le tableau" : "Voir les valeurs en tableau"}
        <motion.span animate={{ rotate: ouvert ? 180 : 0 }} transition={RESSORT} className="inline-flex">
          <ChevronDown className="size-3.5" aria-hidden />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {ouvert && (
          <motion.div
            id={id}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
            className="overflow-hidden"
          >
            <div className="mt-3 overflow-x-auto">
              <table className="w-full min-w-96 text-right text-xs tabular-nums">
                <caption className="sr-only">{legende}</caption>
                <thead className="text-muted">
                  <tr>
                    <th scope="col" className="py-1.5 text-left font-medium">
                      Date
                    </th>
                    {series.map((s) => (
                      <th key={s.nom} scope="col" className="py-1.5 pl-3 font-medium">
                        {s.nom}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {lignes.map((i) => (
                    <tr key={i} className="border-t border-line">
                      <th scope="row" className="whitespace-nowrap py-1.5 text-left font-normal">
                        {dateCourte(dates[i])}
                      </th>
                      {series.map((s) => {
                        const v = s.valeurs[i];
                        return (
                          <td key={s.nom} className="py-1.5 pl-3">
                            {v != null ? format(v) : "—"}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Evolution({ r }: { r: ReponseBacktest }) {
  const pf = r.portefeuille;
  const n = r.dates.length;
  const series: SerieLigne[] = [
    { nom: "Votre portefeuille", couleur: COULEURS[0], valeurs: pf.valeurs, principale: true },
    ...r.benchmarks.map((b, i) => ({ nom: nomCourt(b.nom), couleur: COULEURS[(i + 1) % COULEURS.length], valeurs: b.valeurs })),
  ];
  const description = `Valeur réelle du portefeuille du ${dateLongue(r.dates[0])} au ${dateLongue(r.dates[n - 1])}, de ${euros(pf.capital)} à ${euros(pf.valeur_finale)}, comparée aux indices de référence.`;
  return (
    <Carte className="p-6">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <TitreCarte aide="Ce qu'est devenu votre capital, séance après séance, comparé au même capital placé sur les indices de référence.">Évolution du portefeuille</TitreCarte>
        <Legende series={series} reference="Capital de départ" />
      </div>
      <GraphiqueDates
        dates={r.dates}
        series={series}
        formatY={eurosCompacts}
        formatValeur={(v) => euros(v)}
        reference={{ valeur: pf.capital, nom: "Capital de départ" }}
        description={description}
      />
      <TableauDepliable dates={r.dates} series={series} format={(v) => euros(v)} legende={description} />
    </Carte>
  );
}

type Groupe = { titre: string; actifs: SerieActif[] };

function grouperParClasse(r: ReponseBacktest, catalogue: Catalogue): Groupe[] {
  const rangs = new Map(catalogue.categories.flatMap((c) => c.actifs.map((a) => a.cle)).map((cle, i) => [cle, i]));
  const ordreCategories = catalogue.categories.map((c) => c.nom);
  const parCategorie = new Map<string, SerieActif[]>();
  for (const a of r.actifs) parCategorie.set(a.categorie, [...(parCategorie.get(a.categorie) ?? []), a]);
  const categories = [...parCategorie.keys()].sort((a, b) => ordreCategories.indexOf(a) - ordreCategories.indexOf(b));
  return categories.flatMap((categorie) => {
    const actifs = [...(parCategorie.get(categorie) ?? [])].sort((a, b) => (rangs.get(a.cle) ?? 99) - (rangs.get(b.cle) ?? 99));
    // Au-dela de 5 courbes un graphique devient illisible : on le coupe en plusieurs.
    const morceaux = Math.ceil(actifs.length / SERIES_PAR_GRAPHIQUE);
    return Array.from({ length: morceaux }, (_, k) => ({
      titre: morceaux > 1 ? `${categorie} (${k + 1}/${morceaux})` : categorie,
      actifs: actifs.slice(k * SERIES_PAR_GRAPHIQUE, (k + 1) * SERIES_PAR_GRAPHIQUE),
    }));
  });
}

function base100(prix: (number | null)[]): (number | null)[] {
  const base = prix.find((p) => p != null && p > 0);
  return base ? prix.map((p) => (p == null ? null : (p / base) * 100)) : prix.map(() => null);
}

function CourbesParClasse({ r, catalogue }: { r: ReponseBacktest; catalogue: Catalogue }) {
  const groupes = useMemo(() => grouperParClasse(r, catalogue), [r, catalogue]);
  const debut = dateCourte(r.dates[0]);
  return (
    <section aria-labelledby="titre-classes" className="flex flex-col gap-3">
      <div className="mt-2">
        <h3 id="titre-classes" className="text-[15px] font-semibold tracking-tight">
          Les cours par classe d&apos;actifs
        </h3>
        <p className="mt-1 text-sm leading-relaxed text-ink-2">
          Base 100 au {debut} : 120 signifie +20 %, 80 signifie −20 %{r.converti_eur ? ", en euros" : ""}.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {groupes.map((g, i) => {
          const series: SerieLigne[] = g.actifs.map((a, k) => ({ nom: nomCourt(a.nom), couleur: COULEURS[k], valeurs: base100(a.prix), principale: k === 0 }));
          return (
            // Un graphique seul sur sa ligne prend toute la largeur.
            <Apparition
              key={g.titre}
              auDefilement
              delai={(i % 2) * 0.08}
              className={`min-w-0 ${groupes.length % 2 === 1 && i === groupes.length - 1 ? "xl:col-span-2" : ""}`}
            >
              <Carte className="h-full p-5">
                <div className="mb-3 flex flex-wrap items-start justify-between gap-x-3 gap-y-2">
                  <h4 className="text-sm font-semibold">{g.titre}</h4>
                  <Legende series={series} />
                </div>
                <GraphiqueDates
                  dates={r.dates}
                  series={series}
                  hauteur={240}
                  formatY={(v) => nombre(v, 0)}
                  formatValeur={(v) => nombre(v, 1)}
                  reference={{ valeur: 100, nom: "Base 100" }}
                  description={`${g.titre} : cours en base 100 de ${series.map((s) => s.nom).join(", ")} du ${debut} au ${dateCourte(r.dates[r.dates.length - 1])}.`}
                />
              </Carte>
            </Apparition>
          );
        })}
      </div>
    </section>
  );
}

type Props = { reponse: ReponseBacktest; catalogue: Catalogue };

export function ResultatsBacktest({ reponse: r, catalogue }: Props) {
  const evenement = catalogue.evenements_historiques.find((e) => e.nom === r.evenement);
  const ajustee = !!evenement && (r.date_debut !== evenement.debut || r.date_fin !== evenement.fin);
  const csv = useMemo(() => donneesCsv(r), [r]);
  const rapport = useMemo(() => demandeRapport(r), [r]);
  const n = r.dates.length;

  return (
    <div className="flex flex-col gap-4">
      <Apparition>
        <EnTeteBacktest r={r} ajustee={ajustee} />
      </Apparition>

      {r.actifs_indisponibles.length > 0 && (
        <Apparition delai={0.06}>
          <ActifsIndisponibles actifs={r.actifs_indisponibles} profil={r.parametres.profil} />
        </Apparition>
      )}

      <Apparition delai={0.12}>
        <Synthese r={r} catalogue={catalogue} />
      </Apparition>

      <Apparition auDefilement>
        <Evolution r={r} />
      </Apparition>

      <section aria-labelledby="titre-risque" className="flex flex-col gap-3">
        <div className="mt-2">
          <h3 id="titre-risque" className="text-[15px] font-semibold tracking-tight">
            Le risque, mesuré sur les vrais cours
          </h3>
          <p className="mt-1 text-sm leading-relaxed text-ink-2">Calculé sur les {n} séances réelles de la période, pas sur une simulation.</p>
        </div>
        <TuilesRisque m={r.metriques} />
        <ListeAlertes alertes={r.alertes} />
      </section>

      <Apparition auDefilement>
        <Carte className="p-6">
          <TitreCarte aide={`Variation réelle de chaque actif entre le ${dateCourte(r.dates[0])} et le ${dateCourte(r.dates[n - 1])}${r.converti_eur ? ", en euros" : ""}.`}>
            Performance par actif
          </TitreCarte>
          <BarresPerformance lignes={r.actifs.map((a) => ({ cle: a.cle, nom: a.nom, valeur: a.performance_pct }))} />
        </Carte>
      </Apparition>

      <CourbesParClasse r={r} catalogue={catalogue} />

      <Apparition auDefilement>
        <DetailPortefeuille
          allocations={r.allocations}
          capital={r.portefeuille.capital}
          valeurFinale={r.portefeuille.valeur_finale}
          performancePct={r.portefeuille.performance_pct}
          aide="Ce que serait devenue chaque ligne de votre portefeuille sur cette période, aux vrais cours."
        />
      </Apparition>

      <Apparition auDefilement>
        <BoutonsExport csv={csv} rapport={rapport} />
      </Apparition>

      <p className="px-1 text-xs leading-relaxed text-muted">
        Outil pédagogique : les performances passées ne préjugent pas des performances futures. Frais et fiscalité ne sont pas pris en compte. Ce n&apos;est pas un conseil en investissement.
      </p>
    </div>
  );
}
