// Reglages d'animation communs : tout le site bouge de la meme facon.

/** Courbe "sortie douce" : demarre vite, se pose en douceur. */
export const EASE_SORTIE = [0.22, 1, 0.36, 1] as const;

export const DUREE = { rapide: 0.18, normale: 0.35, lente: 0.6 } as const;

/** Ressort vif pour les elements d'interface (selection, interrupteurs, onglets). */
export const RESSORT = { type: "spring", stiffness: 420, damping: 34, mass: 0.8 } as const;

/** Ressort plus souple pour les blocs qui entrent a l'ecran. */
export const RESSORT_DOUX = { type: "spring", stiffness: 220, damping: 28 } as const;

/** Decalage entre deux elements d'une cascade (secondes). */
export const PAS_CASCADE = 0.06;
