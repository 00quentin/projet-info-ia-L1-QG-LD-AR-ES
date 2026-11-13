"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ErreurApi, lancerBacktest, lireCatalogue, type Catalogue, type ReponseBacktest } from "@/lib/api";
import { ajouterEntree } from "@/lib/historique";
import { contexteBacktest, definirContexteChat } from "@/lib/contexteChat";
import { euros, pourcentSigne } from "@/lib/format";
import { Carte } from "@/components/ui/Carte";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import { FormulaireBacktest, periodeDemandee, reglagesInitiaux, type ReglagesBacktest } from "./FormulaireBacktest";
import { ResultatsBacktest } from "./ResultatsBacktest";
import { Chargement, EtatVide, Erreur } from "./EtatsBacktest";
import { libelleBacktest, scenarioBacktest } from "./outils";

export function Backtest() {
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [erreurCatalogue, setErreurCatalogue] = useState<string | null>(null);
  const [essai, setEssai] = useState(0);
  const [reglages, setReglages] = useState<ReglagesBacktest | null>(null);
  const [resultat, setResultat] = useState<{ id: number; reponse: ReponseBacktest } | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [libelleEnCours, setLibelleEnCours] = useState("");
  const zoneResultats = useRef<HTMLDivElement>(null);
  const compteur = useRef(0);

  useEffect(() => {
    let actif = true;
    lireCatalogue()
      .then((c) => {
        if (!actif) return;
        setErreurCatalogue(null);
        setCatalogue(c);
        setReglages((r) => r ?? reglagesInitiaux(c));
      })
      .catch((e: unknown) => actif && setErreurCatalogue(e instanceof ErreurApi ? e.message : "Chargement impossible."));
    return () => {
      actif = false;
    };
  }, [essai]);

  async function lancer() {
    if (!reglages || !catalogue) return;
    const periode = periodeDemandee(reglages, catalogue);
    setLibelleEnCours(libelleBacktest({ evenement: periode.evenement, date_debut: periode.date_debut ?? "", date_fin: periode.date_fin ?? "" }));
    setEnCours(true);
    setErreur(null);
    // Sur mobile le formulaire est au-dessus ; sur ordinateur on peut etre descendu dans le resultat precedent.
    // Image suivante : la zone a alors pris sa hauteur minimale, sinon le navigateur bride le defilement.
    requestAnimationFrame(() => {
      const zone = zoneResultats.current;
      if (zone && (window.matchMedia("(max-width: 1023px)").matches || zone.getBoundingClientRect().top < parseFloat(getComputedStyle(zone).scrollMarginTop))) {
        zone.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
      }
    });
    const p = reglages.portefeuille;
    try {
      const reponse = await lancerBacktest({
        actifs: p.actifs,
        profil: p.profil,
        allocations: p.allocations,
        capital: p.capital,
        tickers_perso: [],
        convertir_eur: reglages.convertirEur,
        ...periode,
      });
      compteur.current += 1;
      setResultat({ id: compteur.current, reponse });
      definirContexteChat(contexteBacktest(reponse, libelleBacktest(reponse)));
      ajouterEntree({
        type: "Backtest",
        scenario: scenarioBacktest(reponse),
        profil: reponse.parametres.profil,
        capital: reponse.portefeuille.capital,
        valeur_finale: reponse.portefeuille.valeur_finale,
        performance_pct: reponse.portefeuille.performance_pct,
        monte_carlo: false,
        nb_actifs: reponse.parametres.nb_actifs,
      });
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Une erreur est survenue.");
    } finally {
      setEnCours(false);
    }
  }

  if (erreurCatalogue) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <Erreur
          titre="Le backtest n'a pas pu se charger"
          message={`${erreurCatalogue} Le serveur se réveille peut-être : patientez quelques secondes.`}
          onReessayer={() => setEssai((n) => n + 1)}
        />
      </div>
    );
  }

  const etat = enCours ? "chargement" : erreur ? "erreur" : resultat ? `resultat-${resultat.id}` : "vide";

  return (
    <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[23.5rem_minmax(0,1fr)] lg:items-start">
      <aside className="lg:sticky lg:top-(--haut-colle) lg:max-h-[calc(100dvh-var(--haut-colle)-1.5rem)] lg:overflow-y-auto lg:rounded-2xl">
        <Carte className="p-5">
          {catalogue && reglages ? (
            <FormulaireBacktest catalogue={catalogue} reglages={reglages} onChange={setReglages} onLancer={lancer} enCours={enCours} />
          ) : (
            <div className="flex flex-col gap-3" aria-label="Chargement du formulaire">
              <div className="chargement h-12 rounded-xl" />
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="chargement h-20 rounded-xl" />
              ))}
              <div className="chargement h-40 rounded-xl" />
            </div>
          )}
        </Carte>
      </aside>

      <div ref={zoneResultats} className={`min-w-0 scroll-mt-4 lg:scroll-mt-(--haut-colle) ${enCours ? "max-lg:min-h-dvh" : ""}`} aria-busy={enCours}>
        <p className="sr-only" aria-live="polite">
          {resultat && !enCours && !erreur
            ? `Backtest terminé : ${euros(resultat.reponse.portefeuille.valeur_finale)}, soit ${pourcentSigne(resultat.reponse.portefeuille.performance_pct)}.`
            : ""}
        </p>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={etat}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } }}
            exit={{ opacity: 0, y: -6, transition: { duration: DUREE.rapide, ease: EASE_SORTIE } }}
          >
            {enCours ? (
              <Chargement libelle={libelleEnCours} convertirEur={reglages?.convertirEur ?? true} />
            ) : erreur ? (
              <Erreur message={erreur} onReessayer={lancer} />
            ) : resultat && catalogue ? (
              <ResultatsBacktest reponse={resultat.reponse} catalogue={catalogue} />
            ) : (
              <EtatVide />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
