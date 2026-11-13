// Colonnes du CSV d'export, identiques a l'ancien export Python (core/export_csv.py) :
// valeur du portefeuille puis valeur en euros de chaque ligne ("poche"), jour par jour.

import type { LigneAllocation, Portefeuille, SerieActif } from "@/lib/api";

export function slugColonne(nom: string): string {
  let s = nom.toLowerCase().replaceAll("&", " et ").replaceAll("/", " ");
  for (const c of "()[]{}'\",.$") s = s.replaceAll(c, "");
  return s.split(/\s+/).filter(Boolean).join("_");
}

export function colonnesPoches(portefeuille: Portefeuille, allocations: LigneAllocation[], actifs: SerieActif[]) {
  const prix = new Map(actifs.map((a) => [a.cle, a.prix]));
  const poches = allocations.flatMap((l) => {
    const serie = prix.get(l.cle);
    if (!serie || !serie[0]) return [];
    const depart = serie[0];
    return [{ nom: `${slugColonne(l.nom)}_eur`, valeurs: serie.map((v) => (v == null ? null : (v / depart) * l.investi)) }];
  });
  return [{ nom: "valeur_portefeuille_eur", valeurs: portefeuille.valeurs }, ...poches];
}
