"""
DermaLogic - Utilitaire de stockage multi-plateforme
=====================================================

Detecte la plateforme (Android, Windows, macOS, Linux) et retourne
le repertoire de donnees adapte pour la persistance JSON.

Inclut une migration automatique depuis l'ancien dossier user_data/
vers le nouveau dossier plateforme au premier lancement.
"""

import os
import shutil
import platform
from pathlib import Path


# Cache du dossier pour eviter de recalculer a chaque appel
_dossier_cache: Path = None


def obtenir_dossier_donnees() -> Path:
    """
    Retourne le chemin du dossier de donnees adapte a la plateforme.

    - Android (Flet APK) : utilise FLET_APP_STORAGE_DATA
    - Windows : %APPDATA%/DermaLogic/
    - macOS : ~/Library/Application Support/DermaLogic/
    - Linux : ~/.dermalogic/
    - Fallback : user_data/ relatif au projet

    Le dossier est cree automatiquement s'il n'existe pas.
    Au premier lancement, migre les donnees depuis user_data/ si present.
    """
    global _dossier_cache
    if _dossier_cache is not None:
        return _dossier_cache

    # Android (Flet definit cette variable d'environnement)
    flet_storage = os.environ.get("FLET_APP_STORAGE_DATA")
    if flet_storage:
        dossier = Path(flet_storage)
        dossier.mkdir(parents=True, exist_ok=True)
        _dossier_cache = dossier
        return dossier

    systeme = platform.system()

    if systeme == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            dossier = Path(appdata) / "DermaLogic"
        else:
            dossier = Path.home() / "AppData" / "Roaming" / "DermaLogic"
    elif systeme == "Darwin":
        dossier = Path.home() / "Library" / "Application Support" / "DermaLogic"
    elif systeme == "Linux":
        dossier = Path.home() / ".dermalogic"
    else:
        # Fallback : dossier relatif (comportement desktop historique)
        dossier = Path(__file__).parent.parent / "user_data"
        dossier.mkdir(parents=True, exist_ok=True)
        _dossier_cache = dossier
        return dossier

    dossier.mkdir(parents=True, exist_ok=True)

    # Migration automatique depuis l'ancien dossier user_data/
    _migrer_donnees_legacy(dossier)

    _dossier_cache = dossier
    return dossier


def _migrer_donnees_legacy(nouveau_dossier: Path) -> None:
    """
    Migre les fichiers JSON depuis l'ancien dossier user_data/ (relatif au projet)
    vers le nouveau dossier plateforme, si les fichiers n'existent pas encore
    dans la destination.
    """
    ancien_dossier = Path(__file__).parent.parent / "user_data"

    if not ancien_dossier.exists():
        return

    fichiers_json = [
        "settings.json",
        "profile.json",
        "produits_derma.json",
        "historique.json",
        "config.json",
    ]

    migres = 0
    for fichier in fichiers_json:
        ancien = ancien_dossier / fichier
        nouveau = nouveau_dossier / fichier

        if ancien.exists() and not nouveau.exists():
            try:
                shutil.copy2(str(ancien), str(nouveau))
                migres += 1
                print(f"[Storage] Migre: {fichier} -> {nouveau_dossier}")
            except (IOError, OSError) as e:
                print(f"[Storage] Erreur migration {fichier}: {e}")

    if migres > 0:
        print(f"[Storage] Migration terminee: {migres} fichier(s) migre(s)")


def est_mobile() -> bool:
    """
    Detecte si l'app tourne sur un appareil mobile (Android).

    Retourne True si la variable FLET_APP_STORAGE_DATA est definie
    (indiquant un build APK Flet) ou si ANDROID_ROOT est present.
    """
    return bool(
        os.environ.get("FLET_APP_STORAGE_DATA")
        or os.environ.get("ANDROID_ROOT")
    )
