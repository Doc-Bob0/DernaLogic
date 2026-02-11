"""
Layout pour plateforme Mobile.

Bottom navigation bar + contenu principal optimisé tactile.
Support du swipe entre pages et interface adaptée aux petits écrans.
"""

import flet as ft
from typing import Callable, Dict, Any

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE
)


class LayoutMobile:
    """Layout mobile avec bottom navigation bar."""

    def __init__(
        self,
        page: ft.Page,
        on_navigation: Callable[[str], None],
        nom_ville: str = "Paris"
    ):
        """
        Initialise le layout mobile.

        Args:
            page: Page Flet
            on_navigation: Callback appelé lors du changement de page (page_id)
            nom_ville: Nom de la ville actuelle
        """
        self.page = page
        self.on_navigation = on_navigation
        self.nom_ville = nom_ville
        self.page_actuelle = "accueil"

        # Conteneurs pour callbacks externes
        self.on_changer_ville: Callable = None

        # Créer les éléments
        self._creer_elements()

    def _creer_elements(self):
        """Crée les éléments du layout mobile."""
        # Header mobile compact
        self.header = ft.Container(
            content=ft.Row([
                ft.Text(
                    "DermaLogic",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=COULEUR_TEXTE
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.LOCATION_ON_OUTLINED,
                    icon_color=COULEUR_ACCENT,
                    on_click=lambda e: self._clic_changer_ville(),
                    tooltip=self.nom_ville,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COULEUR_PANNEAU,
            height=56,  # Material Design standard app bar height
            padding=ft.padding.symmetric(horizontal=16),
        )

        # Conteneur de pages avec swipe support
        self.conteneur_pages = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # Bottom Navigation Bar (Material Design)
        self.bottom_nav = ft.NavigationBar(
            selected_index=0,
            on_change=self._navigation_changee,
            bgcolor=COULEUR_PANNEAU,
            indicator_color=COULEUR_ACCENT,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Routine",
                ),
                ft.NavigationBarDestination(
                    icon=ft.icons.SHOPPING_BAG_OUTLINED,
                    selected_icon=ft.icons.SHOPPING_BAG,
                    label="Produits",
                ),
                ft.NavigationBarDestination(
                    icon=ft.icons.HISTORY,
                    selected_icon=ft.icons.HISTORY,
                    label="Historique",
                ),
                ft.NavigationBarDestination(
                    icon=ft.icons.PERSON_OUTLINE,
                    selected_icon=ft.icons.PERSON,
                    label="Profil",
                ),
            ],
        )

        # Layout principal
        self.layout = ft.Column([
            self.header,
            self.conteneur_pages,
            self.bottom_nav,
        ], expand=True, spacing=0)

    def _navigation_changee(self, e):
        """Callback quand la navigation change."""
        index = e.control.selected_index

        # Mapper l'index à l'ID de page
        pages = ["accueil", "produits", "historique", "profil"]
        if 0 <= index < len(pages):
            self._changer_page(pages[index])

    def _changer_page(self, page_id: str):
        """Change la page active."""
        self.page_actuelle = page_id

        # Mettre à jour l'index de la bottom nav
        pages = ["accueil", "produits", "historique", "profil"]
        if page_id in pages:
            self.bottom_nav.selected_index = pages.index(page_id)

        # Appeler le callback de navigation
        if self.on_navigation:
            self.on_navigation(page_id)

        self.page.update()

    def _clic_changer_ville(self):
        """Callback pour le changement de ville."""
        if self.on_changer_ville:
            self.on_changer_ville()

    def definir_contenu(self, contenu: ft.Control):
        """
        Définit le contenu principal à afficher.

        Args:
            contenu: Contrôle Flet à afficher dans la zone de contenu
        """
        self.conteneur_pages.controls = [contenu]
        self.page.update()

    def mettre_a_jour_ville(self, nom_ville: str):
        """
        Met à jour le nom de la ville affichée.

        Args:
            nom_ville: Nouveau nom de ville
        """
        self.nom_ville = nom_ville
        # Mettre à jour le tooltip du bouton localisation
        if hasattr(self.header.content, 'controls'):
            for control in self.header.content.controls:
                if isinstance(control, ft.IconButton):
                    control.tooltip = nom_ville
        self.page.update()

    def obtenir_layout(self) -> ft.Control:
        """
        Retourne le layout complet.

        Returns:
            Control Flet contenant tout le layout
        """
        return self.layout

    def configurer_callbacks(self, callbacks: Dict[str, Callable]):
        """
        Configure les callbacks externes.

        Args:
            callbacks: Dictionnaire de callbacks
                - "changer_ville": Callback pour changer de ville
        """
        self.on_changer_ville = callbacks.get("changer_ville")

    def afficher_snackbar(self, message: str, couleur: str = None):
        """
        Affiche un snackbar mobile pour les notifications rapides.

        Args:
            message: Message à afficher
            couleur: Couleur de fond du snackbar
        """
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=couleur if couleur else COULEUR_CARTE,
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()
