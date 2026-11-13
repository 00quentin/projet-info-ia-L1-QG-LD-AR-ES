"use client";

import { useId } from "react";
import { AideInfo } from "./Infobulle";

/**
 * Interrupteur on/off. `aide` s'affiche sous le libelle (une ligne courte) ;
 * `info` part dans une infobulle (i) pour les explications plus longues.
 */
export function Interrupteur({ actif, onChange, libelle, aide, info }: { actif: boolean; onChange: (v: boolean) => void; libelle: string; aide?: string; info?: string }) {
  const id = useId();
  return (
    <div className="flex items-start justify-between gap-4 py-2.5">
      <div className="min-w-0">
        <div className="flex items-center gap-1.5">
          <label htmlFor={id} className="cursor-pointer text-sm font-medium">
            {libelle}
          </label>
          {info && <AideInfo texte={info} libelle={`À propos : ${libelle}`} />}
        </div>
        {aide && <p className="mt-0.5 text-aide leading-snug text-muted">{aide}</p>}
      </div>
      <label className="relative mt-0.5 shrink-0 cursor-pointer">
        <input id={id} type="checkbox" role="switch" checked={actif} onChange={(e) => onChange(e.target.checked)} className="peer sr-only" />
        <span className="block h-5 w-9 rounded-full bg-line-strong transition-colors peer-checked:bg-accent peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-accent" />
        <span className="absolute left-0.5 top-0.5 size-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4" />
      </label>
    </div>
  );
}
