"""
DermaLogic - Moteur de Décision Dermatologique
===============================================

Application qui adapte votre protocole de soins aux conditions 
environnementales (UV, humidité, pollution) pour maximiser 
l'efficacité de vos actifs.

Point d'entrée principal de l'application.
"""

import sys
from pathlib import Path

# Ajout du chemin du projet pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from gui.app_flet import lancer_application


def main():
    """Lance l'application DermaLogic."""
    print("=" * 50)
    print("  DermaLogic - Moteur de Decision Dermatologique")
    print("=" * 50)
    print()
    
    lancer_application()


if __name__ == "__main__":
    main()
