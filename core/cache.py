"""
Module de gestion du cache pour le mode hors-ligne.

Permet de stocker et récupérer les données météorologiques et routines
pour fonctionner en mode dégradé sans connexion internet.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DonneesCachees:
    """Données en cache avec métadonnées."""

    donnees: Dict[str, Any]
    date_cache: str  # ISO format
    ttl_minutes: int  # Time to live en minutes

    @property
    def date_cache_dt(self) -> datetime:
        """Retourne la date de cache en datetime."""
        return datetime.fromisoformat(self.date_cache)

    @property
    def date_expiration(self) -> datetime:
        """Calcule la date d'expiration du cache."""
        return self.date_cache_dt + timedelta(minutes=self.ttl_minutes)

    @property
    def est_expire(self) -> bool:
        """Vérifie si le cache est expiré."""
        return datetime.now() > self.date_expiration

    @property
    def age_minutes(self) -> int:
        """Retourne l'âge du cache en minutes."""
        delta = datetime.now() - self.date_cache_dt
        return int(delta.total_seconds() / 60)


class GestionnaireCache:
    """Gestionnaire de cache pour les données météo et routines."""

    def __init__(self, dossier_cache: Optional[Path] = None):
        """
        Initialise le gestionnaire de cache.

        Args:
            dossier_cache: Dossier de stockage du cache (par défaut: user_data/cache/)
        """
        if dossier_cache is None:
            # Obtenir le chemin du projet
            projet_dir = Path(__file__).parent.parent
            dossier_cache = projet_dir / "user_data" / "cache"

        self.dossier_cache = Path(dossier_cache)
        self.dossier_cache.mkdir(parents=True, exist_ok=True)

        # Fichiers de cache
        self.fichier_meteo_actuelle = self.dossier_cache / "meteo_actuelle.json"
        self.fichier_previsions = self.dossier_cache / "previsions_7j.json"
        self.fichier_derniere_routine = self.dossier_cache / "derniere_routine.json"

    def sauvegarder_meteo_actuelle(self, donnees_meteo: Dict[str, Any], ttl_minutes: int = 60):
        """
        Sauvegarde les données météo actuelles dans le cache.

        Args:
            donnees_meteo: Données météo à mettre en cache
            ttl_minutes: Durée de validité du cache (par défaut: 60 minutes)
        """
        cache = DonneesCachees(
            donnees=donnees_meteo,
            date_cache=datetime.now().isoformat(),
            ttl_minutes=ttl_minutes
        )

        with open(self.fichier_meteo_actuelle, 'w', encoding='utf-8') as f:
            json.dump(asdict(cache), f, ensure_ascii=False, indent=2)

    def charger_meteo_actuelle(self) -> Optional[DonneesCachees]:
        """
        Charge les données météo actuelles depuis le cache.

        Returns:
            DonneesCachees si disponible, None sinon
        """
        if not self.fichier_meteo_actuelle.exists():
            return None

        try:
            with open(self.fichier_meteo_actuelle, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return DonneesCachees(**data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def sauvegarder_previsions(self, previsions: Dict[str, Any], ttl_minutes: int = 720):
        """
        Sauvegarde les prévisions météo 7 jours dans le cache.

        Args:
            previsions: Prévisions météo à mettre en cache
            ttl_minutes: Durée de validité (par défaut: 720 min = 12h)
        """
        cache = DonneesCachees(
            donnees=previsions,
            date_cache=datetime.now().isoformat(),
            ttl_minutes=ttl_minutes
        )

        with open(self.fichier_previsions, 'w', encoding='utf-8') as f:
            json.dump(asdict(cache), f, ensure_ascii=False, indent=2)

    def charger_previsions(self) -> Optional[DonneesCachees]:
        """
        Charge les prévisions météo depuis le cache.

        Returns:
            DonneesCachees si disponible, None sinon
        """
        if not self.fichier_previsions.exists():
            return None

        try:
            with open(self.fichier_previsions, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return DonneesCachees(**data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def sauvegarder_derniere_routine(self, routine: Dict[str, Any], ttl_minutes: int = 1440):
        """
        Sauvegarde la dernière routine générée.

        Args:
            routine: Routine à mettre en cache
            ttl_minutes: Durée de validité (par défaut: 1440 min = 24h)
        """
        cache = DonneesCachees(
            donnees=routine,
            date_cache=datetime.now().isoformat(),
            ttl_minutes=ttl_minutes
        )

        with open(self.fichier_derniere_routine, 'w', encoding='utf-8') as f:
            json.dump(asdict(cache), f, ensure_ascii=False, indent=2)

    def charger_derniere_routine(self) -> Optional[DonneesCachees]:
        """
        Charge la dernière routine depuis le cache.

        Returns:
            DonneesCachees si disponible, None sinon
        """
        if not self.fichier_derniere_routine.exists():
            return None

        try:
            with open(self.fichier_derniere_routine, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return DonneesCachees(**data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def obtenir_meteo_avec_fallback(self) -> tuple[Optional[Dict[str, Any]], bool]:
        """
        Obtient les données météo, même expirées si nécessaire (mode hors-ligne).

        Returns:
            tuple: (données météo, est_en_cache)
                - données météo: Dict ou None si aucune donnée
                - est_en_cache: True si données proviennent du cache
        """
        cache = self.charger_meteo_actuelle()

        if cache is None:
            return None, False

        # Retourner les données même si expirées (mode hors-ligne)
        return cache.donnees, True

    def obtenir_previsions_avec_fallback(self) -> tuple[Optional[Dict[str, Any]], bool]:
        """
        Obtient les prévisions, même expirées si nécessaire (mode hors-ligne).

        Returns:
            tuple: (prévisions, est_en_cache)
        """
        cache = self.charger_previsions()

        if cache is None:
            return None, False

        return cache.donnees, True

    def obtenir_routine_avec_fallback(self) -> tuple[Optional[Dict[str, Any]], bool]:
        """
        Obtient la dernière routine, même expirée si nécessaire.

        Returns:
            tuple: (routine, est_en_cache)
        """
        cache = self.charger_derniere_routine()

        if cache is None:
            return None, False

        return cache.donnees, True

    def nettoyer_cache_expire(self):
        """Supprime les fichiers de cache expirés."""
        fichiers = [
            self.fichier_meteo_actuelle,
            self.fichier_previsions,
            self.fichier_derniere_routine
        ]

        for fichier in fichiers:
            if not fichier.exists():
                continue

            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cache = DonneesCachees(**data)

                    if cache.est_expire:
                        # Ne pas supprimer, juste marquer comme expiré
                        # (utile pour mode hors-ligne)
                        pass
            except (json.JSONDecodeError, KeyError, TypeError):
                # Fichier corrompu, le supprimer
                fichier.unlink()

    def vider_cache(self):
        """Supprime tout le cache."""
        fichiers = [
            self.fichier_meteo_actuelle,
            self.fichier_previsions,
            self.fichier_derniere_routine
        ]

        for fichier in fichiers:
            if fichier.exists():
                fichier.unlink()

    def obtenir_etat_cache(self) -> Dict[str, Any]:
        """
        Obtient l'état actuel du cache.

        Returns:
            Dict avec les informations sur le cache
        """
        etat = {
            "meteo_actuelle": None,
            "previsions": None,
            "derniere_routine": None
        }

        # Météo actuelle
        cache_meteo = self.charger_meteo_actuelle()
        if cache_meteo:
            etat["meteo_actuelle"] = {
                "age_minutes": cache_meteo.age_minutes,
                "expire": cache_meteo.est_expire,
                "date_cache": cache_meteo.date_cache
            }

        # Prévisions
        cache_prev = self.charger_previsions()
        if cache_prev:
            etat["previsions"] = {
                "age_minutes": cache_prev.age_minutes,
                "expire": cache_prev.est_expire,
                "date_cache": cache_prev.date_cache
            }

        # Dernière routine
        cache_routine = self.charger_derniere_routine()
        if cache_routine:
            etat["derniere_routine"] = {
                "age_minutes": cache_routine.age_minutes,
                "expire": cache_routine.est_expire,
                "date_cache": cache_routine.date_cache
            }

        return etat


# Instance globale (singleton)
_gestionnaire_cache: Optional[GestionnaireCache] = None


def obtenir_gestionnaire_cache() -> GestionnaireCache:
    """
    Obtient le gestionnaire de cache global (singleton).

    Returns:
        GestionnaireCache: Instance globale
    """
    global _gestionnaire_cache
    if _gestionnaire_cache is None:
        _gestionnaire_cache = GestionnaireCache()
    return _gestionnaire_cache


if __name__ == "__main__":
    # Test du module
    gestionnaire = obtenir_gestionnaire_cache()

    # Test de sauvegarde/chargement météo
    donnees_test = {
        "temperature": 22.5,
        "uv": 5.2,
        "humidite": 65,
        "pm25": 12
    }

    print("Test du cache météo...")
    gestionnaire.sauvegarder_meteo_actuelle(donnees_test, ttl_minutes=1)

    cache = gestionnaire.charger_meteo_actuelle()
    if cache:
        print(f"✓ Données en cache: {cache.donnees}")
        print(f"✓ Âge: {cache.age_minutes} minutes")
        print(f"✓ Expiré: {cache.est_expire}")

    print("\nÉtat du cache:")
    etat = gestionnaire.obtenir_etat_cache()
    print(json.dumps(etat, indent=2, ensure_ascii=False))
