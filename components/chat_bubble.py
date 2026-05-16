"""
components/chat_bubble.py
=========================
Bulle 💬 flottante fixée en bas à droite + dialog chat plein écran.

Architecture :
- Un bouton Streamlit vide, caché par CSS via title="__qt_hidden__"
- Un components.html() qui injecte la bulle dans window.parent.document
  et clique ce bouton caché au clic → rerun → dialog s'ouvre
- st.dialog() pour le panel chat (natif Streamlit, modal propre)
"""

import streamlit as st
import streamlit.components.v1 as components_v1
from ia_bot import discuter_avec_ia


EXEMPLES = [
    "Pourquoi l'Or monte-t-il en période de crise ?",
    "Qu'est-ce que le VIX et à quoi sert-il ?",
    "Comment interpréter le ratio de Sharpe ?",
    "Quel est l'impact d'une hausse des taux sur les obligations ?",
    "Pourquoi le pétrole et le dollar sont-ils liés ?",
    "Qu'est-ce que la corrélation actions / obligations ?",
]


@st.dialog("🤖  Analyste IA", width="large")
def _dialog_chat():
    """Interface chat en modal plein écran."""
    col_pres, col_sep, col_chat = st.columns([1, 0.04, 1.4])

    # ── Colonne gauche : présentation + exemples ──────────────────────────
    with col_pres:
        st.markdown("""
        <div style="text-align:center; padding: 12px 0 20px 0;">
            <div style="font-size:3.2em; margin-bottom:8px;">🤖</div>
            <div style="font-size:1.1em; font-weight:700; color:var(--text);">
                Analyste Financier IA
            </div>
            <div style="font-size:0.82em; color:var(--text-muted); margin-top:6px; line-height:1.5;">
                Posez vos questions sur les marchés,<br>
                la macro-économie, ou votre simulation.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div style="font-size:0.78em; font-weight:600; text-transform:uppercase; '
            'letter-spacing:.7px; color:var(--text-muted); margin-bottom:8px;">'
            'Questions fréquentes</div>',
            unsafe_allow_html=True,
        )
        for q in EXEMPLES:
            if st.button(q, use_container_width=True, key=f"ex_{hash(q)}"):
                st.session_state.messages_chat.append({"role": "user", "content": q})
                with st.spinner("L'analyste rédige…"):
                    rep = discuter_avec_ia(st.session_state.messages_chat)
                st.session_state.messages_chat.append({"role": "assistant", "content": rep})
                st.rerun()

        st.markdown('<hr style="border-color:var(--border);margin:14px 0;">', unsafe_allow_html=True)
        if st.button("✕  Fermer le chat", use_container_width=True):
            st.session_state.show_chat = False
            st.rerun()

    # Séparateur vertical
    with col_sep:
        st.markdown(
            '<div style="height:480px; border-left:1px solid var(--border); margin:0 auto;"></div>',
            unsafe_allow_html=True,
        )

    # ── Colonne droite : historique + input ──────────────────────────────
    with col_chat:
        if not st.session_state.messages_chat:
            st.markdown("""
            <div style="text-align:center; padding:60px 20px; color:var(--text-muted);">
                <div style="font-size:2em; margin-bottom:10px;">💬</div>
                <div style="font-size:0.9em;">
                    Aucune question posée pour l'instant.<br>
                    Utilisez les exemples à gauche ou tapez ci-dessous.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages_chat[-12:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        question = st.chat_input(
            "Tapez votre question ici…",
            key="qt_chat_dialog_input",
        )
        if question:
            st.session_state.messages_chat.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Analyse en cours…"):
                    rep = discuter_avec_ia(st.session_state.messages_chat)
                    st.markdown(rep)
            st.session_state.messages_chat.append({"role": "assistant", "content": rep})
            st.rerun()


def render_chat_bubble():
    """Bulle fixée + dialog. À appeler une seule fois dans app.py."""
    show = st.session_state.get("show_chat", False)

    # ── Bouton Streamlit caché (title="__qt_hidden__" → ciblé par CSS) ───
    # C'est ce bouton que le JS clique pour déclencher le rerun Streamlit.
    if st.button("", key="qt_chat_toggle", help="__qt_hidden__"):
        st.session_state.show_chat = not show
        st.rerun()

    # ── Injection JS : bulle fixée dans window.parent.document ────────────
    icon = "✕" if show else "💬"
    components_v1.html(f"""
<script>
(function() {{
    var pdoc = window.parent.document;

    // Supprimer l'ancienne bulle
    var old = pdoc.getElementById('qt-fixed-bubble');
    if (old) old.remove();

    // Trouver et masquer le bouton Streamlit caché (title="__qt_hidden__")
    function hideToggleBtn() {{
        var btns = pdoc.querySelectorAll('button[title="__qt_hidden__"]');
        btns.forEach(function(b) {{
            var wrap = b.closest('[data-testid="stButton"]') || b.parentElement;
            if (wrap) wrap.style.cssText =
                'position:absolute;width:1px;height:1px;opacity:0;overflow:hidden;pointer-events:none;';
        }});
    }}
    hideToggleBtn();
    setTimeout(hideToggleBtn, 300);
    setTimeout(hideToggleBtn, 800);

    // Créer la bulle fixée
    var btn = pdoc.createElement('button');
    btn.id = 'qt-fixed-bubble';
    btn.title = 'Analyste IA — poser une question';
    btn.innerHTML = '{icon}';
    btn.style.cssText = [
        'position:fixed','bottom:28px','right:28px','z-index:2147483647',
        'width:60px','height:60px','border-radius:50%',
        'background:#6366f1','color:white','font-size:26px',
        'border:none','cursor:pointer','outline:none',
        'box-shadow:0 4px 24px rgba(99,102,241,0.55)',
        'transition:transform .2s cubic-bezier(.34,1.56,.64,1),box-shadow .2s ease',
        'display:flex','align-items:center','justify-content:center',
        'font-family:sans-serif'
    ].join(';');

    btn.onmouseenter = function() {{
        this.style.transform = 'scale(1.12)';
        this.style.boxShadow = '0 6px 32px rgba(99,102,241,0.75)';
    }};
    btn.onmouseleave = function() {{
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0 4px 24px rgba(99,102,241,0.55)';
    }};

    btn.onclick = function() {{
        var found = false;
        var targets = pdoc.querySelectorAll('button[title="__qt_hidden__"]');
        targets.forEach(function(b) {{ b.click(); found = true; }});
        if (!found) {{
            // Fallback : chercher le bouton vide caché
            var all = pdoc.querySelectorAll('button');
            all.forEach(function(b) {{
                if (!found && b.textContent.trim() === '' && b.title === '__qt_hidden__') {{
                    b.click(); found = true;
                }}
            }});
        }}
    }};

    pdoc.body.appendChild(btn);
}})();
</script>
""", height=0)

    # ── Ouvrir le dialog si show_chat=True ────────────────────────────────
    if show:
        _dialog_chat()
