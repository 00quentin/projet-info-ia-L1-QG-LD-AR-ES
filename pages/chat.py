"""
pages/chat.py
=============
Onglet Analyste IA : chat conversationnel avec un analyste senior.
"""

import streamlit as st
from ia_bot import discuter_avec_ia


def render_page_chat():
    """Affiche le chat avec l'analyste IA."""
    st.markdown('<div class="qt-section-title">Bureau de votre analyste financier IA</div>',
                unsafe_allow_html=True)
    st.caption("Posez vos questions sur le marché, la macro-économie, ou l'impact de votre scénario.")
    st.markdown('<div class="qt-callout">💬 <strong>Tapez votre question dans la barre en bas de cette page</strong> '
                '— l\'analyste IA vous répondra avec un vocabulaire professionnel et pédagogue.</div>',
                unsafe_allow_html=True)

    for message in st.session_state.messages_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("✍️ Tapez votre question ici (ex : Pourquoi l'Or a-t-il monté pendant la crise de 2008 ?)")
    if question:
        st.chat_message("user").markdown(question)
        st.session_state.messages_chat.append({"role": "user", "content": question})
        with st.chat_message("assistant"):
            with st.spinner("L'analyste rédige son rapport..."):
                reponse_ia = discuter_avec_ia(st.session_state.messages_chat)
                st.markdown(reponse_ia)
        st.session_state.messages_chat.append({"role": "assistant", "content": reponse_ia})