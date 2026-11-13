"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMemo, useRef, useState, useSyncExternalStore } from "react";
import { effacerHistorique, HISTORIQUE_TAILLE_MAX, supprimerEntree, useHistorique } from "@/lib/historique";
import { DUREE, EASE_SORTIE, PAS_CASCADE, RESSORT } from "@/components/motion/transitions";
import { BoutonEffacer } from "./BoutonEffacer";
import { ChargementHistorique, FiltreVide, HistoriqueVide } from "./EtatsHistorique";
import { LigneHistorique } from "./LigneHistorique";
import { ResumeHistorique } from "./ResumeHistorique";
import { estEntreeValide, filtrer, type Filtre } from "./outils";

// Faux au rendu serveur et pendant l'hydratation, vrai ensuite : tant que c'est faux,
// useHistorique renvoie une liste vide qui ne reflete pas encore le navigateur.
const abonnementVide = () => () => {};
function useHydrate(): boolean {
  return useSyncExternalStore(
    abonnementVide,
    () => true,
    () => false,
  );
}

const FILTRES: { valeur: Filtre; libelle: string }[] = [
  { valeur: "tout", libelle: "Tout" },
  { valeur: "Simulation", libelle: "Simulations" },
  { valeur: "Backtest", libelle: "Backtests" },
];

const animationReduite = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function PageHistorique() {
  const brut = useHistorique();
  const hydrate = useHydrate();
  const entrees = useMemo(() => brut.filter(estEntreeValide), [brut]);
  const [filtre, setFiltre] = useState<Filtre>("tout");
  const [ouverts, setOuverts] = useState<ReadonlySet<string>>(() => new Set());
  const [annonce, setAnnonce] = useState("");
  const titre = useRef<HTMLHeadingElement>(null);
  const visibles = useMemo(() => filtrer(entrees, filtre), [entrees, filtre]);

  function basculer(id: string) {
    setOuverts((o) => {
      const suivant = new Set(o);
      if (suivant.has(id)) suivant.delete(id);
      else suivant.add(id);
      return suivant;
    });
  }

  function voir(id: string) {
    setOuverts((o) => new Set(o).add(id));
    requestAnimationFrame(() => {
      document.getElementById(`entree-${id}`)?.scrollIntoView({ behavior: animationReduite() ? "auto" : "smooth", block: "center" });
      document.getElementById(`bouton-${id}`)?.focus({ preventScroll: true });
    });
  }

  function supprimer(id: string) {
    // Le focus passe a l'entree voisine pour que le clavier ne se retrouve pas en haut de page.
    const i = visibles.findIndex((e) => e.id === id);
    const voisin = visibles[i + 1] ?? visibles[i - 1];
    supprimerEntree(id);
    setAnnonce("Entrée supprimée de l'historique.");
    requestAnimationFrame(() => {
      const cible = voisin ? document.getElementById(`bouton-${voisin.id}`) : titre.current;
      cible?.focus({ preventScroll: true });
    });
  }

  function toutEffacer() {
    effacerHistorique();
    setOuverts(new Set());
    setAnnonce("Historique effacé.");
    requestAnimationFrame(() => titre.current?.focus({ preventScroll: true }));
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 ref={titre} tabIndex={-1} className="text-2xl font-semibold tracking-tight outline-none sm:text-3xl">
            Historique
          </h1>
          <p className="mt-1.5 max-w-xl text-titre leading-relaxed text-ink-2">
            Vos {HISTORIQUE_TAILLE_MAX} dernières simulations et backtests. Ils restent dans ce navigateur : rien n&apos;est envoyé sur un serveur.
          </p>
        </div>
        <AnimatePresence>
          {hydrate && entrees.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: DUREE.rapide }}>
              <BoutonEffacer nombre={entrees.length} onConfirmer={toutEffacer} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-7">
        {!hydrate ? (
          <ChargementHistorique />
        ) : (
          <AnimatePresence mode="wait">
            {entrees.length === 0 ? (
              <motion.div key="vide" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}>
                <HistoriqueVide tailleMax={HISTORIQUE_TAILLE_MAX} />
              </motion.div>
            ) : (
              <motion.div key="liste" exit={{ opacity: 0, y: -8, transition: { duration: DUREE.rapide } }} className="flex flex-col gap-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div role="group" aria-label="Filtrer par type" className="inline-flex rounded-controle border border-line bg-surface p-1">
                    {FILTRES.map((f) => {
                      const actif = filtre === f.valeur;
                      return (
                        <button
                          key={f.valeur}
                          type="button"
                          aria-pressed={actif}
                          onClick={() => setFiltre(f.valeur)}
                          className={`relative rounded-controle px-3 py-1.5 text-sm font-medium transition-colors ${actif ? "text-ink" : "text-muted hover:text-ink"}`}
                        >
                          {actif && <motion.span layoutId="filtre-historique" className="absolute inset-0 rounded-controle bg-surface-2" transition={RESSORT} />}
                          <span className="relative">
                            {f.libelle} <span className="text-xs text-muted tabular-nums">{filtrer(entrees, f.valeur).length}</span>
                          </span>
                        </button>
                      );
                    })}
                  </div>
                  <p className="text-xs text-muted tabular-nums">
                    {entrees.length} / {HISTORIQUE_TAILLE_MAX} places utilisées
                  </p>
                </div>

                {visibles.length > 0 && <ResumeHistorique entrees={visibles} total={entrees.length} filtre={filtre} onVoir={voir} />}

                <h2 className="sr-only">Liste des simulations</h2>
                {visibles.length === 0 && filtre !== "tout" ? (
                  <FiltreVide filtre={filtre} />
                ) : (
                  <ul className="relative flex flex-col gap-2.5">
                    <AnimatePresence mode="popLayout">
                      {visibles.map((e, i) => (
                        <motion.li
                          key={e.id}
                          id={`entree-${e.id}`}
                          layout="position"
                          initial={{ opacity: 0, y: 12 }}
                          animate={{ opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE, delay: Math.min(i, 10) * PAS_CASCADE } }}
                          exit={{ opacity: 0, x: -24, transition: { duration: 0.22, ease: EASE_SORTIE } }}
                          transition={RESSORT}
                          className="rounded-carte border border-line bg-surface shadow-card"
                        >
                          <LigneHistorique entree={e} ouvert={ouverts.has(e.id)} onBasculer={() => basculer(e.id)} onSupprimer={() => supprimer(e.id)} annoncer={setAnnonce} />
                        </motion.li>
                      ))}
                    </AnimatePresence>
                  </ul>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>

      <p role="status" aria-live="polite" className="sr-only">
        {annonce}
      </p>
    </div>
  );
}
