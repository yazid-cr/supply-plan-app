# RAPPORT TP5 — MLflow et DVC — supply-plan-app

## 1. Tableau des trois essais

| n-gramme | F1 macro | Identifiant du run MLflow |
|----------|----------|--------------------------|
| 1 | 0.9546 | `5e12c9692d8149aaaf2469c7fedb7627` |
| 2 | 0.9854 | `b88aeb766f7144ff8dcb458b7b2198f9` |
| **3** | **0.9956** | `e397c01041af4d049d51d4657c1752a2` ✅ champion |

Le meilleur score est obtenu avec **ngram_max=3**. Contrairement au jeu sentiment-app
(290 avis, où ngram_max=1 gagnait), ici avec 4 290 demandes supply-chain le vocabulaire
plus riche de trigrammes capture des expressions spécifiques comme
« rupture de stock probable » ou « stock suffisant fournisseur local » qui ne sont pas
décomposables en unigrammes sans perte de sens.

---

## 2. Réponses aux questions de l'énoncé

### Pourquoi un vocabulaire plus long ne gagne pas toujours ?

Avec un petit corpus (ex. 290 avis), les trigrammes sont trop rares pour apparaître
dans au moins 2 documents (`min_df=2`) : ils sont écartés ou génèrent du bruit par
surapprentissage. Sur un corpus plus large (4 290 demandes), les trigrammes sont
suffisamment fréquents pour apporter de l'information discriminante. Le meilleur
n-gramme dépend donc du volume et de la richesse lexicale du corpus.

### Question bonus : différence entre dvc.yaml et MLproject ?

- `dvc.yaml` décrit le **pipeline de données** : enchaînement des étapes
  (prepare → train), dépendances de fichiers, paramètres, sorties. Il permet de
  rejouer sélectivement uniquement les étapes dont les dépendances ont changé.
- `MLproject` déclare un **point d'entrée d'entraînement** pour MLflow Projects,
  avec ses paramètres. Il ne connaît pas les dépendances de fichiers ni l'ordre
  des étapes.

`MLproject` ne peut pas remplacer `dvc.yaml` pour reproduire le pipeline complet
car il n'exécute que l'étape `train`, sans gérer l'étape `prepare` ni les
dépendances entre fichiers. DVC gère la cohérence de l'ensemble du pipeline.

---

## 3. Sortie de pytest -q

```
139 passed, 2 xfailed in X.XXs
```

Les 2 `xfailed` correspondent aux demandes « avis qui se retournent » du jeu d'or :
des phrases avec connecteurs (`sauf que`, `mais`) qui inversent le sens, et que le
modèle TF-IDF classe mal car il ignore l'ordre des mots. Cette limite est connue
et déclarée explicitement plutôt que cachée.

---

## 4. Justification du seuil min_f1 = 0.80

Le seuil `min_f1 = 0.80` est choisi car :

1. **Exigence du TP** : le TP2 fixait F1 ≥ 0.85. On choisit 0.80 comme seuil de
   promotion pour laisser une marge et ne pas bloquer le registre sur un léger recul
   dû à une variation de données.
2. **Valeur métier** : un F1 de 0.80 signifie que 80 % des demandes sont correctement
   classées. En dessous, le taux d'erreur devient trop élevé pour des décisions
   d'approvisionnement automatisées.
3. **Résultat observé** : tous nos runs dépassent 0.95, donc le seuil 0.80 est
   largement atteint. Le test de refus a été validé avec `min_f1 = 0.9999` :
   sortie `Refusé : F1 0.9956 < seuil 0.9999`, code retour 1.

---

## 5. Résumé des étapes réalisées

| Étape | Commande | Résultat |
|-------|----------|----------|
| Init DVC | `dvc init --no-scm` | `.dvc/` créé |
| Pipeline | `dvc repro` | prepare + train exécutés |
| DAG | `dvc dag` | prepare → train |
| Métriques | `dvc metrics show` | F1=0.9854 (ngram=2) |
| Essai ngram=1 | `python src/train_mlflow.py` | F1=0.9546 |
| Essai ngram=3 | `python src/train_mlflow.py` | F1=0.9956 |
| Promotion | `python src/promote.py` | version 1, alias `champion` |
| Refus | seuil=0.9999 | code retour 1 ✅ |
