"""
DermaLogic - Module Core
========================

Ce module contient la logique métier :
- Algorithme de décision dermatologique
- Modèles de données (produits, conditions, résultats)
- Gestionnaire de configuration
- Historique des analyses
- Profil utilisateur
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

from core.config import (
    VilleConfig,
    Configuration,
    GestionnaireConfig,
)

from core.historique import (
    ProduitAnalyse,
    ConditionsAnalyse,
    ResultatAnalyseHistorique,
    GestionnaireHistorique,
    creer_conditions_depuis_env,
    creer_produit_depuis_resultat,
    DUREE_RECENTES_JOURS,
)

from core.profil import (
    TypePeau,
    ProblemePeau,
    ProfilUtilisateur,
    EtatQuotidien,
    GestionnaireProfil,
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
    
    # Configuration
    "VilleConfig",
    "Configuration",
    "GestionnaireConfig",
    
    # Historique
    "ProduitAnalyse",
    "ConditionsAnalyse",
    "ResultatAnalyseHistorique",
    "GestionnaireHistorique",
    "creer_conditions_depuis_env",
    "creer_produit_depuis_resultat",
    "DUREE_RECENTES_JOURS",
    
    # Profil
    "TypePeau",
    "ProblemePeau",
    "ProfilUtilisateur",
    "EtatQuotidien",
    "GestionnaireProfil",
]

