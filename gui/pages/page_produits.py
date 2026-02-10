"""
DermaLogic - Page Produits
===========================

Page de gestion des produits personnalisés.
"""

import flet as ft

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE, COULEUR_ACCENT,
    COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE, COULEUR_DANGER,
    COULEUR_IA, COULEURS_MOMENT,
)
from gui.composants_flet import carte_produit


class PageProduits(ft.Column):
    """
    Page de gestion des produits personnalisés.
    Permet d'ajouter, visualiser et supprimer des produits.
    """

    def __init__(self, gestionnaire, on_ouvrir_formulaire, on_ajouter_ia):
        self.gestionnaire = gestionnaire
        self._on_ouvrir_formulaire = on_ouvrir_formulaire
        self._on_ajouter_ia = on_ajouter_ia

        self.label_count = ft.Text(
            "0 produits", size=14, color=COULEUR_TEXTE_SECONDAIRE,
        )
        self.liste = ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=4, expand=True,
        )

        header = ft.Row(
            [
                ft.Text("Mes Produits", size=24, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                self.label_count,
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "+ Ajouter avec IA",
                    on_click=lambda e: self._on_ajouter_ia(),
                    bgcolor=COULEUR_IA, color=COULEUR_TEXTE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                ),
                ft.ElevatedButton(
                    "+ Ajouter",
                    on_click=lambda e: self._on_ouvrir_formulaire(),
                    bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        super().__init__(
            controls=[header, self.liste],
            spacing=15,
            expand=True,
        )

    def actualiser_liste(self):
        """Actualise l'affichage de la liste des produits."""
        self.liste.controls.clear()

        produits = self.gestionnaire.obtenir_tous()
        self.label_count.value = f"{len(produits)} produits"

        if not produits:
            self.liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Aucun produit enregistré\n\nCliquez sur '+ Ajouter' pour commencer",
                                size=14, color=COULEUR_TEXTE_SECONDAIRE,
                                text_align=ft.TextAlign.CENTER,
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=COULEUR_PANNEAU, border_radius=15,
                    padding=ft.padding.all(40),
                    alignment=ft.Alignment(0, 0),
                )
            )
            if self.page:
                self.page.update()
            return

        # Grouper par moment
        moments = {"matin": [], "journee": [], "soir": [], "tous": []}
        for i, produit in enumerate(produits):
            moments[produit.moment.value].append((i, produit))

        for moment, prods in moments.items():
            if prods:
                self._creer_section_moment(moment, prods)

        if self.page:
            self.page.update()

    def _creer_section_moment(self, moment: str, produits_avec_index: list):
        """Crée une section pour un moment de la journée."""
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))

        # Header de section
        self.liste.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(width=6, height=20, bgcolor=couleur, border_radius=3),
                    ft.Text(titre, size=13, weight=ft.FontWeight.BOLD, color=couleur),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(top=15, bottom=5),
            )
        )

        for index, produit in produits_avec_index:
            self.liste.controls.append(
                carte_produit(
                    produit,
                    on_delete=self._supprimer_produit,
                    index=index,
                    compact=False,
                )
            )

    def _supprimer_produit(self, index: int):
        """Supprime un produit après confirmation via SnackBar."""
        def confirmer(e):
            self.gestionnaire.supprimer(index)
            if self.page:
                self.page.close(dlg)
            self.actualiser_liste()

        def annuler(e):
            if self.page:
                self.page.close(dlg)

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmer"),
            content=ft.Text("Supprimer ce produit ?"),
            actions=[
                ft.TextButton("Annuler", on_click=annuler),
                ft.TextButton("Supprimer", on_click=confirmer,
                              style=ft.ButtonStyle(color=COULEUR_DANGER)),
            ],
        )
        if self.page:
            self.page.open(dlg)
