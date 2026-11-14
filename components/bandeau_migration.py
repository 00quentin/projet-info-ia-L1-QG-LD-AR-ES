"""
components/bandeau_migration.py
===============================
Bandeau invitant a passer au nouveau site. Fermable pour la session seulement.
"""

import streamlit as st

from config import URL_NOUVEAU_SITE

CLE_BANDEAU_FERME = "bandeau_migration_ferme"


def render_bandeau_migration():
    """Affiche le bandeau de migration, sauf si l'utilisateur l'a ferme cette session."""
    if st.session_state.get(CLE_BANDEAU_FERME, False):
        return
    st.info(
        "Quant Terminal passe au nouveau site : "
        f"[ouvrir le nouveau site]({URL_NOUVEAU_SITE}). "
        "Cette version Streamlit reste disponible pour le moment."
    )
    if st.button("Masquer ce message pour cette session", key="bouton_fermer_bandeau_migration"):
        st.session_state[CLE_BANDEAU_FERME] = True
        st.rerun()
