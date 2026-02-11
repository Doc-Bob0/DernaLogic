"""
Module de détection de plateforme et configuration adaptative.

Ce module détecte automatiquement la plateforme d'exécution (Desktop, Mobile, Web)
et fournit des informations pour adapter l'interface utilisateur.
"""

import platform
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TypePlateforme(Enum):
    """Types de plateformes supportées."""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    WEB = "web"
    INCONNU = "inconnu"


class SystemeExploitation(Enum):
    """Systèmes d'exploitation détectés."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"
    INCONNU = "inconnu"


@dataclass
class InfoPlateforme:
    """Informations détaillées sur la plateforme d'exécution."""

    type_plateforme: TypePlateforme
    systeme_exploitation: SystemeExploitation
    version_os: str
    est_mobile: bool
    est_desktop: bool
    est_web: bool
    supporte_notifications: bool
    supporte_camera: bool
    supporte_geolocalisation: bool
    largeur_ecran_estimee: int  # En pixels
    hauteur_ecran_estimee: int  # En pixels

    @property
    def est_petit_ecran(self) -> bool:
        """Détermine si l'écran est considéré comme petit (mobile)."""
        return self.largeur_ecran_estimee < 768

    @property
    def est_tablette(self) -> bool:
        """Détermine si l'appareil est probablement une tablette."""
        return (self.est_mobile and
                768 <= self.largeur_ecran_estimee <= 1024)


class DetecteurPlateforme:
    """Détecte la plateforme d'exécution et ses capacités."""

    @staticmethod
    def detecter() -> InfoPlateforme:
        """
        Détecte automatiquement la plateforme et retourne les informations.

        Returns:
            InfoPlateforme: Informations complètes sur la plateforme
        """
        systeme = platform.system().lower()
        machine = platform.machine().lower()
        version = platform.version()

        # Détection du système d'exploitation
        os_type = DetecteurPlateforme._detecter_os(systeme, machine)

        # Détection du type de plateforme
        type_plateforme = DetecteurPlateforme._detecter_type_plateforme(os_type)

        # Capacités selon la plateforme
        est_mobile = type_plateforme == TypePlateforme.MOBILE
        est_desktop = type_plateforme == TypePlateforme.DESKTOP
        est_web = type_plateforme == TypePlateforme.WEB

        # Support des fonctionnalités
        supporte_notifications = DetecteurPlateforme._supporte_notifications(os_type)
        supporte_camera = est_mobile or est_web  # Desktop peut aussi avoir webcam
        supporte_geolocalisation = True  # Flet supporte sur toutes plateformes

        # Dimensions d'écran estimées
        largeur, hauteur = DetecteurPlateforme._estimer_dimensions_ecran(type_plateforme)

        return InfoPlateforme(
            type_plateforme=type_plateforme,
            systeme_exploitation=os_type,
            version_os=version,
            est_mobile=est_mobile,
            est_desktop=est_desktop,
            est_web=est_web,
            supporte_notifications=supporte_notifications,
            supporte_camera=supporte_camera,
            supporte_geolocalisation=supporte_geolocalisation,
            largeur_ecran_estimee=largeur,
            hauteur_ecran_estimee=hauteur
        )

    @staticmethod
    def _detecter_os(systeme: str, machine: str) -> SystemeExploitation:
        """Détecte le système d'exploitation."""
        if systeme == "windows":
            return SystemeExploitation.WINDOWS
        elif systeme == "darwin":
            return SystemeExploitation.MACOS
        elif systeme == "linux":
            # Différencier Linux desktop et Android
            if "android" in machine or hasattr(sys, 'getandroidapilevel'):
                return SystemeExploitation.ANDROID
            return SystemeExploitation.LINUX
        elif systeme == "ios" or machine.startswith("iphone") or machine.startswith("ipad"):
            return SystemeExploitation.IOS
        else:
            return SystemeExploitation.INCONNU

    @staticmethod
    def _detecter_type_plateforme(os_type: SystemeExploitation) -> TypePlateforme:
        """Détermine le type de plateforme selon l'OS."""
        if os_type in [SystemeExploitation.ANDROID, SystemeExploitation.IOS]:
            return TypePlateforme.MOBILE
        elif os_type in [SystemeExploitation.WINDOWS, SystemeExploitation.MACOS, SystemeExploitation.LINUX]:
            return TypePlateforme.DESKTOP
        else:
            return TypePlateforme.INCONNU

    @staticmethod
    def _supporte_notifications(os_type: SystemeExploitation) -> bool:
        """Vérifie si la plateforme supporte les notifications."""
        # Toutes les plateformes modernes supportent les notifications
        # mais l'implémentation diffère
        return os_type != SystemeExploitation.INCONNU

    @staticmethod
    def _estimer_dimensions_ecran(type_plateforme: TypePlateforme) -> tuple[int, int]:
        """
        Estime les dimensions d'écran selon la plateforme.
        Ces valeurs seront affinées par Flet au runtime.

        Returns:
            tuple[int, int]: (largeur, hauteur) en pixels
        """
        if type_plateforme == TypePlateforme.MOBILE:
            # Smartphone typique (portrait)
            return (390, 844)  # iPhone 14 Pro comme référence
        elif type_plateforme == TypePlateforme.DESKTOP:
            # Desktop typique
            return (1920, 1080)  # Full HD
        elif type_plateforme == TypePlateforme.WEB:
            # Navigateur desktop par défaut
            return (1280, 720)
        else:
            # Par défaut
            return (800, 600)


class ConfigurationUI:
    """Configuration de l'interface selon la plateforme détectée."""

    def __init__(self, info_plateforme: InfoPlateforme):
        self.info = info_plateforme

    @property
    def utiliser_navigation_bottom(self) -> bool:
        """Détermine si on utilise une bottom navigation bar (mobile)."""
        return self.info.est_mobile

    @property
    def utiliser_sidebar(self) -> bool:
        """Détermine si on utilise une sidebar (desktop)."""
        return self.info.est_desktop

    @property
    def taille_police_base(self) -> int:
        """Taille de police de base selon la plateforme."""
        if self.info.est_mobile:
            return 16  # Légèrement plus grand pour mobile
        return 14

    @property
    def espacement_base(self) -> int:
        """Espacement de base entre les éléments."""
        if self.info.est_mobile:
            return 12  # Plus d'espacement pour les doigts
        return 8

    @property
    def hauteur_bouton(self) -> int:
        """Hauteur des boutons tactiles."""
        if self.info.est_mobile:
            return 48  # Minimum recommandé pour tactile (Material Design)
        return 36

    @property
    def largeur_maximale_contenu(self) -> int:
        """Largeur maximale du contenu principal."""
        if self.info.est_mobile:
            return self.info.largeur_ecran_estimee
        return 1200  # Desktop: contenu centré avec max-width

    @property
    def nombre_colonnes_grille(self) -> int:
        """Nombre de colonnes dans les grilles responsives."""
        if self.info.est_petit_ecran:
            return 1  # Mobile: 1 colonne
        elif self.info.est_tablette:
            return 2  # Tablette: 2 colonnes
        else:
            return 3  # Desktop: 3 colonnes


# Instance globale (singleton)
_info_plateforme: Optional[InfoPlateforme] = None
_config_ui: Optional[ConfigurationUI] = None


def obtenir_info_plateforme() -> InfoPlateforme:
    """
    Obtient les informations de plateforme (singleton).

    Returns:
        InfoPlateforme: Informations sur la plateforme
    """
    global _info_plateforme
    if _info_plateforme is None:
        _info_plateforme = DetecteurPlateforme.detecter()
    return _info_plateforme


def obtenir_config_ui() -> ConfigurationUI:
    """
    Obtient la configuration UI adaptée à la plateforme (singleton).

    Returns:
        ConfigurationUI: Configuration de l'interface
    """
    global _config_ui
    if _config_ui is None:
        _config_ui = ConfigurationUI(obtenir_info_plateforme())
    return _config_ui


def afficher_info_plateforme():
    """Affiche les informations de plateforme (debug)."""
    info = obtenir_info_plateforme()
    config = obtenir_config_ui()

    print("=" * 60)
    print("INFORMATIONS PLATEFORME - DermaLogic")
    print("=" * 60)
    print(f"Type: {info.type_plateforme.value}")
    print(f"OS: {info.systeme_exploitation.value}")
    print(f"Version: {info.version_os}")
    print(f"Mobile: {info.est_mobile}")
    print(f"Desktop: {info.est_desktop}")
    print(f"Web: {info.est_web}")
    print(f"Petit écran: {info.est_petit_ecran}")
    print(f"Tablette: {info.est_tablette}")
    print("-" * 60)
    print("CAPACITÉS")
    print("-" * 60)
    print(f"Notifications: {info.supporte_notifications}")
    print(f"Caméra: {info.supporte_camera}")
    print(f"Géolocalisation: {info.supporte_geolocalisation}")
    print("-" * 60)
    print("CONFIGURATION UI")
    print("-" * 60)
    print(f"Navigation bottom: {config.utiliser_navigation_bottom}")
    print(f"Sidebar: {config.utiliser_sidebar}")
    print(f"Taille police: {config.taille_police_base}px")
    print(f"Espacement: {config.espacement_base}px")
    print(f"Hauteur bouton: {config.hauteur_bouton}px")
    print(f"Colonnes grille: {config.nombre_colonnes_grille}")
    print("=" * 60)


if __name__ == "__main__":
    # Test du module
    afficher_info_plateforme()
