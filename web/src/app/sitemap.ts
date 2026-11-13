import type { MetadataRoute } from "next";
import { MISE_A_JOUR, SITE_URL } from "@/contenu/legal";

// /historique n'y figure pas : son contenu est propre à chaque navigateur, rien à indexer.
const PAGES: { chemin: string; priorite: number; frequence: "weekly" | "monthly" | "yearly"; miseAJour?: string }[] = [
  { chemin: "/", priorite: 1, frequence: "weekly" },
  { chemin: "/backtest", priorite: 0.8, frequence: "monthly" },
  { chemin: "/academie", priorite: 0.8, frequence: "monthly" },
  { chemin: "/faq", priorite: 0.6, frequence: "monthly" },
  { chemin: "/a-propos", priorite: 0.5, frequence: "monthly" },
  { chemin: "/contact", priorite: 0.4, frequence: "yearly" },
  { chemin: "/mentions-legales", priorite: 0.2, frequence: "yearly", miseAJour: MISE_A_JOUR },
  { chemin: "/cgu", priorite: 0.2, frequence: "yearly", miseAJour: MISE_A_JOUR },
  { chemin: "/confidentialite", priorite: 0.2, frequence: "yearly", miseAJour: MISE_A_JOUR },
];

export default function sitemap(): MetadataRoute.Sitemap {
  return PAGES.map((p) => ({
    url: `${SITE_URL}${p.chemin === "/" ? "" : p.chemin}`,
    changeFrequency: p.frequence,
    priority: p.priorite,
    ...(p.miseAJour ? { lastModified: p.miseAJour } : {}),
  }));
}
