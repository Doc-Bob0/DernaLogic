"""
DermaLogic - Interface Graphique
================================

Ce module implémente l'interface utilisateur avec CustomTkinter :

Structure :
-----------
- GestionnaireProduits : Persistance JSON des produits utilisateur
- CarteEnvironnement : Widget pour afficher une donnée environnementale
- LigneMoment : Widget pour afficher les produits d'un moment (matin/journée/soir)
- PageAccueil : Page principale avec analyse et recommandations
- PageProduits : Page de gestion des produits personnalisés
- FormulaireProduit : Dialogue d'ajout de produit
- FenetreSelectionVille : Dialogue de recherche de ville
- ApplicationPrincipale : Fenêtre principale avec navigation

Thème : Mode sombre avec palette custom
"""

import sys
import json
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

# Configuration du path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.open_meteo import (
    ClientOpenMeteo,
    DonneesEnvironnementales,
    rechercher_villes,
    Localisation,
)
from api.gemini import (
    ClientGemini, 
    ResultatAnalyseIA,
    ResultatRoutineIA,
    ProduitRoutine,
    RoutineMoment,
)
from core.algorithme import (
    ProduitDerma,
    Categorie,
    ActiveTag,
    MomentUtilisation,
    MoteurDecision,
    ConditionsEnvironnementales,
    ResultatDecision,
)
from core.config import GestionnaireConfig, VilleConfig
from core.historique import (
    GestionnaireHistorique,
    ConditionsAnalyse,
    ProduitAnalyse,
    ResultatAnalyseHistorique,
    creer_conditions_depuis_env,
    creer_produit_depuis_resultat,
)
from core.profil import (
    TypePeau,
    ProblemePeau,
    ProfilUtilisateur,
    EtatQuotidien,
    GestionnaireProfil,
)


# =============================================================================
# CONSTANTES DE STYLE
# =============================================================================

# Couleurs principales
COULEUR_FOND = "#0f0f1a"
COULEUR_PANNEAU = "#16213e"
COULEUR_CARTE = "#1a1a2e"
COULEUR_CARTE_HOVER = "#252545"
COULEUR_ACCENT = "#4ecca3"
COULEUR_ACCENT_HOVER = "#3db892"
COULEUR_DANGER = "#e94560"
COULEUR_TEXTE_SECONDAIRE = "#8b8b9e"
COULEUR_BORDURE = "#2a2a4a"

# Couleurs par catégorie de produit
COULEURS_CATEGORIE = {
    "cleanser": "#00b4d8",
    "treatment": "#f9ed69",
    "moisturizer": "#4ecca3",
    "protection": "#f38181",
}

# Couleurs par moment
COULEURS_MOMENT = {
    "matin": ("#f9ed69", "MATIN"),
    "journee": ("#00b4d8", "JOURNEE"),
    "soir": ("#9b59b6", "SOIR"),
    "tous": ("#4ecca3", "TOUS MOMENTS"),
}


# =============================================================================
# GESTIONNAIRE DE PRODUITS
# =============================================================================

class GestionnaireProduits:
    """
    Gère les produits personnalisés avec persistance JSON.
    
    Les produits sont sauvegardés dans user_data/produits_derma.json
    et chargés automatiquement au démarrage.
    
    Note: Le dossier user_data/ est ignoré par git pour ne pas
    partager les données personnelles de l'utilisateur.
    
    Attributes:
        chemin_fichier: Chemin vers le fichier JSON
        produits: Liste des produits en mémoire
    """
    
    def __init__(self, chemin_fichier: Path = None):
        """
        Initialise le gestionnaire.
        
        Args:
            chemin_fichier: Chemin du fichier JSON (optionnel)
        """
        if chemin_fichier is None:
            # Utilise user_data/ qui est ignoré par git
            chemin_fichier = Path(__file__).parent.parent / "user_data" / "produits_derma.json"
        
        self.chemin_fichier = chemin_fichier
        self.chemin_fichier.parent.mkdir(parents=True, exist_ok=True)
        
        self.produits: list[ProduitDerma] = []
        self._charger()
    
    def _charger(self) -> None:
        """Charge les produits depuis le fichier JSON."""
        if not self.chemin_fichier.exists():
            return
            
        try:
            with open(self.chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.produits = [ProduitDerma.depuis_dict(p) for p in data]
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"[GestionnaireProduits] Erreur chargement: {e}")
            self.produits = []
    
    def _sauvegarder(self) -> None:
        """Sauvegarde les produits dans le fichier JSON."""
        try:
            with open(self.chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(
                    [p.vers_dict() for p in self.produits],
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except IOError as e:
            print(f"[GestionnaireProduits] Erreur sauvegarde: {e}")
    
    def obtenir_tous(self) -> list[ProduitDerma]:
        """Retourne une copie de la liste des produits."""
        return self.produits.copy()
    
    def ajouter(self, produit: ProduitDerma) -> None:
        """Ajoute un produit et sauvegarde."""
        self.produits.append(produit)
        self._sauvegarder()
    
    def supprimer(self, index: int) -> None:
        """Supprime un produit par son index et sauvegarde."""
        if 0 <= index < len(self.produits):
            self.produits.pop(index)
            self._sauvegarder()


# =============================================================================
# WIDGETS PERSONNALISÉS
# =============================================================================

class CarteEnvironnement(ctk.CTkFrame):
    """
    Widget carte compacte pour afficher une donnée environnementale.
    
    Affiche un titre, une valeur principale et un niveau textuel coloré.
    """
    
    def __init__(self, master, titre: str, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COULEUR_CARTE, corner_radius=12)
        
        self.label_titre = ctk.CTkLabel(
            self,
            text=titre,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_titre.pack(pady=(10, 2))
        
        self.label_valeur = ctk.CTkLabel(
            self,
            text="--",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.label_valeur.pack()
        
        self.label_niveau = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=COULEUR_ACCENT
        )
        self.label_niveau.pack(pady=(0, 10))
    
    def mettre_a_jour(self, valeur: str, niveau: str = "", couleur: str = COULEUR_ACCENT) -> None:
        """
        Met à jour l'affichage de la carte.
        
        Args:
            valeur: Valeur principale à afficher
            niveau: Texte de niveau (ex: "Modere", "Eleve")
            couleur: Couleur du texte de niveau
        """
        self.label_valeur.configure(text=valeur)
        self.label_niveau.configure(text=niveau, text_color=couleur)


class LigneMoment(ctk.CTkFrame):
    """
    Widget ligne horizontale pour un moment de la journée.
    
    Affiche un header avec le nom du moment et une liste scrollable
    horizontale de cartes produits.
    """
    
    def __init__(self, master, moment: str, **kwargs):
        super().__init__(master, **kwargs)
        self.moment = moment
        self.configure(fg_color=COULEUR_PANNEAU, corner_radius=12)
        
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))
        
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=12, pady=8)
        
        # Indicateur couleur
        ctk.CTkFrame(
            frame_header,
            fg_color=couleur,
            width=6,
            height=25,
            corner_radius=3
        ).pack(side="left", padx=(0, 10))
        
        self.label_titre = ctk.CTkLabel(
            frame_header,
            text=titre,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_titre.pack(side="left")
        
        self.label_count = ctk.CTkLabel(
            frame_header,
            text="0 produits",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_count.pack(side="right")
        
        # Liste des produits (scroll horizontal)
        self.frame_produits = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            orientation="horizontal",
            height=90
        )
        self.frame_produits.pack(fill="x", padx=8, pady=(0, 10))
        
        # Message par défaut
        self._afficher_vide()
    
    def _afficher_vide(self) -> None:
        """Affiche un message quand aucun produit n'est disponible."""
        ctk.CTkLabel(
            self.frame_produits,
            text="Aucun produit",
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(pady=25, padx=50)
    
    def afficher_produits(
        self,
        produits: list[ProduitDerma],
        nettoyant_optimal: ProduitDerma = None
    ) -> None:
        """
        Affiche les produits pour ce moment.
        
        Args:
            produits: Liste des produits à afficher
            nettoyant_optimal: Nettoyant recommandé (mis en évidence)
        """
        # Nettoyer
        for widget in self.frame_produits.winfo_children():
            widget.destroy()
        
        if not produits:
            self._afficher_vide()
            self.label_count.configure(text="0 produits")
            return
        
        self.label_count.configure(text=f"{len(produits)} produits")
        
        for produit in produits:
            is_optimal = (
                nettoyant_optimal is not None
                and produit.nom == nettoyant_optimal.nom
            )
            self._creer_carte_produit(produit, is_optimal)
    
    def _creer_carte_produit(self, produit: ProduitDerma, is_optimal: bool = False) -> None:
        """Crée une carte pour un produit."""
        couleur_cat = COULEURS_CATEGORIE.get(produit.category.value, "#fff")
        
        frame = ctk.CTkFrame(
            self.frame_produits,
            fg_color="#0d7377" if is_optimal else COULEUR_CARTE_HOVER,
            corner_radius=10,
            width=180
        )
        frame.pack(side="left", padx=4, pady=5)
        frame.pack_propagate(False)
        
        frame_content = ctk.CTkFrame(frame, fg_color="transparent")
        frame_content.pack(fill="both", expand=True, padx=8, pady=6)
        
        # Ligne 1: badges
        frame_top = ctk.CTkFrame(frame_content, fg_color="transparent")
        frame_top.pack(fill="x")
        
        ctk.CTkLabel(
            frame_top,
            text=produit.category.value,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COULEUR_FOND,
            fg_color=couleur_cat,
            corner_radius=4,
            width=65
        ).pack(side="left")
        
        if is_optimal:
            ctk.CTkLabel(
                frame_top,
                text="OPTIMAL",
                font=ctk.CTkFont(size=8, weight="bold"),
                text_color=COULEUR_ACCENT
            ).pack(side="right")
        
        if produit.photosensitive:
            ctk.CTkLabel(
                frame_top,
                text="UV!",
                font=ctk.CTkFont(size=8, weight="bold"),
                text_color=COULEUR_DANGER
            ).pack(side="right", padx=3)
        
        # Ligne 2: nom
        ctk.CTkLabel(
            frame_content,
            text=produit.nom,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
            wraplength=160
        ).pack(fill="x", pady=(4, 0))
        
        # Ligne 3: caractéristiques
        ctk.CTkLabel(
            frame_content,
            text=f"O:{produit.occlusivity} C:{produit.cleansing_power}",
            font=ctk.CTkFont(size=9),
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w"
        ).pack(fill="x")


# =============================================================================
# PAGE ACCUEIL (ANALYSE)
# =============================================================================

class PageAccueil(ctk.CTkFrame):
    """
    Page principale avec conditions environnementales et recommandations.
    
    Structure :
    - Section conditions (UV, humidité, PM2.5, température)
    - Bouton d'analyse
    - Barre de filtres actifs
    - 3 lignes de recommandations (matin, journée, soir)
    - Section des produits exclus
    """
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.configure(fg_color="transparent")
        self._creer_interface()
    
    def _creer_interface(self) -> None:
        """Construit l'interface de la page."""
        
        # ===== SECTION CONDITIONS =====
        frame_conditions = ctk.CTkFrame(self, fg_color=COULEUR_PANNEAU, corner_radius=15)
        frame_conditions.pack(fill="x", padx=20, pady=(10, 12))
        
        # Header conditions
        frame_header = ctk.CTkFrame(frame_conditions, fg_color="transparent")
        frame_header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            frame_header,
            text="Conditions Environnementales",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left")
        
        self.btn_actualiser = ctk.CTkButton(
            frame_header,
            text="Actualiser",
            command=self.app.actualiser_donnees,
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            width=100,
            height=28
        )
        self.btn_actualiser.pack(side="right")
        
        # Cartes environnement
        frame_cartes = ctk.CTkFrame(frame_conditions, fg_color="transparent")
        frame_cartes.pack(fill="x", padx=10, pady=(0, 10))
        
        self.carte_uv = CarteEnvironnement(frame_cartes, "Indice UV")
        self.carte_uv.pack(side="left", fill="both", expand=True, padx=4)
        
        self.carte_humidite = CarteEnvironnement(frame_cartes, "Humidite")
        self.carte_humidite.pack(side="left", fill="both", expand=True, padx=4)
        
        self.carte_pollution = CarteEnvironnement(frame_cartes, "PM2.5")
        self.carte_pollution.pack(side="left", fill="both", expand=True, padx=4)
        
        self.carte_temp = CarteEnvironnement(frame_cartes, "Temperature")
        self.carte_temp.pack(side="left", fill="both", expand=True, padx=4)
        
        # ===== BOUTONS D'ANALYSE =====
        frame_btns_analyse = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns_analyse.pack(fill="x", padx=20, pady=(0, 12))
        
        # Bouton analyse simple (algorithme local)
        self.btn_analyse_simple = ctk.CTkButton(
            frame_btns_analyse,
            text="⚡ Analyse rapide",
            command=self.app.lancer_analyse,
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45
        )
        self.btn_analyse_simple.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Bouton analyse IA avec instructions
        self.btn_analyse_ia = ctk.CTkButton(
            frame_btns_analyse,
            text="🤖 Analyse IA personnalisée",
            command=self.app.ouvrir_analyse_ia,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            text_color="#fff",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45
        )
        self.btn_analyse_ia.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # ===== BARRE DE FILTRES =====
        self.frame_filtres = ctk.CTkFrame(
            self,
            fg_color=COULEUR_CARTE,
            corner_radius=10,
            height=35
        )
        self.frame_filtres.pack(fill="x", padx=20, pady=(0, 10))
        self.frame_filtres.pack_propagate(False)
        
        self.label_filtres = ctk.CTkLabel(
            self.frame_filtres,
            text="Cliquez sur ANALYSER pour obtenir vos recommandations",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_filtres.pack(expand=True)
        
        # ===== RECOMMANDATIONS PAR MOMENT =====
        frame_reco = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame_reco.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.ligne_matin = LigneMoment(frame_reco, "matin")
        self.ligne_matin.pack(fill="x", pady=5)
        
        self.ligne_journee = LigneMoment(frame_reco, "journee")
        self.ligne_journee.pack(fill="x", pady=5)
        
        self.ligne_soir = LigneMoment(frame_reco, "soir")
        self.ligne_soir.pack(fill="x", pady=5)
        
        # Section exclus (cachée par défaut)
        self.frame_exclus = ctk.CTkFrame(
            frame_reco,
            fg_color="#2a1a2a",
            corner_radius=10
        )
        
        self.label_exclus = ctk.CTkLabel(
            self.frame_exclus,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_DANGER
        )
        self.label_exclus.pack(pady=8, padx=12)
    
    def afficher_resultat(self, resultat: ResultatDecision) -> None:
        """
        Affiche le résultat de l'analyse.
        
        Args:
            resultat: Résultat de l'algorithme de décision
        """
        # Filtres appliqués
        if resultat.filtres_appliques:
            txt = " | ".join(resultat.filtres_appliques)
            self.label_filtres.configure(
                text=f"Filtres actifs: {txt}",
                text_color="#f9ed69"
            )
        else:
            self.label_filtres.configure(
                text="Aucun filtre - Conditions normales",
                text_color=COULEUR_ACCENT
            )
        
        # Lignes par moment
        self.ligne_matin.afficher_produits(
            resultat.matin.produits,
            resultat.matin.nettoyant_optimal
        )
        self.ligne_journee.afficher_produits(
            resultat.journee.produits,
            resultat.journee.nettoyant_optimal
        )
        self.ligne_soir.afficher_produits(
            resultat.soir.produits,
            resultat.soir.nettoyant_optimal
        )
        
        # Produits exclus
        if resultat.produits_exclus:
            self.frame_exclus.pack(fill="x", pady=(10, 5))
            noms = ", ".join([
                f"{p.nom} ({resultat.raisons_exclusion.get(p.nom, '')})"
                for p in resultat.produits_exclus
            ])
            self.label_exclus.configure(text=f"Exclus: {noms}")
        else:
            self.frame_exclus.pack_forget()


# =============================================================================
# PAGE MES PRODUITS
# =============================================================================

class PageProduits(ctk.CTkFrame):
    """
    Page de gestion des produits personnalisés.
    
    Permet d'ajouter, visualiser et supprimer des produits.
    Les produits sont groupés par moment d'utilisation.
    """
    
    def __init__(self, master, gestionnaire: GestionnaireProduits, **kwargs):
        super().__init__(master, **kwargs)
        self.gestionnaire = gestionnaire
        self.configure(fg_color="transparent")
        self._creer_interface()
    
    def _creer_interface(self) -> None:
        """Construit l'interface de la page."""
        
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            frame_header,
            text="Mes Produits",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        self.label_count = ctk.CTkLabel(
            frame_header,
            text="0 produits",
            font=ctk.CTkFont(size=14),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_count.pack(side="left", padx=15)
        
        self.btn_ajouter = ctk.CTkButton(
            frame_header,
            text="+ Ajouter",
            command=self._ouvrir_formulaire,
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            font=ctk.CTkFont(weight="bold"),
            width=100
        )
        self.btn_ajouter.pack(side="right", padx=(5, 0))
        
        # Bouton Ajouter avec IA
        self.btn_ajouter_ia = ctk.CTkButton(
            frame_header,
            text="+ Ajouter avec IA",
            command=self._ajouter_avec_ia,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            text_color="#fff",
            font=ctk.CTkFont(weight="bold"),
            width=140
        )
        self.btn_ajouter_ia.pack(side="right")
        
        # Liste des produits
        self.frame_liste = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_liste.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.actualiser_liste()
    
    def actualiser_liste(self) -> None:
        """Actualise l'affichage de la liste des produits."""
        # Nettoyer
        for widget in self.frame_liste.winfo_children():
            widget.destroy()
        
        produits = self.gestionnaire.obtenir_tous()
        self.label_count.configure(text=f"{len(produits)} produits")
        
        if not produits:
            self._afficher_liste_vide()
            return
        
        # Grouper par moment
        moments = {"matin": [], "journee": [], "soir": [], "tous": []}
        for i, produit in enumerate(produits):
            moments[produit.moment.value].append((i, produit))
        
        # Afficher chaque section
        for moment, prods in moments.items():
            if prods:
                self._creer_section_moment(moment, prods)
    
    def _afficher_liste_vide(self) -> None:
        """Affiche un message quand la liste est vide."""
        frame_vide = ctk.CTkFrame(
            self.frame_liste,
            fg_color=COULEUR_PANNEAU,
            corner_radius=15
        )
        frame_vide.pack(fill="x", pady=50, padx=50)
        
        ctk.CTkLabel(
            frame_vide,
            text="Aucun produit enregistre\n\nCliquez sur '+ Ajouter un produit'\npour commencer",
            font=ctk.CTkFont(size=14),
            text_color=COULEUR_TEXTE_SECONDAIRE,
            justify="center"
        ).pack(pady=40)
    
    def _creer_section_moment(self, moment: str, produits_avec_index: list) -> None:
        """Crée une section pour un moment de la journée."""
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))
        
        # Header de section
        frame_section = ctk.CTkFrame(self.frame_liste, fg_color="transparent")
        frame_section.pack(fill="x", pady=(15, 5))
        
        ctk.CTkFrame(
            frame_section,
            fg_color=couleur,
            width=6,
            height=20,
            corner_radius=3
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            frame_section,
            text=titre,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=couleur
        ).pack(side="left")
        
        # Produits
        for index, produit in produits_avec_index:
            self._creer_carte_produit(produit, index)
    
    def _creer_carte_produit(self, produit: ProduitDerma, index: int) -> None:
        """Crée une carte pour un produit avec bouton de suppression."""
        couleur = COULEURS_CATEGORIE.get(produit.category.value, "#fff")
        
        frame = ctk.CTkFrame(
            self.frame_liste,
            fg_color=COULEUR_CARTE,
            corner_radius=10
        )
        frame.pack(fill="x", pady=3)
        
        # Indicateur couleur
        ctk.CTkFrame(
            frame,
            fg_color=couleur,
            width=5,
            corner_radius=2
        ).pack(side="left", fill="y")
        
        # Contenu
        frame_content = ctk.CTkFrame(frame, fg_color="transparent")
        frame_content.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        
        # Ligne 1: nom et badges
        frame_top = ctk.CTkFrame(frame_content, fg_color="transparent")
        frame_top.pack(fill="x")
        
        ctk.CTkLabel(
            frame_top,
            text=produit.nom,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame_top,
            text=produit.category.value,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COULEUR_FOND,
            fg_color=couleur,
            corner_radius=4,
            width=75
        ).pack(side="right", padx=5)
        
        if produit.photosensitive:
            ctk.CTkLabel(
                frame_top,
                text="PHOTOSENSIBLE",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COULEUR_DANGER
            ).pack(side="right", padx=5)
        
        # Ligne 2: détails
        details = (
            f"Occlusivite: {produit.occlusivity}/5 | "
            f"Nettoyage: {produit.cleansing_power}/5 | "
            f"{produit.active_tag.value}"
        )
        ctk.CTkLabel(
            frame_content,
            text=details,
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w", pady=(4, 0))
        
        # Bouton supprimer
        ctk.CTkButton(
            frame,
            text="X",
            width=35,
            height=35,
            fg_color=COULEUR_DANGER,
            hover_color="#c73e54",
            command=lambda idx=index: self._supprimer_produit(idx)
        ).pack(side="right", padx=10, pady=5)
    
    def _supprimer_produit(self, index: int) -> None:
        """Supprime un produit après confirmation."""
        if messagebox.askyesno("Confirmer", "Supprimer ce produit ?"):
            self.gestionnaire.supprimer(index)
            self.actualiser_liste()
    
    def _ouvrir_formulaire(self) -> None:
        """Ouvre le formulaire d'ajout de produit."""
        FormulaireProduit(self, self.gestionnaire, self.actualiser_liste)
    
    def _ajouter_avec_ia(self) -> None:
        """Ouvre la fenêtre de recherche IA pour analyser un produit."""
        FenetreRechercheIA(self, self.gestionnaire, self.actualiser_liste)


# =============================================================================
# PAGE HISTORIQUE
# =============================================================================

class PageHistorique(ctk.CTkFrame):
    """
    Page d'affichage de l'historique des analyses.
    
    Affiche les analyses récentes (< 2 semaines) et les archives.
    Chaque analyse peut être dépliée pour voir les détails.
    """
    
    def __init__(self, master, gestionnaire_historique: GestionnaireHistorique, **kwargs):
        super().__init__(master, **kwargs)
        self.gestionnaire = gestionnaire_historique
        self.configure(fg_color="transparent")
        self.onglet_actif = "recentes"  # "recentes" ou "archives"
        self._creer_interface()
    
    def _creer_interface(self) -> None:
        """Construit l'interface de la page."""
        
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            frame_header,
            text="Historique des Analyses",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Statistiques
        stats = self.gestionnaire.statistiques()
        self.label_stats = ctk.CTkLabel(
            frame_header,
            text=f"{stats['nb_total']} analyses",
            font=ctk.CTkFont(size=14),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_stats.pack(side="left", padx=15)
        
        # Onglets
        frame_onglets = ctk.CTkFrame(self, fg_color=COULEUR_PANNEAU, corner_radius=10)
        frame_onglets.pack(fill="x", padx=20, pady=(0, 10))
        
        frame_btns = ctk.CTkFrame(frame_onglets, fg_color="transparent")
        frame_btns.pack(pady=8, padx=10)
        
        self.btn_recentes = ctk.CTkButton(
            frame_btns,
            text=f"📅 Récentes ({stats['nb_recentes']})",
            command=lambda: self._changer_onglet("recentes"),
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            font=ctk.CTkFont(weight="bold"),
            width=150
        )
        self.btn_recentes.pack(side="left", padx=5)
        
        self.btn_archives = ctk.CTkButton(
            frame_btns,
            text=f"📦 Archives ({stats['nb_archives']})",
            command=lambda: self._changer_onglet("archives"),
            fg_color="transparent",
            hover_color=COULEUR_CARTE_HOVER,
            text_color="#fff",
            font=ctk.CTkFont(weight="bold"),
            width=150
        )
        self.btn_archives.pack(side="left", padx=5)
        
        # Contenu scrollable
        self.frame_contenu = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_contenu.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Afficher les récentes par défaut
        self._afficher_recentes()
    
    def _changer_onglet(self, onglet: str) -> None:
        """Change l'onglet actif."""
        self.onglet_actif = onglet
        
        # Mettre à jour les boutons
        if onglet == "recentes":
            self.btn_recentes.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
            self.btn_archives.configure(fg_color="transparent", text_color="#fff")
            self._afficher_recentes()
        else:
            self.btn_archives.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
            self.btn_recentes.configure(fg_color="transparent", text_color="#fff")
            self._afficher_archives()
    
    def _afficher_recentes(self) -> None:
        """Affiche les analyses récentes."""
        self._nettoyer_contenu()
        analyses = self.gestionnaire.obtenir_recentes()
        
        if not analyses:
            self._afficher_vide("Aucune analyse récente")
            return
        
        # Grouper par date
        par_date = {}
        for analyse in analyses:
            if analyse.date not in par_date:
                par_date[analyse.date] = []
            par_date[analyse.date].append(analyse)
        
        for date, liste_analyses in par_date.items():
            self._creer_section_date(date, liste_analyses)
    
    def _afficher_archives(self) -> None:
        """Affiche les analyses archivées."""
        self._nettoyer_contenu()
        analyses = self.gestionnaire.obtenir_archives()
        
        if not analyses:
            self._afficher_vide("Aucune archive disponible")
            return
        
        # Grouper par date
        par_date = {}
        for analyse in analyses:
            if analyse.date not in par_date:
                par_date[analyse.date] = []
            par_date[analyse.date].append(analyse)
        
        for date, liste_analyses in par_date.items():
            self._creer_section_date(date, liste_analyses)
    
    def _nettoyer_contenu(self) -> None:
        """Nettoie le contenu de la frame."""
        for widget in self.frame_contenu.winfo_children():
            widget.destroy()
    
    def _afficher_vide(self, message: str) -> None:
        """Affiche un message quand il n'y a pas de données."""
        frame_vide = ctk.CTkFrame(
            self.frame_contenu,
            fg_color=COULEUR_PANNEAU,
            corner_radius=15
        )
        frame_vide.pack(fill="x", pady=50, padx=50)
        
        ctk.CTkLabel(
            frame_vide,
            text=f"📭\n\n{message}",
            font=ctk.CTkFont(size=16),
            text_color=COULEUR_TEXTE_SECONDAIRE,
            justify="center"
        ).pack(pady=40)
    
    def _creer_section_date(self, date: str, analyses: list) -> None:
        """Crée une section pour une date donnée."""
        # Header de date
        frame_date = ctk.CTkFrame(self.frame_contenu, fg_color="transparent")
        frame_date.pack(fill="x", pady=(15, 5))
        
        # Formater la date
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date)
            date_formatee = dt.strftime("%A %d %B %Y").capitalize()
        except:
            date_formatee = date
        
        ctk.CTkLabel(
            frame_date,
            text=f"📅 {date_formatee}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COULEUR_ACCENT
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame_date,
            text=f"{len(analyses)} analyse(s)",
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(side="right")
        
        # Cartes d'analyses
        for analyse in analyses:
            self._creer_carte_analyse(analyse)
    
    def _creer_carte_analyse(self, analyse: ResultatAnalyseHistorique) -> None:
        """Crée une carte pour une analyse."""
        frame = ctk.CTkFrame(
            self.frame_contenu,
            fg_color=COULEUR_CARTE,
            corner_radius=12
        )
        frame.pack(fill="x", pady=4)
        
        # Header avec l'heure et les conditions
        frame_header = ctk.CTkFrame(frame, fg_color="transparent")
        frame_header.pack(fill="x", padx=15, pady=10)
        
        # Heure
        ctk.CTkLabel(
            frame_header,
            text=f"🕐 {analyse.heure}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")
        
        # Ville
        ctk.CTkLabel(
            frame_header,
            text=f"📍 {analyse.conditions.ville}, {analyse.conditions.pays}",
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(side="left", padx=15)
        
        # Conditions environnementales (badges)
        frame_badges = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_badges.pack(side="right")
        
        # UV
        couleur_uv = self._couleur_niveau(analyse.conditions.niveau_uv)
        ctk.CTkLabel(
            frame_badges,
            text=f"UV {analyse.conditions.indice_uv:.1f}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COULEUR_FOND,
            fg_color=couleur_uv,
            corner_radius=4,
            width=55
        ).pack(side="left", padx=2)
        
        # Humidité
        ctk.CTkLabel(
            frame_badges,
            text=f"💧 {analyse.conditions.humidite:.0f}%",
            font=ctk.CTkFont(size=10),
            text_color="#fff"
        ).pack(side="left", padx=5)
        
        # Température
        ctk.CTkLabel(
            frame_badges,
            text=f"🌡️ {analyse.conditions.temperature:.0f}°C",
            font=ctk.CTkFont(size=10),
            text_color="#fff"
        ).pack(side="left", padx=5)
        
        # Alertes si présentes
        if analyse.alertes:
            frame_alertes = ctk.CTkFrame(frame, fg_color="#2a1a2a", corner_radius=6)
            frame_alertes.pack(fill="x", padx=15, pady=(0, 5))
            
            for alerte in analyse.alertes[:2]:  # Max 2 alertes affichées
                ctk.CTkLabel(
                    frame_alertes,
                    text=f"⚠️ {alerte}",
                    font=ctk.CTkFont(size=10),
                    text_color="#f9ed69"
                ).pack(anchor="w", padx=8, pady=2)
        
        # Résumé des produits par moment
        frame_resume = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resume.pack(fill="x", padx=15, pady=(0, 10))
        
        # Matin
        nb_matin = len(analyse.produits_matin)
        self._creer_badge_moment(frame_resume, "matin", nb_matin)
        
        # Journée
        nb_journee = len(analyse.produits_journee)
        self._creer_badge_moment(frame_resume, "journee", nb_journee)
        
        # Soir
        nb_soir = len(analyse.produits_soir)
        self._creer_badge_moment(frame_resume, "soir", nb_soir)
    
    def _creer_badge_moment(self, parent, moment: str, nb_produits: int) -> None:
        """Crée un badge pour un moment de la journée."""
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))
        
        frame = ctk.CTkFrame(parent, fg_color=COULEUR_CARTE_HOVER, corner_radius=6)
        frame.pack(side="left", padx=3)
        
        ctk.CTkFrame(
            frame,
            fg_color=couleur,
            width=4,
            corner_radius=2
        ).pack(side="left", fill="y", padx=(5, 0), pady=5)
        
        ctk.CTkLabel(
            frame,
            text=f"{titre}: {nb_produits}",
            font=ctk.CTkFont(size=10),
            text_color="#fff"
        ).pack(side="left", padx=(5, 10), pady=5)
    
    def _couleur_niveau(self, niveau: str) -> str:
        """Retourne la couleur pour un niveau."""
        couleurs = {
            "Nul": "#6c757d",
            "Faible": COULEUR_ACCENT,
            "Modéré": "#f9ed69",
            "Modere": "#f9ed69",
            "Élevé": "#f38181",
            "Eleve": "#f38181",
            "Très élevé": COULEUR_DANGER,
            "Tres eleve": COULEUR_DANGER,
            "Extrême": "#aa2ee6",
            "Extreme": "#aa2ee6",
            "Normal": COULEUR_ACCENT,
            "Sec": "#f9ed69",
            "Très sec": "#f38181",
            "Humide": "#00b4d8",
            "Très humide": "#9b59b6",
            "Bon": COULEUR_ACCENT,
            "Mauvais": COULEUR_DANGER
        }
        return couleurs.get(niveau, "#6c757d")
    
    def actualiser(self) -> None:
        """Actualise l'affichage de l'historique."""
        stats = self.gestionnaire.statistiques()
        self.label_stats.configure(text=f"{stats['nb_total']} analyses")
        self.btn_recentes.configure(text=f"📅 Récentes ({stats['nb_recentes']})")
        self.btn_archives.configure(text=f"📦 Archives ({stats['nb_archives']})")
        
        if self.onglet_actif == "recentes":
            self._afficher_recentes()
        else:
            self._afficher_archives()


# =============================================================================
# PAGE PROFIL UTILISATEUR
# =============================================================================

class PageProfil(ctk.CTkFrame):
    """
    Page de gestion du profil utilisateur.
    
    Permet de configurer :
    - Type de peau (permanent)
    - Problèmes de peau / maladies (permanent)
    - Notes personnelles permanentes
    - État quotidien (stress, état du jour)
    """
    
    def __init__(self, master, gestionnaire_profil: GestionnaireProfil, **kwargs):
        super().__init__(master, **kwargs)
        self.gestionnaire = gestionnaire_profil
        self.configure(fg_color="transparent")
        self._creer_interface()
    
    def _creer_interface(self) -> None:
        """Construit l'interface de la page."""
        
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            frame_header,
            text="👤 Mon Profil",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Scrollable content
        self.frame_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # ===== SECTION TYPE DE PEAU =====
        self._creer_section_type_peau()
        
        # ===== SECTION PROBLÈMES DE PEAU =====
        self._creer_section_problemes()
        
        # ===== SECTION NOTES PERMANENTES =====
        self._creer_section_notes()
        
        # ===== SECTION ÉTAT QUOTIDIEN =====
        self._creer_section_quotidien()
    
    def _creer_section_type_peau(self) -> None:
        """Crée la section type de peau."""
        frame = ctk.CTkFrame(self.frame_scroll, fg_color=COULEUR_PANNEAU, corner_radius=12)
        frame.pack(fill="x", pady=8)
        
        # Header
        ctk.CTkLabel(
            frame,
            text="🧬 Type de peau",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(
            frame,
            text="Sélectionnez votre type de peau (sauvegardé)",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w", padx=15)
        
        # Options
        frame_options = ctk.CTkFrame(frame, fg_color="transparent")
        frame_options.pack(fill="x", padx=15, pady=10)
        
        types = [
            ("normale", "Normale"), 
            ("seche", "Sèche"),
            ("grasse", "Grasse"),
            ("mixte", "Mixte"),
            ("sensible", "Sensible")
        ]
        
        self.var_type_peau = ctk.StringVar(value=self.gestionnaire.profil.type_peau.value)
        
        for valeur, label in types:
            btn = ctk.CTkRadioButton(
                frame_options,
                text=label,
                variable=self.var_type_peau,
                value=valeur,
                command=self._on_type_peau_change,
                fg_color=COULEUR_ACCENT,
                hover_color=COULEUR_ACCENT_HOVER
            )
            btn.pack(side="left", padx=10)
    
    def _on_type_peau_change(self) -> None:
        """Callback quand le type de peau change."""
        type_peau = TypePeau.from_str(self.var_type_peau.get())
        self.gestionnaire.modifier_type_peau(type_peau)
    
    def _creer_section_problemes(self) -> None:
        """Crée la section problèmes de peau."""
        frame = ctk.CTkFrame(self.frame_scroll, fg_color=COULEUR_PANNEAU, corner_radius=12)
        frame.pack(fill="x", pady=8)
        
        # Header
        ctk.CTkLabel(
            frame,
            text="⚠️ Problèmes de peau",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(
            frame,
            text="Sélectionnez vos problèmes de peau ou maladies (sauvegardés)",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w", padx=15)
        
        # Grille de checkboxes
        frame_grid = ctk.CTkFrame(frame, fg_color="transparent")
        frame_grid.pack(fill="x", padx=15, pady=10)
        
        problemes = [
            ("acne", "Acné"),
            ("eczema", "Eczéma"),
            ("rosacee", "Rosacée"),
            ("psoriasis", "Psoriasis"),
            ("hyperpigmentation", "Hyperpigmentation"),
            ("rides", "Rides / Ridules"),
            ("pores_dilates", "Pores dilatés"),
            ("deshydratation", "Déshydratation"),
            ("taches", "Taches pigmentaires"),
            ("rougeurs", "Rougeurs")
        ]
        
        self.vars_problemes = {}
        
        for i, (valeur, label) in enumerate(problemes):
            var = ctk.BooleanVar(value=valeur in self.gestionnaire.profil.problemes)
            self.vars_problemes[valeur] = var
            
            cb = ctk.CTkCheckBox(
                frame_grid,
                text=label,
                variable=var,
                command=lambda v=valeur: self._on_probleme_change(v),
                fg_color=COULEUR_ACCENT,
                hover_color=COULEUR_ACCENT_HOVER,
                width=150
            )
            row, col = divmod(i, 3)
            cb.grid(row=row, column=col, padx=5, pady=5, sticky="w")
    
    def _on_probleme_change(self, probleme: str) -> None:
        """Callback quand un problème est coché/décoché."""
        if self.vars_problemes[probleme].get():
            self.gestionnaire.ajouter_probleme(probleme)
        else:
            self.gestionnaire.retirer_probleme(probleme)
    
    def _creer_section_notes(self) -> None:
        """Crée la section notes permanentes."""
        frame = ctk.CTkFrame(self.frame_scroll, fg_color=COULEUR_PANNEAU, corner_radius=12)
        frame.pack(fill="x", pady=8)
        
        # Header
        ctk.CTkLabel(
            frame,
            text="📝 Notes personnelles",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(
            frame,
            text="Informations permanentes (allergies, préférences, etc.)",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w", padx=15)
        
        # Zone de texte
        self.txt_notes = ctk.CTkTextbox(
            frame,
            height=80,
            fg_color=COULEUR_CARTE,
            border_width=1,
            border_color=COULEUR_BORDURE
        )
        self.txt_notes.pack(fill="x", padx=15, pady=10)
        self.txt_notes.insert("1.0", self.gestionnaire.profil.notes_permanentes)
        
        # Bouton sauvegarder
        ctk.CTkButton(
            frame,
            text="💾 Sauvegarder les notes",
            command=self._sauvegarder_notes,
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            width=180
        ).pack(padx=15, pady=(0, 12))
    
    def _sauvegarder_notes(self) -> None:
        """Sauvegarde les notes permanentes."""
        notes = self.txt_notes.get("1.0", "end-1c")
        self.gestionnaire.modifier_notes(notes)
        messagebox.showinfo("Sauvegardé", "Vos notes ont été sauvegardées !")
    
    def _creer_section_quotidien(self) -> None:
        """Crée la section état quotidien."""
        frame = ctk.CTkFrame(self.frame_scroll, fg_color=COULEUR_PANNEAU, corner_radius=12)
        frame.pack(fill="x", pady=8)
        
        # Header
        ctk.CTkLabel(
            frame,
            text="📅 État du jour",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(
            frame,
            text="Ces informations sont utilisées pour l'analyse mais non sauvegardées",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Niveau de stress
        frame_stress = ctk.CTkFrame(frame, fg_color="transparent")
        frame_stress.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            frame_stress,
            text="Niveau de stress :",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")
        
        self.label_stress = ctk.CTkLabel(
            frame_stress,
            text=f"{self.gestionnaire.etat_quotidien.niveau_stress}/10",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COULEUR_ACCENT
        )
        self.label_stress.pack(side="right", padx=10)
        
        self.slider_stress = ctk.CTkSlider(
            frame,
            from_=1,
            to=10,
            number_of_steps=9,
            command=self._on_stress_change,
            fg_color=COULEUR_CARTE,
            progress_color=COULEUR_ACCENT,
            button_color=COULEUR_ACCENT,
            button_hover_color=COULEUR_ACCENT_HOVER
        )
        self.slider_stress.pack(fill="x", padx=15, pady=5)
        self.slider_stress.set(self.gestionnaire.etat_quotidien.niveau_stress)
        
        # État de la peau du jour
        ctk.CTkLabel(
            frame,
            text="État de la peau aujourd'hui (optionnel) :",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.entry_etat_jour = ctk.CTkEntry(
            frame,
            placeholder_text="Ex: Un peu sèche, quelques rougeurs...",
            fg_color=COULEUR_CARTE,
            border_color=COULEUR_BORDURE,
            height=35
        )
        self.entry_etat_jour.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_etat_jour.bind("<KeyRelease>", self._on_etat_jour_change)
    
    def _on_stress_change(self, valeur: float) -> None:
        """Callback quand le niveau de stress change."""
        niveau = int(valeur)
        self.gestionnaire.definir_stress(niveau)
        self.label_stress.configure(text=f"{niveau}/10")
        
        # Couleur selon le niveau
        if niveau <= 3:
            couleur = COULEUR_ACCENT
        elif niveau <= 6:
            couleur = "#f9ed69"
        else:
            couleur = COULEUR_DANGER
        self.label_stress.configure(text_color=couleur)
    
    def _on_etat_jour_change(self, event=None) -> None:
        """Callback quand l'état du jour change."""
        etat = self.entry_etat_jour.get()
        self.gestionnaire.definir_etat_jour(etat)
    
    def actualiser(self) -> None:
        """Actualise l'affichage (recharge les données)."""
        # Type de peau
        self.var_type_peau.set(self.gestionnaire.profil.type_peau.value)
        
        # Problèmes
        for valeur, var in self.vars_problemes.items():
            var.set(valeur in self.gestionnaire.profil.problemes)
        
        # Notes
        self.txt_notes.delete("1.0", "end")
        self.txt_notes.insert("1.0", self.gestionnaire.profil.notes_permanentes)


# =============================================================================
# FORMULAIRE D'AJOUT DE PRODUIT
# =============================================================================

class FormulaireProduit(ctk.CTkToplevel):
    """
    Fenêtre modale pour ajouter un nouveau produit.
    
    Formulaire avec tous les champs nécessaires :
    nom, catégorie, moment, photosensibilité, occlusivité,
    pouvoir nettoyant, action principale.
    
    Peut être pré-rempli avec des valeurs initiales (ex: depuis l'IA).
    """
    
    def __init__(
        self,
        parent,
        gestionnaire: GestionnaireProduits,
        callback,
        valeurs_initiales: dict = None
    ):
        """
        Initialise le formulaire.
        
        Args:
            parent: Widget parent
            gestionnaire: Gestionnaire de produits
            callback: Fonction à appeler après ajout
            valeurs_initiales: Dict avec les valeurs pré-remplies (optionnel)
                {nom, category, moment, photosensitive, occlusivity, cleansing_power, active_tag}
        """
        super().__init__(parent)
        self.gestionnaire = gestionnaire
        self.callback = callback
        self.valeurs = valeurs_initiales or {}
        
        # Titre différent si pré-rempli par IA
        titre = "Nouveau Produit (IA)" if valeurs_initiales else "Nouveau Produit"
        
        self.title("Ajouter un produit")
        self.geometry("420x650")
        self.configure(fg_color=COULEUR_FOND)
        self.transient(parent)
        self.grab_set()
        
        self._creer_widgets(titre)
    
    def _creer_widgets(self, titre: str) -> None:
        """Construit le formulaire."""
        
        # Titre avec indication IA si applicable
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            frame_titre,
            text=titre,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack()
        
        if self.valeurs:
            ctk.CTkLabel(
                frame_titre,
                text="Vérifie les informations avant d'ajouter",
                font=ctk.CTkFont(size=11),
                text_color="#9b59b6"
            ).pack()
        
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=25)
        
        # Nom
        ctk.CTkLabel(frame, text="Nom", anchor="w").pack(fill="x", pady=(10, 2))
        self.entry_nom = ctk.CTkEntry(
            frame,
            placeholder_text="Ex: Mon Serum Niacinamide",
            height=36
        )
        self.entry_nom.pack(fill="x")
        if self.valeurs.get("nom"):
            self.entry_nom.insert(0, self.valeurs["nom"])
        
        # Catégorie
        ctk.CTkLabel(frame, text="Categorie", anchor="w").pack(fill="x", pady=(12, 2))
        self.combo_cat = ctk.CTkComboBox(
            frame,
            values=["cleanser", "treatment", "moisturizer", "protection"],
            height=36
        )
        self.combo_cat.pack(fill="x")
        self.combo_cat.set(self.valeurs.get("category", "moisturizer"))
        
        # Moment d'utilisation
        ctk.CTkLabel(frame, text="Moment d'utilisation", anchor="w").pack(fill="x", pady=(12, 2))
        self.combo_moment = ctk.CTkComboBox(
            frame,
            values=["matin", "journee", "soir", "tous"],
            height=36
        )
        self.combo_moment.pack(fill="x")
        self.combo_moment.set(self.valeurs.get("moment", "tous"))
        
        # Photosensible
        ctk.CTkLabel(
            frame,
            text="Photosensible (reagit aux UV)",
            anchor="w"
        ).pack(fill="x", pady=(12, 2))
        
        self.var_photo = ctk.BooleanVar(value=self.valeurs.get("photosensitive", False))
        frame_radio = ctk.CTkFrame(frame, fg_color="transparent")
        frame_radio.pack(fill="x")
        
        ctk.CTkRadioButton(
            frame_radio,
            text="Non",
            variable=self.var_photo,
            value=False,
            fg_color=COULEUR_ACCENT
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkRadioButton(
            frame_radio,
            text="Oui (BHA, Retinol...)",
            variable=self.var_photo,
            value=True,
            fg_color=COULEUR_DANGER
        ).pack(side="left")
        
        # Occlusivité
        ctk.CTkLabel(
            frame,
            text="Occlusivite (1=leger, 5=riche)",
            anchor="w"
        ).pack(fill="x", pady=(12, 2))
        
        self.slider_occlu = ctk.CTkSlider(
            frame,
            from_=1,
            to=5,
            number_of_steps=4,
            fg_color=COULEUR_CARTE,
            progress_color=COULEUR_ACCENT
        )
        self.slider_occlu.pack(fill="x")
        self.slider_occlu.set(self.valeurs.get("occlusivity", 3))
        
        self.lbl_occlu = ctk.CTkLabel(
            frame,
            text=str(self.valeurs.get("occlusivity", 3)),
            font=ctk.CTkFont(weight="bold")
        )
        self.lbl_occlu.pack()
        self.slider_occlu.configure(
            command=lambda v: self.lbl_occlu.configure(text=str(int(v)))
        )
        
        # Pouvoir nettoyant
        ctk.CTkLabel(
            frame,
            text="Pouvoir nettoyant (1=doux, 5=fort)",
            anchor="w"
        ).pack(fill="x", pady=(12, 2))
        
        self.slider_clean = ctk.CTkSlider(
            frame,
            from_=1,
            to=5,
            number_of_steps=4,
            fg_color=COULEUR_CARTE,
            progress_color="#00b4d8"
        )
        self.slider_clean.pack(fill="x")
        self.slider_clean.set(self.valeurs.get("cleansing_power", 3))
        
        self.lbl_clean = ctk.CTkLabel(
            frame,
            text=str(self.valeurs.get("cleansing_power", 3)),
            font=ctk.CTkFont(weight="bold")
        )
        self.lbl_clean.pack()
        self.slider_clean.configure(
            command=lambda v: self.lbl_clean.configure(text=str(int(v)))
        )
        
        # Action principale
        ctk.CTkLabel(frame, text="Action principale", anchor="w").pack(fill="x", pady=(12, 2))
        self.combo_tag = ctk.CTkComboBox(
            frame,
            values=["hydration", "acne", "repair"],
            height=36
        )
        self.combo_tag.pack(fill="x")
        self.combo_tag.set(self.valeurs.get("active_tag", "hydration"))
        
        # Boutons
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkButton(
            frame_btns,
            text="Annuler",
            fg_color=COULEUR_DANGER,
            hover_color="#c73e54",
            command=self.destroy
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            frame_btns,
            text="Ajouter",
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            font=ctk.CTkFont(weight="bold"),
            command=self._valider
        ).pack(side="right", expand=True, padx=5)
    
    def _valider(self) -> None:
        """Valide et ajoute le produit."""
        nom = self.entry_nom.get().strip()
        if not nom:
            messagebox.showwarning("Attention", "Entrez un nom")
            return
        
        try:
            produit = ProduitDerma(
                nom=nom,
                category=Categorie(self.combo_cat.get()),
                moment=MomentUtilisation(self.combo_moment.get()),
                photosensitive=self.var_photo.get(),
                occlusivity=int(self.slider_occlu.get()),
                cleansing_power=int(self.slider_clean.get()),
                active_tag=ActiveTag(self.combo_tag.get())
            )
            self.gestionnaire.ajouter(produit)
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


# =============================================================================
# FENÊTRE DE RECHERCHE IA
# =============================================================================

class FenetreRechercheIA(ctk.CTkToplevel):
    """
    Fenêtre pour rechercher et analyser un produit avec l'IA Gemini.
    
    L'utilisateur entre le nom du produit, l'IA l'analyse et retourne
    les caractéristiques qui pré-remplissent le formulaire d'ajout.
    """
    
    def __init__(self, parent, gestionnaire: GestionnaireProduits, callback):
        super().__init__(parent)
        self.parent_page = parent
        self.gestionnaire = gestionnaire
        self.callback = callback
        self.client_gemini = ClientGemini()
        
        self.title("Ajouter avec l'IA")
        self.geometry("450x320")
        self.configure(fg_color=COULEUR_FOND)
        self.transient(parent)
        self.grab_set()
        
        self._creer_widgets()
    
    def _creer_widgets(self) -> None:
        """Construit l'interface."""
        
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(
            frame_header,
            text="🤖 Analyse par IA",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            frame_header,
            text="L'IA va analyser le produit et remplir automatiquement\nles caractéristiques. Tu pourras les modifier ensuite.",
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_TEXTE_SECONDAIRE,
            justify="center"
        ).pack(pady=(8, 0))
        
        # Zone de saisie
        frame_input = ctk.CTkFrame(self, fg_color=COULEUR_PANNEAU, corner_radius=12)
        frame_input.pack(fill="x", padx=25, pady=(0, 15))
        
        ctk.CTkLabel(
            frame_input,
            text="Nom du produit",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(15, 5))
        
        self.entry_produit = ctk.CTkEntry(
            frame_input,
            placeholder_text="Ex: CeraVe Crème Hydratante, Paula's Choice BHA...",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.entry_produit.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_produit.bind("<Return>", lambda e: self._analyser())
        
        # Status
        self.label_status = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_status.pack(pady=(0, 10))
        
        # Boutons
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkButton(
            frame_btns,
            text="Annuler",
            fg_color=COULEUR_CARTE,
            hover_color=COULEUR_CARTE_HOVER,
            width=120,
            command=self.destroy
        ).pack(side="left")
        
        self.btn_analyser = ctk.CTkButton(
            frame_btns,
            text="Analyser avec l'IA",
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            text_color="#fff",
            font=ctk.CTkFont(weight="bold"),
            width=180,
            command=self._analyser
        )
        self.btn_analyser.pack(side="right")
    
    def _analyser(self) -> None:
        """Lance l'analyse du produit par l'IA."""
        nom_produit = self.entry_produit.get().strip()
        
        if not nom_produit:
            self.label_status.configure(
                text="Entre le nom d'un produit",
                text_color=COULEUR_DANGER
            )
            return
        
        # État de chargement
        self.btn_analyser.configure(text="Analyse en cours...", state="disabled")
        self.label_status.configure(
            text="Connexion à Gemini...",
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.update()
        
        try:
            # Appel à l'IA
            resultat = self.client_gemini.analyser_produit(nom_produit)
            
            if resultat.succes:
                # Fermer cette fenêtre
                self.destroy()
                
                # Ouvrir le formulaire pré-rempli
                valeurs = {
                    "nom": resultat.nom,
                    "category": resultat.category,
                    "moment": resultat.moment,
                    "photosensitive": resultat.photosensitive,
                    "occlusivity": resultat.occlusivity,
                    "cleansing_power": resultat.cleansing_power,
                    "active_tag": resultat.active_tag
                }
                
                FormulaireProduit(
                    self.parent_page,
                    self.gestionnaire,
                    self.callback,
                    valeurs_initiales=valeurs
                )
            else:
                self.label_status.configure(
                    text=f"Erreur: {resultat.erreur[:100]}",
                    text_color=COULEUR_DANGER
                )
                self.btn_analyser.configure(text="Réessayer", state="normal")
                
        except Exception as e:
            self.label_status.configure(
                text=f"Erreur: {str(e)[:100]}",
                text_color=COULEUR_DANGER
            )
            self.btn_analyser.configure(text="Réessayer", state="normal")


# =============================================================================
# FENÊTRE D'ANALYSE IA PERSONNALISÉE
# =============================================================================

class FenetreAnalyseIA(ctk.CTkToplevel):
    """
    Fenêtre pour lancer une analyse IA personnalisée.
    
    Permet d'entrer des instructions personnalisées qui seront
    envoyées à l'IA avec le profil et les conditions environnementales.
    """
    
    def __init__(self, parent, app, callback):
        """
        Initialise la fenêtre d'analyse IA.
        
        Args:
            parent: Widget parent
            app: Application principale (pour accéder aux gestionnaires)
            callback: Fonction à appeler avec le résultat
        """
        super().__init__(parent)
        self.app = app
        self.callback = callback
        
        self.title("🤖 Analyse IA personnalisée")
        self.geometry("550x400")
        self.configure(fg_color=COULEUR_FOND)
        self.transient(parent)
        self.grab_set()
        
        self._creer_widgets()
    
    def _creer_widgets(self) -> None:
        """Construit l'interface."""
        
        # Titre
        ctk.CTkLabel(
            self,
            text="🤖 Analyse IA personnalisée",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Description
        ctk.CTkLabel(
            self,
            text="L'IA analysera vos produits en tenant compte de :",
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(pady=(0, 5))
        
        # Liste des éléments pris en compte
        infos = ctk.CTkFrame(self, fg_color=COULEUR_PANNEAU, corner_radius=10)
        infos.pack(fill="x", padx=30, pady=10)
        
        elements = [
            "✓ Votre profil (type de peau, problèmes)",
            "✓ Conditions météo actuelles (UV, humidité, pollution)",
            "✓ Votre niveau de stress du jour",
            "✓ Vos produits enregistrés"
        ]
        for elem in elements:
            ctk.CTkLabel(
                infos,
                text=elem,
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(anchor="w", padx=15, pady=2)
        
        # Zone d'instructions personnalisées
        ctk.CTkLabel(
            self,
            text="Instructions personnalisées (optionnel) :",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=30, pady=(15, 5))
        
        self.txt_instructions = ctk.CTkTextbox(
            self,
            height=100,
            fg_color=COULEUR_CARTE,
            border_width=1,
            border_color=COULEUR_BORDURE
        )
        self.txt_instructions.pack(fill="x", padx=30, pady=5)
        self.txt_instructions.insert(
            "1.0",
            "Ex: J'ai un rendez-vous important ce soir, ma peau est un peu irritée..."
        )
        self.txt_instructions.bind("<FocusIn>", self._vider_placeholder)
        
        # Boutons
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            frame_btns,
            text="Annuler",
            command=self.destroy,
            fg_color=COULEUR_CARTE,
            hover_color=COULEUR_CARTE_HOVER,
            width=120
        ).pack(side="left")
        
        self.btn_lancer = ctk.CTkButton(
            frame_btns,
            text="🚀 Lancer l'analyse",
            command=self._lancer_analyse,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=180
        )
        self.btn_lancer.pack(side="right")
        
        # Status
        self.label_status = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_status.pack(pady=(0, 10))
    
    def _vider_placeholder(self, event=None) -> None:
        """Vide le placeholder au focus."""
        contenu = self.txt_instructions.get("1.0", "end-1c")
        if contenu.startswith("Ex:"):
            self.txt_instructions.delete("1.0", "end")
    
    def _lancer_analyse(self) -> None:
        """Lance l'analyse IA."""
        self.btn_lancer.configure(state="disabled", text="Analyse en cours...")
        self.label_status.configure(
            text="⏳ Consultation de l'IA en cours...",
            text_color=COULEUR_ACCENT
        )
        self.update()
        
        # Récupérer les instructions
        instructions = self.txt_instructions.get("1.0", "end-1c")
        if instructions.startswith("Ex:"):
            instructions = ""
        
        # Appeler le callback avec les instructions
        self.callback(instructions)
        self.destroy()


# =============================================================================
# FENÊTRE DE SÉLECTION DE VILLE
# =============================================================================

class FenetreSelectionVille(ctk.CTkToplevel):
    """
    Fenêtre modale pour rechercher et sélectionner une ville.
    
    Fonctionnalités :
    - Recherche de villes via API Open-Meteo
    - Gestion des villes favorites (étoile jaune)
    - Affichage des favoris avec données météo en cache
    - Sauvegarde automatique dans config.json
    """
    
    def __init__(self, parent, client_meteo: ClientOpenMeteo, gestionnaire_config: GestionnaireConfig, callback):
        super().__init__(parent)
        self.client_meteo = client_meteo
        self.gestionnaire_config = gestionnaire_config
        self.callback = callback
        self.resultats: list[Localisation] = []
        self.onglet_actif = "recherche"  # "recherche" ou "favoris"
        
        self.title("Choisir une ville")
        self.geometry("450x520")
        self.configure(fg_color=COULEUR_FOND)
        self.transient(parent)
        self.grab_set()
        
        self._creer_widgets()
    
    def _creer_widgets(self) -> None:
        """Construit l'interface."""
        
        # Header
        ctk.CTkLabel(
            self,
            text="Gerer les villes",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Onglets
        frame_onglets = ctk.CTkFrame(self, fg_color="transparent")
        frame_onglets.pack(fill="x", padx=20, pady=(0, 10))
        
        self.btn_onglet_recherche = ctk.CTkButton(
            frame_onglets,
            text="Rechercher",
            command=lambda: self._changer_onglet("recherche"),
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            width=120
        )
        self.btn_onglet_recherche.pack(side="left", padx=(0, 5))
        
        self.btn_onglet_favoris = ctk.CTkButton(
            frame_onglets,
            text="⭐ Favoris",
            command=lambda: self._changer_onglet("favoris"),
            fg_color=COULEUR_CARTE,
            hover_color=COULEUR_CARTE_HOVER,
            width=120
        )
        self.btn_onglet_favoris.pack(side="left")
        
        # Ville actuelle
        frame_actuel = ctk.CTkFrame(self, fg_color=COULEUR_CARTE, corner_radius=10)
        frame_actuel.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            frame_actuel,
            text="Ville actuelle:",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(side="left", padx=10, pady=8)
        
        self.ville_actuelle = self.gestionnaire_config.obtenir_ville_actuelle()
        ctk.CTkLabel(
            frame_actuel,
            text=str(self.ville_actuelle),
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=5, pady=8)
        
        # Bouton étoile pour ajouter aux favoris
        est_favori = self.gestionnaire_config.est_favorite(
            self.ville_actuelle.nom, self.ville_actuelle.pays
        )
        self.btn_favori_actuel = ctk.CTkButton(
            frame_actuel,
            text="⭐" if est_favori else "☆",
            width=35,
            height=28,
            fg_color="#f1c40f" if est_favori else COULEUR_CARTE_HOVER,
            hover_color="#d4ac0d" if est_favori else "#f1c40f",
            text_color=COULEUR_FOND if est_favori else "#f1c40f",
            font=ctk.CTkFont(size=14),
            command=self._toggle_favori_ville_actuelle
        )
        self.btn_favori_actuel.pack(side="right", padx=10, pady=5)
        
        # Container pour les onglets
        self.frame_contenu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_contenu.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Créer les deux onglets
        self._creer_onglet_recherche()
        self._creer_onglet_favoris()
        
        # Afficher l'onglet par défaut
        self._changer_onglet("recherche")
    
    def _creer_onglet_recherche(self) -> None:
        """Crée le contenu de l'onglet recherche."""
        self.frame_recherche = ctk.CTkFrame(self.frame_contenu, fg_color="transparent")
        
        # Barre de recherche
        frame_input = ctk.CTkFrame(self.frame_recherche, fg_color="transparent")
        frame_input.pack(fill="x", pady=(0, 10))
        
        self.entry_recherche = ctk.CTkEntry(
            frame_input,
            placeholder_text="Ex: Lyon, Marseille, Bordeaux...",
            height=40
        )
        self.entry_recherche.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_recherche.bind("<Return>", lambda e: self._rechercher())
        
        self.btn_recherche = ctk.CTkButton(
            frame_input,
            text="Rechercher",
            command=self._rechercher,
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            width=100,
            height=40
        )
        self.btn_recherche.pack(side="right")
        
        # Label
        ctk.CTkLabel(
            self.frame_recherche,
            text="Resultats",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w")
        
        # Liste des résultats
        self.frame_resultats = ctk.CTkScrollableFrame(
            self.frame_recherche,
            fg_color=COULEUR_PANNEAU,
            corner_radius=10
        )
        self.frame_resultats.pack(fill="both", expand=True, pady=(5, 0))
        
        ctk.CTkLabel(
            self.frame_resultats,
            text="Entrez le nom d'une ville\net appuyez sur Rechercher",
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(pady=40)
    
    def _creer_onglet_favoris(self) -> None:
        """Crée le contenu de l'onglet favoris."""
        self.frame_favoris = ctk.CTkFrame(self.frame_contenu, fg_color="transparent")
        
        # Label
        ctk.CTkLabel(
            self.frame_favoris,
            text="Villes favorites",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COULEUR_TEXTE_SECONDAIRE
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            self.frame_favoris,
            text="Donnees meteo en cache - pas de connexion requise",
            font=ctk.CTkFont(size=10),
            text_color="#9b59b6"
        ).pack(anchor="w", pady=(0, 5))
        
        # Liste des favoris
        self.frame_liste_favoris = ctk.CTkScrollableFrame(
            self.frame_favoris,
            fg_color=COULEUR_PANNEAU,
            corner_radius=10
        )
        self.frame_liste_favoris.pack(fill="both", expand=True, pady=(5, 0))
    
    def _changer_onglet(self, onglet: str) -> None:
        """Change l'onglet actif."""
        self.onglet_actif = onglet
        
        # Masquer tous les onglets
        self.frame_recherche.pack_forget()
        self.frame_favoris.pack_forget()
        
        # Reset des boutons
        self.btn_onglet_recherche.configure(fg_color=COULEUR_CARTE, text_color="#fff")
        self.btn_onglet_favoris.configure(fg_color=COULEUR_CARTE, text_color="#fff")
        
        if onglet == "recherche":
            self.frame_recherche.pack(fill="both", expand=True)
            self.btn_onglet_recherche.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
        else:
            self.frame_favoris.pack(fill="both", expand=True)
            self.btn_onglet_favoris.configure(fg_color="#f1c40f", text_color=COULEUR_FOND)
            self._actualiser_favoris()
    
    def _actualiser_favoris(self) -> None:
        """Actualise la liste des favoris."""
        for widget in self.frame_liste_favoris.winfo_children():
            widget.destroy()
        
        favoris = self.gestionnaire_config.obtenir_favorites()
        
        if not favoris:
            ctk.CTkLabel(
                self.frame_liste_favoris,
                text="Aucune ville favorite\n\nRecherchez une ville et cliquez sur ⭐\npour l'ajouter aux favoris",
                text_color=COULEUR_TEXTE_SECONDAIRE,
                justify="center"
            ).pack(pady=40)
            return
        
        for ville in favoris:
            self._creer_carte_favori(ville)
    
    def _rechercher(self) -> None:
        """Lance la recherche de ville."""
        query = self.entry_recherche.get().strip()
        if not query:
            return
        
        self.btn_recherche.configure(text="...")
        self.update()
        
        self.resultats = rechercher_villes(query)
        
        for widget in self.frame_resultats.winfo_children():
            widget.destroy()
        
        if not self.resultats:
            ctk.CTkLabel(
                self.frame_resultats,
                text=f"Aucun resultat pour '{query}'",
                text_color=COULEUR_DANGER
            ).pack(pady=30)
        else:
            for loc in self.resultats:
                self._creer_carte_resultat(loc)
        
        self.btn_recherche.configure(text="Rechercher")
    
    def _creer_carte_resultat(self, loc: Localisation) -> None:
        """Crée une carte pour un résultat de recherche."""
        frame = ctk.CTkFrame(
            self.frame_resultats,
            fg_color=COULEUR_CARTE_HOVER,
            corner_radius=8
        )
        frame.pack(fill="x", pady=3, padx=2)
        
        # Bouton étoile
        est_favori = self.gestionnaire_config.est_favorite(loc.nom, loc.pays)
        btn_etoile = ctk.CTkButton(
            frame,
            text="⭐" if est_favori else "☆",
            width=35,
            height=35,
            fg_color="#f1c40f" if est_favori else COULEUR_CARTE,
            hover_color="#d4ac0d" if est_favori else COULEUR_CARTE_HOVER,
            text_color=COULEUR_FOND if est_favori else "#f1c40f",
            font=ctk.CTkFont(size=16),
            command=lambda l=loc: self._toggle_favori_recherche(l)
        )
        btn_etoile.pack(side="left", padx=5, pady=5)
        
        # Contenu
        frame_content = ctk.CTkFrame(frame, fg_color="transparent")
        frame_content.pack(side="left", fill="both", expand=True, padx=5, pady=8)
        
        ctk.CTkLabel(
            frame_content,
            text=loc.nom,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            frame_content,
            text=f"{loc.pays} ({loc.latitude:.2f}, {loc.longitude:.2f})",
            font=ctk.CTkFont(size=11),
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w"
        ).pack(fill="x")
        
        # Bouton choisir
        ctk.CTkButton(
            frame,
            text="Choisir",
            command=lambda l=loc: self._selectionner_recherche(l),
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            text_color=COULEUR_FOND,
            width=70,
            height=30
        ).pack(side="right", padx=10, pady=5)
    
    def _creer_carte_favori(self, ville: VilleConfig) -> None:
        """Crée une carte pour une ville favorite."""
        frame = ctk.CTkFrame(
            self.frame_liste_favoris,
            fg_color=COULEUR_CARTE_HOVER,
            corner_radius=8
        )
        frame.pack(fill="x", pady=3, padx=2)
        
        # Bouton étoile (pour supprimer)
        btn_etoile = ctk.CTkButton(
            frame,
            text="⭐",
            width=35,
            height=35,
            fg_color="#f1c40f",
            hover_color="#e74c3c",
            text_color=COULEUR_FOND,
            font=ctk.CTkFont(size=16),
            command=lambda v=ville: self._supprimer_favori(v)
        )
        btn_etoile.pack(side="left", padx=5, pady=5)
        
        # Contenu
        frame_content = ctk.CTkFrame(frame, fg_color="transparent")
        frame_content.pack(side="left", fill="both", expand=True, padx=5, pady=8)
        
        ctk.CTkLabel(
            frame_content,
            text=str(ville),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).pack(fill="x")
        
        # Données météo en cache
        if ville.derniere_maj:
            details = f"UV: {ville.indice_uv:.1f} | H: {ville.humidite:.0f}% | T: {ville.temperature:.1f}°C"
            if ville.pm2_5:
                details += f" | PM2.5: {ville.pm2_5:.0f}"
            details += f"\nMis a jour: {ville.derniere_maj}"
        else:
            details = "Pas encore de donnees"
        
        ctk.CTkLabel(
            frame_content,
            text=details,
            font=ctk.CTkFont(size=10),
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w"
        ).pack(fill="x")
        
        # Bouton choisir
        ctk.CTkButton(
            frame,
            text="Choisir",
            command=lambda v=ville: self._selectionner_favori(v),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            text_color="#fff",
            width=70,
            height=30
        ).pack(side="right", padx=10, pady=5)
    
    def _toggle_favori_recherche(self, loc: Localisation) -> None:
        """Bascule l'état favori d'une ville."""
        ville = VilleConfig(
            nom=loc.nom,
            pays=loc.pays,
            latitude=loc.latitude,
            longitude=loc.longitude
        )
        self.gestionnaire_config.basculer_favorite(ville)
        self._rechercher()  # Rafraîchir l'affichage
    
    def _supprimer_favori(self, ville: VilleConfig) -> None:
        """Supprime une ville des favoris."""
        self.gestionnaire_config.supprimer_favorite(ville.nom, ville.pays)
        self._actualiser_favoris()
    
    def _toggle_favori_ville_actuelle(self) -> None:
        """Bascule l'état favori de la ville actuelle."""
        est_favori = self.gestionnaire_config.basculer_favorite(self.ville_actuelle)
        
        # Mettre à jour le bouton
        if est_favori:
            self.btn_favori_actuel.configure(
                text="⭐",
                fg_color="#f1c40f",
                hover_color="#d4ac0d",
                text_color=COULEUR_FOND
            )
        else:
            self.btn_favori_actuel.configure(
                text="☆",
                fg_color=COULEUR_CARTE_HOVER,
                hover_color="#f1c40f",
                text_color="#f1c40f"
            )
        
        # Actualiser l'onglet favoris si visible
        if self.onglet_actif == "favoris":
            self._actualiser_favoris()
    
    def _selectionner_recherche(self, loc: Localisation) -> None:
        """Sélectionne une ville depuis la recherche (appel API)."""
        ville = VilleConfig(
            nom=loc.nom,
            pays=loc.pays,
            latitude=loc.latitude,
            longitude=loc.longitude
        )
        self.gestionnaire_config.definir_ville_actuelle(ville)
        self.client_meteo.definir_localisation(loc)
        self.callback(utiliser_cache=False)  # Forcer l'appel API
        self.destroy()
    
    def _selectionner_favori(self, ville: VilleConfig) -> None:
        """Sélectionne une ville depuis les favoris (utilise le cache)."""
        self.gestionnaire_config.definir_ville_actuelle(ville)
        
        # Mettre à jour le client météo
        loc = Localisation(
            nom=ville.nom,
            pays=ville.pays,
            latitude=ville.latitude,
            longitude=ville.longitude
        )
        self.client_meteo.definir_localisation(loc)
        
        self.callback(utiliser_cache=True, ville_cache=ville)  # Utiliser le cache
        self.destroy()


# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================

class ApplicationPrincipale(ctk.CTk):
    """
    Fenêtre principale de l'application DermaLogic.
    
    Gère la navigation entre les pages et les données globales
    (météo, produits, configuration, historique).
    
    Attributes:
        client_meteo: Client API Open-Meteo
        gestionnaire: Gestionnaire de produits
        gestionnaire_config: Gestionnaire de configuration
        gestionnaire_historique: Gestionnaire d'historique des analyses
        gestionnaire_profil: Gestionnaire de profil utilisateur
        donnees_env: Données environnementales actuelles
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("DermaLogic")
        self.geometry("1100x750")
        self.configure(fg_color=COULEUR_FOND)
        
        # Configuration du thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Initialisation des services
        self.gestionnaire_config = GestionnaireConfig()
        self.gestionnaire = GestionnaireProduits()
        self.gestionnaire_historique = GestionnaireHistorique()
        self.gestionnaire_profil = GestionnaireProfil()
        self.donnees_env: DonneesEnvironnementales = None
        
        # Client Gemini pour l'analyse IA
        self.client_gemini = ClientGemini()
        
        # Initialiser le client météo avec la ville sauvegardée
        ville_config = self.gestionnaire_config.obtenir_ville_actuelle()
        self.client_meteo = ClientOpenMeteo()
        self.client_meteo.definir_localisation(Localisation(
            nom=ville_config.nom,
            pays=ville_config.pays,
            latitude=ville_config.latitude,
            longitude=ville_config.longitude
        ))
        
        # Construction de l'interface
        self._creer_interface()
        self._afficher_page("accueil")
        self.actualiser_donnees()
    
    def _creer_interface(self) -> None:
        """Construit l'interface principale."""
        
        # ===== BARRE DE NAVIGATION =====
        self.frame_nav = ctk.CTkFrame(self, fg_color=COULEUR_PANNEAU, height=55)
        self.frame_nav.pack(fill="x")
        self.frame_nav.pack_propagate(False)
        
        # Logo
        ctk.CTkLabel(
            self.frame_nav,
            text="DermaLogic",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=20)
        
        # Boutons de navigation
        frame_btns = ctk.CTkFrame(self.frame_nav, fg_color="transparent")
        frame_btns.pack(side="left", padx=25)
        
        self.btn_accueil = ctk.CTkButton(
            frame_btns,
            text="Analyse",
            command=lambda: self._afficher_page("accueil"),
            fg_color="transparent",
            hover_color=COULEUR_CARTE_HOVER,
            width=90
        )
        self.btn_accueil.pack(side="left", padx=5)
        
        self.btn_produits = ctk.CTkButton(
            frame_btns,
            text="Mes Produits",
            command=lambda: self._afficher_page("produits"),
            fg_color="transparent",
            hover_color=COULEUR_CARTE_HOVER,
            width=110
        )
        self.btn_produits.pack(side="left", padx=5)
        
        self.btn_historique = ctk.CTkButton(
            frame_btns,
            text="📊 Historique",
            command=lambda: self._afficher_page("historique"),
            fg_color="transparent",
            hover_color=COULEUR_CARTE_HOVER,
            width=110
        )
        self.btn_historique.pack(side="left", padx=5)
        
        self.btn_profil = ctk.CTkButton(
            frame_btns,
            text="👤 Mon Profil",
            command=lambda: self._afficher_page("profil"),
            fg_color="transparent",
            hover_color=COULEUR_CARTE_HOVER,
            width=110
        )
        self.btn_profil.pack(side="left", padx=5)
        
        # Sélection de ville (à droite)
        frame_ville = ctk.CTkFrame(self.frame_nav, fg_color="transparent")
        frame_ville.pack(side="right", padx=20)
        
        self.label_ville = ctk.CTkLabel(
            frame_ville,
            text=self.client_meteo.nom_ville,
            font=ctk.CTkFont(size=12),
            text_color=COULEUR_TEXTE_SECONDAIRE
        )
        self.label_ville.pack(side="left", padx=(0, 10))
        
        self.btn_ville = ctk.CTkButton(
            frame_ville,
            text="Changer",
            command=self._ouvrir_selection_ville,
            fg_color=COULEUR_CARTE_HOVER,
            hover_color=COULEUR_CARTE,
            width=80,
            height=28
        )
        self.btn_ville.pack(side="left")
        
        # ===== CONTENEUR DE PAGES =====
        self.frame_pages = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_pages.pack(fill="both", expand=True)
        
        # Pages
        self.page_accueil = PageAccueil(self.frame_pages, self)
        self.page_produits = PageProduits(self.frame_pages, self.gestionnaire)
        self.page_historique = PageHistorique(self.frame_pages, self.gestionnaire_historique)
        self.page_profil = PageProfil(self.frame_pages, self.gestionnaire_profil)
    
    def _afficher_page(self, nom: str) -> None:
        """
        Affiche une page et met à jour la navigation.
        
        Args:
            nom: Nom de la page ("accueil", "produits" ou "historique")
        """
        # Masquer toutes les pages
        self.page_accueil.pack_forget()
        self.page_produits.pack_forget()
        self.page_historique.pack_forget()
        self.page_profil.pack_forget()
        
        # Reset des boutons
        self.btn_accueil.configure(fg_color="transparent", text_color="#fff")
        self.btn_produits.configure(fg_color="transparent", text_color="#fff")
        self.btn_historique.configure(fg_color="transparent", text_color="#fff")
        self.btn_profil.configure(fg_color="transparent", text_color="#fff")
        
        # Afficher la page demandée
        if nom == "accueil":
            self.page_accueil.pack(fill="both", expand=True)
            self.btn_accueil.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
        elif nom == "produits":
            self.page_produits.pack(fill="both", expand=True)
            self.page_produits.actualiser_liste()
            self.btn_produits.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
        elif nom == "historique":
            self.page_historique.pack(fill="both", expand=True)
            self.page_historique.actualiser()
            self.btn_historique.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
        elif nom == "profil":
            self.page_profil.pack(fill="both", expand=True)
            self.page_profil.actualiser()
            self.btn_profil.configure(fg_color=COULEUR_ACCENT, text_color=COULEUR_FOND)
    
    # =========================================================================
    # HELPERS COULEUR
    # =========================================================================
    
    @staticmethod
    def _couleur_uv(niveau: str) -> str:
        """Retourne la couleur pour un niveau UV."""
        couleurs = {
            "Faible": COULEUR_ACCENT,
            "Modere": "#f9ed69",
            "Eleve": "#f38181",
            "Tres eleve": COULEUR_DANGER,
            "Extreme": "#aa2ee6"
        }
        return couleurs.get(niveau, "#fff")
    
    @staticmethod
    def _couleur_humidite(niveau: str) -> str:
        """Retourne la couleur pour un niveau d'humidité."""
        couleurs = {
            "Tres sec": COULEUR_DANGER,
            "Sec": "#f9ed69",
            "Normal": COULEUR_ACCENT,
            "Humide": "#00b4d8"
        }
        return couleurs.get(niveau, "#fff")
    
    @staticmethod
    def _couleur_pollution(niveau: str) -> str:
        """Retourne la couleur pour un niveau de pollution."""
        couleurs = {
            "Excellent": COULEUR_ACCENT,
            "Bon": "#9be36d",
            "Modere": "#f9ed69",
            "Mauvais": "#f38181",
            "Tres mauvais": COULEUR_DANGER,
            "Inconnu": COULEUR_TEXTE_SECONDAIRE
        }
        return couleurs.get(niveau, "#fff")
    
    # =========================================================================
    # ACTIONS
    # =========================================================================
    
    def actualiser_donnees(self, utiliser_cache: bool = False, ville_cache: VilleConfig = None) -> None:
        """
        Actualise les données météo.
        
        Args:
            utiliser_cache: Si True, utilise les données en cache (pas d'appel API)
            ville_cache: Données de ville en cache à utiliser
        """
        self.page_accueil.btn_actualiser.configure(text="...")
        self.update()
        
        if utiliser_cache and ville_cache and ville_cache.derniere_maj:
            # Utiliser les données en cache
            self.donnees_env = DonneesEnvironnementales(
                indice_uv=ville_cache.indice_uv,
                humidite_relative=ville_cache.humidite,
                temperature=ville_cache.temperature,
                pm2_5=ville_cache.pm2_5
            )
        else:
            # Appel API
            self.donnees_env = self.client_meteo.obtenir_donnees_jour()
            
            # Sauvegarder les données dans le cache
            if self.donnees_env:
                self.gestionnaire_config.mettre_a_jour_meteo_actuelle(
                    indice_uv=self.donnees_env.indice_uv,
                    humidite=self.donnees_env.humidite_relative,
                    temperature=self.donnees_env.temperature,
                    pm2_5=self.donnees_env.pm2_5
                )
                
                # Aussi mettre à jour le favori si applicable
                ville = self.gestionnaire_config.obtenir_ville_actuelle()
                if self.gestionnaire_config.est_favorite(ville.nom, ville.pays):
                    self.gestionnaire_config.mettre_a_jour_meteo_favorite(
                        nom=ville.nom,
                        pays=ville.pays,
                        indice_uv=self.donnees_env.indice_uv,
                        humidite=self.donnees_env.humidite_relative,
                        temperature=self.donnees_env.temperature,
                        pm2_5=self.donnees_env.pm2_5
                    )
        
        if self.donnees_env:
            # UV
            self.page_accueil.carte_uv.mettre_a_jour(
                f"{self.donnees_env.indice_uv:.1f}",
                self.donnees_env.niveau_uv,
                self._couleur_uv(self.donnees_env.niveau_uv)
            )
            
            # Humidité
            self.page_accueil.carte_humidite.mettre_a_jour(
                f"{self.donnees_env.humidite_relative:.0f}%",
                self.donnees_env.niveau_humidite,
                self._couleur_humidite(self.donnees_env.niveau_humidite)
            )
            
            # Pollution
            pm = f"{self.donnees_env.pm2_5:.0f}" if self.donnees_env.pm2_5 else "--"
            self.page_accueil.carte_pollution.mettre_a_jour(
                f"{pm} ug/m3",
                self.donnees_env.niveau_pollution,
                self._couleur_pollution(self.donnees_env.niveau_pollution)
            )
            
            # Température
            self.page_accueil.carte_temp.mettre_a_jour(
                f"{self.donnees_env.temperature:.1f}C",
                self.donnees_env.heure if hasattr(self.donnees_env, 'heure') else ""
            )
        else:
            # Erreur
            for carte in [
                self.page_accueil.carte_uv,
                self.page_accueil.carte_humidite,
                self.page_accueil.carte_pollution,
                self.page_accueil.carte_temp
            ]:
                carte.mettre_a_jour("Erreur", "Echec", COULEUR_DANGER)
        
        self.page_accueil.btn_actualiser.configure(text="Actualiser")
    
    def lancer_analyse(self) -> None:
        """Lance l'analyse rapide des produits (algorithme local)."""
        if not self.donnees_env:
            messagebox.showwarning(
                "Attention",
                "Chargez d'abord les données météo"
            )
            return
        
        produits = self.gestionnaire.obtenir_tous()
        if not produits:
            messagebox.showinfo(
                "Info",
                "Ajoutez d'abord des produits dans 'Mes Produits'"
            )
            return
        
        self.page_accueil.btn_analyse_simple.configure(text="⏳ Analyse...")
        self.update()
        
        # Construire les conditions
        conditions = ConditionsEnvironnementales(
            indice_uv=self.donnees_env.indice_uv,
            humidite=self.donnees_env.humidite_relative,
            pm2_5=self.donnees_env.pm2_5
        )
        
        # Analyser
        moteur = MoteurDecision(produits)
        resultat = moteur.analyser(conditions)
        
        # Sauvegarder dans l'historique
        self._sauvegarder_analyse_historique(resultat)
        
        # Afficher
        self.page_accueil.afficher_resultat(resultat)
        self.page_accueil.btn_analyse_simple.configure(text="⚡ Analyse rapide")
    
    def ouvrir_analyse_ia(self) -> None:
        """Ouvre la fenêtre d'analyse IA avec instructions personnalisées."""
        if not self.donnees_env:
            messagebox.showwarning(
                "Attention",
                "Chargez d'abord les données météo"
            )
            return
        
        produits = self.gestionnaire.obtenir_tous()
        if not produits:
            messagebox.showinfo(
                "Info",
                "Ajoutez d'abord des produits dans 'Mes Produits'"
            )
            return
        
        FenetreAnalyseIA(self, self, self._executer_analyse_ia)
    
    def _executer_analyse_ia(self, instructions: str = "") -> None:
        """
        Exécute l'analyse IA personnalisée.
        
        Args:
            instructions: Instructions personnalisées de l'utilisateur
        """
        self.page_accueil.btn_analyse_ia.configure(
            text="⏳ IA en cours...",
            state="disabled"
        )
        self.update()
        
        try:
            # Collecter les produits sous forme de dicts
            produits = self.gestionnaire.obtenir_tous()
            produits_dicts = []
            for p in produits:
                produits_dicts.append({
                    "nom": p.nom,
                    "category": p.category.value,
                    "moment": p.moment.value,
                    "photosensitive": p.photosensitive,
                    "occlusivity": p.occlusivity,
                    "cleansing_power": p.cleansing_power,
                    "active_tag": p.active_tag.value
                })
            
            # Collecter les données environnementales
            ville = self.gestionnaire_config.obtenir_ville_actuelle()
            donnees_env = {
                "ville": ville.nom,
                "temperature": self.donnees_env.temperature,
                "indice_uv": self.donnees_env.indice_uv,
                "niveau_uv": self.donnees_env.niveau_uv,
                "humidite": self.donnees_env.humidite_relative,
                "niveau_humidite": self.donnees_env.niveau_humidite,
                "pm2_5": self.donnees_env.pm2_5,
                "niveau_pollution": self.donnees_env.niveau_pollution
            }
            
            # Contextes utilisateur
            profil_texte = self.gestionnaire_profil.generer_contexte_ia()
            etat_texte = self.gestionnaire_profil.etat_quotidien.to_prompt()
            
            # Appeler Gemini
            resultat = self.client_gemini.analyser_routine(
                produits=produits_dicts,
                donnees_env=donnees_env,
                profil_utilisateur=profil_texte,
                etat_quotidien=etat_texte,
                instructions=instructions
            )
            
            if resultat.succes:
                self._afficher_resultat_ia(resultat)
            else:
                messagebox.showerror(
                    "Erreur IA",
                    f"L'analyse IA a échoué :\n{resultat.erreur}"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de l'analyse IA :\n{str(e)}"
            )
        
        finally:
            self.page_accueil.btn_analyse_ia.configure(
                text="🤖 Analyse IA personnalisée",
                state="normal"
            )
    
    def _afficher_resultat_ia(self, resultat: ResultatRoutineIA) -> None:
        """
        Affiche le résultat de l'analyse IA dans une fenêtre dédiée.
        
        Args:
            resultat: Résultat de l'analyse de routine IA
        """
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("🤖 Résultat - Analyse IA")
        fenetre.geometry("700x650")
        fenetre.configure(fg_color=COULEUR_FOND)
        fenetre.transient(self)
        
        # Header
        ctk.CTkLabel(
            fenetre,
            text="🤖 Votre routine personnalisée",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=15)
        
        # Alertes si présentes
        if resultat.alertes:
            frame_alertes = ctk.CTkFrame(
                fenetre, fg_color="#2a1a2a", corner_radius=10
            )
            frame_alertes.pack(fill="x", padx=20, pady=(0, 10))
            for alerte in resultat.alertes:
                ctk.CTkLabel(
                    frame_alertes,
                    text=f"⚠️ {alerte}",
                    font=ctk.CTkFont(size=11),
                    text_color=COULEUR_DANGER
                ).pack(anchor="w", padx=12, pady=3)
        
        # Scrollable content
        frame_scroll = ctk.CTkScrollableFrame(fenetre, fg_color="transparent")
        frame_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Afficher chaque moment
        moments = [
            ("☀️ MATIN", resultat.matin, COULEUR_ACCENT),
            ("🌤️ JOURNÉE", resultat.journee, "#f9ed69"),
            ("🌙 SOIR", resultat.soir, "#9b59b6")
        ]
        
        for titre, moment, couleur in moments:
            self._creer_section_moment_ia(frame_scroll, titre, moment, couleur)
        
        # Bouton fermer
        ctk.CTkButton(
            fenetre,
            text="Fermer",
            command=fenetre.destroy,
            fg_color=COULEUR_ACCENT,
            hover_color=COULEUR_ACCENT_HOVER,
            width=150
        ).pack(pady=15)
    
    def _creer_section_moment_ia(
        self, parent, titre: str, moment: RoutineMoment, couleur: str
    ) -> None:
        """
        Crée une section pour un moment de la journée dans le résultat IA.
        
        Args:
            parent: Widget parent
            titre: Titre du moment
            moment: Données du moment
            couleur: Couleur du header
        """
        frame = ctk.CTkFrame(parent, fg_color=COULEUR_PANNEAU, corner_radius=12)
        frame.pack(fill="x", pady=8)
        
        # Header moment
        header = ctk.CTkFrame(frame, fg_color=couleur, corner_radius=8, height=35)
        header.pack(fill="x", padx=8, pady=(8, 5))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text=titre,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COULEUR_FOND
        ).pack(expand=True)
        
        # Conseils
        if moment.conseils:
            ctk.CTkLabel(
                frame,
                text=moment.conseils,
                font=ctk.CTkFont(size=12),
                wraplength=600,
                justify="left"
            ).pack(anchor="w", padx=12, pady=8)
        
        # Produits avec justification (icône ℹ️)
        if moment.produits:
            for produit in moment.produits:
                frame_produit = ctk.CTkFrame(
                    frame, fg_color=COULEUR_CARTE, corner_radius=8
                )
                frame_produit.pack(fill="x", padx=12, pady=3)
                
                # Nom du produit
                ctk.CTkLabel(
                    frame_produit,
                    text=f"• {produit.nom}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                ).pack(side="left", padx=10, pady=6)
                
                # Bouton info (justification)
                if produit.justification:
                    btn_info = ctk.CTkButton(
                        frame_produit,
                        text="ℹ️",
                        width=30,
                        height=25,
                        fg_color="transparent",
                        hover_color=COULEUR_CARTE_HOVER,
                        command=lambda j=produit.justification, n=produit.nom: 
                            messagebox.showinfo(
                                f"Justification - {n}", j
                            )
                    )
                    btn_info.pack(side="right", padx=5, pady=4)
        
        # Espacement
        ctk.CTkFrame(frame, fg_color="transparent", height=5).pack()
    
    def _sauvegarder_analyse_historique(self, resultat: ResultatDecision) -> None:
        """
        Sauvegarde le résultat de l'analyse dans l'historique.
        
        Args:
            resultat: Résultat de l'algorithme de décision
        """
        ville = self.gestionnaire_config.obtenir_ville_actuelle()
        
        # Créer les conditions d'analyse
        conditions = ConditionsAnalyse(
            ville=ville.nom,
            pays=ville.pays,
            indice_uv=self.donnees_env.indice_uv,
            niveau_uv=self.donnees_env.niveau_uv,
            humidite=self.donnees_env.humidite_relative,
            niveau_humidite=self.donnees_env.niveau_humidite,
            temperature=self.donnees_env.temperature,
            pm2_5=self.donnees_env.pm2_5,
            niveau_pollution=self.donnees_env.niveau_pollution
        )
        
        # Convertir les produits par moment
        def convertir_produits(produits_list, exclus_dict):
            return [
                ProduitAnalyse(
                    nom=p.nom,
                    category=p.category.value,
                    moment=p.moment.value,
                    active_tag=p.active_tag.value,
                    exclu=False,
                    raison_exclusion=""
                )
                for p in produits_list
            ]
        
        produits_matin = convertir_produits(resultat.matin.produits, {})
        produits_journee = convertir_produits(resultat.journee.produits, {})
        produits_soir = convertir_produits(resultat.soir.produits, {})
        
        # Ajouter à l'historique
        self.gestionnaire_historique.ajouter_analyse(
            conditions=conditions,
            produits_matin=produits_matin,
            produits_journee=produits_journee,
            produits_soir=produits_soir,
            alertes=resultat.filtres_appliques
        )
    
    def _ouvrir_selection_ville(self) -> None:
        """Ouvre la fenêtre de sélection de ville."""
        FenetreSelectionVille(
            self, 
            self.client_meteo, 
            self.gestionnaire_config,
            self._on_ville_changee
        )
    
    def _on_ville_changee(self, utiliser_cache: bool = False, ville_cache: VilleConfig = None) -> None:
        """
        Callback quand la ville est changée.
        
        Args:
            utiliser_cache: Si True, utilise les données en cache
            ville_cache: Données de ville en cache
        """
        self.label_ville.configure(text=self.client_meteo.nom_ville)
        self.actualiser_donnees(utiliser_cache=utiliser_cache, ville_cache=ville_cache)


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def lancer_application() -> None:
    """Lance l'application DermaLogic."""
    app = ApplicationPrincipale()
    app.mainloop()


if __name__ == "__main__":
    lancer_application()
