"use client";

import { memo, useEffect, useState } from "react";
import { motion } from "motion/react";
import Markdown, { type Components } from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { CircleAlert, RotateCcw } from "lucide-react";
import type { MessageConversation } from "./conversation";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

// Rendu des reponses de l'IA : balises sobres, titres ramenes a la taille du panneau,
// liens ouverts dans un nouvel onglet.
const titre = "mb-1.5 mt-3.5 text-titre font-semibold text-ink first:mt-0";
const sousTitre = "mb-1 mt-3 font-semibold text-ink first:mt-0";
const composantsMarkdown: Components = {
  p: ({ children }) => <p className="my-2 first:mt-0 last:mb-0">{children}</p>,
  ul: ({ children }) => <ul className="my-2 list-disc space-y-1 pl-5 marker:text-muted">{children}</ul>,
  ol: ({ children, start }) => (
    <ol start={start} className="my-2 list-decimal space-y-1 pl-5 marker:text-muted">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="pl-0.5">{children}</li>,
  h1: ({ children }) => <p className={titre}>{children}</p>,
  h2: ({ children }) => <p className={titre}>{children}</p>,
  h3: ({ children }) => <p className={sousTitre}>{children}</p>,
  h4: ({ children }) => <p className={sousTitre}>{children}</p>,
  h5: ({ children }) => <p className={sousTitre}>{children}</p>,
  h6: ({ children }) => <p className={sousTitre}>{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-ink">{children}</strong>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="font-medium text-accent-ink underline underline-offset-2">
      {children}
    </a>
  ),
  blockquote: ({ children }) => <blockquote className="my-2 border-l-2 border-line-strong pl-3">{children}</blockquote>,
  hr: () => <hr className="my-3 border-line" />,
  pre: ({ children }) => <pre className="my-2 overflow-x-auto rounded-controle bg-surface p-2.5 text-xs">{children}</pre>,
  code: ({ children }) => <code className="rounded bg-surface px-1 py-0.5 font-mono text-[0.85em]">{children}</code>,
};

/**
 * Les modeles ecrivent souvent les formules entre \[ \] ou \( \) : on les convertit
 * en $$ $$ et $ $, les seuls delimiteurs que remark-math reconnait.
 */
const BLOC_LATEX = /\\\[([\s\S]+?)\\\]/g;
const LIGNE_LATEX = /\\\(([\s\S]+?)\\\)/g;
export function versDelimiteursDollar(texte: string): string {
  return texte.replace(BLOC_LATEX, (_, f: string) => `\n$$\n${f.trim()}\n$$\n`).replace(LIGNE_LATEX, (_, f: string) => `$${f.trim()}$`);
}

const ContenuMarkdown = memo(function ContenuMarkdown({ texte }: { texte: string }) {
  return (
    <Markdown components={composantsMarkdown} skipHtml remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
      {versDelimiteursDollar(texte)}
    </Markdown>
  );
});

export function BulleMessage({ message }: { message: MessageConversation }) {
  const utilisateur = message.role === "user";
  return (
    <motion.li
      data-message=""
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, transition: { duration: DUREE.rapide } }}
      transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
      className={`flex ${utilisateur ? "justify-end" : "justify-start"}`}
    >
      <span className="sr-only">{utilisateur ? "Vous :" : "L'analyste (IA) :"}</span>
      {utilisateur ? (
        <div className="max-w-[85%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-accent px-3.5 py-2 text-sm leading-relaxed text-white">
          {message.content}
        </div>
      ) : (
        <div className="min-w-0 max-w-[92%] break-words rounded-2xl rounded-bl-md bg-surface-2 px-3.5 py-2.5 text-sm leading-relaxed text-ink-2">
          <ContenuMarkdown texte={message.content} />
        </div>
      )}
    </motion.li>
  );
}

/** Delai apres lequel on previent que la reponse peut etre longue (serveur qui se reveille). */
const ATTENTE_LONGUE_MS = 12000;

export function IndicateurEcriture() {
  const [longue, setLongue] = useState(false);
  useEffect(() => {
    const minuteur = setTimeout(() => setLongue(true), ATTENTE_LONGUE_MS);
    return () => clearTimeout(minuteur);
  }, []);

  return (
    <motion.li
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
      className="flex flex-col items-start gap-1.5"
    >
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md bg-surface-2 px-3.5 py-3" aria-hidden>
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="size-1.5 rounded-full bg-muted"
            animate={{ y: [0, -4, 0], opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 0.9, repeat: Infinity, ease: "easeInOut", delay: i * 0.15 }}
          />
        ))}
      </div>
      <span className="sr-only">L&apos;analyste écrit…</span>
      {longue && (
        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="px-1 text-xs text-muted">
          Encore un instant : le serveur se réveille peut-être.
        </motion.span>
      )}
    </motion.li>
  );
}

export function BlocErreur({ message, onReessayer }: { message: string; onReessayer: () => void }) {
  return (
    <motion.li
      role="alert"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
      className="flex items-start gap-2.5 rounded-tuile border border-loss/25 bg-loss-soft px-3 py-2.5 text-sm text-loss"
    >
      <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div className="min-w-0 flex-1">
        <p className="leading-relaxed">{message}</p>
        <motion.button
          type="button"
          onClick={onReessayer}
          whileTap={{ scale: 0.97 }}
          className="mt-2 inline-flex items-center gap-1.5 rounded-controle border border-loss/30 bg-surface px-2.5 py-1 text-xs font-semibold text-loss transition-colors hover:border-loss"
        >
          <RotateCcw className="size-3.5" aria-hidden />
          Réessayer
        </motion.button>
      </div>
    </motion.li>
  );
}
