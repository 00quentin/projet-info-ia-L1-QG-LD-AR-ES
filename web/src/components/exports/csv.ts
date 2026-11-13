// Generation du CSV cote navigateur, au format de l'ancien export Python
// (core/export_csv.py) : separateur ";", virgule decimale, 2 decimales,
// UTF-8 avec BOM pour qu'Excel lise correctement les accents.

import type { PropsExport } from "./BoutonsExport";

type DonneesCsv = PropsExport["csv"];

const SEPARATEUR = ";";
const FIN_DE_LIGNE = "\r\n";
const BOM = "﻿";

function cellule(texte: string): string {
  // Une cellule texte commencant par = + - @ serait lue comme une formule par Excel.
  const sur = /^[=+\-@\t\r]/.test(texte) ? `'${texte}` : texte;
  return /[;"\r\n]/.test(sur) ? `"${sur.replace(/"/g, '""')}"` : sur;
}

function valeur(v: number | null | undefined): string {
  if (v == null || !Number.isFinite(v)) return "";
  return v.toFixed(2).replace(".", ",");
}

export function construireCsv({ etiquettes, colonnes, titreColonneEtiquette = "date" }: DonneesCsv): string {
  const lignes = [[titreColonneEtiquette, ...colonnes.map((c) => c.nom)].map(cellule).join(SEPARATEUR)];
  etiquettes.forEach((etiquette, i) => {
    lignes.push([cellule(etiquette), ...colonnes.map((c) => valeur(c.valeurs[i]))].join(SEPARATEUR));
  });
  return lignes.join(FIN_DE_LIGNE) + FIN_DE_LIGNE;
}

export function blobCsv(donnees: DonneesCsv): Blob {
  return new Blob([BOM + construireCsv(donnees)], { type: "text/csv;charset=utf-8" });
}

/**
 * Nom de colonne a la maniere de l'ancien export : "S&P 500" -> "s_et_p_500_eur".
 * A utiliser par les pages qui veulent des en-tetes identiques a l'ancienne app.
 */
export function slugColonneCsv(nom: string, suffixe = "_eur"): string {
  let s = nom.toLowerCase().replace(/&/g, " et ").replace(/\//g, " ");
  s = s.replace(/[()[\]{}'",.$]/g, "");
  return s.split(/\s+/).filter(Boolean).join("_").replace(/^_+|_+$/g, "") + suffixe;
}

const deuxChiffres = (n: number) => String(n).padStart(2, "0");

/** "20261111_2252" : meme horodatage que l'ancienne app (%Y%m%d_%H%M). */
export function horodatage(d = new Date()): string {
  return `${d.getFullYear()}${deuxChiffres(d.getMonth() + 1)}${deuxChiffres(d.getDate())}_${deuxChiffres(d.getHours())}${deuxChiffres(d.getMinutes())}`;
}

/** "2026-11-11" en heure locale. */
export function dateDuJour(d = new Date()): string {
  return `${d.getFullYear()}-${deuxChiffres(d.getMonth() + 1)}-${deuxChiffres(d.getDate())}`;
}

export function nomFichierCsv(base: string, d = new Date()): string {
  const propre = base.replace(/[\\/:*?"<>|\s]+/g, "_").replace(/^_+|_+$/g, "") || "quant_terminal_donnees";
  return `${propre}_${horodatage(d)}.csv`;
}

/** Declenche le telechargement d'un fichier genere dans le navigateur. */
export function telechargerFichier(blob: Blob, nom: string): void {
  const url = URL.createObjectURL(blob);
  const lien = document.createElement("a");
  lien.href = url;
  lien.download = nom;
  lien.rel = "noopener";
  lien.style.display = "none";
  document.body.appendChild(lien);
  lien.click();
  lien.remove();
  // Revoquer tout de suite peut annuler le telechargement dans certains navigateurs.
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
