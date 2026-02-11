"""
Layout pour plateforme Desktop.

Navigation horizontale en haut + contenu principal en dessous.
Optimisé pour grands écrans (1024px+).
"""

import flet as ft
from typing import Callable, Dict, Any

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE_HOVER,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE
)


class LayoutDesktop:
    """Layout desktop avec navigation horizontale."""

    def __init__(
        self,
        page: ft.Page,
        on_navigation: Callable[[str], None],
        nom_ville: str = "Paris"
    ):
        """
        Initialise le layout desktop.

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
        """Crée les éléments du layout."""
        # Boutons de navigation
        self.btn_accueil = ft.TextButton(
            "🏠 Analyse",
            on_click=lambda e: self._changer_page("accueil"),
            style=ft.ButtonStyle(color=COULEUR_ACCENT),
        )
        self.btn_produits = ft.TextButton(
            "🧴 Mes Produits",
            on_click=lambda e: self._changer_page("produits"),
            style=ft.ButtonStyle(color=COULEUR_TEXTE),
        )
        self.btn_historique = ft.TextButton(
            "📊 Historique",
            on_click=lambda e: self._changer_page("historique"),
            style=ft.ButtonStyle(color=COULEUR_TEXTE),
        )
        self.btn_profil = ft.TextButton(
            "👤 Profil",
            on_click=lambda e: self._changer_page("profil"),
            style=ft.ButtonStyle(color=COULEUR_TEXTE),
        )

        # Info ville
        self.label_ville = ft.Text(
            self.nom_ville,
            size=12,
            color=COULEUR_TEXTE_SECONDAIRE,
        )
        self.btn_ville = ft.TextButton(
            "Changer",
            on_click=lambda e: self._clic_changer_ville(),
            style=ft.ButtonStyle(
                bgcolor=COULEUR_CARTE_HOVER,
                color=COULEUR_TEXTE,
            ),
        )

        # Barre de navigation
        self.nav_bar = ft.Container(
            content=ft.Row([
                ft.Text(
                    "DermaLogic",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=COULEUR_TEXTE
                ),
                ft.Container(width=25),
                self.btn_accueil,
                self.btn_produits,
                self.btn_historique,
                self.btn_profil,
                ft.Container(expand=True),
                self.label_ville,
                self.btn_ville,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COULEUR_PANNEAU,
            height=55,
            padding=ft.padding.symmetric(horizontal=20),
        )

        # Conteneur de pages
        self.conteneur_pages = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # Layout principal
        self.layout = ft.Column([
            self.nav_bar,
            self.conteneur_pages,
        ], expand=True, spacing=0)

    def _changer_page(self, page_id: str):
        """Change la page active et met à jour les styles."""
        self.page_actuelle = page_id

        # Mettre à jour les couleurs des boutons
        boutons = {
            "accueil": self.btn_accueil,
            "produits": self.btn_produits,
            "historique": self.btn_historique,
            "profil": self.btn_profil,
        }

        for pid, btn in boutons.items():
            if pid == page_id:
                btn.style = ft.ButtonStyle(color=COULEUR_ACCENT)
            else:
                btn.style = ft.ButtonStyle(color=COULEUR_TEXTE)

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
        self.label_ville.value = nom_ville
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
