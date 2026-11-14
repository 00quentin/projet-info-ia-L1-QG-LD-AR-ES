"""
api/actualite.py
================
GET /api/actualite : scénario neutre condensé depuis les gros titres du jour.
Ne lève jamais d'exception : en cas de souci, `disponible` vaut False + un message.
"""

import ia_actualite
from logger import get_logger

log = get_logger("api.actualite")


def lire_actualite() -> dict:
    jour = ia_actualite.jour_utc()
    base = {"disponible": False, "scenario": None, "themes": [], "date": jour,
            "sources": [], "message": None}
    try:
        titres, sources = ia_actualite.titres_du_jour(jour)
        if not titres:
            base["message"] = "Actualité indisponible pour le moment. Décrivez votre scénario vous-même."
            return base
        res = ia_actualite.condenser_en_scenario(titres, jour)
        if not isinstance(res, dict) or "texte" not in res:
            base["message"] = "Le résumé de l'actualité n'a pas pu être généré. Réessayez plus tard."
            return base
        base.update(disponible=True, scenario=res["texte"], themes=res.get("themes", []),
                    sources=list(sources))
        return base
    except Exception:
        log.error("Échec lecture actualité", exc_info=True)
        base["message"] = "Actualité indisponible pour le moment."
        return base
