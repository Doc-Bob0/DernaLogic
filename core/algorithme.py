"""
DermaLogic - Algorithme de Decision Dermatologique
===================================================

Ce module re-exporte les modeles depuis core.models pour compatibilite,
et contient l'ancien MoteurDecision (deprecie, remplace par l'analyse IA).
"""

from dataclasses import dataclass, field
from typing import Optional

# Re-export depuis models.py pour compatibilite
from core.models import (
    Categorie,
    ActiveTag,
    MomentUtilisation,
    ProduitDerma,
)


# =============================================================================
# CONSTANTES - SEUILS ENVIRONNEMENTAUX
# =============================================================================

SEUIL_UV_CRITIQUE = 3.0
SEUIL_HUMIDITE_BASSE = 45.0
SEUIL_HUMIDITE_HAUTE = 70.0
SEUIL_PM25_POLLUTION = 25.0


# =============================================================================
# CONDITIONS ENVIRONNEMENTALES
# =============================================================================

@dataclass
class ConditionsEnvironnementales:
    """Donnees environnementales pour l'algorithme de decision."""
    indice_uv: float
    humidite: float
    pm2_5: Optional[float] = None

    @property
    def uv_critique(self) -> bool:
        return self.indice_uv > SEUIL_UV_CRITIQUE

    @property
    def environnement_sec(self) -> bool:
        return self.humidite < SEUIL_HUMIDITE_BASSE

    @property
    def environnement_humide(self) -> bool:
        return self.humidite > SEUIL_HUMIDITE_HAUTE

    @property
    def pollution_elevee(self) -> bool:
        if self.pm2_5 is None:
            return False
        return self.pm2_5 > SEUIL_PM25_POLLUTION


# =============================================================================
# RESULTATS DE L'ALGORITHME (gardes pour compatibilite)
# =============================================================================

@dataclass
class ResultatMoment:
    produits: list = field(default_factory=list)
    nettoyant_optimal: Optional[ProduitDerma] = None


@dataclass
class ResultatDecision:
    matin: ResultatMoment = field(default_factory=ResultatMoment)
    journee: ResultatMoment = field(default_factory=ResultatMoment)
    soir: ResultatMoment = field(default_factory=ResultatMoment)
    produits_exclus: list = field(default_factory=list)
    raisons_exclusion: dict = field(default_factory=dict)
    filtres_appliques: list = field(default_factory=list)


# =============================================================================
# MOTEUR DE DECISION (DEPRECIE - remplace par core.analyseur.AnalyseurDerma)
# =============================================================================

class MoteurDecision:
    """
    DEPRECIE : Utiliser core.analyseur.AnalyseurDerma a la place.

    Ancien moteur de decision algorithmique.
    Garde pour reference et tests.
    """

    def __init__(self, produits: list[ProduitDerma]):
        self.produits_originaux = produits.copy()

    def analyser(self, conditions: ConditionsEnvironnementales) -> ResultatDecision:
        resultat = ResultatDecision()
        produits_actifs = self.produits_originaux.copy()

        # A. FILTRE DE SECURITE (UV)
        if conditions.uv_critique:
            resultat.filtres_appliques.append(f"UV={conditions.indice_uv:.1f} > 3")
            produits_filtres = []
            for p in produits_actifs:
                if p.photosensitive:
                    if p.moment in [MomentUtilisation.MATIN, MomentUtilisation.JOURNEE]:
                        resultat.produits_exclus.append(p)
                        resultat.raisons_exclusion[p.nom] = "Photosensible + UV eleve"
                    else:
                        produits_filtres.append(p)
                else:
                    produits_filtres.append(p)
            produits_actifs = produits_filtres

        # B. FILTRE DE TEXTURE (Humidite)
        if conditions.environnement_sec:
            resultat.filtres_appliques.append(f"H={conditions.humidite:.0f}% < 45%")
            produits_actifs.sort(key=lambda p: p.occlusivity, reverse=True)
        elif conditions.environnement_humide:
            resultat.filtres_appliques.append(f"H={conditions.humidite:.0f}% > 70%")
            produits_filtres = []
            for p in produits_actifs:
                if p.occlusivity <= 2 and p.category != Categorie.CLEANSER:
                    resultat.produits_exclus.append(p)
                    resultat.raisons_exclusion[p.nom] = "Trop occlusif (humidite elevee)"
                else:
                    produits_filtres.append(p)
            produits_actifs = produits_filtres

        # C. FILTRE DE PURETE (PM2.5)
        nettoyant_optimal = None
        if conditions.pollution_elevee:
            resultat.filtres_appliques.append(f"PM2.5={conditions.pm2_5:.0f} > 25")
            nettoyants = [p for p in produits_actifs if p.category == Categorie.CLEANSER]
            if nettoyants:
                nettoyant_optimal = max(nettoyants, key=lambda p: p.cleansing_power)

        # REPARTITION PAR MOMENT
        def filtrer_par_moment(moment: MomentUtilisation) -> list[ProduitDerma]:
            return [
                p for p in produits_actifs
                if p.moment == moment or p.moment == MomentUtilisation.TOUS
            ]

        resultat.matin = ResultatMoment(
            produits=filtrer_par_moment(MomentUtilisation.MATIN),
            nettoyant_optimal=nettoyant_optimal,
        )
        resultat.journee = ResultatMoment(
            produits=filtrer_par_moment(MomentUtilisation.JOURNEE),
            nettoyant_optimal=None,
        )
        resultat.soir = ResultatMoment(
            produits=filtrer_par_moment(MomentUtilisation.SOIR),
            nettoyant_optimal=nettoyant_optimal,
        )

        return resultat
