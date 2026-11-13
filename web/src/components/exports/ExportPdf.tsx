"use client";

import { motion } from "motion/react";
import { useEffect, useId, useRef, useState } from "react";
import { CircleAlert, Download, FileText, LoaderCircle, RotateCw } from "lucide-react";
import { ErreurApi, telechargerRapportPdf, type DemandeRapport } from "@/lib/api";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import { Annonce, BoutonExport, CocheAnimee, Depliant, LigneExport, useFlash } from "./commun";
import { dateDuJour, telechargerFichier } from "./csv";

// Etapes affichees pendant que l'IA redige (le serveur ne renvoie pas d'avancement :
// elles suivent le deroulement habituel, 15 a 30 s au total).
const ETAPES = [
  { texte: "Envoi des résultats au serveur", debut: 0 },
  { texte: "L'IA relit le scénario et les chiffres", debut: 2 },
  { texte: "Rédaction de l'analyse approfondie", debut: 7 },
  { texte: "Recommandations et points de vigilance", debut: 16 },
  { texte: "Mise en page du rapport PDF", debut: 23 },
];
const DUREE_ESTIMEE = 28;
const PAS_HORLOGE = 0.5;

type Etat =
  | { phase: "repos" }
  | { phase: "en-cours"; cle: string }
  | { phase: "pret"; cle: string; blob: Blob; nom: string }
  | { phase: "erreur"; cle: string; message: string };

const REPOS: Etat = { phase: "repos" };

function taille(octets: number): string {
  return octets >= 1_000_000 ? `${(octets / 1_000_000).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} Mo` : `${Math.max(1, Math.round(octets / 1000))} Ko`;
}

function Progression() {
  const [ecoule, setEcoule] = useState(0);
  useEffect(() => {
    const horloge = setInterval(() => setEcoule((t) => t + PAS_HORLOGE), PAS_HORLOGE * 1000);
    return () => clearInterval(horloge);
  }, []);
  const etape = ETAPES.findLastIndex((e) => ecoule >= e.debut);

  return (
    <div className="rounded-tuile border border-line bg-surface-2/60 p-4">
      <div className="flex items-center justify-between gap-3 text-xs text-muted">
        <span>Comptez 15 à 30 secondes : l&apos;IA rédige une vraie analyse.</span>
        <span className="shrink-0 tabular-nums" aria-hidden>
          {Math.floor(ecoule)} s
        </span>
      </div>
      <div role="progressbar" aria-label="Préparation du rapport PDF" aria-valuetext={ETAPES[etape].texte} className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-line">
        <motion.div
          className="h-full rounded-full bg-accent"
          initial={{ width: "3%" }}
          animate={{ width: "94%" }}
          transition={{ duration: DUREE_ESTIMEE, ease: [0.12, 0.6, 0.3, 1] }}
        />
      </div>
      <ol className="mt-4 flex flex-col gap-2.5">
        {ETAPES.map((e, i) => {
          const statut = i < etape ? "fait" : i === etape ? "actuel" : "a-venir";
          return (
            <motion.li
              key={e.texte}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: statut === "a-venir" ? 0.55 : 1, x: 0 }}
              transition={{ duration: DUREE.normale, ease: EASE_SORTIE, delay: i * 0.05 }}
              className="flex items-center gap-2.5 text-sm"
            >
              <span className="grid size-5 shrink-0 place-items-center">
                {statut === "fait" ? (
                  <span className="grid size-5 place-items-center rounded-full bg-gain-soft text-gain">
                    <CocheAnimee className="size-3.5" />
                  </span>
                ) : statut === "actuel" ? (
                  <LoaderCircle className="size-4 animate-spin text-accent" aria-hidden />
                ) : (
                  <span className="size-2 rounded-full border border-line-strong" aria-hidden />
                )}
              </span>
              <span className={statut === "actuel" ? "font-medium text-ink" : statut === "fait" ? "text-ink-2" : "text-muted"}>{e.texte}</span>
              <span className="sr-only">{statut === "fait" ? "(terminé)" : statut === "actuel" ? "(en cours)" : "(à venir)"}</span>
            </motion.li>
          );
        })}
      </ol>
      <Annonce message={`${ETAPES[etape].texte}…`} />
    </div>
  );
}

/** Ligne "Rapport PDF" : generation par l'API (analyse IA), progression, telechargement, erreur. */
export function ExportPdf({ rapport }: { rapport: DemandeRapport }) {
  const idPanneau = useId();
  // Le rapport peut changer (nouvelle simulation) : un PDF pret ou une erreur ne valent que pour son contenu.
  const cle = JSON.stringify(rapport);
  const [etatBrut, setEtat] = useState<Etat>(REPOS);
  const etat = etatBrut.phase !== "repos" && etatBrut.cle !== cle ? REPOS : etatBrut;
  const cleCourante = useRef(cle);
  useEffect(() => {
    cleCourante.current = cle;
  }, [cle]);
  const [succesRecent, flashSucces] = useFlash(2600);

  async function generer() {
    const cleDemande = cle;
    setEtat({ phase: "en-cours", cle: cleDemande });
    try {
      const blob = await telechargerRapportPdf(rapport);
      const nom = `rapport-quant-terminal-${dateDuJour()}.pdf`;
      if (cleCourante.current !== cleDemande) return;
      telechargerFichier(blob, nom);
      setEtat({ phase: "pret", cle: cleDemande, blob, nom });
      flashSucces();
    } catch (e) {
      setEtat({ phase: "erreur", cle: cleDemande, message: e instanceof ErreurApi ? e.message : "Le rapport n'a pas pu être généré. Réessayez dans un instant." });
    }
  }

  function retelecharger() {
    if (etat.phase !== "pret") return;
    telechargerFichier(etat.blob, etat.nom);
    flashSucces();
  }

  const action =
    etat.phase === "en-cours" ? (
      <BoutonExport cle="en-cours" disabled aria-busy="true" aria-controls={idPanneau}>
        <LoaderCircle className="size-4 animate-spin text-accent" aria-hidden />
        Rédaction en cours…
      </BoutonExport>
    ) : etat.phase === "pret" ? (
      succesRecent ? (
        <BoutonExport cle="succes" ton="succes" onClick={retelecharger}>
          <CocheAnimee />
          Rapport téléchargé
        </BoutonExport>
      ) : (
        <BoutonExport cle="a-nouveau" onClick={retelecharger}>
          <Download className="size-4 text-accent" aria-hidden />
          Télécharger à nouveau
        </BoutonExport>
      )
    ) : etat.phase === "erreur" ? (
      <BoutonExport cle="erreur" onClick={generer}>
        <RotateCw className="size-4 text-accent" aria-hidden />
        Réessayer
      </BoutonExport>
    ) : (
      <BoutonExport cle="repos" onClick={generer}>
        <FileText className="size-4 text-accent" aria-hidden />
        Générer le rapport
      </BoutonExport>
    );

  return (
    <LigneExport
      icone={FileText}
      titre="Rapport PDF"
      description="Rapport complet rédigé par l'IA : analyse, métriques de risque et recommandations."
      meta={etat.phase === "pret" ? `${etat.nom} · ${taille(etat.blob.size)}` : "Généré à la demande, en 15 à 30 secondes."}
      action={action}
    >
      <Depliant visible={etat.phase === "en-cours" || etat.phase === "erreur"} id={idPanneau}>
        {etat.phase === "en-cours" ? (
          <Progression />
        ) : etat.phase === "erreur" ? (
          <div role="alert" className="flex gap-3 rounded-tuile border border-loss/30 bg-loss-soft px-4 py-3 text-sm">
            <CircleAlert className="mt-0.5 size-4 shrink-0 text-loss" aria-hidden />
            <span className="text-ink">
              <strong className="font-semibold">Le rapport n&apos;a pas pu être généré.</strong> {etat.message}
            </span>
          </div>
        ) : null}
      </Depliant>
      <Annonce message={etat.phase === "pret" && succesRecent ? "Rapport PDF prêt : le téléchargement a commencé." : ""} />
    </LigneExport>
  );
}
