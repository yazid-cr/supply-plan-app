"""Promotion du meilleur run vers le registre MLflow (TP5).

Cherche le run terminé avec le meilleur f1_macro dans l'expérience
supply-plan-app. Si le score dépasse promote.min_f1 (params.yaml),
enregistre le modèle sous le nom 'supply' et pose l'alias 'champion'.
Code de retour : 0 (promu) ou 1 (refusé).
"""
from __future__ import annotations

import sys
from pathlib import Path

import mlflow
import yaml

RACINE = Path(__file__).resolve().parent.parent


def promouvoir() -> int:
    params = yaml.safe_load((RACINE / "params.yaml").read_text())["promote"]
    min_f1: float = params["min_f1"]

    client = mlflow.tracking.MlflowClient()

    # Cherche le meilleur run terminé
    runs = mlflow.search_runs(
        experiment_names=["supply-plan-app"],
        filter_string="status = 'FINISHED'",
        order_by=["metrics.f1_macro DESC"],
        max_results=1,
    )

    if runs.empty:
        print("Aucun run terminé trouvé dans l'expérience supply-plan-app.")
        return 1

    best = runs.iloc[0]
    f1    = best["metrics.f1_macro"]
    run_id = best["run_id"]

    if f1 < min_f1:
        print(f"Refusé : F1 {f1:.4f} < seuil {min_f1} (run {run_id})")
        return 1

    # Enregistrement dans le registre
    model_uri = f"runs:/{run_id}/model"
    result = mlflow.register_model(model_uri=model_uri, name="supply")
    version = result.version

    # Alias champion
    client.set_registered_model_alias("supply", "champion", version)

    print(f"Promu : version {version} (F1 {f1:.4f}, run {run_id})")
    return 0


def main() -> None:
    sys.exit(promouvoir())


if __name__ == "__main__":
    main()
