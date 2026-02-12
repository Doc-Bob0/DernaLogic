"""
DermaLogic - Module GUI (Flet)
===============================

Interface graphique responsive avec Flet.
Fonctionne en mode desktop et web, avec layouts adaptatifs mobile/desktop.

Structure :
- app.py : Orchestrateur principal
- theme.py : Couleurs et theme
- state.py : Etat partage
- data.py : Gestionnaire de produits
- components/ : Widgets reutilisables
- pages/ : Pages principales
- dialogs/ : Dialogues modaux
"""

from gui.app import main as lancer_application
from gui.data import GestionnaireProduits

__all__ = [
    "lancer_application",
    "GestionnaireProduits",
]
