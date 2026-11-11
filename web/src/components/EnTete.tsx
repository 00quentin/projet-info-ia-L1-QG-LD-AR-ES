"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import { CircleHelp, Moon, Sun } from "lucide-react";
import { ouvrirGuide } from "@/components/Guide";
import { RESSORT } from "@/components/motion/transitions";

const PAGES = [
  { href: "/", libelle: "Simulateur" },
  { href: "/backtest", libelle: "Backtest" },
  { href: "/historique", libelle: "Historique" },
  { href: "/academie", libelle: "Académie" },
  { href: "/a-propos", libelle: "À propos" },
];

function basculerTheme() {
  const racine = document.documentElement;
  const suivant = racine.dataset.theme === "dark" ? "light" : "dark";
  const appliquer = () => {
    racine.dataset.theme = suivant;
  };
  // Fondu enchaine entre les deux themes quand le navigateur le permet.
  const doc = document as Document & { startViewTransition?: (f: () => void) => void };
  if (doc.startViewTransition && !matchMedia("(prefers-reduced-motion: reduce)").matches) doc.startViewTransition(appliquer);
  else appliquer();
  try {
    localStorage.setItem("qt-theme", suivant);
  } catch {
    /* stockage indisponible (navigation privee) : le choix vaut pour la page */
  }
}

function Navigation({ className = "" }: { className?: string }) {
  const chemin = usePathname();
  return (
    <nav aria-label="Pages" className={className}>
      <ul className="flex items-center gap-1">
        {PAGES.map((p) => {
          const actif = p.href === "/" ? chemin === "/" : chemin.startsWith(p.href);
          return (
            <li key={p.href} className="relative">
              <Link
                href={p.href}
                aria-current={actif ? "page" : undefined}
                className={`relative block whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${actif ? "text-ink" : "text-muted hover:text-ink"}`}
              >
                {actif && <motion.span layoutId="onglet-actif" className="absolute inset-0 rounded-lg bg-surface-2" transition={RESSORT} />}
                <span className="relative">{p.libelle}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function EnTete() {
  return (
    <header className="border-b border-line bg-bg/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[1400px] items-center justify-between gap-4 px-4 sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2.5">
          <motion.span whileHover={{ rotate: -6, scale: 1.06 }} transition={RESSORT} className="block">
            <Image src="/logo.png" alt="" width={28} height={28} className="rounded-md" priority />
          </motion.span>
          <span className="text-[15px] font-semibold tracking-tight">Quant Terminal</span>
        </Link>
        <Navigation className="hidden md:block" />
        <div className="flex shrink-0 items-center gap-2">
          <motion.button
            type="button"
            onClick={ouvrirGuide}
            whileTap={{ scale: 0.9 }}
            className="grid size-9 place-items-center rounded-lg border border-line bg-surface text-ink-2 transition-colors hover:text-ink"
            aria-label="Ouvrir le guide d'utilisation"
            title="Guide d'utilisation"
          >
            <CircleHelp className="size-4" aria-hidden />
          </motion.button>
          <motion.button
            type="button"
            onClick={basculerTheme}
            whileTap={{ scale: 0.9, rotate: 20 }}
            className="grid size-9 shrink-0 place-items-center rounded-lg border border-line bg-surface text-ink-2 transition-colors hover:text-ink"
            aria-label="Basculer entre thème clair et thème sombre"
          >
            <Sun className="hidden size-4 dark:block" aria-hidden />
            <Moon className="size-4 dark:hidden" aria-hidden />
          </motion.button>
        </div>
      </div>
      <Navigation className="overflow-x-auto px-3 pb-2 [mask-image:linear-gradient(90deg,#000_88%,transparent)] [scrollbar-width:none] md:hidden" />
    </header>
  );
}
