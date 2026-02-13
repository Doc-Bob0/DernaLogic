"""
DermaLogic - Gestionnaire de Parametres
========================================

Persistance des parametres de l'application (cle API, etc.)
dans user_data/settings.json.
"""

import json
from pathlib import Path

from core.models import Settings


class GestionnaireSettings:
    """
    Gere les parametres persistants de l'application.

    Sauvegarde dans user_data/settings.json.
    """

    def __init__(self, chemin_fichier: Path = None):
        if chemin_fichier is None:
            chemin_fichier = Path(__file__).parent.parent / "user_data" / "settings.json"

        self.chemin_fichier = chemin_fichier
        self.chemin_fichier.parent.mkdir(parents=True, exist_ok=True)

        self._settings = self._charger()

    def _charger(self) -> Settings:
        """Charge les parametres depuis le fichier JSON."""
        if not self.chemin_fichier.exists():
            return Settings()

        try:
            with open(self.chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Settings.depuis_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Settings] Erreur chargement: {e}")
            return Settings()

    def _sauvegarder(self) -> None:
        """Sauvegarde les parametres dans le fichier JSON."""
        try:
            with open(self.chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(self._settings.vers_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[Settings] Erreur sauvegarde: {e}")

    def obtenir(self) -> Settings:
        """Retourne les parametres actuels."""
        return self._settings

    def sauvegarder(self, settings: Settings) -> None:
        """Sauvegarde de nouveaux parametres."""
        self._settings = settings
        self._sauvegarder()

    def obtenir_gemini_key(self) -> str:
        """Retourne la cle API Gemini."""
        return self._settings.gemini_api_key

    def definir_gemini_key(self, key: str) -> None:
        """Definit la cle API Gemini et sauvegarde."""
        self._settings.gemini_api_key = key
        self._sauvegarder()
