import type { Metadata, Viewport } from "next";
import "./globals.css";
import { EnTete } from "@/components/EnTete";
import { BandeMarches } from "@/components/BandeMarches";
import { BulleChat } from "@/components/chat/BulleChat";
import { FournisseurMouvement } from "@/components/motion/FournisseurMouvement";

export const metadata: Metadata = {
  title: "Quant Terminal — Simulateur d'investissement",
  description:
    "Testez l'impact d'un événement économique sur votre portefeuille : vrais prix de marché, analyse par IA, métriques de risque.",
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
            <BandeMarches />
          </div>
          <div id="contenu">{children}</div>
          <BulleChat />
        </FournisseurMouvement>
      </body>
    </html>
  );
}
