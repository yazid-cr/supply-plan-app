"""Genere le jeu de demonstration (TP2).

290 demandes supply-chain : 145 OK, 145 RISQUE. Le meme motif que
l'enonce sentiment-app (145 positifs / 145 negatifs), transpose :
demande planifiable vs demande a risque de rupture / retard.

Genere aussi data/demandes_exemple.csv (6 demandes pour l'onglet fichier).
Graine fixee : resultats reproductibles.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

GRAINE = 42
RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "data" / "demo_demandes.csv"
EXEMPLE = RACINE / "data" / "demandes_exemple.csv"

OK_FRAGMENTS = [
    "stock suffisant fournisseur local delai court",
    "delai de livraison standard sans tension capacitaire",
    "commande urgente mais inventaire disponible",
    "approvisionnement confirme date dereception stable",
    "stock de securite superieur au besoin hebdomadaire",
    "fournisseur fiable historique de livraisons a lheure",
    "demande reguliere niveau de stock correct",
    "lead time court rupture improbable",
    "quantite raisonnable entrepot non sature",
    "transport disponible sans retard constate",
    "produit standard delai fournisseur maitrise",
    "niveau de stock eleve consommation stable",
    "rupture evitee grace au stock de securite",
    "approvisionnement planifie sans alerte",
    "demande saisonniere anticipee avec prevision",
]
RISQUE_FRAGMENTS = [
    "rupture de stock probable delai fournisseur inconnu",
    "retard de livraison critique penalites contractuelles",
    "fournisseur unique defaillance capacitaire signalee",
    "demande en forte hausse sans stock disponible",
    "lead time allonge transport perturbe par greve",
    "stock inferieur au seuil de securite rupture imminente",
    "commande urgente aucun fournisseur disponible",
    "saturation entrepot capacite de stockage insuffisante",
    "panne equipement de production ligne arretee",
    "matiere premiere strategique penurie mondiale",
    "delais portuaires congestion suite douane incertaine",
    "produit obsolete risque demarquage eleve",
    "fluctuation dechange couts en forte hausse",
    "grève transporteur impossible de livrer a temps",
    "capacite fournisseur reduite de moitie ce trimestre",
]
# Connecteurs simples (avis qui se retournent = source des erreurs, cf. TP2).
CONNECTEURS = ["ensuite", "puis", "finalement", "sauf que", "mais", "avant que"]

ENSEMBLES = [
    "stock fournisseur entrepot", "delai livraison commande transport",
    "demande prevision saisonnalite", "rupture securite niveau stock",
    "capacite production fournisseur", "lead time inventaire requete",
]


def demarrer(rng: random.Random) -> str:
    return rng.choice(
        ["Demande", "Demande", "Ordre", "Plan", "Plan", "Commande", "Requete", "Batch"]
    )


def generer(rng: random.Random, fragments: list[str]) -> str:
    morceaux = [demarrer(rng), rng.choice(ENSEMBLES)]
    morceaux.extend(rng.choice(fragments) for _ in range(rng.randint(1, 3)))
    texte = " ".join(morceaux)
    if rng.random() < 0.3:
        texte += " " + rng.choice(CONNECTEURS) + " " + rng.choice(fragments)
    return texte


def main() -> None:
    rng = random.Random(GRAINE)
    lignes = []
    for _ in range(145):
        lignes.append({"text": generer(rng, OK_FRAGMENTS), "label": "ok"})
    for _ in range(145):
        lignes.append({"text": generer(rng, RISQUE_FRAGMENTS), "label": "risque"})
    rng.shuffle(lignes)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label"])
        w.writeheader()
        w.writerows(lignes)
    exemples = [
        ("Stock suffisant et delai de livraison standard sans tension capacitaire", "ok"),
        ("Rupture de stock probable et delai fournisseur inconnu", "risque"),
        ("Fournisseur fiable et stock de securite eleve", "ok"),
        ("Retard de livraison critique et fournisseur unique en defaillance capacitaire", "risque"),
        ("Demande reguliere avec lead time court et rupture improbable", "ok"),
        ("Stock inferieur au seuil de securite, rupture imminente", "risque"),
    ]
    with EXEMPLE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label"])
        w.writeheader()
        for text, label in exemples:
            w.writerow({"text": text, "label": label})
    print(f"Demo : {len(lignes)} demandes -> {SORTIE}")
    print(f"Exemples : {len(exemples)} -> {EXEMPLE}")


if __name__ == "__main__":
    main()
