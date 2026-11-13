import katex from "katex";
import "katex/dist/katex.min.css";

// Rendu KaTeX côté serveur : le navigateur reçoit du HTML déjà mis en forme
// (pas de bibliothèque de maths à télécharger).

/** Formule centrée (équivalent de st.latex). */
export function Formule({ tex, description }: { tex: string; description?: string }) {
  const html = katex.renderToString(tex, { throwOnError: false, displayMode: true });
  return (
    <div
      className="formule max-w-[46rem] overflow-x-auto rounded-2xl border border-line bg-surface px-4 py-1 text-ink shadow-card transition-colors hover:border-line-strong [&_.katex-display]:my-4 [&_.katex]:text-[1.15em]"
      title={description}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

/** Formule dans le texte (le $...$ du markdown Streamlit). */
export function M({ tex }: { tex: string }) {
  const html = katex.renderToString(tex, { throwOnError: false, displayMode: false });
  return <span className="text-ink" dangerouslySetInnerHTML={{ __html: html }} />;
}
