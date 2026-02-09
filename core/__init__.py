"""
DermaLogic - Module Core
========================

Ce module contient la logique métier :
- Algorithme de décision dermatologique
- Modèles de données (produits, conditions, résultats)
- Enums et constantes
"""

from core.algorithme import (
    # Énumérations
    Categorie,
    ActiveTag,
    MomentUtilisation,
    
    # Structures de données
    ProduitDerma,
    ConditionsEnvironnementales,
    ResultatMoment,
    ResultatDecision,
    
    # Moteur de décision
    MoteurDecision,
    
    # Constantes
    SEUIL_UV_CRITIQUE,
    SEUIL_HUMIDITE_BASSE,
    SEUIL_HUMIDITE_HAUTE,
    SEUIL_PM25_POLLUTION,
)

__all__ = [
    # Énumérations
    "Categorie",
    "ActiveTag",
    "MomentUtilisation",
    
    # Structures de données
    "ProduitDerma",
    "ConditionsEnvironnementales",
    "ResultatMoment",
    "ResultatDecision",
    
    # Moteur
    "MoteurDecision",
    
    # Constantes
    "SEUIL_UV_CRITIQUE",
    "SEUIL_HUMIDITE_BASSE",
    "SEUIL_HUMIDITE_HAUTE",
    "SEUIL_PM25_POLLUTION",
]
