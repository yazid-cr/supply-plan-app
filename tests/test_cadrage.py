"""TP1 — 12 tests de cadrage : trois fiches, huit rubriques."""
from __future__ import annotations

from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
CADRAGE = RACINE / "docs" / "cadrage.md"
APPROCHES = RACINE / "docs" / "approches.md"
CRITERES = RACINE / "docs" / "criteres.md"

RUBRIQUES = [
    "Besoin en une phrase", "Utilisateur final", "Approche retenue",
    "Justification", "Données nécessaires", "Métrique de succès",
    "Conséquence d'une erreur", "Risques éthiques",
]


def test_cadrage_existe():
    assert CADRAGE.exists()


def test_approches_existe():
    assert APPROCHES.exists()


def test_criteres_existe():
    assert CRITERES.exists()


@pytest.mark.parametrize("rubrique", RUBRIQUES)
def test_rubrique_presente(rubrique):
    assert rubrique in CADRAGE.read_text(encoding="utf-8")


def test_une_seule_case_cochee():
    contenu = CADRAGE.read_text(encoding="utf-8")
    assert contenu.count("[x]") == 1
    assert "[x] Apprentissage automatique" in contenu


def test_deux_criteres_cites():
    contenu = CADRAGE.read_text(encoding="utf-8")
    assert "Justification" in contenu
    assert "(a)" in contenu
    assert "(c)" in contenu


def test_criteres_acceptation_listes():
    contenu = CRITERES.read_text(encoding="utf-8")
    assert "0,85" in contenu or "0.85" in contenu
    assert "422" in contenu
    assert "0,60" in contenu or "0.60" in contenu
    assert "jeu d'or" in contenu
