import { ImageResponse } from "next/og";

// Image de partage (réseaux sociaux, messageries), générée une fois au build.
// ImageResponse ne lit pas les variables CSS : les couleurs reprennent les jetons
// du thème sombre de globals.css (--bg, --surface, --ink, --ink-2, --muted, --line,
// --accent, --accent-ink) et celles du logo.

export const alt = "Quant Terminal — simulez l’impact d’un événement économique sur votre portefeuille";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const C = {
  bg: "#0b0b0e",
  surface: "#131316",
  ink: "#f2f2f4",
  ink2: "#b6b8c3",
  muted: "#959aa8",
  line: "#25252c",
  accent: "#5b5fe3",
  accentInk: "#a3a6f7",
  logoDebut: "#5c70e6",
  logoFin: "#1fbc91",
};

// Courbe décorative : une chute puis une reprise, comme une trajectoire simulée.
const POINTS = [
  [0, 120], [40, 112], [80, 128], [120, 104], [160, 150], [200, 212], [240, 236], [280, 198], [320, 214],
  [360, 168], [400, 150], [440, 160], [480, 118], [520, 96], [560, 104], [600, 66], [640, 52],
];
const LIGNE = POINTS.map(([x, y], i) => `${i ? "L" : "M"}${x} ${y}`).join(" ");
const AIRE = `${LIGNE} L640 280 L0 280 Z`;

const PASTILLES = ["Vrais cours", "Analyse par IA", "Monte-Carlo", "Backtests"];

export default function Image() {
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", background: C.bg, padding: "64px 72px", color: C.ink }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <svg width="64" height="64" viewBox="0 0 64 64">
            <defs>
              <linearGradient id="logo" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor={C.logoDebut} />
                <stop offset="1" stopColor={C.logoFin} />
              </linearGradient>
            </defs>
            <rect width="64" height="64" rx="16" fill="url(#logo)" />
            <path d="M14 44 L25 35 L35 38 L44 26 L50 20" fill="none" stroke="#f5fafb" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="50" cy="19" r="6" fill="#ffffff" />
          </svg>
          <div style={{ fontSize: 34, letterSpacing: -0.5 }}>Quant Terminal</div>
          <div style={{ marginLeft: "auto", fontSize: 22, color: C.muted }}>quant-terminal-qg-team.vercel.app</div>
        </div>

        <div style={{ display: "flex", flex: 1, alignItems: "center", gap: 48, marginTop: 24 }}>
          <div style={{ display: "flex", flexDirection: "column", width: 560 }}>
            <div style={{ fontSize: 60, lineHeight: 1.08, letterSpacing: -2 }}>Et si l’économie basculait demain ?</div>
            <div style={{ fontSize: 26, lineHeight: 1.45, color: C.ink2, marginTop: 24 }}>
              Simulez l’impact d’un événement économique sur votre portefeuille, avec de vrais cours et une analyse par IA.
            </div>
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              width: 452,
              height: 300,
              background: C.surface,
              border: `1px solid ${C.line}`,
              borderRadius: 24,
              padding: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 18, color: C.muted }}>
              <span>Trajectoire simulée</span>
              <span>en euros</span>
            </div>
            <svg width="404" height="200" viewBox="0 0 652 280" style={{ marginTop: 20 }}>
              <defs>
                <linearGradient id="aire" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stopColor={C.accent} stopOpacity="0.45" />
                  <stop offset="1" stopColor={C.accent} stopOpacity="0" />
                </linearGradient>
              </defs>
              <path d={AIRE} fill="url(#aire)" />
              <path d={LIGNE} fill="none" stroke={C.accentInk} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="640" cy="52" r="9" fill={C.accentInk} />
            </svg>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {PASTILLES.map((p) => (
            <div key={p} style={{ display: "flex", fontSize: 20, color: C.ink2, border: `1px solid ${C.line}`, borderRadius: 999, padding: "8px 18px" }}>
              {p}
            </div>
          ))}
          <div style={{ marginLeft: "auto", fontSize: 20, color: C.muted }}>Projet étudiant · Université Paris Nanterre</div>
        </div>
      </div>
    ),
    { ...size },
  );
}
