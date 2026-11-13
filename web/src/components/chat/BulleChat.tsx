"use client";

import { useEffect, useId, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { BotMessageSquare } from "lucide-react";
import { discuter, ErreurApi } from "@/lib/api";
import { retirerContexteChat, useContexteChat } from "@/lib/contexteChat";
import { RESSORT } from "@/components/motion/transitions";
import {
  ajouterMessage,
  effacerConversation,
  lireConversation,
  LONGUEUR_MAX,
  messagesPourApi,
  useConversation,
  type MessageConversation,
} from "./conversation";
import { PanneauChat } from "./PanneauChat";

const ERREUR_GENERIQUE = "L'analyste n'a pas pu répondre. Réessayez dans un instant.";
const SANS_REPONSE = "La réponse à votre dernière question n'est pas arrivée.";

/**
 * Bulle flottante de l'analyste IA (en bas a droite, sur toutes les pages) et son panneau de discussion.
 * La requete vit ici et non dans le panneau : fermer le panneau ne perd pas la reponse en cours.
 */
export function BulleChat() {
  const messages = useConversation();
  const contexte = useContexteChat();
  const [ouvert, setOuvert] = useState(false);
  const [enAttente, setEnAttente] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [nonLu, setNonLu] = useState(false);
  const [brouillon, setBrouillon] = useState("");
  const idPanneau = useId();
  const bulleRef = useRef<HTMLButtonElement>(null);
  const ouvertRef = useRef(false);
  const etaitOuvert = useRef(false);
  // Numero de la requete en cours : une reponse arrivee apres un effacement est ignoree.
  const requete = useRef(0);

  // Le focus revient sur la bulle a la fermeture du panneau.
  useEffect(() => {
    if (etaitOuvert.current && !ouvert) bulleRef.current?.focus({ preventScroll: true });
    etaitOuvert.current = ouvert;
  }, [ouvert]);

  function ouvrir() {
    ouvertRef.current = true;
    setOuvert(true);
    setNonLu(false);
  }

  function fermer() {
    ouvertRef.current = false;
    setOuvert(false);
  }

  async function envoyer(conversation: MessageConversation[]) {
    const numero = ++requete.current;
    setEnAttente(true);
    setErreur(null);
    try {
      const { reponse } = await discuter(messagesPourApi(conversation), contexte?.texte);
      if (numero !== requete.current) return;
      if (typeof reponse !== "string" || !reponse.trim()) {
        setErreur(ERREUR_GENERIQUE);
      } else if (reponse.startsWith("❌")) {
        // L'API renvoie certaines erreurs OpenAI (delai, quota) comme un texte prefixe de ❌.
        setErreur(reponse.replace(/^❌\s*/, ""));
      } else {
        ajouterMessage({ role: "assistant", content: reponse });
        if (!ouvertRef.current) setNonLu(true);
      }
    } catch (e) {
      if (numero !== requete.current) return;
      setErreur(e instanceof ErreurApi ? e.message : ERREUR_GENERIQUE);
    } finally {
      if (numero === requete.current) setEnAttente(false);
    }
  }

  function poser(question: string) {
    const texte = question.trim().slice(0, LONGUEUR_MAX);
    if (!texte || enAttente) return;
    setBrouillon("");
    void envoyer(ajouterMessage({ role: "user", content: texte }));
  }

  function reessayer() {
    if (!enAttente) void envoyer(lireConversation());
  }

  function effacer() {
    requete.current++;
    setEnAttente(false);
    setErreur(null);
    effacerConversation();
  }

  // Question restee sans reponse (page rechargee pendant l'attente) : on propose de la renvoyer.
  const erreurAffichee = erreur ?? (!enAttente && messages.at(-1)?.role === "user" ? SANS_REPONSE : null);

  return (
    <>
      <motion.button
        ref={bulleRef}
        type="button"
        onClick={ouvert ? fermer : ouvrir}
        aria-label={ouvert ? "Réduire l'analyste IA" : nonLu ? "Ouvrir l'analyste IA : nouvelle réponse" : "Ouvrir l'analyste IA"}
        aria-haspopup="dialog"
        aria-expanded={ouvert}
        aria-controls={ouvert ? idPanneau : undefined}
        // Cachee derriere le panneau quand il est ouvert : on la sort de l'ordre de tabulation.
        tabIndex={ouvert ? -1 : undefined}
        initial={{ scale: 0.6, opacity: 0 }}
        animate={ouvert ? { scale: 0.5, opacity: 0 } : { scale: 1, opacity: 1 }}
        whileTap={{ scale: 0.97 }}
        transition={RESSORT}
        // Sous lg, le bouton "Lancer" du simulateur est colle en bas de l'ecran : la bulle se tient au-dessus.
        className={`group fixed bottom-[calc(5.75rem+env(safe-area-inset-bottom))] right-4 z-40 grid size-12 place-items-center rounded-full bg-accent text-on-accent shadow-[0_10px_28px_-8px_color-mix(in_oklab,var(--accent)_75%,transparent)] sm:size-14 lg:bottom-6 lg:right-6 ${ouvert ? "pointer-events-none" : ""}`}
      >
        {/* Invitation : une pulsation douce, une seule fois apres le chargement. */}
        <motion.span
          aria-hidden
          className="pointer-events-none absolute inset-0 rounded-full bg-accent"
          initial={{ opacity: 0, scale: 1 }}
          animate={{ opacity: [0, 0.45, 0], scale: [1, 1.15, 1.9] }}
          transition={{ duration: 1.8, delay: 1.4, ease: "easeOut", times: [0, 0.15, 1] }}
        />
        <BotMessageSquare className="relative size-[22px] sm:size-6" aria-hidden />
        <AnimatePresence>
          {nonLu && (
            <motion.span
              aria-hidden
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={RESSORT}
              className="absolute right-0 top-0 size-3.5 rounded-full bg-(--series-2) ring-2 ring-bg"
            />
          )}
        </AnimatePresence>
        <span className="pointer-events-none absolute right-full top-1/2 mr-3 hidden -translate-y-1/2 translate-x-1 whitespace-nowrap rounded-controle bg-ink px-2.5 py-1.5 text-xs font-medium text-bg opacity-0 shadow-lg transition duration-200 group-hover:translate-x-0 group-hover:opacity-100 group-focus-visible:translate-x-0 group-focus-visible:opacity-100 sm:block">
          {nonLu ? "Nouvelle réponse de l'analyste" : "Une question ? L'analyste IA"}
        </span>
      </motion.button>

      <AnimatePresence>
        {ouvert && (
          <PanneauChat
            key="panneau-chat"
            id={idPanneau}
            messages={messages}
            enAttente={enAttente}
            erreur={erreurAffichee}
            brouillon={brouillon}
            onBrouillon={setBrouillon}
            onPoser={poser}
            onReessayer={reessayer}
            onEffacer={effacer}
            onFermer={fermer}
            contexte={contexte?.titre ?? null}
            onRetirerContexte={retirerContexteChat}
          />
        )}
      </AnimatePresence>
    </>
  );
}
