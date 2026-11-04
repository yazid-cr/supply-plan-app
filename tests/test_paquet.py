"""TP6 — paquet : version unique, dependances, scripts, roue construite."""
from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from supply_app import __version__

RACINE = Path(__file__).resolve().parent.parent
PYPROJECT = RACINE / "pyproject.toml"


def test_version_unique():
    assert __version__ == "0.6.0"
    texte = PYPROJECT.read_text(encoding="utf-8")
    assert "version" not in texte.split("[project]")[1].split("dynamic")[0] or "dynamic" in texte
    assert "supply_app.__version__" in texte


def test_commande_supply_declaree():
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    assert data["project"]["scripts"] == {"supply": "supply_app.cli:main"}


def test_dependances_epinglees():
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    texte = " ".join(deps)
    assert "scikit-learn>=1.5,<1.6" in texte
    assert "fastapi>=0.115,<0.116" in texte


def test_paquets_inclus():
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    assert data["tool"]["setuptools"]["packages"] == ["supply_app", "api", "ui"]


def test_modele_hors_roue():
    # models/ est ignore par Git : le modele garde son propre cycle de vie
    gitignore = (RACINE / ".gitignore").read_text(encoding="utf-8")
    assert "models/*.joblib" in gitignore


def test_roue_construite_si_dist_present():
    dist = RACINE / "dist"
    if not dist.exists():
        pytest.skip("roue non construite : python -m build --wheel")
    assert list(dist.glob("supply_plan_app-0.6.0*.whl"))


def test_cli_importable_sans_modele():
    import supply_app.cli  # sans side-effect

    assert callable(supply_app.cli.main)
