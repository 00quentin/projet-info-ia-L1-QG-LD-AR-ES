"""
pages/academie.py
=================
Académie pédagogique : 7 sections denses pour comprendre la finance de marché.
"""

import streamlit as st


def render_page_academie():
    """Affiche l'académie complète (7 sections en sous-onglets)."""
    st.markdown('<div class="qt-section-title">Académie Quant Terminal</div>',
                unsafe_allow_html=True)
    st.markdown("""
    Bienvenue dans l'Académie. Ici, on ne récite pas des définitions : on cherche à **comprendre** 
    pourquoi les marchés se comportent comme ils le font. L'Académie est conçue pour être lue 
    dans l'ordre — chaque partie s'appuie sur la précédente. Prenez votre temps.
    """)

    st_outils, st_modeles, st_macro, st_cas, st_strat, st_lex, st_methodo = st.tabs([
        "1. Lire les données",
        "2. Modèles & maths",
        "3. Macro-économie",
        "4. Cas historiques",
        "5. Stratégies d'investissement",
        "6. Lexique",
        "7. Méthodologie",
    ])

    with st_outils:
        _render_outils()
    with st_modeles:
        _render_modeles()
    with st_macro:
        _render_macro()
    with st_cas:
        _render_cas()
    with st_strat:
        _render_strategies()
    with st_lex:
        _render_lexique()
    with st_methodo:
        _render_methodologie()


def _render_outils():
    st.markdown("### Apprendre à lire un graphique de marché")
    st.write("""
    Un graphique financier n'est pas un simple dessin : c'est le résultat de millions d'ordres 
    d'achat et de vente, de décisions humaines et algorithmiques, de nouvelles macro-économiques 
    et d'émotions collectives. Savoir lire un graphique, c'est savoir lire la psychologie du marché.
    """)

    st.markdown("#### 1.1 — L'illusion des prix absolus")
    st.write("""
    Un piège courant chez les débutants : comparer les prix bruts. Si l'action Apple vaut 170$ 
    et qu'une petite biotech vaut 3$, laquelle performe le mieux sur un an ? Impossible à dire 
    avec les prix absolus. Peut-être que la biotech valait 1$ il y a un an (elle a fait x3), 
    tandis qu'Apple valait 150$ (elle n'a fait que +13%).
    """)

    st.markdown('<div class="qt-callout">'
                '<strong>La règle professionnelle :</strong> les prix bruts ne disent rien.<br><br>'
                'Seules les <strong>variations relatives</strong> comptent.<br><br>'
                'C\'est pour cela que tous les graphiques comparatifs sont affichés en "base 100".'
                '</div>', unsafe_allow_html=True)

    st.markdown("#### 1.2 — La base 100 et pourquoi elle est magique")
    st.write("""
    On divise chaque prix par le prix du premier jour, puis on multiplie par 100. 
    Résultat : tous les actifs démarrent à 100, et on lit directement les pourcentages sur l'axe.
    
    - Une courbe qui finit à **120** = +20%
    - Une courbe qui finit à **85** = -15%
    - Une courbe qui finit à **250** = +150% (l'actif a été multiplié par 2.5)

    Sur les graphiques de Quant Terminal, toutes les courbes commencent exactement à 100. 
    Celle qui monte le plus a le plus performé. C'est aussi simple que ça.
    """)

    st.markdown("#### 1.3 — La heatmap de performance")
    st.write("""
    La heatmap (ou carte thermique) est un outil de synthèse redoutable. Sur un seul écran, 
    vous voyez d'un coup d'œil qui a gagné et qui a perdu. Vert foncé = gros gain, 
    rouge foncé = grosse perte.

    **Pourquoi c'est crucial ?** Parce que sur les marchés, l'argent ne disparaît jamais : il se 
    **déplace**. Quand les actions s'effondrent, l'argent va quelque part — typiquement dans 
    les obligations d'État et l'or. On appelle cela un *flight to quality* (fuite vers la qualité).
    Une heatmap permet de voir cette rotation en temps réel.
    """)

    st.markdown('<div class="qt-callout-warn">'
                '<strong>Piège classique :</strong> regarder uniquement la performance d\'un actif.<br><br>'
                'Un +10% sur une action qui a une volatilité de 40% est bien moins impressionnant '
                'qu\'un +8% sur une obligation qui a une volatilité de 5%.<br><br>'
                'La performance doit toujours être mise en relation avec le risque pris '
                '(voir le Sharpe Ratio en section 7).'
                '</div>', unsafe_allow_html=True)

    st.markdown("#### 1.4 — Lire une trajectoire stochastique")
    st.write("""
    Une courbe de cours n'est **jamais** lisse. Elle tremble, elle zigzague, elle rebondit. 
    Ce tremblement quotidien s'appelle le **bruit de marché**. Ce qui compte, c'est la **tendance 
    sous-jacente**. Trois signaux à identifier :
    
    - **La pente moyenne** : est-ce que globalement ça monte, descend, ou stagne ?
    - **L'amplitude des oscillations** : est-ce que les variations journalières sont de 0.5%, 
      2%, ou 10% ? Plus elles sont grandes, plus l'actif est risqué.
    - **Les cassures** : les moments où la courbe change brutalement de direction. 
      Ce sont souvent des événements majeurs (décision de banque centrale, résultats d'entreprise, 
      actualité géopolitique).
    """)

    st.markdown("#### 1.5 — Les bandes de confiance Monte-Carlo")
    st.write("""
    Quand vous activez le mode Monte-Carlo, les graphiques affichent non pas **une** trajectoire, 
    mais une **bande colorée** autour de la trajectoire médiane. Cette bande représente l'intervalle 
    dans lequel la vraie trajectoire a 90% de chances de se situer.
    
    **Pourquoi c'est essentiel ?** Parce qu'une simulation unique, c'est un coup de chance (ou de malchance). 
    En moyennant 50 simulations, on obtient une vision **statistiquement robuste** de l'avenir. 
    Plus la bande est large, plus l'incertitude est grande sur cet actif.
    """)


def _render_modeles():
    st.markdown("### Comment simuler l'avenir avec des mathématiques")
    st.write("""
    Personne ne peut prédire le marché. Mais on peut **modéliser les lois statistiques** qui le régissent. 
    C'est exactement ce que font les banques d'investissement, les hedge funds, et ce que fait 
    Quant Terminal en arrière-plan.
    """)

    st.markdown("#### 2.1 — Le modèle de Bachelier et le mouvement brownien")
    st.write("""
    En 1900, un étudiant français nommé Louis Bachelier soutient une thèse révolutionnaire 
    à la Sorbonne : "La théorie de la spéculation". Il propose que les cours de Bourse 
    se comportent comme des particules de pollen sous un microscope — un mouvement chaotique, 
    le **mouvement brownien**.
    
    Ce modèle, approfondi ensuite par Einstein (1905) et formalisé par Itō (1940), est devenu 
    le socle de toute la finance moderne. L'idée est simple : chaque jour, le prix varie d'une 
    quantité tirée au hasard selon une loi normale (courbe en cloche de Gauss).
    """)

    st.latex(r"S_{t+1} = S_t \times (1 + \mu \, \Delta t + \sigma \, \sqrt{\Delta t} \, Z)")

    st.write("""
    Où :
    - $S_t$ = prix à l'instant $t$
    - $\\mu$ = tendance (drift) — estimée ici par notre IA à partir du scénario macro
    - $\\sigma$ = volatilité — calibrée à partir des données historiques de l'actif
    - $Z$ = tirage aléatoire dans une loi normale centrée réduite $\\mathcal{N}(0,1)$
    
    C'est précisément la formule utilisée par le **modèle Black-Scholes** (Prix Nobel 1997) 
    pour pricer les options, et par toutes les grandes banques pour leurs calculs de risque.
    """)

    st.markdown("#### 2.2 — Pourquoi la loi normale est insuffisante")
    st.write("""
    Le modèle brownien a un défaut majeur : il sous-estime **gravement** la probabilité 
    des événements extrêmes. Selon une loi normale pure, un krach de -10% en un jour devrait 
    arriver **une fois tous les 10 000 ans**. Pourtant, ça s'est produit plusieurs fois 
    au cours des 40 dernières années (1987, 2008, 2020).
    
    C'est ce que Benoît Mandelbrot a appelé les **queues épaisses** (*fat tails*) : la réalité 
    des marchés n'est pas gaussienne, elle contient beaucoup plus d'événements extrêmes 
    que ne le prédit la théorie classique. C'est ce qui a mené à l'effondrement du fonds 
    **LTCM** en 1998 — deux prix Nobel au conseil, et pourtant ils ont fait faillite parce qu'ils 
    avaient sous-estimé les queues épaisses du risque russe.
    """)

    st.markdown('<div class="qt-callout-warn">'
                '<strong>Leçon retenue :</strong> en finance, les événements "impossibles" '
                'arrivent tous les 10 ans.<br><br>'
                'Un bon modèle doit en tenir compte.'
                '</div>', unsafe_allow_html=True)

    st.markdown("#### 2.3 — Les 3 modèles de Quant Terminal")
    st.markdown("**A. Modèle Probabiliste (Brownien classique)**")
    st.write("""
    Le plus courant. Chaque jour, variation = tendance + bruit gaussien. Bon pour les périodes 
    calmes et les actifs stables (obligations, grands indices). Mais il rate les krachs.
    """)
    st.markdown("**B. Modèle Historique (queues épaisses)**")
    st.write("""
    Ajoute une probabilité de 2% par jour d'un choc violent (x5 la volatilité normale). 
    Le modèle est globalement plus calme, mais déclenche régulièrement des mouvements brusques — 
    c'est une approximation simple des *fat tails* de Mandelbrot. Idéal pour tester la résilience 
    d'un portefeuille face aux cygnes noirs.
    """)
    st.markdown("**C. Modèle Machine Learning (momentum)**")
    st.write("""
    Inspiré des stratégies *trend-following* des hedge funds comme Renaissance Technologies 
    ou AQR. L'idée : quand une tendance est identifiée, elle s'auto-renforce (les investisseurs 
    suivent le mouvement). Mathématiquement, on fait croître l'impact de la tendance avec le temps.
    """)

    st.markdown("#### 2.4 — La méthode Monte-Carlo")
    st.write("""
    Nommée d'après le casino de Monaco, cette méthode a été inventée par Stanislaw Ulam 
    et John von Neumann dans les années 1940, pendant le projet Manhattan (bombe atomique). 
    L'idée est géniale : au lieu de résoudre analytiquement un problème impossible, 
    on **lance des milliers de simulations aléatoires** et on regarde les résultats.
    
    Exemple concret : on veut savoir ce que donne 100 € investis dans notre portefeuille 
    si on refait l'histoire 50 fois. On obtient 50 valeurs finales différentes. 
    On calcule :
    - La **médiane** (valeur centrale, 25 au-dessus et 25 en-dessous)
    - Le **percentile 5%** (seulement 5% des fois on a fait pire)
    - Le **percentile 95%** (seulement 5% des fois on a fait mieux)
    
    Ces 3 valeurs définissent la **bande de confiance à 90%**. C'est exactement ce que 
    font les actuaires, les ingénieurs nucléaires, et les banquiers d'investissement chaque jour.
    """)

    st.markdown("#### 2.5 — Rendements simples vs rendements logarithmiques")
    st.write("""
    Petit point technique pour les puristes. Quand un prix passe de 100 à 110, on dit que 
    le rendement est +10%. C'est le **rendement simple** : $r = \\frac{P_1 - P_0}{P_0}$.
    
    Mais quand on chaîne les rendements sur plusieurs périodes, les simples ne s'additionnent pas 
    proprement (+10% puis -10% ne fait pas 0, mais -1%). C'est pour ça que les professionnels 
    utilisent les **rendements logarithmiques** : $r_{log} = \\ln(P_1 / P_0)$. 
    Ils s'additionnent parfaitement et suivent plus proprement une loi normale.
    """)


def _render_macro():
    st.markdown("### Les 3 forces qui contrôlent les marchés mondiaux")
    st.write("""
    Il y a des milliers d'actions cotées, des dizaines de devises, des centaines de matières premières. 
    Mais **trois forces invisibles** déterminent la direction globale de tout cela : 
    les taux d'intérêt, l'inflation, et la confiance des investisseurs.
    """)

    st.markdown("#### 3.1 — Les banques centrales : les véritables maîtres du jeu")
    st.write("""
    La Réserve Fédérale américaine (FED), la Banque Centrale Européenne (BCE), la Banque du Japon (BoJ), 
    la Banque Populaire de Chine (PBoC) — ces quatre institutions contrôlent l'essentiel de la liquidité 
    mondiale. Leur outil principal : le **taux directeur**, qui fixe le prix auquel les banques 
    commerciales peuvent emprunter de l'argent.
    """)

    st.markdown("**Quand les taux sont bas (argent gratuit) :**")
    st.write("""
    - Les entreprises empruntent massivement pour investir, innover, racheter leurs concurrents.
    - Les ménages empruntent pour acheter des maisons, des voitures.
    - Les investisseurs, ne trouvant plus de rendement dans les obligations (qui paient peu), 
      se ruent sur les **actions** et les actifs risqués. La Bourse explose.
    - Les cryptos, les valeurs tech non rentables, l'immobilier, tout gonfle.
    - Période emblématique : **2009-2021**, avec des taux proches de zéro après la crise de 2008.
    """)

    st.markdown("**Quand les taux sont hauts (argent cher) :**")
    st.write("""
    - Les crédits deviennent difficiles. Les projets d'investissement sont reportés.
    - Les entreprises endettées peinent à refinancer leur dette.
    - Les investisseurs peuvent placer leur argent **sans risque** dans des Bons du Trésor 
      à 5% — pourquoi prendre du risque sur des actions quand on peut gagner 5% en dormant ?
    - Résultat : rotation massive vers les obligations, chute des actions et des cryptos.
    - Période emblématique : **1979-1982** (Paul Volcker à la FED, taux à 20%), et **2022-2024** 
      (Jerome Powell face à l'inflation post-COVID).
    """)

    st.markdown("#### 3.2 — L'inflation : la taxe invisible qui ronge votre argent")
    st.write("""
    Quand l'inflation est à 5%, cela signifie que le niveau général des prix augmente de 5% 
    par an. Vos 100€ sur votre compte en banque conservent leur valeur nominale, 
    mais perdent **5% de leur pouvoir d'achat** réel chaque année.
    
    Sur 10 ans avec 5% d'inflation constante, votre argent perd **40%** de sa valeur réelle. 
    C'est pour cela qu'on dit que *"le cash est poubelle en période inflationniste"*.
    """)

    st.markdown("**Comment se protéger de l'inflation ?**")
    st.write("""
    On achète des choses **qu'on ne peut pas imprimer à l'infini** :
    
    - **Or** : quantité physique limitée dans la croûte terrestre, actif refuge depuis 5000 ans. 
      Pendant la crise des années 70 (inflation à 15% aux USA), l'or a été multiplié par 20.
    - **Matières premières** (pétrole, cuivre, blé) : leur prix monte avec le coût de la vie.
    - **Immobilier** : les loyers peuvent être indexés sur l'inflation.
    - **Actions d'entreprises avec pricing power** : entreprises capables d'augmenter leurs 
      prix sans perdre de clients (LVMH, Apple, Coca-Cola). On dit qu'elles ont une "douve" 
      (*moat*) selon Warren Buffett.
    - **Crypto** : Bitcoin a été inventé comme une réserve de valeur limitée à 21 millions 
      d'unités. En théorie, c'est un hedge contre l'inflation — en pratique, c'est beaucoup plus 
      corrélé au Nasdaq qu'on ne le pensait.
    """)

    st.markdown("#### 3.3 — La courbe des taux : l'indicateur préféré des récessions")
    st.write("""
    Voici un secret bien gardé : depuis 1960 aux États-Unis, **chaque récession a été précédée 
    par une inversion de la courbe des taux**. Cet indicateur a 100% de précision sur 60 ans.
    
    **La courbe des taux**, c'est le graphique qui montre le rendement des obligations d'État 
    à différentes maturités (3 mois, 2 ans, 5 ans, 10 ans, 30 ans). En temps normal, plus on 
    prête longtemps, plus on exige un rendement élevé (pour compenser le risque de long terme). 
    La courbe monte donc de gauche à droite.
    
    **Quand la courbe s'inverse** (les taux courts deviennent plus hauts que les taux longs), 
    c'est que le marché anticipe une baisse future des taux — donc une récession. C'est arrivé 
    en 2000, 2006, 2019, et mi-2022. À chaque fois, récession 6 à 18 mois plus tard.
    """)

    st.markdown("#### 3.4 — Le dollar américain : le soleil du système financier")
    st.write("""
    80% des transactions commerciales internationales se font en dollars. 60% des réserves 
    de change des banques centrales du monde sont en dollars. C'est ce qu'on appelle le 
    **privilège exorbitant** du dollar, formulé par Valéry Giscard d'Estaing en 1965.
    
    **Quand le dollar monte** (Dollar Index DXY en hausse) :
    - Les pays émergents souffrent : leur dette est souvent en dollars, et il leur en coûte 
      plus cher de la rembourser.
    - L'or baisse mécaniquement (il est coté en dollars).
    - Les matières premières deviennent plus chères pour le reste du monde → ralentissement 
      de la demande.
    
    **Quand le dollar baisse** : effet inverse, les émergents respirent, l'or brille.
    """)

    st.markdown("#### 3.5 — Le VIX : le thermomètre de la peur")
    st.write("""
    Le **VIX** (Volatility Index), calculé par le CBOE de Chicago, mesure la volatilité **attendue** 
    du S&P 500 sur les 30 prochains jours, extraite du prix des options. On l'appelle aussi 
    *"Fear Index"* (indice de la peur).
    
    - VIX < 15 : marché calme, euphorie, complaisance. Danger latent.
    - VIX 15-25 : volatilité normale.
    - VIX 25-40 : marché nerveux, tensions.
    - VIX > 40 : panique. Le VIX a culminé à 82 le 16 mars 2020 (COVID) et à 80 en octobre 2008 
      (Lehman Brothers).
    
    **Utilité pratique :** si vous pensez qu'une crise arrive, acheter du VIX (via des ETF comme VXX) 
    est une assurance contre les krachs boursiers.
    """)


def _render_cas():
    st.markdown("### Les grandes crises expliquées")
    st.write("""
    L'histoire boursière n'est pas une succession d'événements aléatoires. Chaque crise a sa logique, 
    ses victimes, et ses gagnants. Les comprendre, c'est mieux anticiper la prochaine.
    """)

    st.markdown("#### 4.1 — Le krach de 1929 et la Grande Dépression")
    st.write("""
    **Contexte :** Les années 1920 furent les "Roaring Twenties" — une décennie d'euphorie, 
    de spéculation effrénée, d'achats d'actions à crédit (*margin trading*) jusqu'à 90% de levier.
    
    **Le déclenchement :** le jeudi noir, 24 octobre 1929. Le Dow Jones perd 11% en une journée. 
    Puis le mardi 29 octobre, -12% supplémentaires. En quelques semaines, -50%. 
    Le marché ne retrouvera son niveau de 1929 qu'en **1954** — soit 25 ans plus tard.
    
    **Enseignements :**
    - L'effet de levier excessif est une bombe à retardement.
    - Les banques centrales peuvent aggraver une crise par leurs erreurs (la FED a resserré 
      au pire moment en 1931, ce qui a transformé un krach boursier en dépression mondiale).
    - Ce qui a sauvé les USA : le **New Deal** de Roosevelt (1933) et les dépenses publiques massives.
    """)

    st.markdown("#### 4.2 — Le Black Monday du 19 octobre 1987")
    st.write("""
    **Contexte :** Les bourses montent fort depuis 5 ans, nouvelles techniques de *program trading* 
    (algorithmes), portefeuilles dits "assurés" via des options.
    
    **Le déclenchement :** le 19 octobre 1987, le Dow Jones perd **-22.6% en une seule séance**. 
    Record absolu jamais égalé. Cause probable : les algorithmes de vente automatique ont déclenché 
    une cascade de ventes, sans intervention humaine pour l'arrêter.
    
    **Enseignement clé :** les systèmes automatisés peuvent créer des **boucles de rétroaction** 
    catastrophiques. C'est ce qui a mené à l'introduction des **coupe-circuits** (circuit breakers) 
    à Wall Street : la Bourse s'arrête automatiquement si ça baisse de trop.
    """)

    st.markdown("#### 4.3 — La bulle internet (1995-2002)")
    st.write("""
    **Contexte :** Internet se démocratise. Toute entreprise avec ".com" dans son nom voit sa 
    valorisation multipliée par 10. Des sociétés sans chiffre d'affaires valent des milliards. 
    Exemple emblématique : **Pets.com**, valorisée 300M$ en 2000, en faillite en 2001.
    
    **Le pic :** le Nasdaq atteint 5048 points en mars 2000. Il ne reviendra à ce niveau qu'en **2015** 
    — quinze ans de stagnation.
    
    **La chute :** -78% sur le Nasdaq entre 2000 et 2002. Destruction de 5 trillions de dollars 
    de capitalisation boursière.
    
    **Enseignement clé :** une technologie révolutionnaire peut être **réelle** (internet était bien 
    révolutionnaire) mais les **valorisations** peuvent être totalement délirantes. La question n'est 
    pas "cette technologie va-t-elle changer le monde ?" mais "à quel prix est-ce que je l'achète ?".
    """)

    st.markdown("#### 4.4 — La crise des subprimes (2007-2009)")
    st.write("""
    **Contexte :** les banques américaines ont accordé pendant des années des crédits immobiliers 
    à des ménages qui ne pouvaient pas rembourser (les *subprimes*). Ces crédits ont été 
    "titrisés" (transformés en produits financiers complexes, les CDO) et revendus dans le monde entier 
    comme s'ils étaient sûrs.
    
    **Le déclenchement :** en 2007, les prix de l'immobilier US commencent à baisser. 
    Les ménages ne remboursent plus. Les CDO perdent leur valeur. En septembre 2008, 
    **Lehman Brothers** fait faillite — la 4e plus grosse banque d'investissement américaine. 
    Panique mondiale.
    
    **La chute :** S&P 500 -57% entre octobre 2007 et mars 2009. Or : **+25%** sur la même période 
    (flight to quality). Bons du Trésor US 10 ans : rendement de 5% à 2%, prix des obligations explose.
    
    **Enseignement clé :** la complexité financière est une arme à double tranchant. Quand personne 
    ne comprend les produits qu'il détient, la confiance s'effondre en quelques jours. Warren Buffett 
    avait qualifié les dérivés d'*"armes de destruction massive financière"* dès 2003.
    """)

    st.markdown("#### 4.5 — Le krach COVID de mars 2020")
    st.write("""
    **Contexte :** marchés au plus haut, chômage US au plus bas depuis 50 ans, les investisseurs 
    pensent que rien ne peut arriver.
    
    **Le déclenchement :** le 11 mars 2020, l'OMS déclare une pandémie. En 23 jours, le S&P 500 perd 
    **-34%**. Record de vitesse historique — plus rapide que 1929, 1987 ou 2008.
    
    **Le rebond :** en moins de 6 mois, le marché a récupéré toutes ses pertes. Pourquoi ? 
    Parce que les banques centrales ont injecté **plus de 10 000 milliards de dollars** dans l'économie 
    mondiale. La FED a baissé ses taux à zéro en une semaine.
    
    **Enseignement clé :** en 2020, on a appris qu'il y a désormais un **"put implicite" des banques 
    centrales** sous les marchés. Quoi qu'il arrive, elles interviendront. Cela explique pourquoi 
    le marché a quasiment ignoré les mauvaises nouvelles de 2020-2021 : tout le monde parie sur 
    le sauvetage.
    """)

    st.markdown("#### 4.6 — Ce que l'histoire enseigne")
    st.markdown('<div class="qt-callout">'
                '• Les krachs arrivent tous les 8-12 ans en moyenne. C\'est un <strong>fait statistique</strong>.<br><br>'
                '• Chaque fois, les investisseurs disent "cette fois c\'est différent". Ce ne l\'est jamais vraiment.<br><br>'
                '• Le meilleur moment pour acheter est souvent le plus inconfortable (mars 2009, mars 2020).<br><br>'
                '• Diversifier à travers des actifs décorrélés (actions, obligations, or, cash) reste la seule défense sérieuse.<br><br>'
                '• Les liquidités disponibles (cash) sont aussi une position : elles permettent d\'acheter quand tout est bradé.'
                '</div>', unsafe_allow_html=True)


def _render_strategies():
    st.markdown("### Les grandes stratégies d'allocation d'actifs")
    st.write("""
    Il existe des centaines de stratégies d'investissement, mais 5 grandes écoles dominent 
    la réflexion institutionnelle. Les comprendre permet de choisir sa propre voie.
    """)

    st.markdown("#### 5.1 — Le portefeuille 60/40 (la stratégie classique)")
    st.write("""
    **60% d'actions, 40% d'obligations.** C'est le portefeuille de référence depuis les années 1950.
    L'idée : les actions offrent la croissance, les obligations la stabilité. Quand les actions 
    chutent, les obligations montent (flight to quality), ce qui amortit les pertes.
    
    **Performance historique** : environ +8% par an sur 50 ans aux USA, avec des drawdowns 
    maximaux autour de -25%. Raisonnable, peu spectaculaire, mais fiable.
    
    **Limite actuelle :** en 2022, actions ET obligations ont chuté en même temps (car les taux 
    ont flambé). Le 60/40 a fait -17%. Certains disent qu'il est "mort" — d'autres qu'il reste 
    la base raisonnable pour la plupart des épargnants.
    """)

    st.markdown("#### 5.2 — Le All Weather de Ray Dalio (Bridgewater)")
    st.write("""
    Ray Dalio, fondateur du plus gros hedge fund du monde (Bridgewater, 150 milliards $), 
    a conçu ce portefeuille qui doit fonctionner dans **tous les environnements économiques**. 
    Il part d'un constat simple : il existe 4 régimes économiques possibles :
    """)

    st.markdown("""
    | Régime | Inflation | Croissance | Ce qui marche |
    |---|---|---|---|
    | Goldilocks | Basse | Haute | Actions, obligations corporate |
    | Stagflation | Haute | Basse | Or, matières premières |
    | Reflation | Haute | Haute | Actions, immobilier, matières premières |
    | Déflation | Basse | Basse | Obligations longues, cash |
    """)

    st.write("""
    **Sa recette** : 30% actions, 40% obligations longues US, 15% obligations moyennes, 
    7,5% or, 7,5% matières premières. L'idée : avoir une exposition à chaque régime pour ne 
    jamais être totalement perdant.
    
    **Performance** : sur 40 ans, rendement annualisé de 8%, mais avec des drawdowns plus faibles 
    que le 60/40. Moins brillant en bull market, plus résilient en crise.
    """)

    st.markdown("#### 5.3 — La Risk Parity")
    st.write("""
    Stratégie sœur du All Weather, développée dans les années 1990. Au lieu de répartir l'argent 
    en pourcentages (60/40), on répartit le **risque**. Chaque classe d'actif contribue à parts 
    égales à la volatilité totale du portefeuille.
    
    En pratique : comme les obligations sont 4x moins volatiles que les actions, un portefeuille 
    risk parity contient souvent **beaucoup plus d'obligations en valeur** (avec parfois du levier 
    pour booster leur rendement). Assez contre-intuitif pour un débutant.
    """)

    st.markdown("#### 5.4 — Le value investing (Warren Buffett, Benjamin Graham)")
    st.write("""
    Formalisé en 1934 par Benjamin Graham dans "Security Analysis" et "The Intelligent Investor", 
    puis rendu célèbre par son élève Warren Buffett.
    
    **Principe** : chaque action a une **valeur intrinsèque** (basée sur ses profits futurs actualisés). 
    Le marché est parfois irrationnel et vend une action bien en-dessous de cette valeur. 
    Le value investor achète alors, attend que le marché redevienne rationnel, et vend quand 
    le prix dépasse la valeur intrinsèque.
    
    **Les critères de Buffett :**
    - Entreprise avec une **"douve économique"** durable (brevets, marque forte, effet réseau)
    - Management de qualité
    - Faible endettement
    - Historique de profits stables
    - Prix d'achat **raisonnable** par rapport aux profits (ratio P/E bas)
    
    **Exemples emblématiques** : Coca-Cola (acheté en 1988, x20 depuis), Apple (x6 depuis 2016), 
    American Express.
    """)

    st.markdown("#### 5.5 — Le momentum / trend following")
    st.write("""
    Stratégie opposée au value. L'idée : *"the trend is your friend"* (la tendance est ton amie). 
    On achète ce qui monte, on vend ce qui baisse. Empiriquement, les actifs qui ont monté 
    sur les 6-12 derniers mois ont tendance à continuer à monter sur les 3-6 mois suivants — 
    c'est l'**effet momentum**, documenté par Jegadeesh & Titman (1993).
    
    **Qui l'utilise ?** Les hedge funds systématiques comme **AHL (Man Group)**, **Winton Capital**, 
    ou **Renaissance Technologies** (James Simons, le mathématicien le plus riche du monde). 
    Ils gèrent des centaines de milliards sur ce principe.
    """)

    st.markdown("#### 5.6 — Pour choisir votre stratégie")
    st.markdown('<div class="qt-callout">'
                'Il n\'y a pas de "meilleure" stratégie dans l\'absolu. Tout dépend de :<br><br>'
                '• <strong>Votre horizon</strong> : 5 ans vs 30 ans, ce n\'est pas la même chose.<br><br>'
                '• <strong>Votre tolérance au risque</strong> : pouvez-vous dormir si votre portefeuille perd -40% ?<br><br>'
                '• <strong>Vos objectifs</strong> : préservation du capital, rendement, héritage ?<br><br>'
                '• <strong>Vos compétences</strong> : le value investing demande de savoir analyser un bilan, '
                'le momentum d\'avoir une discipline de fer.'
                '</div>', unsafe_allow_html=True)


def _render_lexique():
    st.markdown("### Le lexique du professionnel")

    st.markdown("#### Marchés & cycles")
    st.markdown("""
    - **Bull Market** — Marché haussier (image du taureau qui attaque de bas en haut).
    - **Bear Market** — Marché baissier (-20% minimum depuis le pic). L'ours attaque de haut en bas.
    - **Correction** — Baisse entre -10% et -20%. Saine et fréquente.
    - **Krach** — Chute brutale et rapide (>-10% en quelques jours).
    - **Rally** — Hausse rapide après une baisse.
    - **Melt-up** — Hausse euphorique et irrationnelle (comme fin 2020-2021).
    """)

    st.markdown("#### Banques centrales")
    st.markdown("""
    - **Hawkish** (faucon) — Banquier central qui veut monter les taux pour combattre l'inflation.
    - **Dovish** (colombe) — Banquier central qui veut baisser les taux pour stimuler l'économie.
    - **Quantitative Easing (QE)** — Impression de monnaie par la banque centrale pour acheter des actifs. Stimule l'économie.
    - **Quantitative Tightening (QT)** — Opération inverse : la banque centrale réduit son bilan. Resserre.
    - **Forward guidance** — Communication sur la trajectoire future des taux pour guider les anticipations.
    """)

    st.markdown("#### Mesures de risque")
    st.markdown("""
    - **Volatilité (σ)** — Écart-type des rendements. Mesure l'amplitude des variations.
    - **Sharpe Ratio** — Rendement par unité de risque. >1 = bon, >2 = excellent, <0 = mauvais.
    - **Sortino Ratio** — Version du Sharpe qui ne pénalise que la volatilité baissière.
    - **Beta (β)** — Sensibilité d'un actif au marché. β=1 bouge comme le marché, β=2 amplifie x2.
    - **Alpha (α)** — Surperformance par rapport au benchmark. L'alpha pur = talent du gérant.
    - **Drawdown** — Chute depuis un plus-haut. Mesure ultime du stress d'un portefeuille.
    - **VaR (Value at Risk)** — Perte maximale probable avec un niveau de confiance (ex: 95%).
    - **CVaR / Expected Shortfall** — Moyenne des pertes au-delà de la VaR. Plus conservateur.
    """)

    st.markdown("#### Produits dérivés")
    st.markdown("""
    - **Call** — Option d'achat. Donne le droit d'acheter à un prix fixé.
    - **Put** — Option de vente. Donne le droit de vendre à un prix fixé.
    - **Strike** — Prix d'exercice d'une option.
    - **Maturité** — Date d'échéance d'une option ou d'une obligation.
    - **Delta (Δ)** — Sensibilité du prix d'une option au prix du sous-jacent.
    - **Gamma (Γ)** — Sensibilité du delta au prix du sous-jacent.
    - **Theta (Θ)** — Perte de valeur d'une option due au temps qui passe.
    - **Vega** — Sensibilité du prix d'une option à la volatilité.
    """)

    st.markdown("#### Obligations")
    st.markdown("""
    - **Yield** — Rendement d'une obligation à l'échéance.
    - **Spread** — Écart de rendement entre deux obligations. Ex: spread Italie-Allemagne = prime de risque italienne.
    - **Duration** — Sensibilité du prix d'une obligation à une variation des taux. Duration 10 = -10% si les taux montent de 1%.
    - **Convexité** — Raffinement de la duration pour les gros mouvements de taux.
    - **Investment Grade** — Obligations notées BBB- ou mieux. Risque faible.
    - **High Yield / Junk Bonds** — Obligations notées en-dessous de BBB-. Rendement élevé mais risque de défaut réel.
    """)

    st.markdown("#### Trading & stratégie")
    st.markdown("""
    - **Long** — Position à la hausse (on achète en espérant que ça monte).
    - **Short** — Position à la baisse (on vend à découvert en espérant racheter moins cher).
    - **Hedge** — Couverture. Position prise pour réduire le risque d'une autre.
    - **Leverage** / Levier — Emprunt pour amplifier les gains (et les pertes).
    - **Carry trade** — Emprunter dans une devise à taux bas, investir dans une devise à taux haut.
    - **Arbitrage** — Exploiter une différence de prix entre deux marchés pour un gain sans risque (théoriquement).
    - **Flight to quality** — Fuite vers la qualité : vente massive d'actifs risqués, achat d'actifs sûrs.
    - **Risk-on / Risk-off** — Période où les investisseurs prennent du risque (risk-on) ou le fuient (risk-off).
    """)

    st.markdown("#### Comptabilité & finance d'entreprise")
    st.markdown("""
    - **PnL** (*Profit and Loss*) — Compte de résultat. Bénéfice ou perte.
    - **EBITDA** — Bénéfice avant intérêts, impôts, dépréciation et amortissement. Mesure opérationnelle.
    - **Cash-flow libre (FCF)** — Trésorerie générée par l'activité, disponible pour les actionnaires.
    - **P/E ratio** — Cours / Bénéfice par action. Plus c'est haut, plus l'action est "chère" (ou en forte croissance).
    - **ROE** — Return on Equity. Rentabilité des fonds propres.
    - **Dilution** — Quand une entreprise émet de nouvelles actions, chaque actionnaire possède un pourcentage plus petit.
    """)


def _render_methodologie():
    st.markdown("### Méthodologie mathématique de Quant Terminal")
    st.write("""
    Pour les utilisateurs exigeants (et les professeurs), voici les formules exactes 
    implémentées dans le terminal.
    """)

    st.markdown("#### A. Volatilité annualisée")
    st.latex(r"\sigma_{annuel} = \sigma_{quotidien} \times \sqrt{252}")
    st.write("""
    On multiplie l'écart-type des rendements journaliers par √252 (nombre de jours de cotation 
    dans l'année). Pourquoi √252 et pas 252 ? Parce que la variance s'additionne linéairement 
    avec le temps, donc l'écart-type croît en √t. C'est une conséquence du théorème central limite.
    """)

    st.markdown("#### B. Sharpe Ratio")
    st.latex(r"Sharpe = \frac{R_p - R_f}{\sigma_p}")
    st.write("""
    $R_p$ = rendement annualisé du portefeuille, $R_f$ = taux sans risque (2% par défaut, 
    correspondant approximativement au rendement des Bons du Trésor US court terme), 
    $\\sigma_p$ = volatilité annualisée.
    
    Créé par William Sharpe en 1966 (Prix Nobel 1990). C'est **la** métrique universellement utilisée 
    par les gérants professionnels. Un Sharpe de 1 signifie que pour chaque unité de risque prise, 
    vous avez gagné 1 unité de rendement au-dessus du taux sans risque. En dessous de 0.5, 
    l'effort de prendre du risque n'en vaut pas la peine.
    """)

    st.markdown("#### C. Max Drawdown")
    st.latex(r"DD_{max} = \max_{t} \left( \frac{Peak_t - V_t}{Peak_t} \right)")
    st.write("""
    $Peak_t$ = plus-haut historique au temps $t$, $V_t$ = valeur au temps $t$.
    C'est la pire chute subie depuis un sommet précédent. Mesure cruciale car elle reflète 
    la **vraie souffrance** psychologique d'un investisseur : voir son capital fondre de -30% 
    est bien plus traumatisant qu'une volatilité élevée.
    
    Pendant le krach de 1929, le Dow Jones a subi un drawdown de **-89%** sur 3 ans. 
    Pendant 2008, le S&P 500 a fait **-57%**. Pendant le COVID, **-34% en 23 jours**.
    """)

    st.markdown("#### D. Value at Risk (VaR)")
    st.latex(r"VaR_{95\%} = \text{Percentile}_{5\%}(\text{rendements})")
    st.write("""
    La VaR 95% à 1 jour répond à la question : *"Quelle est la perte maximale que je ne dépasserai 
    pas dans 95% des cas en une journée ?"*. C'est le rendement situé au 5e percentile (5% les pires 
    rendements). 
    
    **Attention** : la VaR ne dit rien sur ce qui se passe dans les 5% restants — les *tail risks*. 
    C'est pour ça qu'on la complète souvent par la **CVaR** (Conditional VaR), qui calcule 
    la moyenne des pertes **au-delà** de la VaR. Beaucoup plus conservateur.
    """)

    st.markdown("#### E. Mouvement Brownien Géométrique (modèle Probabiliste)")
    st.latex(r"\frac{dS_t}{S_t} = \mu \, dt + \sigma \, dW_t")
    st.write("En discrétisant sur un pas journalier :")
    st.latex(r"S_{t+1} = S_t \times (1 + \mu + \sigma \cdot Z_t)")
    st.write("""
    Avec $Z_t \\sim \\mathcal{N}(0, 1)$ un tirage gaussien indépendant à chaque pas de temps. 
    C'est exactement la formule utilisée dans le code de Quant Terminal pour le modèle "Probabiliste".
    
    Le $\\mu$ (drift) est estimé par notre IA à partir du scénario macro-économique, tandis que 
    le $\\sigma$ (volatilité) est calibré à partir des données historiques de chaque actif.
    """)

    st.markdown("#### F. Méthode Monte-Carlo")
    st.write("On simule $N=50$ trajectoires indépendantes. Pour chaque jour $t$ et chaque actif :")
    st.latex(r"\text{Médiane}_t = \text{percentile}_{50}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})")
    st.latex(r"\text{Bas}_t = \text{percentile}_{5}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})")
    st.latex(r"\text{Haut}_t = \text{percentile}_{95}(\{S_t^{(1)}, \ldots, S_t^{(N)}\})")
    st.write("""
    L'intervalle [Bas, Haut] constitue la **bande de confiance à 90%** : dans 90% des cas simulés, 
    le prix à l'instant $t$ se trouve dans cette bande.
    
    La méthode Monte-Carlo converge en $O(1/\\sqrt{N})$ : pour doubler la précision, il faut 
    quadrupler le nombre de simulations. Avec 50 simulations, la précision est typiquement 
    de ±5% sur les percentiles — suffisant pour un outil éducatif. Les grandes banques utilisent 
    couramment 10 000 à 1 000 000 de simulations pour leurs calculs réglementaires (Bâle III, FRTB).
    """)

    st.markdown("#### G. Limites connues de notre modèle")
    st.markdown('<div class="qt-callout-warn">'
                '<strong>Pour l\'honnêteté intellectuelle</strong>, voici les limites de Quant Terminal :<br><br>'
                '• Les volatilités sont supposées <strong>constantes</strong>, alors qu\'en réalité elles '
                'se regroupent en clusters (effet GARCH).<br><br>'
                '• Les actifs sont traités <strong>indépendamment</strong>, alors qu\'en crise toutes '
                'les corrélations montent à 1 (voir 2008).<br><br>'
                '• L\'IA fournit une estimation <strong>globale</strong> du choc, pas une trajectoire '
                'fine dans le temps.<br><br>'
                '• Les distributions restent <strong>gaussiennes</strong>, sauf dans le mode Historique. '
                'La réalité a des queues encore plus épaisses.<br><br>'
                '• Pas de prise en compte des <strong>coûts de transaction</strong>, des <strong>spreads bid-ask</strong>, '
                'ni de la <strong>liquidité</strong>.<br><br>'
                'Quant Terminal est un outil <strong>pédagogique</strong>. '
                'Pour un usage professionnel réel, il faudrait ajouter ces raffinements et calibrer '
                'le modèle sur des données de marché en temps réel.'
                '</div>', unsafe_allow_html=True)