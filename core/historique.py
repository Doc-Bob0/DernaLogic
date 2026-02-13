"""
DermaLogic - Gestionnaire d'Historique
=======================================

Persistance de l'historique des analyses IA
dans user_data/historique.json.
"""

import json
from pathlib import Path

from core.models import EntreeHistorique


class GestionnaireHistorique:
    """
    Gere l'historique des analyses persistant.

    Sauvegarde dans user_data/historique.json.
    """

    def __init__(self, chemin_fichier: Path = None):
        if chemin_fichier is None:
            chemin_fichier = Path(__file__).parent.parent / "user_data" / "historique.json"

        self.chemin_fichier = chemin_fichier
        self.chemin_fichier.parent.mkdir(parents=True, exist_ok=True)

        self._historique: list[EntreeHistorique] = self._charger()

    def _charger(self) -> list[EntreeHistorique]:
        """Charge l'historique depuis le fichier JSON."""
        if not self.chemin_fichier.exists():
            return []

        try:
            with open(self.chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [EntreeHistorique.depuis_dict(e) for e in data]
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Historique] Erreur chargement: {e}")
            return []

    def _sauvegarder(self) -> None:
        """Sauvegarde l'historique dans le fichier JSON."""
        try:
            with open(self.chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(
                    [e.vers_dict() for e in self._historique],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except IOError as e:
            print(f"[Historique] Erreur sauvegarde: {e}")

    def obtenir_tous(self) -> list[EntreeHistorique]:
        """Retourne tout l'historique (plus recent en premier)."""
        return sorted(self._historique, key=lambda e: e.date, reverse=True)

    def obtenir_recents(self, n: int = 3) -> list[EntreeHistorique]:
        """Retourne les n dernieres analyses (plus recent en premier)."""
        return self.obtenir_tous()[:n]

    def ajouter(self, entree: EntreeHistorique) -> None:
        """Ajoute une entree dans l'historique et sauvegarde."""
        self._historique.append(entree)
        self._sauvegarder()
