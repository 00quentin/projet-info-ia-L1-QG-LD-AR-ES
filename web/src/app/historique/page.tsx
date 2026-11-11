import type { Metadata } from "next";
import { EnConstruction } from "@/components/ui/EnConstruction";

export const metadata: Metadata = { title: "Historique — Quant Terminal" };

export default function Page() {
  return <EnConstruction titre="Historique" description="Retrouvez vos simulations précédentes." />;
}
