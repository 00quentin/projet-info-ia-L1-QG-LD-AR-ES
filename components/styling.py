"""
components/styling.py
=====================
Chargement du CSS et gestion des variables de thème (clair/sombre).
"""

import streamlit as st


_DESIGN_TOKENS = """
<style>
:root {
    /* === SPACING SCALE (4px base) === */
    --space-1: 4px;   --space-2: 8px;   --space-3: 12px;  --space-4: 16px;
    --space-5: 20px;  --space-6: 24px;  --space-8: 32px;  --space-10: 40px;
    --space-12: 48px; --space-16: 64px;

    /* === RADIUS SCALE — descendus pour un look pro (vs marketing) === */
    --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px; --radius-xl: 12px;
    --radius-full: 9999px;

    /* === SHADOW SCALE — ultra discretes type Linear/Vercel === */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
    --shadow-lg: 0 4px 12px rgba(0,0,0,0.06);
    --shadow-xl: 0 8px 24px rgba(0,0,0,0.08);
    --shadow-glow: 0 0 0 3px rgba(99,102,241,0.12);

    /* === TYPOGRAPHIE === */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Consolas', 'Menlo', monospace;

    /* === TIMING === */
    --ease-out: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
    --duration-fast: 120ms;
    --duration-base: 180ms;
    --duration-slow: 280ms;

    /* === SLATE SCALE (neutres dominants — inspiration Linear/Vercel) === */
    --slate-50: #fafafa;  --slate-100: #f4f4f5; --slate-200: #e4e4e7;
    --slate-300: #d4d4d8; --slate-400: #a1a1aa; --slate-500: #71717a;
    --slate-600: #52525b; --slate-700: #3f3f46; --slate-800: #27272a;
    --slate-900: #18181b; --slate-950: #09090b;

    /* === INDIGO SCALE (accent unique, sobre type Linear) === */
    --indigo-50: #eef2ff;  --indigo-100: #e0e7ff; --indigo-200: #c7d2fe;
    --indigo-300: #a5b4fc; --indigo-400: #818cf8; --indigo-500: #6366f1;
    --indigo-600: #4f46e5; --indigo-700: #4338ca; --indigo-800: #3730a3;

    /* === Aliases retro-compatibles (anciennes vars utilisees dans style.css) === */
    --blue-50: var(--indigo-50);   --blue-100: var(--indigo-100);
    --blue-200: var(--indigo-200); --blue-300: var(--indigo-300);
    --blue-400: var(--indigo-400); --blue-500: var(--indigo-500);
    --blue-600: var(--indigo-600); --blue-700: var(--indigo-700);
    --blue-800: var(--indigo-800); --blue-900: var(--slate-900);
    --teal-50: var(--indigo-50);   --teal-100: var(--indigo-100);
    --teal-200: var(--indigo-200); --teal-300: var(--indigo-300);
    --teal-400: var(--indigo-400); --teal-500: var(--indigo-500);
    --teal-600: var(--indigo-600); --teal-700: var(--indigo-700);
    --gray-50: var(--slate-50);    --gray-100: var(--slate-100);
    --gray-200: var(--slate-200);  --gray-300: var(--slate-300);
    --gray-400: var(--slate-400);  --gray-500: var(--slate-500);
    --gray-600: var(--slate-600);  --gray-700: var(--slate-700);
    --gray-800: var(--slate-800);  --gray-900: var(--slate-900);

    /* === SEMANTIC — couleurs TradingView (vert/rouge vifs et lisibles) === */
    --success-50: #ecfdf5; --success-500: #16c784; --success-700: #15803d;
    --danger-50:  #fef2f2; --danger-500:  #ef454a; --danger-700:  #b91c1c;
    --warn-50:    #fffbeb; --warn-500:    #d97706; --warn-700:    #b45309;
}
</style>
"""

CSS_VARS_CLAIR = """
<style>
:root {
    /* Identite : slate dominant, indigo en accent unique */
    --primary:       var(--slate-900);          /* titres, headers */
    --secondary:     var(--slate-700);
    --accent:        var(--indigo-600);         /* unique accent (boutons primary, focus) */
    --accent-soft:   var(--indigo-100);
    --bg:            var(--slate-50);
    --bg-2:          #ffffff;
    --card:          #ffffff;
    --border:        var(--slate-200);
    --border-strong: var(--slate-300);
    --text:          var(--slate-800);
    --text-muted:    var(--slate-600);
    --muted:         var(--slate-500);
    --success:       #16c784;                    /* vert TradingView */
    --danger:        #ef454a;                    /* rouge TradingView */
    --warn:          var(--warn-500);
    /* Ombres et hovers contextuels (changent en dark) */
    --shadow-rgb:    15,23,42;                   /* slate-900 a faible opacite */
    --hover-tint:    rgba(99,102,241,0.06);
    --focus-ring:    rgba(99,102,241,0.4);
}
</style>
"""

CSS_VARS_SOMBRE = """
<style>
:root {
    /* Identite sombre : noir presque pur (style Linear/Vercel dark) */
    --primary:       var(--slate-50);            /* titres clairs sur fond sombre */
    --secondary:     var(--slate-200);
    --accent:        var(--indigo-400);          /* indigo plus clair pour le contraste dark */
    --accent-soft:   var(--indigo-800);
    --bg:            #0b0e11;                    /* fond TradingView dark */
    --bg-2:          #131722;                    /* card background dark TradingView */
    --card:          #1e222d;                    /* secondary cards */
    --border:        #2a2e39;
    --border-strong: #363a45;
    --text:          #d1d4dc;                    /* texte principal TradingView */
    --text-muted:    #868993;
    --muted:         #5d606b;
    --success:       #26a69a;                    /* vert TradingView dark — meilleur sur fond noir */
    --danger:        #ef5350;                    /* rouge TradingView dark */
    --warn:          #fbbf24;
    /* Ombres : en dark on assombrit avec du noir profond */
    --shadow-rgb:    0,0,0;
    --hover-tint:    rgba(129,140,248,0.10);
    --focus-ring:    rgba(129,140,248,0.5);
}
</style>
"""


def appliquer_styles():
    """
    Charge les design tokens, les variables sémantiques (clair/sombre) et le CSS externe.
    Doit être appelé tout de suite après st.set_page_config.
    """
    # Tokens d'abord (échelles brutes), puis variables sémantiques qui les référencent
    st.markdown(_DESIGN_TOKENS, unsafe_allow_html=True)
    css_vars = CSS_VARS_SOMBRE if st.session_state.get("dark_mode", False) else CSS_VARS_CLAIR
    st.markdown(css_vars, unsafe_allow_html=True)

    try:
        with open("style.css", "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(
            "<style>\n" + css_content + "\n</style>"
            "\n<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">"
            "\n<link href=\"https://fonts.googleapis.com/icon?family=Material+Icons\" rel=\"stylesheet\">"
            "\n<link href=\"https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block\" rel=\"stylesheet\">"
            # Skip link : invisible jusqu'au focus clavier (Tab dès le chargement)
            "\n<a href='#main-content' class='qt-skip-link'>Aller au contenu principal</a>"
            "\n<span id='main-content' class='sr-only' tabindex='-1'>Contenu principal</span>",
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("Fichier style.css introuvable - le design ne s'appliquera pas correctement.")