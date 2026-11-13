"use client";

import { useLayoutEffect, useRef } from "react";

const CHIFFRES_MAX = 9;
const formater = (n: number) => (n ? n.toLocaleString("fr-FR") : "");

/**
 * Champ de montant en euros affiche avec les espaces francaises (10 000), clavier numerique
 * sur mobile, sans les petites fleches du navigateur. Le curseur reste a sa place pendant la frappe.
 */
export function ChampMontant({
  id,
  valeur,
  onChange,
  max,
  className = "",
  ...reste
}: {
  id: string;
  valeur: number;
  onChange: (n: number) => void;
  max: number;
  className?: string;
  "aria-describedby"?: string;
  "aria-invalid"?: boolean;
}) {
  const champ = useRef<HTMLInputElement>(null);
  // Nombre de chiffres a gauche du curseur, a restaurer apres le reformatage.
  const chiffresAvantCurseur = useRef<number | null>(null);

  useLayoutEffect(() => {
    const el = champ.current;
    const n = chiffresAvantCurseur.current;
    if (!el || n == null || document.activeElement !== el) return;
    chiffresAvantCurseur.current = null;
    let position = 0;
    for (let vus = 0; position < el.value.length && vus < n; position++) if (/\d/.test(el.value[position])) vus++;
    el.setSelectionRange(position, position);
  });

  return (
    <div className="relative">
      <input
        ref={champ}
        id={id}
        type="text"
        inputMode="numeric"
        autoComplete="off"
        value={formater(valeur)}
        onChange={(e) => {
          const brut = e.target.value;
          chiffresAvantCurseur.current = brut.slice(0, e.target.selectionStart ?? brut.length).replace(/\D/g, "").length;
          const chiffres = brut.replace(/\D/g, "").slice(0, CHIFFRES_MAX);
          onChange(Math.min(max, Number(chiffres || 0)));
        }}
        className={`${className} pr-9 tabular-nums`}
        {...reste}
      />
      <span className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-sm text-muted" aria-hidden>
        €
      </span>
    </div>
  );
}
