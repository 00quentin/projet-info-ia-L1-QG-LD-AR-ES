"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Check, Loader2, Plus, Search, X } from "lucide-react";
import { ErreurApi, lireActifPerso, lireMarchesPartages, type ActifPerso, type Catalogue, type CoursMarche } from "@/lib/api";
import { pourcentSigne } from "@/lib/format";
import { descriptionActif, libelleCategorie, nomCourt } from "@/contenu/actifs";
import { champ } from "./styles";
import { AideInfo, Infobulle } from "@/components/ui/Infobulle";
import { Prix, uniteCours } from "@/components/ui/Prix";
import { DUREE, EASE_SORTIE, RESSORT } from "@/components/motion/transitions";

const TICKERS_PERSO_MAX = 10;
const TOUTES = "Toutes";
const CATEGORIE_PERSO = "Actifs personnalisés";

/** Minuscules sans accents : "Pétrole" se trouve en tapant "petrole". */
const normaliser = (t: string) => t.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

type Props = {
  catalogue: Catalogue;
  actifs: string[];
  actifsPerso: ActifPerso[];
  autoriserActifsPerso: boolean;
  /** Actifs du profil choisi (marques d'un point, legende en tete de fenetre). */
  actifsDuProfil: Set<string>;
  /** Nom court du profil type choisi, ou null (profil personnalise). */
  nomProfil?: string | null;
  onValider: (actifs: string[], actifsPerso: ActifPerso[]) => void;
  onFermer: () => void;
};

type Ligne = {
  cle: string;
  /** Nom court affiche (nom officiel pour un actif personnalise). */
  nom: string;
  officiel: string;
  /** Description francaise, ou le ticker tape par l'utilisateur pour un actif personnalise. */
  description: string | null;
  ticker: string;
  perso: boolean;
  devise: string | null;
  prixConnu?: number;
};

/**
 * Fenetre de choix des actifs : recherche, filtre par categorie, cours du jour,
 * selection par categorie, ajout d'un ticker Yahoo. Les changements ne sont
 * appliques qu'a la validation (Annuler laisse le portefeuille intact).
 */
export function SelecteurActifs({ catalogue, actifs, actifsPerso, autoriserActifsPerso, actifsDuProfil, nomProfil = null, onValider, onFermer }: Props) {
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
    const liste: { nom: string; libelle: string; lignes: Ligne[] }[] = catalogue.categories.map((c) => ({
      nom: c.nom,
      libelle: libelleCategorie(c.nom),
      lignes: c.actifs.map((a) => ({
        cle: a.cle,
        nom: nomCourt(a.cle, a.nom),
        officiel: a.nom,
        description: descriptionActif(a.cle),
        ticker: a.ticker ?? "",
        perso: false,
        devise: a.devise,
      })),
    }));
    if (autoriserActifsPerso && perso.length)
      liste.push({
        nom: CATEGORIE_PERSO,
        libelle: libelleCategorie(CATEGORIE_PERSO),
        lignes: perso.map((a) => ({ cle: a.cle, nom: a.nom, officiel: a.nom, description: a.ticker, ticker: a.ticker, perso: true, devise: a.devise, prixConnu: a.prix })),
      });
    return liste;
  }, [catalogue, perso, autoriserActifsPerso]);

  const filtre = normaliser(recherche.trim());
  const visibles = categories
    .filter((c) => categorie === TOUTES || c.nom === categorie)
    .map((c) => ({ ...c, lignes: c.lignes.filter((a) => !filtre || normaliser(`${a.nom} ${a.officiel} ${a.description ?? ""} ${a.ticker} ${c.libelle}`).includes(filtre)) }))
    .filter((c) => c.lignes.length > 0);

  const basculer = (cle: string) => setSelection((s) => (s.includes(cle) ? s.filter((x) => x !== cle) : [...s, cle]));
  function basculerCategorie(cles: string[]) {
    const toutes = cles.every((c) => selection.includes(c));
    setSelection((s) => (toutes ? s.filter((x) => !cles.includes(x)) : Array.from(new Set([...s, ...cles]))));
  }

  const avecProfil = nomProfil && actifsDuProfil.size > 0;

  return (
    <motion.div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: DUREE.normale }}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onFermer} aria-hidden />
      <motion.div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titre-selecteur"
        initial={{ opacity: 0, y: 32 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 24 }}
        transition={RESSORT}
        className="relative flex max-h-[92dvh] w-full max-w-3xl flex-col overflow-hidden rounded-t-carte border border-line bg-surface shadow-2xl sm:max-h-[85dvh] sm:rounded-carte"
      >
        <div className="shrink-0 border-b border-line px-4 pb-3 pt-4 sm:px-6 sm:pt-5">
          <div className="flex items-center justify-between gap-3">
            <h2 id="titre-selecteur" className="text-section font-semibold tracking-tight">
              Choisir les actifs
            </h2>
            <button type="button" onClick={onFermer} aria-label="Fermer sans enregistrer" className="grid size-8 place-items-center rounded-controle text-muted transition-colors hover:bg-surface-2 hover:text-ink">
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
              placeholder="Rechercher : or, nasdaq, bitcoin, obligations…"
              aria-label="Rechercher un actif"
              className={`${champ} pl-9`}
            />
          </div>
          <div role="radiogroup" aria-label="Catégorie" className="-mx-1 mt-3 flex gap-1 overflow-x-auto px-1 pb-0.5 [scrollbar-width:none]">
            {[{ nom: TOUTES, libelle: TOUTES }, ...categories].map(({ nom, libelle }) => {
              const choisi = categorie === nom;
              return (
                <button
                  key={nom}
                  type="button"
                  role="radio"
                  aria-checked={choisi}
                  onClick={() => setCategorie(nom)}
                  className={`relative shrink-0 rounded-full px-3 py-1.5 text-aide font-medium transition-colors ${choisi ? "text-accent-ink" : "text-ink-2 hover:text-ink"}`}
                >
                  {choisi && <motion.span layoutId="selecteur-categorie" className="absolute inset-0 rounded-full bg-accent-soft" transition={RESSORT} />}
                  <span className="relative">{libelle}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4 sm:px-6">
          {(avecProfil || cours.size > 0) && (
            <div className="mb-4 flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-xs text-muted">
              {avecProfil ? (
                <span className="flex items-center gap-1.5">
                  <span className="size-1.5 rounded-full bg-accent" aria-hidden />
                  Dans le profil {nomProfil}
                </span>
              ) : (
                <span />
              )}
              {cours.size > 0 && <span>Cours de clôture · variation du jour</span>}
            </div>
          )}
          {visibles.length === 0 && (
            <p className="py-10 text-center text-sm text-muted">
              Aucun actif ne correspond à « {recherche} ».{autoriserActifsPerso ? " Ajoutez-le par son ticker Yahoo ci-dessous." : ""}
            </p>
          )}
          <div className="flex flex-col gap-6">
            {visibles.map((c) => {
              const cles = c.lignes.map((a) => a.cle);
              const toutes = cles.every((k) => selection.includes(k));
              return (
                <section key={c.nom} aria-label={c.libelle}>
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{c.libelle}</h3>
                    <button type="button" onClick={() => basculerCategorie(cles)} className="text-aide font-medium text-accent-ink hover:underline">
                      {toutes ? "Tout retirer" : "Tout sélectionner"}
                    </button>
                  </div>
                  <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {c.lignes.map((a) => (
                      <li key={a.cle} className="flex">
                        <LigneActif ligne={a} coche={selection.includes(a.cle)} dansProfil={actifsDuProfil.has(a.cle)} cours={cours.get(a.cle)} onBasculer={() => basculer(a.cle)} />
                      </li>
                    ))}
                  </ul>
                </section>
              );
            })}
          </div>
          {autoriserActifsPerso && (
            <AjoutTicker
              suggestion={visibles.length === 0 ? recherche : ""}
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

        <div className="flex shrink-0 items-center justify-between gap-3 border-t border-line bg-surface px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:px-6">
          <span className="text-sm text-ink-2" aria-live="polite">
            <strong className="font-semibold text-ink tabular-nums">{selection.length}</strong> actif{selection.length > 1 ? "s" : ""} sélectionné{selection.length > 1 ? "s" : ""}
          </span>
          <div className="flex gap-2">
            <button type="button" onClick={onFermer} className="rounded-controle px-3.5 py-2 text-sm font-medium text-ink-2 transition-colors hover:bg-surface-2 hover:text-ink">
              Annuler
            </button>
            <motion.button
              type="button"
              whileTap={{ scale: 0.97 }}
              disabled={selection.length === 0}
              onClick={() => onValider(selection, perso.filter((a) => selection.includes(a.cle)))}
              className="rounded-controle bg-accent px-4 py-2 text-sm font-semibold text-on-accent transition-[filter,opacity] hover:brightness-110 disabled:opacity-50"
            >
              Valider
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function LigneActif({ ligne: a, coche, dansProfil, cours, onBasculer }: { ligne: Ligne; coche: boolean; dansProfil: boolean; cours?: CoursMarche; onBasculer: () => void }) {
  const unite = uniteCours(a.cle, cours?.devise ?? a.devise);
  const valeur = cours?.prix ?? a.prixConnu;
  const bouton = (
    <button
      type="button"
      role="checkbox"
      aria-checked={coche}
      onClick={onBasculer}
      className={`flex w-full items-start gap-3 rounded-tuile border px-3 py-2.5 text-left transition-colors ${coche ? "border-accent bg-accent-soft/60" : "border-line hover:border-line-strong hover:bg-surface-2/60"}`}
    >
      <span className={`mt-0.5 grid size-5 shrink-0 place-items-center rounded-[calc(var(--radius-controle)/2)] border transition-colors ${coche ? "border-accent bg-accent text-on-accent" : "border-line-strong bg-surface"}`}>
        <AnimatePresence initial={false}>
          {coche && (
            <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} transition={RESSORT}>
              <Check className="size-3.5" strokeWidth={3} aria-hidden />
            </motion.span>
          )}
        </AnimatePresence>
      </span>
      <span className="min-w-0 flex-1">
        <span className="flex items-center gap-1.5 text-sm font-medium leading-snug">
          {a.nom}
          {dansProfil && (
            <>
              <span className="size-1.5 shrink-0 rounded-full bg-accent" aria-hidden />
              <span className="sr-only">(dans votre profil)</span>
            </>
          )}
        </span>
        {a.description && <span className={`mt-0.5 block text-aide leading-snug text-muted ${a.perso ? "font-mono" : ""}`}>{a.description}</span>}
      </span>
      {valeur != null && (
        <span className="shrink-0 text-right leading-snug">
          <Prix valeur={valeur} unite={unite} className="block text-aide font-medium text-ink" />
          {cours && <span className={`block text-xs tabular-nums ${cours.variation_pct >= 0 ? "text-gain" : "text-loss"}`}>{pourcentSigne(cours.variation_pct, 2)}</span>}
        </span>
      )}
    </button>
  );
  // Le code Yahoo et le nom officiel restent consultables au survol ou au focus clavier.
  if (a.perso || !a.ticker) return bouton;
  return (
    <Infobulle className="flex w-full" texte={`${a.officiel} · cotation Yahoo Finance ${a.ticker}`}>
      {bouton}
    </Infobulle>
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
    <div className="mt-6 rounded-tuile border border-dashed border-line-strong p-3.5">
      <div className="flex items-center gap-1.5">
        <p className="text-sm font-medium">Une action, un ETF ou une crypto absent de la liste ?</p>
        <AideInfo
          libelle="Comment ajouter un actif"
          texte="Saisissez son ticker Yahoo Finance : TSLA, NVDA, AIR.PA, MC.PA, BTC-USD… Le prix et la volatilité sont calibrés sur un an de cours."
        />
      </div>
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
          placeholder={suggestion.trim() ? suggestion.trim().toUpperCase() : "Ticker Yahoo (ex. TSLA, MC.PA)"}
          aria-label="Ticker Yahoo Finance à ajouter"
          maxLength={20}
          className={`${champ} py-2 font-mono uppercase placeholder:font-sans placeholder:normal-case`}
        />
        <motion.button
          type="button"
          onClick={ajouter}
          disabled={enCours || !(ticker || suggestion).trim()}
          whileTap={{ scale: 0.97 }}
          className="flex shrink-0 items-center gap-1.5 rounded-controle border border-line px-3 text-sm font-medium transition-colors hover:border-accent hover:text-accent-ink disabled:opacity-50"
        >
          {enCours ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Plus className="size-4" aria-hidden />}
          Ajouter
        </motion.button>
      </div>
      <AnimatePresence>
        {erreur && (
          <motion.p role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: DUREE.rapide, ease: EASE_SORTIE }} className="mt-1.5 text-aide text-loss">
            {erreur}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}
