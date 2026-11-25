"""Interface Streamlit (TP5) : client de l'API, comme un autre.

Deux onglets : une demande, ou un fichier de demandes CSV.
L'adresse de l'API est dans ui/client.py (API_URL).
"""
from __future__ import annotations

import sys
from pathlib import Path

# S'assure que la racine du projet est dans sys.path (nécessaire quand
# Streamlit est lancé via `streamlit run ui/app.py`)
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from ui import client

ETIQUETTES = {
    "OK": "Demande OK",
    "RISQUE": "Demande a risque",
    "INDETERMINE": "A verifier",
}


def afficher_verdict(rep) -> None:
    if not rep.ok:
        st.error(rep.message or "Reponse invalide de l'API.")
        return
    label = rep.label or "INDETERMINE"
    st.metric(ETIQUETTES.get(label, label), f"{(rep.score or 0) * 100:.0f}%")


def page_avis() -> None:
    texte = st.text_area(
        "Demande a classer",
        value="Stock suffisant et delai de livraison standard, sans tension capacitaire",
        height=120,
    )
    if st.button("Analyser"):
        with client.creer_session() as session:
            afficher_verdict(client.predire(session, texte))


def page_fichier() -> None:
    fichier = st.file_uploader("Fichier CSV (colonne text)", type="csv")
    lignes = None
    if fichier is not None:
        import io

        import pandas as pd

        lignes = [str(x) for x in pd.read_csv(io.BytesIO(fichier.getvalue()))["text"]]
    else:
        exemple = Path(__file__).resolve().parent.parent / "data" / "demandes_exemple.csv"
        if exemple.exists():
            st.caption(f"Exemple charge : {exemple.name}")
            import pandas as pd

            lignes = [str(x) for x in pd.read_csv(exemple)["text"]]
    if not lignes:
        st.info("Deposez un CSV ou laissez l'exemple charge.")
        return
    if st.button("Analyser le fichier"):
        resultats = []
        with client.creer_session() as session:
            for ligne in lignes:
                rep = client.predire(session, ligne)
                resultats.append(
                    {
                        "demande": ligne,
                        "verdict": rep.label if rep.ok else "ERREUR",
                        "confiance": rep.score if rep.ok else None,
                    }
                )
        import pandas as pd

        df = pd.DataFrame(resultats)
        st.dataframe(df, use_container_width=True)
        nb_ok = int((df["verdict"] == "OK").sum())
        nb_risque = int((df["verdict"] == "RISQUE").sum())
        nb_verif = int((df["verdict"] == "INDETERMINE").sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("OK", nb_ok)
        c2.metric("a risque", nb_risque)
        c3.metric("a verifier", nb_verif)
        if nb_ok:
            st.bar_chart(df["verdict"].value_counts())
        df.to_csv("resultats_planification.csv", index=False)
        st.download_button(
            "Telecharger les resultats",
            df.to_csv(index=False),
            "resultats_planification.csv",
            "text/csv",
        )


def main() -> None:
    st.title("Agent de planification de la chaine d'approvisionnement")
    st.caption(
        "Classe une demande en OK (planifiable) ou RISQUE (rupture / retard), "
        "ou INDETERMINE sous 60 % de confiance."
    )
    onglet1, onglet2 = st.tabs(["Une demande", "Un fichier de demandes"])
    with onglet1:
        page_avis()
    with onglet2:
        page_fichier()


if __name__ == "__main__":
    main()
