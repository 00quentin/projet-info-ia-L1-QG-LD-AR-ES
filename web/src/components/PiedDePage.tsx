import Link from "next/link";
import { TriangleAlert } from "lucide-react";
import { AVERTISSEMENT_COURT } from "@/contenu/legal";

const COLONNES: { titre: string; lignes: string[] }[] = [
  { titre: "Quant Terminal", lignes: ["Simulation prospective", "Comparaison de scénarios", "Backtest historique", "Académie financière", "Analyste IA"] },
  { titre: "Données & sources", lignes: ["Yahoo Finance (cours de clôture)", "BCE (taux de change officiels)", "OpenAI (analyse IA)", "23 actifs · 6 catégories + tickers libres"] },
  { titre: "Méthodologie", lignes: ["Volatilités et corrélations réelles", "Monte-Carlo (1 000 trajectoires)", "Métriques de risque institutionnelles", "Calibration sur crises historiques"] },
  { titre: "Équipe", lignes: ["Quentin Geldreich", "Lukha Doazan", "Evan Saadi", "Alex Ruimy"] },
  { titre: "Mentions", lignes: ["Outil pédagogique", "Université Paris Nanterre", "Licence MIASHS · L1 S2", "Projet 2026"] },
];

const LIENS_LEGAUX = [
  { href: "/mentions-legales", libelle: "Mentions légales" },
  { href: "/cgu", libelle: "CGU" },
  { href: "/confidentialite", libelle: "Confidentialité" },
  { href: "/faq", libelle: "FAQ" },
  { href: "/contact", libelle: "Contact" },
  { href: "/academie#methodologie", libelle: "Méthodologie" },
];

const CLASSE_LIEN = "underline decoration-transparent underline-offset-2 transition-colors hover:text-ink hover:decoration-line-strong";

export function PiedDePage() {
  return (
    <footer className="mt-12 border-t border-line bg-surface">
      <div className="mx-auto max-w-[1400px] px-4 py-10 sm:px-6">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:grid-cols-5">
          {COLONNES.map((c) => (
            <div key={c.titre}>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">{c.titre}</h2>
              <ul className="mt-3 flex flex-col gap-1.5 text-sm text-ink-2">
                {c.lignes.map((l) => (
                  <li key={l}>{l}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-8 flex gap-3 rounded-xl border border-warn/30 bg-warn-soft px-4 py-3 text-xs leading-relaxed text-ink-2">
          <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
          <p>
            <strong className="font-semibold text-ink">{AVERTISSEMENT_COURT}</strong> — Quant Terminal est un outil pédagogique développé dans un cadre
            universitaire. Les simulations et analyses présentées sont des estimations produites par un modèle mathématique et une intelligence
            artificielle : elles ne constituent ni un conseil en investissement, ni une recommandation d&apos;achat ou de vente. Les performances passées
            ne préjugent pas des performances futures. Les utilisateurs sont seuls responsables de leurs décisions d&apos;investissement.{" "}
            <Link href="/cgu#avertissement" className="font-medium text-ink underline decoration-warn/50 underline-offset-2 hover:decoration-warn">
              Lire l&apos;avertissement complet
            </Link>
          </p>
        </div>
        <div className="mt-6 flex flex-col gap-3 text-xs text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>© 2026 Quant Terminal · Université Paris Nanterre</p>
          <nav aria-label="Informations légales et aide">
            <ul className="flex flex-wrap gap-x-4 gap-y-2">
              {LIENS_LEGAUX.map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className={CLASSE_LIEN}>
                    {l.libelle}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </div>
    </footer>
  );
}
