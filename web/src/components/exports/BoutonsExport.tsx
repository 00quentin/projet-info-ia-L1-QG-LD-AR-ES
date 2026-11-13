"use client";

import { Download, FileSpreadsheet } from "lucide-react";
import type { DemandeRapport } from "@/lib/api";
import { Carte, TitreCarte } from "@/components/ui/Carte";
import { Annonce, BoutonExport, CocheAnimee, LigneExport, useFlash } from "./commun";
import { blobCsv, nomFichierCsv, telechargerFichier } from "./csv";
import { ExportPdf } from "./ExportPdf";
import { ExportPartage } from "./ExportPartage";

export type ColonneCsv = { nom: string; valeurs: (number | null)[] };

export type PropsExport = {
  /** Donnees du CSV : une ligne par etiquette (date ou "Jour N"), une colonne par serie. */
  csv: { nomFichier: string; etiquettes: string[]; colonnes: ColonneCsv[]; titreColonneEtiquette?: string };
  /** Contenu du rapport PDF ; absent = pas de bouton PDF. */
  rapport?: DemandeRapport;
  /** Adresse a copier pour partager ; absent = pas de bouton de partage. */
  lienPartage?: string;
};

function ExportCsv({ csv }: { csv: PropsExport["csv"] }) {
  const [telecharge, flash] = useFlash(2200);
  const nbLignes = csv.etiquettes.length;
  const nbSeries = csv.colonnes.length;

  function telecharger() {
    telechargerFichier(blobCsv(csv), nomFichierCsv(csv.nomFichier));
    flash();
  }

  return (
    <LigneExport
      icone={FileSpreadsheet}
      titre="Données (CSV)"
      description="Les valeurs jour par jour, en euros. S'ouvre directement dans Excel ou avec Python."
      meta={`${nbLignes.toLocaleString("fr-FR")} ligne${nbLignes > 1 ? "s" : ""} · ${nbSeries} série${nbSeries > 1 ? "s" : ""} · séparateur « ; », virgule décimale`}
      action={
        telecharge ? (
          <BoutonExport cle="succes" ton="succes" onClick={telecharger}>
            <CocheAnimee />
            Fichier téléchargé
          </BoutonExport>
        ) : (
          <BoutonExport cle="repos" onClick={telecharger}>
            <Download className="size-4 text-accent" aria-hidden />
            Télécharger le CSV
          </BoutonExport>
        )
      }
    >
      <Annonce message={telecharge ? "Fichier CSV téléchargé." : ""} />
    </LigneExport>
  );
}

/** Exports d'un resultat : CSV (genere dans le navigateur), rapport PDF (API + IA), lien de partage. */
export function BoutonsExport({ csv, rapport, lienPartage }: PropsExport) {
  return (
    <Carte taille="normale" className="@container">
      <TitreCarte>Exporter et partager</TitreCarte>
      <p className="sr-only">Récupérez les chiffres bruts, un rapport complet ou un lien pour retrouver cette simulation.</p>
      <ul className="divide-y divide-line">
        <ExportCsv csv={csv} />
        {rapport && <ExportPdf rapport={rapport} />}
        {lienPartage && <ExportPartage lien={lienPartage} />}
      </ul>
    </Carte>
  );
}
