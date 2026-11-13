// « L'IA à l'épreuve de l'histoire » : types et appel de GET /api/validation-ia.
// Les types reflètent data/validation_ia.json (scripts/valider_ia_historique.py).

import { API_URL, ErreurApi } from "@/lib/api";

export type MetriquesValidation = {
  nb_actifs: number;
  /** Écart moyen |estimé − réel|, en points de pourcentage. */
  erreur_moyenne_pts: number | null;
  erreur_mediane_pts: number | null;
  /** > 0 : l'IA est en moyenne trop optimiste. */
  biais_moyen_pts: number | null;
  /** Actifs dont le vrai mouvement dépasse le seuil (sens net). */
  nb_sens_comptes: number;
  nb_sens_corrects: number;
  part_sens_correct: number | null;
  correlation: number | null;
  correlation_rangs: number | null;
  /** Taille des chocs de l'IA rapportée à celle des vrais mouvements (< 1 : prudente). */
  ratio_amplitude: number | null;
  /** Comparaisons qui portent une fourchette bas / haut de l'IA. */
  nb_fourchettes?: number;
  nb_dans_fourchette?: number;
  /** Part des vrais mouvements tombés dans la fourchette de l'IA. */
  part_dans_fourchette?: number | null;
  /** Écart moyen haut − bas, en points. */
  largeur_moyenne_pts?: number | null;
  /** Sorties de fourchette où le vrai mouvement a été plus fort que prévu, dans le sens vu par l'IA. */
  nb_sorties_plus_fortes?: number;
  nb_crises?: number;
};

export type ActifValide = {
  cle: string;
  nom: string;
  nom_court: string;
  categorie: string | null;
  /** Devise de la comparaison : EUR, ou la devise locale (GBP, JPY) ; null pour un indicateur (VIX, EUR/USD). */
  devise: string | null;
  estime_pct: number;
  /** Estimation de l'IA dans la devise de cotation, avant conversion en euros. */
  estime_devise_pct: number;
  reel_pct: number;
  ecart_pts: number;
  /** null : vrai mouvement trop faible pour avoir un sens net. */
  sens_correct: boolean | null;
  /** Estimation plafonnée par les garde-fous du simulateur. */
  ecrete: boolean;
  /** Fourchette de l'IA (même conversion en euros que le central). */
  bas_pct?: number;
  haut_pct?: number;
  largeur_pts?: number;
  dans_fourchette?: boolean;
  sortie_plus_forte?: boolean;
};

export type VarianteAvecDate = {
  indice: string;
  reconnue: boolean;
  evenement_cite: string | null;
  metriques: MetriquesValidation;
  estimes_pct: Record<string, number>;
};

export type CriseValidee = {
  nom: string;
  debut: string;
  fin: string;
  premiere_seance: string;
  derniere_seance: string;
  nb_seances: number;
  duree: string;
  description_neutre: string;
  scenario_envoye: string;
  reconnue: boolean;
  evenement_cite: string | null;
  explication: string | null;
  modele: string | null;
  metriques: MetriquesValidation;
  metriques_devise_locale: MetriquesValidation;
  actifs: ActifValide[];
  actifs_absents: { cle: string; nom: string }[];
  avec_date: VarianteAvecDate | null;
};

export type ValidationIA = {
  genere_le: string;
  protocole: {
    version: string;
    version_prompt: string;
    modele: string;
    reglages_ia: Record<string, string | number>;
    modeles_utilises: string[];
    calibration_historique: boolean;
    conjoncture_du_jour: boolean;
    seuil_sens_pts: number;
    devise: string;
    devises_locales: string[];
    source_cours: string;
  };
  global: MetriquesValidation;
  global_devise_locale: MetriquesValidation;
  biais_connaissance: {
    nb_crises: number;
    sans_date: MetriquesValidation;
    avec_date: MetriquesValidation;
    nb_reconnues_sans_date: number;
    nb_reconnues_avec_date: number;
  };
  crises: CriseValidee[];
};

export async function lireValidationIA(): Promise<ValidationIA> {
  let reponse: Response;
  try {
    reponse = await fetch(`${API_URL}/api/validation-ia`);
  } catch {
    throw new ErreurApi("Impossible de joindre le serveur. Vérifiez votre connexion puis réessayez.", 0);
  }
  if (!reponse.ok) {
    let detail = "Les résultats n'ont pas pu être chargés. Réessayez dans un instant.";
    try {
      const corps = await reponse.json();
      if (typeof corps.detail === "string") detail = corps.detail;
    } catch {
      /* corps non JSON : message générique */
    }
    throw new ErreurApi(detail, reponse.status);
  }
  return reponse.json() as Promise<ValidationIA>;
}
