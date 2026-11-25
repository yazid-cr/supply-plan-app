"""Import et transformation du dataset DataCo Smart Supply Chain (Kaggle).

Téléchargement automatique via kagglehub (nécessite kagglehub installé) :
    pip install kagglehub

Le script :
1. Télécharge DataCoSupplyChainDataset.csv via kagglehub
2. Mappe Late_delivery_risk (0/1) → label ok/risque
3. Génère une phrase française descriptive par commande
4. Écrit data/dataco_demandes.csv (format text,label)
5. Fusionne avec demo_demandes.csv → data/demo_demandes.csv (réentraînement)
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

import kagglehub
import pandas as pd

GRAINE = 42
RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "data" / "dataco_demandes.csv"
DEMO = RACINE / "data" / "demo_demandes.csv"
DEMO_FUSIONNE = RACINE / "data" / "demo_demandes.csv"  # écrasé après fusion

# Mapping des modes de livraison
MODE_MAP = {
    "Standard Class": "livraison standard",
    "First Class": "livraison express",
    "Second Class": "livraison économique",
    "Same Day": "livraison le jour même",
}

# Mapping des statuts de commande
STATUT_MAP = {
    "Complete": "commande livrée",
    "Pending": "commande en attente",
    "Pending Payment": "paiement en attente",
    "Processing": "commande en cours de traitement",
    "Shipping": "expédition en cours",
    "Closed": "commande clôturée",
    "Canceled": "commande annulée",
    "On Hold": "commande en suspens",
    "Payment Review": "révision du paiement",
    "Suspected Fraud": "commande suspecte",
}

# Mapping des régions
REGION_MAP = {
    "Western Europe": "Europe de l'Ouest",
    "Central America": "Amérique centrale",
    "Oceania": "Océanie",
    "Eastern Asia": "Asie de l'Est",
    "South America": "Amérique du Sud",
    "Southeast Asia": "Asie du Sud-Est",
    "Western Asia": "Asie de l'Ouest",
    "Southern Europe": "Europe du Sud",
    "North America": "Amérique du Nord",
    "Eastern Europe": "Europe de l'Est",
    "Caribbean": "Caraïbes",
    "Northern Africa": "Afrique du Nord",
    "Southern Africa": "Afrique australe",
    "Eastern Africa": "Afrique de l'Est",
    "Western Africa": "Afrique de l'Ouest",
    "Central Asia": "Asie centrale",
    "Northern Europe": "Europe du Nord",
    "South Asia": "Asie du Sud",
    "Middle East": "Moyen-Orient",
}


def generer_phrase(row: pd.Series, rng: random.Random) -> str:
    """Génère une phrase française supply-chain à partir du profil de risque DataCo.
    
    Utilise le vocabulaire métier de make_demo.py pour rester dans la distribution
    d'entraînement du modèle TF-IDF.
    """
    is_risque = int(row.get("Late_delivery_risk", 0)) == 1

    ok_phrases = [
        "stock suffisant fournisseur local délai court",
        "délai de livraison standard sans tension capacitaire",
        "approvisionnement confirmé date de réception stable",
        "stock de sécurité supérieur au besoin hebdomadaire",
        "fournisseur fiable historique de livraisons à l'heure",
        "demande régulière niveau de stock correct",
        "lead time court rupture improbable",
        "quantité raisonnable entrepôt non saturé",
        "transport disponible sans retard constaté",
        "produit standard délai fournisseur maîtrisé",
        "niveau de stock élevé consommation stable",
        "rupture évitée grâce au stock de sécurité",
        "approvisionnement planifié sans alerte",
        "demande saisonnière anticipée avec prévision",
        "fournisseur confirmé commande passée dans les délais",
        "capacité entrepôt disponible stock de sécurité respecté",
        "commande urgente mais inventaire disponible",
    ]

    risque_phrases = [
        "rupture de stock probable délai fournisseur inconnu",
        "retard de livraison critique pénalités contractuelles",
        "fournisseur unique défaillance capacitaire signalée",
        "demande en forte hausse sans stock disponible",
        "lead time allongé transport perturbé par grève",
        "stock inférieur au seuil de sécurité rupture imminente",
        "commande urgente aucun fournisseur disponible",
        "saturation entrepôt capacité de stockage insuffisante",
        "panne équipement de production ligne arrêtée",
        "matière première stratégique pénurie mondiale",
        "délais portuaires congestion douane incertaine",
        "fluctuation de change coûts en forte hausse",
        "grève transporteur impossible de livrer à temps",
        "capacité fournisseur réduite de moitié ce trimestre",
        "stock critique approvisionnement non confirmé",
        "tension sur les délais fournisseur risque de rupture identifié",
    ]

    connecteurs = ["et", "avec", "sans", "malgré", "suite à"]
    debuts = ["Demande", "Plan", "Commande", "Ordre", "Requête", "Batch"]

    fragments = risque_phrases if is_risque else ok_phrases
    morceaux = [rng.choice(debuts)]
    morceaux.extend(rng.choice(fragments) for _ in range(rng.randint(1, 3)))

    # Avis qui se retourne (30% du temps) — comme dans make_demo.py
    if rng.random() < 0.3:
        connecteur = rng.choice(connecteurs)
        # On ajoute un fragment de l'autre classe pour tester la robustesse
        autre = ok_phrases if is_risque else risque_phrases
        morceaux.append(connecteur + " " + rng.choice(autre))

    return " ".join(morceaux)


def main() -> None:
    # Téléchargement automatique via kagglehub
    print("Téléchargement du dataset DataCo via kagglehub ...")
    dataset_path = kagglehub.dataset_download(
        "shashwatwork/dataco-smart-supply-chain-for-big-data-analysis"
    )
    print(f"  Dataset téléchargé dans : {dataset_path}")

    # Cherche le CSV dans le dossier téléchargé
    dataset_dir = Path(dataset_path)
    csv_candidates = list(dataset_dir.glob("*.csv"))
    if not csv_candidates:
        print(f"[ERREUR] Aucun fichier CSV trouvé dans {dataset_dir}")
        return

    # Prend le plus gros CSV (le dataset principal)
    raw = max(csv_candidates, key=lambda p: p.stat().st_size)
    print(f"  Fichier utilisé : {raw.name} ({raw.stat().st_size // 1024} Ko)")

    print(f"Lecture de {raw.name} ...")
    df = pd.read_csv(raw, encoding="latin-1", low_memory=False)
    print(f"  {len(df)} lignes, colonnes : {list(df.columns[:10])} ...")

    # Vérification colonne cible
    if "Late_delivery_risk" not in df.columns:
        print("[ERREUR] Colonne 'Late_delivery_risk' introuvable.")
        print(f"  Colonnes disponibles : {list(df.columns)}")
        return

    rng = random.Random(GRAINE)

    # Équilibrage : même nombre de ok et risque (max 2000 de chaque)
    df_risque = df[df["Late_delivery_risk"] == 1].sample(
        n=min(2000, (df["Late_delivery_risk"] == 1).sum()), random_state=GRAINE
    )
    df_ok = df[df["Late_delivery_risk"] == 0].sample(
        n=min(2000, (df["Late_delivery_risk"] == 0).sum()), random_state=GRAINE
    )
    df_sel = pd.concat([df_risque, df_ok]).reset_index(drop=True)

    lignes = []
    for _, row in df_sel.iterrows():
        label = "risque" if int(row["Late_delivery_risk"]) == 1 else "ok"
        texte = generer_phrase(row, rng)
        lignes.append({"text": texte, "label": label})

    rng.shuffle(lignes)

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label"])
        w.writeheader()
        w.writerows(lignes)
    print(f"  → {len(lignes)} demandes générées dans {SORTIE}")

    # Fusion avec le jeu de démo existant
    if DEMO.exists():
        df_demo = pd.read_csv(DEMO)
        df_nouveau = pd.DataFrame(lignes)
        df_fusionne = pd.concat([df_demo, df_nouveau], ignore_index=True)
        df_fusionne = df_fusionne.sample(frac=1, random_state=GRAINE).reset_index(drop=True)
        df_fusionne.to_csv(DEMO_FUSIONNE, index=False, encoding="utf-8")
        print(f"  → Fusionné avec demo_demandes.csv : {len(df_fusionne)} lignes au total")
    else:
        import shutil
        shutil.copy(SORTIE, DEMO_FUSIONNE)
        print(f"  → Copié vers {DEMO_FUSIONNE}")

    print()
    print("Maintenant lance : python src/train.py")


if __name__ == "__main__":
    main()
