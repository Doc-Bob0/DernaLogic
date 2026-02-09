"""
DermaLogic - Module API
=======================

Ce module gère les interactions avec les APIs externes :
- Open-Meteo pour les données météorologiques et le géocodage
- Gemini pour les fonctionnalités d'intelligence artificielle
"""

from api.open_meteo import (
    # Client principal
    ClientOpenMeteo,
    
    # Structures de données
    DonneesEnvironnementales,
    Localisation,
    
    # Fonctions utilitaires
    obtenir_conditions_actuelles,
    rechercher_villes,
)

from api.gemini import (
    # Client IA
    ClientGemini,
    
    # Structure résultat
    ResultatAnalyseIA,
)

__all__ = [
    # Open-Meteo
    "ClientOpenMeteo",
    "DonneesEnvironnementales",
    "Localisation",
    "obtenir_conditions_actuelles",
    "rechercher_villes",
    
    # Gemini
    "ClientGemini",
    "ResultatAnalyseIA",
]
