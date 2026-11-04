"""Adaptateur API <-> modele (TP3/TP4) : seuil d'abstention, chargement."""
from __future__ import annotations

from supply_app.predict import SEUIL_CONFIANCE, Classifieur, load_model

__all__ = ["SEUIL_CONFIANCE", "Classifieur", "load_model"]
