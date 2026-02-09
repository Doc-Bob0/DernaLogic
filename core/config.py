"""
DermaLogic - Gestionnaire de Configuration
==========================================

Ce module gère la persistance de la configuration :
- Ville actuelle avec ses données météo
- Villes favorites avec leurs données météo mises en cache
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class VilleConfig:
    """
    Configuration d'une ville avec ses données météo en cache.
    
    Attributes:
        nom: Nom de la ville
        pays: Nom du pays
        latitude: Latitude
        longitude: Longitude
        derniere_maj: Date/heure de la dernière mise à jour météo
        indice_uv: Dernier indice UV récupéré
        humidite: Dernière humidité récupérée
        temperature: Dernière température récupérée
        pm2_5: Dernier PM2.5 récupéré
    """
    nom: str
    pays: str
    latitude: float
    longitude: float
    derniere_maj: str = ""
    indice_uv: float = 0.0
    humidite: float = 50.0
    temperature: float = 20.0
    pm2_5: Optional[float] = None
    
    def vers_dict(self) -> dict:
        """Convertit en dictionnaire pour JSON."""
        return asdict(self)
    
    @classmethod
    def depuis_dict(cls, data: dict) -> "VilleConfig":
        """Crée depuis un dictionnaire."""
        return cls(
            nom=data.get("nom", "Paris"),
            pays=data.get("pays", "France"),
            latitude=data.get("latitude", 48.8566),
            longitude=data.get("longitude", 2.3522),
            derniere_maj=data.get("derniere_maj", ""),
            indice_uv=data.get("indice_uv", 0.0),
            humidite=data.get("humidite", 50.0),
            temperature=data.get("temperature", 20.0),
            pm2_5=data.get("pm2_5")
        )
    
    def __str__(self) -> str:
        return f"{self.nom}, {self.pays}"


@dataclass
class Configuration:
    """
    Configuration globale de l'application.
    
    Attributes:
        ville_actuelle: Ville actuellement sélectionnée
        villes_favorites: Liste des villes en favoris
    """
    ville_actuelle: VilleConfig = field(default_factory=lambda: VilleConfig(
        nom="Paris", pays="France", latitude=48.8566, longitude=2.3522
    ))
    villes_favorites: list[VilleConfig] = field(default_factory=list)
    
    def vers_dict(self) -> dict:
        """Convertit en dictionnaire pour JSON."""
        return {
            "ville_actuelle": self.ville_actuelle.vers_dict(),
            "villes_favorites": [v.vers_dict() for v in self.villes_favorites]
        }
    
    @classmethod
    def depuis_dict(cls, data: dict) -> "Configuration":
        """Crée depuis un dictionnaire."""
        ville_actuelle = VilleConfig.depuis_dict(data.get("ville_actuelle", {}))
        favorites = [
            VilleConfig.depuis_dict(v) 
            for v in data.get("villes_favorites", [])
        ]
        return cls(ville_actuelle=ville_actuelle, villes_favorites=favorites)


# =============================================================================
# GESTIONNAIRE DE CONFIGURATION
# =============================================================================

class GestionnaireConfig:
    """
    Gère la configuration persistante de l'application.
    
    Sauvegarde automatiquement dans user_data/config.json :
    - La ville actuelle avec ses données météo
    - Les villes favorites avec leurs données météo en cache
    
    Note: Le dossier user_data/ est ignoré par git pour ne pas
    partager les données personnelles de l'utilisateur.
    """
    
    def __init__(self, chemin_fichier: Path = None):
        if chemin_fichier is None:
            # Utilise user_data/ qui est ignoré par git
            chemin_fichier = Path(__file__).parent.parent / "user_data" / "config.json"
        
        self.chemin_fichier = chemin_fichier
        self.chemin_fichier.parent.mkdir(parents=True, exist_ok=True)
        
        self.config = self._charger()
    
    def _charger(self) -> Configuration:
        """Charge la configuration depuis le fichier JSON."""
        if not self.chemin_fichier.exists():
            return Configuration()
        
        try:
            with open(self.chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Configuration.depuis_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Config] Erreur chargement: {e}")
            return Configuration()
    
    def _sauvegarder(self) -> None:
        """Sauvegarde la configuration dans le fichier JSON."""
        try:
            with open(self.chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(self.config.vers_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[Config] Erreur sauvegarde: {e}")
    
    # =========================================================================
    # VILLE ACTUELLE
    # =========================================================================
    
    def obtenir_ville_actuelle(self) -> VilleConfig:
        """Retourne la ville actuelle."""
        return self.config.ville_actuelle
    
    def definir_ville_actuelle(self, ville: VilleConfig) -> None:
        """Définit la ville actuelle et sauvegarde."""
        self.config.ville_actuelle = ville
        self._sauvegarder()
    
    def mettre_a_jour_meteo_actuelle(
        self,
        indice_uv: float,
        humidite: float,
        temperature: float,
        pm2_5: Optional[float]
    ) -> None:
        """Met à jour les données météo de la ville actuelle."""
        ville = self.config.ville_actuelle
        ville.indice_uv = indice_uv
        ville.humidite = humidite
        ville.temperature = temperature
        ville.pm2_5 = pm2_5
        ville.derniere_maj = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._sauvegarder()
    
    # =========================================================================
    # FAVORIS
    # =========================================================================
    
    def obtenir_favorites(self) -> list[VilleConfig]:
        """Retourne la liste des villes favorites."""
        return self.config.villes_favorites.copy()
    
    def est_favorite(self, nom: str, pays: str) -> bool:
        """Vérifie si une ville est en favoris."""
        for fav in self.config.villes_favorites:
            if fav.nom == nom and fav.pays == pays:
                return True
        return False
    
    def ajouter_favorite(self, ville: VilleConfig) -> None:
        """Ajoute une ville aux favoris."""
        # Vérifier si déjà en favoris
        if not self.est_favorite(ville.nom, ville.pays):
            self.config.villes_favorites.append(ville)
            self._sauvegarder()
    
    def supprimer_favorite(self, nom: str, pays: str) -> None:
        """Supprime une ville des favoris."""
        self.config.villes_favorites = [
            v for v in self.config.villes_favorites
            if not (v.nom == nom and v.pays == pays)
        ]
        self._sauvegarder()
    
    def basculer_favorite(self, ville: VilleConfig) -> bool:
        """
        Bascule l'état favori d'une ville.
        
        Returns:
            True si ajouté, False si supprimé
        """
        if self.est_favorite(ville.nom, ville.pays):
            self.supprimer_favorite(ville.nom, ville.pays)
            return False
        else:
            self.ajouter_favorite(ville)
            return True
    
    def mettre_a_jour_meteo_favorite(
        self,
        nom: str,
        pays: str,
        indice_uv: float,
        humidite: float,
        temperature: float,
        pm2_5: Optional[float]
    ) -> None:
        """Met à jour les données météo d'une ville favorite."""
        for ville in self.config.villes_favorites:
            if ville.nom == nom and ville.pays == pays:
                ville.indice_uv = indice_uv
                ville.humidite = humidite
                ville.temperature = temperature
                ville.pm2_5 = pm2_5
                ville.derniere_maj = datetime.now().strftime("%Y-%m-%d %H:%M")
                break
        self._sauvegarder()


# =============================================================================
# TEST DU MODULE
# =============================================================================

if __name__ == "__main__":
    print("Test du gestionnaire de configuration")
    print("=" * 50)
    
    config = GestionnaireConfig()
    
    print(f"Ville actuelle: {config.obtenir_ville_actuelle()}")
    print(f"Favoris: {[str(v) for v in config.obtenir_favorites()]}")
