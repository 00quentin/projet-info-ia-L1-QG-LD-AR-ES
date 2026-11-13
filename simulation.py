"""
simulation.py
=============
Moteur de simulation des trajectoires de prix.

Principe : l'IA donne le choc attendu de chaque actif sur l'horizon. Le moteur
tire autour de ce choc des trajectoires aleatoires dont la volatilite et les
correlations sont celles mesurees sur les vrais marches. La mediane des
trajectoires retombe sur le choc de l'IA. En Monte-Carlo, chaque trajectoire
tire en plus son choc dans la fourchette bas / central / haut de l'IA.

Trois modeles d'alea :
- Probabiliste : rendements gaussiens correles, profil de choc "crise".
- Historique   : rejoue des blocs de vraies seances passees (queues epaisses
                 et co-mouvements reels) ; loi de Student si l'historique manque.
                 Profil de choc "crise".
- Tendance     : rendements autocorreles, choc qui s'accelere dans le temps.
"""

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import (
    ACTIFS_SECOURS, ACTIF_TAUX_EUR_USD,
    BOOTSTRAP_MIN_SEANCES, BOOTSTRAP_TAILLE_BLOC,
    CORRELATION_INTER_GROUPES, CORRELATION_INTRA_GROUPE,
    CRISE_DEPASSEMENT, CRISE_FRACTION_CREUX,
    GROUPE_CORRELATION, GROUPE_CORRELATION_DEFAUT, INCERTITUDE_IA_CORRELATION,
    MOMENTUM_ACCELERATION, MOMENTUM_AUTOCORRELATION,
    NB_CHEMINS_CONSERVES, PERTE_MAX_QUOTIDIENNE, STUDENT_DEGRES_LIBERTE,
)

# Alias retro-compatible : catalogue prix/volatilite de secours.
ACTIFS_PRO = ACTIFS_SECOURS

_PRIX_DEFAUT = 100.0
_VOL_DEFAUT = 0.015
_CHOC_MIN, _CHOC_MAX = -0.95, 5.0
# Meme seuil que schemas.py : les bornes y montent jusqu'a +500 % (VIX), donc un
# choc de 4 (= +400 %) est un decimal valide, pas un pourcentage mal forme.
_SEUIL_POURCENTAGE = 5.0
_TOLERANCE_CENTRAL = 1e-6


def _en_decimal(valeur, defaut: float = 0.0) -> float:
    """Choc IA en decimal borne (25 -> 0.25, max +500%) ; `defaut` si illisible."""
    try:
        v = float(valeur)
    except (TypeError, ValueError):
        return defaut
    if not np.isfinite(v):
        return defaut
    if abs(v) > _SEUIL_POURCENTAGE:
        v = v / 100.0
    return max(_CHOC_MIN, min(_CHOC_MAX, v))


def _normaliser_impacts(chocs_ia: dict) -> Dict[str, float]:
    """Convertit les chocs IA en decimaux bornes."""
    return {actif: _en_decimal(valeur)
            for actif, valeur in (chocs_ia.get("actifs") or {}).items()}


def _bornes_fourchette(chocs_ia: dict, cles: List[str], centraux: np.ndarray
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """Chocs bas et haut de chaque actif, encadrant toujours le central.
    Sans fourchette (ancienne reponse IA), bas = haut = central."""
    fourchettes = (chocs_ia or {}).get("fourchettes") or {}
    bas, haut = centraux.copy(), centraux.copy()
    for i, k in enumerate(cles):
        f = fourchettes.get(k)
        if not isinstance(f, dict):
            continue
        c = centraux[i]
        # Fourchette d'un autre choc central (choc retouche apres l'IA) : ignoree.
        if "central" in f and abs(_en_decimal(f["central"], c) - c) > _TOLERANCE_CENTRAL:
            continue
        bas[i] = min(_en_decimal(f.get("bas"), c), c)
        haut[i] = max(_en_decimal(f.get("haut"), c), c)
    return bas, haut


_repartition_normale = np.vectorize(
    lambda x: 0.5 * (1.0 + math.erf(x / math.sqrt(2.0))), otypes=[float])


def tirer_chocs(bas: np.ndarray, central: np.ndarray, haut: np.ndarray, nb: int,
                rng: np.random.Generator) -> np.ndarray:
    """Un choc par trajectoire et par actif, tire dans [bas, haut] : (nb, n_actifs).

    Loi triangulaire en deux moities (mode = central), une chance sur deux de
    chaque cote : la mediane des chocs tires reste le central de l'IA meme si la
    fourchette est asymetrique (une triangulaire classique la decalerait).
    Le tirage est en grande partie commun aux actifs : si le scenario s'avere plus
    grave, tous s'eloignent ensemble de zero, chacun dans le sens de son choc.
    """
    rho = INCERTITUDE_IA_CORRELATION
    gravite = rng.standard_normal((nb, 1))
    z = np.sqrt(rho) * gravite + np.sqrt(1 - rho) * rng.standard_normal((nb, len(central)))
    u = _repartition_normale(z)
    u = np.where(central < 0, 1 - u, u)
    moitie_basse = bas + (central - bas) * np.sqrt(2 * u)
    moitie_haute = haut - (haut - central) * np.sqrt(2 * (1 - u))
    return np.where(u < 0.5, moitie_basse, moitie_haute)


def profil_choc(modele: str, pas: int) -> np.ndarray:
    """Part du choc de l'IA realisee a chaque seance (somme = 1, donc la
    trajectoire mediane finit toujours sur le choc de l'IA)."""
    if "Probabiliste" in modele or "Historique" in modele:
        # Une vraie crise ne derive pas a vitesse constante : elle chute vite
        # (plus fort les premiers jours), depasse sa cible puis rebondit en partie.
        t = np.arange(pas + 1) / pas
        creux, pic = CRISE_FRACTION_CREUX, 1 + CRISE_DEPASSEMENT
        chute = pic * (1 - (1 - np.minimum(t / creux, 1)) ** 2)
        s = np.clip((t - creux) / (1 - creux), 0, 1)
        rebond = CRISE_DEPASSEMENT * (1 - (1 - s) ** 2)
        return np.diff(np.where(t <= creux, chute, pic - rebond))
    profil = 1 + MOMENTUM_ACCELERATION * np.arange(1, pas + 1) / pas
    return profil / profil.sum()


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
                    actifs_en_usd=None, graine=None,
                    incertitude_ia=False) -> Tuple[List[str], np.ndarray]:
    """
    Genere nb_simulations trajectoires de prix.

    Args:
        rendements_historiques: DataFrame de rendements quotidiens reels
            (colonnes = sim_keys) pour mesurer les correlations et alimenter
            le modele Historique. Optionnel.
        actifs_en_usd: actifs cotes en dollars a exprimer en euros via la
            trajectoire simulee de l'EUR/USD (qui doit faire partie des actifs).
        incertitude_ia: chaque trajectoire tire son choc dans la fourchette
            chocs_ia["fourchettes"] au lieu de prendre le choc central.

    Returns:
        (cles, chemins) avec chemins de forme (nb_simulations, jours, n_actifs).
    """
    rng = np.random.default_rng(graine)
    impacts = _normaliser_impacts(chocs_ia or {})
    cles, prix0, vols = _preparer_actifs(actifs, prix_reels, vols_reelles, actifs_extras)
    pas = max(int(jours) - 1, 1)
    n = len(cles)

    eps = _innovations(modele, cles, nb_simulations, pas, rendements_historiques, rng)

    cibles = np.array([impacts.get(k, 0.0) for k in cles])
    if incertitude_ia:
        bas, haut = _bornes_fourchette(chocs_ia, cles, cibles)
        if (haut > bas).any():
            cibles = tirer_chocs(bas, cibles, haut, nb_simulations, rng)

    # Derive en log telle que la trajectoire mediane atteigne le choc de l'IA
    log_cible = np.log1p(np.atleast_2d(cibles))
    derive = profil_choc(modele, pas)[None, :, None] * log_cible[:, None, :]

    log_rendements = derive + eps * vols[None, None, :]
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
    sur de vraies trajectoires plutot que sur la mediane lissee. L'intervalle
    tient compte du bruit de marche ET du doute de l'IA (fourchette des chocs).
    """
    cles, chemins = generer_chemins(
        chocs_ia, jours=jours, modele=modele, actifs=actifs,
        nb_simulations=nb_simulations, prix_reels=prix_reels,
        vols_reelles=vols_reelles, actifs_extras=actifs_extras,
        rendements_historiques=rendements_historiques,
        actifs_en_usd=actifs_en_usd, graine=graine, incertitude_ia=True,
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
