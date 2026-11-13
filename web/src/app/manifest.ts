import type { MetadataRoute } from "next";
import { NOM_SITE } from "@/contenu/legal";

// Couleurs : --bg du thème clair (globals.css), comme la barre du navigateur dans layout.tsx.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: `${NOM_SITE} — Simulateur d’investissement`,
    short_name: NOM_SITE,
    description: "Testez l’impact d’un événement économique sur votre portefeuille : vrais prix de marché, analyse par IA, métriques de risque.",
    lang: "fr",
    dir: "ltr",
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: "#f7f7f8",
    theme_color: "#f7f7f8",
    categories: ["finance", "education"],
    icons: [
      { src: "/icon.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/apple-icon.png", sizes: "180x180", type: "image/png", purpose: "any" },
    ],
  };
}
