"""TP5 â€” 7 tests du client HTTP : codes traduits en messages."""
from __future__ import annotations

from tests.conftest import TEXTE_OK
from ui import client as client_http


def test_client_200_ok(client):
    rep = client_http.predire(client, TEXTE_OK)
    assert rep.ok is True
    assert rep.label in ("OK", "RISQUE", "INDETERMINE")
    assert rep.score is not None


def test_client_422_message(client):
    rep = client_http.predire(client, "   ")
    assert rep.ok is False
    assert rep.message == client_http.REFUS


def test_client_422_trop_long(client):
    rep = client_http.predire(client, "x" * 3000)
    assert rep.ok is False
    assert rep.message == client_http.REFUS


def test_client_503_message(client, monkeypatch):
    from api.main import app

    app.state.classifier = None
    rep = client_http.predire(client, TEXTE_OK)
    assert rep.ok is False
    assert "train.py" in (rep.message or "")


def test_client_injoignable(client, monkeypatch):
    import httpx

    class ConnexionImpossible:
        def post(self, *args, **kwargs):
            # simule une API injoignable : TransportError natif httpx
            raise httpx.ConnectError("connexion refusee", request=None)

    rep = client_http.predire(ConnexionImpossible(), TEXTE_OK)
    assert rep.ok is False
    assert rep.message == client_http.INJOIGNABLE


def test_client_500_message(client, monkeypatch):
    from api.main import app
    from tests.test_integration import ModeleEnPanne

    monkeypatch.setattr(
        app.state, "classifier", ModeleEnPanne(RuntimeError("panne"))
    )
    rep = client_http.predire(client, TEXTE_OK)
    assert rep.ok is False
    assert rep.message is not None


def test_client_reponse_jamais_exception(client):
    # meme avec du bruit, predire renvoie toujours une Reponse
    rep = client_http.predire(client, "\x00 demande \x00")
    assert rep.ok in (True, False)

