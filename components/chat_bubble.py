"""
components/chat_bubble.py
=========================
Bulle de chat flottante (style Intercom) — remplace l'onglet Analyste IA.
La bulle est fixée en bas à droite de l'écran, toujours visible.
"""

import streamlit as st
from ia_bot import discuter_avec_ia


def render_chat_bubble():
    """Affiche la bulle chat flottante + le panneau chat quand ouvert."""

    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False

    # --- Tooltip d'invitation (avant 1er clic) ---
    tooltip_html = ""
    if not st.session_state.show_chat and not st.session_state.messages_chat:
        tooltip_html = (
            '<div class="qt-chat-bubble-tooltip">'
            '<strong>Analyste IA</strong>'
            'Posez vos questions sur votre simulation, les marchés ou la macro-économie.'
            '</div>'
        )

    # --- Bulle bouton ---
    st.markdown('<div class="qt-chat-bubble-wrapper">', unsafe_allow_html=True)
    if tooltip_html:
        st.markdown(tooltip_html, unsafe_allow_html=True)
    icon = "✕" if st.session_state.show_chat else "💬"
    if st.button(icon, key="qt_chat_bubble_btn"):
        st.session_state.show_chat = not st.session_state.show_chat
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Panneau chat ---
    if st.session_state.show_chat:
        st.markdown(
            '<div class="qt-chat-panel">'
            '<div class="qt-chat-panel-header">'
            '<span style="font-size:1.4em;">🤖</span>'
            '<div>'
            '<div class="qt-chat-panel-title">Analyste IA</div>'
            '<div class="qt-chat-panel-sub">Analyste financier · répond en temps réel</div>'
            '</div>'
            '</div>'
            '<div class="qt-chat-panel-body">',
            unsafe_allow_html=True,
        )

        for message in st.session_state.messages_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input(
            "Posez votre question (ex : Pourquoi l'Or monte en crise ?)",
            key="qt_chat_input_bubble",
        )
        if question:
            st.chat_message("user").markdown(question)
            st.session_state.messages_chat.append({"role": "user", "content": question})
            with st.chat_message("assistant"):
                with st.spinner("L'analyste rédige…"):
                    reponse = discuter_avec_ia(st.session_state.messages_chat)
                    st.markdown(reponse)
            st.session_state.messages_chat.append({"role": "assistant", "content": reponse})

        st.markdown('</div></div>', unsafe_allow_html=True)
