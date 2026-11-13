import type { Metadata } from "next";
import { MessageCircleQuestionMark } from "lucide-react";
import { ListeQuestions } from "@/components/legal/Accordeon";
import { Lien, Rubrique } from "@/components/legal/blocs";
import { PageLegale } from "@/components/legal/PageLegale";
import { FAQ, TOUTES_LES_QUESTIONS } from "@/contenu/faq";

export const metadata: Metadata = {
  title: "Questions fréquentes",
  description:
    "D’où viennent les données, comment l’IA estime un scénario, pourquoi les chiffres changent, Monte-Carlo, conversion en euros, confidentialité : les réponses.",
  alternates: { canonical: "/faq" },
};

// Données structurées : la FAQ telle que la lisent les moteurs de recherche.
const JSON_LD = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  inLanguage: "fr-FR",
  mainEntity: TOUTES_LES_QUESTIONS.map((q) => ({
    "@type": "Question",
    name: q.question,
    acceptedAnswer: { "@type": "Answer", text: q.reponse.join("\n\n") },
  })),
};

export default function Page() {
  return (
    <PageLegale
      icone={MessageCircleQuestionMark}
      etiquette="Aide"
      titre="Questions fréquentes"
      sommaire={FAQ.map((t) => ({ id: t.id, titre: t.titre }))}
      avecMiseAJour={false}
      chapeau={
        <p>
          Les réponses aux questions qu’on nous pose le plus souvent. Vous ne trouvez pas la vôtre ? <Lien href="/contact">Écrivez-nous</Lien>.
        </p>
      }
    >
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD).replace(/</g, "\\u003c") }} />
      {FAQ.map((t) => (
        <Rubrique key={t.id} id={t.id} titre={t.titre}>
          <ListeQuestions questions={t.questions} />
        </Rubrique>
      ))}
    </PageLegale>
  );
}
