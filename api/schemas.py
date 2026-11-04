"""Contrats Pydantic (TP3) : valides avant l'execution du code.

Un texte fait uniquement de blancs est refuse ici (TP4) avec la meme
regle que predict() : un seul refus, une seule forme de 422 (liste).
"""
from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def refuser_texte_blanc(cls, valeur: str) -> str:
        if not valeur.strip():
            raise ValueError("texte vide une fois les blancs retires")
        return valeur


class PredictResponse(BaseModel):
    label: str
    score: float = Field(..., ge=0, le=1)
    text: str


class HealthResponse(BaseModel):
    status: str
    model: str
