import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowUpRight, Check, Rocket, Sprout } from "lucide-react";
import { Encadre, G } from "@/components/academie/blocs";
import { Equipe } from "@/components/apropos/Equipe";
import { Stack } from "@/components/apropos/Stack";
import { Apparition } from "@/components/motion/Apparition";
import { FONCTIONNALITES } from "@/contenu/apropos";

export const metadata: Metadata = {
  title: "À propos",
  description: "Le projet Quant Terminal : équipe, genèse, ambitions, stack technique, fonctionnalités, sources et limites.",
};

function Rubrique({ id, titre, children }: { id: string; titre: string; children: ReactNode }) {
  return (
    <section aria-labelledby={id} className="mt-14">
      <Apparition auDefilement>
        <h2 id={id} className="mb-5 text-2xl font-semibold tracking-tight text-ink">
          {titre}
        </h2>
        {children}
      </Apparition>
    </section>
  );
}

function CarteRecit({ icone, titre, children }: { icone: ReactNode; titre: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-3 rounded-carte border border-line bg-surface p-6 shadow-card">
      <h2 className="flex items-center gap-3 text-xl font-semibold tracking-tight text-ink">
        <span className="grid size-9 place-items-center rounded-tuile bg-accent-soft text-accent-ink">{icone}</span>
        {titre}
      </h2>
      <div className="flex flex-col gap-3 text-base leading-relaxed text-ink-2">{children}</div>
    </div>
  );
}

export default function Page() {
  return (
    <div className="mx-auto max-w-5xl px-4 pb-20 pt-10 sm:px-6 sm:pt-14">
      <Apparition>
        <p className="inline-flex rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent-ink">Université Paris Nanterre · Licence 1 · Semestre 2</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">À propos de Quant Terminal</h1>
        <p className="mt-5 max-w-[40rem] text-lg leading-relaxed text-ink-2">
          Quant Terminal est un projet réalisé dans le cadre de notre cours d’<G>informatique de L1, semestre 2</G>, au sein de la licence <G>MIASHS</G>{" "}
          (Mathématiques et Informatique Appliquées aux Sciences Humaines et Sociales), que nous suivons en <G>double licence avec Économie et Gestion</G>{" "}
          à l’Université Paris Nanterre.
        </p>
      </Apparition>

      <Rubrique id="equipe" titre="L’équipe">
        <Equipe />
      </Rubrique>

      <section className="mt-14 grid grid-cols-1 gap-4 lg:grid-cols-[3fr_2fr]">
        <Apparition auDefilement>
          <CarteRecit icone={<Sprout className="size-4.5" aria-hidden />} titre="Genèse du projet">
            <p>
              Nous avons choisi de développer un projet centré sur la <G>finance</G>, un domaine qui nous intéresse particulièrement, tout comme les{" "}
              <G>mathématiques</G>. L’objectif était de combiner ces deux disciplines à travers un outil informatique, afin de créer un projet cohérent et
              enrichissant.
            </p>
            <p>
              Ce projet a également une dimension <G>pédagogique</G> importante. Il vise à rendre certains concepts financiers plus accessibles et
              compréhensibles pour un public large, notamment dans un cadre académique. Bien qu’il ne soit pas destiné à être utilisé en l’état par des
              professionnels de la finance, nous avons cherché à nous rapprocher au maximum d’un outil <G>réaliste et pertinent</G>.
            </p>
          </CarteRecit>
        </Apparition>
        <Apparition auDefilement delai={0.08}>
          <CarteRecit icone={<Rocket className="size-4.5" aria-hidden />} titre="Ambitions">
            <p>
              Au-delà de l’aspect scolaire, notre ambition est de <G>poursuivre le développement</G> de cette application afin d’en faire un outil
              réellement utilisable, avec une utilité concrète pour les utilisateurs. L’idée est donc de faire évoluer ce projet vers quelque chose de plus
              abouti et potentiellement utile à un public plus large.
            </p>
          </CarteRecit>
        </Apparition>
      </section>

      <Rubrique id="stack" titre="Stack technique">
        <Stack />
      </Rubrique>

      <Rubrique id="fonctionnalites" titre="Fonctionnalités principales">
        <ul className="grid grid-cols-1 gap-x-6 gap-y-1 rounded-carte border border-line bg-surface p-3 shadow-card sm:grid-cols-2 sm:p-4">
          {FONCTIONNALITES.map((f) => {
            const texte = (
              <>
                <Check className="mt-0.5 size-4 shrink-0 text-gain" aria-hidden />
                <span className="text-titre leading-relaxed text-ink-2">
                  <G>{f.titre}</G> : {f.texte}
                </span>
                {f.lien && <ArrowUpRight className="ml-auto mt-0.5 size-4 shrink-0 text-muted transition group-hover:text-accent" aria-hidden />}
              </>
            );
            return (
              <li key={f.titre}>
                {f.lien ? (
                  <Link href={f.lien} className="group flex gap-3 rounded-tuile px-3 py-2.5 transition-colors hover:bg-surface-2">
                    {texte}
                  </Link>
                ) : (
                  <div className="flex gap-3 px-3 py-2.5">{texte}</div>
                )}
              </li>
            );
          })}
        </ul>
      </Rubrique>

      <Rubrique id="limites" titre="Sources & limites assumées">
        <Encadre ton="alerte">
          <p>
            <G>Quant Terminal est un outil pédagogique.</G>
          </p>
          <p>
            Le choc de chaque actif est estimé par une IA ; les trajectoires autour de ce choc utilisent les volatilités et les corrélations mesurées sur
            les vrais rendements Yahoo Finance.
          </p>
          <p>Les montants sont convertis en euros (taux officiels BCE en backtest).</p>
          <p>
            <G>Limites :</G> volatilités et corrélations supposées constantes sur l’horizon, pas de coûts de transaction, obligations suivies via des ETF.
          </p>
          <p>
            Pour un usage professionnel, il faudrait calibrer le modèle sur des données institutionnelles et modéliser les changements de régime en crise.
          </p>
          <p>
            <Link href="/methodologie" className="font-medium text-accent-ink underline decoration-accent/40 underline-offset-2 hover:decoration-accent">
              Lire la méthodologie complète
            </Link>{" "}
            : sources, modèle, calibration de l&apos;IA, bornes et limites.
          </p>
        </Encadre>
      </Rubrique>

      <footer className="mt-16 border-t border-line pt-6 text-center text-sm text-muted">© 2026 · Quant Terminal · Université Paris Nanterre · MIASHS</footer>
    </div>
  );
}
