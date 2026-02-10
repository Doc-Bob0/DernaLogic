"""
DermaLogic - Module GUI (Flet)
===============================

Ce module contient l'interface graphique utilisateur basée sur Flet :
- ApplicationFlet : Application principale avec navigation
- PageAccueil : Page d'analyse avec conditions et recommandations
- PageProduits : Page de gestion des produits personnalisés
- PageHistorique : Page d'historique des analyses
- PageProfil : Page de gestion du profil utilisateur
"""

from gui.app_flet import ApplicationFlet, lancer_application
from gui.pages.page_accueil import PageAccueil
from gui.pages.page_produits import PageProduits
from gui.pages.page_historique import PageHistorique
from gui.pages.page_profil import PageProfil

__all__ = [
    "ApplicationFlet",
    "lancer_application",
    "PageAccueil",
    "PageProduits",
    "PageHistorique",
    "PageProfil",
]
