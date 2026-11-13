"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Loader2, RotateCw, ServerOff } from "lucide-react";
import { API_URL, ErreurApi } from "@/lib/api";
import { Carte } from "@/components/ui/Carte";

// L'hebergement gratuit de l'API s'endort apres 15 min sans visite et met 30 a 60 s a repartir :
// au lieu d'une erreur, on attend honnetement en interrogeant /api/sante.
const INTERVALLE_PING_MS = 3000;
const DELAI_PING_MS = 8000;
const ABANDON_MS = 90_000;
const DUREE_ANNONCEE_S = 30;
const PROGRESSION_MAX = 0.95;

/** Diffuse quand le serveur repond de nouveau : les autres blocs (bandeau des cours) se rechargent. */
export const EVENEMENT_SERVEUR_PRET = "qt-serveur-pret";

/** Erreur typique d'un serveur endormi ou en train de redemarrer (pas de reponse, passerelle). */
export function serveurEndormi(e: unknown): boolean {
  return e instanceof ErreurApi && [0, 502, 503, 504].includes(e.statut);
}

async function serveurRepond(): Promise<boolean> {
  const controle = new AbortController();
  const minuterie = setTimeout(() => controle.abort(), DELAI_PING_MS);
  try {
    const r = await fetch(`${API_URL}/api/sante`, { cache: "no-store", signal: controle.signal });
    return r.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(minuterie);
  }
}

const attendre = (ms: number) => new Promise((ok) => setTimeout(ok, ms));

/**
 * Etat d'attente pendant le demarrage du serveur : relance toute seule `onPret` des qu'il repond,
 * abandonne proprement apres 90 s (bouton Reessayer).
 */
export function ReveilServeur({ onPret, action }: { onPret: () => void; action?: ReactNode }) {
  const [essai, setEssai] = useState(0);
  const [ecoule, setEcoule] = useState(0);
  const [abandon, setAbandon] = useState(false);
  const pret = useRef(onPret);
  useEffect(() => {
    pret.current = onPret;
  });

  useEffect(() => {
    let actif = true;
    const debut = Date.now();
    const chrono = setInterval(() => setEcoule(Math.round((Date.now() - debut) / 1000)), 1000);
    (async () => {
      while (actif && Date.now() - debut < ABANDON_MS) {
        const ok = await serveurRepond();
        if (!actif) return;
        if (ok) {
          window.dispatchEvent(new Event(EVENEMENT_SERVEUR_PRET));
          pret.current();
          return;
        }
        await attendre(INTERVALLE_PING_MS);
      }
      if (actif) setAbandon(true);
    })();
    return () => {
      actif = false;
      clearInterval(chrono);
    };
  }, [essai]);

  function reessayer() {
    setAbandon(false);
    setEcoule(0);
    setEssai((n) => n + 1);
  }

  const progression = Math.min(PROGRESSION_MAX, ecoule / (DUREE_ANNONCEE_S * 1.2));

  return (
    <Carte taille="normale">
      <div role="status" aria-live="polite" className="flex items-start gap-3">
        {abandon ? <ServerOff className="mt-0.5 size-5 shrink-0 text-warn" aria-hidden /> : <Loader2 className="mt-0.5 size-5 shrink-0 animate-spin text-accent-ink" aria-hidden />}
        <div className="min-w-0 flex-1">
          <h2 className="text-titre font-semibold">{abandon ? "Le serveur ne répond toujours pas" : `Démarrage du serveur (≈ ${DUREE_ANNONCEE_S} s)…`}</h2>
          <p className="mt-1 text-aide leading-relaxed text-ink-2">
            {abandon
              ? "Vérifiez votre connexion, puis réessayez dans un instant."
              : "Le serveur gratuit se met en veille quand personne ne l'utilise. Il redémarre : la page se mettra à jour toute seule."}
          </p>
        </div>
      </div>
      {!abandon && (
        <div className="mt-4 flex items-center gap-3" aria-hidden>
          <div className="h-1 flex-1 overflow-hidden rounded-full bg-surface-2">
            <div className="h-full origin-left rounded-full bg-accent transition-transform duration-1000 ease-linear" style={{ transform: `scaleX(${progression})` }} />
          </div>
          <span className="w-10 text-right text-xs tabular-nums text-muted">{ecoule} s</span>
        </div>
      )}
      {(abandon || action) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {abandon && (
            <button type="button" onClick={reessayer} className="inline-flex items-center gap-2 rounded-controle border border-line px-3 py-2 text-sm font-medium transition-colors hover:border-line-strong">
              <RotateCw className="size-4" aria-hidden />
              Réessayer
            </button>
          )}
          {action}
        </div>
      )}
    </Carte>
  );
}
