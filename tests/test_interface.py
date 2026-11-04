"""TP5 â€” 5 tests : la vraie page executee sans serveur (AppTest si dispo)."""
from __future__ import annotations

import pytest

pytest.importorskip("streamlit")

from tests.conftest import TEXTE_OK
from ui import client as client_http

PAGE = "ui/app.py"


def test_page_fichier_existe():
    from pathlib import Path

    assert Path(PAGE).exists()


def test_client_module_sans_modele_direct():
    """La page ne parle qu'a l'API : client.py n'importe pas predict ni joblib."""
    from pathlib import Path

    source = Path("ui/client.py").read_text(encoding="utf-8")
    assert "import joblib" not in source
    assert "supply_app.predict" not in source
    assert "from joblib" not in source


def test_page_utilise_client_predire():
    from pathlib import Path

    assert "client.predire" in Path(PAGE).read_text(encoding="utf-8")
    assert "API_URL" in Path("ui/client.py").read_text(encoding="utf-8")


def test_verdicts_affiches(client):
    # meme chemin que la page : client_http.predire -> libelle
    rep = client_http.predire(client, TEXTE_OK)
    assert rep.ok is True
    assert rep.label in ("OK", "RISQUE", "INDETERMINE")


def test_app_test_page_reelle(client, monkeypatch):
    """AppTest execute ui/app.py avec l'API en memoire (si streamlit >= 1.28)."""
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(client_http, "creer_session", lambda: client)
    # AppTest resout les chemins relatifs depuis le fichier appelant :
    # on donne le chemin absolu de la page.
    page_abs = str(Path(PAGE).resolve())
    at = AppTest.from_file(page_abs, default_timeout=30).run()
    at.text_area[0].input(TEXTE_OK).run()
    at.button[0].click().run()
    assert not at.exception

