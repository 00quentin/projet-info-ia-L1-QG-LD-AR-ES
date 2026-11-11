"use client";

import type { DemandeRapport } from "@/lib/api";

export type ColonneCsv = { nom: string; valeurs: (number | null)[] };

export type PropsExport = {
  /** Donnees du CSV : une ligne par etiquette (date ou "Jour N"), une colonne par serie. */
  csv: { nomFichier: string; etiquettes: string[]; colonnes: ColonneCsv[]; titreColonneEtiquette?: string };
  /** Contenu du rapport PDF ; absent = pas de bouton PDF. */
  rapport?: DemandeRapport;
  /** Adresse a copier pour partager ; absent = pas de bouton de partage. */
  lienPartage?: string;
};

/**
 * Exports d'un resultat : CSV, rapport PDF, lien de partage.
 * Provisoire : implementation a venir.
 */
export function BoutonsExport(props: PropsExport) {
  void props;
  return null;
}
