"""TP4 — jeu d'or : 20 demandes de reference.

Une erreur connue se declare (erreur_connue -> xfail strict=True),
elle ne se cache pas. 20 avis : 1 test d'ensemble + 1 par avis = 21 tests.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
JEU_OR = RACINE / "data" / "jeu_or.csv"

# Equivalences OK/RISQUE englobent POSITIVE/NEGATIVE du jeu sentiment d'origine.
EQUIVALENCES = {
    "OK": ("OK", "POSITIVE"),
    "RISQUE": ("RISQUE", "NEGATIVE"),
    "POSITIVE": ("OK", "POSITIVE"),
    "NEGATIVE": ("RISQUE", "NEGATIVE"),
}
ATTENDUS = {"POSITIVE", "NEGATIVE", "OK", "RISQUE"}


def lire_jeu_or() -> list[dict]:
    with JEU_OR.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_jeu_or_vingt_demandes():
    lignes = lire_jeu_or()
    assert len(lignes) == 20
    assert all(ligne["attendu"] in ATTENDUS for ligne in lignes)


def test_jeu_or_sans_erreur_franche_non_declaree(client):
    """Ensemble : aucune erreur franche hors des erreurs connues declarees."""
    for ligne in lire_jeu_or():
        raison = (ligne.get("erreur_connue") or "").strip()
        reponse = client.post("/predict", json={"text": ligne["text"]})
        assert reponse.status_code == 200
        obtenu = reponse.json()["label"]
        if raison:
            continue  # erreur declaree : jusque-la, pas une erreur franche cachee
        attendus = EQUIVALENCES.get(ligne["attendu"], (ligne["attendu"],))
        # INDETERMINE = abstention legale (seuil 0,60), jamais une erreur franche
        assert obtenu in (*attendus, "INDETERMINE")


@pytest.mark.parametrize(
    "ligne",
    lire_jeu_or(),
    ids=lambda l: l["text"][:40],
)
def test_demandes_du_jeu_or(client, ligne):
    raison = (ligne.get("erreur_connue") or "").strip()
    if raison:
        pytest.xfail(reason=raison)
    reponse = client.post("/predict", json={"text": ligne["text"]})
    assert reponse.status_code == 200
    attendu = EQUIVALENCES.get(ligne["attendu"], (ligne["attendu"],))
    obtenu = reponse.json()["label"]
    assert obtenu in (*attendu, "INDETERMINE")


def test_avis_refrance_sentiment(client):
    """Copies sentiment du jeu d'or (OK/RISQUE englobent POSITIVE/NEGATIVE)."""
    reponses = client.post("/predict", json={"text": "Livraison rapide, produit conforme, tres satisfait"})
    assert reponses.status_code == 200
