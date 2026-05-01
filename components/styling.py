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

    /* === RADIUS SCALE === */
    --radius-sm: 6px; --radius-md: 10px; --radius-lg: 14px; --radius-xl: 20px;
    --radius-full: 9999px;

    /* === SHADOW SCALE === */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 2px 8px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.10);
    --shadow-xl: 0 16px 40px rgba(0,0,0,0.14);
    --shadow-glow: 0 0 0 3px rgba(49,151,149,0.18);

    /* === TYPOGRAPHIE === */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Consolas', 'Menlo', monospace;

    /* === TIMING === */
    --ease-out: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
    --duration-fast: 150ms;
    --duration-base: 250ms;
    --duration-slow: 400ms;

    /* === BLUE SCALE 50-900 === */
    --blue-50: #ebf8ff;  --blue-100: #bee3f8; --blue-200: #90cdf4;
    --blue-300: #63b3ed; --blue-400: #4299e1; --blue-500: #3182ce;
    --blue-600: #2c5282; --blue-700: #1a365d; --blue-800: #0f1f3d;
    --blue-900: #0a1628;

    /* === TEAL SCALE === */
    --teal-50: #e6fffa;  --teal-100: #b2f5ea; --teal-200: #81e6d9;
    --teal-300: #4fd1c5; --teal-400: #38b2ac; --teal-500: #319795;
    --teal-600: #2c7a7b; --teal-700: #285e61;

    /* === GRAY SCALE === */
    --gray-50: #f7fafc;  --gray-100: #edf2f7; --gray-200: #e2e8f0;
    --gray-300: #cbd5e0; --gray-400: #a0aec0; --gray-500: #718096;
    --gray-600: #4a5568; --gray-700: #2d3748; --gray-800: #1a202c;
    --gray-900: #171923;

    /* === SEMANTIC === */
    --success-50: #f0fff4; --success-500: #2f855a; --success-700: #22543d;
    --danger-50:  #fff5f5; --danger-500:  #c53030; --danger-700:  #742a2a;
    --warn-50:    #fffaf0; --warn-500:    #d69e2e; --warn-700:    #744210;
}
</style>
"""

CSS_VARS_CLAIR = """
<style>
:root {
    --primary:       var(--blue-700);
    --secondary:     var(--blue-600);
    --accent:        var(--teal-500);
    --accent-soft:   var(--teal-100);
    --bg:            var(--gray-50);
    --bg-2:          #ffffff;
    --card:          #ffffff;
    --border:        var(--gray-300);
    --border-strong: var(--gray-400);
    --text:          var(--gray-700);
    --text-muted:    var(--gray-600);
    --muted:         var(--gray-500);
    --success:       var(--success-500);
    --danger:        var(--danger-500);
    --warn:          var(--warn-500);
}
</style>
"""

CSS_VARS_SOMBRE = """
<style>
:root {
    --primary:       var(--blue-300);
    --secondary:     var(--blue-400);
    --accent:        var(--teal-300);
    --accent-soft:   var(--teal-700);
    --bg:            var(--gray-800);
    --bg-2:          var(--gray-700);
    --card:          var(--gray-700);
    --border:        var(--gray-600);
    --border-strong: var(--gray-500);
    --text:          var(--gray-200);
    --text-muted:    var(--gray-300);
    --muted:         var(--gray-400);
    --success:       #48bb78;
    --danger:        #fc8181;
    --warn:          #f6ad55;
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
            "\n<link href=\"https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block\" rel=\"stylesheet\">",
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("Fichier style.css introuvable - le design ne s'appliquera pas correctement.")