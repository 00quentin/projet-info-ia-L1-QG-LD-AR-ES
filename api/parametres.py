"""
api/parametres.py
=================
Constantes du moteur affichées sur la page Méthodologie, lues à la source
(config.py, schemas.py, market_data.py) avec les mêmes noms que donnees.ts.
"""

import inspect

from annotated_types import Ge, Le

import config
import market_data
import schemas


def _pct(x: float) -> float:
    return x * 100


def _bornes_champ(champ: str) -> tuple:
    meta = schemas.ChocsMacro.model_fields[champ].metadata
    return next(m.ge for m in meta if isinstance(m, Ge)), next(m.le for m in meta if isinstance(m, Le))


def lire_parametres() -> dict:
    jours_vol = inspect.signature(market_data.get_volatilites_historiques).parameters["jours"].default
    parametres = {
        "nbSimulations": config.NB_SIMULATIONS_MONTE_CARLO,
        "cheminsConserves": config.NB_CHEMINS_CONSERVES,
        "joursVolatilite": jours_vol,
        "anneesCorrelation": config.FENETRE_CALIBRATION_JOURS / 365,
        "perteMaxQuotidiennePct": _pct(config.PERTE_MAX_QUOTIDIENNE),
        "horizonMin": config.HORIZON_MIN,
        "horizonMax": config.HORIZON_MAX,
        "horizonDefaut": config.HORIZON_DEFAUT,
        "tauxSansRisqueSecoursPct": _pct(config.TAUX_SANS_RISQUE_ANNUEL),
        "blocBootstrapSeances": config.BOOTSTRAP_TAILLE_BLOC,
        "minSeancesBootstrap": config.BOOTSTRAP_MIN_SEANCES,
        "studentDegresLiberte": config.STUDENT_DEGRES_LIBERTE,
        "autocorrelation": config.MOMENTUM_AUTOCORRELATION,
        "accelerationPct": _pct(config.MOMENTUM_ACCELERATION),
        "criseCreuxPctHorizon": _pct(config.CRISE_FRACTION_CREUX),
        "criseDepassementPct": _pct(config.CRISE_DEPASSEMENT),
        "incertitudePartCommunePct": _pct(config.INCERTITUDE_IA_CORRELATION),
        "fourchetteAggravation": config.FOURCHETTE_ELARGISSEMENT_AGGRAVATION,
        "fourchetteAttenuation": config.FOURCHETTE_ELARGISSEMENT_ATTENUATION,
        "fourchetteDemiLargeurMinPct": _pct(config.FOURCHETTE_DEMI_LARGEUR_MIN),
    }
    return {
        "parametres": parametres,
        "bornes_autres": {
            "inflationPoints": list(_bornes_champ("inflation")),
            "tauxDirecteursPoints": list(_bornes_champ("taux_directeurs")),
            "actifPersoPct": [_pct(x) for x in schemas._BORNE_GENERIQUE_CUSTOM],
        },
        "bornes_ia": {actif: list(b) for actif, b in schemas.BORNES_ACTIFS.items()},
        "modeles_ia": {
            "modeleIa": config.IA_ANALYSE["model"],
            "modeleIaSecours": config.IA_ANALYSE_SECOURS["model"],
        },
    }
