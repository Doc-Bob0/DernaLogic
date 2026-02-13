"""
DermaLogic - Moteur de Decision Dermatologique
===============================================

Application qui adapte votre protocole de soins aux conditions
environnementales (UV, humidite, pollution) pour maximiser
l'efficacite de vos actifs.

Point d'entree principal de l'application.
"""

import sys
import logging
from pathlib import Path

# Ajout du chemin du projet pour les imports
sys.path.insert(0, str(Path(__file__).parent))

# Supprimer les erreurs asyncio a la fermeture sur Windows
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

import flet as ft
from gui.app import main as flet_main


def main():
    """Lance l'application DermaLogic."""
    print("=" * 50)
    print("  DermaLogic - Moteur de Decision Dermatologique")
    print("=" * 50)
    print()

    try:
        ft.run(flet_main)
    except (ConnectionResetError, OSError):
        pass


if __name__ == "__main__":
    main()
