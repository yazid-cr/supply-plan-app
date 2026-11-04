# supply-plan-app — Agent de planification de la chaîne d'approvisionnement

Transposition du projet « sentiment-app » (TP1→TP6, du cadrage au paquet)
à la supply chain. Un seul dépôt qui grandit de TP en TP, quatre couches,
chacune ne parle qu'à sa voisine.

```
« Stock suffisant et délai de livraison standard » → supply-plan-app → OK, confiance 0,82
« Rupture de stock probable, délai fournisseur inconnu » → supply-plan-app → RISQUE, confiance 0,64
```

Des **demandes supply-chain en français**, deux classes : **ok** (planifiable)
et **risque** (rupture / retard probables), plus une abstention **INDETERMINE**
sous 60 % de confiance, confiée à un humain.

## Architecture

| Couche | Contenu |
|---|---|
| Modèle (TP2) | `supply_app/predict.py`, `models/supply.joblib` (pipeline TF-IDF + régression logistique) |
| API (TP3) | `api/main.py`, `api/schemas.py`, `api/model.py` |
| Interface (TP5) | `ui/app.py`, `ui/client.py` |
| Tests (TP4) | pytest, hypothesis, ruff, mypy, CI GitHub |
| Paquet (TP6) | la roue `supply_plan_app`, commande `supply` |

## TP1 — Cadrage (`docs/cadrage.md`)

- **T** : classer une demande en ok / risque ; **E** : 232 demandes étiquetées
  ; **P** : F1 macro sur 58 demandes jamais vues (≥ 0,85 exigé).
- Approche retenue : **apprentissage automatique** — (a) des données étiquetées
  existent, (c) coût par demande faible. Règles métier et RAG comparées
  dans la fiche de cadrage.

## Commandes (environnement activé)

```powershell
# TP2 : générer le jeu de démonstration, puis entraîner
python src/make_demo.py
python src/train.py            # F1 macro, models/supply.joblib, models/metrics.json

# TP3 : API (la page /docs est générée à partir du code)
uvicorn api.main:app --reload  # http://127.0.0.1:8000/docs

# TP4 : qualité
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
ruff check .
mypy api

# TP5 : interface (API lancée)
streamlit run ui/app.py

# TP6 : paquet installable
python -m build --wheel
$env:SUPPLY_MODELE = "C:\chemin\models\supply.joblib"
supply --version               # supply-plan-app 0.6.0
supply predict "Stock suffisant et delai standard"
supply serve --port 8000
supply ui
```

## API : codes HTTP

| Code | Signification |
|---|---|
| 200 | demande classée (OK / RISQUE / INDETERMINE) |
| 422 | requête invalide : faute du client (jamais un 500) |
| 503 | modèle non chargé |
| 500 | panne du serveur (détail journalisé, jamais renvoyé) |

## Jeu d'or

`data/jeu_or.csv` : 20 demandes de référence. Une erreur connue se déclare
(`erreur_connue` → `xfail`), elle ne se cache pas : 11 justes, 8 abstentions,
1 erreur franche déclarée (avis qui se retourne).

## Résultats vérifiés

- Modèle : F1 macro 1,000 sur 58 demandes jamais vues (jeu de démonstration
  très séparable) ; rappel des risques 1,000 ; vocabulaire 441 termes.
- Suite : `139 passed, 2 xfailed` (plus les 3 tests Git en solo).
- Couverture API : 98 % (seuil CI 95 %). `ruff` et `mypy api` verts.
- Roue `supply_plan_app-0.6.0-py3-none-any.whl` construite, installée dans un
  environnement neuf, puis `supply predict` renvoie OK / RISQUE / INDETERMINE.
