"""
DermaLogic - Modeles de donnees centralises
=============================================

Tous les modeles de donnees de l'application :
- Enums (Categorie, MomentUtilisation, ActiveTag, TypePeau, etc.)
- ProduitDerma (avec custom_attributes)
- ProfilUtilisateur
- EntreeHistorique
- Settings
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# =============================================================================
# ENUMERATIONS - PRODUITS (existants, deplaces depuis algorithme.py)
# =============================================================================

class Categorie(Enum):
    """Categories de produits dermatologiques."""
    CLEANSER = "cleanser"
    TREATMENT = "treatment"
    MOISTURIZER = "moisturizer"
    PROTECTION = "protection"


class ActiveTag(Enum):
    """Tags d'action principale des actifs."""
    ACNE = "acne"
    HYDRATION = "hydration"
    REPAIR = "repair"


class MomentUtilisation(Enum):
    """Moment d'utilisation recommande du produit."""
    MATIN = "matin"
    JOURNEE = "journee"
    SOIR = "soir"
    TOUS = "tous"


# =============================================================================
# ENUMERATIONS - PROFIL UTILISATEUR
# =============================================================================

class TypePeau(Enum):
    """Types de peau."""
    GRASSE = "grasse"
    SECHE = "seche"
    MIXTE = "mixte"
    NORMALE = "normale"
    SENSIBLE = "sensible"


class TrancheAge(Enum):
    """Tranches d'age."""
    MOINS_18 = "<18"
    AGE_18_25 = "18-25"
    AGE_26_35 = "26-35"
    AGE_36_45 = "36-45"
    AGE_46_55 = "46-55"
    PLUS_55 = "55+"


class ObjectifPeau(Enum):
    """Objectifs de soin de la peau."""
    HYDRATATION = "hydratation"
    ANTI_ACNE = "anti-acne"
    ECLAT = "eclat"
    ANTI_TACHES = "anti-taches"
    ANTI_AGE = "anti-age"
    APAISEMENT = "apaisement"
    PROTECTION = "protection"


# =============================================================================
# MODELE PRODUIT
# =============================================================================

@dataclass
class ProduitDerma:
    """
    Representation d'un produit dermatologique.

    Attributes:
        nom: Nom du produit
        category: Type de produit
        moment: Quand utiliser le produit
        photosensitive: True si le produit reagit aux UV
        occlusivity: Richesse de texture (1=leger, 5=tres riche)
        cleansing_power: Puissance nettoyante (1=doux, 5=puissant)
        active_tag: Action principale du produit
        custom_attributes: Attributs personnalises supplementaires
    """
    nom: str
    category: Categorie
    moment: MomentUtilisation = MomentUtilisation.TOUS
    photosensitive: bool = False
    occlusivity: int = 3
    cleansing_power: int = 3
    active_tag: ActiveTag = ActiveTag.HYDRATION
    custom_attributes: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validation des valeurs apres initialisation."""
        if not 1 <= self.occlusivity <= 5:
            raise ValueError(f"occlusivity doit etre entre 1 et 5, recu: {self.occlusivity}")
        if not 1 <= self.cleansing_power <= 5:
            raise ValueError(f"cleansing_power doit etre entre 1 et 5, recu: {self.cleansing_power}")

    def vers_dict(self) -> dict:
        """Convertit le produit en dictionnaire pour serialisation JSON."""
        d = {
            "nom": self.nom,
            "category": self.category.value,
            "moment": self.moment.value,
            "photosensitive": self.photosensitive,
            "occlusivity": self.occlusivity,
            "cleansing_power": self.cleansing_power,
            "active_tag": self.active_tag.value,
        }
        if self.custom_attributes:
            d["custom_attributes"] = self.custom_attributes
        return d

    @classmethod
    def depuis_dict(cls, data: dict) -> "ProduitDerma":
        """Cree un produit depuis un dictionnaire."""
        return cls(
            nom=data["nom"],
            category=Categorie(data["category"]),
            moment=MomentUtilisation(data.get("moment", "tous")),
            photosensitive=data.get("photosensitive", False),
            occlusivity=data.get("occlusivity", 3),
            cleansing_power=data.get("cleansing_power", 3),
            active_tag=ActiveTag(data.get("active_tag", "hydration")),
            custom_attributes=data.get("custom_attributes", {}),
        )


# =============================================================================
# PROFIL UTILISATEUR
# =============================================================================

@dataclass
class ProfilUtilisateur:
    """
    Profil dermatologique de l'utilisateur.

    Attributes:
        type_peau: Type de peau (grasse, seche, mixte, normale, sensible)
        tranche_age: Tranche d'age
        niveau_stress: Niveau de stress moyen (1-10)
        maladies_peau: Liste des maladies de peau (eczema, psoriasis, etc.)
        allergies: Liste d'ingredients a eviter
        objectifs: Objectifs de soin
        instructions_quotidiennes: Instructions personnalisees quotidiennes
    """
    type_peau: TypePeau = TypePeau.NORMALE
    tranche_age: TrancheAge = TrancheAge.AGE_26_35
    niveau_stress: int = 5
    maladies_peau: list = field(default_factory=list)
    allergies: list = field(default_factory=list)
    objectifs: list = field(default_factory=list)
    instructions_quotidiennes: str = ""

    def vers_dict(self) -> dict:
        """Convertit le profil en dictionnaire pour serialisation JSON."""
        return {
            "type_peau": self.type_peau.value,
            "tranche_age": self.tranche_age.value,
            "niveau_stress": self.niveau_stress,
            "maladies_peau": self.maladies_peau,
            "allergies": self.allergies,
            "objectifs": [o.value if isinstance(o, ObjectifPeau) else o for o in self.objectifs],
            "instructions_quotidiennes": self.instructions_quotidiennes,
        }

    @classmethod
    def depuis_dict(cls, data: dict) -> "ProfilUtilisateur":
        """Cree un profil depuis un dictionnaire."""
        objectifs_raw = data.get("objectifs", [])
        objectifs = []
        for o in objectifs_raw:
            try:
                objectifs.append(ObjectifPeau(o))
            except ValueError:
                pass

        try:
            type_peau = TypePeau(data.get("type_peau", "normale"))
        except ValueError:
            type_peau = TypePeau.NORMALE

        try:
            tranche_age = TrancheAge(data.get("tranche_age", "26-35"))
        except ValueError:
            tranche_age = TrancheAge.AGE_26_35

        return cls(
            type_peau=type_peau,
            tranche_age=tranche_age,
            niveau_stress=max(1, min(10, int(data.get("niveau_stress", 5)))),
            maladies_peau=data.get("maladies_peau", []),
            allergies=data.get("allergies", []),
            objectifs=objectifs,
            instructions_quotidiennes=data.get("instructions_quotidiennes", ""),
        )


# =============================================================================
# ENTREE HISTORIQUE
# =============================================================================

@dataclass
class EntreeHistorique:
    """
    Entree dans l'historique des analyses.

    Attributes:
        id: Identifiant unique (UUID)
        date: Date ISO de l'analyse
        mode: Mode d'analyse ("rapide" ou "detaille")
        resume_ia: Texte complet de la reponse IA
        routine_matin: Produits recommandes pour le matin
        routine_soir: Produits recommandes pour le soir
        alertes: Alertes generees par l'IA
        conseils_jour: Conseil personnalise du jour
    """
    id: str
    date: str
    mode: str
    resume_ia: str = ""
    routine_matin: list = field(default_factory=list)
    routine_soir: list = field(default_factory=list)
    alertes: list = field(default_factory=list)
    conseils_jour: str = ""
    activites_jour: list = field(default_factory=list)

    def vers_dict(self) -> dict:
        """Convertit en dictionnaire pour serialisation JSON."""
        return {
            "id": self.id,
            "date": self.date,
            "mode": self.mode,
            "resume_ia": self.resume_ia,
            "routine_matin": self.routine_matin,
            "routine_soir": self.routine_soir,
            "alertes": self.alertes,
            "conseils_jour": self.conseils_jour,
            "activites_jour": self.activites_jour,
        }

    @classmethod
    def depuis_dict(cls, data: dict) -> "EntreeHistorique":
        """Cree une entree depuis un dictionnaire."""
        return cls(
            id=data.get("id", ""),
            date=data.get("date", ""),
            mode=data.get("mode", "rapide"),
            resume_ia=data.get("resume_ia", ""),
            routine_matin=data.get("routine_matin", []),
            routine_soir=data.get("routine_soir", []),
            alertes=data.get("alertes", []),
            conseils_jour=data.get("conseils_jour", ""),
            activites_jour=data.get("activites_jour", []),
        )


# =============================================================================
# SETTINGS
# =============================================================================

@dataclass
class Settings:
    """
    Parametres de l'application.

    Attributes:
        gemini_api_key: Cle API Google Gemini
    """
    gemini_api_key: str = ""

    def vers_dict(self) -> dict:
        """Convertit en dictionnaire pour serialisation JSON."""
        return {
            "gemini_api_key": self.gemini_api_key,
        }

    @classmethod
    def depuis_dict(cls, data: dict) -> "Settings":
        """Cree depuis un dictionnaire."""
        return cls(
            gemini_api_key=data.get("gemini_api_key", ""),
        )
