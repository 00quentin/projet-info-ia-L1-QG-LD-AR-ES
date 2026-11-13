import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Apparition } from "@/components/motion/Apparition";
import { dateMiseAJour, MISE_A_JOUR } from "@/contenu/legal";
import { SommaireLateral, SommaireMobile, type EntreeSommaire } from "./Sommaire";

type Props = {
  icone: LucideIcon;
  etiquette: string;
  titre: string;
  chapeau: ReactNode;
  /** Parties de la page, dans l'ordre (sommaire). */
  sommaire: EntreeSommaire[];
  /** Affiche la date de dernière mise à jour (pages juridiques). */
  avecMiseAJour?: boolean;
  children: ReactNode;
};

/** Gabarit des pages de texte long : en-tête, colonne de lecture et sommaire collant. */
export function PageLegale({ icone: Icone, etiquette, titre, chapeau, sommaire, avecMiseAJour = true, children }: Props) {
  return (
    <div className="mx-auto max-w-[1100px] px-4 pb-20 pt-10 sm:px-6 sm:pt-14">
      <Apparition className="max-w-[46rem]">
        <p className="inline-flex items-center gap-1.5 rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent-ink">
          <Icone className="size-3.5" aria-hidden />
          {etiquette}
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">{titre}</h1>
        <div className="mt-4 max-w-[37rem] text-[17px] leading-[1.7] text-ink-2 sm:text-lg">{chapeau}</div>
        {avecMiseAJour && (
          <p className="mt-4 text-sm text-muted">
            Dernière mise à jour : <time dateTime={MISE_A_JOUR}>{dateMiseAJour()}</time>
          </p>
        )}
      </Apparition>

      <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-[minmax(0,1fr)_15rem] lg:gap-14">
        <div className="flex min-w-0 max-w-[46rem] flex-col gap-12">
          <SommaireMobile entrees={sommaire} />
          {children}
        </div>
        <aside className="hidden lg:block">
          <SommaireLateral entrees={sommaire} />
        </aside>
      </div>
    </div>
  );
}
