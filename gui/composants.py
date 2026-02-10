"""
Composants UI réutilisables pour DermaLogic.

Contient les widgets personnalisés utilisés dans toute l'interface :
- CarteEnvironnement : Affichage d'une donnée environnementale
- LigneMoment : Liste horizontale de produits pour un moment de la journée
"""

import customtkinter as ctk

from core.algorithme import ProduitDerma
from .constantes import (
    COULEUR_CARTE,
    COULEUR_CARTE_HOVER,
    COULEUR_PANNEAU,
    COULEUR_TEXTE_SECONDAIRE,
    COULEUR_ACCENT,
    COULEUR_DANGER,
    COULEUR_FOND,
    COULEURS_CATEGORIE,
    COULEURS_MOMENT,
)


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
