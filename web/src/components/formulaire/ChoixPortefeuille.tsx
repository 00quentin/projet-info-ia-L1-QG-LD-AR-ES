"use client";

import { useId, useState, useSyncExternalStore } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "motion/react";
import { SlidersHorizontal, X } from "lucide-react";
import { SelecteurActifs } from "./SelecteurActifs";
import type { ActifPerso, Catalogue } from "@/lib/api";
import { champ } from "./styles";
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

const DESCRIPTIONS_PROFIL: Record<string, string> = {
  Prudent: "Surtout des obligations et de l'or",
  Équilibré: "Actions, obligations, un peu de crypto",
  Agressif: "Actions et cryptomonnaies",
  Personnalisé: "Vous fixez chaque part",
};

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

export function ChoixPortefeuille({ catalogue, valeur: v, onChange, autoriserActifsPerso = true }: Props) {
  const maj = (partiel: Partial<ValeurPortefeuille>) => onChange({ ...v, ...partiel });
  const idGroupe = useId();

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

  return (
    <div className="flex flex-col gap-3">
      <div>
        <label htmlFor="capital" className="mb-1.5 block text-sm font-medium">
          Capital de départ
        </label>
        <div className="relative">
          <input
            id="capital"
            type="number"
            inputMode="numeric"
            min={catalogue.capital.min}
            max={catalogue.capital.max}
            value={v.capital || ""}
            onChange={(e) => maj({ capital: Math.min(catalogue.capital.max, Math.max(0, Number(e.target.value))) })}
            className={`${champ} pr-9 tabular-nums`}
          />
          <span className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-sm text-muted">€</span>
        </div>
      </div>

      <div role="radiogroup" aria-label="Profil d'investisseur" className="grid grid-cols-2 gap-2">
        {catalogue.profils.map((p) => {
          const choisi = v.profil === p.nom;
          const court = nomCourtProfil(p.nom);
          return (
            <motion.button
              key={p.nom}
              type="button"
              role="radio"
              aria-checked={choisi}
              onClick={() => choisirProfil(p.nom)}
              whileTap={{ scale: 0.97 }}
              className={`relative rounded-xl border px-3 py-2.5 text-left transition-colors ${choisi ? "border-accent" : "border-line bg-surface hover:border-line-strong"}`}
            >
              {choisi && <motion.span layoutId={`${idGroupe}-profil`} className="absolute inset-0 rounded-[11px] bg-accent-soft" transition={RESSORT} />}
              <span className="relative">
                <span className={`block text-sm font-semibold transition-colors ${choisi ? "text-accent-ink" : ""}`}>{court}</span>
                <span className="mt-0.5 block text-xs leading-snug text-muted">{DESCRIPTIONS_PROFIL[court]}</span>
              </span>
            </motion.button>
          );
        })}
      </div>

      <ActifsChoisis catalogue={catalogue} valeur={v} onChange={onChange} autoriserActifsPerso={autoriserActifsPerso} />
    </div>
  );
}

const abonnementVide = () => () => {};

/** Etiquettes des actifs choisis (avec leur part), et ouverture du selecteur. */
function ActifsChoisis({ catalogue, valeur: v, onChange, autoriserActifsPerso }: Props & { autoriserActifsPerso: boolean }) {
  const [ouvert, setOuvert] = useState(false);
  const estClient = useSyncExternalStore(
    abonnementVide,
    () => true,
    () => false,
  );
  const perso = v.profil === PROFIL_PERSONNALISE;
  const totalPerso = v.actifs.reduce((s, a) => s + (v.allocations[a] ?? 0), 0);
  const noms = new Map<string, string>(catalogue.categories.flatMap((c) => c.actifs.map((a) => [a.cle, a.nom] as const)));
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
  const tries = [...v.actifs].sort((a, b) => (parts.get(b) ?? 0) - (parts.get(a) ?? 0));
  const court = (cle: string) => (noms.get(cle) ?? cle).split(" (")[0];

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
    <div className="rounded-xl border border-line bg-surface p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium">
          Actifs{" "}
          <span className="font-normal text-muted">
            ·{" "}
            <motion.span key={v.actifs.length} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} className="inline-block tabular-nums">
              {v.actifs.length}
            </motion.span>
          </span>
        </span>
        <motion.button
          type="button"
          onClick={() => setOuvert(true)}
          whileTap={{ scale: 0.96 }}
          className="flex items-center gap-1.5 rounded-lg bg-accent-soft px-2.5 py-1.5 text-xs font-semibold text-accent-ink transition hover:brightness-95"
        >
          <SlidersHorizontal className="size-3.5" aria-hidden />
          Choisir les actifs
        </motion.button>
      </div>

      {perso ? (
        <ul className="mt-2.5 flex flex-col">
          <AnimatePresence initial={false}>
            {v.actifs.map((cle) => (
              <motion.li key={cle} layout initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
                <div className="flex items-center justify-between gap-2 py-1">
                  <span className="min-w-0 truncate text-sm">{court(cle)}</span>
                  <span className="flex shrink-0 items-center gap-1.5 text-sm text-muted">
                    <input
                      type="number"
                      min={0}
                      max={100}
                      aria-label={`Part de ${court(cle)} en pourcentage`}
                      value={v.allocations[cle] ?? 0}
                      onChange={(e) => onChange({ ...v, allocations: { ...v.allocations, [cle]: Math.min(100, Math.max(0, Math.round(Number(e.target.value)))) } })}
                      className="w-16 rounded-lg border border-line bg-surface px-2 py-1 text-right text-sm text-ink tabular-nums outline-none focus:border-accent"
                    />
                    %
                    <button
                      type="button"
                      onClick={() => retirer(cle)}
                      aria-label={`Retirer ${court(cle)}`}
                      className="grid size-6 place-items-center rounded-md text-muted transition hover:bg-surface-2 hover:text-loss"
                    >
                      <X className="size-3.5" aria-hidden />
                    </button>
                  </span>
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
          <li className="mt-1.5 flex items-center justify-between border-t border-line pt-2 text-sm">
            <span className={totalPerso === 100 ? "text-gain" : "text-warn"}>
              Total : <strong className="tabular-nums">{totalPerso} %</strong> {totalPerso === 100 ? "✓" : "(doit faire 100 %)"}
            </span>
            <button type="button" onClick={repartirEgalement} className="text-sm font-medium text-accent-ink hover:underline">
              Répartir également
            </button>
          </li>
        </ul>
      ) : (
        <ul className="mt-2.5 flex flex-wrap gap-1.5" aria-label="Actifs sélectionnés">
          <AnimatePresence initial={false}>
            {tries.map((cle) => {
              const part = parts.get(cle);
              return (
                <motion.li
                  key={cle}
                  layout
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={RESSORT}
                  className={`flex items-center gap-1 rounded-full border py-1 pl-2.5 pr-1 text-xs ${part ? "border-accent/40 bg-accent-soft/50" : "border-line text-ink-2"}`}
                  title={part ? `${noms.get(cle) ?? cle} : ${Math.round(part * 100)} % du capital` : `${noms.get(cle) ?? cle} : analysé à titre de comparaison (hors profil)`}
                >
                  <span className="font-medium">{court(cle)}</span>
                  {part ? <span className="tabular-nums text-accent-ink">{Math.round(part * 100)} %</span> : null}
                  <button
                    type="button"
                    onClick={() => retirer(cle)}
                    aria-label={`Retirer ${court(cle)}`}
                    className="grid size-5 place-items-center rounded-full text-muted transition hover:bg-surface hover:text-loss"
                  >
                    <X className="size-3" aria-hidden />
                  </button>
                </motion.li>
              );
            })}
          </AnimatePresence>
        </ul>
      )}
      {!perso && v.actifs.some((a) => !parts.get(a)) && (
        <p className="mt-2 text-[11px] leading-relaxed text-muted">Les étiquettes sans pourcentage ne font pas partie du profil : elles sont analysées à titre de comparaison.</p>
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
