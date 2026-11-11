"use client";

import Image from "next/image";
import Link from "next/link";
import { Moon, Sun } from "lucide-react";

function basculerTheme() {
  const racine = document.documentElement;
  const suivant = racine.dataset.theme === "dark" ? "light" : "dark";
  racine.dataset.theme = suivant;
  try {
    localStorage.setItem("qt-theme", suivant);
  } catch {
    /* stockage indisponible (navigation privee) : le choix vaut pour la page */
  }
}

export function EnTete() {
  return (
    <header className="border-b border-line bg-bg/85 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-[1400px] items-center justify-between gap-4 px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <Image src="/logo.png" alt="" width={28} height={28} className="rounded-md" priority />
          <span className="text-[15px] font-semibold tracking-tight">Quant Terminal</span>
        </Link>
        <button
          type="button"
          onClick={basculerTheme}
          className="grid size-9 place-items-center rounded-lg border border-line bg-surface text-ink-2 transition hover:text-ink"
          aria-label="Basculer entre thème clair et thème sombre"
        >
          <Sun className="hidden size-4 dark:block" aria-hidden />
          <Moon className="size-4 dark:hidden" aria-hidden />
        </button>
      </div>
    </header>
  );
}
