// Fonctions pures de la page Historique (aucun rendu).

import type { EntreeHistorique } from "@/lib/historique";

export type Filtre = "tout" | "Simulation" | "Backtest";

/** Le stockage du navigateur peut contenir n'importe quoi : on ne garde que les entrees lisibles. */
export function estEntreeValide(e: unknown): e is EntreeHistorique {
  if (!e || typeof e !== "object") return false;
  const x = e as Record<string, unknown>;
  const nombre = (v: unknown) => typeof v === "number" && Number.isFinite(v);
  return (
    typeof x.id === "string" &&
    typeof x.date === "string" &&
    !Number.isNaN(Date.parse(x.date)) &&
    (x.type === "Simulation" || x.type === "Backtest") &&
    typeof x.scenario === "string" &&
    typeof x.profil === "string" &&
    nombre(x.capital) &&
    nombre(x.valeur_finale) &&
    nombre(x.performance_pct) &&
    nombre(x.nb_actifs)
  );
}

export function titreEntree(e: EntreeHistorique): string {
  return e.nom?.trim() || e.scenario;
}

/** "Équilibré (Normal)" -> "Équilibré" */
export function profilCourt(profil: string): string {
  return profil.split(" (")[0];
}

const formatDate = new Intl.DateTimeFormat("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric" });
const formatHeure = new Intl.DateTimeFormat("fr-FR", { hour: "2-digit", minute: "2-digit" });

const memeJour = (a: Date, b: Date) => a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();

/** "Aujourd'hui à 22:52", "Hier à 09:10", sinon "11/11/2026 à 22:52". */
export function dateLisible(iso: string, maintenant = new Date()): string {
  const d = new Date(iso);
  const hier = new Date(maintenant);
  hier.setDate(hier.getDate() - 1);
  const jour = memeJour(d, maintenant) ? "Aujourd'hui" : memeJour(d, hier) ? "Hier" : formatDate.format(d);
  return `${jour} à ${formatHeure.format(d)}`;
}

/** "11/11/2026 22:52" (format de l'ancienne app), pour les infobulles et lecteurs d'ecran. */
export function dateComplete(iso: string): string {
  const d = new Date(iso);
  return `${formatDate.format(d)} ${formatHeure.format(d)}`;
}

/**
 * Chemin interne pour relancer une simulation, ou null.
 * Le lien vient du stockage du navigateur : on n'accepte qu'une adresse de ce site.
 */
export function cheminRelance(lien: string | undefined): string | null {
  if (!lien || typeof window === "undefined") return null;
  try {
    const url = new URL(lien, window.location.origin);
    if (url.origin !== window.location.origin) return null;
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return null;
  }
}

export function filtrer(entrees: EntreeHistorique[], filtre: Filtre): EntreeHistorique[] {
  return filtre === "tout" ? entrees : entrees.filter((e) => e.type === filtre);
}

/** Meilleure et pire performance (null si liste vide). */
export function extremes(entrees: EntreeHistorique[]): { meilleure: EntreeHistorique; pire: EntreeHistorique } | null {
  if (entrees.length === 0) return null;
  let meilleure = entrees[0];
  let pire = entrees[0];
  for (const e of entrees) {
    if (e.performance_pct > meilleure.performance_pct) meilleure = e;
    if (e.performance_pct < pire.performance_pct) pire = e;
  }
  return { meilleure, pire };
}
