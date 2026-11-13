"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Lightbulb, RotateCw, TriangleAlert, X } from "lucide-react";
import { RESSORT } from "@/components/motion/transitions";

const EVENEMENT = "qt-guide";

/** Ouvre le guide d'utilisation depuis n'importe quel composant. */
export function ouvrirGuide() {
  window.dispatchEvent(new Event(EVENEMENT));
}

const ETAPES: { titre: string; texte: React.ReactNode }[] = [
  {
    titre: "Choisissez un scénario",
    texte: (
      <>
        Dans la colonne de gauche, cliquez sur une idée de scénario (« Plus d&apos;idées » en montre d&apos;autres) ou écrivez le vôtre. Plus il est précis (pays, secteur, ampleur), plus l&apos;IA est pertinente.
      </>
    ),
  },
  {
    titre: "Choisissez vos actifs",
    texte: (
      <>
        Cliquez sur « Modifier » dans le bloc Actifs et cochez ce que vous voulez analyser (actions, obligations, or, pétrole, cryptos…). Vous pouvez aussi <strong>ajouter n&apos;importe quel ticker Yahoo</strong> (TSLA, NVDA, MC.PA…).
      </>
    ),
  },
  {
    titre: "Définissez votre portefeuille",
    texte: (
      <>
        Saisissez votre capital et choisissez un profil : <em>Prudent</em> (obligations et or), <em>Équilibré</em> (mix classique), <em>Agressif</em> (actions et cryptos) ou <em>Personnalisé</em> (vous fixez chaque pourcentage). La petite barre colorée de chaque profil montre sa répartition. Les actifs « Investis » reçoivent une part du capital ; les actifs « Suivis » sont seulement analysés, pour comparer.
      </>
    ),
  },
  {
    titre: "Lancez et explorez",
    texte: (
      <>
        Cliquez sur « Lancer la simulation » (ou sur « Essayer avec un exemple » pour voir tout de suite un résultat déjà calculé) : analyse de l&apos;IA, évolution du portefeuille, risque, détail par actif, exports. Les pages en haut donnent accès au backtest, à l&apos;historique et à l&apos;Académie.
      </>
    ),
  },
];

const ASTUCES: React.ReactNode[] = [
  "Comparez jusqu'à 3 scénarios côte à côte avec le lien « Comparer avec un autre scénario » sous le champ.",
  "Monte-Carlo (options avancées, activé par défaut) montre la fourchette des issues possibles et la probabilité de perte. Le bouton (i) à côté de chaque option l'explique.",
  "La page Backtest rejoue les vraies données passées (2008, COVID…) sur votre portefeuille.",
  "L'analyste IA (bulle en bas à droite) répond à vos questions de finance à tout moment.",
  <>
    Le bouton <RotateCw className="inline size-3.5 align-[-2px]" aria-label="recharger" /> du bandeau des cours recharge les derniers prix Yahoo Finance ; survolez la date pour voir le jour de clôture.
  </>,
  "Le bouton ? en haut à droite rouvre ce guide ; le bouton lune/soleil change de thème.",
];

export function Guide() {
  const [ouvert, setOuvert] = useState(false);
  const boutonFermer = useRef<HTMLButtonElement>(null);
  const focusPrecedent = useRef<Element | null>(null);

  useEffect(() => {
    const ouvrir = () => setOuvert(true);
    // Plus d'ouverture automatique : bouton « Visite guidee » de l'ecran vide ou bouton ? de l'en-tete.
    window.addEventListener(EVENEMENT, ouvrir);
    return () => window.removeEventListener(EVENEMENT, ouvrir);
  }, []);

  useEffect(() => {
    if (!ouvert) return;
    focusPrecedent.current = document.activeElement;
    boutonFermer.current?.focus();
    const surTouche = (e: KeyboardEvent) => e.key === "Escape" && fermer();
    window.addEventListener("keydown", surTouche);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", surTouche);
      document.body.style.overflow = "";
    };
  }, [ouvert]);

  function fermer() {
    setOuvert(false);
    (focusPrecedent.current as HTMLElement | null)?.focus?.();
  }

  return (
    <AnimatePresence>
      {ouvert && (
        <motion.div className="fixed inset-0 z-50 grid place-items-center p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={fermer} aria-hidden />
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="titre-guide"
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={RESSORT}
            className="relative max-h-[88dvh] w-full max-w-3xl overflow-y-auto rounded-carte border border-line bg-surface p-6 shadow-2xl sm:p-8"
          >
            <button ref={boutonFermer} type="button" onClick={fermer} aria-label="Fermer le guide" className="absolute right-4 top-4 grid size-8 place-items-center rounded-controle text-muted transition hover:bg-surface-2 hover:text-ink">
              <X className="size-4" aria-hidden />
            </button>
            <p className="text-xs font-semibold uppercase tracking-wider text-accent-ink">Simulateur d&apos;investissement pédagogique · L1 MIASHS 2026</p>
            <h2 id="titre-guide" className="mt-2 text-2xl font-semibold tracking-tight">Bienvenue sur Quant Terminal</h2>
            <p className="mt-2 text-titre leading-relaxed text-ink-2">
              Vous décrivez un événement (krach, guerre, hausse des taux, révolution IA…) et le terminal estime son impact sur votre portefeuille, à partir des <strong className="font-semibold text-ink">vrais prix de marché</strong> (Yahoo Finance), convertis en euros. Comptez <strong className="font-semibold text-ink">environ 2 minutes</strong> pour votre première simulation.
            </p>
            <ol className="mt-6 grid gap-3 sm:grid-cols-2">
              {ETAPES.map((e, i) => (
                <motion.li
                  key={e.titre}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.12 + i * 0.07 }}
                  className="rounded-tuile border border-line bg-surface-2/50 p-4"
                >
                  <span className="grid size-7 place-items-center rounded-full bg-accent text-xs font-bold text-on-accent">{i + 1}</span>
                  <h3 className="mt-2.5 text-sm font-semibold">{e.titre}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-ink-2">{e.texte}</p>
                </motion.li>
              ))}
            </ol>
            <div className="mt-5 rounded-tuile border-l-4 border-accent bg-accent-soft/50 px-4 py-3">
              <p className="flex items-center gap-2 text-sm font-semibold">
                <Lightbulb className="size-4 text-accent-ink" aria-hidden />
                Astuces pour bien démarrer
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-relaxed text-ink-2">
                {ASTUCES.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
            <div className="mt-4 flex gap-3 rounded-tuile border-l-4 border-warn bg-warn-soft px-4 py-3 text-sm leading-relaxed text-ink-2">
              <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
              <p>
                <strong className="font-semibold text-ink">Important :</strong> outil pédagogique, pas un conseil en investissement. L&apos;IA estime des ordres de grandeur en s&apos;inspirant de crises historiques ; la réalité peut fortement diverger.
              </p>
            </div>
            <motion.button whileTap={{ scale: 0.98 }} type="button" onClick={fermer} className="mt-6 h-11 w-full rounded-controle bg-accent text-sm font-semibold text-on-accent transition hover:brightness-110 sm:w-auto sm:px-6">
              J&apos;ai compris, c&apos;est parti
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
