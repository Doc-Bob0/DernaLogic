"""
DermaLogic - Client API Open-Meteo
==================================

Ce module fournit :
- ClientOpenMeteo : Client pour récupérer les données météo et air quality
- rechercher_villes : Fonction de géocodage pour chercher des villes
- DonneesEnvironnementales : Structure des données récupérées
- Localisation : Structure pour les coordonnées d'une ville
"""

import requests
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class DonneesEnvironnementales:
    """
    Données environnementales récupérées pour une localisation.
    
    Attributes:
        date: Date de la mesure (YYYY-MM-DD)
        heure: Heure de la mesure (HH:MM)
        indice_uv: Indice UV actuel (0-11+)
        indice_uv_max: Indice UV maximum du jour
        humidite_relative: Humidité en pourcentage (0-100)
        temperature: Température en degrés Celsius
        pm2_5: Particules fines PM2.5 en µg/m³ (optionnel)
        pm10: Particules grossières PM10 en µg/m³ (optionnel)
    """
    date: str
    heure: str
    indice_uv: float
    indice_uv_max: float
    humidite_relative: float
    temperature: float
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    
    @property
    def niveau_uv(self) -> str:
        """Catégorisation OMS du niveau UV."""
        if self.indice_uv < 3:
            return "Faible"
        elif self.indice_uv < 6:
            return "Modere"
        elif self.indice_uv < 8:
            return "Eleve"
        elif self.indice_uv < 11:
            return "Tres eleve"
        else:
            return "Extreme"
    
    @property
    def niveau_humidite(self) -> str:
        """Catégorisation du niveau d'humidité."""
        if self.humidite_relative < 30:
            return "Tres sec"
        elif self.humidite_relative < 50:
            return "Sec"
        elif self.humidite_relative < 70:
            return "Normal"
        else:
            return "Humide"
    
    @property
    def niveau_pollution(self) -> str:
        """Catégorisation de la pollution (basée sur PM2.5 OMS)."""
        if self.pm2_5 is None:
            return "Inconnu"
        if self.pm2_5 < 10:
            return "Excellent"
        elif self.pm2_5 < 25:
            return "Bon"
        elif self.pm2_5 < 50:
            return "Modere"
        elif self.pm2_5 < 75:
            return "Mauvais"
        else:
            return "Tres mauvais"


@dataclass
class Localisation:
    """
    Représente une localisation géographique.
    
    Attributes:
        nom: Nom de la ville
        pays: Nom du pays
        latitude: Latitude en degrés décimaux
        longitude: Longitude en degrés décimaux
    """
    nom: str
    pays: str
    latitude: float
    longitude: float
    
    def __str__(self) -> str:
        return f"{self.nom}, {self.pays}"


# =============================================================================
# FONCTION DE GÉOCODAGE
# =============================================================================

def rechercher_villes(query: str, limit: int = 5) -> list[Localisation]:
    """
    Recherche des villes via l'API Open-Meteo Geocoding.
    
    Args:
        query: Nom de la ville à rechercher
        limit: Nombre maximum de résultats (défaut: 5)
    
    Returns:
        Liste d'objets Localisation correspondant à la recherche
    
    Example:
        >>> villes = rechercher_villes("Lyon")
        >>> print(villes[0])
        Lyon, France
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": query,
        "count": limit,
        "language": "fr",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        resultats = []
        for r in data.get("results", []):
            resultats.append(Localisation(
                nom=r.get("name", ""),
                pays=r.get("country", ""),
                latitude=r.get("latitude", 0),
                longitude=r.get("longitude", 0)
            ))
        return resultats
        
    except requests.RequestException as e:
        print(f"[API] Erreur recherche ville: {e}")
        return []


# =============================================================================
# CLIENT OPEN-METEO
# =============================================================================

class ClientOpenMeteo:
    """
    Client pour les APIs Open-Meteo (météo et qualité de l'air).
    
    Attributes:
        latitude: Latitude de la localisation courante
        longitude: Longitude de la localisation courante
        nom_ville: Nom affiché de la ville courante
    
    Example:
        >>> client = ClientOpenMeteo()
        >>> donnees = client.obtenir_donnees_jour()
        >>> print(f"UV: {donnees.indice_uv}")
    """
    
    BASE_URL_METEO = "https://api.open-meteo.com/v1/forecast"
    BASE_URL_AIR = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    def __init__(
        self,
        latitude: float = 48.8566,
        longitude: float = 2.3522,
        nom_ville: str = "Paris"
    ):
        """
        Initialise le client avec une localisation.
        
        Args:
            latitude: Latitude (défaut: Paris)
            longitude: Longitude (défaut: Paris)
            nom_ville: Nom à afficher (défaut: Paris)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.nom_ville = nom_ville
    
    def definir_localisation(self, localisation: Localisation) -> None:
        """
        Change la localisation courante.
        
        Args:
            localisation: Nouvelle localisation à utiliser
        """
        self.latitude = localisation.latitude
        self.longitude = localisation.longitude
        self.nom_ville = str(localisation)
    
    def obtenir_donnees_meteo(self) -> dict:
        """
        Récupère les données météo depuis Open-Meteo.
        
        Returns:
            Dictionnaire brut de l'API ou dict vide en cas d'erreur
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "uv_index"],
            "daily": ["uv_index_max"],
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.BASE_URL_METEO, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[API] Erreur meteo: {e}")
            return {}
    
    def obtenir_qualite_air(self) -> dict:
        """
        Récupère les données de qualité de l'air depuis Open-Meteo.
        
        Returns:
            Dictionnaire brut de l'API ou dict vide en cas d'erreur
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ["pm10", "pm2_5"],
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.BASE_URL_AIR, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[API] Erreur qualite air: {e}")
            return {}
    
    def obtenir_donnees_jour(self) -> Optional[DonneesEnvironnementales]:
        """
        Récupère toutes les données environnementales du jour.
        
        Returns:
            DonneesEnvironnementales ou None en cas d'erreur
        """
        donnees_meteo = self.obtenir_donnees_meteo()
        donnees_air = self.obtenir_qualite_air()
        
        if not donnees_meteo:
            return None
        
        maintenant = datetime.now()
        
        # Extraction des données
        current = donnees_meteo.get("current", {})
        daily = donnees_meteo.get("daily", {})
        air_current = donnees_air.get("current", {})
        
        return DonneesEnvironnementales(
            date=maintenant.strftime("%Y-%m-%d"),
            heure=maintenant.strftime("%H:%M"),
            indice_uv=current.get("uv_index", 0),
            indice_uv_max=daily.get("uv_index_max", [0])[0] if daily.get("uv_index_max") else 0,
            humidite_relative=current.get("relative_humidity_2m", 50),
            temperature=current.get("temperature_2m", 20),
            pm2_5=air_current.get("pm2_5"),
            pm10=air_current.get("pm10")
        )


# =============================================================================
# FONCTION UTILITAIRE
# =============================================================================

def obtenir_conditions_actuelles(
    latitude: float = 48.8566,
    longitude: float = 2.3522
) -> Optional[DonneesEnvironnementales]:
    """
    Fonction simple pour obtenir les conditions actuelles.
    
    Args:
        latitude: Latitude (défaut: Paris)
        longitude: Longitude (défaut: Paris)
    
    Returns:
        DonneesEnvironnementales ou None en cas d'erreur
    """
    client = ClientOpenMeteo(latitude, longitude)
    return client.obtenir_donnees_jour()


# =============================================================================
# TEST DU MODULE
# =============================================================================

if __name__ == "__main__":
    print("Test du module API Open-Meteo")
    print("=" * 40)
    
    # Test météo
    donnees = obtenir_conditions_actuelles()
    if donnees:
        print(f"Date: {donnees.date} a {donnees.heure}")
        print(f"Temperature: {donnees.temperature}C")
        print(f"UV: {donnees.indice_uv} ({donnees.niveau_uv})")
        print(f"Humidite: {donnees.humidite_relative}% ({donnees.niveau_humidite})")
        print(f"PM2.5: {donnees.pm2_5} ({donnees.niveau_pollution})")
    else:
        print("Erreur de recuperation des donnees")
    
    print()
    
    # Test géocodage
    print("Test recherche 'Lyon':")
    villes = rechercher_villes("Lyon")
    for v in villes:
        print(f"  - {v}")
