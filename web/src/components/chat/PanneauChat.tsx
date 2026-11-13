"use client";

import { useEffect, useEffectEvent, useId, useRef, useState, useSyncExternalStore, type KeyboardEvent } from "react";
import { AnimatePresence, motion, useReducedMotion, type Variants } from "motion/react";
import { ArrowUpRight, Bot, ChartLine, Sparkles, Trash2, X } from "lucide-react";
import type { MessageConversation } from "./conversation";
import { BlocErreur, BulleMessage, IndicateurEcriture } from "./Message";
import { Saisie } from "./Saisie";
import { DUREE, EASE_SORTIE, PAS_CASCADE } from "@/components/motion/transitions";

/** Questions d'exemple (reprises de l'ancienne bulle Streamlit). */
const QUESTIONS_EXEMPLES = [
  "Pourquoi l'Or monte-t-il en période de crise ?",
  "Qu'est-ce que le VIX et à quoi sert-il ?",
  "Comment interpréter le ratio de Sharpe ?",
  "Quel impact d'une hausse des taux sur les obligations ?",
  "Pourquoi le pétrole et le dollar sont-ils liés ?",
  "C'est quoi la corrélation actions / obligations ?",
];

/** Proposee en tete quand un resultat est transmis a l'analyste. */
const QUESTION_CONTEXTE = "Explique-moi le résultat que j'ai sous les yeux";

const REQUETE_MOBILE = "(max-width: 639.98px)";
const DELAI_CONFIRMATION_MS = 4000;

function useEstMobile() {
  return useSyncExternalStore(
    (rappel) => {
      const requete = matchMedia(REQUETE_MOBILE);
      requete.addEventListener("change", rappel);
      return () => requete.removeEventListener("change", rappel);
    },
    () => matchMedia(REQUETE_MOBILE).matches,
    () => false,
  );
}

// Ordinateur : la fenetre jaillit de la bulle. Mobile : la feuille monte du bas.
const FENETRE: Variants = {
  cache: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } },
  sortie: { opacity: 0, y: 8, transition: { duration: DUREE.rapide, ease: EASE_SORTIE } },
};
const FEUILLE: Variants = {
  cache: { y: "100%" },
  visible: { y: 0, transition: { duration: DUREE.normale + 0.05, ease: EASE_SORTIE } },
  sortie: { y: "100%", transition: { duration: DUREE.rapide + 0.03, ease: EASE_SORTIE } },
};

const LISTE_EXEMPLES: Variants = { cache: {}, visible: { transition: { staggerChildren: PAS_CASCADE * 0.7, delayChildren: 0.08 } } };
const EXEMPLE: Variants = {
  cache: { opacity: 0, y: 6 },
  visible: { opacity: 1, y: 0, transition: { duration: DUREE.normale, ease: EASE_SORTIE } },
};

type Props = {
  id: string;
  messages: MessageConversation[];
  enAttente: boolean;
  erreur: string | null;
  brouillon: string;
  onBrouillon: (v: string) => void;
  onPoser: (question: string) => void;
  onReessayer: () => void;
  onEffacer: () => void;
  onFermer: () => void;
  /** Titre du resultat transmis a l'analyste (null : aucun). */
  contexte: string | null;
  onRetirerContexte: () => void;
};

export function PanneauChat({ id, messages, enAttente, erreur, brouillon, onBrouillon, onPoser, onReessayer, onEffacer, onFermer, contexte, onRetirerContexte }: Props) {
  const questions = contexte ? [QUESTION_CONTEXTE, ...QUESTIONS_EXEMPLES] : QUESTIONS_EXEMPLES;
  const idTitre = useId();
  const mobile = useEstMobile();
  const reduit = useReducedMotion();
  const panneauRef = useRef<HTMLDivElement>(null);
  const zoneRef = useRef<HTMLDivElement>(null);
  const filRef = useRef<HTMLUListElement>(null);
  const champRef = useRef<HTMLTextAreaElement>(null);
  const premierDefilement = useRef(true);
  const [confirmer, setConfirmer] = useState(false);

  const fermerSurEchap = useEffectEvent((e: globalThis.KeyboardEvent) => {
    if (e.key !== "Escape" || e.defaultPrevented || e.isComposing) return;
    // Fenetre non modale sur ordinateur : Echap ne la ferme que si on y travaille.
    const actif = document.activeElement;
    if (actif === document.body || panneauRef.current?.contains(actif)) onFermer();
  });

  useEffect(() => {
    champRef.current?.focus({ preventScroll: true });
    const surTouche = (e: globalThis.KeyboardEvent) => fermerSurEchap(e);
    document.addEventListener("keydown", surTouche);
    return () => document.removeEventListener("keydown", surTouche);
  }, []);

  // Sur mobile la feuille couvre l'ecran : la page derriere ne doit pas defiler.
  useEffect(() => {
    if (!mobile) return;
    const avant = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = avant;
    };
  }, [mobile]);

  useEffect(() => {
    if (!confirmer) return;
    const minuteur = setTimeout(() => setConfirmer(false), DELAI_CONFIRMATION_MS);
    return () => clearTimeout(minuteur);
  }, [confirmer]);

  // Defile vers le bas a chaque nouveau message. Pour une longue reponse, on s'arrete
  // sur son debut : le lecteur la lit de haut en bas.
  const nbMessages = messages.length;
  const dernierRole = messages.at(-1)?.role;
  useEffect(() => {
    const zone = zoneRef.current;
    if (!zone) return;
    // Conversation vide (ou effacee) : on montre l'accueil depuis le debut.
    let cible = nbMessages === 0 ? 0 : zone.scrollHeight - zone.clientHeight;
    if (nbMessages > 0 && dernierRole === "assistant" && !enAttente && !premierDefilement.current) {
      const elements = filRef.current?.querySelectorAll<HTMLElement>("[data-message]");
      const dernier = elements?.[elements.length - 1];
      if (dernier) cible = Math.min(cible, dernier.offsetTop - 12);
    }
    // Glissement doux sur une courte distance ; saut direct sinon (un long glissement fait attendre).
    const loin = Math.abs(cible - zone.scrollTop) > zone.clientHeight * 1.5;
    zone.scrollTo({ top: cible, behavior: premierDefilement.current || reduit || loin ? "auto" : "smooth" });
    premierDefilement.current = false;
  }, [nbMessages, dernierRole, enAttente, erreur, reduit]);

  function poserExemple(question: string) {
    onPoser(question);
    champRef.current?.focus({ preventScroll: true });
  }

  function effacer() {
    if (!confirmer) {
      setConfirmer(true);
      return;
    }
    setConfirmer(false);
    onEffacer();
    champRef.current?.focus({ preventScroll: true });
  }

  // Sur mobile (feuille plein ecran, modale), Tab reste dans le panneau.
  function garderFocus(e: KeyboardEvent<HTMLDivElement>) {
    if (e.key !== "Tab" || !mobile) return;
    const focusables = e.currentTarget.querySelectorAll<HTMLElement>("button:not([disabled]), textarea, a[href]");
    if (!focusables.length) return;
    const premier = focusables[0];
    const dernier = focusables[focusables.length - 1];
    if (e.shiftKey && (document.activeElement === premier || document.activeElement === e.currentTarget)) {
      e.preventDefault();
      dernier.focus();
    } else if (!e.shiftKey && document.activeElement === dernier) {
      e.preventDefault();
      premier.focus();
    }
  }

  return (
    <motion.div
      ref={panneauRef}
      id={id}
      role="dialog"
      aria-modal={mobile || undefined}
      aria-labelledby={idTitre}
      tabIndex={-1}
      onKeyDown={garderFocus}
      variants={mobile ? FEUILLE : FENETRE}
      initial="cache"
      animate="visible"
      exit="sortie"
      style={{ transformOrigin: "bottom right" }}
      className="fixed inset-0 z-50 flex flex-col overflow-hidden bg-surface outline-none sm:inset-auto sm:bottom-6 sm:right-6 sm:h-[min(600px,calc(100dvh-7.5rem))] sm:w-[400px] sm:rounded-carte sm:border sm:border-line sm:shadow-[0_24px_60px_-16px_rgba(15,17,21,0.28)] dark:sm:shadow-[0_24px_60px_-16px_rgba(0,0,0,0.7)]"
    >
      <header className="flex shrink-0 items-center gap-3 border-b border-line py-3 pl-4 pr-2.5 pt-[max(0.75rem,env(safe-area-inset-top))] sm:pt-3">
        <span className="grid size-9 shrink-0 place-items-center rounded-tuile bg-accent text-on-accent">
          <Bot className="size-4.5" aria-hidden />
        </span>
        <div className="min-w-0 flex-1">
          <h2 id={idTitre} className="truncate text-titre font-semibold leading-5 tracking-tight">
            Analyste IA
          </h2>
          <p className="truncate text-xs leading-4 text-muted">Assistant IA · marchés, macro, votre simulation</p>
        </div>
        <AnimatePresence initial={false}>
          {nbMessages > 0 && (
            <motion.button
              key="effacer"
              type="button"
              onClick={effacer}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              whileTap={{ scale: 0.97 }}
              aria-label={confirmer ? "Confirmer : effacer toute la conversation (cliquez encore)" : "Effacer la conversation"}
              className={`flex h-9 items-center gap-1.5 rounded-controle px-2.5 text-xs font-semibold transition-colors ${confirmer ? "bg-loss-soft text-loss" : "text-muted hover:bg-surface-2 hover:text-ink"}`}
            >
              <Trash2 className="size-4" aria-hidden />
              <AnimatePresence initial={false}>
                {confirmer && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: "auto" }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }}
                    className="overflow-hidden whitespace-nowrap"
                  >
                    Effacer ?
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          )}
        </AnimatePresence>
        <motion.button
          type="button"
          onClick={onFermer}
          whileTap={{ scale: 0.97 }}
          aria-label="Fermer l'analyste IA (Échap)"
          className="grid size-9 shrink-0 place-items-center rounded-controle text-muted transition-colors hover:bg-surface-2 hover:text-ink"
        >
          <X className="size-4.5" aria-hidden />
        </motion.button>
      </header>

      <div ref={zoneRef} className="relative min-h-0 flex-1 overflow-y-auto overscroll-contain">
        <section aria-label="Présentation de l'analyste" className="px-4 pb-3 pt-4">
          {/* Transparence (AI Act, art. 50) : on sait d'emblee qu'on parle a une IA. */}
          <p role="note" className="mb-3 flex gap-2 rounded-tuile border border-line bg-surface-2 px-3 py-2 text-xs leading-relaxed text-ink-2">
            <Bot className="mt-0.5 size-3.5 shrink-0 text-muted" aria-hidden />
            <span>
              Réponses générées par une IA (OpenAI), elles peuvent contenir des erreurs. Ce n&apos;est pas un conseil en investissement.
            </span>
          </p>
          <div className="flex items-start gap-3 rounded-tuile bg-accent-soft/60 p-3.5">
            <span className="grid size-9 shrink-0 place-items-center rounded-tuile bg-surface text-accent-ink shadow-card">
              <Sparkles className="size-4.5" aria-hidden />
            </span>
            <div className="min-w-0">
              <p className="text-sm font-semibold tracking-tight text-ink">Votre analyste financier</p>
              <p className="mt-0.5 text-aide leading-relaxed text-ink-2">
                Marchés, macro, crises historiques : je réponds en pro et j&apos;explique simplement.
              </p>
            </div>
          </div>
          <p className="mb-2 mt-4 text-xs font-semibold uppercase tracking-wider text-muted">Questions fréquentes</p>
          <motion.ul variants={LISTE_EXEMPLES} initial="cache" animate="visible" className="flex flex-col gap-1.5">
            {questions.map((q) => (
              <motion.li key={q} variants={EXEMPLE}>
                <motion.button
                  type="button"
                  onClick={() => poserExemple(q)}
                  disabled={enAttente}
                  whileTap={enAttente ? undefined : { scale: 0.98 }}
                  className="group flex w-full items-center justify-between gap-3 rounded-controle border border-line bg-surface px-3 py-1.5 text-left text-sm leading-5 text-ink-2 transition-colors hover:border-accent/50 hover:bg-accent-soft hover:text-accent-ink disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <span>{q}</span>
                  <ArrowUpRight className="size-4 shrink-0 text-muted transition-colors group-hover:text-accent-ink" aria-hidden />
                </motion.button>
              </motion.li>
            ))}
          </motion.ul>
        </section>

        <div role="log" aria-live="polite" aria-label="Conversation avec l'analyste">
          <ul ref={filRef} className="flex flex-col gap-3 px-4 pb-4 pt-1">
            <AnimatePresence initial={false}>
              {messages.map((m) => (
                <BulleMessage key={m.id} message={m} />
              ))}
            </AnimatePresence>
            {enAttente && <IndicateurEcriture />}
            {erreur && !enAttente && <BlocErreur message={erreur} onReessayer={onReessayer} />}
          </ul>
        </div>
      </div>

      <div className="shrink-0 border-t border-line bg-surface px-3 pb-[max(0.625rem,env(safe-area-inset-bottom))] pt-3">
        <AnimatePresence initial={false}>
          {contexte && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: DUREE.rapide }}
              className="overflow-hidden"
            >
              <div className="mb-2 flex items-center gap-2 rounded-controle bg-accent-soft px-2.5 py-1.5 text-xs text-accent-ink">
                <ChartLine className="size-3.5 shrink-0" aria-hidden />
                <span className="min-w-0 flex-1 truncate">
                  Contexte : <strong className="font-semibold">{contexte}</strong>
                  <span className="sr-only"> (l&apos;analyste connaît les chiffres de ce résultat)</span>
                </span>
                <button type="button" onClick={onRetirerContexte} aria-label="Ne plus transmettre ce résultat à l'analyste" className="grid size-5 shrink-0 place-items-center rounded hover:bg-surface/60">
                  <X className="size-3" aria-hidden />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <Saisie valeur={brouillon} onChange={onBrouillon} onEnvoyer={() => onPoser(brouillon)} enAttente={enAttente} champRef={champRef} />
      </div>
    </motion.div>
  );
}
