"""
DermaLogic - Analyseur Dermatologique IA
=========================================

Orchestrateur d'analyse qui collecte tout le contexte
(produits, meteo, profil, historique) et appelle Gemini
pour generer des recommandations de routine personnalisees.

Remplace l'ancien MoteurDecision algorithmique.
"""

from uuid import uuid4
from datetime import datetime

from core.models import EntreeHistorique


class AnalyseurDerma:
    """
    Orchestrateur d'analyse dermatologique par IA.

    Collecte le contexte complet et delegue l'analyse a Gemini.
    Sauvegarde automatiquement les resultats dans l'historique.
    """

    def __init__(
        self,
        gestionnaire_produits,
        gestionnaire_profil,
        gestionnaire_historique,
        client_gemini,
    ):
        self.produits = gestionnaire_produits
        self.profil = gestionnaire_profil
        self.historique = gestionnaire_historique
        self.gemini = client_gemini

    def analyser(
        self,
        conditions_actuelles,
        previsions: list,
        ville: str = "",
        mode: str = "rapide",
        instructions_jour: str = "",
        niveau_stress_jour: int = None,
    ) -> dict:
        """
        Lance une analyse complete.

        Pipeline :
        1. Recupere produits, profil, historique recent (3)
        2. Envoie tout le contexte a Gemini 2.5 Flash
        3. Sauvegarde le resultat dans l'historique
        4. Retourne le resultat pour l'UI

        Args:
            conditions_actuelles: DonneesEnvironnementales du jour
            previsions: Liste de PrevisionJournaliere (3 jours)
            ville: Nom de la ville actuelle
            mode: "rapide" ou "detaille"
            instructions_jour: Instructions specifiques (mode detaille)
            niveau_stress_jour: Stress du jour (mode detaille)

        Returns:
            dict avec routine_matin, routine_soir, alertes, conseils_jour, resume
            (ou avec cle "erreur" en cas de probleme)
        """
        # 1. Collecter le contexte
        produits = self.produits.obtenir_tous()
        profil = self.profil.obtenir()
        historique_recent = self.historique.obtenir_recents(3)

        # 2. Appeler Gemini
        resultat = self.gemini.analyser_routine(
            produits=produits,
            conditions_actuelles=conditions_actuelles,
            previsions=previsions,
            profil=profil,
            historique_recent=historique_recent,
            ville=ville,
            mode=mode,
            instructions_jour=instructions_jour,
            niveau_stress_jour=niveau_stress_jour,
        )

        # 3. Sauvegarder dans l'historique (sauf si erreur)
        if "erreur" not in resultat:
            entree = EntreeHistorique(
                id=str(uuid4()),
                date=datetime.now().isoformat(),
                mode=mode,
                resume_ia=resultat.get("resume", ""),
                routine_matin=resultat.get("routine_matin", []),
                routine_soir=resultat.get("routine_soir", []),
                alertes=resultat.get("alertes", []),
                conseils_jour=resultat.get("conseils_jour", ""),
                activites_jour=resultat.get("activites_jour", []),
            )
            self.historique.ajouter(entree)

        return resultat
