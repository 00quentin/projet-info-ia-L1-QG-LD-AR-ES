"""
components/notifications.py
===========================
Systeme de notifications unifie : un seul style cross-app pour les
messages de validation, erreur et confirmation.

Pourquoi ne pas reutiliser st.warning / st.error directement ?
- Ils utilisent les couleurs Streamlit par defaut, sans cohesion avec
  les design tokens (--accent, --primary, --warn, --danger).
- Pas de control sur l'icone ni sur le poids visuel.
- En dark mode, leur fond clair detonne avec le reste de l'UI.

Usage :
    from components.notifications import notify, notify_success, notify_warn,
                                          notify_error, notify_info, toast_done

    notify_warn("Sélectionnez au moins un actif.")
    notify_error("Aucune donnée disponible pour cette période.")
    notify_success("Rapport prêt !")
    toast_done("Simulation terminée", icon="🎉")
"""

from typing import Optional, Literal
import streamlit as st


Kind = Literal["info", "success", "warning", "error"]

# Mapping vers icone Material Symbols + couleur semantique
_KIND_META = {
    "info":    ("info",            "var(--accent)",  "rgba(49,151,149,0.10)", "rgba(49,151,149,0.32)"),
    "success": ("check_circle",    "var(--success)", "rgba(47,133,90,0.10)",  "rgba(47,133,90,0.32)"),
    "warning": ("warning",         "var(--warn)",    "rgba(214,158,46,0.12)", "rgba(214,158,46,0.36)"),
    "error":   ("error",           "var(--danger)",  "rgba(197,48,48,0.10)",  "rgba(197,48,48,0.32)"),
}

# Roles ARIA : alert pour error/warning (urgent), status pour info/success
_ARIA_ROLE = {"info": "status", "success": "status", "warning": "alert", "error": "alert"}


def notify(message: str, kind: Kind = "info", icon: Optional[str] = None) -> None:
    """Affiche une notification inline stylee (non-toast, persistante)."""
    sym, color, bg, border = _KIND_META[kind]
    role = _ARIA_ROLE[kind]
    icon_html = (
        f'<span class="material-symbols-rounded qt-notify-icon" aria-hidden="true">{icon or sym}</span>'
    )
    st.markdown(
        f'<div class="qt-notify qt-notify-{kind}" role="{role}" '
        f'style="background:{bg}; border-color:{border}; color:var(--text);">'
        f'{icon_html}'
        f'<span class="qt-notify-msg" style="color:{color};">{message}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def notify_info(message: str, icon: Optional[str] = None) -> None:
    notify(message, "info", icon)


def notify_success(message: str, icon: Optional[str] = None) -> None:
    notify(message, "success", icon)


def notify_warn(message: str, icon: Optional[str] = None) -> None:
    notify(message, "warning", icon)


def notify_error(message: str, icon: Optional[str] = None) -> None:
    notify(message, "error", icon)


def toast_done(message: str, kind: Kind = "success", icon: Optional[str] = None) -> None:
    """Wrapper sur st.toast : ephemere, en haut a droite. Pour les
    confirmations apres action (simulation OK, PDF genere, etc.)."""
    default_icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    st.toast(message, icon=icon or default_icons[kind])
