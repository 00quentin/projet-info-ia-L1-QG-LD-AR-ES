"use client";

import { useEffect, useMemo, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Brain,
  ChartCandlestick,
  Globe,
  History,
  ListTree,
  Puzzle,
  Sigma,
  Target,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import { MODULES, listeSections, resoudreAncre, type IdModule } from "@/contenu/academie/modules";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { changerAncre, useAncre } from "./ancre";

const ICONES: Record<IdModule, LucideIcon> = {
  outils: ChartCandlestick,
  modeles: Sigma,
  macro: Globe,
  cas: History,
  strategies: Target,
  construction: Puzzle,
  biais: Brain,
  lexique: BookOpen,
  methodologie: Workflow,
};

// En dessous de cette ligne (px depuis le haut), une section est considérée comme "en cours de lecture".
const LIGNE_LECTURE = 160;

function Onglets({ actif, choisir }: { actif: IdModule; choisir: (id: IdModule) => void }) {
  const liste = useRef<HTMLDivElement>(null);

  // Garde l'onglet actif visible quand la barre défile horizontalement (mobile).
  useEffect(() => {
    const conteneur = liste.current;
    const bouton = conteneur?.querySelector<HTMLElement>(`[data-module="${actif}"]`);
    if (!conteneur || !bouton) return;
    const gauche = bouton.offsetLeft - conteneur.clientWidth / 2 + bouton.clientWidth / 2;
    conteneur.scrollTo({ left: gauche, behavior: "smooth" });
  }, [actif]);

  function clavier(e: KeyboardEvent<HTMLDivElement>) {
    const i = MODULES.findIndex((m) => m.id === actif);
    const cibles: Record<string, number> = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: MODULES.length - 1 };
    if (!(e.key in cibles)) return;
    e.preventDefault();
    const suivant = MODULES[(cibles[e.key] + MODULES.length) % MODULES.length].id;
    choisir(suivant);
    liste.current?.querySelector<HTMLElement>(`[data-module="${suivant}"]`)?.focus();
  }

  return (
    <div className="relative">
      <div
        ref={liste}
        role="tablist"
        aria-label="Modules de l’Académie"
        onKeyDown={clavier}
        className="flex gap-0.5 overflow-x-auto rounded-carte border border-line bg-surface-2 p-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {MODULES.map((m) => {
          const choisi = m.id === actif;
          return (
            <motion.button
              key={m.id}
              type="button"
              role="tab"
              id={`onglet-${m.id}`}
              data-module={m.id}
              aria-selected={choisi}
              aria-controls={choisi ? `panneau-${m.id}` : undefined}
              tabIndex={choisi ? 0 : -1}
              onClick={() => choisir(m.id)}
              whileTap={{ scale: 0.96 }}
              className={`relative flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-tuile px-2.5 py-2 text-sm font-medium transition-colors ${
                choisi ? "text-ink" : "text-muted hover:text-ink"
              }`}
            >
              {choisi && <motion.span layoutId="academie-onglet-actif" className="absolute inset-0 rounded-tuile bg-surface shadow-card" transition={RESSORT} />}
              <span
                className={`relative grid size-5 place-items-center rounded-md text-xs font-semibold tabular-nums transition-colors ${
                  choisi ? "bg-accent text-surface" : "bg-line text-ink-2"
                }`}
              >
                {m.numero}
              </span>
              <span className="relative">{m.court}</span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

/** Table des matières collante (grand écran) : la section en cours de lecture est surlignée. */
function Sommaire({ module, aller }: { module: IdModule; aller: (id: string) => void }) {
  const sections = useMemo(() => listeSections(module), [module]);
  const [visible, setVisible] = useState(sections[0]?.id);

  useEffect(() => {
    let image = 0;
    const mesurer = () => {
      image = 0;
      let courante = sections[0]?.id;
      for (const s of sections) {
        const el = document.getElementById(s.id);
        if (el && el.getBoundingClientRect().top <= LIGNE_LECTURE) courante = s.id;
      }
      // Tout en bas de la page, la dernière section est forcément celle qu'on lit.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) courante = sections[sections.length - 1]?.id;
      setVisible(courante);
    };
    const auDefilement = () => {
      if (!image) image = requestAnimationFrame(mesurer);
    };
    auDefilement();
    window.addEventListener("scroll", auDefilement, { passive: true });
    window.addEventListener("resize", auDefilement);
    return () => {
      cancelAnimationFrame(image);
      window.removeEventListener("scroll", auDefilement);
      window.removeEventListener("resize", auDefilement);
    };
  }, [sections]);

  return (
    <nav aria-label="Sommaire du module" className="sticky top-32">
      <p className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted">
        <ListTree className="size-3.5" aria-hidden />
        Dans ce module
      </p>
      <ul className="relative flex flex-col border-l border-line">
        {sections.map((s) => {
          const actif = s.id === visible;
          return (
            <li key={s.id} className="relative">
              {actif && <motion.span layoutId="academie-sommaire-actif" className="absolute -left-px inset-y-0 w-0.5 rounded-full bg-accent" transition={RESSORT} />}
              <a
                href={`#${s.id}`}
                aria-current={actif ? "location" : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  aller(s.id);
                }}
                className={`block py-1.5 pl-4 text-aide leading-snug transition-colors ${actif ? "font-medium text-ink" : "text-muted hover:text-ink"}`}
              >
                {s.numero && <span className="mr-1.5 tabular-nums text-accent">{s.numero}</span>}
                {s.titre}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

/** Sommaire repliable affiché à la place de la table latérale sur mobile. */
function SommaireMobile({ module, aller }: { module: IdModule; aller: (id: string) => void }) {
  return (
    <details className="group rounded-carte border border-line bg-surface px-4 py-3 shadow-card lg:hidden">
      <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-medium text-ink [&::-webkit-details-marker]:hidden">
        <ListTree className="size-4 text-muted" aria-hidden />
        Sommaire du module
        <span className="ml-auto text-muted transition-transform group-open:rotate-90" aria-hidden>
          ›
        </span>
      </summary>
      <ul className="mt-3 flex flex-col gap-1 border-t border-line pt-3">
        {listeSections(module).map((s) => (
          <li key={s.id}>
            <a
              href={`#${s.id}`}
              onClick={(e) => {
                e.preventDefault();
                aller(s.id);
              }}
              className="block py-1 text-sm text-ink-2 hover:text-ink"
            >
              {s.numero && <span className="mr-1.5 tabular-nums text-accent">{s.numero}</span>}
              {s.titre}
            </a>
          </li>
        ))}
      </ul>
    </details>
  );
}

function NavigationModules({ module, choisir }: { module: IdModule; choisir: (id: IdModule) => void }) {
  const i = MODULES.findIndex((m) => m.id === module);
  const precedent = MODULES[i - 1];
  const suivant = MODULES[i + 1];
  const carte = "flex flex-1 flex-col gap-1 rounded-carte border border-line bg-surface p-4 shadow-card transition-colors hover:border-accent/50";
  return (
    <nav aria-label="Modules précédent et suivant" className="mt-4 flex max-w-[46rem] flex-col gap-3 border-t border-line pt-8 sm:flex-row">
      {precedent ? (
        <motion.button type="button" onClick={() => choisir(precedent.id)} whileTap={{ scale: 0.98 }} transition={RESSORT} className={`${carte} text-left`}>
          <span className="flex items-center gap-1.5 text-xs text-muted">
            <ArrowLeft className="size-3.5" aria-hidden /> Module précédent
          </span>
          <span className="text-titre font-semibold text-ink">
            {precedent.numero}. {precedent.nom}
          </span>
        </motion.button>
      ) : (
        <span className="hidden flex-1 sm:block" />
      )}
      {suivant && (
        <motion.button type="button" onClick={() => choisir(suivant.id)} whileTap={{ scale: 0.98 }} transition={RESSORT} className={`${carte} items-end text-right`}>
          <span className="flex items-center gap-1.5 text-xs text-muted">
            Module suivant <ArrowRight className="size-3.5" aria-hidden />
          </span>
          <span className="text-titre font-semibold text-ink">
            {suivant.numero}. {suivant.nom}
          </span>
        </motion.button>
      )}
    </nav>
  );
}

function Panneau({ module, section, contenu, choisir }: { module: IdModule; section?: string; contenu: ReactNode; choisir: (id: IdModule) => void }) {
  const meta = MODULES.find((m) => m.id === module) ?? MODULES[0];
  const Icone = ICONES[module];

  // Lien direct vers une section (/academie#modeles-monte-carlo) ou clic dans le sommaire.
  useEffect(() => {
    if (section) document.getElementById(section)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [section]);

  const aller = (id: string) => {
    if (id === section) document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    else changerAncre(id);
  };

  return (
    <motion.div
      role="tabpanel"
      id={`panneau-${module}`}
      aria-labelledby={`onglet-${module}`}
      tabIndex={0}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6, transition: { duration: DUREE.rapide } }}
      transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
      className="grid grid-cols-1 gap-10 outline-none lg:grid-cols-[minmax(0,1fr)_15rem] lg:gap-12"
    >
      <article className="flex min-w-0 max-w-[46rem] flex-col gap-12">
        <header className="flex flex-col gap-4">
          <p className="flex items-center gap-2.5 text-sm font-medium text-accent-ink">
            <span className="grid size-8 place-items-center rounded-controle bg-accent-soft">
              <Icone className="size-4" aria-hidden />
            </span>
            Module {meta.numero} · {meta.nom}
          </p>
          <h2 className="text-3xl font-semibold leading-tight tracking-tight text-ink">{meta.titre}</h2>
          <SommaireMobile module={module} aller={aller} />
        </header>
        {contenu}
        <NavigationModules module={module} choisir={choisir} />
      </article>
      <aside className="hidden lg:block">
        <Sommaire module={module} aller={aller} />
      </aside>
    </motion.div>
  );
}

export function Academie({ contenus }: { contenus: Record<IdModule, ReactNode> }) {
  const { module, section } = resoudreAncre(useAncre());
  const haut = useRef<HTMLDivElement>(null);

  function choisir(id: IdModule, remonter = false) {
    changerAncre(id);
    if (remonter) haut.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <div className="mx-auto max-w-[1280px] px-4 pb-20 pt-8 sm:px-6 sm:pt-12">
      <div ref={haut} className="scroll-mt-4 lg:scroll-mt-32">
        <Onglets actif={module} choisir={(id) => choisir(id)} />
      </div>
      <div className="mt-10">
        <AnimatePresence mode="wait" initial={false}>
          <Panneau key={module} module={module} section={section} contenu={contenus[module]} choisir={(id) => choisir(id, true)} />
        </AnimatePresence>
      </div>
    </div>
  );
}
