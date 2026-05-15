"""
components/academie_illustrations.py
====================================
Blocs visuels enrichis pour l'Academie.

Architecture :
- Fonctions `img_xxx()` : images individuelles Wikipedia, integrables au sein
  du contenu d'une section au moment opportun (pas systematiquement en haut).
- Fonctions `block_xxx()` : blocs visuels riches (grilles de cards, etc.)
  affiches en bas de section pour synthese.
- `get_academie_illustration(section)` : conserve pour compatibilite, retourne
  un en-tete leger + le bloc de synthese de fin de section.

Toutes les images utilisent le pattern Wikimedia Special:FilePath qui suit la
redirection vers la bonne URL. En cas d'echec, `onerror` masque l'image et
le contenu textuel reste intact.
"""

WIKIMEDIA_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath"


# ==========================================================
# HELPERS DE BASE
# ==========================================================


def _img(filename: str, caption: str, credit: str,
         mode: str = "contain", width: int = 800) -> str:
    """
    Bloc image Wikipedia avec legende explicative + credit + fallback.

    Args:
        filename: nom du fichier sur Wikimedia Commons.
        caption: legende affichee sous l'image (explique le lien avec le texte).
        credit: credit photo (ex: "Wikimedia Commons - CC BY-SA").
        mode: "contain" (ne zoome pas, garde tout) ou "cover" (remplit le cadre).
        width: largeur demandee a Wikipedia.
    """
    url = f"{WIKIMEDIA_BASE}/{filename}?width={width}"
    extra_class = " qt-acad-photo-cover" if mode == "cover" else ""
    # alt vide : si l'image casse, on ne veut PAS afficher de texte alt brut.
    # onerror masque toute la figure (image + legende) -> aucun placeholder moche.
    return (
        f'<figure class="qt-acad-photo{extra_class}">'
        f'<img src="{url}" alt="" loading="lazy" '
        f'onerror="this.closest(\'figure\').style.display=\'none\'"/>'
        f'<figcaption>{caption}<span class="qt-acad-photo-credit"> &middot; {credit}</span></figcaption>'
        f'</figure>'
    )


def _section_header(titre: str, accent: str, emoji: str) -> str:
    """En-tete coloree pour une section de l'academie."""
    return (
        f'<div class="qt-acad-section-header" style="--acad-accent:{accent};">'
        f'<span class="qt-acad-section-emoji">{emoji}</span>'
        f'<strong>{titre}</strong>'
        f'</div>'
    )


def _retenir(accent: str, contenu: str) -> str:
    """Bloc 'A retenir' uniforme."""
    return (
        f'<div class="qt-acad-retenir" style="border-left-color:{accent};">'
        f'<strong>💡 A retenir :</strong><br>{contenu}'
        f'</div>'
    )


# ==========================================================
# IMAGES INDIVIDUELLES (a placer dans le texte)
# ==========================================================


def img_chandelier() -> str:
    return _img(
        "Candlestick_chart_scheme_03-en.svg",
        "Anatomie d'un chandelier japonais : ouverture, plus haut, plus bas, cloture (OHLC). "
        "C'est la brique de base de tous les graphiques de marche.",
        "Wikimedia Commons - Public domain",
        mode="contain",
    )


def img_gaussienne() -> str:
    return _img(
        "Standard_deviation_diagram.svg",
        "Loi normale : 68% des rendements quotidiens tombent dans -1 sigma a +1 sigma, "
        "95% dans -2 a +2 sigma. Les krachs (-10% en un jour) sont theoriquement impossibles "
        "selon ce modele, alors qu'ils arrivent en pratique tous les 5-10 ans.",
        "Wikimedia Commons - CC BY-SA",
        mode="contain",
    )


def img_fed_building() -> str:
    return _img(
        "Marriner_S._Eccles_Federal_Reserve_Board_Building.jpg",
        "Le siege de la Federal Reserve a Washington D.C. C'est ici que se decident les taux "
        "directeurs qui orientent toute la liquidite mondiale.",
        "Wikimedia Commons - Public domain",
        mode="cover",
    )


def img_crowd_1929() -> str:
    return _img(
        "Crowd_outside_nyse.jpg",
        "Foule paniquee devant le New York Stock Exchange, 24 octobre 1929. "
        "Le krach effacera 89% de la valeur du Dow Jones sur 3 ans.",
        "Wikimedia Commons - Public domain",
        mode="cover",
    )


def img_gas_line_1973() -> str:
    return _img(
        "Line_at_a_gas_station,_June_15,_1979.jpg",
        "Files d'attente aux stations-service pendant le choc petrolier. L'embargo OPEP "
        "a quadruple le prix du baril en quelques mois, provoquant une stagflation mondiale.",
        "Wikimedia Commons - Public domain (US Federal Govt)",
        mode="cover",
    )


def img_lehman_brothers() -> str:
    return _img(
        "Lehman_Brothers_Times_Square_by_David_Shankbone.jpg",
        "Le siege de Lehman Brothers a Times Square, peu apres sa faillite en septembre 2008. "
        "La 4e plus grosse banque d'investissement americaine s'est ecroulee en un week-end.",
        "Wikimedia - David Shankbone, CC BY 3.0",
        mode="cover",
    )


def img_black_monday_1987() -> str:
    return _img(
        "Black_Monday_Dow_Jones.svg",
        "Le Dow Jones le 19 octobre 1987 : -22,6% en une seule seance, record absolu jamais egale. "
        "Le trading algorithmique automatique a ete identifie comme cause principale.",
        "Wikimedia Commons - CC BY-SA",
        mode="contain",
    )


def img_markowitz_frontier() -> str:
    return _img(
        "Markowitz_frontier.jpg",
        "La frontiere efficiente de Markowitz (1952) : pour chaque niveau de risque, "
        "il existe un portefeuille qui maximise le rendement attendu. Les portefeuilles en-dessous "
        "de cette courbe sont sous-optimaux.",
        "Wikimedia Commons - CC BY-SA",
        mode="contain",
    )


def img_buffett() -> str:
    return _img(
        "Warren_Buffett_KU_Visit.jpg",
        "Warren Buffett, eleve de Benjamin Graham et figure emblematique du value investing. "
        "Berkshire Hathaway a fait +20%/an sur 60 ans en achetant des entreprises sous-evaluees "
        "avec une 'douve economique' durable.",
        "Wikimedia Commons - CC BY 2.0",
        mode="cover",
    )


def img_nyse_building() -> str:
    return _img(
        "NYSE_(September_2007).jpg",
        "Le New York Stock Exchange, premiere bourse mondiale. C'est ici que se traitent "
        "les actions des plus grandes entreprises (S&P 500, Dow Jones).",
        "Wikimedia Commons - CC BY-SA",
        mode="cover",
    )


def img_kahneman() -> str:
    return _img(
        "Daniel_KAHNEMAN.jpg",
        "Daniel Kahneman (1934-2024), Prix Nobel d'economie 2002. Avec Amos Tversky, "
        "il a demontre que les humains ne sont pas rationnels face a l'argent : "
        "perdre 100 EUR est psychologiquement deux fois plus douloureux que gagner 100 EUR.",
        "Wikimedia Commons - CC BY-SA",
        mode="cover",
    )


# ==========================================================
# BLOCS VISUELS RICHES (a placer en fin de section)
# ==========================================================


def block_crises_grid() -> str:
    """Grille de 5 crises historiques avec photos d'archive."""
    crises = [
        {
            "year": "1929",
            "name": "Krach de Wall Street",
            "img": "Crowd_outside_nyse.jpg",
            "emoji": "📉",
            "credit": "Public domain",
            "desc": "Bulle speculative + leverage 90% -> -89% sur le Dow en 3 ans. Grande Depression.",
            "color": "#dc2626",
        },
        {
            "year": "1973",
            "name": "Choc petrolier",
            "img": "Line_at_a_gas_station,_June_15,_1979.jpg",
            "emoji": "🛢️",
            "credit": "Public domain US",
            "desc": "Embargo OPEP. Baril x4 en quelques mois. Stagflation mondiale jusqu'en 1982.",
            "color": "#92400e",
        },
        {
            "year": "1987",
            "name": "Lundi noir",
            "img": "Black_Monday_Dow_Jones.svg",
            "emoji": "⚡",
            "credit": "CC BY-SA",
            "desc": "-22,6% en une seule seance. Premiers coupe-circuits introduits a Wall Street.",
            "color": "#dc2626",
        },
        {
            "year": "2008",
            "name": "Subprimes",
            "img": "Lehman_Brothers_Times_Square_by_David_Shankbone.jpg",
            "emoji": "🏦",
            "credit": "D. Shankbone, CC BY 3.0",
            "desc": "Faillite Lehman. S&P -57% en 18 mois. Sauvetage massif (TARP, QE).",
            "color": "#dc2626",
        },
        {
            "year": "2020",
            "name": "COVID-19",
            "img": "Wall_Street,_Manhattan_2009.jpg",
            "emoji": "🦠",
            "credit": "Wikimedia Commons",
            "desc": "Krach eclair (-34% en 23 jours). Sauvetage record : 10 000 milliards injectes.",
            "color": "#0891b2",
        },
    ]
    html = '<div class="qt-acad-crises">'
    for c in crises:
        html += (
            f'<article class="qt-acad-crisis-card">'
            f'<div class="qt-acad-crisis-photo" style="--crisis-color:{c["color"]};">'
            f'<div class="qt-acad-crisis-fallback">{c["emoji"]}</div>'
            f'<img src="{WIKIMEDIA_BASE}/{c["img"]}?width=640" alt="" loading="lazy" '
            f'onerror="this.style.display=\'none\'"/>'
            f'<div class="qt-acad-crisis-year" style="background:{c["color"]};">{c["year"]}</div>'
            f'</div>'
            f'<div class="qt-acad-crisis-body">'
            f'<h4 style="color:{c["color"]};">{c["name"]}</h4>'
            f'<p>{c["desc"]}</p>'
            f'<div class="qt-acad-photo-credit">{c["credit"]}</div>'
            f'</div>'
            f'</article>'
        )
    html += '</div>'
    return html


def block_strategies_grid() -> str:
    """3 profils d'investisseur cote a cote."""
    strategies = [
        {"name": "Prudent", "icon": "🛡️", "risk": "Risque bas",
         "allocation": "60% obligations<br>30% actions<br>10% or"},
        {"name": "Equilibre", "icon": "⚖️", "risk": "Risque moyen",
         "allocation": "50% actions<br>40% obligations<br>10% diversification"},
        {"name": "Agressif", "icon": "🚀", "risk": "Risque eleve",
         "allocation": "70% actions<br>20% crypto<br>10% cash"},
    ]
    html = '<div class="qt-acad-grid qt-acad-grid-3">'
    for s in strategies:
        html += (
            f'<div class="qt-acad-item qt-acad-item-tall">'
            f'<div class="qt-acad-item-icon qt-acad-item-icon-xl">{s["icon"]}</div>'
            f'<div class="qt-acad-item-label">{s["name"]}</div>'
            f'<div class="qt-acad-pill">{s["risk"]}</div>'
            f'<div class="qt-acad-alloc">{s["allocation"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def block_allocation_bars() -> str:
    """Barres horizontales d'allocation d'actifs."""
    assets = [
        {"name": "Actions", "icon": "📈", "pct": 40, "color": "#3b82f6"},
        {"name": "Obligations", "icon": "🏦", "pct": 25, "color": "#10b981"},
        {"name": "Or", "icon": "🪙", "pct": 15, "color": "#f59e0b"},
        {"name": "Crypto", "icon": "₿", "pct": 10, "color": "#8b5cf6"},
        {"name": "Cash", "icon": "💵", "pct": 10, "color": "#ec4899"},
    ]
    html = '<div class="qt-acad-alloc-bars">'
    for a in assets:
        html += (
            f'<div class="qt-acad-alloc-row">'
            f'<div class="qt-acad-alloc-label">'
            f'<span>{a["icon"]} {a["name"]}</span>'
            f'<span style="color:{a["color"]}; font-weight:700;">{a["pct"]}%</span>'
            f'</div>'
            f'<div class="qt-acad-alloc-bar-bg">'
            f'<div class="qt-acad-alloc-bar-fill" '
            f'style="background:{a["color"]}; width:{a["pct"]}%;"></div>'
            f'</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def block_biases_grid() -> str:
    """Grille des 4 grands biais comportementaux."""
    biais = [
        {"name": "PEUR", "icon": "😨", "desc": "Vendre au pire moment, apres une chute", "color": "#dc2626"},
        {"name": "CUPIDITE", "icon": "🤑", "desc": "Acheter au pic, sur un coup d'euphorie", "color": "#16a34a"},
        {"name": "FOMO", "icon": "📱", "desc": "Chaser une tendance par peur de rater", "color": "#7c3aed"},
        {"name": "ANCRAGE", "icon": "⚓", "desc": "S'accrocher au prix d'achat originel", "color": "#0891b2"},
    ]
    html = '<div class="qt-acad-grid qt-acad-grid-2">'
    for b in biais:
        html += (
            f'<div class="qt-acad-bias-card" style="--bias-color:{b["color"]};">'
            f'<div class="qt-acad-item-icon qt-acad-item-icon-xl">{b["icon"]}</div>'
            f'<div class="qt-acad-bias-name">{b["name"]}</div>'
            f'<div class="qt-acad-item-desc">{b["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def block_lexicon_grid() -> str:
    """Termes financiers essentiels en cards compactes."""
    terms = [
        {"term": "Alpha", "desc": "Surperformance vs le marche", "icon": "α"},
        {"term": "Beta", "desc": "Sensibilite vs l'indice de reference", "icon": "β"},
        {"term": "Drawdown", "desc": "Perte maximale du pic au creux", "icon": "📉"},
        {"term": "Sharpe", "desc": "Rendement par unite de risque", "icon": "⚖️"},
        {"term": "VaR 95%", "desc": "Perte maximale dans 95% des cas", "icon": "⚠️"},
        {"term": "Volatilite", "desc": "Amplitude des variations", "icon": "📊"},
    ]
    html = '<div class="qt-acad-grid qt-acad-grid-3">'
    for t in terms:
        html += (
            f'<div class="qt-acad-lex">'
            f'<div class="qt-acad-lex-icon">{t["icon"]}</div>'
            f'<div class="qt-acad-lex-term">{t["term"]}</div>'
            f'<div class="qt-acad-item-desc">{t["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def block_methodology_steps() -> str:
    """Pipeline en 4 etapes : saisie -> IA -> simulation -> resultats."""
    steps = [
        {"step": "1", "icon": "📥", "label": "SAISIE", "desc": "Votre scenario en francais"},
        {"step": "2", "icon": "🤖", "label": "IA", "desc": "Claude calibre les chocs"},
        {"step": "3", "icon": "📊", "label": "SIMULATION", "desc": "Modele probabiliste / historique"},
        {"step": "4", "icon": "📈", "label": "RESULTATS", "desc": "Graphiques + metriques"},
    ]
    html = '<div class="qt-acad-grid qt-acad-grid-4">'
    for s in steps:
        html += (
            f'<div class="qt-acad-step">'
            f'<div class="qt-acad-step-num">{s["step"]}</div>'
            f'<div class="qt-acad-item-icon qt-acad-item-icon-xl">{s["icon"]}</div>'
            f'<div class="qt-acad-item-label">{s["label"]}</div>'
            f'<div class="qt-acad-item-desc">{s["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


# ==========================================================
# COMPATIBILITE : get_academie_illustration
# ==========================================================
# Maintenant chaque section retourne seulement un en-tete leger + (optionnel)
# un bloc visuel de synthese. Les images individuelles sont placees au sein
# du texte via les fonctions img_xxx() depuis views/academie.py.

_SECTION_META = {
    "outils":       ("Lire les donnees", "#6366f1", "📊", None),
    "modeles":      ("Modeles & mathematiques", "#8b5cf6", "🔬", None),
    "macro":        ("Macro-economie", "#f59e0b", "🌍", None),
    "cas":          ("Cas historiques", "#64748b", "📚", block_crises_grid),
    "strategies":   ("Strategies d'investissement", "#8b5cf6", "🎯", block_strategies_grid),
    "construction": ("Construction de portefeuille", "#3b82f6", "🧩", block_allocation_bars),
    "biais":        ("Biais comportementaux", "#f59e0b", "🧠", block_biases_grid),
    "lexique":      ("Lexique", "#06b6d4", "📖", block_lexicon_grid),
    "methodologie": ("Methodologie", "#8b5cf6", "⚙️", block_methodology_steps),
}


def get_academie_illustration(section: str) -> str:
    """
    Retourne un en-tete compact pour la section (appele en debut de section).
    L'en-tete est volontairement leger : un seul titre colore, sans image
    par defaut. Les images sont placees au sein du contenu via img_xxx().
    """
    meta = _SECTION_META.get(section)
    if not meta:
        return ""
    titre, accent, emoji, _ = meta
    return _section_header(titre, accent, emoji)


def get_academie_synthese(section: str) -> str:
    """
    Retourne le bloc de synthese a placer EN FIN de section :
    - un bloc visuel riche (crises grid, strategies grid, etc.) si pertinent
    - eventuellement un "a retenir"
    """
    meta = _SECTION_META.get(section)
    if not meta:
        return ""
    _, accent, _, block_fn = meta
    return block_fn() if block_fn else ""
