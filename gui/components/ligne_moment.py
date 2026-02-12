"""
DermaLogic - Ligne Moment
==========================

Widget ligne horizontale pour un moment de la journee (matin/journee/soir).
Affiche un header colore et une liste scrollable horizontale de cartes produits.
"""

import flet as ft
from gui.theme import (
    COULEUR_PANNEAU,
    COULEUR_CARTE_HOVER,
    COULEUR_TEXTE_SECONDAIRE,
    COULEUR_FOND,
    COULEUR_ACCENT,
    COULEUR_DANGER,
    COULEURS_CATEGORIE,
    COULEURS_MOMENT,
)
from core.algorithme import ProduitDerma


class LigneMoment(ft.Container):
    """Ligne de produits pour un moment de la journee."""

    def __init__(self, moment: str):
        super().__init__()
        self.moment = moment
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))
        self._couleur = couleur

        self._label_count = ft.Text("0 produits", size=11, color=COULEUR_TEXTE_SECONDAIRE)

        self._row_produits = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
        )
        self._message_vide = ft.Container(
            content=ft.Text("Aucun produit", color=COULEUR_TEXTE_SECONDAIRE),
            padding=ft.Padding.symmetric(vertical=25, horizontal=50),
        )
        self._row_produits.controls = [self._message_vide]

        self.bgcolor = COULEUR_PANNEAU
        self.border_radius = 12
        self.padding = ft.Padding.all(12)
        self.content = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=6, height=25, bgcolor=couleur, border_radius=3
                        ),
                        ft.Text(titre, size=14, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ft.Container(expand=True),
                        self._label_count,
                    ],
                ),
                ft.Container(
                    content=self._row_produits,
                    height=100,
                ),
            ],
        )

    def afficher_produits(
        self,
        produits: list[ProduitDerma],
        nettoyant_optimal: ProduitDerma = None,
    ):
        """Affiche les produits pour ce moment."""
        self._row_produits.controls.clear()

        if not produits:
            self._row_produits.controls.append(self._message_vide)
            self._label_count.value = "0 produits"
        else:
            self._label_count.value = f"{len(produits)} produits"
            for p in produits:
                is_optimal = nettoyant_optimal is not None and p.nom == nettoyant_optimal.nom
                self._row_produits.controls.append(self._creer_carte(p, is_optimal))

    def _creer_carte(self, produit: ProduitDerma, is_optimal: bool) -> ft.Container:
        """Cree une carte pour un produit."""
        couleur_cat = COULEURS_CATEGORIE.get(produit.category.value, "#fff")

        badges = [
            ft.Container(
                content=ft.Text(
                    produit.category.value,
                    size=9,
                    weight=ft.FontWeight.BOLD,
                    color=COULEUR_FOND,
                ),
                bgcolor=couleur_cat,
                border_radius=4,
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            )
        ]

        if is_optimal:
            badges.append(
                ft.Text("OPTIMAL", size=8, weight=ft.FontWeight.BOLD, color=COULEUR_ACCENT)
            )

        if produit.photosensitive:
            badges.append(
                ft.Text("UV!", size=8, weight=ft.FontWeight.BOLD, color=COULEUR_DANGER)
            )

        return ft.Container(
            width=180,
            bgcolor="#0d7377" if is_optimal else COULEUR_CARTE_HOVER,
            border_radius=10,
            padding=ft.Padding.all(8),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(controls=badges, spacing=4),
                    ft.Text(
                        produit.nom,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color="#ffffff",
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"O:{produit.occlusivity} C:{produit.cleansing_power}",
                        size=9,
                        color=COULEUR_TEXTE_SECONDAIRE,
                    ),
                ],
            ),
        )
