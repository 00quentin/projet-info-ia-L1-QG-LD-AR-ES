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
- Probabiliste : rendements gaussiens correles.
- Historique   : rejoue des blocs de vraies seances passees (queues epaisses
                 et co-mouvements reels) ; loi de Student si l'historique manque.
- Tendance     : rendements autocorreles, choc qui s'accelere dans le temps.

Pour Probabiliste et Historique, l'IA choisit la forme du choc dans le temps
(brutal, progressif, rebond) et un regime de crise s'active quand la baisse du
S&P 500 est forte : volatilites majorees, correlations de crise (jours de stress
reels de l'historique, actifs risques rapproches de 1).
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
    NB_CHEMINS_CONSERVES, PERTE_MAX_QUOTIDIENNE, PROFIL_CHOC_DEFAUT, PROFILS_CHOC,
    REBOND_DEPASSEMENT, REBOND_FRACTION_CREUX,
    REGIME_CRISE_ACTIF_REPERE, REGIME_CRISE_ACTIFS_SANS_MAJORATION,
    REGIME_CRISE_FENETRE_VOL, REGIME_CRISE_GROUPES_RISQUES,
    REGIME_CRISE_MELANGE_CORRELATION, REGIME_CRISE_MIN_SEANCES,
    REGIME_CRISE_MULT_VOL, REGIME_CRISE_PLEIN_SP500, REGIME_CRISE_QUANTILE_VOL,
    REGIME_CRISE_SEUIL_SP500, STUDENT_DEGRES_LIBERTE,
    TAUX_CHANGE_SECOURS, TAUX_CHANGE_SIMULATION,
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


def forme_du_choc(chocs_ia: Optional[dict]) -> str:
    """Forme du choc demandee par l'IA ; "brutal" si absente ou inconnue."""
    forme = (chocs_ia or {}).get("profil_choc")
    return forme if forme in PROFILS_CHOC else PROFIL_CHOC_DEFAUT


def _profil_creux(pas: int, creux: float, depassement: float) -> np.ndarray:
    """Chute rapide (plus forte les premiers jours) jusqu'a un extremum qui va
    `depassement` plus loin que le choc final, puis retour vers le choc final."""
    t = np.arange(pas + 1) / pas
    pic = 1 + depassement
    chute = pic * (1 - (1 - np.minimum(t / creux, 1)) ** 2)
    s = np.clip((t - creux) / (1 - creux), 0, 1)
    rebond = depassement * (1 - (1 - s) ** 2)
    return np.diff(np.where(t <= creux, chute, pic - rebond))


def profil_choc(modele: str, pas: int, forme: str = PROFIL_CHOC_DEFAUT) -> np.ndarray:
    """Part du choc de l'IA realisee a chaque seance (somme = 1, donc la
    trajectoire mediane finit toujours sur le choc de l'IA)."""
    if "Probabiliste" in modele or "Historique" in modele:
        if forme == "progressif":
            return np.full(pas, 1.0 / pas)
        if forme == "rebond":
            return _profil_creux(pas, REBOND_FRACTION_CREUX, REBOND_DEPASSEMENT)
        # Une vraie crise ne derive pas a vitesse constante : elle chute vite,
        # depasse sa cible puis rebondit en partie.
        return _profil_creux(pas, CRISE_FRACTION_CREUX, CRISE_DEPASSEMENT)
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

    return _rendre_definie_positive(corr)


def _rendre_definie_positive(corr: np.ndarray) -> np.ndarray:
    """Un melange mesure/secours (ou une correlation de crise retouchee) n'est pas
    toujours une matrice valide : on ecrete les valeurs propres negatives puis on
    renormalise la diagonale."""
    valeurs, vecteurs = np.linalg.eigh(corr)
    if valeurs.min() < 1e-8:
        corr = (vecteurs * np.clip(valeurs, 1e-8, None)) @ vecteurs.T
        d = np.sqrt(np.diag(corr))
        corr = corr / np.outer(d, d)
    return corr


# === Regime de crise ========================================================


def intensite_crise(choc_sp500) -> np.ndarray:
    """Intensite du regime de crise (0 = calme, 1 = crise pleine) selon le choc
    du S&P 500 : nulle tant que la baisse reste sous le seuil, puis lineaire."""
    baisse = -np.asarray(choc_sp500, dtype=float)
    return np.clip((baisse - REGIME_CRISE_SEUIL_SP500)
                   / (REGIME_CRISE_PLEIN_SP500 - REGIME_CRISE_SEUIL_SP500), 0.0, 1.0)


def multiplicateur_volatilite(intensite) -> np.ndarray:
    """Volatilite equivalente : une part `intensite` des seances est en crise."""
    return np.sqrt(1 + np.asarray(intensite, dtype=float) * (REGIME_CRISE_MULT_VOL ** 2 - 1))


def diagnostic_regime_crise(chocs_ia: Optional[dict]) -> dict:
    """Regime de crise du choc central (affichage) : actif, intensite, volatilite x."""
    choc = _normaliser_impacts(chocs_ia or {}).get(REGIME_CRISE_ACTIF_REPERE, 0.0)
    g = float(intensite_crise(choc))
    return {
        "actif": g > 0,
        "intensite": round(g, 3),
        "multiplicateur_vol": round(float(multiplicateur_volatilite(g)), 3),
        "seuil_baisse_sp500": REGIME_CRISE_SEUIL_SP500,
    }


def jours_de_stress(rendements: Optional[pd.DataFrame]) -> Optional[pd.Series]:
    """Seances de forte volatilite du S&P 500 (quintile le plus haut, fenetre centree).
    None si le S&P 500 manque a l'historique."""
    if (rendements is None or rendements.empty
            or REGIME_CRISE_ACTIF_REPERE not in rendements.columns):
        return None
    vol = rendements[REGIME_CRISE_ACTIF_REPERE].rolling(
        REGIME_CRISE_FENETRE_VOL, center=True, min_periods=REGIME_CRISE_FENETRE_VOL // 2).std()
    if vol.notna().sum() == 0:
        return None
    return vol >= vol.quantile(REGIME_CRISE_QUANTILE_VOL)


def correlations_de_crise(cles: List[str],
                          rendements_historiques: Optional[pd.DataFrame] = None) -> np.ndarray:
    """Correlations en crise : mesurees sur les jours de stress de l'historique
    (tout l'historique s'il y en a trop peu), puis celles entre actifs risques
    rapprochees de 1. Toujours definie positive."""
    stress = jours_de_stress(rendements_historiques)
    base = rendements_historiques
    if stress is not None and stress.sum() >= REGIME_CRISE_MIN_SEANCES:
        base = rendements_historiques[stress]
    corr = construire_correlations(cles, base).copy()
    risques = [GROUPE_CORRELATION.get(k, GROUPE_CORRELATION_DEFAUT) in REGIME_CRISE_GROUPES_RISQUES
               for k in cles]
    lam = REGIME_CRISE_MELANGE_CORRELATION
    for i in range(len(cles)):
        for j in range(i + 1, len(cles)):
            if risques[i] and risques[j]:
                corr[i, j] = corr[j, i] = corr[i, j] + lam * (1 - corr[i, j])
    return _rendre_definie_positive(corr)


def _majoration_par_actif(cles: List[str]) -> np.ndarray:
    return np.array([1.0 if k in REGIME_CRISE_ACTIFS_SANS_MAJORATION else REGIME_CRISE_MULT_VOL
                     for k in cles])


# === Innovations (alea quotidien) ===========================================


def _base_bootstrap(rendements: Optional[pd.DataFrame], cles: List[str]) -> Optional[pd.DataFrame]:
    """Seances completes de l'historique pour le modele Historique (None si insuffisant)."""
    if rendements is None or any(c not in rendements.columns for c in cles):
        return None
    base = rendements[cles].dropna()
    if len(base) < BOOTSTRAP_MIN_SEANCES or (base.std().values <= 0).any():
        return None
    return base


def _centrer_reduire(base: pd.DataFrame) -> np.ndarray:
    """Centre-reduit : seule la forme des seances compte, pas leur tendance."""
    return ((base - base.mean()) / base.std()).values


def _tirer_blocs(std: np.ndarray, nb: int, pas: int, rng: np.random.Generator) -> np.ndarray:
    """Blocs de BOOTSTRAP_TAILLE_BLOC seances consecutives : (nb, pas, n_actifs)."""
    nb_blocs = -(-pas // BOOTSTRAP_TAILLE_BLOC)
    debuts = rng.integers(0, len(std) - BOOTSTRAP_TAILLE_BLOC + 1, size=(nb, nb_blocs))
    idx = (debuts[:, :, None] + np.arange(BOOTSTRAP_TAILLE_BLOC)).reshape(nb, -1)[:, :pas]
    return std[idx]


def _innovations_bootstrap(rendements: pd.DataFrame, cles: List[str], nb: int,
                           pas: int, rng: np.random.Generator) -> Optional[np.ndarray]:
    """Rejoue des blocs de vraies seances (toutes colonnes ensemble, donc les
    co-mouvements reels sont conserves). Retourne None si historique insuffisant."""
    base = _base_bootstrap(rendements, cles)
    if base is None:
        return None
    return _tirer_blocs(_centrer_reduire(base), nb, pas, rng)


def _student(z: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Student multivariee : meme facteur d'echelle pour tous les actifs d'une
    seance, donc les seances extremes touchent tout le portefeuille a la fois."""
    nu = STUDENT_DEGRES_LIBERTE
    echelle = np.sqrt(nu / rng.chisquare(nu, size=z.shape[:2] + (1,)))
    return z * echelle * np.sqrt((nu - 2) / nu)


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
        return _student(rng.standard_normal((nb, pas, n)) @ cholesky.T, rng)

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


def _appliquer_regime_crise(modele: str, eps: np.ndarray, intensite: np.ndarray,
                            cles: List[str], rendements_historiques: Optional[pd.DataFrame],
                            rng: np.random.Generator) -> np.ndarray:
    """Melange les innovations normales avec des innovations de crise, trajectoire
    par trajectoire, dans la proportion `intensite` (0 = inchange).

    Historique : une part `intensite` des blocs est tiree parmi les vrais jours de
    stress de l'historique (leurs co-mouvements), amplifiee par REGIME_CRISE_MULT_VOL.
    Probabiliste (et Historique sans historique) : z = sqrt(1-g) z_normal + sqrt(g) x
    REGIME_CRISE_MULT_VOL x z_crise, de covariance (1-g) C_normale + g C_crise majoree,
    melange de deux matrices definies positives, donc definie positive.
    """
    nb, pas, n = eps.shape
    majoration = _majoration_par_actif(cles)
    g = intensite[:, None, None]

    base = _base_bootstrap(rendements_historiques, cles) if "Historique" in modele else None
    if base is not None:
        stress = jours_de_stress(rendements_historiques)
        pool = base
        if stress is not None:
            jours = base[stress.reindex(base.index, fill_value=False).values]
            if len(jours) >= max(REGIME_CRISE_MIN_SEANCES, BOOTSTRAP_TAILLE_BLOC) \
                    and (jours.std().values > 0).all():
                pool = jours
        std = _centrer_reduire(pool)
        # Recoloration : les vrais jours de stress gardent leur forme (queues epaisses,
        # enchainements), mais leurs correlations sont amenees sur celles de crise.
        cible = np.linalg.cholesky(correlations_de_crise(cles, rendements_historiques))
        mesuree = np.linalg.cholesky(_rendre_definie_positive(np.atleast_2d(np.corrcoef(std.T))))
        std = std @ np.linalg.solve(mesuree.T, cible.T)
        crise = _tirer_blocs(std, nb, pas, rng) * majoration
        nb_blocs = -(-pas // BOOTSTRAP_TAILLE_BLOC)
        en_crise = rng.random((nb, nb_blocs)) < intensite[:, None]
        en_crise = np.repeat(en_crise, BOOTSTRAP_TAILLE_BLOC, axis=1)[:, :pas, None]
        return np.where(en_crise, crise, eps)

    cholesky = np.linalg.cholesky(correlations_de_crise(cles, rendements_historiques))
    z = rng.standard_normal((nb, pas, n)) @ cholesky.T
    if "Historique" in modele:
        z = _student(z, rng)
    return np.sqrt(1 - g) * eps + np.sqrt(g) * z * majoration


# === Trajectoires ============================================================


def _ajouter_taux_change(actifs, devises: Dict[str, str], actifs_extras
                         ) -> Tuple[Optional[List[str]], Optional[dict], List[str]]:
    """Ajoute aux actifs simules les taux de change techniques (livre, yen) dont
    les actifs a convertir ont besoin. Retourne aussi les taux a masquer ensuite."""
    if actifs is None or not devises:
        return actifs, actifs_extras, []
    actifs = list(actifs)
    extras = dict(actifs_extras or {})
    caches = []
    for actif, devise in devises.items():
        taux = TAUX_CHANGE_SIMULATION.get(devise)
        if (taux in TAUX_CHANGE_SECOURS and actif in actifs
                and taux not in actifs and taux not in caches):
            actifs.append(taux)
            caches.append(taux)
            extras.setdefault(taux, dict(TAUX_CHANGE_SECOURS[taux]))
    return actifs, extras, caches


def generer_chemins(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                    actifs=None, nb_simulations=1, prix_reels=None, vols_reelles=None,
                    actifs_extras=None, rendements_historiques=None,
                    actifs_en_usd=None, graine=None,
                    incertitude_ia=False, devises_actifs=None) -> Tuple[List[str], np.ndarray]:
    """
    Genere nb_simulations trajectoires de prix.

    Args:
        rendements_historiques: DataFrame de rendements quotidiens reels
            (colonnes = sim_keys) pour mesurer les correlations et alimenter
            le modele Historique. Optionnel.
        actifs_en_usd: actifs cotes en dollars a exprimer en euros via la
            trajectoire simulee de l'EUR/USD (qui doit faire partie des actifs).
        devises_actifs: {actif: devise} des actifs a convertir en euros ("USD",
            "GBP", "JPY"). Livre et yen sont simules comme taux techniques
            (EUR_GBP, EUR_JPY), retires du resultat.
        incertitude_ia: chaque trajectoire tire son choc dans la fourchette
            chocs_ia["fourchettes"] au lieu de prendre le choc central.

    Returns:
        (cles, chemins) avec chemins de forme (nb_simulations, jours, n_actifs).
    """
    rng = np.random.default_rng(graine)
    impacts = _normaliser_impacts(chocs_ia or {})
    devises = {k: "USD" for k in (actifs_en_usd or [])}
    devises.update(devises_actifs or {})
    actifs, actifs_extras, taux_caches = _ajouter_taux_change(actifs, devises, actifs_extras)
    cles, prix0, vols = _preparer_actifs(actifs, prix_reels, vols_reelles, actifs_extras)
    pas = max(int(jours) - 1, 1)
    n = len(cles)

    eps = _innovations(modele, cles, nb_simulations, pas, rendements_historiques, rng)

    cibles = np.array([impacts.get(k, 0.0) for k in cles])
    if incertitude_ia:
        bas, haut = _bornes_fourchette(chocs_ia, cles, cibles)
        if (haut > bas).any():
            cibles = tirer_chocs(bas, cibles, haut, nb_simulations, rng)
    cibles_2d = np.atleast_2d(cibles)

    if "Probabiliste" in modele or "Historique" in modele:
        # Le regime suit le choc S&P 500 de chaque trajectoire : un scenario qui
        # s'avere plus grave que prevu passe aussi en regime de crise.
        if REGIME_CRISE_ACTIF_REPERE in cles:
            choc_repere = cibles_2d[:, cles.index(REGIME_CRISE_ACTIF_REPERE)]
        else:
            choc_repere = np.array([impacts.get(REGIME_CRISE_ACTIF_REPERE, 0.0)])
        intensite = np.broadcast_to(intensite_crise(choc_repere), (nb_simulations,))
        if (intensite > 0).any():
            eps = _appliquer_regime_crise(modele, eps, np.array(intensite), cles,
                                          rendements_historiques, rng)

    # Derive en log telle que la trajectoire mediane atteigne le choc de l'IA
    log_cible = np.log1p(cibles_2d)
    derive = profil_choc(modele, pas, forme_du_choc(chocs_ia))[None, :, None] * log_cible[:, None, :]

    log_rendements = derive + eps * vols[None, None, :]
    log_rendements = np.maximum(log_rendements, np.log(1 - PERTE_MAX_QUOTIDIENNE))

    chemins = np.empty((nb_simulations, pas + 1, n))
    chemins[:, 0, :] = prix0
    chemins[:, 1:, :] = prix0 * np.exp(np.cumsum(log_rendements, axis=1))

    for k, devise in devises.items():
        taux = TAUX_CHANGE_SIMULATION.get(devise)
        if k in cles and taux in cles and k != taux:
            chemins[:, :, cles.index(k)] /= chemins[:, :, cles.index(taux)]

    if taux_caches:
        garder = [i for i, k in enumerate(cles) if k not in taux_caches]
        cles = [cles[i] for i in garder]
        chemins = chemins[:, :, garder]

    return cles, chemins


def simuler_marche_dynamique(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                             actifs=None, prix_reels=None, vols_reelles=None,
                             actifs_extras=None, rendements_historiques=None,
                             actifs_en_usd=None, graine=None,
                             devises_actifs=None) -> pd.DataFrame:
    """Une seule trajectoire : DataFrame (jours x actifs)."""
    cles, chemins = generer_chemins(
        chocs_ia, jours=jours, modele=modele, actifs=actifs, nb_simulations=1,
        prix_reels=prix_reels, vols_reelles=vols_reelles, actifs_extras=actifs_extras,
        rendements_historiques=rendements_historiques,
        actifs_en_usd=actifs_en_usd, graine=graine, devises_actifs=devises_actifs,
    )
    return pd.DataFrame(chemins[0], columns=cles)


def simuler_monte_carlo(chocs_ia, jours=100, modele="Probabiliste (Réaliste)",
                        actifs=None, nb_simulations=1000, prix_reels=None,
                        vols_reelles=None, actifs_extras=None,
                        rendements_historiques=None, actifs_en_usd=None,
                        graine=None, devises_actifs=None) -> dict:
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
        devises_actifs=devises_actifs,
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
