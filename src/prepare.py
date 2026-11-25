"""Nettoyage et découpage des données (TP5 — DVC pipeline étape prepare).

Lit data/demo_demandes.csv, supprime les doublons et les vides,
découpe de façon stratifiée en train/test.
Sortie : data/prepared/train.csv et data/prepared/test.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

RACINE = Path(__file__).resolve().parent.parent


def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"].str.strip() != ""]
    df = df.drop_duplicates(subset=["text"])
    df = df.reset_index(drop=True)
    return df


def preparer(source: Path, sortie: Path, test_size: float = 0.2, seed: int = 42) -> None:
    df = pd.read_csv(source)
    df = nettoyer(df)

    X_train, X_test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df["label"]
    )

    sortie.mkdir(parents=True, exist_ok=True)
    X_train.to_csv(sortie / "train.csv", index=False)
    X_test.to_csv(sortie / "test.csv", index=False)

    print(f"train : {len(X_train)} demandes, test : {len(X_test)} demandes -> {sortie}")


def main() -> None:
    import yaml

    params = yaml.safe_load((RACINE / "params.yaml").read_text())["prepare"]
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "data" / "demo_demandes.csv"
    preparer(source, RACINE / "data" / "prepared",
             test_size=params["test_size"], seed=params["seed"])


if __name__ == "__main__":
    main()
