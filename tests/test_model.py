"""TP2 — tests du modele : F1 au-dessus du seuil + unitaires sur Classifieur."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from supply_app.predict import SEUIL_CONFIANCE, Classifieur

RACINE = Path(__file__).resolve().parent.parent
METRICS = RACINE / "models" / "metrics.json"

SEUIL_F1 = 0.85


def test_metrics_fichier_lisible():
    assert METRICS.exists()
    donnees = json.loads(METRICS.read_text(encoding="utf-8"))
    assert donnees["n_train"] == 232
    assert donnees["n_test"] == 58


def test_f1_au_dessus_du_seuil():
    donnees = json.loads(METRICS.read_text(encoding="utf-8"))
    # placeholder : le vrai score est ecrit par src/train.py
    if donnees.get("note", "").startswith("placeholder"):
        pytest.skip("metrics.json placeholder : lancez `python src/train.py`")
    assert donnees["f1_macro"] >= SEUIL_F1


def test_f1_rappel_risque_suivi():
    donnees = json.loads(METRICS.read_text(encoding="utf-8"))
    if donnees.get("note", "").startswith("placeholder"):
        pytest.skip("metrics.json placeholder")
    assert donnees["recall_risque"] >= 0.80


def test_matrices_confusion_somme():
    donnees = json.loads(METRICS.read_text(encoding="utf-8"))
    if donnees.get("note", "").startswith("placeholder"):
        pytest.skip("metrics.json placeholder")
    assert sum(sum(ligne) for ligne in donnees["confusion"]) == donnees["n_test"]


class FauxPipeline:
    def __init__(self) -> None:
        self.classes_: list[str] = ["ok", "risque"]

    def predict_proba(self, texts):
        return [[0.9, 0.1]] if "rupture" not in texts[0] else [[0.2, 0.8]]


def test_classifieur_ok():
    clf = Classifieur(FauxPipeline())
    res = clf.predict("Stock suffisant")
    assert res["label"] == "OK"
    assert res["score"] == pytest.approx(0.9)


def test_classifieur_risque():
    clf = Classifieur(FauxPipeline())
    res = clf.predict("rupture imminente")
    assert res["label"] == "RISQUE"
    assert res["score"] == pytest.approx(0.8)


def test_classifieur_abstention_sous_seuil():
    class Faible:
        def __init__(self) -> None:
            self.classes_: list[str] = ["ok", "risque"]

        def predict_proba(self, texts):
            return [[0.52, 0.48]]

    res = Classifieur(Faible()).predict("demande floue")
    assert res["label"] == "INDETERMINE"
    assert res["score"] == pytest.approx(0.52)


def test_classifieur_texte_vide_refuse():
    clf = Classifieur(FauxPipeline())
    with pytest.raises(ValueError):
        clf.predict("   ")


@pytest.mark.parametrize("score", [0.5, 0.59])
def test_seuil_abstention(score):
    assert score < SEUIL_CONFIANCE
