import type { Metadata } from "next";
import { PageValidation } from "@/components/validation/PageValidation";

export const metadata: Metadata = {
  title: "L'IA à l'épreuve de l'histoire — Quant Terminal",
  description:
    "Les chocs estimés par l'IA comparés aux vrais cours de six crises passées (COVID-19, 2008, bulle internet…), décrites sans être nommées ni datées.",
};

export default function Page() {
  return <PageValidation />;
}
