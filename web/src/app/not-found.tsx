import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, ChartLine, GraduationCap, History, MessageCircleQuestionMark, Send, type LucideIcon } from "lucide-react";

export const metadata: Metadata = {
  title: "Page introuvable",
  description: "Cette page n’existe pas ou a été déplacée.",
};

const LIENS: { href: string; titre: string; texte: string; icone: LucideIcon }[] = [
  { href: "/", titre: "Simulateur", texte: "Tester un scénario sur un portefeuille", icone: ChartLine },
  { href: "/backtest", titre: "Backtest", texte: "Rejouer une vraie crise passée", icone: History },
  { href: "/academie", titre: "Académie", texte: "Comprendre la finance de marché", icone: GraduationCap },
  { href: "/faq", titre: "Questions fréquentes", texte: "Données, IA, confidentialité", icone: MessageCircleQuestionMark },
  { href: "/contact", titre: "Contact", texte: "Signaler un lien cassé", icone: Send },
];

// Composant serveur sans animation JavaScript : ce fichier accompagne toutes les pages du site.
export default function PageIntrouvable() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col items-center px-4 pb-20 pt-16 text-center sm:px-6 sm:pt-24">
      <p className="apparition text-[88px] font-semibold leading-none tracking-tighter text-accent tabular-nums sm:text-[120px]" aria-hidden>
        404
      </p>
      <h1 className="apparition mt-4 text-3xl font-semibold tracking-tight text-ink sm:text-4xl">Cette page est introuvable</h1>
      <p className="apparition mt-4 max-w-[34rem] text-[17px] leading-[1.7] text-ink-2">
        L’adresse est peut-être mal saisie, ou la page a été déplacée. Même les meilleurs modèles ne prévoient pas tout : voici de quoi reprendre le
        fil.
      </p>
      <Link
        href="/"
        className="apparition mt-8 inline-flex h-11 items-center gap-2 rounded-xl bg-accent px-5 text-sm font-semibold text-white transition hover:brightness-110"
      >
        <ArrowLeft className="size-4" aria-hidden />
        Retour à l’accueil
      </Link>

      <nav aria-label="Pages utiles" className="apparition mt-14 w-full">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">Pages utiles</h2>
        <ul className="mt-4 grid grid-cols-1 gap-3 text-left sm:grid-cols-2">
          {LIENS.map(({ href, titre, texte, icone: Icone }) => (
            <li key={href} className={href === "/" ? "sm:col-span-2" : undefined}>
              <Link
                href={href}
                className="group flex h-full items-center gap-3 rounded-2xl border border-line bg-surface p-4 shadow-card transition-colors hover:border-accent/50"
              >
                <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent-ink">
                  <Icone className="size-4.5" aria-hidden />
                </span>
                <span className="min-w-0">
                  <span className="block text-[15px] font-semibold text-ink">{titre}</span>
                  <span className="block text-sm text-muted">{texte}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
