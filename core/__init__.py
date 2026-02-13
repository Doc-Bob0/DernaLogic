"""
DermaLogic - Module Core
========================

Ce module contient la logique metier :
- Modeles de donnees centralises (produits, profil, historique)
- Analyseur IA (remplace l'ancien MoteurDecision)
- Gestionnaires de persistence (profil, historique, settings)
"""

from core.models import (
    # Enumerations
    Categorie,
    ActiveTag,
    MomentUtilisation,
    TypePeau,
    TrancheAge,
    ObjectifPeau,

    # Structures de donnees
    ProduitDerma,
    ProfilUtilisateur,
    EntreeHistorique,
    Settings,
)

from core.algorithme import (
    # Legacy (deprecie)
    ConditionsEnvironnementales,
    ResultatMoment,
    ResultatDecision,
    MoteurDecision,

    # Constantes
    SEUIL_UV_CRITIQUE,
    SEUIL_HUMIDITE_BASSE,
    SEUIL_HUMIDITE_HAUTE,
    SEUIL_PM25_POLLUTION,
)

__all__ = [
    # Enumerations
    "Categorie",
    "ActiveTag",
    "MomentUtilisation",
    "TypePeau",
    "TrancheAge",
    "ObjectifPeau",

    # Structures de donnees
    "ProduitDerma",
    "ProfilUtilisateur",
    "EntreeHistorique",
    "Settings",

    # Legacy
    "ConditionsEnvironnementales",
    "ResultatMoment",
    "ResultatDecision",
    "MoteurDecision",

    # Constantes
    "SEUIL_UV_CRITIQUE",
    "SEUIL_HUMIDITE_BASSE",
    "SEUIL_HUMIDITE_HAUTE",
    "SEUIL_PM25_POLLUTION",
]
