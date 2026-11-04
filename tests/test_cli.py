"""TP6 — la commande supply : parse, version, predict, modele manquant."""
from __future__ import annotations

import json

import pytest

from supply_app import __version__
from supply_app.cli import main


def test_version():
    assert __version__ == "0.6.0"


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "0.6.0" in capsys.readouterr().out


def test_commande_requise():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_predict_sans_modele_code_1(capsys, monkeypatch):
    monkeypatch.setenv("SUPPLY_MODELE", "/chemin/introuvable/supply.joblib")
    code = main(["predict", "Stock suffisant"])
    assert code == 1
    assert "modele introuvable" in capsys.readouterr().err


def test_predict_vrai_modele():
    from supply_app.predict import chemin_modele

    if not chemin_modele().exists():
        pytest.skip("modele absent : lancez `python src/train.py`")
    code = main(["predict", "Stock suffisant et delai standard"])
    assert code == 0


def test_predict_json_reel(capsys):
    from supply_app.predict import chemin_modele

    if not chemin_modele().exists():
        pytest.skip("modele absent")
    code = main(["predict", "Rupture de stock probable"])
    assert code == 0
    corps = json.loads(capsys.readouterr().out)
    assert corps["label"] in ("OK", "RISQUE", "INDETERMINE")
    assert 0 <= corps["score"] <= 1


def test_sous_commandes_declarees():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
