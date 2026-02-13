"""
DermaLogic - Page Mes Produits
================================

Page de gestion des produits personnalises.
Permet d'ajouter, visualiser et supprimer des produits.
"""

import flet as ft
from gui.theme import (
    COULEUR_ACCENT,
    COULEUR_ACCENT_HOVER,
    COULEUR_FOND,
    COULEUR_DANGER,
    COULEUR_PANNEAU,
    COULEUR_CARTE,
    COULEUR_TEXTE_SECONDAIRE,
    COULEURS_CATEGORIE,
    COULEURS_MOMENT,
)
from gui.data import GestionnaireProduits
from gui.dialogs.formulaire_produit import FormulaireProduit
from gui.dialogs.fenetre_recherche_ia import FenetreRechercheIA
from core.models import ProduitDerma


class PageProduits(ft.Column):
    """Page de gestion des produits."""

    def __init__(self, page: ft.Page, gestionnaire: GestionnaireProduits, get_api_key=None):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.page_ref = page
        self.gestionnaire = gestionnaire
        self._get_api_key = get_api_key

        # Header
        self.label_count = ft.Text(
            "0 produits", size=14, color=COULEUR_TEXTE_SECONDAIRE
        )

        self.btn_ajouter_ia = ft.Button(
            "+ Ajouter avec IA",
            on_click=self._ajouter_avec_ia,
            bgcolor="#9b59b6",
            color="#ffffff",
            height=36,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
        )

        self.btn_ajouter = ft.Button(
            "+ Ajouter",
            on_click=self._ouvrir_formulaire,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=36,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
        )

        # Liste des produits
        self.liste_produits = ft.Column(spacing=0)

        self.controls = [
            # Header
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=15, bottom=10),
                content=ft.ResponsiveRow(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            col={"xs": 12, "md": 6},
                            content=ft.Row(
                                controls=[
                                    ft.Text(
                                        "Mes Produits",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color="#ffffff",
                                    ),
                                    ft.Container(width=15),
                                    self.label_count,
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12, "md": 6},
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.END,
                                controls=[
                                    self.btn_ajouter_ia,
                                    ft.Container(width=5),
                                    self.btn_ajouter,
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            # Liste
            ft.Container(
                margin=ft.Margin.symmetric(horizontal=20),
                expand=True,
                content=self.liste_produits,
            ),
        ]

        self.actualiser_liste()

    def actualiser_liste(self):
        """Actualise l'affichage de la liste des produits."""
        self.liste_produits.controls.clear()

        produits = self.gestionnaire.obtenir_tous()
        self.label_count.value = f"{len(produits)} produits"

        if not produits:
            self._afficher_liste_vide()
            return

        # Grouper par moment
        moments = {"matin": [], "journee": [], "soir": [], "tous": []}
        for i, produit in enumerate(produits):
            moments[produit.moment.value].append((i, produit))

        for moment, prods in moments.items():
            if prods:
                self._creer_section_moment(moment, prods)

    def _afficher_liste_vide(self):
        """Affiche un message quand la liste est vide."""
        self.liste_produits.controls.append(
            ft.Container(
                bgcolor=COULEUR_PANNEAU,
                border_radius=15,
                margin=ft.Margin.symmetric(vertical=50, horizontal=50),
                padding=40,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "Aucun produit enregistre\n\nCliquez sur '+ Ajouter'\npour commencer",
                    size=14,
                    color=COULEUR_TEXTE_SECONDAIRE,
                    text_align=ft.TextAlign.CENTER,
                ),
            )
        )

    def _creer_section_moment(self, moment: str, produits_avec_index: list):
        """Cree une section pour un moment de la journee."""
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))

        # Header de section
        self.liste_produits.controls.append(
            ft.Container(
                margin=ft.Margin.only(top=15, bottom=5),
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=6, height=20, bgcolor=couleur, border_radius=3
                        ),
                        ft.Container(width=8),
                        ft.Text(
                            titre,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=couleur,
                        ),
                    ],
                ),
            )
        )

        # Produits
        for index, produit in produits_avec_index:
            self.liste_produits.controls.append(
                self._creer_carte_produit(produit, index)
            )

    def _creer_carte_produit(self, produit: ProduitDerma, index: int) -> ft.Container:
        """Cree une carte pour un produit avec bouton de suppression."""
        couleur = COULEURS_CATEGORIE.get(produit.category.value, "#fff")

        badges = [
            ft.Container(
                content=ft.Text(
                    produit.category.value,
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=COULEUR_FOND,
                ),
                bgcolor=couleur,
                border_radius=4,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            )
        ]

        if produit.photosensitive:
            badges.append(
                ft.Text(
                    "PHOTOSENSIBLE",
                    size=9,
                    weight=ft.FontWeight.BOLD,
                    color=COULEUR_DANGER,
                )
            )

        details = (
            f"Occlusivite: {produit.occlusivity}/5 | "
            f"Nettoyage: {produit.cleansing_power}/5 | "
            f"{produit.active_tag.value}"
        )

        return ft.Container(
            bgcolor=COULEUR_CARTE,
            border_radius=10,
            margin=ft.Margin.symmetric(vertical=3),
            padding=ft.Padding.only(left=0, right=10, top=10, bottom=10),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Indicateur couleur
                    ft.Container(
                        width=5,
                        height=60,
                        bgcolor=couleur,
                        border_radius=ft.BorderRadius.only(
                            top_left=10, bottom_left=10
                        ),
                    ),
                    ft.Container(width=12),
                    # Contenu
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        produit.nom,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color="#ffffff",
                                        expand=True,
                                    ),
                                    *badges,
                                ],
                            ),
                            ft.Text(
                                details,
                                size=11,
                                color=COULEUR_TEXTE_SECONDAIRE,
                            ),
                        ],
                    ),
                    # Bouton supprimer
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=COULEUR_DANGER,
                        icon_size=20,
                        on_click=lambda e, idx=index: self._confirmer_suppression(idx),
                    ),
                ],
            ),
        )

    def _confirmer_suppression(self, index: int):
        """Affiche une confirmation avant suppression."""

        def _supprimer(e):
            self.gestionnaire.supprimer(index)
            dialog.open = False
            self.page_ref.update()
            if dialog in self.page_ref.overlay:
                self.page_ref.overlay.remove(dialog)
            self.actualiser_liste()
            self.page_ref.update()

        def _annuler(e):
            dialog.open = False
            self.page_ref.update()
            if dialog in self.page_ref.overlay:
                self.page_ref.overlay.remove(dialog)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmer", color="#ffffff"),
            content=ft.Text("Supprimer ce produit ?", color="#ffffff"),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=_annuler,
                    style=ft.ButtonStyle(color=COULEUR_TEXTE_SECONDAIRE),
                ),
                ft.Button(
                    "Supprimer",
                    on_click=_supprimer,
                    bgcolor=COULEUR_DANGER,
                    color="#ffffff",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()

    def _ouvrir_formulaire(self, e=None):
        """Ouvre le formulaire d'ajout de produit."""
        form = FormulaireProduit(
            self.page_ref,
            self.gestionnaire,
            self._on_produit_ajoute,
        )
        form.ouvrir()

    def _ajouter_avec_ia(self, e=None):
        """Ouvre la fenetre de recherche IA."""
        api_key = self._get_api_key() if self._get_api_key else ""
        fenetre = FenetreRechercheIA(
            self.page_ref,
            self.gestionnaire,
            self._on_produit_ajoute,
            api_key=api_key,
        )
        fenetre.ouvrir()

    def _on_produit_ajoute(self):
        """Callback apres ajout d'un produit."""
        self.actualiser_liste()
        self.page_ref.update()
