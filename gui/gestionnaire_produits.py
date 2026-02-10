"""
Gestionnaire de produits pour DermaLogic.

Gère la persistance JSON des produits personnalisés de l'utilisateur.
"""

from pathlib import Path
import json

from core.algorithme import ProduitDerma


class GestionnaireProduits:
    """
    Gère les produits personnalisés avec persistance JSON.
    
    Les produits sont sauvegardés dans user_data/produits_derma.json
    et chargés automatiquement au démarrage.
    
    Note: Le dossier user_data/ est ignoré par git pour ne pas
    partager les données personnelles de l'utilisateur.
    
    Attributes:
        chemin_fichier: Chemin vers le fichier JSON
        produits: Liste des produits en mémoire
    """
    
    def __init__(self, chemin_fichier: Path = None):
        """
        Initialise le gestionnaire.
        
        Args:
            chemin_fichier: Chemin du fichier JSON (optionnel)
        """
        if chemin_fichier is None:
            # Utilise user_data/ qui est ignoré par git
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
                    indent=2
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
