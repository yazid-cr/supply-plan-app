"""Prédiction via le registre MLflow ou le fichier local (TP5).

Usage :
  python src/predict_mlflow.py "Stock suffisant" "Rupture imminente"
  python src/predict_mlflow.py --registre "Stock suffisant"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
URI_REGISTRE = "models:/supply@champion"
MODELE_LOCAL  = RACINE / "models" / "supply.joblib"
SEUIL = 0.60


def charger():
    import joblib
    return joblib.load(MODELE_LOCAL)


def charger_registre():
    import mlflow.pyfunc
    return mlflow.pyfunc.load_model(URI_REGISTRE)


def predire(modele, textes: list[str]) -> list[tuple[str, float]]:
    import numpy as np
    resultats = []
    for texte in textes:
        try:
            proba = modele.predict_proba([texte])[0]
            classes = modele.classes_
        except AttributeError:
            # mlflow.pyfunc n'expose pas predict_proba directement
            import pandas as pd
            pred = modele.predict(pd.DataFrame({"text": [texte]}))
            resultats.append((str(pred[0]).upper(), 1.0))
            continue

        idx = int(np.argmax(proba))
        score = float(proba[idx])
        label = str(classes[idx]).upper() if score >= SEUIL else "INDETERMINE"
        resultats.append((label, score))
    return resultats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("textes", nargs="+")
    parser.add_argument("--registre", action="store_true",
                        help="Charge le modèle depuis le registre MLflow")
    args = parser.parse_args()

    modele = charger_registre() if args.registre else charger()
    for texte, (label, score) in zip(args.textes, predire(modele, args.textes)):
        print(f"{label:<12} ({score*100:.0f}%)  {texte}")


if __name__ == "__main__":
    main()
