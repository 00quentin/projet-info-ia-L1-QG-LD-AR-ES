"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronDown, Loader2, Plus, X } from "lucide-react";
import { ErreurApi, lireActifPerso, type ActifPerso, type Catalogue } from "@/lib/api";
import { champ } from "./styles";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

export const PROFIL_PERSONNALISE = "Personnalisé";
const TICKERS_PERSO_MAX = 10;

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
  const [ouvert, setOuvert] = useState(false);
  const idPanneau = useId();
  const idGroupe = useId();
  const perso = v.profil === PROFIL_PERSONNALISE;
  const totalPerso = v.actifs.reduce((s, a) => s + (v.allocations[a] ?? 0), 0);

  function choisirProfil(nom: string) {
    const profil = catalogue.profils.find((p) => p.nom === nom);
    // On ajoute les actifs du profil a la selection : sinon une partie du profil serait ignoree.
    const actifs = profil?.poids ? Array.from(new Set([...v.actifs, ...Object.keys(profil.poids)])) : v.actifs;
    maj({ profil: nom, actifs });
    if (nom === PROFIL_PERSONNALISE) setOuvert(true);
  }

  function basculerActif(cle: string) {
    maj({ actifs: v.actifs.includes(cle) ? v.actifs.filter((a) => a !== cle) : [...v.actifs, cle] });
  }

  function repartirEgalement() {
    const n = v.actifs.length;
    if (n === 0) return;
    const base = Math.floor(100 / n);
    maj({ allocations: Object.fromEntries(v.actifs.map((a, i) => [a, base + (i < 100 - base * n ? 1 : 0)])) });
  }

  const ligneActif = (cle: string, nom: string, retirer?: () => void) => {
    const coche = v.actifs.includes(cle);
    return (
      <div key={cle} className="flex items-center justify-between gap-2 py-1">
        <label className="flex min-w-0 cursor-pointer items-center gap-2.5 text-sm">
          <input type="checkbox" checked={coche} onChange={() => basculerActif(cle)} className="size-4 shrink-0 accent-(--accent)" />
          <span className="truncate">{nom}</span>
        </label>
        <span className="flex shrink-0 items-center gap-1.5">
          {perso && coche && (
            <span className="flex items-center gap-1 text-sm text-muted">
              <input
                type="number"
                min={0}
                max={100}
                aria-label={`Part de ${nom} en pourcentage`}
                value={v.allocations[cle] ?? 0}
                onChange={(e) => maj({ allocations: { ...v.allocations, [cle]: Math.min(100, Math.max(0, Math.round(Number(e.target.value)))) } })}
                className="w-16 rounded-lg border border-line bg-surface px-2 py-1 text-right text-sm text-ink tabular-nums outline-none focus:border-accent"
              />
              %
            </span>
          )}
          {retirer && (
            <button type="button" onClick={retirer} aria-label={`Retirer ${nom}`} className="grid size-6 place-items-center rounded-md text-muted transition hover:bg-surface-2 hover:text-loss">
              <X className="size-3.5" aria-hidden />
            </button>
          )}
        </span>
      </div>
    );
  };

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

      <div className="rounded-xl border border-line bg-surface">
        <button
          type="button"
          aria-expanded={ouvert}
          aria-controls={idPanneau}
          onClick={() => setOuvert((o) => !o)}
          className="flex w-full items-center justify-between px-3.5 py-2.5 text-sm font-medium"
        >
          <span>
            Actifs{" "}
            <span className="font-normal text-muted">
              ·{" "}
              <motion.span key={v.actifs.length} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} className="inline-block tabular-nums">
                {v.actifs.length}
              </motion.span>{" "}
              sélectionné{v.actifs.length > 1 ? "s" : ""}
            </span>
          </span>
          <motion.span animate={{ rotate: ouvert ? 180 : 0 }} transition={RESSORT}>
            <ChevronDown className="size-4 text-muted" aria-hidden />
          </motion.span>
        </button>
        <AnimatePresence initial={false}>
          {ouvert && (
            <motion.div
              id={idPanneau}
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: DUREE.normale, ease: EASE_SORTIE }}
              className="overflow-hidden"
            >
              <div className="flex flex-col gap-4 border-t border-line px-3.5 py-3">
                {catalogue.categories.map((c) => (
                  <div key={c.nom}>
                    <div className="mb-1.5 text-xs font-medium text-muted">{c.nom}</div>
                    <div className="flex flex-col">{c.actifs.map((a) => ligneActif(a.cle, a.nom))}</div>
                  </div>
                ))}
                {autoriserActifsPerso && (
                  <ActifsPersonnalises
                    valeur={v}
                    onChange={onChange}
                    ligne={(a) =>
                      ligneActif(a.cle, a.nom, () =>
                        maj({
                          actifsPerso: v.actifsPerso.filter((x) => x.cle !== a.cle),
                          actifs: v.actifs.filter((x) => x !== a.cle),
                        }),
                      )
                    }
                  />
                )}
                {perso && (
                  <div className="flex items-center justify-between border-t border-line pt-3 text-sm">
                    <span className={totalPerso === 100 ? "text-gain" : "text-warn"}>
                      Total : <strong className="tabular-nums">{totalPerso} %</strong> {totalPerso === 100 ? "✓" : "(doit faire 100 %)"}
                    </span>
                    <button type="button" onClick={repartirEgalement} className="text-sm font-medium text-accent-ink hover:underline">
                      Répartir également
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      {!perso && <p className="text-xs leading-relaxed text-muted">Le capital est réparti selon le profil choisi. Les autres actifs cochés sont analysés à titre de comparaison.</p>}
    </div>
  );
}

function ActifsPersonnalises({
  valeur: v,
  onChange,
  ligne,
}: {
  valeur: ValeurPortefeuille;
  onChange: (v: ValeurPortefeuille) => void;
  ligne: (a: ActifPerso) => React.ReactNode;
}) {
  const [ticker, setTicker] = useState("");
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  async function ajouter() {
    const t = ticker.trim().toUpperCase();
    if (!t) return;
    if (v.actifsPerso.some((a) => a.ticker === t)) {
      setErreur(`${t} est déjà dans la liste.`);
      return;
    }
    if (v.actifsPerso.length >= TICKERS_PERSO_MAX) {
      setErreur(`Au plus ${TICKERS_PERSO_MAX} actifs personnalisés.`);
      return;
    }
    setEnCours(true);
    setErreur(null);
    try {
      const actif = await lireActifPerso(t);
      onChange({ ...v, actifsPerso: [...v.actifsPerso, actif], actifs: [...v.actifs, actif.cle] });
      setTicker("");
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Ticker introuvable.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <div>
      <div className="mb-1.5 text-xs font-medium text-muted">Actifs personnalisés</div>
      <AnimatePresence initial={false}>
        {v.actifsPerso.map((a) => (
          <motion.div key={a.cle} initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
            {ligne(a)}
          </motion.div>
        ))}
      </AnimatePresence>
      <div className="mt-1 flex gap-2">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              ajouter();
            }
          }}
          placeholder="Ticker Yahoo : TSLA, NVDA, MC.PA…"
          aria-label="Ticker Yahoo Finance à ajouter"
          maxLength={20}
          className={`${champ} py-2 uppercase placeholder:normal-case`}
        />
        <motion.button
          type="button"
          onClick={ajouter}
          disabled={enCours || !ticker.trim()}
          whileTap={{ scale: 0.95 }}
          className="flex shrink-0 items-center gap-1.5 rounded-xl border border-line px-3 text-sm font-medium transition hover:border-accent hover:text-accent-ink disabled:opacity-50"
        >
          {enCours ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Plus className="size-4" aria-hidden />}
          Ajouter
        </motion.button>
      </div>
      <AnimatePresence>
        {erreur && (
          <motion.p role="alert" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-1.5 text-xs text-loss">
            {erreur}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}
