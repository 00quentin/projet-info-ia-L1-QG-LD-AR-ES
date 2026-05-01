"""
components/styling.py
=====================
Chargement du CSS et gestion des variables de thème (clair/sombre).
"""

import streamlit as st


CSS_VARS_CLAIR = """
<style>
:root {
    --primary:   #1a365d;
    --secondary: #2c5282;
    --accent:    #319795;
    --bg:        #f7fafc;
    --bg-2:      #ffffff;
    --card:      #ffffff;
    --border:    #cbd5e0;
    --border-strong: #a0aec0;
    --text:      #2d3748;
    --text-muted:#4a5568;
    --muted:     #718096;
    --success:   #2f855a;
    --danger:    #c53030;
}
</style>
"""

CSS_VARS_SOMBRE = """
<style>
:root {
    --primary:   #63b3ed;
    --secondary: #4299e1;
    --accent:    #4fd1c5;
    --bg:        #1a202c;
    --bg-2:      #2d3748;
    --card:      #2d3748;
    --border:    #4a5568;
    --border-strong: #718096;
    --text:      #e2e8f0;
    --text-muted:#cbd5e0;
    --muted:     #a0aec0;
    --success:   #48bb78;
    --danger:    #fc8181;
}
</style>
"""


def appliquer_styles():
    """
    Charge les variables CSS et le fichier style.css externe.
    Doit être appelé tout de suite après st.set_page_config.
    """
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