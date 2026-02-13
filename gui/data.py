"""
DermaLogic - Gestionnaire de Produits
=====================================

Persistance JSON des produits utilisateur.
"""

import json
from pathlib import Path

from core.models import ProduitDerma


class GestionnaireProduits:
    """
    Gere les produits personnalises avec persistance JSON.

    Les produits sont sauvegardes dans user_data/produits_derma.json
    et charges automatiquement au demarrage.
    """

    def __init__(self, chemin_fichier: Path = None):
        if chemin_fichier is None:
            chemin_fichier = Path(__file__).parent.parent / "user_data" / "produits_derma.json"

        self.chemin_fichier = chemin_fichier
        self.chemin_fichier.parent.mkdir(parents=True, exist_ok=True)

        self.produits: list[ProduitDerma] = []
        self._charger()

    def _charger(self) -> None:
        """Charge les produits depuis le fichier JSON."""
        if not self.chemin_fichier.exists():
            return

        try:
            with open(self.chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.produits = [ProduitDerma.depuis_dict(p) for p in data]
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"[GestionnaireProduits] Erreur chargement: {e}")
            self.produits = []

    def _sauvegarder(self) -> None:
        """Sauvegarde les produits dans le fichier JSON."""
        try:
            with open(self.chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(
                    [p.vers_dict() for p in self.produits],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except IOError as e:
            print(f"[GestionnaireProduits] Erreur sauvegarde: {e}")

    def obtenir_tous(self) -> list[ProduitDerma]:
        """Retourne une copie de la liste des produits."""
        return self.produits.copy()

    def ajouter(self, produit: ProduitDerma) -> None:
        """Ajoute un produit et sauvegarde."""
        self.produits.append(produit)
        self._sauvegarder()

    def supprimer(self, index: int) -> None:
        """Supprime un produit par son index et sauvegarde."""
        if 0 <= index < len(self.produits):
            self.produits.pop(index)
            self._sauvegarder()
