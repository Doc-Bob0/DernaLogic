"""
DermaLogic - Gestionnaire de Profil Utilisateur
================================================

Persistance du profil dermatologique de l'utilisateur
dans user_data/profile.json.
"""

import json
from pathlib import Path

from core.models import ProfilUtilisateur
from core.storage import obtenir_dossier_donnees


class GestionnaireProfil:
    """
    Gere le profil utilisateur persistant.

    Sauvegarde dans le dossier de donnees de la plateforme.
    """

    def __init__(self, chemin_fichier: Path = None):
        if chemin_fichier is None:
            chemin_fichier = obtenir_dossier_donnees() / "profile.json"

        self.chemin_fichier = chemin_fichier
        self.chemin_fichier.parent.mkdir(parents=True, exist_ok=True)

        self._profil = self._charger()

    def _charger(self) -> ProfilUtilisateur:
        """Charge le profil depuis le fichier JSON."""
        if not self.chemin_fichier.exists():
            return ProfilUtilisateur()

        try:
            with open(self.chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ProfilUtilisateur.depuis_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Profil] Erreur chargement: {e}")
            return ProfilUtilisateur()

    def _sauvegarder(self) -> None:
        """Sauvegarde le profil dans le fichier JSON."""
        try:
            with open(self.chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(self._profil.vers_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[Profil] Erreur sauvegarde: {e}")

    def obtenir(self) -> ProfilUtilisateur:
        """Retourne le profil actuel."""
        return self._profil

    def sauvegarder(self, profil: ProfilUtilisateur) -> None:
        """Sauvegarde un nouveau profil."""
        self._profil = profil
        self._sauvegarder()
