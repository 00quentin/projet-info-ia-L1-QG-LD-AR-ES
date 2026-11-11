// Outils du backtest : dates en francais, periode choisie, contenu des exports.

import type { DemandeRapport, EvenementHistorique, ReponseBacktest } from "@/lib/api";
import type { PropsExport } from "@/components/exports/BoutonsExport";
import { dateFr } from "@/lib/format";

// Miroir de API_BACKTEST_JOURS_MAX (config.py) : l'API refuse au-dela.
export const PERIODE_JOURS_MAX = 3660;
/** Les taux BCE (conversion en euros) commencent en 1999. */
const DATE_MIN_EUR = "1999-01-04";
const DATE_MIN = "1990-01-02";
export const dateMin = (convertirEur: boolean) => (convertirEur ? DATE_MIN_EUR : DATE_MIN);

const UTC = { timeZone: "UTC" } as const;
const fmtJourMoisAn = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short", year: "numeric", ...UTC });
const fmtLong = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "long", year: "numeric", ...UTC });
const fmtMois = new Intl.DateTimeFormat("fr-FR", { month: "short", ...UTC });
const fmtMoisAn = new Intl.DateTimeFormat("fr-FR", { month: "short", year: "numeric", ...UTC });

// Midi UTC : la date reste la meme quel que soit le fuseau du visiteur.
const versDate = (iso: string) => new Date(`${iso}T12:00:00Z`);
const JOUR_MS = 86_400_000;

/** "17 févr. 2020" */
export const dateCourte = (iso: string) => fmtJourMoisAn.format(versDate(iso));
/** "17 février 2020" */
export const dateLongue = (iso: string) => fmtLong.format(versDate(iso));

export function joursEntre(debut: string, fin: string): number {
  return Math.round((versDate(fin).getTime() - versDate(debut).getTime()) / JOUR_MS);
}

/** "févr. → avr. 2020" ou "mars 2000 → oct. 2002" */
export function periodeCourte(debut: string, fin: string): string {
  const memeAnnee = debut.slice(0, 4) === fin.slice(0, 4);
  return `${(memeAnnee ? fmtMois : fmtMoisAn).format(versDate(debut))} → ${fmtMoisAn.format(versDate(fin))}`;
}

/** "2 mois", "1 an et 8 mois", "12 jours" */
export function dureeLisible(debut: string, fin: string): string {
  const jours = joursEntre(debut, fin);
  const mois = Math.round(jours / 30.44);
  if (mois < 1) return `${jours} jour${jours > 1 ? "s" : ""}`;
  if (mois < 12) return `${mois} mois`;
  const ans = Math.floor(mois / 12);
  const reste = mois % 12;
  return `${ans} an${ans > 1 ? "s" : ""}${reste ? ` et ${reste} mois` : ""}`;
}

export function aujourdhui(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Une periode personnalisee qui recouvre encore l'evenement garde son nom ; sinon c'est une periode libre. */
export function recouvreEvenement(debut: string, fin: string, e: EvenementHistorique): boolean {
  return debut <= e.fin && fin >= e.debut;
}

/** Message d'erreur a afficher, ou null si la periode peut partir. */
export function validerPeriode(debut: string, fin: string, convertirEur: boolean): string | null {
  if (!debut || !fin) return "Indiquez une date de début et une date de fin.";
  if (convertirEur && debut < DATE_MIN_EUR) return "Les taux de change BCE commencent en janvier 1999 : choisissez une date plus récente ou désactivez la conversion en euros.";
  if (debut < DATE_MIN) return "Les données commencent en 1990 : choisissez une date de début plus récente.";
  if (fin > aujourdhui()) return "La date de fin ne peut pas être dans le futur.";
  if (fin <= debut) return "La date de fin doit être après la date de début.";
  if (joursEntre(debut, fin) > PERIODE_JOURS_MAX) return "La période d'un backtest est limitée à 10 ans.";
  return null;
}

/** Nom affiche du backtest : l'evenement, ou la periode libre demandee. */
export function libelleBacktest(r: Pick<ReponseBacktest, "evenement" | "date_debut" | "date_fin">): string {
  return r.evenement ?? `période du ${dateFr(r.date_debut)} au ${dateFr(r.date_fin)}`;
}

export const scenarioBacktest = (r: Pick<ReponseBacktest, "evenement" | "date_debut" | "date_fin">) => `Backtest : ${libelleBacktest(r)}`;

function phrasePeriode(r: ReponseBacktest): string {
  const n = r.dates.length;
  return `Période réelle : du ${dateFr(r.dates[0])} au ${dateFr(r.dates[n - 1])} (${n} séances de cotation).`;
}

const slug = (texte: string) =>
  texte
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "")
    .slice(0, 40);

const arrondi = (v: number) => Math.round(v * 100) / 100;

/**
 * Une ligne par seance : valeur du portefeuille, valeur de chaque ligne du
 * portefeuille (comme l'export de l'ancienne app), puis cours de chaque actif.
 */
export function donneesCsv(r: ReponseBacktest): PropsExport["csv"] {
  const unite = r.converti_eur ? " (€)" : "";
  const parCle = new Map(r.actifs.map((a) => [a.cle, a]));
  const lignes = r.allocations.flatMap((l) => {
    const serie = parCle.get(l.cle);
    const base = serie?.prix[0];
    if (!serie || !base) return [];
    return [{ nom: `${l.nom} — ligne du portefeuille (€)`, valeurs: serie.prix.map((p) => (p == null ? null : arrondi((l.investi * p) / base))) }];
  });
  const jour = new Date().toISOString().slice(0, 10).replaceAll("-", "");
  return {
    nomFichier: `quant_terminal_backtest_${slug(libelleBacktest(r))}_${jour}`,
    titreColonneEtiquette: "Date",
    etiquettes: r.dates,
    colonnes: [
      { nom: "Valeur du portefeuille (€)", valeurs: r.portefeuille.valeurs.map((v) => (v == null ? null : arrondi(v))) },
      ...lignes,
      ...r.actifs.map((a) => ({ nom: `${a.nom} — cours${unite}`, valeurs: a.prix })),
    ],
  };
}

/** Contenu du rapport PDF, a partir de la reponse deja affichee. */
export function demandeRapport(r: ReponseBacktest): DemandeRapport {
  const m = r.metriques;
  return {
    type_rapport: "Backtest",
    scenario: scenarioBacktest(r),
    profil: r.parametres.profil,
    capital: r.portefeuille.capital,
    valeur_finale: r.portefeuille.valeur_finale,
    duree: r.parametres.duree,
    monte_carlo: false,
    prix_reels: true,
    calibration: false,
    nb_actifs: r.parametres.nb_actifs,
    inflation: 0,
    taux_directeurs: 0,
    explication: [r.description, phrasePeriode(r)].filter(Boolean).join(" "),
    evenement_reference: null,
    performances: r.actifs.map((a) => ({ nom: a.nom, performance: a.performance_pct })),
    // Le PDF attend des fractions (0,25 = 25 %), comme construire_allocations_finales.
    allocations: r.allocations.map((l) => ({ nom: l.nom, poids: l.poids, investi: l.investi, final: l.final, rendement: l.performance_pct / 100 })),
    vol_ann: m.vol_ann,
    sharpe: m.sharpe,
    max_dd: m.max_dd,
    var_95: m.var_95,
    avec_analyse_ia: true,
  };
}
