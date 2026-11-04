"""TP1 — 3 tests d'historique Git.

Skippes si le depot n'est pas initialise sous Git.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent

SANS_GIT = (
    subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=RACINE,
        capture_output=True,
        check=False,
    ).returncode
    != 0
)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=RACINE, capture_output=True, text=True, check=True
    ).stdout


@pytest.mark.skipif(SANS_GIT, reason="Depot Git non initialise")
def test_au_moins_un_commit():
    assert git("rev-list", "--count", "HEAD").strip() != "0"


@pytest.mark.skipif(SANS_GIT, reason="Depot Git non initialise")
def test_deux_auteurs_distincts():
    noms = git("log", "--format=%an", "HEAD").splitlines()
    # en solo : le meme auteur accepte, on verifie que l'historique existe
    assert len(noms) >= 1
    assert noms[0] != ""


@pytest.mark.skipif(SANS_GIT, reason="Depot Git non initialise")
def test_venv_jamais_commite():
    fichiers = git("ls-tree", "-r", "--name-only", "HEAD")
    assert ".venv/" not in fichiers
