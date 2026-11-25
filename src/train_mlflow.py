"""Entraînement avec journalisation MLflow (TP5).

Lit data/prepared/train.csv et test.csv, entraîne le pipeline TF-IDF +
régression logistique, journalise params/métriques/artefact/modèle dans MLflow.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
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

RACINE = Path(__file__).resolve().parent.parent
MODELE = RACINE / "models" / "supply.joblib"
METRICS = RACINE / "models" / "metrics.json"


def construire_pipeline(ngram_max: int = 2, min_df: int = 2, seed: int = 42) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, ngram_max), min_df=min_df, sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=seed
        )),
    ])


def entrainer(ngram_max: int = 2, min_df: int = 2, seed: int = 42) -> float:
    # Chargement des données préparées
    prepared = RACINE / "data" / "prepared"
    if (prepared / "train.csv").exists():
        df_train = pd.read_csv(prepared / "train.csv")
        df_test  = pd.read_csv(prepared / "test.csv")
        X_train, y_train = df_train["text"], df_train["label"]
        X_test,  y_test  = df_test["text"],  df_test["label"]
    else:
        # Fallback : découpage direct depuis demo_demandes.csv
        df = pd.read_csv(RACINE / "data" / "demo_demandes.csv")
        X_train, X_test, y_train, y_test = train_test_split(
            df["text"], df["label"], test_size=0.2, random_state=seed, stratify=df["label"]
        )

    pipe = construire_pipeline(ngram_max=ngram_max, min_df=min_df, seed=seed)
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)

    f1 = f1_score(y_test, pred, average="macro")
    prec, rap, f1s, _ = precision_recall_fscore_support(
        y_test, pred, labels=["risque", "ok"], zero_division=0
    )

    metrics = {
        "f1_macro":        round(float(f1), 4),
        "accuracy":        round(float(accuracy_score(y_test, pred)), 4),
        "recall_risque":   round(float(rap[0]), 4),
        "recall_ok":       round(float(rap[1]), 4),
        "precision_risque":round(float(prec[0]), 4),
        "precision_ok":    round(float(prec[1]), 4),
        "f1_risque":       round(float(f1s[0]), 4),
        "f1_ok":           round(float(f1s[1]), 4),
        "vocab_size":      len(pipe.named_steps["tfidf"].vocabulary_),
        "n_train":         len(X_train),
        "n_test":          len(X_test),
        "confusion":       confusion_matrix(y_test, pred, labels=["risque", "ok"]).tolist(),
    }

    # Sauvegarde locale
    MODELE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODELE)
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Journalisation MLflow ---
    mlflow.set_experiment("supply-plan-app")
    run_name = f"tfidf-logreg-ngram{ngram_max}"
    with mlflow.start_run(run_name=run_name) as run:
        # Paramètres
        mlflow.log_param("ngram_max", ngram_max)
        mlflow.log_param("min_df",    min_df)
        mlflow.log_param("seed",      seed)

        # Métriques
        mlflow.log_metric("f1_macro",        metrics["f1_macro"])
        mlflow.log_metric("accuracy",        metrics["accuracy"])
        mlflow.log_metric("recall_risque",   metrics["recall_risque"])
        mlflow.log_metric("recall_ok",       metrics["recall_ok"])
        mlflow.log_metric("vocab_size",      metrics["vocab_size"])

        # Artefact : fichier metrics.json
        mlflow.log_artifact(str(METRICS))

        # Modèle
        mlflow.sklearn.log_model(pipe, artifact_path="model")

        run_id = run.info.run_id

    print(classification_report(y_test, pred, digits=3))
    print(f"Vocabulaire : {metrics['vocab_size']} termes")
    print(f"F1 macro (test) : {metrics['f1_macro']} | run MLflow : {run_id}")
    return f1


def main() -> None:
    params = yaml.safe_load((RACINE / "params.yaml").read_text())["train"]
    entrainer(
        ngram_max=params["ngram_max"],
        min_df=params["min_df"],
        seed=params["seed"],
    )


if __name__ == "__main__":
    main()
