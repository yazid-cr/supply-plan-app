"""Couche modele (TP2) : chargement du pipeline et prediction.

Le pipeline TF-IDF + regression logistique est sauvegarde d'un bloc
(models/supply.joblib) : meme transformation a l'entrainement et en
production. Ce module ne connait ni l'API ni l'interface.
"""
from __future__ import annotations

import os
from pathlib import Path

import joblib

SEUIL_CONFIANCE = 0.60
MODEL_NAME = "tfidf-logreg (TP2, models/supply.joblib)"


def chemin_modele() -> Path:
    """Chemin du modele : variable SUPPLY_MODELE, sinon models/supply.joblib."""
    env = os.environ.get("SUPPLY_MODELE")
    if env:
        return Path(env)
    # racine du depot (parent de supply_app/) puis dossier courant
    candidats = [
        Path(__file__).resolve().parent.parent / "models" / "supply.joblib",
        Path.cwd() / "models" / "supply.joblib",
    ]
    for candidat in candidats:
        if candidat.exists():
            return candidat
    return candidats[0]


class Classifieur:
    """Enveloppe du pipeline : predict(texte) -> {label, score, text}."""

    def __init__(self, pipeline, model_name: str = MODEL_NAME) -> None:
        self.pipeline = pipeline
        self.model_name = model_name

    def predict(self, text: str) -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("texte vide une fois les blancs retires")
        proba = list(self.pipeline.predict_proba([text])[0])
        classes = list(self.pipeline.classes_)
        idx = max(range(len(proba)), key=lambda i: proba[i])
        label_brut = str(classes[idx]).upper()
        score = float(proba[idx])
        # Seuil d'abstention (TP4) : sous 0,60 on ne tranche pas.
        label = label_brut if score >= SEUIL_CONFIANCE else "INDETERMINE"
        return {"label": label, "score": score, "text": text}


def load_model(path: str | Path | None = None) -> Classifieur:
    """Charge le pipeline. Leve FileNotFoundError si le modele est absent."""
    chemin = Path(path) if path else chemin_modele()
    if not chemin.exists():
        raise FileNotFoundError(
            f"modele introuvable : {chemin} — lancez d'abord "
            f"`python src/train.py` ou indiquez son chemin dans "
            f"la variable SUPPLY_MODELE"
        )
    pipeline = joblib.load(chemin)
    return Classifieur(pipeline)
