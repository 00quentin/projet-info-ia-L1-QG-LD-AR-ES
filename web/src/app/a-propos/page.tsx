import type { Metadata } from "next";
import { EnConstruction } from "@/components/ui/EnConstruction";

export const metadata: Metadata = { title: "À propos — Quant Terminal" };

export default function Page() {
  return <EnConstruction titre="À propos" description="Le projet Quant Terminal et son équipe." />;
}
