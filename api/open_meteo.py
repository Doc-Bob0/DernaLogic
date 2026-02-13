"""
DermaLogic - Client API Open-Meteo
==================================

Ce module fournit :
- ClientOpenMeteo : Client pour recuperer les donnees meteo et air quality
- rechercher_villes : Fonction de geocodage pour chercher des villes
- DonneesEnvironnementales : Structure des donnees recuperees
- Localisation : Structure pour les coordonnees d'une ville
- PrevisionJournaliere : Structure pour les previsions quotidiennes
"""

import requests
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


# =============================================================================
# STRUCTURES DE DONNEES
# =============================================================================

@dataclass
class DonneesEnvironnementales:
    """
    Donnees environnementales recuperees pour une localisation.

    Attributes:
        date: Date de la mesure (YYYY-MM-DD)
        heure: Heure de la mesure (HH:MM)
        indice_uv: Indice UV actuel (0-11+)
        indice_uv_max: Indice UV maximum du jour
        humidite_relative: Humidite en pourcentage (0-100)
        temperature: Temperature en degres Celsius
        pm2_5: Particules fines PM2.5 en ug/m3 (optionnel)
        pm10: Particules grossieres PM10 en ug/m3 (optionnel)
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
        """Categorisation OMS du niveau UV."""
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
        """Categorisation du niveau d'humidite."""
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
        """Categorisation de la pollution (basee sur PM2.5 OMS)."""
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
    """Represente une localisation geographique."""
    nom: str
    pays: str
    latitude: float
    longitude: float

    def __str__(self) -> str:
        return f"{self.nom}, {self.pays}"


@dataclass
class PrevisionJournaliere:
    """
    Prevision meteo pour une journee.

    Attributes:
        date: Date de la prevision (YYYY-MM-DD)
        uv_max: Indice UV maximum du jour
        temperature_max: Temperature maximale
        temperature_min: Temperature minimale
        humidite_moyenne: Humidite relative moyenne
        pm2_5_moyen: PM2.5 moyen (optionnel)
    """
    date: str
    uv_max: float
    temperature_max: float
    temperature_min: float
    humidite_moyenne: float
    pm2_5_moyen: Optional[float] = None

    def vers_dict(self) -> dict:
        """Convertit en dictionnaire pour le prompt IA."""
        return {
            "date": self.date,
            "uv_max": self.uv_max,
            "temperature_max": self.temperature_max,
            "temperature_min": self.temperature_min,
            "humidite_moyenne": self.humidite_moyenne,
            "pm2_5_moyen": self.pm2_5_moyen,
        }


# =============================================================================
# FONCTION DE GEOCODAGE
# =============================================================================

def rechercher_villes(query: str, limit: int = 5) -> list[Localisation]:
    """
    Recherche des villes via l'API Open-Meteo Geocoding.

    Args:
        query: Nom de la ville a rechercher
        limit: Nombre maximum de resultats (defaut: 5)

    Returns:
        Liste d'objets Localisation correspondant a la recherche
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
    Client pour les APIs Open-Meteo (meteo et qualite de l'air).

    Attributes:
        latitude: Latitude de la localisation courante
        longitude: Longitude de la localisation courante
        nom_ville: Nom affiche de la ville courante
    """

    BASE_URL_METEO = "https://api.open-meteo.com/v1/forecast"
    BASE_URL_AIR = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def __init__(
        self,
        latitude: float = 48.8566,
        longitude: float = 2.3522,
        nom_ville: str = "Paris"
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.nom_ville = nom_ville

    def definir_localisation(self, localisation: Localisation) -> None:
        """Change la localisation courante."""
        self.latitude = localisation.latitude
        self.longitude = localisation.longitude
        self.nom_ville = str(localisation)

    def obtenir_donnees_meteo(self) -> dict:
        """Recupere les donnees meteo depuis Open-Meteo."""
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
        """Recupere les donnees de qualite de l'air depuis Open-Meteo."""
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
        """Recupere toutes les donnees environnementales du jour."""
        donnees_meteo = self.obtenir_donnees_meteo()
        donnees_air = self.obtenir_qualite_air()

        if not donnees_meteo:
            return None

        maintenant = datetime.now()

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

    def obtenir_previsions_3_jours(self) -> list[PrevisionJournaliere]:
        """
        Recupere les previsions meteo sur 3 jours.

        Returns:
            Liste de PrevisionJournaliere (3 jours)
        """
        # Requete meteo avec previsions quotidiennes
        params_meteo = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "daily": [
                "uv_index_max",
                "temperature_2m_max",
                "temperature_2m_min",
                "relative_humidity_2m_mean",
            ],
            "forecast_days": 3,
            "timezone": "auto",
        }

        # Requete qualite de l'air avec previsions
        params_air = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": ["pm2_5"],
            "forecast_days": 3,
            "timezone": "auto",
        }

        previsions = []

        try:
            resp_meteo = requests.get(self.BASE_URL_METEO, params=params_meteo, timeout=10)
            resp_meteo.raise_for_status()
            data_meteo = resp_meteo.json()
        except requests.RequestException as e:
            print(f"[API] Erreur previsions meteo: {e}")
            return previsions

        # Recuperer qualite de l'air (optionnel)
        pm25_par_jour = {}
        try:
            resp_air = requests.get(self.BASE_URL_AIR, params=params_air, timeout=10)
            resp_air.raise_for_status()
            data_air = resp_air.json()

            # Calculer la moyenne PM2.5 par jour
            heures = data_air.get("hourly", {}).get("time", [])
            pm25_valeurs = data_air.get("hourly", {}).get("pm2_5", [])

            for h, v in zip(heures, pm25_valeurs):
                if v is not None:
                    jour = h[:10]  # YYYY-MM-DD
                    if jour not in pm25_par_jour:
                        pm25_par_jour[jour] = []
                    pm25_par_jour[jour].append(v)

            # Calculer les moyennes
            for jour in pm25_par_jour:
                vals = pm25_par_jour[jour]
                pm25_par_jour[jour] = sum(vals) / len(vals) if vals else None

        except requests.RequestException:
            pass  # Pas grave si on n'a pas la qualite de l'air

        # Construire les previsions
        daily = data_meteo.get("daily", {})
        dates = daily.get("time", [])
        uv_max = daily.get("uv_index_max", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        humidite = daily.get("relative_humidity_2m_mean", [])

        for i, date in enumerate(dates):
            previsions.append(PrevisionJournaliere(
                date=date,
                uv_max=uv_max[i] if i < len(uv_max) else 0,
                temperature_max=temp_max[i] if i < len(temp_max) else 0,
                temperature_min=temp_min[i] if i < len(temp_min) else 0,
                humidite_moyenne=humidite[i] if i < len(humidite) else 50,
                pm2_5_moyen=pm25_par_jour.get(date),
            ))

        return previsions


# =============================================================================
# FONCTION UTILITAIRE
# =============================================================================

def obtenir_conditions_actuelles(
    latitude: float = 48.8566,
    longitude: float = 2.3522
) -> Optional[DonneesEnvironnementales]:
    """Fonction simple pour obtenir les conditions actuelles."""
    client = ClientOpenMeteo(latitude, longitude)
    return client.obtenir_donnees_jour()
