"use client";

import { useEffect, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ErreurApi } from "@/lib/api";
import { lireValidationIA, type ValidationIA } from "@/lib/validation";
import { dateFr } from "@/lib/format";
import { Carte } from "@/components/ui/Carte";
import { Apparition } from "@/components/motion/Apparition";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import { Erreur } from "@/components/backtest/EtatsBacktest";
import { BiaisConnaissance } from "./BiaisConnaissance";
import { CarteCrise } from "./CarteCrise";
import { ChiffresCles } from "./ChiffresCles";
import { Methode } from "./Methode";
import { NuageEstimeReel } from "./NuageEstimeReel";
import { PlusGrosEcarts } from "./PlusGrosEcarts";

function Rubrique({ id, titre, chapeau, children }: { id: string; titre: string; chapeau?: ReactNode; children: ReactNode }) {
  return (
    <section aria-labelledby={id} className="mt-12">
      <Apparition auDefilement decalage={10}>
        <h2 id={id} className="text-2xl font-semibold tracking-tight text-ink">
          {titre}
        </h2>
        {chapeau && <p className="mt-2 max-w-[44rem] text-[15px] leading-relaxed text-ink-2">{chapeau}</p>}
      </Apparition>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function Squelette() {
  return (
    <div className="mt-10 flex flex-col gap-4" aria-label="Chargement des résultats">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="chargement h-32 rounded-2xl" />
        ))}
      </div>
      <div className="chargement h-96 rounded-2xl" />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="chargement h-80 rounded-2xl" />
        <div className="chargement h-80 rounded-2xl" />
      </div>
    </div>
  );
}

function Contenu({ v }: { v: ValidationIA }) {
  return (
    <>
      <Rubrique id="score" titre="Le score global">
        <ChiffresCles v={v} />
      </Rubrique>

      <Rubrique
        id="nuage"
        titre="Estimé contre réel, d’un coup d’œil"
        chapeau="Chaque point est un actif dans une crise. Plus il est proche de la diagonale, plus l’estimation est juste ; dans les zones teintées, l’IA a vu le bon sens de variation."
      >
        <Carte className="grid grid-cols-1 gap-6 p-4 sm:p-6 lg:grid-cols-[minmax(0,1fr)_17rem]">
          <div className="min-w-0">
            <NuageEstimeReel crises={v.crises} />
          </div>
          <aside className="border-t border-line pt-5 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
            <PlusGrosEcarts crises={v.crises} />
          </aside>
        </Carte>
      </Rubrique>

      <Rubrique id="biais" titre="Le biais de connaissance">
        <BiaisConnaissance v={v} />
      </Rubrique>

      <Rubrique
        id="crises"
        titre="Crise par crise"
        chapeau="Pour chaque crise : la description envoyée à l’IA, ses scores et, actif par actif, son estimation face au vrai mouvement en euros."
      >
        {/* Deux colonnes façon « mur » : les cartes n’ont pas toutes le même nombre d’actifs. */}
        <div className="gap-4 xl:columns-2">
          {v.crises.map((c, i) => (
            <Apparition key={c.nom} auDefilement delai={(i % 2) * 0.06} className="mb-4 min-w-0 break-inside-avoid">
              <CarteCrise crise={c} />
            </Apparition>
          ))}
        </div>
      </Rubrique>

      <Rubrique id="methode" titre="Méthode et limites">
        <Methode v={v} />
      </Rubrique>
    </>
  );
}

/** Page « L'IA à l'épreuve de l'histoire » : résultats précalculés, aucun appel IA. */
export function PageValidation() {
  const [donnees, setDonnees] = useState<ValidationIA | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);
  const [essai, setEssai] = useState(0);

  useEffect(() => {
    let actif = true;
    lireValidationIA()
      .then((v) => {
        if (!actif) return;
        setErreur(null);
        setDonnees(v);
      })
      .catch((e: unknown) => actif && setErreur(e instanceof ErreurApi ? e.message : "Chargement impossible."));
    return () => {
      actif = false;
    };
  }, [essai]);

  const etat = donnees ? "resultats" : erreur ? "erreur" : "chargement";

  return (
    <div className="mx-auto max-w-6xl px-4 pb-20 pt-10 sm:px-6 sm:pt-14">
      <Apparition>
        <p className="inline-flex rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent-ink">Crédibilité · test à l’aveugle partiel</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">L’IA à l’épreuve de l’histoire</h1>
        <p className="mt-5 max-w-[42rem] text-[17px] leading-[1.7] text-ink-2 sm:text-lg">
          Pourquoi croire les chocs estimés par l’IA ? Pour chaque grande crise passée, on lui a décrit l’événement <strong className="font-semibold text-ink">sans le nommer ni le dater</strong>, puis on a comparé ses estimations aux{" "}
          <strong className="font-semibold text-ink">vrais cours</strong> sur la même période.
        </p>
        {donnees && (
          <p className="mt-3 text-sm text-muted">
            Calculé le {dateFr(donnees.genere_le.slice(0, 10))} · modèle {donnees.protocole.modele} · {donnees.crises.length} crises · aucun appel à l’IA pendant votre visite
          </p>
        )}
      </Apparition>

      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={etat}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } }}
          exit={{ opacity: 0, y: -6, transition: { duration: DUREE.rapide, ease: EASE_SORTIE } }}
        >
          {donnees ? (
            <Contenu v={donnees} />
          ) : erreur ? (
            <div className="mx-auto mt-10 max-w-xl">
              <Erreur
                titre="Les résultats n’ont pas pu se charger"
                message={`${erreur} Le serveur se réveille peut-être : patientez quelques secondes.`}
                onReessayer={() => {
                  setErreur(null);
                  setEssai((n) => n + 1);
                }}
              />
            </div>
          ) : (
            <Squelette />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
