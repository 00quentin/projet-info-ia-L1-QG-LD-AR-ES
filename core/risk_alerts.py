"""
core/risk_alerts.py
===================
Detection automatique des profils de risque alarmants ou exceptionnels.

Pourquoi : un utilisateur non specialiste regarde les jauges de risque
sans savoir quel niveau est inquietant. Cette logique scanne les
metriques et fait remonter explicitement les drapeaux rouges (drawdown
severe, Sharpe negatif, vol extreme) ainsi que les performances
remarquables (Sharpe > 2).

Seuils calibres selon les standards de l'industrie :
- Sharpe Ratio : >2 excellent, 1-2 bon, 0-1 acceptable, <0 mauvais
- Max Drawdown : <10% limite, 10-25% modere, 25-40% severe, >40% critique
- Volatilite annualisee : <15% modere, 15-25% normal, 25-35% eleve,
  >35% tres eleve (cryptos, leveraged)
- VaR 95% (1 jour) : > -2% faible, -2 a -4% modere, < -4% eleve

Tout ceci est purement defensif : on alerte, on n'empeche jamais
l'utilisateur de continuer.
"""

from dataclasses import dataclass
from typing import Dict, List, Literal


Severite = Literal["info", "success", "warning", "error"]


@dataclass(frozen=True)
class AlerteRisque:
    """Une alerte issue de l'analyse des metriques."""
    severite: Severite      # mapping vers components/notifications.py
    titre: str              # libelle court (3-5 mots)
    message: str            # explication 1 phrase, lisible non-specialiste
    metrique: str           # nom de la metrique source (vol_ann, sharpe, max_dd, var_95)


def evaluer_alertes_risque(metriques: Dict[str, float]) -> List[AlerteRisque]:
    """
    Analyse les metriques et retourne une liste d'alertes triees par
    severite (les plus urgentes en premier).

    Args:
        metriques: dict {vol_ann, sharpe, max_dd, var_95} (sortie de
                    calculer_metriques_risque).

    Returns:
        Liste d'AlerteRisque, ordre : error -> warning -> success -> info.
    """
    alertes: List[AlerteRisque] = []

    sharpe = metriques.get("sharpe", 0.0)
    vol = metriques.get("vol_ann", 0.0)
    dd = metriques.get("max_dd", 0.0)
    var = abs(metriques.get("var_95", 0.0))

    # === Sharpe Ratio ===
    if sharpe < -1.0:
        alertes.append(AlerteRisque(
            "error", "Rendement risque tres defavorable",
            f"Sharpe Ratio de {sharpe:.2f} : le portefeuille perd plus que ce que le risque le justifie. Reconsiderer l'allocation.",
            "sharpe"))
    elif sharpe < 0:
        alertes.append(AlerteRisque(
            "warning", "Sharpe Ratio negatif",
            f"Sharpe de {sharpe:.2f} : la volatilite n'est pas compensee par le rendement.",
            "sharpe"))
    elif sharpe >= 2.0:
        alertes.append(AlerteRisque(
            "success", "Excellent rapport rendement-risque",
            f"Sharpe de {sharpe:.2f} : performance exceptionnelle compte tenu du risque pris.",
            "sharpe"))

    # === Max Drawdown ===
    if dd >= 40.0:
        alertes.append(AlerteRisque(
            "error", "Drawdown critique",
            f"Chute maximale de -{dd:.1f}% depuis un sommet : le portefeuille a connu un effondrement majeur. Hors profil prudent.",
            "max_dd"))
    elif dd >= 25.0:
        alertes.append(AlerteRisque(
            "warning", "Drawdown severe",
            f"Chute maximale de -{dd:.1f}% : pertes temporaires importantes. A reserver aux profils tolerants au risque.",
            "max_dd"))

    # === Volatilite annualisee ===
    if vol >= 50.0:
        alertes.append(AlerteRisque(
            "error", "Volatilite extreme",
            f"Volatilite annualisee de {vol:.1f}% : variations dignes d'actifs cryptos ou leverages. Risque de pertes brutales.",
            "vol_ann"))
    elif vol >= 35.0:
        alertes.append(AlerteRisque(
            "warning", "Volatilite tres elevee",
            f"Volatilite annualisee de {vol:.1f}% : amplitude des variations bien superieure a un portefeuille standard.",
            "vol_ann"))

    # === VaR 95% (1 jour) ===
    if var >= 5.0:
        alertes.append(AlerteRisque(
            "warning", "Risque journalier eleve",
            f"VaR 95% a 1 jour de -{var:.2f}% : probabilite reelle de perdre plus de {var:.1f}% en une seule seance.",
            "var_95"))

    # Tri : error > warning > success > info
    ordre = {"error": 0, "warning": 1, "success": 2, "info": 3}
    return sorted(alertes, key=lambda a: ordre[a.severite])
