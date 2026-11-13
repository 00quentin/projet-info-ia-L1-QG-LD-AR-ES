// Informations légales du site : un seul endroit à mettre à jour (mentions légales,
// CGU, confidentialité, contact, pied de page, SEO).

import { MEMBRES_EQUIPE } from "@/contenu/apropos";

export const NOM_SITE = "Quant Terminal";

/** Adresse publique du site (surchargée par NEXT_PUBLIC_SITE_URL si un domaine est ajouté). */
export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://quant-terminal-qg-team.vercel.app").replace(/\/$/, "");

/** Adresse e-mail de contact. Si elle est vide, le site renvoie vers le dépôt GitHub à la place. */
export const CONTACT_EMAIL = "450009207@parisnanterre.fr";

export const DEPOT_GITHUB = "https://github.com/00quentin/projet-info-ia-L1-QG-LD-AR-ES";
export const DEPOT_ISSUES = `${DEPOT_GITHUB}/issues`;

/** Date de dernière mise à jour des pages légales (format ISO, affichée en français). */
export const MISE_A_JOUR = "2026-11-13";

export const EQUIPE = MEMBRES_EQUIPE.map((m) => m.nom);
export const RESPONSABLE_PUBLICATION = "Quentin Geldreich";

export const UNIVERSITE = {
  nom: "Université Paris Nanterre",
  formation: "Licence MIASHS (double licence Économie & Gestion), L1, semestre 2",
  adresse: "200 avenue de la République, 92001 Nanterre Cedex, France",
};

export type Prestataire = {
  nom: string;
  role: string;
  adresse: string;
  site: string;
  /** Autres coordonnées publiées par le prestataire lui-même. */
  contact?: string;
  confidentialite: string;
};

// Coordonnées relevées sur les pages légales officielles de chaque prestataire.
export const HEBERGEURS: Prestataire[] = [
  {
    nom: "Vercel Inc.",
    role: "Hébergement du site web (pages, images, diffusion mondiale)",
    adresse: "440 N Barranca Ave #4133, Covina, CA 91723, États-Unis",
    site: "https://vercel.com",
    confidentialite: "https://vercel.com/legal/privacy-policy",
  },
  {
    nom: "Render Services, Inc.",
    role: "Hébergement de l’API (moteur de simulation et relais vers l’IA)",
    adresse: "525 Brannan Street, Suite 300, San Francisco, CA 94107, États-Unis",
    site: "https://render.com",
    contact: "legal@render.com",
    confidentialite: "https://render.com/privacy",
  },
];

export const OPENAI: Prestataire = {
  nom: "OpenAI",
  role: "Génération des analyses, des réponses du chat et du commentaire des rapports PDF",
  adresse: "États-Unis",
  site: "https://openai.com",
  confidentialite: "https://openai.com/policies/privacy-policy",
};

export const WIKIMEDIA: Prestataire = {
  nom: "Wikimedia Foundation",
  role: "Photos d’archives de l’Académie, chargées depuis Wikimedia Commons",
  adresse: "États-Unis",
  site: "https://commons.wikimedia.org",
  confidentialite: "https://foundation.wikimedia.org/wiki/Policy:Privacy_policy",
};

export const SOURCES_DONNEES: { nom: string; usage: string; lien: string }[] = [
  {
    nom: "Yahoo Finance",
    usage: "Cours de clôture, volatilités et corrélations (récupérés avec la bibliothèque open source yfinance, sans lien avec Yahoo).",
    lien: "https://finance.yahoo.com",
  },
  {
    nom: "Banque centrale européenne (BCE)",
    usage: "Taux de change de référence de l’euro, pour convertir les montants en euros.",
    lien: "https://www.ecb.europa.eu",
  },
  {
    nom: "FRED — Federal Reserve Bank of St. Louis",
    usage: "Taux directeurs, taux à 10 ans et inflation (certaines séries proviennent de l’OCDE ou d’Eurostat via FRED).",
    lien: "https://fred.stlouisfed.org",
  },
  {
    nom: "OpenAI",
    usage: "Modèles de langage qui estiment l’impact des scénarios et répondent dans le chat.",
    lien: "https://openai.com",
  },
  {
    nom: "Wikimedia Commons",
    usage: "Photos d’archives de l’Académie, sous leurs licences respectives (crédit indiqué sous chaque photo).",
    lien: "https://commons.wikimedia.org",
  },
];

/** Formule courte reprise dans le pied de page et les CGU. */
export const AVERTISSEMENT_COURT = "Outil pédagogique — pas un conseil en investissement";

/** Ce que le site garde dans le navigateur du visiteur (rien d'autre n'y est écrit). */
export const STOCKAGE_NAVIGATEUR: { cle: string; contenu: string; lieu: "localStorage" | "sessionStorage"; duree: string }[] = [
  { cle: "qt-historique-v1", contenu: "Vos 20 dernières simulations et backtests (page Historique)", lieu: "localStorage", duree: "Jusqu’à ce que vous l’effaciez" },
  { cle: "qt-chat-v1", contenu: "Votre conversation avec l’analyste IA (100 derniers messages)", lieu: "localStorage", duree: "Jusqu’à ce que vous l’effaciez" },
  { cle: "qt-chat-contexte", contenu: "Résumé chiffré du dernier résultat affiché, proposé à l’analyste", lieu: "sessionStorage", duree: "Fermeture de l’onglet" },
  { cle: "qt-theme", contenu: "Thème clair ou sombre choisi", lieu: "localStorage", duree: "Jusqu’à ce que vous l’effaciez" },
  { cle: "qt-guide-vu", contenu: "Le guide de bienvenue a déjà été montré", lieu: "localStorage", duree: "Jusqu’à ce que vous l’effaciez" },
];

export function dateMiseAJour(iso = MISE_A_JOUR): string {
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
}
