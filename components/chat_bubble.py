"""
components/chat_bubble.py
=========================
Bulle de chat flottante fixée en bas à droite, toujours visible.

Streamlit bloque position:fixed via overflow:hidden sur ses conteneurs.
Solution : on injecte le bouton directement dans window.parent.document
via components.html(), et on le fait cliquer un bouton Streamlit caché
qui déclenche le rerun + toggle de session_state.
"""

import streamlit as st
import streamlit.components.v1 as components_v1
from ia_bot import discuter_avec_ia


def render_chat_bubble():
    """Bulle 💬 fixée viewport + panel chat Streamlit sous les onglets."""

    show = st.session_state.get("show_chat", False)

    # ── Bouton Streamlit caché — son clic déclenche le rerun ──────────────
    # On l'entoure d'un div avec un id connu pour que le JS puisse le trouver.
    st.markdown('<div id="qt-chat-hidden-toggle" style="display:none">', unsafe_allow_html=True)
    if st.button("__toggle_chat__", key="qt_chat_toggle"):
        st.session_state.show_chat = not show
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Injection JS : bulle fixée dans window.parent.document ────────────
    icon = "✕" if show else "💬"
    first_visit = not show and not st.session_state.messages_chat
    tooltip_js = (
        """
        var tip = pdoc.createElement('div');
        tip.id = 'qt-bubble-tip';
        tip.innerHTML = '<strong>Analyste IA</strong><br>Posez vos questions sur votre simulation ou les marchés.';
        tip.style.cssText = [
            'position:fixed','bottom:96px','right:28px','z-index:2147483646',
            'background:#1e222d','border:1px solid #2a2e39','border-radius:12px',
            'padding:10px 14px','font-size:13px','color:#d1d4dc',
            'max-width:220px','text-align:center','line-height:1.5',
            'box-shadow:0 4px 16px rgba(0,0,0,0.3)','pointer-events:none'
        ].join(';');
        pdoc.body.appendChild(tip);
        setTimeout(function(){ if(tip.parentNode) tip.parentNode.removeChild(tip); }, 6000);
        """
        if first_visit else ""
    )

    components_v1.html(f"""
<script>
(function() {{
    var pdoc = window.parent.document;

    // Supprimer l'ancienne bulle si elle existe déjà
    ['qt-fixed-bubble','qt-bubble-tip'].forEach(function(id){{
        var el = pdoc.getElementById(id);
        if (el) el.remove();
    }});

    // Créer le bouton fixé dans le DOM parent
    var btn = pdoc.createElement('button');
    btn.id = 'qt-fixed-bubble';
    btn.textContent = '{icon}';
    btn.title = 'Analyste IA — poser une question';
    btn.style.cssText = [
        'position:fixed','bottom:28px','right:28px','z-index:2147483647',
        'width:58px','height:58px','border-radius:50%',
        'background:#6366f1','color:white','font-size:26px',
        'border:none','cursor:pointer','outline:none',
        'box-shadow:0 4px 20px rgba(99,102,241,0.5)',
        'transition:transform 0.18s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.18s ease',
        'display:flex','align-items:center','justify-content:center'
    ].join(';');

    btn.onmouseenter = function(){{
        btn.style.transform = 'scale(1.1)';
        btn.style.boxShadow = '0 6px 28px rgba(99,102,241,0.7)';
    }};
    btn.onmouseleave = function(){{
        btn.style.transform = 'scale(1)';
        btn.style.boxShadow = '0 4px 20px rgba(99,102,241,0.5)';
    }};

    btn.onclick = function() {{
        // Cliquer le bouton Streamlit caché pour déclencher le rerun
        var container = pdoc.getElementById('qt-chat-hidden-toggle');
        if (container) {{
            var hiddenBtn = container.querySelector('button');
            if (hiddenBtn) {{ hiddenBtn.click(); return; }}
        }}
        // Fallback : chercher par contenu
        var allBtns = pdoc.querySelectorAll('button');
        for (var i = 0; i < allBtns.length; i++) {{
            if (allBtns[i].textContent.trim() === '__toggle_chat__') {{
                allBtns[i].click(); return;
            }}
        }}
    }};

    pdoc.body.appendChild(btn);
    {tooltip_js}
}})();
</script>
""", height=0)

    # ── Panel chat Streamlit (dans le flux normal, en bas de page) ─────────
    if show:
        st.markdown("---")
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
            '<span style="font-size:1.6em;">🤖</span>'
            '<div><div style="font-weight:700;font-size:1em;color:var(--text)">Analyste IA</div>'
            '<div style="font-size:0.8em;color:var(--text-muted)">Analyste financier senior · répond en temps réel</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        st.caption("Posez vos questions sur votre simulation, les marchés ou la macro-économie.")

        for message in st.session_state.messages_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input(
            "Ex : Pourquoi l'Or monte-t-il en période de crise ?",
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
