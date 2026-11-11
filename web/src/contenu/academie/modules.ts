// Plan de l'Académie : onglets, titres de parties et sommaire lisent tous cette liste.
// Les ancres de section valent "<module>-<cle>" (ex. /academie#modeles-monte-carlo).

export type SectionMeta = { numero?: string; titre: string };

export type ModuleMeta = {
  id: string;
  numero: number;
  /** Nom complet du module (ancien onglet Streamlit). */
  nom: string;
  /** Libellé court de l'onglet. */
  court: string;
  /** Titre de la partie (h2). */
  titre: string;
  sections: Record<string, SectionMeta>;
};

export const MODULES = [
  {
    id: "outils",
    numero: 1,
    nom: "Lire les données",
    court: "Lire les données",
    titre: "Apprendre à lire un graphique de marché",
    sections: {
      "prix-absolus": { numero: "1.1", titre: "L’illusion des prix absolus" },
      "base-100": { numero: "1.2", titre: "La base 100 et pourquoi elle est magique" },
      heatmap: { numero: "1.3", titre: "La heatmap de performance" },
      trajectoire: { numero: "1.4", titre: "Lire une trajectoire stochastique" },
      "monte-carlo": { numero: "1.5", titre: "Les bandes de confiance Monte-Carlo" },
    },
  },
  {
    id: "modeles",
    numero: 2,
    nom: "Modèles & maths",
    court: "Modèles & maths",
    titre: "Comment simuler l’avenir avec des mathématiques",
    sections: {
      bachelier: { numero: "2.1", titre: "Le modèle de Bachelier et le mouvement brownien" },
      "loi-normale": { numero: "2.2", titre: "Pourquoi la loi normale est insuffisante" },
      "trois-modeles": { numero: "2.3", titre: "Les 3 modèles de Quant Terminal" },
      "monte-carlo": { numero: "2.4", titre: "La méthode Monte-Carlo" },
      rendements: { numero: "2.5", titre: "Rendements simples vs rendements logarithmiques" },
    },
  },
  {
    id: "macro",
    numero: 3,
    nom: "Macro-économie",
    court: "Macro-économie",
    titre: "Les 3 forces qui contrôlent les marchés mondiaux",
    sections: {
      "banques-centrales": { numero: "3.1", titre: "Les banques centrales : les véritables maîtres du jeu" },
      inflation: { numero: "3.2", titre: "L’inflation : la taxe invisible qui ronge votre argent" },
      "courbe-taux": { numero: "3.3", titre: "La courbe des taux : l’indicateur préféré des récessions" },
      dollar: { numero: "3.4", titre: "Le dollar américain : le soleil du système financier" },
      vix: { numero: "3.5", titre: "Le VIX : le thermomètre de la peur" },
    },
  },
  {
    id: "cas",
    numero: 4,
    nom: "Cas historiques",
    court: "Cas historiques",
    titre: "Les grandes crises expliquées",
    sections: {
      "krach-1929": { numero: "4.1", titre: "Le krach de 1929 et la Grande Dépression" },
      "black-monday": { numero: "4.2", titre: "Le Black Monday du 19 octobre 1987" },
      "bulle-internet": { numero: "4.3", titre: "La bulle internet (1995-2002)" },
      subprimes: { numero: "4.4", titre: "La crise des subprimes (2007-2009)" },
      covid: { numero: "4.5", titre: "Le krach COVID de mars 2020" },
      lecons: { numero: "4.6", titre: "Ce que l’histoire enseigne" },
      synthese: { titre: "Synthèse visuelle des grandes crises" },
    },
  },
  {
    id: "strategies",
    numero: 5,
    nom: "Stratégies d’investissement",
    court: "Stratégies",
    titre: "Les grandes stratégies d’allocation d’actifs",
    sections: {
      "60-40": { numero: "5.1", titre: "Le portefeuille 60/40 (la stratégie classique)" },
      "all-weather": { numero: "5.2", titre: "Le All Weather de Ray Dalio (Bridgewater)" },
      "risk-parity": { numero: "5.3", titre: "La Risk Parity" },
      value: { numero: "5.4", titre: "Le value investing (Warren Buffett, Benjamin Graham)" },
      momentum: { numero: "5.5", titre: "Le momentum / trend following" },
      indexation: { numero: "5.6", titre: "L’indexation passive (Bogle, Vanguard)" },
      dca: { numero: "5.7", titre: "Le DCA (Dollar-Cost Averaging)" },
      facteurs: { numero: "5.8", titre: "Le factor investing (Fama, French)" },
      choisir: { numero: "5.9", titre: "Pour choisir votre stratégie" },
      synthese: { titre: "Les 3 profils en un coup d’œil" },
    },
  },
  {
    id: "construction",
    numero: 6,
    nom: "Construction de portefeuille",
    court: "Portefeuille",
    titre: "Construire un portefeuille comme un pro",
    sections: {
      diversification: { numero: "6.1", titre: "La diversification : le seul vrai « free lunch »" },
      frontiere: { numero: "6.2", titre: "La frontière efficiente" },
      correlations: { numero: "6.3", titre: "Les corrélations entre classes d’actifs (régime normal)" },
      rebalancement: { numero: "6.4", titre: "Le rebalancement (rebalancing)" },
      buckets: { numero: "6.5", titre: "Le découpage par horizon (bucket strategy)" },
      synthese: { titre: "Exemple d’allocation équilibrée" },
    },
  },
  {
    id: "biais",
    numero: 7,
    nom: "Biais comportementaux",
    court: "Biais",
    titre: "Les biais qui ruinent les investisseurs",
    sections: {
      "aversion-perte": { numero: "7.1", titre: "L’aversion à la perte" },
      confirmation: { numero: "7.2", titre: "Le biais de confirmation" },
      recence: { numero: "7.3", titre: "L’effet de récence" },
      ancrage: { numero: "7.4", titre: "Le biais d’ancrage" },
      confiance: { numero: "7.5", titre: "L’excès de confiance" },
      disponibilite: { numero: "7.6", titre: "Le biais de disponibilité" },
      mimetisme: { numero: "7.7", titre: "Le mimétisme (herding)" },
      synthese: { titre: "Les 4 grands biais à connaître" },
    },
  },
  {
    id: "lexique",
    numero: 8,
    nom: "Lexique",
    court: "Lexique",
    titre: "Le lexique du professionnel",
    sections: {
      marches: { titre: "Marchés & cycles" },
      "banques-centrales": { titre: "Banques centrales" },
      risque: { titre: "Mesures de risque" },
      derives: { titre: "Produits dérivés" },
      obligations: { titre: "Obligations" },
      trading: { titre: "Trading & stratégie" },
      comptabilite: { titre: "Comptabilité & finance d’entreprise" },
      synthese: { titre: "Les termes essentiels à retenir" },
    },
  },
  {
    id: "methodologie",
    numero: 9,
    nom: "Méthodologie",
    court: "Méthodologie",
    titre: "Méthodologie mathématique de Quant Terminal",
    sections: {
      volatilite: { numero: "A.", titre: "Volatilité annualisée" },
      sharpe: { numero: "B.", titre: "Sharpe Ratio" },
      drawdown: { numero: "C.", titre: "Max Drawdown" },
      var: { numero: "D.", titre: "Value at Risk (VaR)" },
      mbg: { numero: "E.", titre: "Mouvement Brownien Géométrique (modèle Probabiliste)" },
      euros: { numero: "E bis.", titre: "Conversion en euros" },
      "monte-carlo": { numero: "F.", titre: "Méthode Monte-Carlo" },
      limites: { numero: "G.", titre: "Limites connues de notre modèle" },
      pipeline: { titre: "Pipeline de Quant Terminal" },
    },
  },
] as const satisfies readonly ModuleMeta[];

export type IdModule = (typeof MODULES)[number]["id"];
type ModuleDe<I extends IdModule> = Extract<(typeof MODULES)[number], { id: I }>;
export type CleSection<I extends IdModule> = keyof ModuleDe<I>["sections"] & string;

export const idSection = (module: IdModule, cle: string) => `${module}-${cle}`;

/** Liste ordonnée des sections d'un module, avec leur ancre. */
export function listeSections(module: IdModule): ({ id: string } & SectionMeta)[] {
  const m: ModuleMeta = MODULES.find((x) => x.id === module) ?? MODULES[0];
  return Object.entries(m.sections).map(([cle, s]) => ({ id: idSection(module, cle), ...s }));
}

/** Raccourci pour les fichiers de contenu : section("base-100") -> { id, numero, titre }. */
export function sectionsDe<I extends IdModule>(module: I) {
  const m: ModuleMeta = MODULES.find((x) => x.id === module) ?? MODULES[0];
  return (cle: CleSection<I>) => ({ id: idSection(module, cle), ...m.sections[cle] });
}

/** Retrouve le module (et la section éventuelle) désigné par le hash de l'adresse. */
export function resoudreAncre(ancre: string): { module: IdModule; section?: string } {
  for (const m of MODULES) {
    if (ancre === m.id) return { module: m.id };
    if (ancre.startsWith(`${m.id}-`) && ancre.slice(m.id.length + 1) in m.sections) return { module: m.id, section: ancre };
  }
  return { module: MODULES[0].id };
}
