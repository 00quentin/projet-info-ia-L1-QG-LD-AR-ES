"use client";

import { Compass, Crosshair, MoveHorizontal, Ruler, Scale } from "lucide-react";
import type { ReactNode } from "react";
import type { ValidationIA } from "@/lib/validation";
import { nombre } from "@/lib/format";
import { Carte } from "@/components/ui/Carte";
import { Cascade, ElementCascade } from "@/components/motion/Apparition";
import { NombreAnime } from "@/components/motion/NombreAnime";
import { lectureGlobale, points } from "./outils";

function Tuile({ icone, libelle, valeur, aide }: { icone: ReactNode; libelle: string; valeur: ReactNode; aide: ReactNode }) {
  return (
    <ElementCascade className="flex flex-col gap-1.5 rounded-xl border border-line bg-surface-2/50 p-4">
      <span className="flex items-center gap-2 text-xs font-medium text-ink-2">
        <span className="grid size-6 place-items-center rounded-lg bg-accent-soft text-accent-ink">{icone}</span>
        {libelle}
      </span>
      <span className="text-3xl font-semibold tracking-tight text-ink">{valeur}</span>
      <span className="text-xs leading-relaxed text-muted">{aide}</span>
    </ElementCascade>
  );
}

/** Score global : quatre chiffres et leur lecture en clair. */
export function ChiffresCles({ v }: { v: ValidationIA }) {
  const g = v.global;
  return (
    <Carte className="p-5 sm:p-6">
      <Cascade className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        <Tuile
          icone={<Compass className="size-3.5" aria-hidden />}
          libelle="Bon sens de variation"
          valeur={<NombreAnime valeur={(g.part_sens_correct ?? 0) * 100} depuis={0} format={(x) => `${nombre(x, 0)} %`} />}
          aide={`${g.nb_sens_corrects} mouvements sur ${g.nb_sens_comptes} : hausse prévue et observée, ou baisse prévue et observée.`}
        />
        <Tuile
          icone={<Crosshair className="size-3.5" aria-hidden />}
          libelle="Erreur moyenne"
          valeur={<NombreAnime valeur={g.erreur_moyenne_pts ?? 0} depuis={0} format={(x) => points(x)} />}
          aide={`Écart moyen entre l’estimation et la réalité, actif par actif (médiane ${points(g.erreur_mediane_pts)}).`}
        />
        <Tuile
          icone={<Scale className="size-3.5" aria-hidden />}
          libelle="Corrélation estimé / réel"
          valeur={<NombreAnime valeur={g.correlation ?? 0} depuis={0} format={(x) => nombre(x, 2)} />}
          aide="De −1 à 1 : à 1, les estimations suivent parfaitement les vrais mouvements ; à 0, aucun lien."
        />
        <Tuile
          icone={<Ruler className="size-3.5" aria-hidden />}
          libelle="Taille des chocs"
          valeur={<NombreAnime valeur={g.ratio_amplitude ?? 0} depuis={0} format={(x) => `×${nombre(x, 2)}`} />}
          aide="Ampleur des chocs de l’IA rapportée aux vrais mouvements : sous 1, elle est trop prudente."
        />
        {g.part_dans_fourchette != null && (
          <Tuile
            icone={<MoveHorizontal className="size-3.5" aria-hidden />}
            libelle="Dans la fourchette"
            valeur={<NombreAnime valeur={g.part_dans_fourchette * 100} depuis={0} format={(x) => `${nombre(x, 0)} %`} />}
            aide={`${g.nb_dans_fourchette} vrais mouvements sur ${g.nb_fourchettes} tombent entre le bas et le haut estimés (largeur moyenne ${points(g.largeur_moyenne_pts ?? null)}).`}
          />
        )}
      </Cascade>
      <div className="mt-5 flex flex-col gap-2 border-t border-line pt-4 text-[15px] leading-relaxed text-ink-2">
        {lectureGlobale(v).map((phrase) => (
          <p key={phrase}>{phrase}</p>
        ))}
        <p className="text-xs text-muted">
          {g.nb_crises} crises · {g.nb_actifs} comparaisons actif par actif · en euros, comme le backtest.
        </p>
      </div>
    </Carte>
  );
}
