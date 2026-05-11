"""
components/academie_illustrations.py
====================================
Illustrations SVG "hero" pour chaque section de l'Académie.
Style cohérent avec les illustrations de scénarios :
- Format paysage (400x140)
- Animations CSS subtiles
- Gradient de fond pastel
- Élément central iconique + détails périphériques
"""


def _wrap(svg_inner: str, accent: str, bg: str, label: str, sublabel: str = "") -> str:
    """Wrapper commun : illustration + bandeau labellisé en bas."""
    sub_html = (f'<span class="qt-acad-illu-sub">{sublabel}</span>'
                if sublabel else "")
    return (
        f'<div class="qt-acad-illu" style="--acad-accent:{accent}; background:{bg};">'
        f'<svg viewBox="0 0 400 140" xmlns="http://www.w3.org/2000/svg" '
        f'preserveAspectRatio="xMidYMid meet" width="100%" height="100%">'
        f'{svg_inner}'
        f'</svg>'
        f'<div class="qt-acad-illu-caption">'
        f'<span class="qt-acad-illu-label">{label}</span>{sub_html}'
        f'</div>'
        f'</div>'
    )


def illu_outils():
    """Graphique de marché : chandeliers + volume + axes."""
    inner = '''
    <defs>
        <linearGradient id="acad_g_outils" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#319795" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="#319795" stop-opacity="0"/>
        </linearGradient>
    </defs>
    <!-- Grille -->
    <g stroke="#e2e8f0" stroke-width="0.5">
        <line x1="30" y1="30" x2="380" y2="30"/>
        <line x1="30" y1="60" x2="380" y2="60"/>
        <line x1="30" y1="90" x2="380" y2="90"/>
    </g>
    <!-- Axes -->
    <line x1="30" y1="115" x2="380" y2="115" stroke="#94a3b8" stroke-width="1.2"/>
    <line x1="30" y1="20" x2="30" y2="115" stroke="#94a3b8" stroke-width="1.2"/>
    <!-- Volume bars en bas -->
    <g fill="#cbd5e1">
        <rect x="50" y="105" width="6" height="10"/>
        <rect x="80" y="100" width="6" height="15"/>
        <rect x="110" y="95" width="6" height="20"/>
        <rect x="140" y="103" width="6" height="12"/>
        <rect x="170" y="98" width="6" height="17"/>
        <rect x="200" y="90" width="6" height="25"/>
        <rect x="230" y="100" width="6" height="15"/>
        <rect x="260" y="92" width="6" height="23"/>
        <rect x="290" y="97" width="6" height="18"/>
        <rect x="320" y="88" width="6" height="27"/>
        <rect x="350" y="94" width="6" height="21"/>
    </g>
    <!-- Chandeliers -->
    <g>
        <!-- Bullish (vert) -->
        <line x1="53" y1="55" x2="53" y2="80" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="49" y="60" width="8" height="15" fill="#16a34a"/>
        <!-- Bearish (rouge) -->
        <line x1="83" y1="50" x2="83" y2="75" stroke="#dc2626" stroke-width="1.2"/>
        <rect x="79" y="55" width="8" height="12" fill="#dc2626"/>
        <!-- Bullish -->
        <line x1="113" y1="45" x2="113" y2="70" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="109" y="50" width="8" height="15" fill="#16a34a"/>
        <!-- Bullish -->
        <line x1="143" y1="38" x2="143" y2="60" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="139" y="42" width="8" height="14" fill="#16a34a"/>
        <!-- Bearish -->
        <line x1="173" y1="40" x2="173" y2="62" stroke="#dc2626" stroke-width="1.2"/>
        <rect x="169" y="45" width="8" height="12" fill="#dc2626"/>
        <!-- Bullish -->
        <line x1="203" y1="32" x2="203" y2="55" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="199" y="36" width="8" height="15" fill="#16a34a"/>
        <!-- Bearish -->
        <line x1="233" y1="35" x2="233" y2="55" stroke="#dc2626" stroke-width="1.2"/>
        <rect x="229" y="40" width="8" height="12" fill="#dc2626"/>
        <!-- Bullish -->
        <line x1="263" y1="28" x2="263" y2="50" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="259" y="32" width="8" height="14" fill="#16a34a"/>
        <!-- Bullish -->
        <line x1="293" y1="22" x2="293" y2="42" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="289" y="26" width="8" height="12" fill="#16a34a"/>
        <!-- Bullish (dernier, plus haut) -->
        <line x1="323" y1="18" x2="323" y2="40" stroke="#16a34a" stroke-width="1.2"/>
        <rect x="319" y="22" width="8" height="14" fill="#16a34a"/>
        <!-- Indicateur lumineux sur la dernière bougie -->
        <circle cx="323" cy="22" r="4" fill="#16a34a" opacity="0.4">
            <animate attributeName="r" values="4;9;4" dur="2s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite"/>
        </circle>
    </g>
    <!-- Moyenne mobile (courbe lissée) -->
    <path d="M 35 75 Q 80 68 113 60 T 173 50 T 233 42 T 293 32 T 360 22"
          fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="4 3" opacity="0.7"/>
    <!-- Axe Y labels -->
    <text x="22" y="33" text-anchor="end" font-size="7" fill="#94a3b8">100</text>
    <text x="22" y="63" text-anchor="end" font-size="7" fill="#94a3b8">80</text>
    <text x="22" y="93" text-anchor="end" font-size="7" fill="#94a3b8">60</text>
    '''
    return _wrap(inner, "#319795",
                 "linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)",
                 "Lire les données",
                 "Chandeliers · Volume · Moyennes mobiles")


def illu_modeles():
    """Distribution gaussienne + formules mathématiques."""
    inner = '''
    <defs>
        <linearGradient id="acad_g_gauss" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#7c3aed" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
        </linearGradient>
    </defs>
    <!-- Axe horizontal -->
    <line x1="40" y1="105" x2="360" y2="105" stroke="#94a3b8" stroke-width="1"/>
    <!-- Distribution normale -->
    <path d="M 40 105 Q 130 105 200 30 T 360 105 Z" fill="url(#acad_g_gauss)"/>
    <path d="M 40 105 Q 130 105 200 30 T 360 105"
          fill="none" stroke="#7c3aed" stroke-width="2.2" stroke-linecap="round"/>
    <!-- Lignes σ -->
    <g stroke="#a78bfa" stroke-width="1" stroke-dasharray="3 2">
        <line x1="150" y1="50" x2="150" y2="105"/>
        <line x1="250" y1="50" x2="250" y2="105"/>
        <line x1="120" y1="80" x2="120" y2="105"/>
        <line x1="280" y1="80" x2="280" y2="105"/>
    </g>
    <!-- Labels σ -->
    <g font-size="9" fill="#7c3aed" font-weight="700" font-family="Inter">
        <text x="200" y="120" text-anchor="middle">μ</text>
        <text x="150" y="120" text-anchor="middle">-σ</text>
        <text x="250" y="120" text-anchor="middle">+σ</text>
        <text x="120" y="120" text-anchor="middle">-2σ</text>
        <text x="280" y="120" text-anchor="middle">+2σ</text>
    </g>
    <!-- Pic central -->
    <circle cx="200" cy="30" r="4" fill="#7c3aed">
        <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/>
    </circle>
    <!-- Formules -->
    <g font-family="Georgia, serif" font-style="italic" fill="#475569">
        <text x="30" y="25" font-size="11">P(x) = </text>
        <text x="65" y="20" font-size="9">1</text>
        <line x1="58" y1="23" x2="78" y2="23" stroke="#475569" stroke-width="0.7"/>
        <text x="58" y="33" font-size="9">σ√2π</text>
        <text x="85" y="25" font-size="11">e</text>
        <text x="92" y="20" font-size="7">-(x-μ)²/2σ²</text>
    </g>
    <g font-family="Georgia, serif" font-style="italic" fill="#475569">
        <text x="305" y="55" font-size="11">σ = √Var</text>
        <text x="305" y="75" font-size="11">Sharpe = </text>
        <text x="345" y="70" font-size="8">μ-rf</text>
        <line x1="345" y1="72" x2="370" y2="72" stroke="#475569" stroke-width="0.7"/>
        <text x="350" y="83" font-size="8">σ</text>
    </g>
    '''
    return _wrap(inner, "#7c3aed",
                 "linear-gradient(135deg, #faf5ff 0%, #ede9fe 100%)",
                 "Modèles & mathématiques",
                 "Loi normale · Volatilité · Sharpe Ratio")


def illu_macro():
    """Inflation / Taux / Croissance : 3 courbes croisées."""
    inner = '''
    <!-- Grille discrète -->
    <g stroke="#fde68a" stroke-width="0.4" opacity="0.5">
        <line x1="30" y1="35" x2="370" y2="35"/>
        <line x1="30" y1="65" x2="370" y2="65"/>
        <line x1="30" y1="95" x2="370" y2="95"/>
    </g>
    <line x1="30" y1="115" x2="370" y2="115" stroke="#92400e" stroke-width="1"/>
    <!-- Inflation (rouge, descend puis remonte) -->
    <path d="M 30 90 Q 80 100 130 95 Q 180 75 230 55 Q 280 35 330 45 L 370 50"
          fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- Taux directeurs (bleu, monte progressivement) -->
    <path d="M 30 100 L 80 100 L 130 95 L 180 80 L 230 60 L 280 45 L 330 35 L 370 30"
          fill="none" stroke="#1e40af" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- PIB / Croissance (vert, légère ondulation) -->
    <path d="M 30 75 Q 100 70 170 65 T 310 60 T 370 75"
          fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
          stroke-dasharray="6 3"/>
    <!-- Points clignotants -->
    <circle cx="370" cy="50" r="3.5" fill="#dc2626">
        <animate attributeName="r" values="3.5;6;3.5" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="370" cy="30" r="3.5" fill="#1e40af">
        <animate attributeName="r" values="3.5;6;3.5" dur="1.8s" begin="0.6s" repeatCount="indefinite"/>
    </circle>
    <circle cx="370" cy="75" r="3.5" fill="#16a34a">
        <animate attributeName="r" values="3.5;6;3.5" dur="1.8s" begin="1.2s" repeatCount="indefinite"/>
    </circle>
    <!-- Légende -->
    <g font-size="8" font-family="Inter" font-weight="600">
        <rect x="40" y="20" width="10" height="2.5" fill="#dc2626"/>
        <text x="55" y="25" fill="#dc2626">Inflation</text>
        <rect x="110" y="20" width="10" height="2.5" fill="#1e40af"/>
        <text x="125" y="25" fill="#1e40af">Taux FED</text>
        <rect x="180" y="20" width="10" height="2.5" fill="#16a34a"/>
        <text x="195" y="25" fill="#16a34a">PIB</text>
    </g>
    <!-- Boussole économique -->
    <g transform="translate(330 95)">
        <circle r="14" fill="#fef3c7" stroke="#92400e" stroke-width="1.5"/>
        <text x="0" y="-7" text-anchor="middle" font-size="6" font-weight="700" fill="#92400e">N</text>
        <text x="7" y="2" text-anchor="middle" font-size="6" font-weight="700" fill="#92400e">E</text>
        <text x="0" y="11" text-anchor="middle" font-size="6" font-weight="700" fill="#92400e">S</text>
        <text x="-7" y="2" text-anchor="middle" font-size="6" font-weight="700" fill="#92400e">O</text>
        <polygon points="0,-9 -2,1 0,-1 2,1" fill="#dc2626">
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="6s" repeatCount="indefinite"/>
        </polygon>
    </g>
    '''
    return _wrap(inner, "#d97706",
                 "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
                 "Macro-économie",
                 "Inflation · Taux directeurs · Cycles")


def illu_cas_historiques():
    """Ligne de temps avec événements marquants."""
    inner = '''
    <!-- Ligne de temps principale -->
    <line x1="30" y1="70" x2="370" y2="70" stroke="#475569" stroke-width="2.5" stroke-linecap="round"/>
    <!-- Flèche au bout -->
    <polygon points="370,70 363,66 363,74" fill="#475569"/>
    <!-- Événements (avec hauteurs variées pour effet timeline) -->
    <!-- 1929 - Krach -->
    <g transform="translate(60 70)">
        <circle r="5" fill="#dc2626"/>
        <line x1="0" y1="0" x2="0" y2="-30" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="2 2"/>
        <rect x="-22" y="-50" width="44" height="20" rx="3" fill="#fee2e2" stroke="#dc2626" stroke-width="1"/>
        <text x="0" y="-37" text-anchor="middle" font-size="7" font-weight="700" fill="#991b1b">1929</text>
        <text x="0" y="-30" text-anchor="middle" font-size="6" fill="#7f1d1d">Krach</text>
        <text x="0" y="85" text-anchor="middle" font-size="6" fill="#64748b">Wall St.</text>
    </g>
    <!-- 1973 - Choc pétrolier -->
    <g transform="translate(130 70)">
        <circle r="5" fill="#92400e"/>
        <line x1="0" y1="0" x2="0" y2="25" stroke="#92400e" stroke-width="1.5" stroke-dasharray="2 2"/>
        <rect x="-25" y="25" width="50" height="20" rx="3" fill="#fed7aa" stroke="#92400e" stroke-width="1"/>
        <text x="0" y="38" text-anchor="middle" font-size="7" font-weight="700" fill="#7c2d12">1973</text>
        <text x="0" y="45" text-anchor="middle" font-size="6" fill="#7c2d12">Pétrole</text>
    </g>
    <!-- 1987 -->
    <g transform="translate(180 70)">
        <circle r="5" fill="#dc2626"/>
        <line x1="0" y1="0" x2="0" y2="-25" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="2 2"/>
        <rect x="-22" y="-45" width="44" height="20" rx="3" fill="#fee2e2" stroke="#dc2626" stroke-width="1"/>
        <text x="0" y="-32" text-anchor="middle" font-size="7" font-weight="700" fill="#991b1b">1987</text>
        <text x="0" y="-25" text-anchor="middle" font-size="6" fill="#7f1d1d">Lundi noir</text>
    </g>
    <!-- 2000 - Dot-com -->
    <g transform="translate(230 70)">
        <circle r="5" fill="#7c3aed"/>
        <line x1="0" y1="0" x2="0" y2="20" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="2 2"/>
        <rect x="-22" y="20" width="44" height="20" rx="3" fill="#ede9fe" stroke="#7c3aed" stroke-width="1"/>
        <text x="0" y="33" text-anchor="middle" font-size="7" font-weight="700" fill="#5b21b6">2000</text>
        <text x="0" y="40" text-anchor="middle" font-size="6" fill="#5b21b6">Dot-com</text>
    </g>
    <!-- 2008 - Subprimes -->
    <g transform="translate(280 70)">
        <circle r="6" fill="#dc2626">
            <animate attributeName="r" values="6;8;6" dur="2s" repeatCount="indefinite"/>
        </circle>
        <line x1="0" y1="0" x2="0" y2="-28" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="2 2"/>
        <rect x="-25" y="-48" width="50" height="20" rx="3" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
        <text x="0" y="-35" text-anchor="middle" font-size="7" font-weight="700" fill="#991b1b">2008</text>
        <text x="0" y="-28" text-anchor="middle" font-size="6" fill="#7f1d1d">Subprimes</text>
    </g>
    <!-- 2020 - COVID -->
    <g transform="translate(335 70)">
        <circle r="6" fill="#0891b2">
            <animate attributeName="r" values="6;8;6" dur="2s" begin="0.5s" repeatCount="indefinite"/>
        </circle>
        <line x1="0" y1="0" x2="0" y2="22" stroke="#0891b2" stroke-width="1.5" stroke-dasharray="2 2"/>
        <rect x="-22" y="22" width="44" height="20" rx="3" fill="#cffafe" stroke="#0891b2" stroke-width="1.5"/>
        <text x="0" y="35" text-anchor="middle" font-size="7" font-weight="700" fill="#155e75">2020</text>
        <text x="0" y="42" text-anchor="middle" font-size="6" fill="#155e75">COVID</text>
    </g>
    <!-- Titre -->
    <text x="30" y="20" font-size="11" font-weight="700" fill="#1e293b" font-family="Inter">100 ans de crises</text>
    '''
    return _wrap(inner, "#475569",
                 "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
                 "Cas historiques",
                 "1929 · 1987 · 2008 · 2020 — les leçons des crises")


def illu_strategies():
    """Balance entre risque et rendement, plusieurs stratégies."""
    inner = '''
    <defs>
        <linearGradient id="acad_g_scale" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#16a34a"/>
            <stop offset="100%" stop-color="#dc2626"/>
        </linearGradient>
    </defs>
    <!-- Axe risque-rendement -->
    <line x1="30" y1="100" x2="370" y2="100" stroke="#94a3b8" stroke-width="1.5"/>
    <line x1="30" y1="30" x2="30" y2="100" stroke="#94a3b8" stroke-width="1.5"/>
    <polygon points="370,100 363,96 363,104" fill="#94a3b8"/>
    <polygon points="30,30 26,37 34,37" fill="#94a3b8"/>
    <text x="375" y="103" font-size="8" fill="#64748b" font-weight="600">Risque →</text>
    <text x="35" y="22" font-size="8" fill="#64748b" font-weight="600">Rendement ↑</text>
    <!-- Frontière efficiente (courbe) -->
    <path d="M 50 95 Q 90 75 140 60 Q 200 45 280 35 Q 330 28 360 25"
          fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 3" opacity="0.7"/>
    <!-- Stratégies points -->
    <!-- Prudent -->
    <g>
        <circle cx="70" cy="88" r="9" fill="#16a34a" opacity="0.25"/>
        <circle cx="70" cy="88" r="5" fill="#16a34a"/>
        <text x="70" y="78" text-anchor="middle" font-size="8" font-weight="700" fill="#15803d">Prudent</text>
    </g>
    <!-- Équilibré -->
    <g>
        <circle cx="170" cy="65" r="10" fill="#d97706" opacity="0.25"/>
        <circle cx="170" cy="65" r="5.5" fill="#d97706"/>
        <text x="170" y="55" text-anchor="middle" font-size="8" font-weight="700" fill="#92400e">Équilibré</text>
    </g>
    <!-- Agressif -->
    <g>
        <circle cx="300" cy="38" r="11" fill="#dc2626" opacity="0.25">
            <animate attributeName="r" values="11;15;11" dur="2.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="300" cy="38" r="6" fill="#dc2626"/>
        <text x="300" y="27" text-anchor="middle" font-size="8" font-weight="700" fill="#991b1b">Agressif</text>
    </g>
    <!-- Flèche du portefeuille optimal -->
    <g transform="translate(220 50)">
        <text x="0" y="0" font-size="8" fill="#5b21b6" font-weight="600">Frontière efficiente</text>
        <path d="M 0 5 L -10 18" stroke="#5b21b6" stroke-width="1.2" fill="none" stroke-linecap="round"/>
        <polygon points="-10,18 -7,14 -13,14" fill="#5b21b6"/>
    </g>
    '''
    return _wrap(inner, "#7c3aed",
                 "linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)",
                 "Stratégies d'investissement",
                 "Frontière efficiente · Profil de risque")


def illu_construction():
    """Camembert + blocs représentant la diversification."""
    inner = '''
    <!-- Camembert central -->
    <g transform="translate(100 70)">
        <!-- Slices (5 actifs) -->
        <path d="M 0 0 L 0 -45 A 45 45 0 0 1 38.97 22.5 Z" fill="#3b82f6"/>
        <path d="M 0 0 L 38.97 22.5 A 45 45 0 0 1 -22.5 38.97 Z" fill="#10b981"/>
        <path d="M 0 0 L -22.5 38.97 A 45 45 0 0 1 -42.79 -13.91 Z" fill="#f59e0b"/>
        <path d="M 0 0 L -42.79 -13.91 A 45 45 0 0 1 -19.47 -40.55 Z" fill="#8b5cf6"/>
        <path d="M 0 0 L -19.47 -40.55 A 45 45 0 0 1 0 -45 Z" fill="#ec4899"/>
        <!-- Hole -->
        <circle r="22" fill="white"/>
        <text x="0" y="3" text-anchor="middle" font-size="11" font-weight="800" fill="#1e293b">100%</text>
        <!-- Rotation animée -->
        <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="40s" repeatCount="indefinite" additive="sum"/>
    </g>
    <!-- Légende avec barres horizontales -->
    <g font-family="Inter" font-size="8" font-weight="600">
        <rect x="200" y="30" width="14" height="6" fill="#3b82f6" rx="1"/>
        <text x="220" y="36" fill="#1e293b">Actions</text>
        <rect x="262" y="32" width="35" height="3" fill="#3b82f6" rx="1" opacity="0.4"/>
        <text x="305" y="36" fill="#64748b" font-size="7">40%</text>

        <rect x="200" y="48" width="14" height="6" fill="#10b981" rx="1"/>
        <text x="220" y="54" fill="#1e293b">Obligations</text>
        <rect x="265" y="50" width="22" height="3" fill="#10b981" rx="1" opacity="0.4"/>
        <text x="295" y="54" fill="#64748b" font-size="7">25%</text>

        <rect x="200" y="66" width="14" height="6" fill="#f59e0b" rx="1"/>
        <text x="220" y="72" fill="#1e293b">Or</text>
        <rect x="240" y="68" width="13" height="3" fill="#f59e0b" rx="1" opacity="0.4"/>
        <text x="260" y="72" fill="#64748b" font-size="7">15%</text>

        <rect x="200" y="84" width="14" height="6" fill="#8b5cf6" rx="1"/>
        <text x="220" y="90" fill="#1e293b">Crypto</text>
        <rect x="252" y="86" width="9" height="3" fill="#8b5cf6" rx="1" opacity="0.4"/>
        <text x="268" y="90" fill="#64748b" font-size="7">10%</text>

        <rect x="200" y="102" width="14" height="6" fill="#ec4899" rx="1"/>
        <text x="220" y="108" fill="#1e293b">Cash</text>
        <rect x="248" y="104" width="9" height="3" fill="#ec4899" rx="1" opacity="0.4"/>
        <text x="264" y="108" fill="#64748b" font-size="7">10%</text>
    </g>
    '''
    return _wrap(inner, "#3b82f6",
                 "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
                 "Construction de portefeuille",
                 "Diversification · Pondération · Rééquilibrage")


def illu_biais():
    """Cerveau stylisé avec ondes émotionnelles."""
    inner = '''
    <defs>
        <radialGradient id="acad_g_brain">
            <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
        </radialGradient>
    </defs>
    <!-- Aura -->
    <circle cx="200" cy="70" r="55" fill="url(#acad_g_brain)">
        <animate attributeName="r" values="50;65;50" dur="3s" repeatCount="indefinite"/>
    </circle>
    <!-- Cerveau (forme stylisée 2 lobes) -->
    <g transform="translate(200 70)">
        <!-- Lobe gauche -->
        <path d="M -2 -28 Q -32 -28 -32 -8 Q -38 0 -32 8 Q -32 28 -2 28 L -2 -28 Z"
              fill="#fcd34d" stroke="#d97706" stroke-width="1.5"/>
        <!-- Lobe droit -->
        <path d="M 2 -28 Q 32 -28 32 -8 Q 38 0 32 8 Q 32 28 2 28 L 2 -28 Z"
              fill="#fcd34d" stroke="#d97706" stroke-width="1.5"/>
        <!-- Sillons (gauche) -->
        <path d="M -25 -15 Q -18 -10 -25 -5" fill="none" stroke="#d97706" stroke-width="1" opacity="0.6"/>
        <path d="M -25 5 Q -18 10 -25 15" fill="none" stroke="#d97706" stroke-width="1" opacity="0.6"/>
        <!-- Sillons (droite) -->
        <path d="M 25 -15 Q 18 -10 25 -5" fill="none" stroke="#d97706" stroke-width="1" opacity="0.6"/>
        <path d="M 25 5 Q 18 10 25 15" fill="none" stroke="#d97706" stroke-width="1" opacity="0.6"/>
    </g>
    <!-- Bulles d'émotions / biais -->
    <g>
        <!-- Peur -->
        <circle cx="80" cy="40" r="18" fill="#dc2626" opacity="0.2"/>
        <text x="80" y="44" text-anchor="middle" font-size="9" font-weight="700" fill="#991b1b">PEUR</text>

        <!-- Cupidité -->
        <circle cx="320" cy="40" r="22" fill="#16a34a" opacity="0.2"/>
        <text x="320" y="44" text-anchor="middle" font-size="9" font-weight="700" fill="#15803d">CUPIDITÉ</text>

        <!-- FOMO -->
        <circle cx="60" cy="100" r="16" fill="#7c3aed" opacity="0.2"/>
        <text x="60" y="104" text-anchor="middle" font-size="9" font-weight="700" fill="#5b21b6">FOMO</text>

        <!-- Ancrage -->
        <circle cx="340" cy="100" r="18" fill="#0891b2" opacity="0.2"/>
        <text x="340" y="104" text-anchor="middle" font-size="9" font-weight="700" fill="#155e75">ANCRAGE</text>
    </g>
    <!-- Connexions cerveau ↔ biais -->
    <g stroke="#d97706" stroke-width="1" stroke-dasharray="2 3" opacity="0.5">
        <line x1="170" y1="55" x2="98" y2="48"/>
        <line x1="230" y1="55" x2="298" y2="48"/>
        <line x1="170" y1="85" x2="76" y2="98"/>
        <line x1="230" y1="85" x2="322" y2="98"/>
    </g>
    <!-- Étincelles -->
    <g fill="#fbbf24">
        <circle cx="170" cy="50" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.5s" repeatCount="indefinite"/></circle>
        <circle cx="230" cy="60" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.3s" repeatCount="indefinite"/></circle>
        <circle cx="180" cy="90" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.6s" repeatCount="indefinite"/></circle>
        <circle cx="220" cy="80" r="1.5"><animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="0.9s" repeatCount="indefinite"/></circle>
    </g>
    '''
    return _wrap(inner, "#d97706",
                 "linear-gradient(135deg, #fffbeb 0%, #fed7aa 100%)",
                 "Biais comportementaux",
                 "Peur · Cupidité · FOMO · Ancrage")


def illu_lexique():
    """Livre ouvert avec termes financiers."""
    inner = '''
    <!-- Livre ouvert (perspective) -->
    <g transform="translate(200 70)">
        <!-- Pli central -->
        <path d="M 0 -35 L 0 35" stroke="#1e293b" stroke-width="2"/>
        <!-- Page gauche -->
        <path d="M 0 -35 L -80 -30 L -85 30 L 0 35 Z" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
        <!-- Page droite -->
        <path d="M 0 -35 L 80 -30 L 85 30 L 0 35 Z" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
        <!-- Ombre intérieure -->
        <path d="M 0 -33 L -78 -28 L -78 -25 L 0 -30 Z" fill="#e2e8f0" opacity="0.6"/>
        <path d="M 0 -33 L 78 -28 L 78 -25 L 0 -30 Z" fill="#e2e8f0" opacity="0.6"/>
        <!-- Texte page gauche -->
        <g font-family="Inter" fill="#1e293b">
            <text x="-70" y="-18" font-size="6" font-weight="700">Alpha</text>
            <line x1="-70" y1="-15" x2="-15" y2="-15" stroke="#cbd5e1" stroke-width="0.7"/>
            <line x1="-70" y1="-10" x2="-10" y2="-10" stroke="#cbd5e1" stroke-width="0.5"/>

            <text x="-70" y="0" font-size="6" font-weight="700">Beta</text>
            <line x1="-70" y1="3" x2="-15" y2="3" stroke="#cbd5e1" stroke-width="0.7"/>
            <line x1="-70" y1="8" x2="-10" y2="8" stroke="#cbd5e1" stroke-width="0.5"/>

            <text x="-70" y="18" font-size="6" font-weight="700">Drawdown</text>
            <line x1="-70" y1="21" x2="-15" y2="21" stroke="#cbd5e1" stroke-width="0.7"/>
        </g>
        <!-- Texte page droite -->
        <g font-family="Inter" fill="#1e293b">
            <text x="10" y="-18" font-size="6" font-weight="700">Sharpe</text>
            <line x1="10" y1="-15" x2="65" y2="-15" stroke="#cbd5e1" stroke-width="0.7"/>
            <line x1="10" y1="-10" x2="70" y2="-10" stroke="#cbd5e1" stroke-width="0.5"/>

            <text x="10" y="0" font-size="6" font-weight="700">VaR 95%</text>
            <line x1="10" y1="3" x2="65" y2="3" stroke="#cbd5e1" stroke-width="0.7"/>
            <line x1="10" y1="8" x2="70" y2="8" stroke="#cbd5e1" stroke-width="0.5"/>

            <text x="10" y="18" font-size="6" font-weight="700">Volatilité</text>
            <line x1="10" y1="21" x2="65" y2="21" stroke="#cbd5e1" stroke-width="0.7"/>
        </g>
    </g>
    <!-- Loupe au-dessus -->
    <g transform="translate(95 35) rotate(-15)">
        <circle cx="0" cy="0" r="14" fill="none" stroke="#0891b2" stroke-width="2.5"/>
        <circle cx="0" cy="0" r="11" fill="#cffafe" opacity="0.4"/>
        <line x1="10" y1="10" x2="22" y2="22" stroke="#0891b2" stroke-width="3" stroke-linecap="round"/>
        <text x="0" y="3" text-anchor="middle" font-size="9" font-weight="700" fill="#155e75">α β</text>
    </g>
    <!-- Marque-page -->
    <path d="M 285 35 L 285 100 L 295 92 L 305 100 L 305 35 Z" fill="#dc2626"/>
    '''
    return _wrap(inner, "#0891b2",
                 "linear-gradient(135deg, #ecfeff 0%, #cffafe 100%)",
                 "Lexique",
                 "Alpha · Beta · Sharpe · VaR · et plus")


def illu_methodologie():
    """Engrenages connectés + flux de données."""
    inner = '''
    <!-- Flux de données -->
    <defs>
        <linearGradient id="acad_g_flow" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
        </linearGradient>
    </defs>
    <!-- Sources de données (gauche) -->
    <g transform="translate(40 50)">
        <rect x="-15" y="-12" width="30" height="24" rx="3" fill="#1e293b"/>
        <text x="0" y="3" text-anchor="middle" font-size="7" font-weight="700" fill="#fbbf24">YAHOO</text>
        <text x="0" y="20" text-anchor="middle" font-size="6" font-weight="600" fill="#475569">Prix marché</text>
    </g>
    <g transform="translate(40 100)">
        <rect x="-15" y="-12" width="30" height="24" rx="3" fill="#1e293b"/>
        <text x="0" y="3" text-anchor="middle" font-size="7" font-weight="700" fill="#fbbf24">IA</text>
        <text x="0" y="20" text-anchor="middle" font-size="6" font-weight="600" fill="#475569">Calibration</text>
    </g>
    <!-- Connexions -->
    <path d="M 65 50 Q 110 50 130 70" fill="none" stroke="url(#acad_g_flow)" stroke-width="3">
        <animate attributeName="stroke-dashoffset" from="0" to="-20" dur="1.5s" repeatCount="indefinite"/>
    </path>
    <path d="M 65 100 Q 110 100 130 80" fill="none" stroke="url(#acad_g_flow)" stroke-width="3"/>
    <!-- Engrenage central -->
    <g transform="translate(180 75)">
        <circle r="25" fill="#7c3aed" opacity="0.15"/>
        <g class="qt-acad-gear">
            <circle r="20" fill="#7c3aed"/>
            <!-- Dents -->
            <g fill="#7c3aed">
                <rect x="-3" y="-25" width="6" height="6"/>
                <rect x="-3" y="19" width="6" height="6"/>
                <rect x="-25" y="-3" width="6" height="6"/>
                <rect x="19" y="-3" width="6" height="6"/>
                <rect x="-3" y="-25" width="6" height="6" transform="rotate(45)"/>
                <rect x="-3" y="19" width="6" height="6" transform="rotate(45)"/>
                <rect x="-25" y="-3" width="6" height="6" transform="rotate(45)"/>
                <rect x="19" y="-3" width="6" height="6" transform="rotate(45)"/>
            </g>
            <circle r="8" fill="#f3e8ff"/>
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="8s" repeatCount="indefinite"/>
        </g>
    </g>
    <!-- Engrenage secondaire (rotation inverse) -->
    <g transform="translate(240 50)">
        <g class="qt-acad-gear-rev">
            <circle r="14" fill="#0891b2"/>
            <g fill="#0891b2">
                <rect x="-2" y="-18" width="4" height="5"/>
                <rect x="-2" y="13" width="4" height="5"/>
                <rect x="-18" y="-2" width="5" height="4"/>
                <rect x="13" y="-2" width="5" height="4"/>
            </g>
            <circle r="5" fill="#cffafe"/>
            <animateTransform attributeName="transform" type="rotate" from="0" to="-360" dur="6s" repeatCount="indefinite"/>
        </g>
    </g>
    <!-- Sortie : graphique stylisé -->
    <g transform="translate(310 75)">
        <rect x="-22" y="-25" width="60" height="50" rx="3" fill="#f1f5f9" stroke="#475569" stroke-width="1"/>
        <polyline points="-15,15 -5,5 5,8 15,-3 25,-10 33,-15"
                  fill="none" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round"/>
        <circle cx="33" cy="-15" r="2.5" fill="#16a34a">
            <animate attributeName="r" values="2.5;4;2.5" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <text x="8" y="20" text-anchor="middle" font-size="6" fill="#475569" font-weight="600">Résultat</text>
    </g>
    <!-- Flèches finales -->
    <path d="M 215 60 Q 250 60 280 65" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="4 2"/>
    '''
    return _wrap(inner, "#7c3aed",
                 "linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)",
                 "Méthodologie",
                 "Yahoo + IA → Simulation → Résultats")


# Mapping section → fonction
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
