import type { Metadata } from "next";
import { EnConstruction } from "@/components/ui/EnConstruction";

export const metadata: Metadata = { title: "Backtest historique — Quant Terminal" };

export default function Page() {
  return <EnConstruction titre="Backtest historique" description="Rejouez votre portefeuille sur une vraie crise passée." />;
}
