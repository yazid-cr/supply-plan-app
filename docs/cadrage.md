# Fiche de cadrage — cas supply chain : repérer les demandes à risque

## Approches
- [ ] Règles métier
- [x] Apprentissage automatique
- [ ] RAG

## Rubriques (huit, remplies)

- **Besoin en une phrase** : Repérer chaque jour les demandes supply-chain à risque de rupture ou de retard, pour les sécuriser en priorité.
- **Utilisateur final** : L'équipe planification / approvisionnement.
- **Approche retenue** : Une seule case cochée : apprentissage automatique.
- **Justification** : (a) des demandes étiquetées existent ; (c) le coût par demande est faible.
- **Données nécessaires** : Des demandes en français, étiquetées ok ou risque.
- **Métrique de succès** : F1 macro d'au moins 0,85 ; rappel des risques suivi.
- **Conséquence d'une erreur** : Une rupture manquée coûte plus qu'une fausse alerte.
- **Risques éthiques** : Données commerciales sensibles dans les demandes ; un humain tranche les cas douteux (seuil d'abstention 0,60).

## Critères d'acceptation (fixés avant de construire)

1. F1 macro d'au moins 0,85 sur un jeu de test jamais vu — `test_f1_au_dessus_du_seuil` (TP2).
2. Toute entrée invalide refusée par un 422, jamais par un 500 — `test_limites.py` (TP4).
3. Aucune erreur franche non déclarée sur le jeu d'or — `test_jeu_or.py` (TP4).
4. Sous une confiance de 0,60, l'API s'abstient — `api/model.py` (TP4).

## Comparaison des approches (critères a–d)

| Critère | Règles métier | Apprentissage automatique | RAG |
|---|---|---|---|
| (a) Données étiquetées | Inutiles | Indispensables, en quantité | Inutiles : des documents |
| (b) Vérifiabilité | Totale : on cite la règle | Partielle : on explique les poids | Bonne, si la réponse cite ses sources |
| (c) Coût par requête | Quasi nul | Faible | Élevé : un modèle de langage |
| (d) Conséquence d'une erreur | Maîtrisée | Mesurable, à encadrer | À contrôler : hallucinations |

Le bon choix est l'approche la plus simple qui satisfait les critères
d'acceptation : l'apprentissage automatique.
