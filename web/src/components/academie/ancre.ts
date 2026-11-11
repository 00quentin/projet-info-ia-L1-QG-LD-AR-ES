"use client";

import { useSyncExternalStore } from "react";

// Le module affiché suit le hash de l'adresse (/academie#biais) : liens directs et partage.
const EVENEMENT = "qt-academie-ancre";

function abonner(rappel: () => void) {
  window.addEventListener("hashchange", rappel);
  window.addEventListener("popstate", rappel);
  window.addEventListener(EVENEMENT, rappel);
  return () => {
    window.removeEventListener("hashchange", rappel);
    window.removeEventListener("popstate", rappel);
    window.removeEventListener(EVENEMENT, rappel);
  };
}

const lire = () => decodeURIComponent(window.location.hash.slice(1));

export function useAncre() {
  return useSyncExternalStore(abonner, lire, () => "");
}

/** Change le hash sans ajouter d'entrée à l'historique (comportement d'onglets). */
export function changerAncre(ancre: string) {
  window.history.replaceState(null, "", `#${ancre}`);
  window.dispatchEvent(new Event(EVENEMENT));
}
