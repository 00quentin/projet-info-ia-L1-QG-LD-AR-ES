"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Check, Loader2, Plus, Search, X } from "lucide-react";
import { ErreurApi, lireActifPerso, lireMarchesPartages, type ActifPerso, type Catalogue, type CoursMarche } from "@/lib/api";
import { pourcent, prix } from "@/lib/format";
import { champ } from "./styles";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

const TICKERS_PERSO_MAX = 10;
const TOUTES = "Toutes";

/** Minuscules sans accents : "Pétrole" se trouve en tapant "petrole". */
const normaliser = (t: string) => t.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

type Props = {
  catalogue: Catalogue;
  actifs: string[];
  actifsPerso: ActifPerso[];
  autoriserActifsPerso: boolean;
  /** Actifs du profil choisi (marques "dans le profil"). */
  actifsDuProfil: Set<string>;
  onValider: (actifs: string[], actifsPerso: ActifPerso[]) => void;
  onFermer: () => void;
};

/**
 * Fenetre de choix des actifs : recherche, filtre par categorie, cours du jour,
 * selection par categorie, ajout d'un ticker Yahoo. Les changements ne sont
 * appliques qu'a la validation (Annuler laisse le portefeuille intact).
 */
export function SelecteurActifs({ catalogue, actifs, actifsPerso, autoriserActifsPerso, actifsDuProfil, onValider, onFermer }: Props) {
  const [selection, setSelection] = useState<string[]>(actifs);
  const [perso, setPerso] = useState<ActifPerso[]>(actifsPerso);
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState(TOUTES);
  const [cours, setCours] = useState<Map<string, CoursMarche>>(new Map());
  const champRecherche = useRef<HTMLInputElement>(null);
  const focusPrecedent = useRef<Element | null>(null);

  // Le parent passe souvent une fonction recreee a chaque rendu : on la lit via une ref
  // pour que l'effet ci-dessous (focus, blocage du defilement) ne s'execute qu'une fois.
  const fermerRef = useRef(onFermer);
  useEffect(() => {
    fermerRef.current = onFermer;
  });

  useEffect(() => {
    focusPrecedent.current = document.activeElement;
    champRecherche.current?.focus();
    const surTouche = (e: KeyboardEvent) => e.key === "Escape" && fermerRef.current();
    window.addEventListener("keydown", surTouche);
    const avant = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    let actif = true;
    lireMarchesPartages()
      .then((m) => actif && setCours(new Map(m.actifs.map((c) => [c.cle, c]))))
      .catch(() => undefined); // les cours sont un plus : la liste reste utilisable sans
    return () => {
      actif = false;
      window.removeEventListener("keydown", surTouche);
      document.body.style.overflow = avant;
      (focusPrecedent.current as HTMLElement | null)?.focus?.();
    };
  }, []);

  const categories = useMemo(() => {
    const liste = catalogue.categories.map((c) => ({ nom: c.nom, actifs: c.actifs.map((a) => ({ cle: a.cle, nom: a.nom, ticker: a.ticker ?? "" })) }));
    if (autoriserActifsPerso && perso.length) liste.push({ nom: "Actifs personnalisés", actifs: perso.map((a) => ({ cle: a.cle, nom: a.nom, ticker: a.ticker })) });
    return liste;
  }, [catalogue, perso, autoriserActifsPerso]);

  const filtre = normaliser(recherche.trim());
  const visibles = categories
    .filter((c) => categorie === TOUTES || c.nom === categorie)
    .map((c) => ({ ...c, actifs: c.actifs.filter((a) => !filtre || normaliser(`${a.nom} ${a.ticker} ${c.nom}`).includes(filtre)) }))
    .filter((c) => c.actifs.length > 0);

  const basculer = (cle: string) => setSelection((s) => (s.includes(cle) ? s.filter((x) => x !== cle) : [...s, cle]));
  function basculerCategorie(cles: string[]) {
    const toutes = cles.every((c) => selection.includes(c));
    setSelection((s) => (toutes ? s.filter((x) => !cles.includes(x)) : Array.from(new Set([...s, ...cles]))));
  }

  return (
    <motion.div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onFermer} aria-hidden />
      <motion.div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titre-selecteur"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 30 }}
        transition={RESSORT}
        className="relative flex max-h-[92dvh] w-full max-w-2xl flex-col overflow-hidden rounded-t-2xl border border-line bg-surface shadow-2xl sm:max-h-[85dvh] sm:rounded-2xl"
      >
        <div className="shrink-0 border-b border-line p-4 sm:p-5">
          <div className="flex items-center justify-between gap-3">
            <h2 id="titre-selecteur" className="text-lg font-semibold tracking-tight">
              Choisir les actifs
            </h2>
            <button type="button" onClick={onFermer} aria-label="Fermer sans enregistrer" className="grid size-8 place-items-center rounded-lg text-muted transition hover:bg-surface-2 hover:text-ink">
              <X className="size-4" aria-hidden />
            </button>
          </div>
          <div className="relative mt-3">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
            <input
              ref={champRecherche}
              type="search"
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              placeholder="Rechercher : or, nasdaq, BTC, obligations…"
              aria-label="Rechercher un actif"
              className={`${champ} pl-9`}
            />
          </div>
          <div role="radiogroup" aria-label="Catégorie" className="-mx-1 mt-3 flex gap-1 overflow-x-auto px-1 pb-0.5 [scrollbar-width:none]">
            {[TOUTES, ...categories.map((c) => c.nom)].map((nom) => {
              const choisi = categorie === nom;
              return (
                <button
                  key={nom}
                  type="button"
                  role="radio"
                  aria-checked={choisi}
                  onClick={() => setCategorie(nom)}
                  className={`relative shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${choisi ? "text-accent-ink" : "text-ink-2 hover:text-ink"}`}
                >
                  {choisi && <motion.span layoutId="selecteur-categorie" className="absolute inset-0 rounded-full bg-accent-soft" transition={RESSORT} />}
                  <span className="relative">{nom}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-5">
          {visibles.length === 0 && <p className="py-10 text-center text-sm text-muted">Aucun actif ne correspond à « {recherche} ».{autoriserActifsPerso ? " Ajoutez-le par son ticker Yahoo ci-dessous." : ""}</p>}
          <div className="flex flex-col gap-5">
            {visibles.map((c) => {
              const cles = c.actifs.map((a) => a.cle);
              const toutes = cles.every((k) => selection.includes(k));
              return (
                <section key={c.nom} aria-label={c.nom}>
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{c.nom}</h3>
                    <button type="button" onClick={() => basculerCategorie(cles)} className="text-xs font-medium text-accent-ink hover:underline">
                      {toutes ? "Tout retirer" : "Tout sélectionner"}
                    </button>
                  </div>
                  <ul className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
                    {c.actifs.map((a) => {
                      const coche = selection.includes(a.cle);
                      const cours_ = cours.get(a.cle);
                      const hausse = (cours_?.variation_pct ?? 0) >= 0;
                      return (
                        <li key={a.cle}>
                          <motion.button
                            type="button"
                            role="checkbox"
                            aria-checked={coche}
                            onClick={() => basculer(a.cle)}
                            whileTap={{ scale: 0.98 }}
                            className={`flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition-colors ${coche ? "border-accent bg-accent-soft/60" : "border-line hover:border-line-strong"}`}
                          >
                            <span className={`grid size-5 shrink-0 place-items-center rounded-md border transition-colors ${coche ? "border-accent bg-accent text-white" : "border-line-strong"}`}>
                              <AnimatePresence>
                                {coche && (
                                  <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} transition={RESSORT}>
                                    <Check className="size-3.5" strokeWidth={3} aria-hidden />
                                  </motion.span>
                                )}
                              </AnimatePresence>
                            </span>
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-sm font-medium">{a.nom}</span>
                              <span className="flex items-center gap-1.5 text-xs text-muted">
                                {a.ticker && <span className="font-mono">{a.ticker}</span>}
                                {actifsDuProfil.has(a.cle) && <span className="rounded bg-surface-2 px-1.5 text-[10px] font-medium text-ink-2">dans le profil</span>}
                              </span>
                            </span>
                            {cours_ && (
                              <span className="shrink-0 text-right tabular-nums">
                                <span className="block text-xs font-medium">{prix(cours_.prix)}</span>
                                <span className={`block text-[11px] ${hausse ? "text-gain" : "text-loss"}`}>
                                  <span aria-hidden>{hausse ? "▲" : "▼"}</span> {pourcent(Math.abs(cours_.variation_pct), 2)}
                                </span>
                              </span>
                            )}
                          </motion.button>
                        </li>
                      );
                    })}
                  </ul>
                </section>
              );
            })}
          </div>
          {autoriserActifsPerso && (
            <AjoutTicker
              suggestion={recherche}
              dejaPresents={perso}
              onAjout={(a) => {
                setPerso((p) => [...p, a]);
                setSelection((s) => [...s, a.cle]);
                setRecherche("");
                setCategorie(TOUTES);
              }}
            />
          )}
        </div>

        <div className="flex shrink-0 items-center justify-between gap-3 border-t border-line bg-surface px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:px-5">
          <span className="text-sm text-ink-2">
            <motion.strong key={selection.length} initial={{ y: -6, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="inline-block font-semibold text-ink tabular-nums">
              {selection.length}
            </motion.strong>{" "}
            actif{selection.length > 1 ? "s" : ""} sélectionné{selection.length > 1 ? "s" : ""}
          </span>
          <div className="flex gap-2">
            <button type="button" onClick={onFermer} className="rounded-xl px-3.5 py-2 text-sm font-medium text-ink-2 transition hover:bg-surface-2">
              Annuler
            </button>
            <motion.button
              type="button"
              whileTap={{ scale: 0.97 }}
              disabled={selection.length === 0}
              onClick={() => onValider(selection, perso.filter((a) => selection.includes(a.cle)))}
              className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110 disabled:opacity-50"
            >
              Valider
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function AjoutTicker({ suggestion, dejaPresents, onAjout }: { suggestion: string; dejaPresents: ActifPerso[]; onAjout: (a: ActifPerso) => void }) {
  const [ticker, setTicker] = useState("");
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  async function ajouter() {
    const t = (ticker || suggestion).trim().toUpperCase();
    if (!t) return;
    if (dejaPresents.some((a) => a.ticker === t)) return setErreur(`${t} est déjà dans la liste.`);
    if (dejaPresents.length >= TICKERS_PERSO_MAX) return setErreur(`Au plus ${TICKERS_PERSO_MAX} actifs personnalisés.`);
    setEnCours(true);
    setErreur(null);
    try {
      onAjout(await lireActifPerso(t));
      setTicker("");
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Ticker introuvable.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <div className="mt-6 rounded-xl border border-dashed border-line-strong p-3.5">
      <p className="text-sm font-medium">Ajouter n&apos;importe quelle action, ETF ou crypto</p>
      <p className="mt-0.5 text-xs text-muted">Par son ticker Yahoo Finance : TSLA, NVDA, AIR.PA, MC.PA, BTC-USD… Le prix et la volatilité sont calibrés sur un an.</p>
      <div className="mt-2.5 flex gap-2">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              ajouter();
            }
          }}
          placeholder={suggestion.trim() ? suggestion.trim().toUpperCase() : "Ticker"}
          aria-label="Ticker Yahoo Finance à ajouter"
          maxLength={20}
          className={`${champ} py-2 uppercase placeholder:normal-case`}
        />
        <motion.button
          type="button"
          onClick={ajouter}
          disabled={enCours || !(ticker || suggestion).trim()}
          whileTap={{ scale: 0.95 }}
          className="flex shrink-0 items-center gap-1.5 rounded-xl border border-line px-3 text-sm font-medium transition hover:border-accent hover:text-accent-ink disabled:opacity-50"
        >
          {enCours ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Plus className="size-4" aria-hidden />}
          Ajouter
        </motion.button>
      </div>
      <AnimatePresence>
        {erreur && (
          <motion.p role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }} className="mt-1.5 text-xs text-loss">
            {erreur}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}
