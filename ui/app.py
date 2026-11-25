"""Interface Streamlit (TP5) : client de l'API, comme un autre.

Deux onglets : une demande, ou un fichier de demandes CSV.
Nouvelles fonctionnalités :
- Historique des prédictions sauvegardé en SQLite (data/historique.db)
- Graphique de confiance sur l'onglet "Une demande"
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from ui import client

# --- Base SQLite -------------------------------------------------------
DB_PATH = _ROOT / "data" / "historique.db"


def init_db() -> None:
    """Crée la table historique si elle n'existe pas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS historique (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                horodatage TEXT NOT NULL,
                texte     TEXT NOT NULL,
                verdict   TEXT NOT NULL,
                confiance REAL
            )
        """)


def sauvegarder(texte: str, verdict: str, confiance: float | None) -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO historique (horodatage, texte, verdict, confiance) VALUES (?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), texte, verdict, confiance),
        )


def charger_historique() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame(columns=["id", "horodatage", "texte", "verdict", "confiance"])
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql("SELECT * FROM historique ORDER BY id DESC LIMIT 100", con)


def vider_historique() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM historique")


# --- Constantes --------------------------------------------------------
ETIQUETTES = {
    "OK": "Demande OK",
    "RISQUE": "Demande a risque",
    "INDETERMINE": "A verifier",
}

COULEURS = {
    "OK": "🟢",
    "RISQUE": "🔴",
    "INDETERMINE": "🟡",
}


# --- Pages -------------------------------------------------------------
def afficher_verdict(rep, texte: str) -> None:
    if not rep.ok:
        st.error(rep.message or "Reponse invalide de l'API.")
        return

    label = rep.label or "INDETERMINE"
    score = rep.score or 0.0

    # Verdict + score
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            f"{COULEURS.get(label, '')} {ETIQUETTES.get(label, label)}",
            f"{score * 100:.0f}%",
        )

    # Graphique de confiance en HTML pur
    with col2:
        score_ok     = score if label == "OK"     else round(1 - score, 4)
        score_risque = score if label == "RISQUE" else round(1 - score, 4)
        st.markdown("**Distribution de confiance**")
        st.markdown(f"""
<div style="margin-top:8px">
  <div style="margin-bottom:6px">
    🟢 <b>OK</b> &nbsp; {score_ok*100:.1f}%
    <div style="background:#1e1e1e;border-radius:4px;height:18px;width:100%">
      <div style="background:#2ecc71;height:18px;border-radius:4px;width:{score_ok*100:.1f}%"></div>
    </div>
  </div>
  <div>
    🔴 <b>RISQUE</b> &nbsp; {score_risque*100:.1f}%
    <div style="background:#1e1e1e;border-radius:4px;height:18px;width:100%">
      <div style="background:#e74c3c;height:18px;border-radius:4px;width:{score_risque*100:.1f}%"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Sauvegarde dans l'historique
    sauvegarder(texte, label, score)
    st.caption("✅ Enregistré dans l'historique.")


def page_avis() -> None:
    texte = st.text_area(
        "Demande a classer",
        value="Stock suffisant et delai de livraison standard, sans tension capacitaire",
        height=120,
    )
    if st.button("Analyser"):
        with client.creer_session() as session:
            rep = client.predire(session, texte)
            afficher_verdict(rep, texte)

    # --- Historique ---
    st.divider()
    st.subheader("📋 Historique des prédictions")

    col_refresh, col_vider = st.columns([3, 1])
    with col_vider:
        if st.button("🗑️ Vider l'historique"):
            vider_historique()
            st.success("Historique vidé.")
            st.rerun()

    df_hist = charger_historique()
    if df_hist.empty:
        st.info("Aucune prédiction enregistrée pour l'instant.")
    else:
        df_hist[""] = df_hist["verdict"].map(COULEURS)

        # Table HTML pure
        rows = ""
        for _, r in df_hist.head(20).iterrows():
            conf = f"{r['confiance']*100:.1f}%" if r['confiance'] else "-"
            rows += f"<tr><td>{r['']}</td><td>{r['horodatage']}</td><td style='max-width:400px'>{r['texte']}</td><td><b>{r['verdict']}</b></td><td>{conf}</td></tr>"
        st.markdown(f"""
<table style="width:100%;border-collapse:collapse;font-size:13px">
  <thead><tr style="border-bottom:1px solid #444">
    <th></th><th style="text-align:left">Date</th>
    <th style="text-align:left">Demande</th>
    <th style="text-align:left">Verdict</th>
    <th style="text-align:left">Confiance</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
""", unsafe_allow_html=True)

        st.markdown("**Répartition globale des verdicts**")
        counts = df_hist["verdict"].value_counts()
        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 OK",          counts.get("OK", 0))
        c2.metric("🔴 RISQUE",      counts.get("RISQUE", 0))
        c3.metric("🟡 INDÉTERMINÉ", counts.get("INDETERMINE", 0))


def page_fichier() -> None:
    fichier = st.file_uploader("Fichier CSV (colonne text)", type="csv")
    lignes = None
    if fichier is not None:
        import io
        lignes = [str(x) for x in pd.read_csv(io.BytesIO(fichier.getvalue()))["text"]]
    else:
        exemple = _ROOT / "data" / "demandes_exemple.csv"
        if exemple.exists():
            st.caption(f"Exemple charge : {exemple.name}")
            lignes = [str(x) for x in pd.read_csv(exemple)["text"]]

    if not lignes:
        st.info("Deposez un CSV ou laissez l'exemple charge.")
        return

    if st.button("Analyser le fichier"):
        resultats = []
        with client.creer_session() as session:
            for ligne in lignes:
                rep = client.predire(session, ligne)
                verdict = rep.label if rep.ok else "ERREUR"
                confiance = rep.score if rep.ok else None
                resultats.append({
                    "demande": ligne,
                    "verdict": verdict,
                    "confiance": confiance,
                })
                if rep.ok:
                    sauvegarder(ligne, verdict, confiance)

        df = pd.DataFrame(resultats)
        # Table HTML pure pour le fichier
        df[""] = df["verdict"].map(COULEURS)
        rows2 = ""
        for _, r in df.iterrows():
            conf = f"{r['confiance']*100:.1f}%" if r['confiance'] else "-"
            rows2 += f"<tr><td>{r['']}</td><td style='max-width:500px'>{r['demande']}</td><td><b>{r['verdict']}</b></td><td>{conf}</td></tr>"
        st.markdown(f"""
<table style="width:100%;border-collapse:collapse;font-size:13px">
  <thead><tr style="border-bottom:1px solid #444">
    <th></th><th style="text-align:left">Demande</th>
    <th style="text-align:left">Verdict</th>
    <th style="text-align:left">Confiance</th>
  </tr></thead>
  <tbody>{rows2}</tbody>
</table>
""", unsafe_allow_html=True)

        nb_ok = int((df["verdict"] == "OK").sum())
        nb_risque = int((df["verdict"] == "RISQUE").sum())
        nb_verif = int((df["verdict"] == "INDETERMINE").sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 OK", nb_ok)
        c2.metric("🔴 A risque", nb_risque)
        c3.metric("🟡 A verifier", nb_verif)

        st.markdown("**Distribution des verdicts**")
        counts2 = df["verdict"].value_counts()
        d1, d2, d3 = st.columns(3)
        d1.metric("🟢 OK",          counts2.get("OK", 0))
        d2.metric("🔴 RISQUE",      counts2.get("RISQUE", 0))
        d3.metric("🟡 INDÉTERMINÉ", counts2.get("INDETERMINE", 0))

        # Distribution des scores de confiance sous forme de texte
        df_conf = df[df["confiance"].notna()]
        if not df_conf.empty:
            st.markdown("**Scores de confiance (min / moy / max)**")
            st.markdown(
                f"Min : `{df_conf['confiance'].min():.2f}` &nbsp;|&nbsp; "
                f"Moy : `{df_conf['confiance'].mean():.2f}` &nbsp;|&nbsp; "
                f"Max : `{df_conf['confiance'].max():.2f}`"
            )

        st.download_button(
            "⬇️ Telecharger les resultats",
            df.drop(columns=[""]).to_csv(index=False),
            "resultats_planification.csv",
            "text/csv",
        )


def main() -> None:
    st.set_page_config(
        page_title="Agent Supply Chain",
        page_icon="🏭",
        layout="wide",
    )
    init_db()

    st.title("🏭 Agent de planification de la chaine d'approvisionnement")
    st.caption(
        "Classe une demande en OK (planifiable) ou RISQUE (rupture / retard), "
        "ou INDETERMINE sous 60 % de confiance."
    )

    onglet1, onglet2 = st.tabs(["🔍 Une demande", "📂 Un fichier de demandes"])
    with onglet1:
        page_avis()
    with onglet2:
        page_fichier()


if __name__ == "__main__":
    main()
