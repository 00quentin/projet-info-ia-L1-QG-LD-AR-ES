"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { ArrowRight, ChevronDown } from "lucide-react";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";
import type { QuestionFaq } from "@/contenu/faq";

function Question({ q, ouvert, basculer }: { q: QuestionFaq; ouvert: boolean; basculer: () => void }) {
  const reduit = useReducedMotion();
  const idBouton = `${q.id}-question`;
  const idReponse = `${q.id}-reponse`;
  return (
    <li id={q.id} className="scroll-mt-6 lg:scroll-mt-36">
      <h3>
        <button
          type="button"
          id={idBouton}
          aria-expanded={ouvert}
          aria-controls={idReponse}
          onClick={basculer}
          className="flex w-full items-start gap-4 px-4 py-4 text-left text-[15px] font-medium leading-snug text-ink transition-colors hover:bg-surface-2/60 sm:px-5 sm:text-base"
        >
          <span className="min-w-0 flex-1">{q.question}</span>
          <motion.span
            animate={{ rotate: ouvert ? 180 : 0 }}
            transition={{ duration: reduit ? 0 : DUREE.normale, ease: EASE_SORTIE }}
            className={`mt-0.5 grid size-6 shrink-0 place-items-center rounded-full transition-colors ${ouvert ? "bg-accent-soft text-accent-ink" : "bg-surface-2 text-muted"}`}
            aria-hidden
          >
            <ChevronDown className="size-4" />
          </motion.span>
        </button>
      </h3>
      {/* Fermée, la réponse reste dans la page mais inerte : ni focus clavier, ni lecture par les lecteurs d'écran. */}
      <motion.div
        id={idReponse}
        role="region"
        aria-labelledby={idBouton}
        inert={!ouvert}
        initial={false}
        animate={ouvert ? { height: "auto", opacity: 1 } : { height: 0, opacity: 0 }}
        transition={{ duration: reduit ? 0 : DUREE.normale, ease: EASE_SORTIE }}
        className="overflow-hidden"
      >
        <div className="flex max-w-[40rem] flex-col gap-3 px-4 pb-5 text-[15px] leading-[1.75] text-ink-2 sm:px-5">
          {q.reponse.map((p) => (
            <p key={p.slice(0, 40)}>{p}</p>
          ))}
          {q.liens && (
            <p className="flex flex-wrap gap-x-4 gap-y-1">
              {q.liens.map((l) => (
                <Link
                  key={l.href}
                  href={l.href}
                  className="inline-flex items-center gap-1 text-sm font-medium text-accent-ink underline decoration-accent/40 underline-offset-2 transition-colors hover:decoration-accent"
                >
                  {l.libelle}
                  <ArrowRight className="size-3.5" aria-hidden />
                </Link>
              ))}
            </p>
          )}
        </div>
      </motion.div>
    </li>
  );
}

/** Questions en accordéons : plusieurs peuvent être ouvertes ; /faq#identifiant ouvre la question visée. */
export function ListeQuestions({ questions }: { questions: QuestionFaq[] }) {
  const [ouvertes, setOuvertes] = useState<string[]>([]);

  useEffect(() => {
    const ouvrirDepuisAncre = () => {
      const ancre = decodeURIComponent(window.location.hash.slice(1));
      if (!questions.some((q) => q.id === ancre)) return;
      setOuvertes((o) => (o.includes(ancre) ? o : [...o, ancre]));
      requestAnimationFrame(() => document.getElementById(ancre)?.scrollIntoView({ block: "start" }));
    };
    ouvrirDepuisAncre();
    window.addEventListener("hashchange", ouvrirDepuisAncre);
    return () => window.removeEventListener("hashchange", ouvrirDepuisAncre);
  }, [questions]);

  const basculer = (id: string) => setOuvertes((o) => (o.includes(id) ? o.filter((x) => x !== id) : [...o, id]));

  return (
    <ul className="divide-y divide-line overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      {questions.map((q) => (
        <Question key={q.id} q={q} ouvert={ouvertes.includes(q.id)} basculer={() => basculer(q.id)} />
      ))}
    </ul>
  );
}
