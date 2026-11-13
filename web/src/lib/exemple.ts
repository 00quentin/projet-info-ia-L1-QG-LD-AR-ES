// Demo en un clic : une vraie simulation calculee a l'avance par l'API, servie comme fichier statique
// (public/exemple/simulation.json). Elle s'affiche tout de suite, meme quand le serveur dort.
// Pour la regenerer : POST /api/simulations avec `reglages` (format de l'API), puis remplacer `reponse`.

import type { ReponseSimulation } from "@/lib/api";
import type { ReglagesPartages } from "@/lib/partage";

export type Exemple = {
  /** Reglages qui ont produit l'exemple : ils remplissent le formulaire pour « Relancer en direct ». */
  reglages: ReglagesPartages;
  reponse: ReponseSimulation;
};

const CHEMIN_EXEMPLE = "/exemple/simulation.json";

let chargement: Promise<Exemple> | null = null;

/** Un seul telechargement par page ; on peut l'amorcer au survol du bouton. */
export function chargerExemple(): Promise<Exemple> {
  chargement ??= fetch(CHEMIN_EXEMPLE)
    .then((r) => {
      if (!r.ok) throw new Error("Exemple indisponible.");
      return r.json() as Promise<Exemple>;
    })
    .catch((e) => {
      chargement = null; // on pourra retenter
      throw e;
    });
  return chargement;
}
