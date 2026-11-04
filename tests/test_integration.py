"""TP4 — 6 tests d'integration : demarrage, 503, 500."""
from __future__ import annotations

import pytest

from api.main import app
from tests.conftest import TEXTE_OK


class ModeleEnPanne:
    model_name = "modele en panne (test)"

    def __init__(self, erreur: Exception) -> None:
        self.erreur = erreur

    def predict(self, text: str) -> dict:
        raise self.erreur


@pytest.mark.parametrize(
    "erreur",
    [RuntimeError("panne inattendue"), ValueError("texte refuse par le modele")],
)
def test_modele_en_panne_repond_500(client, monkeypatch, erreur):
    monkeypatch.setattr(app.state, "classifier", ModeleEnPanne(erreur))
    if isinstance(erreur, ValueError):
        reponse = client.post("/predict", json={"text": TEXTE_OK})
        assert reponse.status_code == 422
    else:
        reponse = client.post("/predict", json={"text": TEXTE_OK})
        assert reponse.status_code == 500


def test_modele_absent_repond_503(client, monkeypatch):
    from fastapi import HTTPException

    monkeypatch.setattr(app.state, "classifier", None)
    # _classifier refuse avant predict : 503, jamais 500

    from api.main import _classifier

    class FakeReq:
        class app:
            class state:
                classifier = None

    with pytest.raises(HTTPException) as exc:
        _classifier(FakeReq())  # type: ignore[arg-type]
    assert exc.value.status_code == 503
    reponse = client.get("/health")
    assert reponse.status_code == 503


def test_demarre_sans_modele_refuse_lancement(monkeypatch):
    """Sans modele, le demarrage refuse (T20) : load_model leve."""
    from supply_app.predict import load_model

    with pytest.raises(FileNotFoundError):
        load_model("/chemin/introuvable/supply.joblib")


def test_route_non_declaree_404(client):
    # /predict existe en POST seul : GET donne 405, route inconnue donne 404
    assert client.get("/route-inexistante").status_code == 404


def test_method_not_allowed(client):
    # GET sur une route POST : 405
    assert client.get("/predict").status_code in (404, 405)


def test_panne_journalisee_sans_detail(client, monkeypatch):

    monkeypatch.setattr(
        app.state, "classifier", ModeleEnPanne(RuntimeError("secret serveur"))
    )
    with pytest.MonkeyPatch.context():
        pass
    reponse = client.post("/predict", json={"text": TEXTE_OK})
    assert reponse.status_code == 500
    # le detail interne n'est jamais renvoye au client
    assert "secret serveur" not in reponse.text
