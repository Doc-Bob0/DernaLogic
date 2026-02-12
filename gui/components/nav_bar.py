"""
DermaLogic - Barres de navigation
==================================

Navigation desktop (top bar) et mobile (bottom navigation bar).
"""

import flet as ft
from gui.theme import (
    COULEUR_PANNEAU,
    COULEUR_CARTE_HOVER,
    COULEUR_ACCENT,
    COULEUR_FOND,
    COULEUR_TEXTE_SECONDAIRE,
)


class NavBarDesktop(ft.Container):
    """Barre de navigation desktop (haut de page)."""

    def __init__(self, on_page_change, on_ville_click, nom_ville: str):
        super().__init__()
        self._on_page_change = on_page_change

        self._btn_accueil = ft.TextButton(
            "Analyse",
            on_click=lambda e: on_page_change("accueil"),
            style=ft.ButtonStyle(
                color=COULEUR_FOND,
                bgcolor=COULEUR_ACCENT,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            ),
        )
        self._btn_produits = ft.TextButton(
            "Mes Produits",
            on_click=lambda e: on_page_change("produits"),
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="transparent",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            ),
        )
        self._label_ville = ft.Text(nom_ville, size=12, color=COULEUR_TEXTE_SECONDAIRE)

        self.bgcolor = COULEUR_PANNEAU
        self.height = 55
        self.padding = ft.Padding.symmetric(horizontal=20)
        self.content = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("DermaLogic", size=20, weight=ft.FontWeight.BOLD, color="#ffffff"),
                ft.Container(width=25),
                self._btn_accueil,
                ft.Container(width=5),
                self._btn_produits,
                ft.Container(expand=True),
                self._label_ville,
                ft.Container(width=10),
                ft.Button(
                    "Changer",
                    on_click=on_ville_click,
                    bgcolor=COULEUR_CARTE_HOVER,
                    color="#ffffff",
                    height=28,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=6),
                        padding=ft.Padding.symmetric(horizontal=12),
                    ),
                ),
            ],
        )

    def set_active(self, page_name: str):
        """Met a jour le bouton actif."""
        if page_name == "accueil":
            self._btn_accueil.style.bgcolor = COULEUR_ACCENT
            self._btn_accueil.style.color = COULEUR_FOND
            self._btn_produits.style.bgcolor = "transparent"
            self._btn_produits.style.color = "#ffffff"
        else:
            self._btn_accueil.style.bgcolor = "transparent"
            self._btn_accueil.style.color = "#ffffff"
            self._btn_produits.style.bgcolor = COULEUR_ACCENT
            self._btn_produits.style.color = COULEUR_FOND

    def set_ville(self, nom: str):
        """Met a jour le nom de la ville affichee."""
        self._label_ville.value = nom


def creer_nav_mobile(on_page_change) -> ft.NavigationBar:
    """Cree la barre de navigation mobile (bas de page)."""

    def _on_change(e):
        idx = e.control.selected_index
        on_page_change("accueil" if idx == 0 else "produits")

    return ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.ANALYTICS_OUTLINED,
                selected_icon=ft.Icons.ANALYTICS,
                label="Analyse",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.INVENTORY_2_OUTLINED,
                selected_icon=ft.Icons.INVENTORY_2,
                label="Mes Produits",
            ),
        ],
        on_change=_on_change,
        bgcolor=COULEUR_PANNEAU,
        indicator_color=COULEUR_ACCENT,
        selected_index=0,
    )
