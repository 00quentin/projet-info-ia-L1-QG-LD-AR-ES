"use client";

import { useState, type ReactNode } from "react";
import { motion } from "motion/react";
import {
  Anchor,
  Banknote,
  Bitcoin,
  Bot,
  ChartColumn,
  ChartLine,
  Coins,
  Frown,
  Fuel,
  Gem,
  Inbox,
  Landmark,
  Rocket,
  Scale,
  Shield,
  Smartphone,
  TrendingDown,
  TrendingUp,
  TriangleAlert,
  Activity,
  Virus,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { EASE_SORTIE, RESSORT } from "@/components/motion/transitions";
import { Pastille } from "@/components/ui/Carte";
import { ImageWikimedia } from "./Photo";

const survol = { y: -3, transition: RESSORT };

/* ---------- 4. Cas historiques ---------- */

const CRISES = [
  { annee: "1929", nom: "Krach de Wall Street", fichier: "Crowd_outside_nyse.jpg", Icone: TrendingDown, credit: "Public domain", couleur: "var(--loss)", desc: "Bulle spéculative + leverage 90% → −89% sur le Dow en 3 ans. Grande Dépression." },
  { annee: "1973", nom: "Choc pétrolier", fichier: "Line_at_a_gas_station,_June_15,_1979.jpg", Icone: Fuel, credit: "Public domain US", couleur: "var(--warn)", desc: "Embargo OPEP. Baril x4 en quelques mois. Stagflation mondiale jusqu’en 1982." },
  { annee: "1987", nom: "Lundi noir", fichier: "Black_Monday_Dow_Jones.svg", Icone: Zap, credit: "CC BY-SA", couleur: "var(--loss)", desc: "−22,6% en une seule séance. Premiers coupe-circuits introduits à Wall Street." },
  { annee: "2008", nom: "Subprimes", fichier: "Lehman_Brothers_Times_Square_by_David_Shankbone.jpg", Icone: Landmark, credit: "D. Shankbone, CC BY 3.0", couleur: "var(--loss)", desc: "Faillite Lehman. S&P −57% en 18 mois. Sauvetage massif (TARP, QE)." },
  { annee: "2020", nom: "COVID-19", fichier: "Wall_Street,_Manhattan_2009.jpg", Icone: Virus, credit: "Wikimedia Commons", couleur: "var(--accent)", desc: "Krach éclair (−34% en 23 jours). Sauvetage record : 10 000 milliards injectés." },
];

function CarteCrise({ c }: { c: (typeof CRISES)[number] }) {
  const [cassee, setCassee] = useState(false);
  return (
    <ElementCascade whileHover={survol} className="h-full">
      <article className="flex h-full flex-col overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
        <div className="relative aspect-[16/10] overflow-hidden" style={{ background: `color-mix(in oklab, ${c.couleur} 14%, var(--surface-2))` }}>
          <c.Icone className="absolute left-1/2 top-1/2 size-10 -translate-x-1/2 -translate-y-1/2 opacity-60" style={{ color: c.couleur }} aria-hidden />
          {!cassee && <ImageWikimedia fichier={c.fichier} alt="" largeur={640} onCassee={() => setCassee(true)} className="relative block size-full object-cover" />}
          <span className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full bg-surface/90 px-2.5 py-1 text-xs font-semibold text-ink shadow-card backdrop-blur">
            <span className="size-2 rounded-full" style={{ background: c.couleur }} aria-hidden />
            {c.annee}
          </span>
        </div>
        <div className="flex flex-1 flex-col border-t-2 p-4" style={{ borderTopColor: c.couleur }}>
          <h4 className="text-[15px] font-semibold tracking-tight text-ink">{c.nom}</h4>
          <p className="mt-1.5 flex-1 text-sm leading-relaxed text-ink-2">{c.desc}</p>
          <p className="mt-3 text-xs text-muted">{c.credit}</p>
        </div>
      </article>
    </ElementCascade>
  );
}

export function SyntheseCrises() {
  return (
    <Cascade auDefilement className="grid max-w-[46rem] grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {CRISES.map((c) => (
        <CarteCrise key={c.annee} c={c} />
      ))}
    </Cascade>
  );
}

/* ---------- Couleurs des classes d'actifs (synthèses 5 et 6) ---------- */

const CLASSES = {
  actions: { nom: "Actions", couleur: "var(--series-1)", Icone: TrendingUp },
  obligations: { nom: "Obligations", couleur: "var(--series-3)", Icone: Landmark },
  or: { nom: "Or", couleur: "var(--series-4)", Icone: Coins },
  crypto: { nom: "Crypto", couleur: "var(--series-5)", Icone: Bitcoin },
  cash: { nom: "Cash", couleur: "var(--series-2)", Icone: Banknote },
  diversification: { nom: "Diversification", couleur: "var(--muted)", Icone: Gem },
} as const;
type Classe = keyof typeof CLASSES;

/** Barre empilée qui se remplit segment par segment. */
function BarreEmpilee({ parts }: { parts: { classe: Classe; pct: number }[] }) {
  return (
    <div className="flex h-2.5 overflow-hidden rounded-full bg-surface-2" aria-hidden>
      {parts.map((p, i) => (
        <motion.span
          key={p.classe}
          className="h-full origin-left"
          style={{ width: `${p.pct}%`, background: CLASSES[p.classe].couleur }}
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45, ease: EASE_SORTIE, delay: 0.2 + i * 0.12 }}
        />
      ))}
    </div>
  );
}

/* ---------- 5. Stratégies : les 3 profils ---------- */

const PROFILS: { nom: string; Icone: LucideIcon; risque: string; ton: "gain" | "alerte" | "perte"; parts: { classe: Classe; pct: number }[] }[] = [
  { nom: "Prudent", Icone: Shield, risque: "Risque bas", ton: "gain", parts: [{ classe: "obligations", pct: 60 }, { classe: "actions", pct: 30 }, { classe: "or", pct: 10 }] },
  { nom: "Équilibré", Icone: Scale, risque: "Risque moyen", ton: "alerte", parts: [{ classe: "actions", pct: 50 }, { classe: "obligations", pct: 40 }, { classe: "diversification", pct: 10 }] },
  { nom: "Agressif", Icone: Rocket, risque: "Risque élevé", ton: "perte", parts: [{ classe: "actions", pct: 70 }, { classe: "crypto", pct: 20 }, { classe: "cash", pct: 10 }] },
];

export function SyntheseProfils() {
  return (
    <Cascade auDefilement className="grid max-w-[46rem] grid-cols-1 gap-3 sm:grid-cols-3">
      {PROFILS.map((p) => (
        <ElementCascade key={p.nom} whileHover={survol} className="flex flex-col gap-4 rounded-2xl border border-line bg-surface p-5 shadow-card">
          <div className="flex items-center justify-between gap-2">
            <span className="grid size-10 place-items-center rounded-xl bg-accent-soft text-accent-ink">
              <p.Icone className="size-5" aria-hidden />
            </span>
            <Pastille ton={p.ton}>{p.risque}</Pastille>
          </div>
          <h4 className="text-lg font-semibold tracking-tight text-ink">{p.nom}</h4>
          <BarreEmpilee parts={p.parts} />
          <ul className="flex flex-col gap-1.5 text-sm text-ink-2">
            {p.parts.map((x) => (
              <li key={x.classe} className="flex items-center gap-2">
                <span className="size-2 rounded-full" style={{ background: CLASSES[x.classe].couleur }} aria-hidden />
                <span className="font-semibold text-ink tabular-nums">{x.pct}%</span> {CLASSES[x.classe].nom.toLowerCase()}
              </li>
            ))}
          </ul>
        </ElementCascade>
      ))}
    </Cascade>
  );
}

/* ---------- 6. Construction : exemple d'allocation équilibrée ---------- */

const ALLOCATION: { classe: Classe; pct: number }[] = [
  { classe: "actions", pct: 40 },
  { classe: "obligations", pct: 25 },
  { classe: "or", pct: 15 },
  { classe: "crypto", pct: 10 },
  { classe: "cash", pct: 10 },
];

export function SyntheseAllocation() {
  return (
    <div className="max-w-[46rem] rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-6">
      <BarreEmpilee parts={ALLOCATION} />
      <ul className="mt-5 flex flex-col gap-3.5" aria-label="Répartition de l’exemple d’allocation">
        {ALLOCATION.map((a, i) => {
          const c = CLASSES[a.classe];
          return (
            <li key={a.classe} className="grid grid-cols-[minmax(0,9rem)_1fr_3rem] items-center gap-3 text-sm">
              <span className="flex items-center gap-2 text-ink">
                <c.Icone className="size-4 shrink-0" style={{ color: c.couleur }} aria-hidden />
                {c.nom}
              </span>
              <span className="h-2 overflow-hidden rounded-full bg-surface-2" aria-hidden>
                <motion.span
                  className="block h-full origin-left rounded-full"
                  style={{ width: `${a.pct * 2}%`, background: c.couleur }}
                  initial={{ scaleX: 0 }}
                  whileInView={{ scaleX: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.55, ease: EASE_SORTIE, delay: 0.15 + i * 0.07 }}
                />
              </span>
              <NombreAnime valeur={a.pct} depuis={0} duree={0.6} format={(v) => `${Math.round(v)}%`} className="text-right font-semibold text-ink tabular-nums" />
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/* ---------- 7. Biais : les 4 grands biais ---------- */

const BIAIS = [
  { nom: "Peur", Icone: Frown, desc: "Vendre au pire moment, après une chute", couleur: "var(--loss)" },
  { nom: "Cupidité", Icone: Coins, desc: "Acheter au pic, sur un coup d’euphorie", couleur: "var(--gain)" },
  { nom: "FOMO", Icone: Smartphone, desc: "Courir après une tendance par peur de la rater", couleur: "var(--series-5)" },
  { nom: "Ancrage", Icone: Anchor, desc: "S’accrocher au prix d’achat originel", couleur: "var(--accent)" },
];

export function SyntheseBiais() {
  return (
    <Cascade auDefilement className="grid max-w-[46rem] grid-cols-1 gap-3 sm:grid-cols-2">
      {BIAIS.map((b) => (
        <ElementCascade
          key={b.nom}
          whileHover={survol}
          className="flex items-start gap-4 rounded-2xl border border-line bg-surface p-5 shadow-card"
          style={{ borderLeftColor: b.couleur, borderLeftWidth: 3 }}
        >
          <motion.span
            className="grid size-11 shrink-0 place-items-center rounded-xl"
            style={{ background: `color-mix(in oklab, ${b.couleur} 14%, transparent)`, color: b.couleur }}
            whileHover={{ rotate: -8, scale: 1.06 }}
            transition={RESSORT}
          >
            <b.Icone className="size-5" aria-hidden />
          </motion.span>
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide text-ink">{b.nom}</h4>
            <p className="mt-1 text-sm leading-relaxed text-ink-2">{b.desc}</p>
          </div>
        </ElementCascade>
      ))}
    </Cascade>
  );
}

/* ---------- 8. Lexique : les termes essentiels ---------- */

const TERMES: { terme: string; desc: string; symbole: ReactNode }[] = [
  { terme: "Alpha", desc: "Surperformance vs le marché", symbole: "α" },
  { terme: "Beta", desc: "Sensibilité vs l’indice de référence", symbole: "β" },
  { terme: "Drawdown", desc: "Perte maximale du pic au creux", symbole: <TrendingDown className="size-5" aria-hidden /> },
  { terme: "Sharpe", desc: "Rendement par unité de risque", symbole: <Scale className="size-5" aria-hidden /> },
  { terme: "VaR 95%", desc: "Perte maximale dans 95% des cas", symbole: <TriangleAlert className="size-5" aria-hidden /> },
  { terme: "Volatilité", desc: "Amplitude des variations", symbole: <Activity className="size-5" aria-hidden /> },
];

export function SyntheseLexique() {
  return (
    <Cascade auDefilement className="grid max-w-[46rem] grid-cols-2 gap-3 sm:grid-cols-3">
      {TERMES.map((t) => (
        <ElementCascade key={t.terme} whileHover={survol} className="rounded-2xl border border-line bg-surface p-4 shadow-card">
          <span className="grid size-10 place-items-center rounded-xl bg-accent-soft font-serif text-xl font-semibold text-accent-ink">{t.symbole}</span>
          <h4 className="mt-3 text-[15px] font-semibold tracking-tight text-ink">{t.terme}</h4>
          <p className="mt-1 text-sm leading-relaxed text-ink-2">{t.desc}</p>
        </ElementCascade>
      ))}
    </Cascade>
  );
}

/* ---------- 9. Méthodologie : le pipeline ---------- */

const ETAPES = [
  { Icone: Inbox, libelle: "Saisie", desc: "Votre scénario en français" },
  { Icone: Bot, libelle: "IA", desc: "GPT-6.1 calibre les chocs" },
  { Icone: ChartLine, libelle: "Simulation", desc: "Modèle probabiliste, historique ou tendance" },
  { Icone: ChartColumn, libelle: "Résultats", desc: "Graphiques + métriques" },
];

export function SynthesePipeline() {
  return (
    <div className="relative max-w-[46rem]">
      {/* Fil qui relie les étapes : horizontal sur grand écran, vertical sur mobile. */}
      <motion.span
        aria-hidden
        className="absolute left-[2.15rem] top-10 bottom-10 w-px origin-top bg-line-strong sm:left-[12.5%] sm:right-[12.5%] sm:top-[2.15rem] sm:bottom-auto sm:h-px sm:w-auto sm:origin-left"
        initial={{ scale: 0 }}
        whileInView={{ scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: EASE_SORTIE, delay: 0.1 }}
      />
      <Cascade auDefilement className="relative grid grid-cols-1 gap-3 sm:grid-cols-4">
        {ETAPES.map((e, i) => (
          <ElementCascade key={e.libelle} className="flex items-center gap-4 sm:flex-col sm:text-center">
            <motion.span
              whileHover={{ scale: 1.08 }}
              transition={RESSORT}
              className="relative grid size-[4.3rem] shrink-0 place-items-center rounded-2xl border border-line bg-surface text-accent-ink shadow-card"
            >
              <e.Icone className="size-6" aria-hidden />
              <span className="absolute -right-1.5 -top-1.5 grid size-6 place-items-center rounded-full bg-accent text-xs font-semibold text-surface">{i + 1}</span>
            </motion.span>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wide text-ink">{e.libelle}</h4>
              <p className="mt-1 text-sm leading-relaxed text-ink-2">{e.desc}</p>
            </div>
          </ElementCascade>
        ))}
      </Cascade>
    </div>
  );
}
