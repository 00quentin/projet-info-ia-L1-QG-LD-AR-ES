"use client";

import { useId, useState } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "motion/react";
import { Check, SlidersHorizontal, TriangleAlert, X } from "lucide-react";
import { SelecteurActifs } from "./SelecteurActifs";
import type { ActifPerso, Catalogue } from "@/lib/api";
import { nomCourt } from "@/contenu/actifs";
import { champ, puce } from "./styles";
import { ChampMontant } from "@/components/ui/ChampMontant";
import { AideInfo, Infobulle, useEstClient } from "@/components/ui/Infobulle";
import { RESSORT } from "@/components/motion/transitions";

export const PROFIL_PERSONNALISE = "Personnalisé";

export type ValeurPortefeuille = {
  capital: number;
  profil: string;
  /** Cles des actifs coches (catalogue + "PERSO_<TICKER>"). */
  actifs: string[];
  /** Pourcentages entiers, utilises seulement avec le profil Personnalise. */
  allocations: Record<string, number>;
  actifsPerso: ActifPerso[];
};

// Phrases lues par les lecteurs d'ecran et montrees dans l'infobulle de chaque profil.
const DESCRIPTIONS_PROFIL: Record<string, string> = {
  Prudent: "Surtout des obligations et de l'or",
  Équilibré: "Actions, obligations, un peu de crypto",
  Agressif: "Actions et cryptomonnaies",
  Personnalisé: "Vous fixez chaque part",
};

/** Montants proposes en un clic sous le champ du capital. */
const MONTANTS_RAPIDES = [1_000, 10_000, 100_000];

/** Grandes familles de la mini-barre de repartition des profils (reconnues au nom de categorie). */
const POCHES = [
  { cle: "actions", libelle: "Actions", couleur: "var(--series-1)", motifs: ["action", "indice", "sector", "themat"] },
  { cle: "obligations", libelle: "Obligations", couleur: "var(--series-3)", motifs: ["oblig"] },
  { cle: "matieres", libelle: "Matières premières", couleur: "var(--series-4)", motifs: ["matiere"] },
  { cle: "crypto", libelle: "Cryptos", couleur: "var(--series-5)", motifs: ["crypto"] },
  { cle: "devises", libelle: "Devises", couleur: "var(--series-2)", motifs: ["devise", "volatil"] },
] as const;
type Poche = (typeof POCHES)[number];

const normaliser = (t: string) => t.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

function pochesDuCatalogue(catalogue: Catalogue): Map<string, Poche> {
  const m = new Map<string, Poche>();
  for (const c of catalogue.categories) {
    const nom = normaliser(c.nom);
    const poche = POCHES.find((p) => p.motifs.some((motif) => nom.includes(motif))) ?? POCHES[0];
    c.actifs.forEach((a) => m.set(a.cle, poche));
  }
  return m;
}

/** Part de chaque famille (0 a 1) pour des poids quelconques ; les actifs inconnus comptent comme actions. */
function repartitionParPoche(poids: Record<string, number>, poches: Map<string, Poche>) {
  const total = Object.values(poids).reduce((s, p) => s + p, 0);
  if (!total) return [];
  return POCHES.map((p) => ({
    poche: p,
    part: Object.entries(poids).reduce((s, [cle, v]) => s + ((poches.get(cle) ?? POCHES[0]) === p ? v : 0), 0) / total,
  })).filter((x) => x.part > 0);
}

export const nomCourtProfil = (profil: string) => profil.split(" (")[0];

export function portefeuilleInitial(catalogue: Catalogue): ValeurPortefeuille {
  const equilibre = catalogue.profils.find((p) => p.nom.startsWith("Équilibré")) ?? catalogue.profils[0];
  return {
    capital: catalogue.capital.defaut,
    profil: equilibre.nom,
    actifs: catalogue.categories.flatMap((c) => c.actifs.filter((a) => a.par_defaut).map((a) => a.cle)),
    allocations: {},
    actifsPerso: [],
  };
}

/** Message d'erreur a afficher, ou null si le portefeuille est valide. */
export function validerPortefeuille(v: ValeurPortefeuille, catalogue: Catalogue): string | null {
  if (v.actifs.length === 0) return "Sélectionnez au moins un actif.";
  if (v.capital < catalogue.capital.min || v.capital > catalogue.capital.max)
    return `Le capital doit être compris entre ${catalogue.capital.min.toLocaleString("fr-FR")} € et ${catalogue.capital.max.toLocaleString("fr-FR")} €.`;
  if (v.profil === PROFIL_PERSONNALISE) {
    const total = v.actifs.reduce((s, a) => s + (v.allocations[a] ?? 0), 0);
    if (total !== 100) return `La répartition doit totaliser 100 % (actuellement ${total} %).`;
  }
  return null;
}

type Props = {
  catalogue: Catalogue;
  valeur: ValeurPortefeuille;
  onChange: (v: ValeurPortefeuille) => void;
  /** Le backtest ne sait pas rejouer les actifs personnalises : on masque l'ajout. */
  autoriserActifsPerso?: boolean;
};

function MiniBarre({ parts }: { parts: { poche: Poche; part: number }[] }) {
  if (!parts.length) return <span className="block h-1.5 rounded-full border border-dashed border-line-strong" aria-hidden />;
  return (
    <span className="flex h-1.5 gap-px overflow-hidden rounded-full" aria-hidden>
      {parts.map(({ poche, part }) => (
        <span key={poche.cle} className="h-full" style={{ width: `${part * 100}%`, background: poche.couleur }} />
      ))}
    </span>
  );
}

const detailRepartition = (parts: { poche: Poche; part: number }[]) => parts.map(({ poche, part }) => `${poche.libelle} ${Math.round(part * 100)} %`).join(" · ");

export function ChoixPortefeuille({ catalogue, valeur: v, onChange, autoriserActifsPerso = true }: Props) {
  const maj = (partiel: Partial<ValeurPortefeuille>) => onChange({ ...v, ...partiel });
  const idGroupe = useId();
  const poches = pochesDuCatalogue(catalogue);
  const montants = MONTANTS_RAPIDES.filter((m) => m >= catalogue.capital.min && m <= catalogue.capital.max);
  const allocationsPerso = Object.fromEntries(v.actifs.map((a) => [a, v.allocations[a] ?? 0]));

  function choisirProfil(nom: string) {
    const profil = catalogue.profils.find((p) => p.nom === nom);
    // On ajoute les actifs du profil a la selection : sinon une partie du profil serait ignoree.
    const actifs = profil?.poids ? Array.from(new Set([...v.actifs, ...Object.keys(profil.poids)])) : v.actifs;
    // Passage en Personnalise : on part d'une repartition egale plutot que de 0 % partout.
    let allocations = v.allocations;
    if (nom === PROFIL_PERSONNALISE && actifs.reduce((t, a) => t + (v.allocations[a] ?? 0), 0) === 0 && actifs.length) {
      const base = Math.floor(100 / actifs.length);
      allocations = Object.fromEntries(actifs.map((a, i) => [a, base + (i < 100 - base * actifs.length ? 1 : 0)]));
    }
    maj({ profil: nom, actifs, allocations });
  }

  const legende = POCHES.filter((p) => catalogue.profils.some((pr) => repartitionParPoche(pr.poids ?? {}, poches).some((x) => x.poche === p)));

  return (
    <div className="flex flex-col gap-4">
      <div>
        <label htmlFor={`${idGroupe}-capital`} className="mb-1.5 block text-sm font-medium">
          Capital de départ
        </label>
        <ChampMontant id={`${idGroupe}-capital`} valeur={v.capital} max={catalogue.capital.max} onChange={(capital) => maj({ capital })} className={champ} />
        {montants.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5" aria-label="Montants rapides">
            {montants.map((m) => (
              <button key={m} type="button" aria-pressed={v.capital === m} onClick={() => maj({ capital: m })} className={`${puce} tabular-nums`}>
                {m.toLocaleString("fr-FR")} €
              </button>
            ))}
          </div>
        )}
      </div>

      <div>
        <div role="radiogroup" aria-label="Profil d'investisseur" className="grid grid-cols-2 gap-2">
          {catalogue.profils.map((p) => {
            const choisi = v.profil === p.nom;
            const court = nomCourtProfil(p.nom);
            const parts = repartitionParPoche(p.poids ?? (p.nom === PROFIL_PERSONNALISE ? allocationsPerso : {}), poches);
            const description = DESCRIPTIONS_PROFIL[court] ?? court;
            return (
              <Infobulle key={p.nom} className="flex" texte={parts.length ? `${description}. ${detailRepartition(parts)}.` : `${description}.`}>
                <motion.button
                  type="button"
                  role="radio"
                  aria-checked={choisi}
                  onClick={() => choisirProfil(p.nom)}
                  whileTap={{ scale: 0.98 }}
                  className={`relative w-full rounded-tuile border px-3 pb-3 pt-2.5 text-left transition-colors ${choisi ? "border-accent" : "border-line bg-surface hover:border-line-strong"}`}
                >
                  {choisi && <motion.span layoutId={`${idGroupe}-profil`} className="absolute inset-0 rounded-[calc(var(--radius-tuile)-1px)] bg-accent-soft" transition={RESSORT} />}
                  <span className="relative flex flex-col gap-2">
                    <span className={`text-sm font-semibold transition-colors ${choisi ? "text-accent-ink" : ""}`}>{court}</span>
                    <MiniBarre parts={parts} />
                  </span>
                </motion.button>
              </Infobulle>
            );
          })}
        </div>
        {legende.length > 0 && (
          <ul className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted" aria-label="Légende des barres de répartition">
            {legende.map((p) => (
              <li key={p.cle} className="flex items-center gap-1.5">
                <span className="size-2 rounded-sm" style={{ background: p.couleur }} aria-hidden />
                {p.libelle}
              </li>
            ))}
          </ul>
        )}
      </div>

      <ActifsChoisis catalogue={catalogue} valeur={v} onChange={onChange} autoriserActifsPerso={autoriserActifsPerso} />
    </div>
  );
}

function Etiquette({ nom, part, onRetirer }: { nom: string; part: number | null; onRetirer: () => void }) {
  const investi = part != null;
  return (
    <motion.li
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={RESSORT}
      className={`flex items-center gap-1.5 rounded-full border py-1 pl-2.5 pr-1 text-aide ${investi ? "border-transparent bg-accent-soft text-accent-ink" : "border-line text-ink-2"}`}
    >
      <span className="font-medium">{nom}</span>
      <span className={`tabular-nums ${investi ? "font-semibold" : "text-muted"}`}>{Math.round((part ?? 0) * 100)} %</span>
      <button type="button" onClick={onRetirer} aria-label={`Retirer ${nom}`} className="grid size-5 place-items-center rounded-full text-muted transition-colors hover:bg-surface hover:text-loss">
        <X className="size-3" aria-hidden />
      </button>
    </motion.li>
  );
}

/** Etiquettes des actifs choisis (avec leur part), et ouverture du selecteur. */
function ActifsChoisis({ catalogue, valeur: v, onChange, autoriserActifsPerso }: Props & { autoriserActifsPerso: boolean }) {
  const [ouvert, setOuvert] = useState(false);
  const estClient = useEstClient();
  const perso = v.profil === PROFIL_PERSONNALISE;
  const totalPerso = v.actifs.reduce((s, a) => s + (v.allocations[a] ?? 0), 0);
  const noms = new Map<string, string>(catalogue.categories.flatMap((c) => c.actifs.map((a) => [a.cle, nomCourt(a.cle, a.nom)] as const)));
  v.actifsPerso.forEach((a) => noms.set(a.cle, a.ticker));
  const profil = catalogue.profils.find((p) => p.nom === v.profil);
  const actifsDuProfil = new Set(Object.keys(profil?.poids ?? {}));

  // Part de chaque actif dans le portefeuille (profil type : poids renormalises sur les actifs coches).
  const parts = new Map<string, number>();
  if (perso) {
    v.actifs.forEach((a) => parts.set(a, (v.allocations[a] ?? 0) / 100));
  } else if (profil?.poids) {
    const retenus = v.actifs.filter((a) => (profil.poids?.[a] ?? 0) > 0);
    const total = retenus.reduce((s, a) => s + (profil.poids?.[a] ?? 0), 0);
    retenus.forEach((a) => parts.set(a, (profil.poids?.[a] ?? 0) / (total || 1)));
  }
  const investis = v.actifs.filter((a) => parts.get(a)).sort((a, b) => (parts.get(b) ?? 0) - (parts.get(a) ?? 0));
  const suivis = v.actifs.filter((a) => !parts.get(a));
  const nom = (cle: string) => noms.get(cle) ?? cle;
  const totalOk = totalPerso === 100;

  function retirer(cle: string) {
    onChange({ ...v, actifs: v.actifs.filter((a) => a !== cle), actifsPerso: v.actifsPerso.filter((a) => a.cle !== cle) });
  }

  function repartirEgalement() {
    const n = v.actifs.length;
    if (n === 0) return;
    const base = Math.floor(100 / n);
    onChange({ ...v, allocations: Object.fromEntries(v.actifs.map((a, i) => [a, base + (i < 100 - base * n ? 1 : 0)])) });
  }

  return (
    <div className="rounded-tuile border border-line bg-surface p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium">
          Actifs <span className="font-normal tabular-nums text-muted">· {v.actifs.length}</span>
        </span>
        <motion.button
          type="button"
          onClick={() => setOuvert(true)}
          whileTap={{ scale: 0.97 }}
          aria-label="Modifier les actifs"
          className="flex items-center gap-1.5 rounded-controle border border-line px-2.5 py-1.5 text-aide font-medium text-ink-2 transition-colors hover:border-line-strong hover:text-ink"
        >
          <SlidersHorizontal className="size-3.5" aria-hidden />
          Modifier
        </motion.button>
      </div>

      {perso ? (
        <ul className="mt-2.5 flex flex-col" aria-label="Répartition personnalisée">
          <AnimatePresence initial={false}>
            {v.actifs.map((cle) => (
              <motion.li key={cle} layout initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
                <div className="flex items-center justify-between gap-2 py-1">
                  <span className="min-w-0 truncate text-sm">{nom(cle)}</span>
                  <span className="flex shrink-0 items-center gap-1.5 text-sm text-muted">
                    <input
                      type="number"
                      inputMode="numeric"
                      min={0}
                      max={100}
                      aria-label={`Part de ${nom(cle)} en pourcentage`}
                      value={v.allocations[cle] ?? 0}
                      onChange={(e) => onChange({ ...v, allocations: { ...v.allocations, [cle]: Math.min(100, Math.max(0, Math.round(Number(e.target.value)))) } })}
                      className="w-16 rounded-controle border border-line bg-surface px-2 py-1 text-right text-sm text-ink tabular-nums outline-none focus:border-accent"
                    />
                    %
                    <button type="button" onClick={() => retirer(cle)} aria-label={`Retirer ${nom(cle)}`} className="grid size-6 place-items-center rounded-controle text-muted transition-colors hover:bg-surface-2 hover:text-loss">
                      <X className="size-3.5" aria-hidden />
                    </button>
                  </span>
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
          <li className="mt-1.5 border-t border-line pt-2.5">
            <div className="flex items-center justify-between gap-2 text-sm">
              <span className={`flex items-center gap-1.5 ${totalOk ? "text-ink" : "text-warn"}`} role="status">
                {totalOk ? <Check className="size-4 text-accent-ink" aria-hidden /> : <TriangleAlert className="size-4" aria-hidden />}
                Total <strong className="tabular-nums">{totalPerso} %</strong>
                {!totalOk && <span className="text-aide">(doit faire 100 %)</span>}
              </span>
              <button type="button" onClick={repartirEgalement} className="text-aide font-medium text-accent-ink hover:underline">
                Répartir également
              </button>
            </div>
            <div className="mt-2 h-1 overflow-hidden rounded-full bg-surface-2" aria-hidden>
              <div className={`h-full rounded-full transition-[width] duration-200 ${totalOk ? "bg-accent" : "bg-warn"}`} style={{ width: `${Math.min(totalPerso, 100)}%` }} />
            </div>
          </li>
        </ul>
      ) : (
        <div className="mt-3 flex flex-col gap-3">
          <div>
            <p className="mb-1.5 text-xs font-medium text-muted">
              Investis <span className="tabular-nums">· {investis.length}</span>
            </p>
            {investis.length ? (
              <ul className="flex flex-wrap gap-1.5" aria-label="Actifs investis">
                <AnimatePresence initial={false}>
                  {investis.map((cle) => (
                    <Etiquette key={cle} nom={nom(cle)} part={parts.get(cle) ?? 0} onRetirer={() => retirer(cle)} />
                  ))}
                </AnimatePresence>
              </ul>
            ) : (
              <p className="text-aide text-warn">Aucun actif de ce profil n&apos;est sélectionné : ajoutez-en avec « Modifier ».</p>
            )}
          </div>
          {suivis.length > 0 && (
            <div>
              <p className="mb-1.5 flex items-center gap-1 text-xs font-medium text-muted">
                Suivis, sans investissement <span className="tabular-nums">· {suivis.length}</span>
                <AideInfo
                  libelle="À propos des actifs suivis"
                  texte="Ces actifs ne font pas partie du profil : aucun euro n'y est placé. Ils sont analysés à titre de comparaison."
                />
              </p>
              <ul className="flex flex-wrap gap-1.5" aria-label="Actifs suivis sans investissement">
                <AnimatePresence initial={false}>
                  {suivis.map((cle) => (
                    <Etiquette key={cle} nom={nom(cle)} part={null} onRetirer={() => retirer(cle)} />
                  ))}
                </AnimatePresence>
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Portail vers <body> : la colonne collante du formulaire cree un contexte
          d'empilement qui ferait passer la fenetre sous l'en-tete. */}
      {estClient &&
        createPortal(
          <AnimatePresence>
            {ouvert && (
              <SelecteurActifs
                catalogue={catalogue}
                actifs={v.actifs}
                actifsPerso={v.actifsPerso}
                autoriserActifsPerso={autoriserActifsPerso}
                actifsDuProfil={actifsDuProfil}
                nomProfil={profil?.poids ? nomCourtProfil(profil.nom) : null}
                onFermer={() => setOuvert(false)}
                onValider={(actifs, actifsPerso) => {
                  onChange({ ...v, actifs, actifsPerso });
                  setOuvert(false);
                }}
              />
            )}
          </AnimatePresence>,
          document.body,
        )}
    </div>
  );
}
