import { Suspense } from "react";
import { Simulateur } from "@/components/Simulateur";

export default function Accueil() {
  // Suspense : le simulateur lit l'adresse (lien de partage) cote client.
  return (
    <Suspense>
      <Simulateur />
    </Suspense>
  );
}
