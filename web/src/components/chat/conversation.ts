// Conversation avec l'analyste IA, gardee dans le navigateur du visiteur (localStorage).

import { useSyncExternalStore } from "react";
import type { MessageChat } from "@/lib/api";

/** Limites imposees par l'API (api/modeles.py). */
export const MESSAGES_MAX_API = 30;
export const LONGUEUR_MAX = 4000;
/** Au-dela, on ne garde que les messages les plus recents dans le navigateur. */
const MESSAGES_MAX_STOCKES = 100;

export type MessageConversation = MessageChat & { id: string };

const CLE = "qt-chat-v1";
const EVENEMENT = "qt-chat";
const VIDE: MessageConversation[] = [];

let cache: MessageConversation[] | null = null;

// crypto.randomUUID n'existe qu'en contexte securise (https, localhost).
const nouvelId = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

/** Message relu du stockage, ou null s'il est invalide (stockage modifie a la main, ancienne version). */
function normaliser(m: unknown, i: number): MessageConversation | null {
  if (typeof m !== "object" || m === null) return null;
  const { role, content, id } = m as Record<string, unknown>;
  if ((role !== "user" && role !== "assistant") || typeof content !== "string" || !content.trim()) return null;
  return { role, content, id: typeof id === "string" ? id : `ancien-${i}` };
}

function lire(): MessageConversation[] {
  if (cache) return cache;
  try {
    const brut = localStorage.getItem(CLE);
    const donnees: unknown = brut ? JSON.parse(brut) : [];
    cache = Array.isArray(donnees) ? donnees.map(normaliser).filter((m) => m !== null) : [];
  } catch {
    cache = [];
  }
  return cache;
}

function ecrire(messages: MessageConversation[]) {
  cache = messages.slice(-MESSAGES_MAX_STOCKES);
  try {
    if (cache.length) localStorage.setItem(CLE, JSON.stringify(cache));
    else localStorage.removeItem(CLE);
  } catch {
    /* stockage plein ou bloque (navigation privee) : la conversation vit le temps de la page */
  }
  window.dispatchEvent(new Event(EVENEMENT));
}

export function lireConversation(): MessageConversation[] {
  return typeof window === "undefined" ? VIDE : lire();
}

/** Ajoute un message et renvoie la conversation complete. */
export function ajouterMessage(message: MessageChat): MessageConversation[] {
  ecrire([...lire(), { ...message, id: nouvelId() }]);
  return lire();
}

export function effacerConversation(): void {
  ecrire([]);
}

/** Ce qu'on envoie a l'API : les derniers messages, sans champ en trop, longueur bornee. */
export function messagesPourApi(messages: MessageConversation[]): MessageChat[] {
  return messages.slice(-MESSAGES_MAX_API).map((m) => ({ role: m.role, content: m.content.slice(0, LONGUEUR_MAX) }));
}

function abonner(rappel: () => void) {
  // Un autre onglet a modifie la conversation : on relit le stockage.
  const surStockage = (e: StorageEvent) => {
    if (e.key !== CLE && e.key !== null) return;
    cache = null;
    rappel();
  };
  window.addEventListener(EVENEMENT, rappel);
  window.addEventListener("storage", surStockage);
  return () => {
    window.removeEventListener(EVENEMENT, rappel);
    window.removeEventListener("storage", surStockage);
  };
}

export function useConversation(): MessageConversation[] {
  return useSyncExternalStore(abonner, lire, () => VIDE);
}
