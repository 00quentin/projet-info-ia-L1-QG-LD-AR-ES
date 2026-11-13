// Reglages d'animation communs : tout le site bouge de la meme facon.

/** Courbe "sortie douce" : demarre vite, se pose en douceur. */
export const EASE_SORTIE = [0.22, 1, 0.36, 1] as const;

// Durees (docs/BENCHMARK.md 3.6) : retours d'interface < 300 ms, graphiques 0,8 s une seule fois.
export const DUREE = { rapide: 0.15, normale: 0.25, lente: 0.45, donnees: 0.8 } as const;

/** Ressort vif pour les elements d'interface (selection, interrupteurs, onglets). */
export const RESSORT = { type: "spring", stiffness: 420, damping: 34, mass: 0.8 } as const;

/** Ressort plus souple pour les blocs qui entrent a l'ecran. */
export const RESSORT_DOUX = { type: "spring", stiffness: 220, damping: 28 } as const;

/** Decalage entre deux elements d'une cascade (secondes). */
export const PAS_CASCADE = 0.06;
