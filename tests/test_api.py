"""TP3 — l'API est un contrat : 200, 422 pour les trois requetes invalides."""
from __future__ import annotations

from tests.conftest import CONTRAT, TEXTE_OK, TEXTE_RISQUE


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    corps = r.json()
    assert corps["status"] == "OK"
    # le FauxModele annonce son nom de test
    assert corps["model"] == "faux-modele (test)"


def test_accueil(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/predict" in r.json()["routes"]


def test_predict_ok(client):
    r = client.post("/predict", json={"text": TEXTE_OK})
    assert r.status_code == 200
    corps = r.json()
    # labels majuscules OK/RISQUE, le pipeline entraine utilise ok/risque en minuscules
    assert corps["label"] in CONTRAT
    assert 0 <= corps["score"] <= 1
    assert corps["text"] == TEXTE_OK


def test_predict_risque(client):
    r = client.post("/predict", json={"text": TEXTE_RISQUE})
    assert r.status_code == 200
    corps = r.json()
    assert corps["label"] == "RISQUE"


def test_text_vide_refuse_422(client):
    r = client.post("/predict", json={"text": ""})
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert isinstance(detail, list)  # forme Pydantic : jamais une chaine simple


def test_champ_manquant_refuse_422(client):
    r = client.post("/predict", json={})
    assert r.status_code == 422


def test_type_invalide_refuse_422(client):
    r = client.post("/predict", json={"text": 42})
    assert r.status_code == 422


def test_trop_long_refuse_422(client):
    r = client.post("/predict", json={"text": "x" * 2001})
    assert r.status_code == 422


def test_422_jamais_500(client):
    # une entree invalide donne 422, jamais 500
    r = client.post("/predict", json={"text": "   "})
    assert r.status_code == 422
    assert r.status_code != 500


def test_reponse_dans_contrat(client):
    r = client.post("/predict", json={"text": "demande quelconque de test"})
    assert r.json()["label"] in CONTRAT
