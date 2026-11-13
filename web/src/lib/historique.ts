// Historique des simulations, garde dans le navigateur du visiteur (localStorage).
// Prive par construction : rien n'est stocke sur le serveur.

import { useSyncExternalStore } from "react";

export type EntreeHistorique = {
  id: string;
  /** Date ISO de la simulation. */
  date: string;
  type: "Simulation" | "Backtest";
  /** Texte du scenario, ou "Backtest : <evenement>". */
  scenario: string;
  /** Nom personnalise donne par le visiteur. */
  nom?: string;
  profil: string;
  capital: number;
  valeur_finale: number;
  performance_pct: number;
  monte_carlo: boolean;
  nb_actifs: number;
  /** "A", "B" ou "C" quand la simulation faisait partie d'une comparaison. */
  label_comparaison?: string | null;
  /** Lien pour relancer la meme simulation (voir lib/partage.ts). */
  lien?: string;
};

const CLE = "qt-historique-v1";
export const HISTORIQUE_TAILLE_MAX = 20;
const EVENEMENT = "qt-historique";
const VIDE: EntreeHistorique[] = [];

let cache: EntreeHistorique[] | null = null;

function lire(): EntreeHistorique[] {
  if (cache) return cache;
  try {
    const brut = localStorage.getItem(CLE);
    const donnees = brut ? JSON.parse(brut) : [];
    cache = Array.isArray(donnees) ? donnees : [];
  } catch {
    cache = [];
  }
  return cache;
}

function ecrire(entrees: EntreeHistorique[]) {
  cache = entrees;
  try {
    localStorage.setItem(CLE, JSON.stringify(entrees));
  } catch {
    /* stockage plein ou bloque (navigation privee) : l'historique vit le temps de la page */
  }
  window.dispatchEvent(new Event(EVENEMENT));
}

export function lireHistorique(): EntreeHistorique[] {
  return typeof window === "undefined" ? VIDE : lire();
}

export function ajouterEntree(entree: Omit<EntreeHistorique, "id" | "date">): void {
  const complete: EntreeHistorique = {
    ...entree,
    id: crypto.randomUUID(),
    date: new Date().toISOString(),
  };
  ecrire([complete, ...lire()].slice(0, HISTORIQUE_TAILLE_MAX));
}

export function renommerEntree(id: string, nom: string): void {
  ecrire(lire().map((e) => (e.id === id ? { ...e, nom: nom.trim() || undefined } : e)));
}

export function supprimerEntree(id: string): void {
  ecrire(lire().filter((e) => e.id !== id));
}

export function effacerHistorique(): void {
  ecrire([]);
}

function abonner(rappel: () => void) {
  const surStockage = (e: StorageEvent) => {
    if (e.key === CLE) {
      cache = null; // modifie depuis un autre onglet
      rappel();
    }
  };
  window.addEventListener(EVENEMENT, rappel);
  window.addEventListener("storage", surStockage);
  return () => {
    window.removeEventListener(EVENEMENT, rappel);
    window.removeEventListener("storage", surStockage);
  };
}

/** Historique reactif : le composant se met a jour a chaque ajout/suppression. */
export function useHistorique(): EntreeHistorique[] {
  return useSyncExternalStore(abonner, lireHistorique, () => VIDE);
}
