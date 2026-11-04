# Critères d'acceptation (fixés avant de construire)

| Critère d'acceptation | Vérifié par |
|---|---|
| F1 macro d'au moins 0,85 sur un jeu de test jamais vu | test_f1_au_dessus_du_seuil (TP2) |
| Toute entrée invalide refusée par un 422, jamais par un 500 | test_limites.py (TP4) |
| Aucune erreur franche non déclarée sur le jeu d'or | test_jeu_or.py (TP4) |
| Sous une confiance de 0,60, l'API s'abstient | api/model.py (TP4) |

Fixés après coup, les critères décriraient seulement ce que le modèle sait
déjà faire.
