"""
DermaLogic - Etat de l'application
===================================

Etat partage entre les pages et dialogues.
"""

from api.open_meteo import ClientOpenMeteo, DonneesEnvironnementales, Localisation
from core.config import GestionnaireConfig
from gui.data import GestionnaireProduits


class AppState:
    """Etat global de l'application, partage par reference."""

    def __init__(self):
        self.gestionnaire_config = GestionnaireConfig()
        self.gestionnaire_produits = GestionnaireProduits()
        self.donnees_env: DonneesEnvironnementales | None = None

        # Initialiser le client meteo avec la ville sauvegardee
        ville = self.gestionnaire_config.obtenir_ville_actuelle()
        self.client_meteo = ClientOpenMeteo()
        self.client_meteo.definir_localisation(
            Localisation(
                nom=ville.nom,
                pays=ville.pays,
                latitude=ville.latitude,
                longitude=ville.longitude,
            )
        )
