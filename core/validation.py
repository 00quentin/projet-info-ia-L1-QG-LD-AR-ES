"""
core/validation.py
==================
Validations de configuration de simulation. Logique pure, testable, sans
import Streamlit. handlers.py se contente d'afficher les erreurs renvoyees.
"""

from typing import Dict, List, Optional, Tuple


def valider_actifs_et_allocation(
    actifs_selectionnes: List[str],
    profil_risque: str,
    allocations_custom: Dict[str, int],
) -> Optional[str]:
    """Valide qu'au moins un actif est selectionne et que l'allocation Personnalisee
    totalise 100%.

    Returns:
        None si la config est valide, sinon un message d'erreur traduisible
        affichable a l'utilisateur.
    """
    if not actifs_selectionnes:
        return "Sélectionnez au moins un actif dans la barre latérale."
    if profil_risque == "Personnalisé":
        total = sum(allocations_custom.values())
        if total != 100:
            return f"L'allocation doit totaliser 100% (actuellement {total}%)."
    return None


def valider_scenarios_textes(textes: Dict[str, str], min_len: int = 10
                                ) -> Optional[Tuple[str, str]]:
    """Valide chaque scenario texte. Renvoie le 1er en erreur, ou None.

    Returns:
        None si tous OK, sinon (label_du_scenario, message_d_erreur).
    """
    for label, txt in textes.items():
        if len(txt.strip()) < min_len:
            return (label, f"Scénario {label} trop court (au moins {min_len} caractères).")
    return None


def construire_params_sim_simulation(config: Dict, nb_scenarios: int) -> Dict:
    """Construit le dict params_sim a stocker dans st.session_state pour
    une simulation prospective. Pure (pas d'effet de bord)."""
    return {
        "actifs_sim":   list(config["actifs_selectionnes"]),
        "allocations":  dict(config["allocations_custom"]),
        "profil":       config["profil_risque"],
        "capital":      config["capital_initial"],
        "duree":        config["duree"],
        "mc":           config["mode_monte_carlo"],
        "nb_scenarios": nb_scenarios,
        "prix_reels":   config["utiliser_prix_reels"],
        "calib":        config["calibration_historique"],
    }


def construire_params_sim_backtest(config: Dict, actifs_disponibles: List[str]
                                      ) -> Dict:
    """Construit le dict params_sim a stocker dans st.session_state pour
    un backtest historique. Pure (pas d'effet de bord)."""
    return {
        "actifs_sim":   list(actifs_disponibles),
        "allocations":  dict(config["allocations_custom"]),
        "profil":       config["profil_risque"],
        "capital":      config["capital_initial"],
    }
