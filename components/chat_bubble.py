"""
components/chat_bubble.py
=========================
Bulle 💬 flottante + dialog chat plein écran.

Le JS dans components.html() cherche le bouton Streamlit caché par son
texte unique "QT_CHAT_TRIGGER", le masque visuellement et le clique
quand l'utilisateur appuie sur la bulle → déclenche le rerun Streamlit.
"""

import streamlit as st
import streamlit.components.v1 as components_v1
from ia_bot import discuter_avec_ia

# Texte unique du bouton caché — le JS le cherche par ce texte
_TRIGGER = "QT_CHAT_TRIGGER"

EXEMPLES = [
    "Pourquoi l'Or monte-t-il en période de crise ?",
    "Qu'est-ce que le VIX et à quoi sert-il ?",
    "Comment interpréter le ratio de Sharpe ?",
    "Quel impact d'une hausse des taux sur les obligations ?",
    "Pourquoi le pétrole et le dollar sont-ils liés ?",
    "C'est quoi la corrélation actions / obligations ?",
]


@st.dialog("🤖  Analyste IA", width="large")
def _dialog_chat():
    """Modal chat : présentation à gauche, conversation à droite."""
    col_pres, col_sep, col_chat = st.columns([1, 0.04, 1.4])

    with col_pres:
        st.markdown("""
        <div style="text-align:center;padding:8px 0 18px;">
            <div style="font-size:3em;margin-bottom:6px;">🤖</div>
            <div style="font-size:1.05em;font-weight:700;color:var(--text);">Analyste Financier IA</div>
            <div style="font-size:0.82em;color:var(--text-muted);margin-top:6px;line-height:1.5;">
                Posez vos questions sur les marchés,<br>la macro-économie ou votre simulation.
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            '<div style="font-size:0.75em;font-weight:600;text-transform:uppercase;'
            'letter-spacing:.7px;color:var(--text-muted);margin-bottom:8px;">Questions fréquentes</div>',
            unsafe_allow_html=True)

        for q in EXEMPLES:
            if st.button(q, use_container_width=True, key=f"ex_{abs(hash(q))}"):
                st.session_state.messages_chat.append({"role": "user", "content": q})
                with st.spinner("L'analyste rédige…"):
                    rep = discuter_avec_ia(st.session_state.messages_chat)
                st.session_state.messages_chat.append({"role": "assistant", "content": rep})
                st.rerun()

        st.markdown('<hr style="border-color:var(--border);margin:14px 0;">', unsafe_allow_html=True)
        if st.button("✕  Fermer", use_container_width=True):
            st.session_state.show_chat = False
            st.rerun()

    with col_sep:
        st.markdown(
            '<div style="height:500px;border-left:1px solid var(--border);margin:0 auto;"></div>',
            unsafe_allow_html=True)

    with col_chat:
        if not st.session_state.messages_chat:
            st.markdown("""
            <div style="text-align:center;padding:60px 16px;color:var(--text-muted);">
                <div style="font-size:2em;margin-bottom:10px;">💬</div>
                <div style="font-size:0.88em;">Aucune question posée.<br>
                Choisissez un exemple ou tapez ci-dessous.</div>
            </div>""", unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages_chat[-12:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        question = st.chat_input("Tapez votre question…", key="qt_dialog_input")
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
    icon = "✕" if show else "💬"

    # ── Bouton Streamlit caché, trouvé par le JS via son texte unique ─────
    if st.button(_TRIGGER, key="qt_chat_toggle"):
        st.session_state.show_chat = not show
        st.rerun()

    # ── Injection JS : crée la bulle fixée + masque + câble le clic ───────
    components_v1.html(f"""
<script>
(function() {{
    var TRIGGER = "{_TRIGGER}";
    var pdoc = window.parent.document;

    function findTriggerBtn() {{
        var all = pdoc.querySelectorAll('button');
        for (var i = 0; i < all.length; i++) {{
            if (all[i].textContent.trim() === TRIGGER) return all[i];
        }}
        return null;
    }}

    function hideTriggerBtn(btn) {{
        if (!btn) return;
        var wrap = btn.closest('[data-testid="stButton"]') || btn.parentElement;
        if (wrap) {{
            wrap.style.position = 'absolute';
            wrap.style.width = '1px';
            wrap.style.height = '1px';
            wrap.style.opacity = '0';
            wrap.style.overflow = 'hidden';
            wrap.style.pointerEvents = 'none';
        }}
    }}

    function setup() {{
        // Supprimer ancienne bulle
        var old = pdoc.getElementById('qt-fixed-bubble');
        if (old) old.remove();

        // Trouver et masquer le bouton trigger
        var triggerBtn = findTriggerBtn();
        hideTriggerBtn(triggerBtn);

        // Créer la bulle fixée
        var bubble = pdoc.createElement('button');
        bubble.id = 'qt-fixed-bubble';
        bubble.innerHTML = '{icon}';
        bubble.setAttribute('title', 'Ouvrir l\\'Analyste IA');
        bubble.style.cssText = [
            'position:fixed', 'bottom:28px', 'right:28px', 'z-index:2147483647',
            'width:60px', 'height:60px', 'border-radius:50%',
            'background:#6366f1', 'color:white', 'font-size:26px',
            'border:none', 'cursor:pointer', 'outline:none',
            'box-shadow:0 4px 24px rgba(99,102,241,0.55)',
            'transition:transform .2s cubic-bezier(.34,1.56,.64,1),box-shadow .2s ease',
            'display:flex', 'align-items:center', 'justify-content:center'
        ].join(';');

        bubble.onmouseenter = function() {{
            this.style.transform = 'scale(1.12)';
            this.style.boxShadow = '0 6px 32px rgba(99,102,241,0.75)';
        }};
        bubble.onmouseleave = function() {{
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 4px 24px rgba(99,102,241,0.55)';
        }};

        bubble.onclick = function() {{
            var btn = findTriggerBtn();
            if (btn) {{
                // Remettre pointer-events le temps du clic programmatique
                var wrap = btn.closest('[data-testid="stButton"]') || btn.parentElement;
                if (wrap) wrap.style.pointerEvents = 'auto';
                btn.click();
                if (wrap) setTimeout(function(){{ wrap.style.pointerEvents = 'none'; }}, 100);
            }}
        }};

        pdoc.body.appendChild(bubble);
    }}

    // Lancer après que Streamlit a rendu le bouton
    setTimeout(setup, 200);
    setTimeout(setup, 600);
}})();
</script>
""", height=0)

    # ── Ouvrir le dialog si show_chat=True ────────────────────────────────
    if show:
        _dialog_chat()
