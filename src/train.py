"""Entrainement + mesure (TP2).

Decoupe AVANT vectorisation : 232 demandes d'entrainement (80 %) et
58 de test jamais vues. Pipeline unique TF-IDF + regression logistique,
sauvegarde dans models/supply.joblib ; mesure dans models/metrics.json
(versionnee dans Git — le modele, lui, reste hors de Git).
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

GRAINE = 42
RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data" / "demo_demandes.csv"
MODELE = RACINE / "models" / "supply.joblib"
METRICS = RACINE / "models" / "metrics.json"


def construire_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2), min_df=2, sublinear_tf=True
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=GRAINE,
                ),
            ),
        ]
    )


def main() -> None:
    df = pd.read_csv(DATA)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    pipe = construire_pipeline()
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)

    f1 = f1_score(y_test, pred, average="macro")
    prec, rap, f1s, _ = precision_recall_fscore_support(
        y_test, pred, labels=["risque", "ok"], zero_division=0
    )
    metrics = {
        "source": "demo",
        "n_total": len(df),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "f1_macro": round(float(f1), 3),
        "accuracy": round(float(accuracy_score(y_test, pred)), 3),
        "recall_risque": round(float(rap[0]), 3),
        "recall_ok": round(float(rap[1]), 3),
        "precision_risque": round(float(prec[0]), 3),
        "precision_ok": round(float(prec[1]), 3),
        "f1_risque": round(float(f1s[0]), 3),
        "f1_ok": round(float(f1s[1]), 3),
        "confusion": confusion_matrix(y_test, pred, labels=["risque", "ok"]).tolist(),
        "vocab_size": len(pipe.named_steps["tfidf"].vocabulary_),
    }
    MODELE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODELE)
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(classification_report(y_test, pred, digits=3))
    print(f"Vocabulaire : {metrics['vocab_size']} termes")
    print(f"Modele -> {MODELE}")
    print(f"Mesures -> {METRICS} : F1 macro = {metrics['f1_macro']}")


if __name__ == "__main__":
    main()
