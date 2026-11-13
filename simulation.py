"""
simulation.py
=============
Moteur de simulation des trajectoires de prix.

Principe : l'IA donne le choc attendu de chaque actif sur l'horizon. Le moteur
tire autour de ce choc des trajectoires aleatoires dont la volatilite et les
correlations sont celles mesurees sur les vrais marches. La mediane des
trajectoires retombe sur le choc de l'IA.

Trois modeles d'alea :
- Probabiliste : rendements gaussiens correles.
- Historique   : rejoue des blocs de vraies seances passees (queues epaisses
                 et co-mouvements reels) ; loi de Student si l'historique manque.
- Tendance     : rendements autocorreles, choc qui s'accelere dans le temps.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import (
    ACTIFS_SECOURS, ACTIF_TAUX_EUR_USD,
    BOOTSTRAP_MIN_SEANCES, BOOTSTRAP_TAILLE_BLOC,
    CORRELATION_INTER_GROUPES, CORRELATION_INTRA_GROUPE,
    GROUPE_CORRELATION, GROUPE_CORRELATION_DEFAUT,
    MOMENTUM_ACCELERATION, MOMENTUM_AUTOCORRELATION,
    NB_CHEMINS_CONSERVES, PERTE_MAX_QUOTIDIENNE, STUDENT_DEGRES_LIBERTE,
)

# Alias retro-compatible : catalogue prix/volatilite de secours.
ACTIFS_PRO = ACTIFS_SECOURS

_PRIX_DEFAUT = 100.0
_VOL_DEFAUT = 0.015
_CHOC_MIN, _CHOC_MAX = -0.95, 5.0


def _normaliser_impacts(chocs_ia: dict) -> Dict[str, float]:
    """Convertit les chocs IA en decimaux bornes (25 -> 0.25, max +500%)."""
    impacts = {}
    for actif, valeur in (chocs_ia.get("actifs") or {}).items():
        try:
            v = float(valeur)
        except (TypeError, ValueError):
            v = 0.0
        if not np.isfinite(v):
            v = 0.0
        # Au-dela de 3 (=300%), c'est un pourcentage mal forme
        if abs(v) > 3:
            v = v / 100.0
        impacts[actif] = max(_CHOC_MIN, min(_CHOC_MAX, v))
    return impacts


def _preparer_actifs(actifs, prix_reels, vols_reelles, actifs_extras
                     ) -> Tuple[List[str], np.ndarray, np.ndarray]:
    """Resout la liste des actifs a simuler avec leur prix initial et volatilite."""
    catalogue = {k: dict(v) for k, v in ACTIFS_SECOURS.items()}
    for sim_key, params in (actifs_extras or {}).items():
        catalogue[sim_key] = {
            "prix":       float(params.get("prix", _PRIX_DEFAUT)),
            "volatilite": float(params.get("volatilite", _VOL_DEFAUT)),
        }

    cles = [k for k in catalogue if actifs is None or k in actifs]
    if not cles:
        cles = list(catalogue)

    prix, vols = [], []
    for k in cles:
        p = (prix_reels or {}).get(k) or 0
        v = (vols_reelles or {}).get(k) or 0
        prix.append(p if p > 0 else catalogue[k]["prix"])
        vols.append(v if v > 0 else catalogue[k]["volatilite"])
    return cles, np.array(prix, dtype=float), np.array(vols, dtype=float)


def _correlation_secours(a: str, b: str) -> float:
    ga = GROUPE_CORRELATION.get(a, GROUPE_CORRELATION_DEFAUT)
    gb = GROUPE_CORRELATION.get(b, GROUPE_CORRELATION_DEFAUT)
    if ga == gb:
        return CORRELATION_INTRA_GROUPE.get(ga, 0.0)
    return CORRELATION_INTER_GROUPES.get((ga, gb), CORRELATION_INTER_GROUPES.get((gb, ga), 0.0))


def construire_correlations(cles: List[str],
                            rendements_historiques: Optional[pd.DataFrame] = None
                            ) -> np.ndarray:
    """Matrice de correlation des actifs : mesuree sur l'historique reel quand
    il existe, completee par les ordres de grandeur de config sinon."""
    n = len(cles)
    corr = np.eye(n)
    mesurees = None
    if rendements_historiques is not None and not rendements_historiques.empty:
        mesurees = rendements_historiques.corr(min_periods=60)

    for i, a in enumerate(cles):
        for j in range(i + 1, n):
            b = cles[j]
            c = np.nan
            if mesurees is not None and a in mesurees.index and b in mesurees.columns:
                c = mesurees.loc[a, b]
            if not np.isfinite(c):
                c = _correlation_secours(a, b)
            corr[i, j] = corr[j, i] = c

    # Un melange mesure/secours n'est pas toujours une matrice valide :
    # on ecrete les valeurs propres negatives puis on renormalise la diagonale.
    valeurs, vecteurs = np.linalg.eigh(corr)
    if valeurs.min() < 1e-8:
        corr = (vecteurs * np.clip(valeurs, 1e-8, None)) @ vecteurs.T
        d = np.sqrt(np.diag(corr))
        corr = corr / np.outer(d, d)
    return corr


def _innovations_bootstrap(rendements: pd.DataFrame, cles: List[str], nb: int,
                           pas: int, rng: np.random.Generator) -> Optional[np.ndarray]:
    """Rejoue des blocs de vraies seances (toutes colonnes ensemble, donc les
    co-mouvements reels sont conserves). Retourne None si historique insuffisant."""
    if rendements is None or any(c not in rendements.columns for c in cles):
        return None
    base = rendements[cles].dropna()
    if len(base) < BOOTSTRAP_MIN_SEANCES:
        return None
    ecarts = base.std().values
    if (ecarts <= 0).any():
        return None
    std = ((base - base.mean()) / ecarts).values  # centre-reduit : seule la forme compte

    nb_blocs = -(-pas // BOOTSTRAP_TAILLE_BLOC)
    debuts = rng.integers(0, len(std) - BOOTSTRAP_TAILLE_BLOC + 1, size=(nb, nb_blocs))
    idx = (debuts[:, :, None] + np.arange(BOOTSTRAP_TAILLE_BLOC)).reshape(nb, -1)[:, :pas]
    return std[idx]


def _innovations(modele: str, cles: List[str], nb: int, pas: int,
                 rendements_historiques: Optional[pd.DataFrame],
                 rng: np.random.Generator) -> np.ndarray:
    """Tirages centres de variance 1, correles entre actifs : (nb, pas, n_actifs)."""
    n = len(cles)
    if "Historique" in modele:
        boot = _innovations_bootstrap(rendements_historiques, cles, nb, pas, rng)
        if boot is not None:
            return boot

    cholesky = np.linalg.cholesky(construire_correlations(cles, rendements_historiques))

    if "Historique" in modele:
        nu = STUDENT_DEGRES_LIBERTE
        z = rng.standard_normal((nb, pas, n)) @ cholesky.T
        # Student multivariee : meme facteur d'echelle pour tous les actifs d'une
        # seance, donc les seances extremes touchent tout le portefeuille a la fois.
        echelle = np.sqrt(nu / rng.chisquare(nu, size=(nb, pas, 1)))
        return z * echelle * np.sqrt((nu - 2) / nu)

    z = rng.standard_normal((nb, pas, n)) @ cholesky.T
    if "Probabiliste" in modele:
        return z

    # Tendance : AR(1) de variance stationnaire 1
    phi = MOMENTUM_AUTOCORRELATION
    eps = np.empty_like(z)
    eps[:, 0] = z[:, 0]
    for t in range(1, pas):
        eps[:, t] = phi * eps[:, t - 1] + np.sqrt(1 - phi ** 2) * z[:, t]
    return eps


def generer_chemins(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                    actifs=None, nb_simulations=1, prix_reels=None, vols_reelles=None,
                    actifs_extras=None, rendements_historiques=None,
                    actifs_en_usd=None, graine=None) -> Tuple[List[str], np.ndarray]:
    """
    Genere nb_simulations trajectoires de prix.

    Args:
        rendements_historiques: DataFrame de rendements quotidiens reels
            (colonnes = sim_keys) pour mesurer les correlations et alimenter
            le modele Historique. Optionnel.
        actifs_en_usd: actifs cotes en dollars a exprimer en euros via la
            trajectoire simulee de l'EUR/USD (qui doit faire partie des actifs).

    Returns:
        (cles, chemins) avec chemins de forme (nb_simulations, jours, n_actifs).
    """
    rng = np.random.default_rng(graine)
    impacts = _normaliser_impacts(chocs_ia or {})
    cles, prix0, vols = _preparer_actifs(actifs, prix_reels, vols_reelles, actifs_extras)
    pas = max(int(jours) - 1, 1)
    n = len(cles)

    eps = _innovations(modele, cles, nb_simulations, pas, rendements_historiques, rng)

    # Derive en log telle que la trajectoire mediane atteigne le choc de l'IA
    log_cible = np.log1p(np.array([impacts.get(k, 0.0) for k in cles]))
    if "Probabiliste" in modele or "Historique" in modele:
        profil = np.full(pas, 1.0 / pas)
    else:
        profil = 1 + MOMENTUM_ACCELERATION * np.arange(1, pas + 1) / pas
        profil = profil / profil.sum()
    derive = profil[:, None] * log_cible[None, :]

    log_rendements = derive[None, :, :] + eps * vols[None, None, :]
    log_rendements = np.maximum(log_rendements, np.log(1 - PERTE_MAX_QUOTIDIENNE))

    chemins = np.empty((nb_simulations, pas + 1, n))
    chemins[:, 0, :] = prix0
    chemins[:, 1:, :] = prix0 * np.exp(np.cumsum(log_rendements, axis=1))

    if actifs_en_usd and ACTIF_TAUX_EUR_USD in cles:
        taux = chemins[:, :, cles.index(ACTIF_TAUX_EUR_USD)]
        for k in actifs_en_usd:
            if k in cles and k != ACTIF_TAUX_EUR_USD:
                chemins[:, :, cles.index(k)] /= taux

    return cles, chemins


def simuler_marche_dynamique(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                             actifs=None, prix_reels=None, vols_reelles=None,
                             actifs_extras=None, rendements_historiques=None,
                             actifs_en_usd=None, graine=None) -> pd.DataFrame:
    """Une seule trajectoire : DataFrame (jours x actifs)."""
    cles, chemins = generer_chemins(
        chocs_ia, jours=jours, modele=modele, actifs=actifs, nb_simulations=1,
        prix_reels=prix_reels, vols_reelles=vols_reelles, actifs_extras=actifs_extras,
        rendements_historiques=rendements_historiques,
        actifs_en_usd=actifs_en_usd, graine=graine,
    )
    return pd.DataFrame(chemins[0], columns=cles)


def simuler_monte_carlo(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                        actifs=None, nb_simulations=1000, prix_reels=None,
                        vols_reelles=None, actifs_extras=None,
                        rendements_historiques=None, actifs_en_usd=None,
                        graine=None) -> dict:
    """
    Monte-Carlo : mediane et intervalle 5%-95% par actif, plus un echantillon
    de trajectoires completes ("chemins") pour calculer le risque du portefeuille
    sur de vraies trajectoires plutot que sur la mediane lissee.
    """
    cles, chemins = generer_chemins(
        chocs_ia, jours=jours, modele=modele, actifs=actifs,
        nb_simulations=nb_simulations, prix_reels=prix_reels,
        vols_reelles=vols_reelles, actifs_extras=actifs_extras,
        rendements_historiques=rendements_historiques,
        actifs_en_usd=actifs_en_usd, graine=graine,
    )
    bas, mediane, haut = np.percentile(chemins, [5, 50, 95], axis=0)
    return {
        "mediane": pd.DataFrame(mediane, columns=cles),
        "bas":     pd.DataFrame(bas, columns=cles),
        "haut":    pd.DataFrame(haut, columns=cles),
        "chemins": chemins[:NB_CHEMINS_CONSERVES].astype(np.float32),
        "colonnes": cles,
        "nb_simulations": nb_simulations,
    }
