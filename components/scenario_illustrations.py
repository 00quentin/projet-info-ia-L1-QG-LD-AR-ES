"""
components/scenario_illustrations.py
====================================
Illustrations SVG animées pour les cartes de scénarios.
Chaque scénario a sa propre illustration vectorielle riche et animée,
inspirée du style des grands sites fintech (Stripe, Linear, Vercel).

Toutes les animations sont en CSS pur (pas de JS), pour rester fluide
et léger même avec plusieurs cartes affichées simultanément.
"""

# Hauteur fixe pour homogénéité visuelle
ILLUSTRATION_HEIGHT = 140


def _wrap(svg_inner: str, accent: str, bg_gradient: str, scenario_class: str) -> str:
    """Wrapper commun à toutes les illustrations : viewBox + gradient de fond."""
    return (
        f'<div class="qt-scenario-illu {scenario_class}" '
        f'style="--scn-accent:{accent}; background:{bg_gradient};">'
        f'<svg viewBox="0 0 320 140" xmlns="http://www.w3.org/2000/svg" '
        f'preserveAspectRatio="xMidYMid slice" width="100%" height="100%">'
        f'{svg_inner}'
        f'</svg>'
        f'</div>'
    )


def illu_guerre_mondiale() -> str:
    """Épées croisées + ondes d'explosion concentriques."""
    inner = '''
    <defs>
        <linearGradient id="g_war_metal" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#e2e8f0"/>
            <stop offset="50%" stop-color="#94a3b8"/>
            <stop offset="100%" stop-color="#475569"/>
        </linearGradient>
    </defs>
    <!-- Ondes d'explosion -->
    <circle cx="160" cy="70" r="20" fill="none" stroke="#dc2626" stroke-width="1.5" opacity="0.6">
        <animate attributeName="r" values="10;55;10" dur="2.8s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.7;0;0.7" dur="2.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="160" cy="70" r="15" fill="none" stroke="#ef4444" stroke-width="1" opacity="0.4">
        <animate attributeName="r" values="5;45;5" dur="2.8s" begin="0.6s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.6;0;0.6" dur="2.8s" begin="0.6s" repeatCount="indefinite"/>
    </circle>
    <!-- Épée 1 (rotation droite) -->
    <g transform="translate(160 70) rotate(45)" class="qt-svg-pulse">
        <rect x="-3" y="-50" width="6" height="55" fill="url(#g_war_metal)" rx="1"/>
        <polygon points="0,-55 -4,-50 4,-50" fill="#e2e8f0"/>
        <rect x="-12" y="5" width="24" height="4" fill="#78350f" rx="1"/>
        <rect x="-2" y="9" width="4" height="14" fill="#92400e" rx="1"/>
        <circle cx="0" cy="25" r="3" fill="#fbbf24"/>
    </g>
    <!-- Épée 2 (rotation gauche) -->
    <g transform="translate(160 70) rotate(-45)" class="qt-svg-pulse" style="animation-delay:0.4s;">
        <rect x="-3" y="-50" width="6" height="55" fill="url(#g_war_metal)" rx="1"/>
        <polygon points="0,-55 -4,-50 4,-50" fill="#e2e8f0"/>
        <rect x="-12" y="5" width="24" height="4" fill="#78350f" rx="1"/>
        <rect x="-2" y="9" width="4" height="14" fill="#92400e" rx="1"/>
        <circle cx="0" cy="25" r="3" fill="#fbbf24"/>
    </g>
    <!-- Étincelles -->
    <circle cx="160" cy="70" r="2" fill="#fde047">
        <animate attributeName="r" values="2;5;2" dur="0.8s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;0.3;1" dur="0.8s" repeatCount="indefinite"/>
    </circle>
    '''
    return _wrap(inner, "#dc2626",
                 "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)",
                 "scn-guerre")


def illu_pandemie() -> str:
    """Virus stylisé avec spikes qui pulsent + particules en suspension."""
    inner = '''
    <!-- Particules flottantes -->
    <g opacity="0.5">
        <circle cx="40" cy="30" r="2" fill="#dc2626">
            <animate attributeName="cy" values="30;110;30" dur="4s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0;0.6;0" dur="4s" repeatCount="indefinite"/>
        </circle>
        <circle cx="280" cy="40" r="1.5" fill="#ef4444">
            <animate attributeName="cy" values="40;120;40" dur="5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0;0.5;0" dur="5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="80" cy="20" r="1" fill="#dc2626">
            <animate attributeName="cy" values="20;100;20" dur="3.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0;0.7;0" dur="3.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="240" cy="100" r="1.5" fill="#ef4444">
            <animate attributeName="cy" values="100;20;100" dur="4.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0;0.5;0" dur="4.5s" repeatCount="indefinite"/>
        </circle>
    </g>
    <!-- Virus principal -->
    <g transform="translate(160 70)" class="qt-svg-rotate-slow">
        <!-- Spikes -->
        <g fill="#dc2626">
            <circle cx="0" cy="-38" r="5"/><rect x="-1.5" y="-38" width="3" height="12" rx="1"/>
            <circle cx="27" cy="-27" r="5"/><rect x="25.5" y="-32" width="3" height="10" rx="1" transform="rotate(45 27 -27)"/>
            <circle cx="38" cy="0" r="5"/><rect x="33" y="-1.5" width="12" height="3" rx="1"/>
            <circle cx="27" cy="27" r="5"/><rect x="25.5" y="22" width="3" height="10" rx="1" transform="rotate(-45 27 27)"/>
            <circle cx="0" cy="38" r="5"/><rect x="-1.5" y="26" width="3" height="12" rx="1"/>
            <circle cx="-27" cy="27" r="5"/><rect x="-28.5" y="22" width="3" height="10" rx="1" transform="rotate(45 -27 27)"/>
            <circle cx="-38" cy="0" r="5"/><rect x="-45" y="-1.5" width="12" height="3" rx="1"/>
            <circle cx="-27" cy="-27" r="5"/><rect x="-28.5" y="-32" width="3" height="10" rx="1" transform="rotate(-45 -27 -27)"/>
        </g>
    </g>
    <!-- Corps central avec pulse -->
    <circle cx="160" cy="70" r="22" fill="#b91c1c">
        <animate attributeName="r" values="22;25;22" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="160" cy="70" r="14" fill="#dc2626" opacity="0.7"/>
    <circle cx="155" cy="65" r="3" fill="#fca5a5" opacity="0.6"/>
    '''
    return _wrap(inner, "#dc2626",
                 "linear-gradient(135deg, #fef2f2 0%, #fecaca 100%)",
                 "scn-pandemie")


def illu_revolution_ia() -> str:
    """Réseau neuronal animé avec nœuds qui s'allument en cascade."""
    inner = '''
    <defs>
        <radialGradient id="g_ai_glow">
            <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="g_ai_line" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#a78bfa"/>
            <stop offset="100%" stop-color="#7c3aed"/>
        </linearGradient>
    </defs>
    <!-- Lueur de fond -->
    <circle cx="160" cy="70" r="55" fill="url(#g_ai_glow)" opacity="0.4">
        <animate attributeName="r" values="50;65;50" dur="3s" repeatCount="indefinite"/>
    </circle>
    <!-- Connexions -->
    <g stroke="url(#g_ai_line)" stroke-width="1" fill="none" opacity="0.5">
        <line x1="90" y1="40" x2="155" y2="60"/>
        <line x1="90" y1="100" x2="155" y2="80"/>
        <line x1="50" y1="70" x2="155" y2="70"/>
        <line x1="165" y1="60" x2="230" y2="40"/>
        <line x1="165" y1="80" x2="230" y2="100"/>
        <line x1="165" y1="70" x2="270" y2="70"/>
        <line x1="90" y1="40" x2="90" y2="100"/>
        <line x1="230" y1="40" x2="230" y2="100"/>
    </g>
    <!-- Pulses qui voyagent sur les connexions -->
    <circle r="2.5" fill="#fbbf24">
        <animateMotion dur="2s" repeatCount="indefinite" path="M 90 40 L 160 70"/>
        <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle r="2.5" fill="#fbbf24">
        <animateMotion dur="2s" begin="0.5s" repeatCount="indefinite" path="M 90 100 L 160 70"/>
        <animate attributeName="opacity" values="0;1;0" dur="2s" begin="0.5s" repeatCount="indefinite"/>
    </circle>
    <circle r="2.5" fill="#fbbf24">
        <animateMotion dur="2s" begin="1s" repeatCount="indefinite" path="M 160 70 L 230 40"/>
        <animate attributeName="opacity" values="0;1;0" dur="2s" begin="1s" repeatCount="indefinite"/>
    </circle>
    <circle r="2.5" fill="#fbbf24">
        <animateMotion dur="2s" begin="1.5s" repeatCount="indefinite" path="M 160 70 L 230 100"/>
        <animate attributeName="opacity" values="0;1;0" dur="2s" begin="1.5s" repeatCount="indefinite"/>
    </circle>
    <!-- Couche entrée -->
    <circle cx="50" cy="70" r="6" fill="#7c3aed">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="90" cy="40" r="6" fill="#7c3aed">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" begin="0.3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="90" cy="100" r="6" fill="#7c3aed">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" begin="0.6s" repeatCount="indefinite"/>
    </circle>
    <!-- Couche cachée centrale (cerveau) -->
    <circle cx="160" cy="60" r="7" fill="#8b5cf6">
        <animate attributeName="r" values="7;9;7" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="160" cy="80" r="7" fill="#8b5cf6">
        <animate attributeName="r" values="7;9;7" dur="2s" begin="0.5s" repeatCount="indefinite"/>
    </circle>
    <!-- Couche sortie -->
    <circle cx="230" cy="40" r="6" fill="#7c3aed">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" begin="0.9s" repeatCount="indefinite"/>
    </circle>
    <circle cx="230" cy="100" r="6" fill="#7c3aed">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" begin="1.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="270" cy="70" r="6" fill="#7c3aed">
        <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" begin="1.5s" repeatCount="indefinite"/>
    </circle>
    '''
    return _wrap(inner, "#7c3aed",
                 "linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)",
                 "scn-ia")


def illu_krach() -> str:
    """Courbe boursière qui plonge avec bougies rouges + buildings."""
    inner = '''
    <defs>
        <linearGradient id="g_krach_fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#dc2626" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#dc2626" stop-opacity="0"/>
        </linearGradient>
    </defs>
    <!-- Grille de fond -->
    <g stroke="#fecaca" stroke-width="0.5" opacity="0.6">
        <line x1="0" y1="30" x2="320" y2="30"/>
        <line x1="0" y1="60" x2="320" y2="60"/>
        <line x1="0" y1="90" x2="320" y2="90"/>
        <line x1="0" y1="120" x2="320" y2="120"/>
    </g>
    <!-- Aire sous la courbe -->
    <path d="M 10 25 L 50 35 L 90 30 L 130 50 L 170 75 L 210 100 L 250 115 L 295 125 L 295 140 L 10 140 Z"
          fill="url(#g_krach_fill)">
        <animate attributeName="opacity" values="0.4;0.8;0.4" dur="3s" repeatCount="indefinite"/>
    </path>
    <!-- Bougies (red candles) qui chutent -->
    <g fill="#dc2626">
        <rect x="20" y="20" width="8" height="14" rx="1"/>
        <line x1="24" y1="14" x2="24" y2="38" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="55" y="28" width="8" height="12" rx="1"/>
        <line x1="59" y1="22" x2="59" y2="44" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="90" y="25" width="8" height="10" rx="1"/>
        <line x1="94" y1="20" x2="94" y2="40" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="125" y="40" width="8" height="18" rx="1"/>
        <line x1="129" y1="34" x2="129" y2="62" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="160" y="60" width="8" height="20" rx="1"/>
        <line x1="164" y1="55" x2="164" y2="85" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="195" y="85" width="8" height="22" rx="1"/>
        <line x1="199" y1="80" x2="199" y2="112" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="230" y="100" width="8" height="20" rx="1"/>
        <line x1="234" y1="95" x2="234" y2="125" stroke="#dc2626" stroke-width="1.5"/>

        <rect x="265" y="115" width="8" height="14" rx="1"/>
        <line x1="269" y1="110" x2="269" y2="134" stroke="#dc2626" stroke-width="1.5"/>
    </g>
    <!-- Courbe principale -->
    <path d="M 10 25 L 50 35 L 90 30 L 130 50 L 170 75 L 210 100 L 250 115 L 295 125"
          fill="none" stroke="#b91c1c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- Indicateur en chute (triangle pointant vers le bas) -->
    <g transform="translate(285 130)">
        <circle r="6" fill="#dc2626">
            <animate attributeName="r" values="6;9;6" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <polygon points="-3,-2 3,-2 0,3" fill="#ffffff"/>
    </g>
    '''
    return _wrap(inner, "#dc2626",
                 "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)",
                 "scn-krach")


def illu_fusion() -> str:
    """Atome avec électrons en orbite + noyau qui pulse."""
    inner = '''
    <defs>
        <radialGradient id="g_atom_core">
            <stop offset="0%" stop-color="#fde047"/>
            <stop offset="50%" stop-color="#facc15"/>
            <stop offset="100%" stop-color="#ca8a04"/>
        </radialGradient>
        <radialGradient id="g_atom_glow">
            <stop offset="0%" stop-color="#fde047" stop-opacity="0.7"/>
            <stop offset="100%" stop-color="#facc15" stop-opacity="0"/>
        </radialGradient>
    </defs>
    <!-- Lueur du noyau -->
    <circle cx="160" cy="70" r="40" fill="url(#g_atom_glow)">
        <animate attributeName="r" values="30;50;30" dur="2s" repeatCount="indefinite"/>
    </circle>
    <!-- Orbite 1 (horizontale) -->
    <ellipse cx="160" cy="70" rx="60" ry="20" fill="none" stroke="#0891b2" stroke-width="1.5" opacity="0.6"/>
    <!-- Orbite 2 (rotation 60deg) -->
    <ellipse cx="160" cy="70" rx="60" ry="20" fill="none" stroke="#06b6d4" stroke-width="1.5" opacity="0.6"
             transform="rotate(60 160 70)"/>
    <!-- Orbite 3 (rotation 120deg) -->
    <ellipse cx="160" cy="70" rx="60" ry="20" fill="none" stroke="#22d3ee" stroke-width="1.5" opacity="0.6"
             transform="rotate(120 160 70)"/>
    <!-- Électron 1 -->
    <circle r="4" fill="#0e7490">
        <animateMotion dur="2s" repeatCount="indefinite">
            <mpath href="#orbit1"/>
        </animateMotion>
    </circle>
    <path id="orbit1" d="M 220 70 A 60 20 0 1 1 100 70 A 60 20 0 1 1 220 70" fill="none" opacity="0"/>
    <!-- Électron 2 -->
    <circle r="4" fill="#0e7490">
        <animateMotion dur="2.5s" repeatCount="indefinite" rotate="auto">
            <mpath href="#orbit2"/>
        </animateMotion>
    </circle>
    <path id="orbit2" d="M 220 70 A 60 20 0 1 1 100 70 A 60 20 0 1 1 220 70"
          fill="none" opacity="0" transform="rotate(60 160 70)"/>
    <!-- Électron 3 -->
    <circle r="4" fill="#0e7490">
        <animateMotion dur="3s" repeatCount="indefinite" rotate="auto">
            <mpath href="#orbit3"/>
        </animateMotion>
    </circle>
    <path id="orbit3" d="M 220 70 A 60 20 0 1 1 100 70 A 60 20 0 1 1 220 70"
          fill="none" opacity="0" transform="rotate(120 160 70)"/>
    <!-- Noyau -->
    <circle cx="160" cy="70" r="14" fill="url(#g_atom_core)">
        <animate attributeName="r" values="14;17;14" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="156" cy="66" r="3" fill="#fef9c3" opacity="0.7"/>
    '''
    return _wrap(inner, "#0891b2",
                 "linear-gradient(135deg, #ecfeff 0%, #cffafe 100%)",
                 "scn-fusion")


def illu_petrole() -> str:
    """Derrick pétrolier + gouttes qui tombent + barils."""
    inner = '''
    <defs>
        <linearGradient id="g_oil_drop" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#451a03"/>
            <stop offset="100%" stop-color="#78350f"/>
        </linearGradient>
        <linearGradient id="g_barrel" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#a16207"/>
            <stop offset="50%" stop-color="#854d0e"/>
            <stop offset="100%" stop-color="#713f12"/>
        </linearGradient>
    </defs>
    <!-- Sol -->
    <rect x="0" y="120" width="320" height="20" fill="#fed7aa" opacity="0.5"/>
    <line x1="0" y1="120" x2="320" y2="120" stroke="#c2410c" stroke-width="1" opacity="0.4"/>
    <!-- Derrick (tour en treillis métallique) -->
    <g stroke="#78350f" stroke-width="2" fill="none">
        <line x1="100" y1="120" x2="125" y2="30"/>
        <line x1="150" y1="120" x2="125" y2="30"/>
        <line x1="110" y1="90" x2="140" y2="90"/>
        <line x1="115" y1="70" x2="135" y2="70"/>
        <line x1="118" y1="50" x2="132" y2="50"/>
        <line x1="105" y1="105" x2="145" y2="105"/>
    </g>
    <!-- Tête de pompage (haut du derrick) -->
    <rect x="120" y="22" width="10" height="10" fill="#92400e"/>
    <circle cx="125" cy="35" r="3" fill="#fbbf24">
        <animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite"/>
    </circle>
    <!-- Gouttes de pétrole qui tombent -->
    <ellipse cx="125" cy="50" rx="3" ry="5" fill="url(#g_oil_drop)">
        <animate attributeName="cy" values="50;120;50" dur="1.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;1;0" dur="1.5s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="125" cy="60" rx="2.5" ry="4" fill="url(#g_oil_drop)">
        <animate attributeName="cy" values="60;120;60" dur="1.5s" begin="0.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;1;0" dur="1.5s" begin="0.5s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="125" cy="70" rx="2" ry="3" fill="url(#g_oil_drop)">
        <animate attributeName="cy" values="70;120;70" dur="1.5s" begin="1s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;1;0" dur="1.5s" begin="1s" repeatCount="indefinite"/>
    </ellipse>
    <!-- Flaque qui pulse -->
    <ellipse cx="125" cy="120" rx="20" ry="3" fill="#451a03" opacity="0.6">
        <animate attributeName="rx" values="15;22;15" dur="2s" repeatCount="indefinite"/>
    </ellipse>
    <!-- Barils empilés à droite -->
    <g transform="translate(210 80)">
        <!-- Baril 1 (bas) -->
        <ellipse cx="20" cy="40" rx="20" ry="5" fill="url(#g_barrel)"/>
        <rect x="0" y="20" width="40" height="20" fill="url(#g_barrel)"/>
        <ellipse cx="20" cy="20" rx="20" ry="5" fill="#a16207"/>
        <line x1="0" y1="30" x2="40" y2="30" stroke="#451a03" stroke-width="1"/>
        <!-- Baril 2 (haut) -->
        <ellipse cx="35" cy="20" rx="15" ry="4" fill="url(#g_barrel)"/>
        <rect x="20" y="5" width="30" height="15" fill="url(#g_barrel)"/>
        <ellipse cx="35" cy="5" rx="15" ry="4" fill="#a16207"/>
        <line x1="20" y1="12" x2="50" y2="12" stroke="#451a03" stroke-width="0.8"/>
    </g>
    <!-- Flèche de prix qui monte -->
    <g transform="translate(50 50)">
        <path d="M 0 30 L 0 5 M -5 10 L 0 0 L 5 10" stroke="#dc2626" stroke-width="2.5"
              fill="none" stroke-linecap="round" stroke-linejoin="round">
            <animateTransform attributeName="transform" type="translate"
                              values="0 5;0 0;0 5" dur="2s" repeatCount="indefinite"/>
        </path>
        <text x="0" y="-5" text-anchor="middle" fill="#dc2626" font-size="11" font-weight="bold">$</text>
    </g>
    '''
    return _wrap(inner, "#92400e",
                 "linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%)",
                 "scn-petrole")


def illu_fed() -> str:
    """Bâtiment FED avec colonnes + courbe de taux qui grimpe."""
    inner = '''
    <defs>
        <linearGradient id="g_fed_bldg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f8fafc"/>
            <stop offset="100%" stop-color="#cbd5e1"/>
        </linearGradient>
    </defs>
    <!-- Sol -->
    <rect x="0" y="125" width="320" height="15" fill="#e2e8f0"/>
    <!-- Bâtiment FED -->
    <g transform="translate(180 50)">
        <!-- Fronton triangulaire -->
        <polygon points="0,0 70,0 35,-20" fill="#475569"/>
        <!-- Plateforme du fronton -->
        <rect x="-3" y="0" width="76" height="6" fill="#64748b"/>
        <!-- Colonnes (5) -->
        <rect x="5" y="6" width="6" height="60" fill="url(#g_fed_bldg)"/>
        <rect x="19" y="6" width="6" height="60" fill="url(#g_fed_bldg)"/>
        <rect x="33" y="6" width="6" height="60" fill="url(#g_fed_bldg)"/>
        <rect x="47" y="6" width="6" height="60" fill="url(#g_fed_bldg)"/>
        <rect x="61" y="6" width="6" height="60" fill="url(#g_fed_bldg)"/>
        <!-- Base -->
        <rect x="-5" y="66" width="80" height="9" fill="#64748b"/>
        <!-- Marches -->
        <rect x="-8" y="69" width="86" height="3" fill="#94a3b8"/>
        <rect x="-10" y="72" width="90" height="3" fill="#cbd5e1"/>
        <!-- Texte FED -->
        <text x="35" y="-7" text-anchor="middle" fill="#fbbf24" font-size="7" font-weight="bold">FED</text>
    </g>
    <!-- Courbe de taux qui grimpe (gauche) -->
    <g transform="translate(20 50)">
        <!-- Axes -->
        <line x1="0" y1="0" x2="0" y2="70" stroke="#94a3b8" stroke-width="1"/>
        <line x1="0" y1="70" x2="100" y2="70" stroke="#94a3b8" stroke-width="1"/>
        <!-- Courbe -->
        <path d="M 0 60 L 20 58 L 40 50 L 60 35 L 80 15 L 100 5"
              fill="none" stroke="#dc2626" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Point clignotant en haut -->
        <circle cx="100" cy="5" r="5" fill="#dc2626">
            <animate attributeName="r" values="5;8;5" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="100" cy="5" r="3" fill="#fee2e2"/>
        <!-- Pourcentage -->
        <text x="100" y="-3" text-anchor="middle" fill="#dc2626" font-size="11" font-weight="bold">
            +2%
            <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/>
        </text>
        <!-- Flèche montante -->
        <path d="M 90 18 L 100 5 L 95 8 M 100 5 L 102 12"
              stroke="#dc2626" stroke-width="2" fill="none" stroke-linecap="round"/>
    </g>
    '''
    return _wrap(inner, "#475569",
                 "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
                 "scn-fed")


def illu_chine_taiwan() -> str:
    """Globe avec lignes de tension + zone surlignée Asie."""
    inner = '''
    <defs>
        <radialGradient id="g_globe" cx="40%" cy="40%">
            <stop offset="0%" stop-color="#bfdbfe"/>
            <stop offset="100%" stop-color="#1e40af"/>
        </radialGradient>
    </defs>
    <!-- Globe -->
    <circle cx="160" cy="70" r="50" fill="url(#g_globe)"/>
    <!-- Méridiens -->
    <g fill="none" stroke="#dbeafe" stroke-width="0.7" opacity="0.6">
        <ellipse cx="160" cy="70" rx="50" ry="50"/>
        <ellipse cx="160" cy="70" rx="40" ry="50"/>
        <ellipse cx="160" cy="70" rx="25" ry="50"/>
        <ellipse cx="160" cy="70" rx="10" ry="50"/>
        <ellipse cx="160" cy="70" rx="50" ry="15"/>
        <ellipse cx="160" cy="70" rx="50" ry="30"/>
    </g>
    <!-- Continents stylisés -->
    <g fill="#16a34a" opacity="0.8">
        <!-- Asie -->
        <path d="M 175 55 Q 185 45 195 50 Q 200 60 195 70 Q 185 75 175 70 Z"/>
        <!-- Petit point Taiwan -->
        <circle cx="195" cy="78" r="2.5" fill="#fbbf24">
            <animate attributeName="r" values="2.5;4.5;2.5" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <!-- Europe -->
        <path d="M 150 55 Q 160 50 165 60 Q 162 65 155 65 Z"/>
        <!-- Amériques -->
        <path d="M 125 65 Q 130 55 135 70 Q 132 85 128 80 Z"/>
    </g>
    <!-- Zone de tension avec onde -->
    <circle cx="195" cy="78" r="8" fill="none" stroke="#dc2626" stroke-width="2">
        <animate attributeName="r" values="5;20;5" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="195" cy="78" r="5" fill="none" stroke="#ef4444" stroke-width="1.5">
        <animate attributeName="r" values="3;15;3" dur="2s" begin="0.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" begin="0.5s" repeatCount="indefinite"/>
    </circle>
    <!-- Lignes de connexion mondiales -->
    <g stroke="#fbbf24" stroke-width="1" fill="none" opacity="0.4">
        <path d="M 195 78 Q 175 30 130 50">
            <animate attributeName="stroke-dasharray" values="0 100;100 0" dur="3s" repeatCount="indefinite"/>
        </path>
        <path d="M 195 78 Q 220 40 250 60">
            <animate attributeName="stroke-dasharray" values="0 100;100 0" dur="3s" begin="1s" repeatCount="indefinite"/>
        </path>
    </g>
    <!-- Icône puce électronique (semi-conducteur) -->
    <g transform="translate(45 95)">
        <rect x="0" y="0" width="24" height="24" fill="#1e293b" rx="2"/>
        <rect x="3" y="3" width="18" height="18" fill="#334155" rx="1"/>
        <!-- Broches -->
        <g fill="#64748b">
            <rect x="-2" y="5" width="2" height="2"/>
            <rect x="-2" y="11" width="2" height="2"/>
            <rect x="-2" y="17" width="2" height="2"/>
            <rect x="24" y="5" width="2" height="2"/>
            <rect x="24" y="11" width="2" height="2"/>
            <rect x="24" y="17" width="2" height="2"/>
        </g>
        <text x="12" y="15" text-anchor="middle" fill="#fbbf24" font-size="8" font-weight="bold">Si</text>
    </g>
    '''
    return _wrap(inner, "#1e40af",
                 "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
                 "scn-chine")


# Mapping nom de scénario → fonction d'illustration
_ILLUSTRATIONS = {
    "Guerre mondiale":      illu_guerre_mondiale,
    "Pandémie mondiale":    illu_pandemie,
    "Révolution IA":        illu_revolution_ia,
    "Krach 2008 bis":       illu_krach,
    "Fusion nucléaire":     illu_fusion,
    "Choc pétrolier":       illu_petrole,
    "Hausse brutale FED":   illu_fed,
    "Crise Chine-Taïwan":   illu_chine_taiwan,
}


def get_illustration(nom_scenario: str) -> str:
    """Retourne le HTML/SVG d'illustration pour un scénario, ou un fallback."""
    fn = _ILLUSTRATIONS.get(nom_scenario)
    if fn:
        return fn()
    # Fallback générique : graphique stylisé
    fallback = '''
    <g stroke="#64748b" stroke-width="2" fill="none">
        <path d="M 20 100 Q 80 60 160 80 T 300 50" stroke-linecap="round"/>
    </g>
    <circle cx="160" cy="70" r="30" fill="none" stroke="#94a3b8" stroke-width="1.5" opacity="0.5"/>
    '''
    return _wrap(fallback, "#64748b",
                 "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
                 "scn-default")
