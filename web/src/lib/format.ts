// Formats d'affichage francais (espaces fines insecables, virgule decimale).

const euros0 = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
const euros2 = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", minimumFractionDigits: 2, maximumFractionDigits: 2 });
const compact = new Intl.NumberFormat("fr-FR", { notation: "compact", maximumFractionDigits: 1 });

export function euros(valeur: number, decimales = false): string {
  return (decimales ? euros2 : euros0).format(valeur);
}

export function eurosCompacts(valeur: number): string {
  return `${compact.format(valeur)} €`;
}

/** Pourcentage signe : +4,1 % / −7,5 % (vrai signe moins typographique). */
export function pourcentSigne(valeur: number, decimales = 1): string {
  const abs = Math.abs(valeur).toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
  const signe = valeur > 0 ? "+" : valeur < 0 ? "−" : "";
  return `${signe}${abs} %`;
}

export function pourcent(valeur: number, decimales = 1): string {
  return `${valeur.toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales })} %`;
}

/** Nombre signe avec un vrai signe moins typographique : −2,87 / 1,32. */
export function nombreSigne(valeur: number, decimales = 2): string {
  const abs = Math.abs(valeur).toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
  return valeur < 0 ? `−${abs}` : abs;
}

export function nombre(valeur: number, decimales = 2): string {
  return valeur.toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
}

/** Prix de marche : precision adaptee a l'ordre de grandeur (1,1169 / 86,43 / 73 312). */
export function prix(valeur: number): string {
  const abs = Math.abs(valeur);
  const decimales = abs >= 1000 ? 0 : abs >= 10 ? 2 : 4;
  return nombre(valeur, decimales);
}

/** "2026-11-10" -> "10/11/2026" */
export function dateFr(iso: string): string {
  const [a, m, j] = iso.split("-");
  return `${j}/${m}/${a}`;
}
