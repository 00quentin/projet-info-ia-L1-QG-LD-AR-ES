// Formats et lectures partagés par la page de validation.

import { nombre, pourcent } from "@/lib/format";
import type { MetriquesValidation, ValidationIA } from "@/lib/validation";

/** 10,7 pts */
export const points = (v: number | null, decimales = 1) => (v == null ? "—" : `${nombre(v, decimales)} pts`);
/** 0.944 → 94 % */
export const part = (v: number | null) => (v == null ? "—" : pourcent(v * 100, 0));
/** 0,93 */
export const coefficient = (v: number | null) => (v == null ? "—" : nombre(v, 2));

/** « 17/02/2020 → 14/04/2020 » */
export function periode(debut: string, fin: string) {
  const fr = (iso: string) => iso.split("-").reverse().join("/");
  return `${fr(debut)} → ${fr(fin)}`;
}

/** Phrase de lecture honnête, écrite à partir des chiffres (elle reste vraie si on régénère le fichier). */
export function lectureGlobale(v: ValidationIA): string[] {
  const g = v.global;
  const b = v.biais_connaissance;
  const phrases: string[] = [];
  if (g.part_sens_correct != null)
    phrases.push(
      `Sur ${g.nb_sens_comptes} mouvements nets, l’IA trouve le bon sens de variation ${g.nb_sens_corrects} fois (${part(g.part_sens_correct)}).`,
    );
  if (g.ratio_amplitude != null && g.ratio_amplitude < 0.9)
    phrases.push(
      `Elle sous-estime en revanche l’ampleur : ses chocs font en moyenne ${part(g.ratio_amplitude)} de la taille des vrais mouvements, ce qui colle à la consigne de prudence du simulateur.`,
    );
  else if (g.ratio_amplitude != null && g.ratio_amplitude > 1.1)
    phrases.push(`Elle exagère l’ampleur : ses chocs font en moyenne ${part(g.ratio_amplitude)} de la taille des vrais mouvements.`);
  if (g.part_dans_fourchette != null && g.nb_fourchettes)
    phrases.push(
      `Le vrai mouvement tombe dans la fourchette de l’IA (bas–haut) dans ${part(g.part_dans_fourchette)} des cas${
        g.part_dans_fourchette < 0.6
          ? ` seulement : ses fourchettes sont trop étroites, et ${g.nb_sorties_plus_fortes} des ${g.nb_fourchettes - (g.nb_dans_fourchette ?? 0)} sorties viennent d’un mouvement plus fort que prévu`
          : ""
      }.`,
    );
  if (b.nb_crises > 0)
    phrases.push(
      `Mais elle a reconnu ${b.nb_reconnues_sans_date} crise${b.nb_reconnues_sans_date > 1 ? "s" : ""} sur ${b.nb_crises} sans qu’on les nomme : c’est un test à l’aveugle partiel, qui mesure surtout sa connaissance des crises passées.`,
    );
  return phrases;
}

export function ecartRelatif(sans: MetriquesValidation, avec: MetriquesValidation): number | null {
  if (sans.erreur_moyenne_pts == null || avec.erreur_moyenne_pts == null || avec.erreur_moyenne_pts === 0) return null;
  return sans.erreur_moyenne_pts / avec.erreur_moyenne_pts;
}
