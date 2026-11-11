import { BandeMarches } from "@/components/BandeMarches";
import { EnTete } from "@/components/EnTete";
import { Simulateur } from "@/components/Simulateur";

export default function Accueil() {
  return (
    <>
      {/* En-tete et cours restent visibles au defilement sur grand ecran */}
      <div className="z-30 lg:sticky lg:top-0">
        <EnTete />
        <BandeMarches />
      </div>
      <Simulateur />
    </>
  );
}
