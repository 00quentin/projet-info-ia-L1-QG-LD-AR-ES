import { prix } from "@/lib/format";

// Unite affichee a cote d'un cours : un indice se lit en points, un taux de change se passe d'unite.
const INDICES = new Set(["S&P 500", "NASDAQ", "CAC 40", "VIX", "Dollar_Index"]);
const TAUX_DE_CHANGE = new Set(["EUR_USD"]);
const SYMBOLES: Record<string, string> = { USD: "$", EUR: "€", GBP: "£", JPY: "¥", CHF: "CHF" };

export function uniteCours(cle: string, devise: string | null | undefined): string | null {
  if (TAUX_DE_CHANGE.has(cle)) return null;
  if (INDICES.has(cle)) return "pts";
  return devise ? (SYMBOLES[devise] ?? devise) : null;
}

/** Cours avec son unite en petit : « 3 898 $ », « 7 592 pts », « 1,1053 ». */
export function Prix({ valeur, unite, className = "" }: { valeur: number; unite: string | null; className?: string }) {
  return (
    <span className={`whitespace-nowrap tabular-nums ${className}`}>
      {prix(valeur)}
      {unite && <span className="ml-0.5 text-xs font-normal text-muted">{unite}</span>}
    </span>
  );
}
