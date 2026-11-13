"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { ImageOff } from "lucide-react";
import { DUREE, EASE_SORTIE } from "@/components/motion/transitions";

// Special:FilePath suit la redirection vers le bon fichier et le redimensionne.
const WIKIMEDIA = "https://commons.wikimedia.org/wiki/Special:FilePath";

type PropsImage = { fichier: string; alt: string; largeur?: number; className?: string; onCassee: () => void };

/** Image Wikimedia Commons ; prévient son parent si elle ne charge pas. */
export function ImageWikimedia({ fichier, alt, largeur = 800, className = "", onCassee }: PropsImage) {
  return (
    // Images servies et redimensionnées par Wikimedia : l'optimiseur de Next n'apporte rien ici.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      // L'image a pu échouer avant l'hydratation : onError ne se déclencherait alors jamais.
      ref={(img) => {
        if (img && img.complete && img.naturalWidth === 0) onCassee();
      }}
      src={`${WIKIMEDIA}/${encodeURIComponent(fichier)}?width=${largeur}`}
      alt={alt}
      loading="lazy"
      decoding="async"
      onError={onCassee}
      className={className}
    />
  );
}

type Props = {
  fichier: string;
  alt: string;
  legende: string;
  credit: string;
};

/** Photo d'archive avec légende et crédit. Si l'image ne charge pas, seule la légende reste. */
export function Photo({ fichier, alt, legende, credit }: Props) {
  const [cassee, setCassee] = useState(false);
  return (
    <figure className="max-w-[46rem]">
      {!cassee && (
        <motion.div
          className="chargement aspect-[16/9] overflow-hidden rounded-carte border border-line shadow-card"
          initial={{ opacity: 0, scale: 0.985 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "0px 0px -40px 0px" }}
          transition={{ duration: DUREE.lente, ease: EASE_SORTIE }}
        >
          <ImageWikimedia
            fichier={fichier}
            alt={alt}
            onCassee={() => setCassee(true)}
            className="relative block size-full object-cover"
          />
        </motion.div>
      )}
      <figcaption className={`flex gap-2 text-sm leading-relaxed text-muted ${cassee ? "" : "mt-2.5"}`}>
        {cassee && <ImageOff className="mt-0.5 size-4 shrink-0" aria-hidden />}
        <span>
          {legende} <span className="text-xs opacity-80">· {credit}</span>
        </span>
      </figcaption>
    </figure>
  );
}
