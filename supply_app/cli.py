"""Commande `supply` (TP6) : argparse et trois sous-commandes."""
from __future__ import annotations

import argparse
import json
import sys

from supply_app import __version__


def _predire(args: argparse.Namespace) -> int:
    from supply_app.predict import load_model

    try:
        clf = load_model()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    texte = " ".join(args.texte)
    print(json.dumps(clf.predict(texte), ensure_ascii=False))
    return 0


def _servir(args: argparse.Namespace) -> int:  # pragma: no cover - lance un serveur
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=args.port)
    return 0


def _ui(args: argparse.Namespace) -> int:  # pragma: no cover - lance Streamlit
    import subprocess

    return subprocess.call([sys.executable, "-m", "streamlit", "run", "ui/app.py"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="supply",
        description="Agent de planification de la chaine d'approvisionnement",
    )
    parser.add_argument(
        "--version", action="version", version=f"supply-plan-app {__version__}"
    )
    commandes = parser.add_subparsers(dest="commande", required=True)

    predire = commandes.add_parser("predict", help="classe une demande, sans serveur")
    predire.add_argument("texte", nargs="+", help="la demande a analyser")
    predire.set_defaults(fonction=_predire)

    servir = commandes.add_parser("serve", help="lance l'API")
    servir.add_argument("--port", type=int, default=8000)
    servir.set_defaults(fonction=_servir)

    interface = commandes.add_parser(
        "ui", help="lance la page Streamlit (l'API doit tourner)"
    )
    interface.set_defaults(fonction=_ui)

    args = parser.parse_args(argv)
    return int(args.fonction(args))


if __name__ == "__main__":
    raise SystemExit(main())
