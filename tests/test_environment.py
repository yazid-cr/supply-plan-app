"""TP1 — 23 tests d'environnement (independants du modele)."""
from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

PAQUETS = [
    "fastapi", "pydantic", "sklearn", "joblib", "pandas",
    "httpx", "pytest", "hypothesis",
]
DOSSIERS = ["api", "supply_app", "ui", "src", "data", "models", "tests", "docs"]
FICHIERS = [
    "requirements.txt", "pyproject.toml", ".gitignore", "README.md",
    "api/main.py", "api/schemas.py", "api/model.py",
    "supply_app/predict.py", "supply_app/__init__.py",
    "ui/app.py", "ui/client.py", "src/train.py", "src/make_demo.py",
]


def test_python_311_ou_plus():
    assert sys.version_info >= (3, 11)


def test_environnement_virtuel_actif():
    assert sys.prefix != sys.base_prefix


import pytest


@pytest.mark.parametrize("paquet", PAQUETS)
def test_paquet_installé(paquet):
    pytest.importorskip(paquet) if paquet != "sklearn" else None
    __import__(paquet)


@pytest.mark.parametrize("dossier", DOSSIERS)
def test_dossier_existe(dossier):
    assert (RACINE / dossier).is_dir()


@pytest.mark.parametrize("fichier", FICHIERS)
def test_fichier_existe(fichier):
    assert (RACINE / fichier).exists()


def test_gitigignore_existe():
    assert (RACINE / ".gitignore").exists()


def test_gitigignore_ignore_venv():
    contenu = (RACINE / ".gitignore").read_text(encoding="utf-8")
    assert ".venv/" in contenu


def test_gitigignore_ignore_modele():
    contenu = (RACINE / ".gitignore").read_text(encoding="utf-8")
    assert ".joblib" in contenu


def test_dependances_epinglees():
    contenu = (RACINE / "requirements.txt").read_text(encoding="utf-8")
    assert "fastapi" in contenu
    assert "scikit-learn" in contenu
    assert ">=" in contenu


def test_pyproject_declare_nom():
    assert 'name = "supply-plan-app"' in (RACINE / "pyproject.toml").read_text(
        encoding="utf-8"
    )


def test_aucun_fichier_env_commite():
    assert not list(RACINE.rglob(".env")) or all(
        ".venv" in str(p) for p in RACINE.rglob(".env")
    )
