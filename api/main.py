"""
api/main.py
===========
API web de Quant Terminal (FastAPI) : le moteur Python expose au site Next.js.

Lancer en local :  uvicorn api.main:app --reload --port 8000
Documentation interactive : http://localhost:8000/docs
"""

import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from api import services
from api.limites import LimiteurAppels
from api.modeles import DemandeBacktest, DemandeChat, DemandeRapport, DemandeSimulation
from config import (
    API_FENETRE_LIMITE_SECONDES, API_LIMITE_APPELS_DONNEES, API_LIMITE_APPELS_IA,
    API_ORIGINES_PAR_DEFAUT,
)
from logger import get_logger

log = get_logger("api")

app = FastAPI(
    title="Quant Terminal API",
    description="Simulation de portefeuille, backtests, prix de marché et analyste IA.",
    version="3.0.0",
)

# Sites autorises a appeler l'API depuis un navigateur. En production :
# QT_ORIGINES_AUTORISEES="https://mon-site.vercel.app,https://autre-domaine.fr"
_origines = [o.strip() for o in os.getenv("QT_ORIGINES_AUTORISEES", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origines or API_ORIGINES_PAR_DEFAUT,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

limiteur_ia = LimiteurAppels(API_LIMITE_APPELS_IA, API_FENETRE_LIMITE_SECONDES)
limiteur_donnees = LimiteurAppels(API_LIMITE_APPELS_DONNEES, API_FENETRE_LIMITE_SECONDES)


def _adresse_client(request: Request) -> str:
    """Adresse du visiteur. Derriere un hebergeur (Render), la vraie adresse est
    la derniere ajoutee a X-Forwarded-For par son proxy : les precedentes sont
    fournies par le client et donc falsifiables."""
    transmis = request.headers.get("x-forwarded-for")
    if transmis:
        return transmis.split(",")[-1].strip()
    return request.client.host if request.client else "inconnu"


def _limiter(limiteur: LimiteurAppels):
    def verifier(request: Request) -> None:
        if not limiteur.autoriser(_adresse_client(request)):
            raise HTTPException(
                status_code=429,
                detail="Trop de demandes en peu de temps. Patientez une minute puis réessayez.",
            )
    return verifier


limite_ia = Depends(_limiter(limiteur_ia))
limite_donnees = Depends(_limiter(limiteur_donnees))


@app.exception_handler(services.DemandeInvalide)
def _demande_invalide(_: Request, exc: services.DemandeInvalide) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(services.ServiceIndisponible)
def _service_indisponible(_: Request, exc: services.ServiceIndisponible) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(Exception)
def _erreur_inattendue(_: Request, exc: Exception) -> JSONResponse:
    # Le detail technique reste dans les logs : on ne l'expose pas au visiteur.
    log.error("Erreur inattendue : %s", exc, exc_info=True)
    return JSONResponse(status_code=500,
                        content={"detail": "Erreur interne. Réessayez dans un instant."})


@app.get("/api/sante", tags=["Technique"])
def sante() -> dict:
    """Verifie que l'API repond (sert aussi a la reveiller)."""
    return {"statut": "ok"}


@app.get("/api/catalogue", tags=["Données"], dependencies=[limite_donnees])
def lire_catalogue() -> dict:
    """Actifs, profils, scénarios rapides, événements historiques, bornes."""
    return services.catalogue()


@app.get("/api/marches", tags=["Données"], dependencies=[limite_donnees])
def lire_marches(rafraichir: bool = False) -> dict:
    """Dernière clôture de chaque actif, avec sa source et sa date.

    `rafraichir=true` recharge les prix depuis Yahoo (au plus une fois toutes les 5 minutes).
    """
    return services.marches(rafraichir)


@app.get("/api/conjoncture", tags=["Données"], dependencies=[limite_donnees])
def lire_conjoncture() -> dict:
    """Taux directeurs, taux à 10 ans et inflation du moment (FRED), taux sans risque du Sharpe."""
    return services.conjoncture()


@app.get("/api/actifs-perso/{ticker}", tags=["Données"], dependencies=[limite_donnees])
def lire_actif_perso(ticker: str) -> dict:
    """Valide un ticker Yahoo Finance (ex : TSLA) et renvoie son prix et sa volatilité."""
    return services.actif_perso(ticker)


@app.post("/api/simulations", tags=["Simulation"], dependencies=[limite_ia])
def creer_simulation(demande: DemandeSimulation) -> dict:
    """Simule l'impact de 1 à 3 scénarios sur un portefeuille."""
    return services.executer_simulation(demande)


@app.post("/api/backtests", tags=["Simulation"], dependencies=[limite_donnees])
def creer_backtest(demande: DemandeBacktest) -> dict:
    """Rejoue un portefeuille sur une vraie période passée."""
    return services.executer_backtest(demande)


@app.post("/api/chat", tags=["IA"], dependencies=[limite_ia])
def discuter(demande: DemandeChat) -> dict:
    """Pose une question à l'analyste IA."""
    reponse = services.repondre_chat([m.model_dump() for m in demande.messages], demande.contexte)
    return {"reponse": reponse}


@app.post("/api/rapports/pdf", tags=["IA"], dependencies=[limite_ia])
def creer_rapport(demande: DemandeRapport) -> Response:
    """Génère le rapport PDF d'un résultat affiché."""
    pdf = services.generer_pdf(demande)
    return Response(
        content=pdf, media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="rapport-quant-terminal.pdf"'},
    )


# === Validation historique de l'IA ==========================================
# Ajoute en fin de fichier pour rester independant des autres routes.
from api.validation import resultats_validation  # noqa: E402


@app.get("/api/validation-ia", tags=["Données"], dependencies=[limite_donnees])
def lire_validation_ia() -> dict:
    """L'IA à l'épreuve de l'histoire : estimations de l'IA face aux vraies crises passées
    (calculées une fois par scripts/valider_ia_historique.py, aucun appel IA ici)."""
    return resultats_validation()
