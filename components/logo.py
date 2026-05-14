"""
components/logo.py
==================
Logo SVG identitaire de Quant Terminal.

Identite visuelle : carre arrondi indigo->vert (gradient), avec une
ligne de marche stylisee qui monte (signature fintech) et un point
final qui pulse (vie/temps reel).

Utilisable en plusieurs tailles : 24 (favicon), 32 (header), 64 (hero).
"""


def logo_svg(size: int = 32, animate: bool = True) -> str:
    """
    Logo Quant Terminal — carre arrondi avec courbe ascendante.

    Args:
        size: taille en px (carre).
        animate: si True, le point final pulse doucement.
    """
    pulse = ('<animate attributeName="r" values="2.5;3.5;2.5" '
             'dur="2s" repeatCount="indefinite"/>') if animate else ""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 40 40" '
        f'xmlns="http://www.w3.org/2000/svg" class="qt-logo-svg" '
        f'role="img" aria-label="Quant Terminal logo">'
        # Gradient signature : indigo vers vert TradingView
        '<defs>'
        '<linearGradient id="qtLogoGrad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%" stop-color="#6366f1"/>'
        '<stop offset="100%" stop-color="#16c784"/>'
        '</linearGradient>'
        # Glow subtil derriere le point
        '<filter id="qtLogoGlow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="1.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
        '</defs>'
        # Forme : carre arrondi
        '<rect x="2" y="2" width="36" height="36" rx="10" '
        'fill="url(#qtLogoGrad)"/>'
        # Courbe ascendante (graphique de marche stylise)
        '<path d="M 9 27 L 15 22 L 21 24 L 27 16 L 31 12" '
        'stroke="white" stroke-width="2.6" fill="none" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'opacity="0.95"/>'
        # Point final lumineux
        f'<circle cx="31" cy="12" r="2.8" fill="white" filter="url(#qtLogoGlow)">'
        f'{pulse}'
        '</circle>'
        '</svg>'
    )


def logo_brand_html(size: int = 32) -> str:
    """
    Logo + wordmark "Quant Terminal" cote a cote pour le header.
    Utilise les classes CSS qt-brand-*.
    """
    return (
        f'<div class="qt-brand">'
        f'{logo_svg(size=size)}'
        f'<div class="qt-brand-text">'
        f'<span class="qt-brand-name">Quant Terminal</span>'
        f'<span class="qt-brand-tag">Simulateur d\'investissement IA</span>'
        f'</div>'
        f'</div>'
    )
