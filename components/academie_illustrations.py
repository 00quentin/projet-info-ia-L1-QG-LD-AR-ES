"""
components/academie_illustrations.py
====================================
Blocs informatifs enrichis pour chaque section de l'Académie.
Utilise des icônes, des grilles visuelles et du contenu structuré
plutôt que des SVG générés pour une meilleure lisibilité.
"""


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
    html = '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin:12px 0;">'
    for item in items:
        html += (
            f'<div style="'
            f'background:#f8fafc; border-radius:8px; padding:12px; '
            f'border:1px solid #e2e8f0; text-align:center;">'
            f'<div style="font-size:2em; margin-bottom:6px;">{item["icon"]}</div>'
            f'<div style="font-weight:600; font-size:0.95em; color:#1e293b;">{item["label"]}</div>'
            f'<div style="font-size:0.85em; color:#64748b; margin-top:4px;">{item["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def illu_outils():
    """Lecture des données : chandelier, volume, analyses."""
    items = [
        {"icon": "📊", "label": "Chandeliers", "desc": "OHLC\nles 4 prix clés"},
        {"icon": "📈", "label": "Volume", "desc": "Activité\ndu marché"},
        {"icon": "📉", "label": "Tendance", "desc": "Moyennes\nmobiles"},
    ]
    html = _card_header("Lire les données de marché", "#319795", "📊") + _item_grid(items)
    html += (
        '<div style="background:#f0fdfa; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #319795;">'
        '<strong>💡 À retenir :</strong><br>'
        'Les chandeliers montrent la tension acheteur-vendeur. Le volume confirme la force '
        'des mouvements. Les moyennes mobiles révèlent la tendance sous-jacente.'
        '</div>'
    )
    return html


def illu_modeles():
    """Modèles & mathématiques : loi normale, Sharpe, VaR."""
    items = [
        {"icon": "🔔", "label": "Loi Normale", "desc": "Distribution\ndes rendements"},
        {"icon": "📐", "label": "Sharpe Ratio", "desc": "Rendement\npar risque"},
        {"icon": "⚠️", "label": "VaR 95%", "desc": "Perte\nmaximal attestée"},
    ]
    html = _card_header("Modèles & mathématiques", "#7c3aed", "🔬") + _item_grid(items)
    html += (
        '<div style="background:#faf5ff; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #7c3aed;">'
        '<strong>💡 À retenir :</strong><br>'
        'La loi normale aide à prévoir les mouvements. Sharpe mesure l\'efficacité : '
        'un haut Sharpe = bon rendement avec peu de risque. VaR = la perte que vous '
        'acceptez 95% du temps.'
        '</div>'
    )
    return html


def illu_macro():
    """Macro-économie : inflation, taux, croissance, cycles."""
    items = [
        {"icon": "💰", "label": "Inflation", "desc": "↗ Hausse\ndes prix"},
        {"icon": "📊", "label": "Taux Directeurs", "desc": "↑ Politique\nmonétaire"},
        {"icon": "🏭", "label": "Croissance", "desc": "↔ Activité\néco"},
    ]
    html = _card_header("Macro-économie", "#d97706", "🌍") + _item_grid(items)
    html += (
        '<div style="background:#fffbeb; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #d97706;">'
        '<strong>💡 À retenir :</strong><br>'
        '↑ Inflation → Banques centrales ↑ taux → Actions ralentissent, obligations baissent.<br>'
        '↑ Croissance → Actions montent. Cycles économiques dictent tout.'
        '</div>'
    )
    return html


def illu_cas_historiques():
    """100 ans de crises : les vraies analogies du passé."""
    crises = [
        {"year": "1929", "name": "Krach", "icon": "💔", "desc": "Wall Street s'effondre"},
        {"year": "1973", "name": "Pétrole", "icon": "🛢️", "desc": "Choc énergétique"},
        {"year": "1987", "name": "Lundi noir", "icon": "📉", "desc": "-22% en 1 jour"},
        {"year": "2008", "name": "Subprimes", "icon": "🏚️", "desc": "Crise immo globale"},
        {"year": "2020", "name": "COVID", "icon": "🦠", "desc": "Arrêt économique"},
    ]
    html = _card_header("100 ans de crises & opportunités", "#475569", "📚")
    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:12px 0;">'
    for crisis in crises:
        html += (
            f'<div style="'
            f'background:#f8fafc; border-radius:8px; padding:10px; '
            f'border:1px solid #e2e8f0;">'
            f'<div style="font-size:1.8em; margin-bottom:4px;">{crisis["icon"]}</div>'
            f'<div style="font-weight:700; color:#1e293b;">{crisis["year"]}</div>'
            f'<div style="font-weight:600; font-size:0.9em; color:#1e293b;">{crisis["name"]}</div>'
            f'<div style="font-size:0.8em; color:#64748b;">{crisis["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    html += (
        '<div style="background:#f8fafc; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #475569;">'
        '<strong>💡 À retenir :</strong><br>'
        'L\'histoire se répète. Chaque crise offre des leçons : panique vs prise de profit, '
        'diversification vs concentration, timing vs buy-and-hold.'
        '</div>'
    )
    return html


def illu_strategies():
    """Stratégies d'investissement : de prudent à agressif."""
    strategies = [
        {"name": "Prudent", "icon": "🛡️", "risk": "Bas", "allocation": "60% obligations,\n40% actions"},
        {"name": "Équilibré", "icon": "⚖️", "risk": "Moyen", "allocation": "50% actions,\n50% autres"},
        {"name": "Agressif", "icon": "🚀", "risk": "Haut", "allocation": "80% actions,\n20% cash"},
    ]
    html = _card_header("Stratégies d'investissement", "#7c3aed", "🎯")
    html += '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin:12px 0;">'
    for strat in strategies:
        html += (
            f'<div style="'
            f'background:#f8fafc; border-radius:8px; padding:12px; '
            f'border:1px solid #e2e8f0; text-align:center;">'
            f'<div style="font-size:2.5em; margin-bottom:8px;">{strat["icon"]}</div>'
            f'<div style="font-weight:700; font-size:1em; color:#1e293b;">{strat["name"]}</div>'
            f'<div style="font-size:0.85em; color:#64748b; margin:6px 0;">Risque : {strat["risk"]}</div>'
            f'<div style="font-size:0.8em; color:#475569; '
            f'background:#e2e8f0; padding:8px; border-radius:6px; margin-top:6px;">'
            f'{strat["allocation"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def illu_construction():
    """Construction : diversification et rééquilibrage."""
    assets = [
        {"name": "Actions", "icon": "📈", "pct": "40%", "color": "#3b82f6"},
        {"name": "Obligations", "icon": "🏦", "pct": "25%", "color": "#10b981"},
        {"name": "Or", "icon": "🪙", "pct": "15%", "color": "#f59e0b"},
        {"name": "Crypto", "icon": "₿", "pct": "10%", "color": "#8b5cf6"},
        {"name": "Cash", "icon": "💵", "pct": "10%", "color": "#ec4899"},
    ]
    html = _card_header("Construction de portefeuille", "#3b82f6", "🧩")
    html += '<div style="margin:12px 0;">'
    for asset in assets:
        html += (
            f'<div style="margin-bottom:10px;">'
            f'<div style="display:flex; align-items:center; justify-content:space-between;">'
            f'<span style="font-weight:600; color:#1e293b;">{asset["icon"]} {asset["name"]}</span>'
            f'<span style="font-weight:700; color:{asset["color"]};">{asset["pct"]}</span>'
            f'</div>'
            f'<div style="background:#e2e8f0; border-radius:4px; height:24px; overflow:hidden;">'
            f'<div style="background:{asset["color"]}; height:100%; width:{asset["pct"]}; '
            f'border-radius:4px;"></div>'
            f'</div>'
            f'</div>'
        )
    html += '</div>'
    html += (
        '<div style="background:#eff6ff; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #3b82f6;">'
        '<strong>💡 À retenir :</strong><br>'
        'Plus on diversifie, moins le risque est concentré. Rééquilibrez régulièrement '
        'pour maintenir l\'allocation cible.'
        '</div>'
    )
    return html


def illu_biais():
    """Biais comportementaux : la psychologie de l'investisseur."""
    biais_list = [
        {"name": "PEUR", "icon": "😨", "desc": "Vendre au pire\nmoment", "color": "#dc2626"},
        {"name": "CUPIDITÉ", "icon": "🤑", "desc": "Acheter au pic\ndu marché", "color": "#16a34a"},
        {"name": "FOMO", "icon": "📱", "desc": "Chaser les\ntrendis", "color": "#7c3aed"},
        {"name": "ANCRAGE", "icon": "⚓", "desc": "S'accrocher\naux vieux prix", "color": "#0891b2"},
    ]
    html = _card_header("Biais comportementaux", "#d97706", "🧠")
    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:12px 0;">'
    for bias in biais_list:
        html += (
            f'<div style="'
            f'background:linear-gradient(135deg, {bias["color"]}15 0%, {bias["color"]}05 100%); '
            f'border-left:4px solid {bias["color"]}; border-radius:8px; padding:12px;">'
            f'<div style="font-size:2.5em; margin-bottom:6px;">{bias["icon"]}</div>'
            f'<div style="font-weight:700; color:{bias["color"]}; margin-bottom:4px;">{bias["name"]}</div>'
            f'<div style="font-size:0.85em; color:#475569;">{bias["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    html += (
        '<div style="background:#fffbeb; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #d97706;">'
        '<strong>💡 À retenir :</strong><br>'
        'Vos émotions sont vos pires ennemis. Créez un plan et respectez-le. '
        'La discipline bat la prédiction.'
        '</div>'
    )
    return html


def illu_lexique():
    """Lexique : les vrais termes de la finance."""
    terms = [
        {"term": "Alpha", "desc": "Surperformance vs le marché", "icon": "α"},
        {"term": "Beta", "desc": "Volatilité vs l'indice", "icon": "β"},
        {"term": "Drawdown", "desc": "Perte du pic au creux", "icon": "📉"},
        {"term": "Sharpe", "desc": "Rendement/risque", "icon": "⚖️"},
        {"term": "VaR 95%", "desc": "Perte max en 95% cas", "icon": "⚠️"},
        {"term": "Volatilité", "desc": "Ecart-type quotidien", "icon": "📊"},
    ]
    html = _card_header("Lexique", "#0891b2", "📖")
    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:12px 0;">'
    for t in terms:
        html += (
            f'<div style="'
            f'background:#ecfeff; border:1px solid #a5f3fc; border-radius:8px; '
            f'padding:10px;">'
            f'<div style="font-size:1.6em; margin-bottom:4px;">{t["icon"]}</div>'
            f'<div style="font-weight:700; color:#0891b2; font-size:0.95em;">{t["term"]}</div>'
            f'<div style="font-size:0.8em; color:#475569; margin-top:4px;">{t["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def illu_methodologie():
    """Méthodologie : le pipeline de la plateforme."""
    steps = [
        {"step": "1", "icon": "📥", "label": "SAISIE", "desc": "Votre scénario en français"},
        {"step": "2", "icon": "🤖", "label": "IA", "desc": "Claude calibre les chocs"},
        {"step": "3", "icon": "📊", "label": "SIMULATION", "desc": "Modèle probabiliste/historique"},
        {"step": "4", "icon": "📈", "label": "RÉSULTATS", "desc": "Graphiques + métriques"},
    ]
    html = _card_header("Méthodologie", "#7c3aed", "⚙️")
    html += '<div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:10px; margin:12px 0;">'
    for s in steps:
        html += (
            f'<div style="'
            f'background:#f5f3ff; border:2px solid #7c3aed; border-radius:8px; '
            f'padding:14px; text-align:center;">'
            f'<div style="'
            f'background:#7c3aed; color:white; width:40px; height:40px; '
            f'border-radius:50%; display:flex; align-items:center; justify-content:center; '
            f'margin:0 auto 10px; font-weight:700; font-size:1.2em;">{s["step"]}</div>'
            f'<div style="font-size:2em; margin-bottom:6px;">{s["icon"]}</div>'
            f'<div style="font-weight:700; color:#1e293b; margin-bottom:4px;">{s["label"]}</div>'
            f'<div style="font-size:0.8em; color:#475569;">{s["desc"]}</div>'
            f'</div>'
        )
    html += '</div>'
    html += (
        '<div style="background:#f5f3ff; border-radius:8px; padding:12px; margin-top:12px; '
        'border-left:4px solid #7c3aed;">'
        '<strong>💡 À retenir :</strong><br>'
        'Yahoo Finance fournit les vrais prix actuels. L\'IA analyse et calibre vos '
        'scénarios. Les simulations testent 50-1000 trajectoires. Vous récupérez des '
        'résultats analysables et exportables.'
        '</div>'
    )
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
