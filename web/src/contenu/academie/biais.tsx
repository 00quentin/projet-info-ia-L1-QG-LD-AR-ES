import { Apparition } from "@/components/motion/Apparition";
import { Antidote, Chapeau, Citation, Encadre, G, Liste, ListeEncadre, P, Point, Section } from "@/components/academie/blocs";
import { Photo } from "@/components/academie/Photo";
import { SyntheseBiais } from "@/components/academie/Syntheses";
import { sectionsDe } from "./modules";

const s = sectionsDe("biais");

export function ContenuBiais() {
  return (
    <>
      <Chapeau>
        Daniel Kahneman (Nobel d’économie 2002) a démontré que les humains ne sont <G>pas rationnels</G> face à l’argent. Notre cerveau utilise des
        heuristiques (raccourcis) qui marchent au quotidien mais qui sont <G>catastrophiques</G> en investissement. Les connaître, c’est déjà se
        protéger.
      </Chapeau>

      <Section {...s("aversion-perte")}>
        <P>
          <G>Découverte fondamentale de Kahneman &amp; Tversky (1979)</G> : la douleur de perdre 100€ est <G>psychologiquement deux fois plus intense</G>{" "}
          que le plaisir de gagner 100€. Conséquences :
        </P>
        <Liste>
          <Point>On vend trop tôt les positions gagnantes (« sécuriser le gain »)</Point>
          <Point>On garde trop longtemps les positions perdantes (« attendre que ça remonte »)</Point>
          <Point>On panique en bas de cycle et on rate la reprise</Point>
        </Liste>
        <P>
          <G>Étude Dalbar 2024</G> : sur 30 ans, l’investisseur particulier moyen a gagné <G>+3,7%/an</G> sur les actions, contre <G>+10,2%/an</G> pour
          le S&amp;P 500. La différence (~6,5%/an !) vient quasi-exclusivement de mauvais timing dicté par les émotions.
        </P>
        <Photo
          fichier="Daniel_KAHNEMAN.jpg"
          alt="Portrait de Daniel Kahneman"
          legende="Daniel Kahneman (1934-2024), Prix Nobel d’économie 2002. Avec Amos Tversky, il a démontré que les humains ne sont pas rationnels face à l’argent : perdre 100 EUR est psychologiquement deux fois plus douloureux que gagner 100 EUR."
          credit="Wikimedia Commons - CC BY-SA"
        />
      </Section>

      <Section {...s("confirmation")}>
        <P>
          On cherche les informations qui <G>confirment</G> ce qu’on croit déjà, et on ignore celles qui le contredisent. Si vous achetez Tesla, vous
          lirez les articles haussiers et zapperez les baissiers. C’est humain, mais désastreux.
        </P>
        <Antidote titre="Antidote pro">
          avant chaque décision, listez explicitement <G>3 raisons pour lesquelles vous pourriez avoir tort</G>. Si vous n’en trouvez pas, ne tradez pas
          — vous êtes biaisé.
        </Antidote>
      </Section>

      <Section {...s("recence")}>
        <P>
          On donne trop d’importance aux événements récents. Après 3 ans de bull market sur la tech, on croit que ça durera toujours (souvenez-vous de
          2021). Après un krach, on croit que les actions sont « finies » (mars 2009). Les deux fois, on prend exactement la mauvaise décision.
        </P>
        <Antidote>
          raisonner sur <G>20 ans</G>, pas sur 6 mois. Le S&amp;P 500 a fait +10%/an sur 100 ans, malgré 1929, 1987, 2000, 2008, 2020. Le long terme
          efface les drames.
        </Antidote>
      </Section>

      <Section {...s("ancrage")}>
        <P>
          Notre cerveau s’accroche au <G>premier chiffre</G> vu (l’ancre). Si vous avez acheté NVDA à 200$ et qu’elle vaut maintenant 800$, vous pensez
          « trop tard pour entrer ». Si elle vaut 120$, vous pensez « super, c’est en solde ». Mais le <G>prix initial n’a aucune importance</G> — seule
          compte la valeur intrinsèque future.
        </P>
        <Antidote>
          oubliez votre prix d’achat. Chaque jour, demandez-vous : <em>« Si je n’avais pas cette position, est-ce que je l’achèterais à ce prix
          aujourd’hui ? »</em>. Si la réponse est non, vendez.
        </Antidote>
      </Section>

      <Section {...s("confiance")}>
        <P>
          Les investisseurs particuliers <G>surestiment systématiquement leurs compétences</G>. Étude Barber &amp; Odean (2001) : les hommes tradent 45%
          plus que les femmes — et <G>gagnent 1,4%/an de moins</G>, à cause des frais et des mauvaises décisions. Plus on trade, moins on gagne.
        </P>
        <P>
          <G>Statistique brutale</G> : 80% des day-traders particuliers perdent de l’argent sur un an. <G>97% sur 5 ans</G> (étude Brésil 2017).
          Pourtant, chacun croit faire partie des 3% qui réussissent.
        </P>
      </Section>

      <Section {...s("disponibilite")}>
        <P>
          On surestime la probabilité des événements <G>dont on entend parler</G>. Après un krach médiatisé, on est sûr qu’un autre arrive bientôt.
          Pendant un bull market calme, on oublie que la volatilité existe. Les médias amplifient ce biais en couvrant ce qui fait du clic.
        </P>
        <Antidote>
          ne jamais prendre une décision d’investissement après avoir lu une news sensationnelle. Attendez 24h. Les pros disent : <em>« Sleep on it »</em>.
        </Antidote>
      </Section>

      <Section {...s("mimetisme")}>
        <P>
          On se sent en sécurité quand on fait comme tout le monde. C’est ce qui crée les <G>bulles</G> (tout le monde achète, donc on achète) et les{" "}
          <G>paniques</G> (tout le monde vend, donc on vend). Robert Shiller (Nobel 2013) a démontré que les marchés sont régulièrement loin de la valeur
          fondamentale à cause de cette dynamique.
        </P>
        <Citation auteur="Warren Buffett" traduction="(Soyez craintif quand les autres sont avides, et avide quand les autres sont craintifs.)">
          « Be fearful when others are greedy, and greedy when others are fearful. »
        </Citation>
      </Section>

      <Apparition auDefilement>
        <Encadre ton="info">
          <p>
            <G>Le seul antidote universel : un plan écrit.</G>
          </p>
          <p>Avant d’investir, écrivez sur papier :</p>
          <ListeEncadre>
            <Point>Votre allocation cible (ex : 60% actions, 40% obligations)</Point>
            <Point>Vos règles de rebalancement (ex : tous les 12 mois)</Point>
            <Point>Vos critères de vente d’une position (ex : −25% sur l’objectif initial)</Point>
          </ListeEncadre>
          <p>
            Quand l’émotion vous dit de tout vendre en bas de cycle, relisez ce plan. C’est ce que font les meilleurs gérants :{" "}
            <G>déléguer les décisions à un soi-même rationnel passé</G> plutôt qu’au soi-même paniqué présent.
          </p>
        </Encadre>
      </Apparition>

      <Section {...s("synthese")} etiquette="Synthèse">
        <SyntheseBiais />
      </Section>
    </>
  );
}
