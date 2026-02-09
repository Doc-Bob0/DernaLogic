"""
DermaLogic - Gestionnaire d'Historique des Analyses
====================================================

Ce module gère l'historique des analyses :
- Stockage des analyses dans user_data/historique/
- Séparation entre analyses récentes (< 2 semaines) et archives
- Rotation automatique des anciennes analyses

Structure des fichiers :
    user_data/historique/
    ├── analyses_recentes.json   # 2 dernières semaines
    └── analyses_archives.json   # Plus anciennes
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timedelta


# =============================================================================
# CONSTANTES
# =============================================================================

# Durée de rétention des analyses récentes (en jours)
DUREE_RECENTES_JOURS = 14


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class ProduitAnalyse:
    """Produit inclus dans une analyse."""
    nom: str
    category: str
    moment: str
    active_tag: str
    exclu: bool = False
    raison_exclusion: str = ""
    
    def vers_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def depuis_dict(cls, data: dict) -> "ProduitAnalyse":
        return cls(
            nom=data.get("nom", ""),
            category=data.get("category", ""),
            moment=data.get("moment", ""),
            active_tag=data.get("active_tag", ""),
            exclu=data.get("exclu", False),
            raison_exclusion=data.get("raison_exclusion", "")
        )


@dataclass
class ConditionsAnalyse:
    """Conditions environnementales lors de l'analyse."""
    ville: str
    pays: str
    indice_uv: float
    niveau_uv: str
    humidite: float
    niveau_humidite: str
    temperature: float
    pm2_5: Optional[float]
    niveau_pollution: str
    
    def vers_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def depuis_dict(cls, data: dict) -> "ConditionsAnalyse":
        return cls(
            ville=data.get("ville", ""),
            pays=data.get("pays", ""),
            indice_uv=data.get("indice_uv", 0.0),
            niveau_uv=data.get("niveau_uv", ""),
            humidite=data.get("humidite", 50.0),
            niveau_humidite=data.get("niveau_humidite", ""),
            temperature=data.get("temperature", 20.0),
            pm2_5=data.get("pm2_5"),
            niveau_pollution=data.get("niveau_pollution", "")
        )


@dataclass
class ResultatAnalyseHistorique:
    """Résultat d'une analyse stocké dans l'historique."""
    id: str  # Format: YYYYMMDD_HHMMSS
    date: str  # Format ISO: YYYY-MM-DD
    heure: str  # Format: HH:MM
    timestamp: str  # Format ISO complet
    conditions: ConditionsAnalyse
    produits_matin: list[ProduitAnalyse] = field(default_factory=list)
    produits_journee: list[ProduitAnalyse] = field(default_factory=list)
    produits_soir: list[ProduitAnalyse] = field(default_factory=list)
    alertes: list[str] = field(default_factory=list)
    
    def vers_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "heure": self.heure,
            "timestamp": self.timestamp,
            "conditions": self.conditions.vers_dict(),
            "produits_matin": [p.vers_dict() for p in self.produits_matin],
            "produits_journee": [p.vers_dict() for p in self.produits_journee],
            "produits_soir": [p.vers_dict() for p in self.produits_soir],
            "alertes": self.alertes
        }
    
    @classmethod
    def depuis_dict(cls, data: dict) -> "ResultatAnalyseHistorique":
        return cls(
            id=data.get("id", ""),
            date=data.get("date", ""),
            heure=data.get("heure", ""),
            timestamp=data.get("timestamp", ""),
            conditions=ConditionsAnalyse.depuis_dict(data.get("conditions", {})),
            produits_matin=[ProduitAnalyse.depuis_dict(p) for p in data.get("produits_matin", [])],
            produits_journee=[ProduitAnalyse.depuis_dict(p) for p in data.get("produits_journee", [])],
            produits_soir=[ProduitAnalyse.depuis_dict(p) for p in data.get("produits_soir", [])],
            alertes=data.get("alertes", [])
        )


# =============================================================================
# GESTIONNAIRE D'HISTORIQUE
# =============================================================================

class GestionnaireHistorique:
    """
    Gère l'historique des analyses avec rotation automatique.
    
    - analyses_recentes.json : analyses des 2 dernières semaines
    - analyses_archives.json : analyses plus anciennes
    
    La rotation est effectuée automatiquement lors de l'ajout d'une analyse.
    """
    
    def __init__(self, dossier_historique: Path = None):
        if dossier_historique is None:
            dossier_historique = Path(__file__).parent.parent / "user_data" / "historique"
        
        self.dossier = dossier_historique
        self.dossier.mkdir(parents=True, exist_ok=True)
        
        self.fichier_recentes = self.dossier / "analyses_recentes.json"
        self.fichier_archives = self.dossier / "analyses_archives.json"
        
        # Charger les données existantes
        self.analyses_recentes = self._charger(self.fichier_recentes)
        self.analyses_archives = self._charger(self.fichier_archives)
        
        # Effectuer la rotation au démarrage
        self._rotation_analyses()
    
    def _charger(self, fichier: Path) -> list[ResultatAnalyseHistorique]:
        """Charge les analyses depuis un fichier JSON."""
        if not fichier.exists():
            return []
        
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [ResultatAnalyseHistorique.depuis_dict(a) for a in data]
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Historique] Erreur chargement {fichier.name}: {e}")
            return []
    
    def _sauvegarder(self, fichier: Path, analyses: list[ResultatAnalyseHistorique]) -> None:
        """Sauvegarde les analyses dans un fichier JSON."""
        try:
            with open(fichier, "w", encoding="utf-8") as f:
                data = [a.vers_dict() for a in analyses]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[Historique] Erreur sauvegarde {fichier.name}: {e}")
    
    def _sauvegarder_tout(self) -> None:
        """Sauvegarde les deux fichiers."""
        self._sauvegarder(self.fichier_recentes, self.analyses_recentes)
        self._sauvegarder(self.fichier_archives, self.analyses_archives)
    
    def _rotation_analyses(self) -> None:
        """
        Déplace les analyses de plus de 2 semaines vers les archives.
        
        Cette méthode est appelée automatiquement :
        - Au démarrage de l'application
        - Lors de l'ajout d'une nouvelle analyse
        """
        date_limite = datetime.now() - timedelta(days=DUREE_RECENTES_JOURS)
        
        analyses_a_archiver = []
        analyses_a_garder = []
        
        for analyse in self.analyses_recentes:
            try:
                date_analyse = datetime.fromisoformat(analyse.timestamp)
                if date_analyse < date_limite:
                    analyses_a_archiver.append(analyse)
                else:
                    analyses_a_garder.append(analyse)
            except (ValueError, TypeError):
                # Si la date est invalide, garder dans les récentes
                analyses_a_garder.append(analyse)
        
        if analyses_a_archiver:
            print(f"[Historique] Archivage de {len(analyses_a_archiver)} analyse(s)")
            self.analyses_archives.extend(analyses_a_archiver)
            self.analyses_recentes = analyses_a_garder
            self._sauvegarder_tout()
    
    # =========================================================================
    # MÉTHODES PUBLIQUES
    # =========================================================================
    
    def ajouter_analyse(
        self,
        conditions: ConditionsAnalyse,
        produits_matin: list[ProduitAnalyse],
        produits_journee: list[ProduitAnalyse],
        produits_soir: list[ProduitAnalyse],
        alertes: list[str] = None
    ) -> ResultatAnalyseHistorique:
        """
        Ajoute une nouvelle analyse à l'historique.
        
        Args:
            conditions: Conditions environnementales
            produits_matin: Produits recommandés le matin
            produits_journee: Produits recommandés en journée
            produits_soir: Produits recommandés le soir
            alertes: Messages d'alerte éventuels
        
        Returns:
            L'analyse créée
        """
        maintenant = datetime.now()
        
        analyse = ResultatAnalyseHistorique(
            id=maintenant.strftime("%Y%m%d_%H%M%S"),
            date=maintenant.strftime("%Y-%m-%d"),
            heure=maintenant.strftime("%H:%M"),
            timestamp=maintenant.isoformat(),
            conditions=conditions,
            produits_matin=produits_matin,
            produits_journee=produits_journee,
            produits_soir=produits_soir,
            alertes=alertes or []
        )
        
        # Ajouter en tête de liste (le plus récent en premier)
        self.analyses_recentes.insert(0, analyse)
        
        # Effectuer la rotation si nécessaire
        self._rotation_analyses()
        
        # Sauvegarder
        self._sauvegarder(self.fichier_recentes, self.analyses_recentes)
        
        return analyse
    
    def obtenir_recentes(self, limite: int = None) -> list[ResultatAnalyseHistorique]:
        """
        Retourne les analyses récentes (< 2 semaines).
        
        Args:
            limite: Nombre maximum d'analyses à retourner (None = toutes)
        
        Returns:
            Liste des analyses récentes, triée par date décroissante
        """
        if limite:
            return self.analyses_recentes[:limite]
        return self.analyses_recentes.copy()
    
    def obtenir_archives(self, limite: int = None) -> list[ResultatAnalyseHistorique]:
        """
        Retourne les analyses archivées (> 2 semaines).
        
        Args:
            limite: Nombre maximum d'analyses à retourner (None = toutes)
        
        Returns:
            Liste des analyses archivées, triée par date décroissante
        """
        if limite:
            return self.analyses_archives[:limite]
        return self.analyses_archives.copy()
    
    def obtenir_toutes(self) -> list[ResultatAnalyseHistorique]:
        """
        Retourne toutes les analyses (récentes + archives).
        
        Returns:
            Liste de toutes les analyses, triée par date décroissante
        """
        return self.analyses_recentes + self.analyses_archives
    
    def obtenir_par_date(self, date: str) -> list[ResultatAnalyseHistorique]:
        """
        Retourne les analyses d'une date spécifique.
        
        Args:
            date: Date au format YYYY-MM-DD
        
        Returns:
            Liste des analyses de cette date
        """
        toutes = self.obtenir_toutes()
        return [a for a in toutes if a.date == date]
    
    def obtenir_par_id(self, id_analyse: str) -> Optional[ResultatAnalyseHistorique]:
        """
        Retourne une analyse par son ID.
        
        Args:
            id_analyse: ID de l'analyse (format YYYYMMDD_HHMMSS)
        
        Returns:
            L'analyse ou None si non trouvée
        """
        for analyse in self.obtenir_toutes():
            if analyse.id == id_analyse:
                return analyse
        return None
    
    def supprimer_analyse(self, id_analyse: str) -> bool:
        """
        Supprime une analyse de l'historique.
        
        Args:
            id_analyse: ID de l'analyse à supprimer
        
        Returns:
            True si supprimée, False si non trouvée
        """
        # Chercher dans les récentes
        for i, analyse in enumerate(self.analyses_recentes):
            if analyse.id == id_analyse:
                del self.analyses_recentes[i]
                self._sauvegarder(self.fichier_recentes, self.analyses_recentes)
                return True
        
        # Chercher dans les archives
        for i, analyse in enumerate(self.analyses_archives):
            if analyse.id == id_analyse:
                del self.analyses_archives[i]
                self._sauvegarder(self.fichier_archives, self.analyses_archives)
                return True
        
        return False
    
    def vider_archives(self) -> int:
        """
        Supprime toutes les archives.
        
        Returns:
            Nombre d'analyses supprimées
        """
        nb = len(self.analyses_archives)
        self.analyses_archives = []
        self._sauvegarder(self.fichier_archives, self.analyses_archives)
        return nb
    
    def forcer_rotation(self) -> int:
        """
        Force la rotation des analyses (utile pour les tests).
        
        Returns:
            Nombre d'analyses archivées
        """
        nb_avant = len(self.analyses_archives)
        self._rotation_analyses()
        return len(self.analyses_archives) - nb_avant
    
    def statistiques(self) -> dict:
        """
        Retourne des statistiques sur l'historique.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            "nb_recentes": len(self.analyses_recentes),
            "nb_archives": len(self.analyses_archives),
            "nb_total": len(self.analyses_recentes) + len(self.analyses_archives),
            "derniere_analyse": self.analyses_recentes[0].timestamp if self.analyses_recentes else None
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def creer_conditions_depuis_env(
    ville: str,
    pays: str,
    donnees_env
) -> ConditionsAnalyse:
    """
    Crée un objet ConditionsAnalyse depuis les données environnementales.
    
    Args:
        ville: Nom de la ville
        pays: Nom du pays
        donnees_env: Objet DonneesEnvironnementales
    
    Returns:
        ConditionsAnalyse
    """
    return ConditionsAnalyse(
        ville=ville,
        pays=pays,
        indice_uv=donnees_env.indice_uv,
        niveau_uv=donnees_env.niveau_uv,
        humidite=donnees_env.humidite_relative,
        niveau_humidite=donnees_env.niveau_humidite,
        temperature=donnees_env.temperature,
        pm2_5=donnees_env.pm2_5,
        niveau_pollution=donnees_env.niveau_pollution
    )


def creer_produit_depuis_resultat(produit, exclu: bool = False, raison: str = "") -> ProduitAnalyse:
    """
    Crée un objet ProduitAnalyse depuis un ProduitDerma.
    
    Args:
        produit: ProduitDerma
        exclu: Si le produit a été exclu
        raison: Raison de l'exclusion
    
    Returns:
        ProduitAnalyse
    """
    return ProduitAnalyse(
        nom=produit.nom,
        category=produit.category.value if hasattr(produit.category, 'value') else str(produit.category),
        moment=produit.moment.value if hasattr(produit.moment, 'value') else str(produit.moment),
        active_tag=produit.active_tag.value if hasattr(produit.active_tag, 'value') else str(produit.active_tag),
        exclu=exclu,
        raison_exclusion=raison
    )


# =============================================================================
# TEST DU MODULE
# =============================================================================

if __name__ == "__main__":
    print("Test du gestionnaire d'historique")
    print("=" * 50)
    
    historique = GestionnaireHistorique()
    
    print(f"Statistiques: {historique.statistiques()}")
    print(f"Analyses récentes: {len(historique.obtenir_recentes())}")
    print(f"Analyses archives: {len(historique.obtenir_archives())}")
