import type { Metadata } from "next";
import { GraduationCap } from "lucide-react";
import { Academie } from "@/components/academie/Academie";
import { Apparition } from "@/components/motion/Apparition";
import { CONTENUS } from "@/contenu/academie";

export const metadata: Metadata = {
  title: "Académie — Quant Terminal",
  description: "Comprendre la finance de marché : lecture des graphiques, modèles mathématiques, macro-économie, crises historiques, stratégies, biais et lexique.",
};

export default function Page() {
  return (
    <>
      <header className="mx-auto max-w-[1280px] px-4 pt-10 sm:px-6 sm:pt-14">
        <Apparition className="max-w-[46rem]">
          <p className="inline-flex items-center gap-1.5 rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent-ink">
            <GraduationCap className="size-3.5" aria-hidden />
            Académie
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">Académie Quant Terminal</h1>
          <p className="mt-4 max-w-[37rem] text-[17px] leading-[1.7] text-ink-2 sm:text-lg">
            Bienvenue dans l’Académie. Ici, on ne récite pas des définitions : on cherche à <strong className="font-semibold text-ink">comprendre</strong>{" "}
            pourquoi les marchés se comportent comme ils le font. L’Académie est conçue pour être lue dans l’ordre — chaque partie s’appuie sur la
            précédente. Prenez votre temps.
          </p>
        </Apparition>
      </header>
      <Academie contenus={CONTENUS} />
    </>
  );
}
