import type { Metadata } from "next";
import { EnConstruction } from "@/components/ui/EnConstruction";

export const metadata: Metadata = { title: "Académie — Quant Terminal" };

export default function Page() {
  return <EnConstruction titre="Académie" description="Les notions de finance expliquées simplement." />;
}
