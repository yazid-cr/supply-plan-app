# models/

- `metrics.json` : la mesure de chaque entraînement (**dans Git** — la CI
  vérifie le F1 sans avoir le modèle).
- `supply.joblib` : le pipeline entraîné (**hors de Git**, `.gitignore`) ;
  reconstruit en une commande : `python src/make_demo.py && python src/train.py`.

Référence (sentiment-app, TP2) :

```json
{
  "source": "demo",
  "n_train": 232,
  "n_test": 58,
  "f1_macro": 0.879,
  "recall_negative": 0.931
}
```

Pour supply-plan-app, le même contrat : `f1_macro` ≥ 0,85, `recall_risque` suivi.
