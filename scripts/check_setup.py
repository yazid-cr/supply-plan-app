"""Diagnostic d'environnement (TP4) : Python, paquets, dossiers, fichiers."""
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
    "requirements.txt", "pyproject.toml", ".gitignore",
    "api/main.py", "api/schemas.py", "supply_app/predict.py",
    "ui/app.py", "ui/client.py", "src/train.py", "src/make_demo.py",
]


def main() -> int:
    erreurs: list[str] = []
    if (sys.version_info.major, sys.version_info.minor) < (3, 11):
        erreurs.append(f"Python 3.11+ requis, trouve {sys.version_info}")
    for paquet in PAQUETS:
        try:
            __import__(paquet)
        except ImportError:
            erreurs.append(f"paquet manquant : {paquet}")
    for dossier in DOSSIERS:
        if not (RACINE / dossier).is_dir():
            erreurs.append(f"dossier manquant : {dossier}")
    for fichier in FICHIERS:
        if not (RACINE / fichier).exists():
            erreurs.append(f"fichier manquant : {fichier}")
    if erreurs:
        print("DIAGNOSTIC ECHOUE :")
        for e in erreurs:
            print(f" - {e}")
        return 1
    print(
        f"Diagnostic OK : Python {sys.version_info.major}."
        f"{sys.version_info.minor}, {len(PAQUETS)} paquets, "
        f"{len(DOSSIERS)} dossiers, {len(FICHIERS)} fichiers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
