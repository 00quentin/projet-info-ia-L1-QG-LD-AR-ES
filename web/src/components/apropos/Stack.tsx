"use client";

import { motion } from "motion/react";
import { ArrowRight, Bot, Database, FileText, Globe, Server, type LucideIcon } from "lucide-react";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { STACK } from "@/contenu/apropos";

const ICONES: Record<string, LucideIcon> = { site: Globe, moteur: Server, donnees: Database, ia: Bot, rapports: FileText };

/** Chemin d'une simulation : navigateur → site → API → sources. */
function Schema() {
  const etapes = [
    { titre: "Votre navigateur", detail: "scénario, portefeuille" },
    { titre: "Site Next.js", detail: "interface et graphiques" },
    { titre: "API FastAPI", detail: "moteur Python" },
    { titre: "Sources", detail: "Yahoo Finance · BCE · OpenAI" },
  ];
  return (
    <ol className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center" aria-label="Chemin d’une simulation">
      {etapes.map((e, i) => (
        <li key={e.titre} className="flex flex-col items-center gap-2 sm:flex-1 sm:flex-row">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.35, ease: EASE_SORTIE, delay: i * 0.12 }}
            className={`w-full rounded-xl border px-3 py-2.5 text-center sm:flex-1 ${i === 2 ? "border-accent/40 bg-accent-soft" : "border-line bg-surface"}`}
          >
            <p className="text-sm font-semibold text-ink">{e.titre}</p>
            <p className="mt-0.5 text-xs text-muted">{e.detail}</p>
          </motion.div>
          {i < etapes.length - 1 && (
            <motion.span
              initial={{ opacity: 0, x: -4 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: 0.08 + i * 0.12 }}
              className="text-muted"
              aria-hidden
            >
              <ArrowRight className="size-4 rotate-90 sm:rotate-0" />
            </motion.span>
          )}
        </li>
      ))}
    </ol>
  );
}

export function Stack() {
  return (
    <div className="flex flex-col gap-4">
      <Schema />
      <Cascade auDefilement className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {STACK.map((b) => {
          const Icone = ICONES[b.id];
          return (
            <ElementCascade key={b.id} whileHover={{ y: -3, transition: RESSORT }} className="flex flex-col gap-3 rounded-2xl border border-line bg-surface p-5 shadow-card">
              <div className="flex items-center gap-3">
                <span className="grid size-9 place-items-center rounded-xl bg-accent-soft text-accent-ink">
                  <Icone className="size-4.5" aria-hidden />
                </span>
                <h3 className="text-[15px] font-semibold tracking-tight text-ink">{b.titre}</h3>
              </div>
              <p className="text-sm leading-relaxed text-ink-2">{b.role}</p>
              <ul className="mt-auto flex flex-wrap gap-1.5" aria-label={`Outils : ${b.titre}`}>
                {b.outils.map((o) => (
                  <li key={o} className="rounded-full border border-line bg-surface-2 px-2.5 py-1 text-xs font-medium text-ink-2">
                    {o}
                  </li>
                ))}
              </ul>
            </ElementCascade>
          );
        })}
      </Cascade>
    </div>
  );
}
