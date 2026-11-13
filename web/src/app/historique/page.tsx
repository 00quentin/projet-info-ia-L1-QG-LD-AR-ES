import type { Metadata } from "next";
import { PageHistorique } from "@/components/historique/PageHistorique";

export const metadata: Metadata = { title: "Historique — Quant Terminal" };

export default function Page() {
  return <PageHistorique />;
}
