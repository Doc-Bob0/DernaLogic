"""
DermaLogic - Module GUI
=======================

Ce module contient l'interface graphique utilisateur :
- ApplicationPrincipale : Fenêtre principale avec navigation
- PageAccueil : Page d'analyse avec conditions et recommandations
- PageProduits : Page de gestion des produits personnalisés
- Widgets personnalisés (cartes environnement, lignes moment, etc.)
"""

from gui.interface import (
    # Application
    ApplicationPrincipale,
    lancer_application,
    
    # Pages
    PageAccueil,
    PageProduits,
    
    # Widgets
    CarteEnvironnement,
    LigneMoment,
    
    # Dialogues
    FormulaireProduit,
    FenetreSelectionVille,
    
    # Gestionnaire
    GestionnaireProduits,
)

__all__ = [
    # Application
    "ApplicationPrincipale",
    "lancer_application",
    
    # Pages
    "PageAccueil",
    "PageProduits",
    
    # Widgets
    "CarteEnvironnement",
    "LigneMoment",
    
    # Dialogues
    "FormulaireProduit",
    "FenetreSelectionVille",
    
    # Gestionnaire
    "GestionnaireProduits",
]
