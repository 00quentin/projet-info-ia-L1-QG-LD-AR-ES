import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowRight, ArrowUpRight, Bug, CircleHelp, Mail, Send, ShieldCheck, type LucideIcon } from "lucide-react";
import { G } from "@/components/academie/blocs";
import { LienContact } from "@/components/legal/blocs";
import { CopierTexte } from "@/components/legal/CopierTexte";
import { Apparition, Cascade, ElementCascade } from "@/components/motion/Apparition";
import { CONTACT_EMAIL, DEPOT_GITHUB, DEPOT_ISSUES, EQUIPE, NOM_SITE, UNIVERSITE } from "@/contenu/legal";

export const metadata: Metadata = {
  title: "Contact",
  description: "Joindre l’équipe Quant Terminal : e-mail, signalement d’un bug sur GitHub, questions sur vos données personnelles.",
  alternates: { canonical: "/contact" },
};

const BOUTON = "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors";
const BOUTON_PRINCIPAL = `${BOUTON} bg-accent font-semibold text-white hover:brightness-110`;
const BOUTON_SECONDAIRE = `${BOUTON} border border-line bg-surface text-ink-2 hover:border-line-strong hover:text-ink`;

function CarteContact({ icone: Icone, titre, children, actions }: { icone: LucideIcon; titre: string; children: ReactNode; actions: ReactNode }) {
  return (
    <div className="flex h-full flex-col gap-3 rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-6">
      <h2 className="flex items-center gap-3 text-lg font-semibold tracking-tight text-ink">
        <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent-ink">
          <Icone className="size-4.5" aria-hidden />
        </span>
        {titre}
      </h2>
      <div className="flex flex-1 flex-col gap-2 text-[15px] leading-[1.7] text-ink-2">{children}</div>
      <div className="mt-1 flex flex-wrap items-center gap-2">{actions}</div>
    </div>
  );
}

function LienExterne({ href, children, principal = false }: { href: string; children: ReactNode; principal?: boolean }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={principal ? BOUTON_PRINCIPAL : BOUTON_SECONDAIRE}>
      {children}
      <ArrowUpRight className="size-3.5" aria-hidden />
      <span className="sr-only"> (nouvel onglet)</span>
    </a>
  );
}

export default function Page() {
  return (
    <div className="mx-auto max-w-5xl px-4 pb-20 pt-10 sm:px-6 sm:pt-14">
      <Apparition className="max-w-[46rem]">
        <p className="inline-flex items-center gap-1.5 rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent-ink">
          <Send className="size-3.5" aria-hidden />
          Contact
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">Nous contacter</h1>
        <p className="mt-4 max-w-[37rem] text-[17px] leading-[1.7] text-ink-2 sm:text-lg">
          Une question, une erreur repérée, une idée d’amélioration ? {NOM_SITE} est un projet étudiant : nous lisons tous les messages et répondons
          dès que possible, en général sous quelques jours.
        </p>
      </Apparition>

      <Cascade auDefilement className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-2">
        <ElementCascade className="md:col-span-2">
          <CarteContact
            icone={Mail}
            titre="Écrire à l’équipe"
            actions={
              CONTACT_EMAIL ? (
                <>
                  <a href={`mailto:${CONTACT_EMAIL}`} className={BOUTON_PRINCIPAL}>
                    <Mail className="size-4" aria-hidden />
                    Écrire un e-mail
                  </a>
                  <CopierTexte texte={CONTACT_EMAIL} libelle="Copier l’adresse" confirmation="Adresse copiée" />
                </>
              ) : (
                <LienExterne href={DEPOT_ISSUES} principal>
                  Écrire sur GitHub
                </LienExterne>
              )
            }
          >
            <p>
              Le moyen le plus simple pour toute question sur le site, son contenu ou son fonctionnement{CONTACT_EMAIL ? " :" : "."}
            </p>
            {CONTACT_EMAIL && (
              <p className="text-lg font-semibold tracking-tight text-ink sm:text-xl">
                <LienContact />
              </p>
            )}
          </CarteContact>
        </ElementCascade>

        <ElementCascade>
          <CarteContact
            icone={Bug}
            titre="Signaler un bug, proposer une idée"
            actions={
              <>
                <LienExterne href={DEPOT_ISSUES}>Ouvrir un ticket</LienExterne>
                <LienExterne href={DEPOT_GITHUB}>Voir le code</LienExterne>
              </>
            }
          >
            <p>
              Le code du projet est public sur GitHub. Un ticket (« issue ») nous permet de suivre le problème et d’y répondre au même endroit : décrivez
              ce que vous avez fait, ce que vous attendiez et ce qui s’est passé.
            </p>
            <p className="text-sm text-muted">Les tickets sont visibles par tous : n’y mettez aucune information personnelle.</p>
          </CarteContact>
        </ElementCascade>

        <ElementCascade>
          <CarteContact
            icone={ShieldCheck}
            titre="Vos données personnelles"
            actions={
              <Link href="/confidentialite#droits" className={BOUTON_SECONDAIRE}>
                Vos droits
                <ArrowRight className="size-3.5" aria-hidden />
              </Link>
            }
          >
            <p>
              Pour exercer vos droits (accès, effacement, opposition…) ou poser une question sur la confidentialité, écrivez à <LienContact />. Sachez
              que votre historique et vos conversations ne sont conservés que dans votre navigateur.
            </p>
          </CarteContact>
        </ElementCascade>

        <ElementCascade className="md:col-span-2">
          <CarteContact
            icone={CircleHelp}
            titre="Une question sur le fonctionnement ?"
            actions={
              <>
                <Link href="/faq" className={BOUTON_SECONDAIRE}>
                  Questions fréquentes
                  <ArrowRight className="size-3.5" aria-hidden />
                </Link>
                <Link href="/methodologie" className={BOUTON_SECONDAIRE}>
                  Méthodologie
                  <ArrowRight className="size-3.5" aria-hidden />
                </Link>
              </>
            }
          >
            <p>
              D’où viennent les données, pourquoi les chiffres changent d’une simulation à l’autre, comment l’IA estime un scénario : la réponse est
              peut-être déjà dans la FAQ ou dans la méthodologie de l’Académie.
            </p>
          </CarteContact>
        </ElementCascade>
      </Cascade>

      <Apparition auDefilement className="mt-14">
        <h2 className="text-2xl font-semibold tracking-tight text-ink">L’équipe</h2>
        <p className="mt-3 max-w-[37rem] text-base leading-[1.75] text-ink-2">
          <G>{EQUIPE.join(", ").replace(/, ([^,]*)$/, " et $1")}</G>, étudiants en licence MIASHS et Économie &amp; Gestion à l’{UNIVERSITE.nom}.
          Le projet est présenté en détail sur la page <Link href="/a-propos" className="font-medium text-accent-ink underline decoration-accent/40 underline-offset-2 hover:decoration-accent">À propos</Link>.
        </p>
        <p className="mt-3 max-w-[37rem] text-sm leading-relaxed text-muted">
          Pas de formulaire de contact sur ce site : un e-mail ou un ticket suffit, et nous évitons ainsi de collecter des données dont nous n’avons pas
          besoin.
        </p>
      </Apparition>
    </div>
  );
}
