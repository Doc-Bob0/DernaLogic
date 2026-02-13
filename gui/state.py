"""
DermaLogic - Etat de l'application
===================================

Etat partage entre les pages et dialogues.
"""

from api.open_meteo import ClientOpenMeteo, DonneesEnvironnementales, Localisation, PrevisionJournaliere
from api.gemini import ClientGemini
from core.config import GestionnaireConfig
from core.settings import GestionnaireSettings
from core.profil import GestionnaireProfil
from core.historique import GestionnaireHistorique
from core.analyseur import AnalyseurDerma
from gui.data import GestionnaireProduits


class AppState:
    """Etat global de l'application, partage par reference."""

    def __init__(self):
        # Gestionnaires de donnees
        self.gestionnaire_config = GestionnaireConfig()
        self.gestionnaire_produits = GestionnaireProduits()
        self.gestionnaire_settings = GestionnaireSettings()
        self.gestionnaire_profil = GestionnaireProfil()
        self.gestionnaire_historique = GestionnaireHistorique()

        # Donnees environnementales
        self.donnees_env: DonneesEnvironnementales | None = None
        self.previsions: list[PrevisionJournaliere] = []

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

        # Client Gemini (cle API depuis settings)
        api_key = self.gestionnaire_settings.obtenir_gemini_key()
        self.client_gemini = ClientGemini(api_key=api_key)

        # Analyseur IA
        self.analyseur = AnalyseurDerma(
            gestionnaire_produits=self.gestionnaire_produits,
            gestionnaire_profil=self.gestionnaire_profil,
            gestionnaire_historique=self.gestionnaire_historique,
            client_gemini=self.client_gemini,
        )

    def actualiser_client_gemini(self):
        """Recree le client Gemini avec la cle API actuelle."""
        api_key = self.gestionnaire_settings.obtenir_gemini_key()
        self.client_gemini = ClientGemini(api_key=api_key)
        self.analyseur.gemini = self.client_gemini
