"""
components/academie_illustrations.py
====================================
Blocs visuels enrichis pour chaque section de l'Académie.

Combine :
- Image réelle (Wikimedia Commons) : photo d'événement historique ou
  illustration documentaire. Stable via Special:FilePath qui redirige.
- Bloc de contenu structuré en dessous : cards / grilles / "à retenir".

En cas d'echec de chargement de l'image, onerror masque l'element :
le contenu textuel reste parfaitement lisible.
"""

WIKIMEDIA_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath"


def _wiki_img(filename: str, alt: str, credit: str = "Wikimedia Commons",
              width: int = 800) -> str:
    """
    Retourne un bloc image Wikimedia avec credit et fallback gracieux.
    `filename` : nom du fichier sur Commons (sans le 'File:' prefix).
    """
    url = f"{WIKIMEDIA_BASE}/{filename}?width={width}"
    return (
        f'<figure class="qt-acad-photo">'
        f'<img src="{url}" alt="{alt}" loading="lazy" '
        f'onerror="this.parentElement.style.display=\'none\'"/>'
        f'<figcaption>{alt} <span class="qt-acad-photo-credit">· {credit}</span></figcaption>'
        f'</figure>'
    )


def _card_header(titre: str, accent: str, emoji: str) -> str:
    """En-tête coloré pour une carte d'illustration."""
    return (
        f'<div style="'
        f'background:linear-gradient(135deg, {accent}15 0%, {accent}05 100%); '
        f'border-left:4px solid {accent}; padding:14px 16px; '
        f'border-radius:8px; margin-bottom:12px;">'
        f'<span style="font-size:1.3em; margin-right:10px;">{emoji}</span>'
        f'<strong style="color:{accent}; font-size:1.05em;">{titre}</strong>'
        f'</div>'
    )


def _item_grid(items: list) -> str:
    """Grille d'items (3 colonnes)."""
    html = '<div class="qt-acad-grid qt-acad-grid-3">'
    for item in items:
        html += (
            f'<div class="qt-acad-item">'
            f'<div class="qt-acad-item-icon">{item["icon"]}</div>'
            f'<div class="qt-acad-item-label">{item["label"]}</div>'
            f'<div class="qt-acad-item-desc">{item["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def _retenir(accent: str, contenu: str) -> str:
    """Bloc 'À retenir' avec accent coloré."""
    return (
        f'<div class="qt-acad-retenir" style="border-left-color:{accent};">'
        f'<strong>💡 À retenir :</strong><br>{contenu}'
        f'</div>'
    )


# ==========================================================
# SECTIONS DE L'ACADEMIE
# ==========================================================


def illu_outils():
    """Lecture des données : chandelier, volume, analyses."""
    items = [
        {"icon": "📊", "label": "Chandeliers", "desc": "OHLC — les 4 prix clés (ouverture, plus haut, plus bas, clôture)"},
        {"icon": "📈", "label": "Volume", "desc": "Mesure l'activité du marché"},
        {"icon": "📉", "label": "Tendance", "desc": "Moyennes mobiles 50/200 jours"},
    ]
    html = _wiki_img("Candlestick_chart_scheme_03-en.svg",
                     "Schéma d'un chandelier japonais",
                     "Wikimedia Commons · Public domain")
    html += _card_header("Lire les données de marché", "#319795", "📊")
    html += _item_grid(items)
    html += _retenir("#319795",
                     "Les chandeliers montrent la tension acheteur-vendeur. "
                     "Le volume confirme la force des mouvements. "
                     "Les moyennes mobiles révèlent la tendance sous-jacente.")
    return html


def illu_modeles():
    """Modèles & mathématiques : loi normale, Sharpe, VaR."""
    items = [
        {"icon": "🔔", "label": "Loi Normale", "desc": "Distribution des rendements quotidiens"},
        {"icon": "📐", "label": "Sharpe Ratio", "desc": "Rendement par unité de risque"},
        {"icon": "⚠️", "label": "VaR 95%", "desc": "Perte max attendue 95% du temps"},
    ]
    html = _wiki_img("Standard_deviation_diagram.svg",
                     "Distribution normale — 68-95-99.7",
                     "Wikimedia Commons · CC BY-SA")
    html += _card_header("Modèles & mathématiques", "#7c3aed", "🔬")
    html += _item_grid(items)
    html += _retenir("#7c3aed",
                     "La loi normale modélise les variations de marché. "
                     "Un Sharpe élevé = bon rendement avec peu de risque. "
                     "VaR = la perte que vous acceptez de subir 95% du temps.")
    return html


def illu_macro():
    """Macro-économie : inflation, taux, croissance."""
    items = [
        {"icon": "💰", "label": "Inflation", "desc": "↗ Hausse générale des prix"},
        {"icon": "🏛️", "label": "Taux Directeurs", "desc": "↑ Politique monétaire des banques centrales"},
        {"icon": "🏭", "label": "Croissance PIB", "desc": "↔ Activité économique globale"},
    ]
    html = _wiki_img("Marriner_S._Eccles_Federal_Reserve_Board_Building.jpg",
                     "Federal Reserve — Washington D.C.",
                     "Wikimedia Commons · Public domain")
    html += _card_header("Macro-économie", "#d97706", "🌍")
    html += _item_grid(items)
    html += _retenir("#d97706",
                     "↑ Inflation → Banques centrales ↑ taux → Actions ralentissent, obligations baissent.<br>"
                     "↑ Croissance → Actions montent. Les cycles économiques dictent tout.")
    return html


def illu_cas_historiques():
    """100 ans de crises avec photos d'archive."""
    crises = [
        {
            "year": "1929",
            "name": "Krach de Wall Street",
            "img": "Crowd_outside_nyse.jpg",
            "alt": "Foule devant le NYSE — Krach de 1929",
            "credit": "Wikimedia · Public domain",
            "desc": "Bulle spéculative → effondrement → Grande Dépression. -89% sur le Dow Jones en 3 ans.",
            "color": "#dc2626",
        },
        {
            "year": "1973",
            "name": "Choc pétrolier",
            "img": "Line_at_a_gas_station,_June_15,_1979.jpg",
            "alt": "File d'attente à une station-service — Crise pétrolière",
            "credit": "Wikimedia · Public domain (US Federal Govt)",
            "desc": "Embargo OPEP. Prix du baril ×4 en quelques mois. Stagflation mondiale.",
            "color": "#92400e",
        },
        {
            "year": "1987",
            "name": "Lundi noir",
            "img": "Black_Monday_Dow_Jones.svg",
            "alt": "Effondrement Dow Jones 19 octobre 1987",
            "credit": "Wikimedia · CC BY-SA",
            "desc": "-22% en une seule journée. Trading algorithmique mis en cause.",
            "color": "#dc2626",
        },
        {
            "year": "2008",
            "name": "Crise des subprimes",
            "img": "Lehman_Brothers_Times_Square_by_David_Shankbone.jpg",
            "alt": "Lehman Brothers — Times Square, septembre 2008",
            "credit": "Wikimedia · David Shankbone, CC BY 3.0",
            "desc": "Faillite Lehman Brothers. Effondrement immobilier US. Sauvetage massif des banques.",
            "color": "#dc2626",
        },
        {
            "year": "2020",
            "name": "COVID-19",
            "img": "Empty_streets_of_Manhattan_during_COVID-19_pandemic_(49736552003).jpg",
            "alt": "Rues vides de Manhattan — pandémie COVID-19",
            "credit": "Wikimedia · CC BY 2.0",
            "desc": "Krach éclair en mars 2020. Plans de relance massifs. Rebond record sur 18 mois.",
            "color": "#0891b2",
        },
    ]
    html = _card_header("100 ans de crises & opportunités", "#475569", "📚")
    html += '<div class="qt-acad-crises">'
    for c in crises:
        html += (
            f'<article class="qt-acad-crisis-card">'
            f'<div class="qt-acad-crisis-photo">'
            f'<img src="{WIKIMEDIA_BASE}/{c["img"]}?width=640" alt="{c["alt"]}" loading="lazy" '
            f'onerror="this.parentElement.classList.add(\'qt-acad-crisis-photo-fallback\'); '
            f'this.style.display=\'none\'"/>'
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
    html += _retenir("#475569",
                     "L'histoire se répète mais ne se copie jamais à l'identique. "
                     "Chaque crise offre des leçons : panique vs prise de profit, "
                     "diversification vs concentration, timing vs buy-and-hold.")
    return html


def illu_strategies():
    """Stratégies d'investissement : de prudent à agressif."""
    strategies = [
        {"name": "Prudent", "icon": "🛡️", "risk": "Risque bas",
         "allocation": "60% obligations<br>30% actions<br>10% or"},
        {"name": "Équilibré", "icon": "⚖️", "risk": "Risque moyen",
         "allocation": "50% actions<br>40% obligations<br>10% diversification"},
        {"name": "Agressif", "icon": "🚀", "risk": "Risque élevé",
         "allocation": "70% actions<br>20% crypto<br>10% cash"},
    ]
    html = _wiki_img("Markowitz_frontier.jpg",
                     "Frontière efficiente de Markowitz",
                     "Wikimedia Commons · CC BY-SA")
    html += _card_header("Stratégies d'investissement", "#7c3aed", "🎯")
    html += '<div class="qt-acad-grid qt-acad-grid-3">'
    for strat in strategies:
        html += (
            f'<div class="qt-acad-item qt-acad-item-tall">'
            f'<div class="qt-acad-item-icon qt-acad-item-icon-xl">{strat["icon"]}</div>'
            f'<div class="qt-acad-item-label">{strat["name"]}</div>'
            f'<div class="qt-acad-pill">{strat["risk"]}</div>'
            f'<div class="qt-acad-alloc">{strat["allocation"]}</div>'
            f'</div>'
        )
    html += '</div>'
    html += _retenir("#7c3aed",
                     "Le bon profil dépend de votre horizon et votre tolérance à la perte. "
                     "Un horizon long permet plus de risque (le temps lisse les chocs).")
    return html


def illu_construction():
    """Construction : diversification et rééquilibrage."""
    assets = [
        {"name": "Actions", "icon": "📈", "pct": 40, "color": "#3b82f6"},
        {"name": "Obligations", "icon": "🏦", "pct": 25, "color": "#10b981"},
        {"name": "Or", "icon": "🪙", "pct": 15, "color": "#f59e0b"},
        {"name": "Crypto", "icon": "₿", "pct": 10, "color": "#8b5cf6"},
        {"name": "Cash", "icon": "💵", "pct": 10, "color": "#ec4899"},
    ]
    html = _card_header("Construction de portefeuille", "#3b82f6", "🧩")
    html += '<div class="qt-acad-alloc-bars">'
    for asset in assets:
        html += (
            f'<div class="qt-acad-alloc-row">'
            f'<div class="qt-acad-alloc-label">'
            f'<span>{asset["icon"]} {asset["name"]}</span>'
            f'<span style="color:{asset["color"]}; font-weight:700;">{asset["pct"]}%</span>'
            f'</div>'
            f'<div class="qt-acad-alloc-bar-bg">'
            f'<div class="qt-acad-alloc-bar-fill" '
            f'style="background:{asset["color"]}; width:{asset["pct"]}%;"></div>'
            f'</div>'
            f'</div>'
        )
    html += '</div>'
    html += _retenir("#3b82f6",
                     "Plus on diversifie, moins le risque est concentré. "
                     "Rééquilibrez régulièrement (1-2x par an) pour maintenir l'allocation cible.")
    return html


def illu_biais():
    """Biais comportementaux."""
    biais_list = [
        {"name": "PEUR", "icon": "😨", "desc": "Vendre au pire moment, après une chute", "color": "#dc2626"},
        {"name": "CUPIDITÉ", "icon": "🤑", "desc": "Acheter au pic, sur un coup d'euphorie", "color": "#16a34a"},
        {"name": "FOMO", "icon": "📱", "desc": "Chaser une tendance par peur de rater", "color": "#7c3aed"},
        {"name": "ANCRAGE", "icon": "⚓", "desc": "S'accrocher au prix d'achat originel", "color": "#0891b2"},
    ]
    html = _wiki_img("Fear_and_Greed_Index_(crop).png",
                     "Fear & Greed Index",
                     "Wikimedia Commons · CC BY-SA")
    html += _card_header("Biais comportementaux", "#d97706", "🧠")
    html += '<div class="qt-acad-grid qt-acad-grid-2">'
    for bias in biais_list:
        html += (
            f'<div class="qt-acad-bias-card" style="--bias-color:{bias["color"]};">'
            f'<div class="qt-acad-item-icon qt-acad-item-icon-xl">{bias["icon"]}</div>'
            f'<div class="qt-acad-bias-name">{bias["name"]}</div>'
            f'<div class="qt-acad-item-desc">{bias["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    html += _retenir("#d97706",
                     "Vos émotions sont vos pires ennemis en bourse. "
                     "Créez un plan d'investissement et respectez-le. "
                     "La discipline bat la prédiction.")
    return html


def illu_lexique():
    """Lexique financier."""
    terms = [
        {"term": "Alpha", "desc": "Surperformance vs le marché", "icon": "α"},
        {"term": "Beta", "desc": "Sensibilité vs l'indice de référence", "icon": "β"},
        {"term": "Drawdown", "desc": "Perte maximale du pic au creux", "icon": "📉"},
        {"term": "Sharpe", "desc": "Rendement par unité de risque", "icon": "⚖️"},
        {"term": "VaR 95%", "desc": "Perte maximale dans 95% des cas", "icon": "⚠️"},
        {"term": "Volatilité", "desc": "Amplitude des variations", "icon": "📊"},
    ]
    html = _card_header("Lexique", "#0891b2", "📖")
    html += '<div class="qt-acad-grid qt-acad-grid-3">'
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


def illu_methodologie():
    """Méthodologie : pipeline Yahoo + IA + simulation."""
    steps = [
        {"step": "1", "icon": "📥", "label": "SAISIE", "desc": "Votre scénario en français"},
        {"step": "2", "icon": "🤖", "label": "IA", "desc": "Claude calibre les chocs"},
        {"step": "3", "icon": "📊", "label": "SIMULATION", "desc": "Modèle probabiliste / historique"},
        {"step": "4", "icon": "📈", "label": "RÉSULTATS", "desc": "Graphiques + métriques"},
    ]
    html = _card_header("Méthodologie", "#7c3aed", "⚙️")
    html += '<div class="qt-acad-grid qt-acad-grid-4">'
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
    html += _retenir("#7c3aed",
                     "Yahoo Finance fournit les vrais prix actuels. L'IA analyse et calibre vos "
                     "scénarios à partir des crises historiques. Les simulations testent 50-1000 "
                     "trajectoires. Vous récupérez des résultats analysables et exportables.")
    return html


_ACADEMIE_ILLUSTRATIONS = {
    "outils":       illu_outils,
    "modeles":      illu_modeles,
    "macro":        illu_macro,
    "cas":          illu_cas_historiques,
    "strategies":   illu_strategies,
    "construction": illu_construction,
    "biais":        illu_biais,
    "lexique":      illu_lexique,
    "methodologie": illu_methodologie,
}


def get_academie_illustration(section: str) -> str:
    """Retourne l'illustration HTML pour une section de l'académie."""
    fn = _ACADEMIE_ILLUSTRATIONS.get(section)
    return fn() if fn else ""
