"""
DermaLogic - Algorithme de Décision Dermatologique
===================================================

Ce module implémente l'algorithme de filtrage intelligent des produits
basé sur les conditions environnementales (UV, humidité, pollution).

L'algorithme applique 3 filtres successifs :
1. Filtre de Sécurité (UV) - Exclut les produits photosensibles si UV élevé
2. Filtre de Texture (Humidité) - Adapte selon le niveau d'humidité
3. Filtre de Pureté (Pollution) - Recommande le meilleur nettoyant si pollution élevée
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# =============================================================================
# CONSTANTES - SEUILS ENVIRONNEMENTAUX
# =============================================================================

SEUIL_UV_CRITIQUE = 3.0       # Au-dessus: exclure les photosensibles
SEUIL_HUMIDITE_BASSE = 45.0   # En-dessous: prioriser haute occlusivité
SEUIL_HUMIDITE_HAUTE = 70.0   # Au-dessus: éviter les textures trop riches
SEUIL_PM25_POLLUTION = 25.0   # Au-dessus: recommander nettoyage puissant


# =============================================================================
# ÉNUMÉRATIONS
# =============================================================================

class Categorie(Enum):
    """Catégories de produits dermatologiques."""
    CLEANSER = "cleanser"         # Nettoyant
    TREATMENT = "treatment"       # Traitement (sérum, acide)
    MOISTURIZER = "moisturizer"   # Hydratant
    PROTECTION = "protection"     # Protection solaire


class ActiveTag(Enum):
    """Tags d'action principale des actifs."""
    ACNE = "acne"           # Anti-acné (BHA, niacinamide)
    HYDRATION = "hydration" # Hydratation (acide hyaluronique)
    REPAIR = "repair"       # Réparation (céramides, panthénol)


class MomentUtilisation(Enum):
    """Moment d'utilisation recommandé du produit."""
    MATIN = "matin"     # Routine du matin uniquement
    JOURNEE = "journee" # Réapplication en journée
    SOIR = "soir"       # Routine du soir uniquement
    TOUS = "tous"       # Utilisable à tout moment


# =============================================================================
# MODÈLE PRODUIT
# =============================================================================

@dataclass
class ProduitDerma:
    """
    Représentation d'un produit dermatologique pour l'algorithme.
    
    Attributes:
        nom: Nom du produit
        category: Type de produit (cleanser, treatment, moisturizer, protection)
        moment: Quand utiliser le produit
        photosensitive: True si le produit réagit aux UV (BHA, rétinol, AHA)
        occlusivity: Richesse de texture (1=léger, 5=très riche/occlusif)
        cleansing_power: Puissance nettoyante (1=doux, 5=puissant)
        active_tag: Action principale du produit
    
    Example:
        >>> serum = ProduitDerma(
        ...     nom="Paula's Choice BHA 2%",
        ...     category=Categorie.TREATMENT,
        ...     moment=MomentUtilisation.SOIR,
        ...     photosensitive=True,
        ...     occlusivity=1,
        ...     cleansing_power=1,
        ...     active_tag=ActiveTag.ACNE
        ... )
    """
    nom: str
    category: Categorie
    moment: MomentUtilisation = MomentUtilisation.TOUS
    photosensitive: bool = False
    occlusivity: int = 3
    cleansing_power: int = 3
    active_tag: ActiveTag = ActiveTag.HYDRATION
    
    def __post_init__(self):
        """Validation des valeurs après initialisation."""
        if not 1 <= self.occlusivity <= 5:
            raise ValueError(f"occlusivity doit être entre 1 et 5, reçu: {self.occlusivity}")
        if not 1 <= self.cleansing_power <= 5:
            raise ValueError(f"cleansing_power doit être entre 1 et 5, reçu: {self.cleansing_power}")
    
    def vers_dict(self) -> dict:
        """Convertit le produit en dictionnaire pour sérialisation JSON."""
        return {
            "nom": self.nom,
            "category": self.category.value,
            "moment": self.moment.value,
            "photosensitive": self.photosensitive,
            "occlusivity": self.occlusivity,
            "cleansing_power": self.cleansing_power,
            "active_tag": self.active_tag.value
        }
    
    @classmethod
    def depuis_dict(cls, data: dict) -> "ProduitDerma":
        """
        Crée un produit depuis un dictionnaire.
        
        Args:
            data: Dictionnaire avec les attributs du produit
        
        Returns:
            Instance de ProduitDerma
        """
        return cls(
            nom=data["nom"],
            category=Categorie(data["category"]),
            moment=MomentUtilisation(data.get("moment", "tous")),
            photosensitive=data.get("photosensitive", False),
            occlusivity=data.get("occlusivity", 3),
            cleansing_power=data.get("cleansing_power", 3),
            active_tag=ActiveTag(data.get("active_tag", "hydration"))
        )


# =============================================================================
# CONDITIONS ENVIRONNEMENTALES
# =============================================================================

@dataclass
class ConditionsEnvironnementales:
    """
    Données environnementales pour l'algorithme de décision.
    
    Attributes:
        indice_uv: Indice UV actuel (0-11+)
        humidite: Humidité relative en % (0-100)
        pm2_5: Particules fines PM2.5 en µg/m³ (optionnel)
    """
    indice_uv: float
    humidite: float
    pm2_5: Optional[float] = None
    
    @property
    def uv_critique(self) -> bool:
        """True si UV dépasse le seuil critique."""
        return self.indice_uv > SEUIL_UV_CRITIQUE
    
    @property
    def environnement_sec(self) -> bool:
        """True si l'air est sec (humidité basse)."""
        return self.humidite < SEUIL_HUMIDITE_BASSE
    
    @property
    def environnement_humide(self) -> bool:
        """True si l'air est très humide."""
        return self.humidite > SEUIL_HUMIDITE_HAUTE
    
    @property
    def pollution_elevee(self) -> bool:
        """True si la pollution est élevée."""
        if self.pm2_5 is None:
            return False
        return self.pm2_5 > SEUIL_PM25_POLLUTION


# =============================================================================
# RÉSULTATS DE L'ALGORITHME
# =============================================================================

@dataclass
class ResultatMoment:
    """
    Résultat de l'analyse pour un moment spécifique de la journée.
    
    Attributes:
        produits: Liste des produits recommandés pour ce moment
        nettoyant_optimal: Nettoyant le plus adapté (si pollution élevée)
    """
    produits: list = field(default_factory=list)
    nettoyant_optimal: Optional[ProduitDerma] = None


@dataclass
class ResultatDecision:
    """
    Résultat complet de l'algorithme de décision.
    
    Attributes:
        matin: Recommandations pour le matin
        journee: Recommandations pour la journée
        soir: Recommandations pour le soir
        produits_exclus: Produits exclus par les filtres
        raisons_exclusion: Mapping nom_produit -> raison de l'exclusion
        filtres_appliques: Liste des filtres activés
    """
    matin: ResultatMoment = field(default_factory=ResultatMoment)
    journee: ResultatMoment = field(default_factory=ResultatMoment)
    soir: ResultatMoment = field(default_factory=ResultatMoment)
    produits_exclus: list = field(default_factory=list)
    raisons_exclusion: dict = field(default_factory=dict)
    filtres_appliques: list = field(default_factory=list)


# =============================================================================
# MOTEUR DE DÉCISION
# =============================================================================

class MoteurDecision:
    """
    Moteur de décision dermatologique.
    
    Applique les filtres de sécurité, texture et pureté basés sur
    les conditions environnementales pour recommander les produits
    les plus adaptés.
    
    Attributes:
        produits_originaux: Liste des produits à analyser
    
    Example:
        >>> moteur = MoteurDecision(mes_produits)
        >>> conditions = ConditionsEnvironnementales(
        ...     indice_uv=5.0,
        ...     humidite=35,
        ...     pm2_5=30
        ... )
        >>> resultat = moteur.analyser(conditions)
        >>> print(resultat.filtres_appliques)
        ['UV=5.0 > 3', 'H=35% < 45%', 'PM2.5=30 > 25']
    """
    
    def __init__(self, produits: list[ProduitDerma]):
        """
        Initialise le moteur avec une liste de produits.
        
        Args:
            produits: Liste des produits à analyser
        """
        self.produits_originaux = produits.copy()
    
    def analyser(self, conditions: ConditionsEnvironnementales) -> ResultatDecision:
        """
        Analyse les conditions et filtre les produits.
        
        Args:
            conditions: Conditions environnementales actuelles
        
        Returns:
            ResultatDecision avec les recommandations par moment
        """
        resultat = ResultatDecision()
        produits_actifs = self.produits_originaux.copy()
        
        # =================================================================
        # A. FILTRE DE SÉCURITÉ (UV vs Photosensibilité)
        # =================================================================
        if conditions.uv_critique:
            resultat.filtres_appliques.append(f"UV={conditions.indice_uv:.1f} > 3")
            
            produits_filtres = []
            for p in produits_actifs:
                if p.photosensitive:
                    # Les photosensibles sont exclus matin/journée mais ok le soir
                    if p.moment in [MomentUtilisation.MATIN, MomentUtilisation.JOURNEE]:
                        resultat.produits_exclus.append(p)
                        resultat.raisons_exclusion[p.nom] = "Photosensible + UV eleve"
                    else:
                        produits_filtres.append(p)
                else:
                    produits_filtres.append(p)
            
            produits_actifs = produits_filtres
        
        # =================================================================
        # B. FILTRE DE TEXTURE (Humidité vs Occlusivité)
        # =================================================================
        if conditions.environnement_sec:
            resultat.filtres_appliques.append(f"H={conditions.humidite:.0f}% < 45%")
            # Prioriser les textures riches (tri par occlusivité décroissante)
            produits_actifs.sort(key=lambda p: p.occlusivity, reverse=True)
            
        elif conditions.environnement_humide:
            resultat.filtres_appliques.append(f"H={conditions.humidite:.0f}% > 70%")
            
            produits_filtres = []
            for p in produits_actifs:
                # Exclure les textures trop légères en environnement humide
                # (sauf les nettoyants qui restent toujours)
                if p.occlusivity <= 2 and p.category != Categorie.CLEANSER:
                    resultat.produits_exclus.append(p)
                    resultat.raisons_exclusion[p.nom] = "Trop occlusif (humidite elevee)"
                else:
                    produits_filtres.append(p)
            
            produits_actifs = produits_filtres
        
        # =================================================================
        # C. FILTRE DE PURETÉ (PM2.5 vs Nettoyage)
        # =================================================================
        nettoyant_optimal = None
        if conditions.pollution_elevee:
            resultat.filtres_appliques.append(f"PM2.5={conditions.pm2_5:.0f} > 25")
            
            # Trouver le nettoyant le plus efficace
            nettoyants = [p for p in produits_actifs if p.category == Categorie.CLEANSER]
            if nettoyants:
                nettoyant_optimal = max(nettoyants, key=lambda p: p.cleansing_power)
        
        # =================================================================
        # RÉPARTITION PAR MOMENT
        # =================================================================
        def filtrer_par_moment(moment: MomentUtilisation) -> list[ProduitDerma]:
            """Retourne les produits pour un moment donné (ou TOUS)."""
            return [
                p for p in produits_actifs 
                if p.moment == moment or p.moment == MomentUtilisation.TOUS
            ]
        
        resultat.matin = ResultatMoment(
            produits=filtrer_par_moment(MomentUtilisation.MATIN),
            nettoyant_optimal=nettoyant_optimal
        )
        resultat.journee = ResultatMoment(
            produits=filtrer_par_moment(MomentUtilisation.JOURNEE),
            nettoyant_optimal=None
        )
        resultat.soir = ResultatMoment(
            produits=filtrer_par_moment(MomentUtilisation.SOIR),
            nettoyant_optimal=nettoyant_optimal
        )
        
        return resultat


# =============================================================================
# TEST DU MODULE
# =============================================================================

if __name__ == "__main__":
    print("Test du module Algorithme")
    print("=" * 40)
    
    # Créer quelques produits de test
    produits = [
        ProduitDerma(
            nom="CeraVe Nettoyant",
            category=Categorie.CLEANSER,
            moment=MomentUtilisation.TOUS,
            cleansing_power=3,
            occlusivity=1
        ),
        ProduitDerma(
            nom="Paula's Choice BHA",
            category=Categorie.TREATMENT,
            moment=MomentUtilisation.SOIR,
            photosensitive=True,
            active_tag=ActiveTag.ACNE
        ),
        ProduitDerma(
            nom="La Roche-Posay SPF50",
            category=Categorie.PROTECTION,
            moment=MomentUtilisation.MATIN
        ),
    ]
    
    # Conditions de test
    conditions = ConditionsEnvironnementales(
        indice_uv=5.0,
        humidite=40,
        pm2_5=30
    )
    
    # Analyser
    moteur = MoteurDecision(produits)
    resultat = moteur.analyser(conditions)
    
    print(f"Filtres: {resultat.filtres_appliques}")
    print(f"Matin: {[p.nom for p in resultat.matin.produits]}")
    print(f"Soir: {[p.nom for p in resultat.soir.produits]}")
    print(f"Exclus: {[p.nom for p in resultat.produits_exclus]}")
