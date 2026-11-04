"""Client HTTP de l'API (TP5).

La page ne parle qu'a l'API : jamais a predict(), jamais au fichier
.joblib. Le client renvoie toujours une Reponse, jamais une exception.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

REFUS = ("Texte refuse : vide, fait d'espaces, ou de plus de 2000 caracteres.")
SANS_MODELE = ("Modele non charge : lancez `python src/train.py`, puis relancez l'API.")
INJOIGNABLE = ("API injoignable : lancez d'abord `uvicorn api.main:app`")


@dataclass
class Reponse:
    ok: bool
    label: str | None = None
    score: float | None = None
    message: str | None = None


def creer_session(base_url: str = API_URL) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=10.0)


def predire(session, texte: str) -> Reponse:
    """POST /predict et traduction du code en message afficheur."""
    try:
        r = session.post("/predict", json={"text": texte})
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if r.status_code == 200:
        corps = r.json()
        return Reponse(True, label=corps["label"], score=corps["score"])
    if r.status_code == 422:
        return Reponse(False, message=REFUS)
    if r.status_code == 503:
        return Reponse(False, message=SANS_MODELE)
    return Reponse(
        False,
        message=f"Erreur inattendue de l'API (code {r.status_code}).",
    )
