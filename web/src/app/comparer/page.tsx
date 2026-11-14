import type { Metadata } from "next";
import { PageComparaison } from "@/components/comparaison/PageComparaison";

export const metadata: Metadata = {
  title: "Comparer deux portefeuilles",
  description: "Deux portefeuilles face au même scénario économique, côte à côte : valeur finale, volatilité, Sharpe, VaR et perte maximale, avec une seule analyse de l'IA.",
};

export default function Page() {
  return <PageComparaison />;
}
