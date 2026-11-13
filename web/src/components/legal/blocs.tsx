import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowUpRight } from "lucide-react";
import { Apparition } from "@/components/motion/Apparition";
import { CONTACT_EMAIL, DEPOT_GITHUB, type Prestataire } from "@/contenu/legal";

// Briques des pages légales, FAQ et contact (sans état : rendues côté serveur).
// Le texte courant reprend les briques de l'Académie (P, G, Liste, Point, Encadre).

const CLASSE_LIEN = "font-medium text-accent-ink underline decoration-accent/40 underline-offset-2 transition-colors hover:decoration-accent";

/** Partie numérotée d'une page légale (h2) : son ancre est reprise par le sommaire. */
export function Rubrique({ id, numero, titre, children }: { id: string; numero?: string; titre: string; children: ReactNode }) {
  return (
    <section aria-labelledby={id}>
      <Apparition auDefilement decalage={10}>
        <h2 id={id} className="scroll-mt-6 text-xl font-semibold leading-snug tracking-tight text-ink sm:text-[22px] lg:scroll-mt-36">
          {numero && <span className="mr-2 tabular-nums text-accent">{numero}</span>}
          {titre}
        </h2>
        <div className="mt-4 flex flex-col gap-4">{children}</div>
      </Apparition>
    </section>
  );
}

/** Lien dans le texte : interne (navigation du site) ou externe (nouvel onglet). */
export function Lien({ href, children }: { href: string; children: ReactNode }) {
  if (href.startsWith("/") || href.startsWith("#")) {
    return (
      <Link href={href} className={CLASSE_LIEN}>
        {children}
      </Link>
    );
  }
  const externe = href.startsWith("http");
  return (
    <a href={href} className={CLASSE_LIEN} {...(externe ? { target: "_blank", rel: "noopener noreferrer" } : {})}>
      {children}
      {externe && (
        <>
          <ArrowUpRight className="ml-0.5 inline size-3.5 align-[-0.1em] text-muted" aria-hidden />
          <span className="sr-only"> (nouvel onglet)</span>
        </>
      )}
    </a>
  );
}

/** Adresse e-mail de l'équipe (lien mailto) ou, faute d'adresse, le dépôt GitHub. */
export function LienContact() {
  if (CONTACT_EMAIL) {
    return (
      <a href={`mailto:${CONTACT_EMAIL}`} className={`${CLASSE_LIEN} break-words`}>
        {CONTACT_EMAIL}
      </a>
    );
  }
  return (
    <>
      via le <Lien href={DEPOT_GITHUB}>dépôt GitHub du projet</Lien>
    </>
  );
}

/** Liste « libellé : valeur » encadrée (coordonnées, identité). */
export function Fiche({ lignes, titre }: { titre?: ReactNode; lignes: [string, ReactNode][] }) {
  return (
    <div className="max-w-[40rem] rounded-2xl border border-line bg-surface shadow-card">
      {titre && <p className="border-b border-line px-4 py-3 text-[15px] font-semibold text-ink sm:px-5">{titre}</p>}
      <dl className="divide-y divide-line">
        {lignes.map(([libelle, valeur]) => (
          <div key={libelle} className="grid gap-0.5 px-4 py-2.5 sm:grid-cols-[10rem_minmax(0,1fr)] sm:gap-4 sm:px-5">
            <dt className="text-sm text-muted">{libelle}</dt>
            <dd className="min-w-0 text-[15px] leading-relaxed text-ink-2">{valeur}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

/** Coordonnées d'un prestataire (hébergeur, sous-traitant). */
export function FichePrestataire({ p }: { p: Prestataire }) {
  const lignes: [string, ReactNode][] = [
    ["Rôle", p.role],
    ["Adresse", p.adresse],
    ["Site", <Lien key="site" href={p.site}>{p.site.replace(/^https:\/\//, "")}</Lien>],
  ];
  if (p.contact) lignes.push(["Contact", p.contact.includes("@") ? <Lien key="contact" href={`mailto:${p.contact}`}>{p.contact}</Lien> : p.contact]);
  return <Fiche titre={p.nom} lignes={lignes} />;
}
