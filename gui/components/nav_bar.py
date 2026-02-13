"""
DermaLogic - Barres de navigation
==================================

Navigation desktop (top bar) et mobile (bottom navigation bar).
5 pages : Analyse, Produits, Profil, Historique, Parametres.
"""

import flet as ft
from gui.theme import (
    COULEUR_PANNEAU,
    COULEUR_CARTE_HOVER,
    COULEUR_ACCENT,
    COULEUR_FOND,
    COULEUR_TEXTE_SECONDAIRE,
)

# Mapping nom de page -> index pour la nav mobile
PAGES_INDEX = {
    "accueil": 0,
    "produits": 1,
    "profil": 2,
    "historique": 3,
    "parametres": 4,
}

INDEX_PAGES = {v: k for k, v in PAGES_INDEX.items()}


class NavBarDesktop(ft.Container):
    """Barre de navigation desktop (haut de page)."""

    def __init__(self, on_page_change, on_ville_click, nom_ville: str):
        super().__init__()
        self._on_page_change = on_page_change

        # Boutons de navigation
        self._btn_accueil = self._creer_bouton("Analyse", "accueil", actif=True)
        self._btn_produits = self._creer_bouton("Produits", "produits")
        self._btn_profil = self._creer_bouton("Profil", "profil")
        self._btn_historique = self._creer_bouton("Historique", "historique")
        self._btn_parametres = ft.IconButton(
            ft.Icons.SETTINGS,
            icon_color=COULEUR_TEXTE_SECONDAIRE,
            icon_size=20,
            on_click=lambda e: on_page_change("parametres"),
            tooltip="Parametres",
        )

        self._boutons = {
            "accueil": self._btn_accueil,
            "produits": self._btn_produits,
            "profil": self._btn_profil,
            "historique": self._btn_historique,
        }

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
                ft.Container(width=5),
                self._btn_profil,
                ft.Container(width=5),
                self._btn_historique,
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
                ft.Container(width=10),
                self._btn_parametres,
            ],
        )

    def _creer_bouton(self, label: str, page_name: str, actif: bool = False) -> ft.TextButton:
        """Cree un bouton de navigation."""
        return ft.TextButton(
            label,
            on_click=lambda e: self._on_page_change(page_name),
            style=ft.ButtonStyle(
                color=COULEUR_FOND if actif else "#ffffff",
                bgcolor=COULEUR_ACCENT if actif else "transparent",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            ),
        )

    def set_active(self, page_name: str):
        """Met a jour le bouton actif."""
        for nom, btn in self._boutons.items():
            if nom == page_name:
                btn.style.bgcolor = COULEUR_ACCENT
                btn.style.color = COULEUR_FOND
            else:
                btn.style.bgcolor = "transparent"
                btn.style.color = "#ffffff"

        # Icone parametres
        if page_name == "parametres":
            self._btn_parametres.icon_color = COULEUR_ACCENT
        else:
            self._btn_parametres.icon_color = COULEUR_TEXTE_SECONDAIRE

    def set_ville(self, nom: str):
        """Met a jour le nom de la ville affichee."""
        self._label_ville.value = nom


def creer_nav_mobile(on_page_change) -> ft.NavigationBar:
    """Cree la barre de navigation mobile (bas de page)."""

    def _on_change(e):
        idx = e.control.selected_index
        page_name = INDEX_PAGES.get(idx, "accueil")
        on_page_change(page_name)

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
                label="Produits",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_OUTLINED,
                selected_icon=ft.Icons.PERSON,
                label="Profil",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.HISTORY_OUTLINED,
                selected_icon=ft.Icons.HISTORY,
                label="Historique",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Parametres",
            ),
        ],
        on_change=_on_change,
        bgcolor=COULEUR_PANNEAU,
        indicator_color=COULEUR_ACCENT,
        selected_index=0,
    )
