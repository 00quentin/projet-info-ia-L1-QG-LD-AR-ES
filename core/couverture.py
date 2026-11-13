"""
core/couverture.py
==================
« Comment protéger mon portefeuille ? » : cherche une répartition plus
résistante au scénario simulé, puis compare avant / après sur les mêmes
trajectoires. Calcul pur (numpy), sans réseau ni IA.

Méthode :
1. Trajectoires : le moteur (simulation.py) tire des trajectoires de prix
   autour des chocs que l'IA a estimés pour CE scénario, avec les vraies
   volatilités et corrélations. On travaille sur les prix relatifs (1 au jour 0).
2. Contraintes : pourcentages entiers de somme 100, aucune ligne au-dessus de
   40 %, chaque ligne bouge d'au plus 15 points, au plus 30 % du portefeuille
   change de main, seulement les actifs déjà sélectionnés (les seuls dont
   l'IA a estimé le choc). Un actif personnalisé peut être allégé, jamais renforcé.
3. Recherche (descente pas à pas) : à chaque étape on essaie TOUS les
   transferts de 5 points d'un actif vers un autre et on garde le plus utile,
   au sens du score de risque (plus bas = mieux) :
       score = perte maximale / perte maximale initiale
             + probabilité de perte / max(probabilité initiale, 5 %)
   (chaque terme vaut 1 pour le portefeuille de départ). On s'arrête quand
   plus aucun transfert ne gagne au moins 1 % de score.
4. Vérification : l'appelant ré-évalue avant et après sur d'AUTRES
   trajectoires que celles de la recherche (`comparer_portefeuilles`), pour
   ne pas surestimer le gain par sur-apprentissage.
"""

from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

from core.metrics import bandes_portefeuille_monte_carlo, calculer_metriques_monte_carlo

from config import (
    COUVERTURE_POIDS_MAX_LIGNE, COUVERTURE_ECART_MAX_LIGNE, COUVERTURE_ROTATION_MAX, COUVERTURE_PAS_TRANSFERT, COUVERTURE_ETAPES_MAX, COUVERTURE_GAIN_MIN_RELATIF, COUVERTURE_PLANCHER_PROBA_PERTE, COUVERTURE_PLANCHER_PERTE_MAX, COUVERTURE_NB_TRAJECTOIRES_RECHERCHE, COUVERTURE_NB_TRAJECTOIRES_EVALUATION, COUVERTURE_GRAINE, COUVERTURE_TAILLE_LOT, JOURS_PAR_AN,
)


# === Répartitions entières ==================================================


def arrondir_pourcentages(poids: Dict[str, float]) -> Dict[str, int]:
    """Poids positifs (somme quelconque) -> pourcentages entiers de somme 100.

    Méthode des plus forts restes : l'écart à la valeur exacte reste < 1 point.
    """
    cles = list(poids)
    valeurs = np.array([max(0.0, float(poids[k])) for k in cles])
    total = valeurs.sum()
    if not cles or total <= 0:
        return {k: 0 for k in cles}
    exacts = valeurs / total * 100
    entiers = np.floor(exacts).astype(int)
    restes = exacts - entiers
    for i in np.argsort(-restes, kind="stable")[: 100 - int(entiers.sum())]:
        entiers[i] += 1
    return {k: int(v) for k, v in zip(cles, entiers)}


def bornes_lignes(initial: np.ndarray, figes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Bornes basse/haute (points entiers) de chaque ligne.

    Si l'écart maximal par ligne ne permet pas d'atteindre 100 % sous le
    plafond (ex : 100 % sur un seul actif), il est levé pour les lignes à renforcer.
    """
    bas = np.maximum(0, initial - COUVERTURE_ECART_MAX_LIGNE)
    haut = np.minimum(COUVERTURE_POIDS_MAX_LIGNE, initial + COUVERTURE_ECART_MAX_LIGNE)
    haut = np.where(figes, np.minimum(haut, initial), haut)
    if haut.sum() < 100:
        haut = np.where(figes, np.minimum(COUVERTURE_POIDS_MAX_LIGNE, initial), COUVERTURE_POIDS_MAX_LIGNE)
    return np.minimum(bas, haut), haut


def rotation(poids: np.ndarray, initial: np.ndarray) -> float:
    """Part du portefeuille (en points) qui change de main : moitié des écarts absolus."""
    return float(np.abs(poids - initial).sum() / 2)


# === Mesure du risque de nombreux portefeuilles à la fois ===================


def prix_relatifs(chemins: np.ndarray) -> np.ndarray:
    """Trajectoires de prix (n_traj, jours, n_actifs) ramenées à 1 au jour 0."""
    chemins = np.asarray(chemins, dtype=float)
    return chemins / chemins[:, :1, :]


def mesurer_risque(relatifs: np.ndarray, poids: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Perte maximale médiane et probabilité de perte (en %) de K portefeuilles.

    Args:
        relatifs: prix relatifs (n_traj, jours, n_actifs).
        poids: (K, n_actifs), chaque ligne de somme 1.

    Returns:
        (perte_max, proba_perte), deux tableaux de longueur K.
    """
    poids = np.atleast_2d(np.asarray(poids, dtype=float))
    perte_max = np.empty(len(poids))
    proba = np.empty(len(poids))
    for debut in range(0, len(poids), COUVERTURE_TAILLE_LOT):
        lot = poids[debut:debut + COUVERTURE_TAILLE_LOT]
        valeurs = np.tensordot(relatifs, lot.T, axes=([2], [0]))  # (n_traj, jours, k)
        plus_hauts = np.maximum.accumulate(valeurs, axis=1)
        chutes = ((plus_hauts - valeurs) / plus_hauts).max(axis=1)
        perte_max[debut:debut + len(lot)] = np.median(chutes, axis=0) * 100
        proba[debut:debut + len(lot)] = (valeurs[:, -1, :] < 1).mean(axis=0) * 100
    return perte_max, proba


def score_risque(perte_max, proba_perte, perte_max_ref: float, proba_ref: float):
    """Score à minimiser : chaque terme vaut 1 pour le portefeuille de référence."""
    return (np.asarray(perte_max) / max(perte_max_ref, COUVERTURE_PLANCHER_PERTE_MAX)
            + np.asarray(proba_perte) / max(proba_ref, COUVERTURE_PLANCHER_PROBA_PERTE))


# === Recherche ==============================================================


def _transferts(poids: np.ndarray, bas: np.ndarray, haut: np.ndarray,
                initial: np.ndarray, rotation_max: float,
                source: Optional[int] = None, montant_max: int = COUVERTURE_PAS_TRANSFERT
                ) -> List[np.ndarray]:
    """Répartitions voisines : `montant_max` points (ou moins, en butée) d'un actif vers un autre."""
    voisins = []
    n = len(poids)
    for i in range(n) if source is None else [source]:
        for j in range(n):
            if i == j:
                continue
            montant = min(montant_max, poids[i] - bas[i], haut[j] - poids[j])
            if montant < 1:
                continue
            voisin = poids.copy()
            voisin[i] -= montant
            voisin[j] += montant
            if source is None and rotation(voisin, initial) > rotation_max:
                continue
            voisins.append(voisin)
    return voisins


def proposer_couverture(
    relatifs: np.ndarray,
    cles: List[str],
    poids_initiaux: Dict[str, float],
    cles_figees: Iterable[str] = (),
) -> Tuple[Optional[Dict], Optional[str]]:
    """Cherche une répartition plus résistante au scénario (voir l'en-tête du module).

    Args:
        relatifs: prix relatifs des actifs `cles`, (n_traj, jours, n_actifs).
        cles: actifs autorisés (ceux du portefeuille et de la sélection).
        poids_initiaux: {cle: poids} du portefeuille actuel (somme quelconque > 0).
        cles_figees: actifs qu'on peut alléger mais pas renforcer (actifs personnalisés).

    Returns:
        (resultat, None) ou (None, message d'erreur). resultat contient :
        initial_pct et propose_pct ({cle: % entier}), score_initial, score_propose,
        nb_etapes, nb_portefeuilles_testes, rotation_pct, plafond_impose (bool).
    """
    n = len(cles)
    if n * COUVERTURE_POIDS_MAX_LIGNE < 100:
        return None, (f"Il faut au moins {-(-100 // COUVERTURE_POIDS_MAX_LIGNE)} actifs sélectionnés pour "
                      f"répartir le risque (aucune ligne ne dépasse {COUVERTURE_POIDS_MAX_LIGNE} %).")
    if relatifs.shape[2] != n:
        return None, "Trajectoires et actifs ne correspondent pas."

    exacts = np.array([max(0.0, float(poids_initiaux.get(k, 0.0))) for k in cles])
    if exacts.sum() <= 0:
        return None, "Le portefeuille de départ est vide."
    exacts = exacts / exacts.sum()
    initial_pct = arrondir_pourcentages(dict(zip(cles, exacts)))
    initial = np.array([initial_pct[k] for k in cles])
    figees = set(cles_figees)
    figes = np.array([k in figees for k in cles])
    bas, haut = bornes_lignes(initial, figes)
    if haut.sum() < 100:
        return None, ("Pas assez d'actifs du catalogue pour répartir le risque : ajoutez par exemple "
                      "des obligations ou de l'or à votre sélection.")

    perte_ref, proba_ref = (float(x[0]) for x in mesurer_risque(relatifs, exacts[None, :]))

    def scores(candidats: List[np.ndarray]) -> np.ndarray:
        perte, proba = mesurer_risque(relatifs, np.array(candidats) / 100)
        return score_risque(perte, proba, perte_ref, proba_ref)

    poids = initial.copy()
    nb_testes = 0

    # 1) Lignes au-dessus du plafond : elles doivent baisser ; le surplus va
    #    là où il réduit le plus le risque.
    plafond_impose = bool((poids > haut).any())
    while (poids > haut).any():
        source = int(np.argmax(poids - haut))
        voisins = _transferts(poids, bas, haut, initial, np.inf, source=source,
                              montant_max=min(COUVERTURE_PAS_TRANSFERT, int(poids[source] - haut[source])))
        if not voisins:
            return None, "Impossible de respecter le plafond par ligne avec ces actifs."
        s = scores(voisins)
        nb_testes += len(voisins)
        poids = voisins[int(np.argmin(s))]

    # 2) Transferts volontaires, tant qu'ils réduisent nettement le risque.
    rotation_max = max(COUVERTURE_ROTATION_MAX, rotation(poids, initial))
    score_courant = float(scores([poids])[0])
    nb_etapes = 0
    for _ in range(COUVERTURE_ETAPES_MAX):
        voisins = _transferts(poids, bas, haut, initial, rotation_max)
        if not voisins:
            break
        s = scores(voisins)
        nb_testes += len(voisins)
        meilleur = int(np.argmin(s))
        if s[meilleur] > score_courant * (1 - COUVERTURE_GAIN_MIN_RELATIF):
            break
        poids, score_courant = voisins[meilleur], float(s[meilleur])
        nb_etapes += 1

    return {
        "initial_pct": initial_pct,
        "propose_pct": {k: int(v) for k, v in zip(cles, poids)},
        "score_initial": float(score_risque(perte_ref, proba_ref, perte_ref, proba_ref)),
        "score_propose": score_courant,
        "nb_etapes": nb_etapes,
        "nb_portefeuilles_testes": nb_testes,
        "rotation_pct": rotation(poids, initial),
        "plafond_impose": plafond_impose,
    }, None


# === Comparaison avant / après ==============================================


def comparer_portefeuilles(
    chemins: np.ndarray,
    colonnes: List[str],
    poids_avant: Dict[str, float],
    poids_apres: Dict[str, float],
    capital: float,
    taux_sans_risque: float,
) -> Dict[str, Dict]:
    """Métriques et trajectoire médiane (avec fourchette 5 %-95 %) des deux
    portefeuilles, calculées sur les mêmes trajectoires : la comparaison est équitable."""
    sortie = {}
    for nom, poids in (("avant", poids_avant), ("apres", poids_apres)):
        poids = {k: v for k, v in poids.items() if v > 0}
        metriques = calculer_metriques_monte_carlo(chemins, colonnes, poids, capital, taux_sans_risque)
        bandes = bandes_portefeuille_monte_carlo(chemins, colonnes, poids, capital)
        sortie[nom] = {"metriques": metriques, "bandes": bandes}
    return sortie


def score_comparaison(avant: Dict[str, float], apres: Dict[str, float]) -> Tuple[float, float]:
    """Score de risque (même formule que la recherche) d'après les métriques des deux portefeuilles."""
    ref = (avant["max_dd"], avant["proba_perte"])
    return (float(score_risque(avant["max_dd"], avant["proba_perte"], *ref)),
            float(score_risque(apres["max_dd"], apres["proba_perte"], *ref)))


def faits_par_actif(relatifs: np.ndarray, cles: List[str],
                    poids_initiaux: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    """Volatilité annualisée (%) de chaque actif et sa corrélation avec le
    portefeuille de départ, mesurées sur les trajectoires du scénario."""
    rendements = relatifs[:, 1:, :] / relatifs[:, :-1, :] - 1
    w = np.array([max(0.0, float(poids_initiaux.get(k, 0.0))) for k in cles])
    w = w / w.sum() if w.sum() > 0 else np.full(len(cles), 1 / len(cles))
    valeurs = relatifs @ w
    rend_pf = (valeurs[:, 1:] / valeurs[:, :-1] - 1).ravel()
    faits = {}
    for i, cle in enumerate(cles):
        r = rendements[:, :, i].ravel()
        vol = float(r.std() * np.sqrt(JOURS_PAR_AN) * 100)
        correlation = float(np.corrcoef(r, rend_pf)[0, 1]) if r.std() > 0 and rend_pf.std() > 0 else 0.0
        faits[cle] = {"volatilite_pct": vol, "correlation": correlation}
    return faits


def lister_changements(initial_pct: Dict[str, int], propose_pct: Dict[str, int]) -> List[Dict]:
    """Lignes dont le poids change, de la plus forte variation à la plus faible."""
    lignes = [
        {"cle": k, "avant_pct": initial_pct.get(k, 0), "apres_pct": propose_pct.get(k, 0),
         "ecart_pct": propose_pct.get(k, 0) - initial_pct.get(k, 0)}
        for k in dict.fromkeys([*initial_pct, *propose_pct])
    ]
    lignes = [l for l in lignes if l["ecart_pct"] != 0]
    return sorted(lignes, key=lambda l: (-abs(l["ecart_pct"]), -l["ecart_pct"]))


def _pct(valeur: float) -> str:
    """Pourcentage signé à la française : +14 %, −8,5 %, +7 % (une décimale sous 10 %)."""
    signe = "+" if valeur > 0 else "−" if valeur < 0 else ""
    texte = f"{abs(valeur):.{0 if abs(valeur) >= 10 else 1}f}".removesuffix(".0").replace(".", ",")
    return f"{signe}{texte} %"


def justification_par_defaut(ecart_pct: int, choc_pct: float, volatilite_pct: float,
                             correlation: float, plafond: bool = False) -> str:
    """Phrase de secours (sans IA) qui explique un changement de poids à partir des chiffres."""
    choc = _pct(choc_pct)
    if ecart_pct < 0 and plafond:
        return (f"Ramené sous le plafond de {COUVERTURE_POIDS_MAX_LIGNE} % : une ligne trop lourde "
                "concentre le risque du portefeuille.")
    if ecart_pct > 0:
        if choc_pct > 1:
            debut = f"Progresse dans ce scénario (choc estimé {choc})"
        elif choc_pct > -3:
            debut = f"Bouge peu dans ce scénario (choc estimé {choc})"
        else:
            debut = f"Recule moins que les actifs allégés (choc estimé {choc})"
        if correlation < -0.2:
            return f"{debut} et évolue souvent à l'inverse du reste du portefeuille : il amortit les chutes."
        if correlation < 0.3:
            return f"{debut} et suit peu le reste du portefeuille : il amortit les chutes."
        if volatilite_pct < 10:
            return f"{debut}, avec une volatilité faible ({volatilite_pct:.0f} %/an) : il stabilise le portefeuille."
        return f"{debut} : il compense une partie des pertes des autres lignes."
    if choc_pct < -3:
        return f"Très exposé à ce scénario (choc estimé {choc}) : alléger sa part limite la perte."
    if volatilite_pct > 30:
        return f"Très volatil ({volatilite_pct:.0f} %/an) : alléger sa part réduit les chutes en cours de route."
    return "Sa part est réduite au profit d'actifs plus résistants à ce scénario."
