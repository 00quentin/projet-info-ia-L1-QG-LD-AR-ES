// Classes partagees par les formulaires (simulation, backtest).
/** Titre d'une etape du formulaire : 14 px, sans majuscules (docs/BENCHMARK.md F3). */
export const titreSection = "text-sm font-semibold text-ink";
export const champ =
  "w-full rounded-controle border border-line bg-surface px-3.5 py-2.5 text-sm outline-none transition-colors placeholder:text-muted focus:border-accent focus:ring-2 focus:ring-accent/20";
/** Petite puce cliquable (scenarios rapides, montants) : seule la couleur change au survol. */
export const puce =
  "rounded-full border border-line bg-surface px-3 py-1.5 text-aide font-medium text-ink-2 transition-colors hover:border-line-strong hover:text-ink aria-pressed:border-accent aria-pressed:bg-accent-soft aria-pressed:text-accent-ink";
/** Barre collante du bouton principal, calee sur la marge de la carte qui contient le formulaire. */
export const barreLancement =
  "sticky bottom-0 z-10 -mx-(--marge-carte) -mb-(--marge-carte) flex flex-col gap-2 rounded-b-carte border-t border-line bg-surface/95 px-(--marge-carte) py-4 backdrop-blur";
export const boutonPrincipal =
  "relative flex h-11 items-center justify-center gap-2 overflow-hidden rounded-controle bg-accent text-sm font-semibold text-white transition-[filter,opacity] hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50";
