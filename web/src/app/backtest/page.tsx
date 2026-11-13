import type { Metadata } from "next";
import { Backtest } from "@/components/backtest/Backtest";

export const metadata: Metadata = {
  title: "Backtest historique",
  description: "Rejouez votre portefeuille sur une vraie crise passée (COVID-19, krach 2008, bulle internet…) avec les cours réels convertis en euros.",
};

export default function Page() {
  return <Backtest />;
}
