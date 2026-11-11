import { Carte } from "@/components/ui/Carte";

/** Page provisoire, remplacee au fur et a mesure de la migration. */
export function EnConstruction({ titre, description }: { titre: string; description: string }) {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <Carte className="p-8 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">{titre}</h1>
        <p className="mt-2 text-ink-2">{description}</p>
      </Carte>
    </div>
  );
}
