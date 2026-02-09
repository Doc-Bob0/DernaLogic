"""
Module de gestion du profil utilisateur.

Stocke les informations permanentes sur l'utilisateur :
- Type de peau
- Problèmes de peau / maladies
- Préférences personnelles

Les données quotidiennes (stress, état du jour) sont gérées en session.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum
from pathlib import Path
import json


# =============================================================================
# ÉNUMÉRATIONS
# =============================================================================

class TypePeau(Enum):
    """Types de peau possibles."""
    NORMALE = "normale"
    SECHE = "seche"
    GRASSE = "grasse"
    MIXTE = "mixte"
    SENSIBLE = "sensible"
    
    @classmethod
    def from_str(cls, valeur: str) -> "TypePeau":
        """Convertit une chaîne en TypePeau."""
        for membre in cls:
            if membre.value == valeur:
                return membre
        return cls.NORMALE


class ProblemePeau(Enum):
    """Problèmes de peau / maladies dermatologiques."""
    ACNE = "acne"
    ECZEMA = "eczema"
    ROSACEE = "rosacee"
    PSORIASIS = "psoriasis"
    DERMATITE = "dermatite"
    HYPERPIGMENTATION = "hyperpigmentation"
    RIDES = "rides"
    PORES_DILATES = "pores_dilates"
    DESHYDRATATION = "deshydratation"
    TACHES = "taches"
    ROUGEURS = "rougeurs"
    
    @classmethod
    def from_str(cls, valeur: str) -> Optional["ProblemePeau"]:
        """Convertit une chaîne en ProblemePeau."""
        for membre in cls:
            if membre.value == valeur:
                return membre
        return None
    
    def label(self) -> str:
        """Retourne le label affichable."""
        labels = {
            "acne": "Acné",
            "eczema": "Eczéma",
            "rosacee": "Rosacée",
            "psoriasis": "Psoriasis",
            "dermatite": "Dermatite",
            "hyperpigmentation": "Hyperpigmentation",
            "rides": "Rides / Ridules",
            "pores_dilates": "Pores dilatés",
            "deshydratation": "Déshydratation",
            "taches": "Taches pigmentaires",
            "rougeurs": "Rougeurs"
        }
        return labels.get(self.value, self.value)


# =============================================================================
# MODÈLES DE DONNÉES
# =============================================================================

@dataclass
class ProfilUtilisateur:
    """
    Profil permanent de l'utilisateur.
    
    Attributes:
        type_peau: Type de peau de l'utilisateur
        problemes: Liste des problèmes de peau
        notes_permanentes: Notes personnelles permanentes
    """
    type_peau: TypePeau = TypePeau.NORMALE
    problemes: List[str] = field(default_factory=list)
    notes_permanentes: str = ""
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            "type_peau": self.type_peau.value,
            "problemes": self.problemes,
            "notes_permanentes": self.notes_permanentes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProfilUtilisateur":
        """Crée une instance depuis un dictionnaire."""
        return cls(
            type_peau=TypePeau.from_str(data.get("type_peau", "normale")),
            problemes=data.get("problemes", []),
            notes_permanentes=data.get("notes_permanentes", "")
        )
    
    def description_problemes(self) -> str:
        """Retourne une description textuelle des problèmes."""
        if not self.problemes:
            return "Aucun problème particulier"
        
        labels = []
        for p in self.problemes:
            prob = ProblemePeau.from_str(p)
            if prob:
                labels.append(prob.label())
            else:
                labels.append(p)
        return ", ".join(labels)


@dataclass
class EtatQuotidien:
    """
    État quotidien de l'utilisateur (non sauvegardé).
    
    Attributes:
        niveau_stress: Niveau de stress de 1 à 10
        etat_peau_jour: Description de l'état de la peau aujourd'hui
    """
    niveau_stress: int = 5
    etat_peau_jour: str = ""
    
    def to_prompt(self) -> str:
        """Génère le texte pour le prompt IA."""
        lignes = []
        lignes.append(f"Niveau de stress aujourd'hui : {self.niveau_stress}/10")
        
        if self.etat_peau_jour:
            lignes.append(f"État de la peau aujourd'hui : {self.etat_peau_jour}")
        
        return "\n".join(lignes)


# =============================================================================
# GESTIONNAIRE DE PROFIL
# =============================================================================

class GestionnaireProfil:
    """
    Gère le chargement et la sauvegarde du profil utilisateur.
    
    Le profil est stocké dans user_data/profil.json
    """
    
    def __init__(self, chemin: str = None):
        """
        Initialise le gestionnaire.
        
        Args:
            chemin: Chemin vers le fichier de profil (optionnel)
        """
        if chemin:
            self.chemin = Path(chemin)
        else:
            self.chemin = Path(__file__).parent.parent / "user_data" / "profil.json"
        
        self.profil = self._charger()
        self.etat_quotidien = EtatQuotidien()
    
    def _charger(self) -> ProfilUtilisateur:
        """Charge le profil depuis le fichier JSON."""
        if self.chemin.exists():
            try:
                with open(self.chemin, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return ProfilUtilisateur.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                return ProfilUtilisateur()
        return ProfilUtilisateur()
    
    def sauvegarder(self) -> None:
        """Sauvegarde le profil dans le fichier JSON."""
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        with open(self.chemin, "w", encoding="utf-8") as f:
            json.dump(self.profil.to_dict(), f, indent=2, ensure_ascii=False)
    
    def modifier_type_peau(self, type_peau: TypePeau) -> None:
        """Modifie le type de peau."""
        self.profil.type_peau = type_peau
        self.sauvegarder()
    
    def ajouter_probleme(self, probleme: str) -> None:
        """Ajoute un problème de peau."""
        if probleme not in self.profil.problemes:
            self.profil.problemes.append(probleme)
            self.sauvegarder()
    
    def retirer_probleme(self, probleme: str) -> None:
        """Retire un problème de peau."""
        if probleme in self.profil.problemes:
            self.profil.problemes.remove(probleme)
            self.sauvegarder()
    
    def modifier_notes(self, notes: str) -> None:
        """Modifie les notes permanentes."""
        self.profil.notes_permanentes = notes
        self.sauvegarder()
    
    def definir_stress(self, niveau: int) -> None:
        """Définit le niveau de stress quotidien (1-10)."""
        self.etat_quotidien.niveau_stress = max(1, min(10, niveau))
    
    def definir_etat_jour(self, etat: str) -> None:
        """Définit l'état de la peau du jour."""
        self.etat_quotidien.etat_peau_jour = etat
    
    def generer_contexte_ia(self) -> str:
        """
        Génère le contexte utilisateur pour le prompt IA.
        
        Returns:
            Texte formaté avec toutes les informations utilisateur
        """
        lignes = []
        
        # Type de peau
        type_labels = {
            "normale": "normale",
            "seche": "sèche",
            "grasse": "grasse",
            "mixte": "mixte",
            "sensible": "sensible"
        }
        lignes.append(f"Type de peau : {type_labels.get(self.profil.type_peau.value, 'non défini')}")
        
        # Problèmes
        lignes.append(f"Problèmes de peau : {self.profil.description_problemes()}")
        
        # Notes permanentes
        if self.profil.notes_permanentes:
            lignes.append(f"Notes personnelles : {self.profil.notes_permanentes}")
        
        # État quotidien
        lignes.append("")
        lignes.append(self.etat_quotidien.to_prompt())
        
        return "\n".join(lignes)
