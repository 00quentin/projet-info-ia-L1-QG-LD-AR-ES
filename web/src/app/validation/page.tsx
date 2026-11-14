import type { Metadata } from "next";
import { PageValidation } from "@/components/validation/PageValidation";

export const metadata: Metadata = {
  title: "L'IA à l'épreuve de l'histoire — Quant Terminal",
  description:
    "Les chocs estimés par l'IA comparés aux vrais cours de dizaines d'événements de marché passés (grandes crises, décisions de banques centrales, élections, chocs pétroliers…), décrits sans être nommés ni datés.",
};

export default function Page() {
  return <PageValidation />;
}
