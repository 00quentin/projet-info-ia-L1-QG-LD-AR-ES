import { TriangleAlert } from "lucide-react";

const COLONNES: { titre: string; lignes: string[] }[] = [
  { titre: "Quant Terminal", lignes: ["Simulation prospective", "Comparaison de scénarios", "Backtest historique", "Académie financière", "Analyste IA"] },
  { titre: "Données & sources", lignes: ["Yahoo Finance (cours de clôture)", "BCE (taux de change officiels)", "OpenAI (analyse IA)", "23 actifs · 6 catégories + tickers libres"] },
  { titre: "Méthodologie", lignes: ["Volatilités et corrélations réelles", "Monte-Carlo (1 000 trajectoires)", "Métriques de risque institutionnelles", "Calibration sur crises historiques"] },
  { titre: "Équipe", lignes: ["Quentin Geldreich", "Lukha Doazan", "Evan Saadi", "Alex Ruimy"] },
  { titre: "Mentions", lignes: ["Outil pédagogique", "Université Paris Nanterre", "Licence MIASHS · L1 S2", "Projet 2026"] },
];

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
            <strong className="font-semibold text-ink">Avertissement</strong> — Quant Terminal est un outil pédagogique développé dans un cadre universitaire. Les simulations et analyses présentées ne constituent pas un conseil en investissement, ni une recommandation d&apos;achat ou de vente. Les performances passées ne préjugent pas des performances futures. Les utilisateurs sont seuls responsables de leurs décisions d&apos;investissement.
          </p>
        </div>
        <p className="mt-6 text-xs text-muted">© 2026 Quant Terminal · Université Paris Nanterre</p>
      </div>
    </footer>
  );
}
