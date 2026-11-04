"""Fixtures partagees : modele de demonstration en memoire (sans serveur)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app

CONTRAT = ["OK", "RISQUE", "INDETERMINE"]

TEXTE_OK = "Stock suffisant et delai fournisseur court, sans rupture"
TEXTE_RISQUE = "Rupture de stock probable et delai fournisseur inconnu"

_RISQUE_KEYWORDS = (
    "rupture",
    "retard",
    "penurie",
    "penrie",
    "greve",
    "congestion",
    "defaillance",
    "saturation",
    "panne",
    "critique",
    "incertain",
    "inconnu",
    "insuffisant",
    "insuffisante",
    "risque",
    "fluctuation",
    "forte hausse",
    "casse",
    "injoignable",
)

_OK_KEYWORDS = (
    "suffisant",
    "fiable",
    "reguliere",
    "standard",
    "maitrise",
    "satisfait",
    "conforme",
    "rapide",
    "parfait",
    "soigne",
    "recommande",
    "avance",
    "eleve",
    "stable",
    "disponible",
    "planifie",
    "court",
    "anticipee",
)


class FauxModele:
    """Classifieur deterministe pour les tests (pas de modele a charger).

    Heuristique simple sur mots-cles, avec abstention sous seuil quand le
    texte ne contient aucun mot-cle : deterministe et reproductible.
    """

    model_name = "faux-modele (test)"

    def __init__(self, seuil: float = 0.60) -> None:
        self.seuil = seuil

    def predict(self, text: str) -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("texte vide une fois les blancs retires")
        t = text.lower()
        # Negations courtes : "sans retard", "sans tension", "without" esclent les risques.
        # Petite liste ferme, deterministe, documentee : le faux modele ne pretends pas etre le modele.
        negatives = ("sans ",)
        # compte les mots-cles, en ignorants une occurrence precedee de "sans "
        def compter(mots: tuple[str, ...]) -> int:
            n = 0
            for m in mots:
                idx = 0
                while True:
                    pos = t.find(m, idx)
                    if pos == -1:
                        break
                    # "sans retard" -> ne compte pas "retard"
                    fenetre = t[max(0, pos - 6):pos]
                    if not any(fenetre.endswith(neg) for neg in negatives):
                        n += 1
                    idx = pos + len(m)
            return n

        score_risque = compter(_RISQUE_KEYWORDS)
        score_ok = compter(_OK_KEYWORDS)
        if score_risque == 0 and score_ok == 0:
            return {"label": "INDETERMINE", "score": 0.55, "text": text}
        total = score_risque + score_ok
        part_risque = score_risque / total
        label = "RISQUE" if part_risque >= 0.5 else "OK"
        score = 0.80 + 0.10 * abs(part_risque - 0.5) * 2
        if score < self.seuil:
            label = "INDETERMINE"
        return {"label": label, "score": round(score, 4), "text": text}


@pytest.fixture
def faux_modele() -> FauxModele:
    return FauxModele()


@pytest.fixture
def client(faux_modele) -> TestClient:
    """API en memoire avec le faux modele dans app.state (sans serveur)."""
    app.state.classifier = faux_modele
    with TestClient(app) as c:
        yield c


@pytest.fixture
def client_reel():
    """API avec le vrai pipeline si le modele existe, sinon marquee skip."""

    from supply_app.predict import chemin_modele, load_model

    if not chemin_modele().exists():
        pytest.skip("modele absent : lancez `python src/train.py`")
    app.state.classifier = load_model()
    with TestClient(app) as c:
        yield c
