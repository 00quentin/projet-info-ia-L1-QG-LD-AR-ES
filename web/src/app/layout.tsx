import type { Metadata, Viewport } from "next";
import "./globals.css";
import { EnTete } from "@/components/EnTete";
import { BandeMarches } from "@/components/BandeMarches";
import { BulleChat } from "@/components/chat/BulleChat";
import { FournisseurMouvement } from "@/components/motion/FournisseurMouvement";
import { PiedDePage } from "@/components/PiedDePage";
import { Guide } from "@/components/Guide";
import { ZoneNotifications } from "@/components/ui/Notifications";

export const metadata: Metadata = {
  // Même adresse que SITE_URL (contenu/legal.ts) : base des liens absolus (image de partage, etc.).
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://quant-terminal-qg-team.vercel.app"),
  title: {
    default: "Quant Terminal — Simulateur d'investissement",
    template: "%s · Quant Terminal",
  },
  description:
    "Testez l'impact d'un événement économique sur votre portefeuille : vrais prix de marché, analyse par IA, métriques de risque.",
  applicationName: "Quant Terminal",
  authors: [{ name: "Quentin Geldreich" }, { name: "Lukha Doazan" }, { name: "Evan Saadi" }, { name: "Alex Ruimy" }],
  keywords: ["simulateur de portefeuille", "simulation financière", "backtest", "Monte-Carlo", "analyse IA", "finance de marché", "outil pédagogique"],
  category: "finance",
  // Sans titre ni description ici : chaque page reprend les siens pour le partage.
  openGraph: { type: "website", locale: "fr_FR", siteName: "Quant Terminal" },
  twitter: { card: "summary_large_image" },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f7f7f8" },
    { media: "(prefers-color-scheme: dark)", color: "#0b0b0e" },
  ],
};

// Applique le theme avant le premier affichage (evite un flash clair en mode sombre).
const SCRIPT_THEME = `try{var t=localStorage.getItem("qt-theme");if(t!=="light"&&t!=="dark"){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className="h-full antialiased" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: SCRIPT_THEME }} />
      </head>
      <body className="min-h-full">
        <FournisseurMouvement>
          <a href="#contenu" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2">
            Aller au contenu
          </a>
          {/* En-tete et cours restent visibles au defilement sur grand ecran */}
          <div className="z-30 lg:sticky lg:top-0">
            <EnTete />
          </div>
          <BandeMarches />
          <main id="contenu">{children}</main>
          <PiedDePage />
          <BulleChat />
          <Guide />
          <ZoneNotifications />
        </FournisseurMouvement>
      </body>
    </html>
  );
}
