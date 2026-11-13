// Lien de partage d'une simulation : les reglages sont encodes dans l'adresse.
// Format compatible avec l'ancienne app Streamlit pour s, s2, s3, nb et p.

export type ReglagesPartages = {
  scenarios: string[];
  profil?: string;
  capital?: number;
  actifs?: string[];
  allocations?: Record<string, number>;
  tickersPerso?: string[];
  duree?: number;
  modele?: string;
  monteCarlo?: boolean;
  convertirEur?: boolean;
  calibration?: boolean;
  prixReels?: boolean;
};

const SCENARIO_LONGUEUR_MAX = 1000;
const binaire = (v: boolean | undefined) => (v === undefined ? null : v ? "1" : "0");

export function encoderReglages(r: ReglagesPartages): string {
  const p = new URLSearchParams();
  const [s1, s2, s3] = r.scenarios;
  if (s1) p.set("s", s1);
  if (s2) p.set("s2", s2);
  if (s3) p.set("s3", s3);
  if (r.scenarios.length > 1) p.set("nb", String(r.scenarios.length));
  if (r.profil) p.set("p", r.profil);
  if (r.capital) p.set("c", String(r.capital));
  if (r.actifs?.length) p.set("a", r.actifs.join(","));
  if (r.allocations && Object.keys(r.allocations).length)
    p.set("al", Object.entries(r.allocations).map(([k, v]) => `${k}:${v}`).join(","));
  if (r.tickersPerso?.length) p.set("t", r.tickersPerso.join(","));
  if (r.duree) p.set("h", String(r.duree));
  if (r.modele) p.set("m", r.modele);
  for (const [cle, v] of [["mc", r.monteCarlo], ["eur", r.convertirEur], ["cal", r.calibration], ["px", r.prixReels]] as const) {
    const b = binaire(v);
    if (b) p.set(cle, b);
  }
  return p.toString();
}

export function lienDePartage(r: ReglagesPartages, chemin = "/"): string {
  const base = typeof window === "undefined" ? "" : window.location.origin;
  return `${base}${chemin}?${encoderReglages(r)}`;
}

/** Lit les reglages d'une adresse. Les valeurs inconnues sont ignorees, jamais executees. */
export function decoderReglages(params: URLSearchParams): ReglagesPartages | null {
  const s = params.get("s");
  if (!s) return null;
  const nb = Math.min(3, Math.max(1, Number(params.get("nb")) || 1));
  const scenarios = [s, params.get("s2") ?? "", params.get("s3") ?? ""].slice(0, nb).map((x) => x.slice(0, SCENARIO_LONGUEUR_MAX));
  const nombre = (cle: string) => {
    const v = Number(params.get(cle));
    return Number.isFinite(v) && v > 0 ? v : undefined;
  };
  const liste = (cle: string) => params.get(cle)?.split(",").map((x) => x.trim()).filter(Boolean);
  const bool = (cle: string) => (params.has(cle) ? params.get(cle) === "1" : undefined);
  const allocations = liste("al")?.reduce<Record<string, number>>((acc, paire) => {
    const i = paire.lastIndexOf(":");
    const v = Number(paire.slice(i + 1));
    if (i > 0 && Number.isFinite(v)) acc[paire.slice(0, i)] = v;
    return acc;
  }, {});
  return {
    scenarios,
    profil: params.get("p") ?? undefined,
    capital: nombre("c"),
    actifs: liste("a"),
    allocations,
    tickersPerso: liste("t"),
    duree: nombre("h"),
    modele: params.get("m") ?? undefined,
    monteCarlo: bool("mc"),
    convertirEur: bool("eur"),
    calibration: bool("cal"),
    prixReels: bool("px"),
  };
}
