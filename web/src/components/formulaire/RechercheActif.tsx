"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Loader2, Search } from "lucide-react";
import { ErreurApi, lireActifPerso, rechercherActifs, type ActifPerso, type ResultatRecherche } from "@/lib/api";
import { champ } from "./styles";

type Props = {
  dejaPresents: ActifPerso[];
  max: number;
  onAjout: (a: ActifPerso) => void;
};

/**
 * Recherche d'un actif par son nom (« Apple », « Total », « ETF or »...) avec suggestions.
 * Un clic reutilise le mecanisme d'ajout de ticker perso (lireActifPerso) : le prix et la
 * volatilite sont calibres, l'IA estime le choc par analogie.
 */
export function RechercheActif({ dejaPresents, max, onAjout }: Props) {
  const id = useId();
  const [saisie, setSaisie] = useState("");
  const [resultats, setResultats] = useState<ResultatRecherche[]>([]);
  const [ouvert, setOuvert] = useState(false);
  const [actif, setActif] = useState(-1);
  const [recherche, setRecherche] = useState(false);
  const [ajout, setAjout] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);
  const racine = useRef<HTMLDivElement>(null);

  // Debounce 300 ms ; `courant` ignore les reponses d'une saisie depassee.
  useEffect(() => {
    const q = saisie.trim();
    if (q.length < 2) return;
    let courant = true;
    const t = setTimeout(() => {
      setRecherche(true);
      setActif(-1);
      rechercherActifs(q)
        .then((r) => {
          if (!courant) return;
          setResultats(r.resultats);
          setInfo(r.resultats.length === 0 ? (r.message ?? `Aucun résultat pour « ${q} ». Essayez le nom de la société ou son symbole.`) : null);
          setOuvert(true);
        })
        .catch(() => {
          if (!courant) return;
          setResultats([]);
          setInfo("La recherche est indisponible. Saisissez le symbole Yahoo ci-dessous.");
          setOuvert(true);
        })
        .finally(() => courant && setRecherche(false));
    }, 300);
    return () => {
      courant = false;
      clearTimeout(t);
    };
  }, [saisie]);

  useEffect(() => {
    const surClic = (e: MouseEvent) => !racine.current?.contains(e.target as Node) && setOuvert(false);
    document.addEventListener("mousedown", surClic);
    return () => document.removeEventListener("mousedown", surClic);
  }, []);

  async function choisir(r: ResultatRecherche) {
    if (dejaPresents.some((a) => a.ticker === r.symbole)) return setErreur(`${r.symbole} est déjà dans la liste.`);
    if (dejaPresents.length >= max) return setErreur(`Au plus ${max} actifs personnalisés.`);
    setAjout(r.symbole);
    setErreur(null);
    try {
      onAjout(await lireActifPerso(r.symbole));
      setSaisie("");
      setResultats([]);
      setOuvert(false);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : `${r.symbole} n'a pas pu être ajouté.`);
    } finally {
      setAjout(null);
    }
  }

  function surTouche(e: React.KeyboardEvent) {
    if (e.key === "Escape" && ouvert) {
      e.preventDefault();
      e.stopPropagation(); // ne ferme pas la fenetre du selecteur
      setOuvert(false);
    } else if (e.key === "ArrowDown" && resultats.length) {
      e.preventDefault();
      setOuvert(true);
      setActif((i) => (i + 1) % resultats.length);
    } else if (e.key === "ArrowUp" && resultats.length) {
      e.preventDefault();
      setActif((i) => (i <= 0 ? resultats.length - 1 : i - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (ouvert && actif >= 0 && resultats[actif]) choisir(resultats[actif]);
    }
  }

  const listeId = `${id}-liste`;
  const afficherListe = ouvert && (resultats.length > 0 || info !== null);

  return (
    <div ref={racine} className="mt-6">
      <label htmlFor={`${id}-champ`} className="text-sm font-medium">
        Rechercher une action, un ETF, une crypto…
      </label>
      <div className="relative mt-2">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
        <input
          id={`${id}-champ`}
          role="combobox"
          aria-expanded={afficherListe}
          aria-controls={listeId}
          aria-autocomplete="list"
          aria-activedescendant={actif >= 0 ? `${id}-opt-${actif}` : undefined}
          autoComplete="off"
          value={saisie}
          maxLength={40}
          onChange={(e) => {
            setSaisie(e.target.value);
            if (e.target.value.trim().length < 2) {
              setResultats([]);
              setInfo(null);
              setRecherche(false);
              setActif(-1);
            }
          }}
          onFocus={() => (resultats.length || info) && setOuvert(true)}
          onKeyDown={surTouche}
          placeholder="Ex. Apple, LVMH, Total, ETF or…"
          className={`${champ} py-2 pl-9 pr-9`}
        />
        {(recherche || ajout) && <Loader2 className="absolute right-3 top-1/2 size-4 -translate-y-1/2 animate-spin text-muted" aria-hidden />}
        <ul
          id={listeId}
          role="listbox"
          aria-label="Suggestions d'actifs"
          hidden={!afficherListe}
          className="absolute inset-x-0 top-full z-10 mt-1 max-h-64 overflow-y-auto rounded-tuile border border-line bg-surface shadow-lg"
        >
          {resultats.map((r, i) => (
            <li
              key={r.symbole}
              id={`${id}-opt-${i}`}
              role="option"
              aria-selected={i === actif}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => choisir(r)}
              onMouseEnter={() => setActif(i)}
              className={`flex cursor-pointer items-center gap-3 px-3 py-2 ${i === actif ? "bg-accent-soft" : "hover:bg-surface-2"}`}
            >
              <span className="w-20 shrink-0 truncate font-mono text-aide font-semibold">{r.symbole}</span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm">{r.nom}</span>
                <span className="block truncate text-xs text-muted">
                  {r.type}
                  {r.bourse ? ` · ${r.bourse}` : ""}
                  {r.devise ? ` · ${r.devise}` : ""}
                </span>
              </span>
            </li>
          ))}
          {resultats.length === 0 && info && (
            <li role="presentation" aria-live="polite" className="px-3 py-3 text-aide text-muted">
              {info}
            </li>
          )}
        </ul>
      </div>
      <p className="mt-1.5 text-xs text-muted">Estimation par analogie, moins fiable que les 23 actifs de référence.</p>
      <p className="sr-only" role="status" aria-live="polite">
        {recherche ? "Recherche en cours" : ouvert && resultats.length ? `${resultats.length} suggestions` : ""}
      </p>
      {erreur && (
        <p role="alert" className="mt-1.5 text-aide text-loss">
          {erreur}
        </p>
      )}
    </div>
  );
}
