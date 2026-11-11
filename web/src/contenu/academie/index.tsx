import type { ReactNode } from "react";
import type { IdModule } from "./modules";
import { ContenuOutils } from "./outils";
import { ContenuModeles } from "./modeles";
import { ContenuMacro } from "./macro";
import { ContenuCas } from "./cas";
import { ContenuStrategies } from "./strategies";
import { ContenuConstruction } from "./construction";
import { ContenuBiais } from "./biais";
import { ContenuLexique } from "./lexique";
import { ContenuMethodologie } from "./methodologie";

/** Contenu de chaque module, rendu côté serveur (formules KaTeX comprises). */
export const CONTENUS: Record<IdModule, ReactNode> = {
  outils: <ContenuOutils />,
  modeles: <ContenuModeles />,
  macro: <ContenuMacro />,
  cas: <ContenuCas />,
  strategies: <ContenuStrategies />,
  construction: <ContenuConstruction />,
  biais: <ContenuBiais />,
  lexique: <ContenuLexique />,
  methodologie: <ContenuMethodologie />,
};
