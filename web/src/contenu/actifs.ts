// Noms courts et descriptions des actifs, cote site uniquement (docs/BENCHMARK.md 2.3).
// Le moteur garde ses noms officiels (`nom` renvoye par l'API) : PDF, IA et Streamlit les utilisent.

export type FicheActif = { nom: string; description: string };

export const FICHES_ACTIFS: Record<string, FicheActif> = {
  "S&P 500": { nom: "S&P 500", description: "500 grandes entreprises américaines" },
  NASDAQ: { nom: "Nasdaq 100", description: "Les géants de la tech américaine" },
  "CAC 40": { nom: "CAC 40", description: "40 grandes entreprises françaises" },
  MSCI_World: { nom: "Actions monde", description: "Grandes entreprises des pays développés" },
  Emerging_Markets: { nom: "Pays émergents", description: "Chine, Inde, Taïwan, Brésil…" },
  Bons_Tresor_US_10Y: { nom: "Emprunts d'État américains", description: "Prêter à l'État américain" },
  Bund_10Y: { nom: "Emprunts d'État allemands", description: "La valeur refuge de la zone euro" },
  OAT_10Y: { nom: "Emprunts d'État français", description: "Les OAT, la dette de la France" },
  JGB_10Y: { nom: "Emprunts d'État japonais", description: "Taux parmi les plus bas du monde" },
  Gilt_10Y: { nom: "Emprunts d'État britanniques", description: "Les « gilts » du Trésor britannique" },
  EUR_USD: { nom: "Euro / dollar", description: "Combien de dollars vaut 1 €" },
  Dollar_Index: { nom: "Indice du dollar", description: "Le dollar face à 6 grandes devises" },
  VIX: { nom: "Indice de la peur (VIX)", description: "Nervosité attendue sur le S&P 500" },
  Or: { nom: "Or", description: "Valeur refuge, en dollars l'once" },
  Argent: { nom: "Argent", description: "Métal précieux et industriel" },
  Petrole: { nom: "Pétrole", description: "Baril de brut américain (WTI)" },
  Cuivre: { nom: "Cuivre", description: "Thermomètre de l'industrie mondiale" },
  ETF_Terres_Rares: { nom: "Terres rares", description: "Métaux des batteries et des aimants" },
  ETF_Defense: { nom: "Défense et aéronautique", description: "Industriels américains de la défense" },
  Bitcoin: { nom: "Bitcoin", description: "La première cryptomonnaie" },
  Ethereum: { nom: "Ethereum", description: "Crypto des applications décentralisées" },
  XRP: { nom: "XRP", description: "Crypto des paiements internationaux" },
  Solana: { nom: "Solana", description: "Blockchain rapide et peu chère" },
};

/** Libelles courts des categories renvoyees par l'API (config.ACTIFS_DISPONIBLES). */
export const LIBELLES_CATEGORIES: Record<string, string> = {
  "Actions & Indices": "Actions",
  "Obligations d'État (10 ans)": "Obligations d'État",
  "Obligations d'État": "Obligations d'État",
  "Devises & Volatilité": "Devises et volatilité",
  "Matières Premières": "Matières premières",
  Sectoriels: "Thématiques",
  Cryptomonnaies: "Cryptomonnaies",
  "Actifs personnalisés": "Mes actifs",
};

/** Nom court d'un actif ; repli sur le nom officiel (actifs personnalises, actifs futurs). */
export function nomCourt(cle: string, nomOfficiel?: string): string {
  return FICHES_ACTIFS[cle]?.nom ?? nomOfficiel ?? cle;
}

/** Description en une ligne, ou null si l'actif n'a pas de fiche (actif personnalise). */
export function descriptionActif(cle: string): string | null {
  return FICHES_ACTIFS[cle]?.description ?? null;
}

export function libelleCategorie(categorie: string): string {
  return LIBELLES_CATEGORIES[categorie] ?? categorie;
}
