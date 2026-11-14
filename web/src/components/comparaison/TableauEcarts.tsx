import type { ResultatScenario } from "@/lib/api";
import { euros, nombreSigne, pourcent, pourcentSigne } from "@/lib/format";
import { Carte, TitreCarte } from "@/components/ui/Carte";

type Ligne = {
  nom: string;
  valeur: (s: ResultatScenario) => number;
  format: (v: number) => string;
  /** Ecart B - A affiche (meme unite que la valeur, ou points de % pour une performance). */
  formatEcart: (v: number) => string;
  plusGrandEstMieux: boolean;
};

const LIGNES: Ligne[] = [
  { nom: "Valeur finale", valeur: (s) => s.portefeuille.valeur_finale, format: (v) => euros(v), formatEcart: (v) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${euros(Math.abs(v))}`, plusGrandEstMieux: true },
  { nom: "Performance", valeur: (s) => s.portefeuille.performance_pct, format: (v) => pourcentSigne(v, 2), formatEcart: (v) => `${nombreSigne(v)} pt`, plusGrandEstMieux: true },
  { nom: "Volatilité annualisée", valeur: (s) => s.metriques.vol_ann, format: (v) => pourcent(v, 2), formatEcart: (v) => `${nombreSigne(v)} pt`, plusGrandEstMieux: false },
  { nom: "Ratio de Sharpe", valeur: (s) => s.metriques.sharpe, format: (v) => nombreSigne(v), formatEcart: (v) => nombreSigne(v), plusGrandEstMieux: true },
  { nom: "VaR 95 % (1 jour)", valeur: (s) => Math.abs(s.metriques.var_95), format: (v) => `−${pourcent(v, 2)}`, formatEcart: (v) => `${nombreSigne(v)} pt`, plusGrandEstMieux: false },
  { nom: "Perte maximale", valeur: (s) => Math.abs(s.metriques.max_dd), format: (v) => `−${pourcent(v, 2)}`, formatEcart: (v) => `${nombreSigne(v)} pt`, plusGrandEstMieux: false },
];

const SEUIL_EGALITE = 1e-9;

/** Metriques des deux portefeuilles, et ce que B gagne ou perd par rapport a A. */
export function TableauEcarts({ a, b }: { a: ResultatScenario; b: ResultatScenario }) {
  return (
    <Carte taille="normale">
      <TitreCarte aide="L'écart se lit « B moins A » ; vert = B fait mieux, rouge = B fait moins bien.">Résultats côte à côte</TitreCarte>
      <div tabIndex={0} className="overflow-x-auto">
        <table className="w-full text-sm tabular-nums">
          <thead className="text-xs text-muted">
            <tr>
              <th className="pb-2 pr-2 text-left font-medium">Métrique</th>
              <th className="pb-2 pl-2 text-right font-medium">A</th>
              <th className="pb-2 pl-2 text-right font-medium">B</th>
              <th className="pb-2 pl-2 text-right font-medium">Écart</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {LIGNES.map((l) => {
              const va = l.valeur(a);
              const vb = l.valeur(b);
              const ecart = vb - va;
              const egal = Math.abs(ecart) < SEUIL_EGALITE;
              const meilleur = l.plusGrandEstMieux ? ecart > 0 : ecart < 0;
              return (
                <tr key={l.nom}>
                  <th scope="row" className="py-2.5 pr-2 text-left font-normal text-ink-2">
                    {l.nom}
                  </th>
                  <td className="py-2.5 pl-2 text-right">{l.format(va)}</td>
                  <td className="py-2.5 pl-2 text-right">{l.format(vb)}</td>
                  <td className={`py-2.5 pl-2 text-right font-medium ${egal ? "text-muted" : meilleur ? "text-gain" : "text-loss"}`}>{egal ? "=" : l.formatEcart(ecart)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Carte>
  );
}
