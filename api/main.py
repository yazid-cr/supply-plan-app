"""API FastAPI (TP3) : le modele est charge une fois, via lifespan."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from api.model import load_model
from api.schemas import HealthResponse, PredictRequest, PredictResponse

logger = logging.getLogger("supply-plan-api")


def _classifier(request: Request):
    clf = getattr(request.app.state, "classifier", None)
    if clf is None:
        raise HTTPException(status_code=503, detail="modele non charge")
    return clf


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Charge le modele une seule fois, avant la premiere requete.

    Si un classifieur de test a ete installe avant le demarrage, on le
    conserve : les tests remplacent le modele par un faux modele.
    """
    logger.info("Demarrage de l'API...")
    if getattr(app.state, "classifier", None) is None:
        app.state.classifier = load_model()
    logger.info("Modele charge avec succes : %s", app.state.classifier.model_name)
    yield
    logger.info("Arret de l'API")


app = FastAPI(
    title="Supply Plan Agent API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", summary="Accueil")
def accueil() -> dict:
    return {
        "service": "Agent de planification de la chaine d'approvisionnement",
        "routes": ["/health", "/predict", "/docs"],
    }


@app.get("/health", response_model=HealthResponse, summary="Sante de l'API")
def health(request: Request) -> HealthResponse:
    clf = _classifier(request)
    return HealthResponse(status="OK", model=clf.model_name)


@app.post("/predict", response_model=PredictResponse, summary="Classer une demande")
async def predict(request: PredictRequest, req: Request) -> dict:
    clf = _classifier(req)
    try:
        result = clf.predict(request.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception:
        logger.exception("Erreur lors de la prediction")
        raise HTTPException(
            status_code=500, detail="Erreur interne du serveur"
        ) from None
    logger.info(
        "predict: %r -> %s (%.2f)",
        request.text[:50],
        result["label"],
        result["score"],
    )
    return result
