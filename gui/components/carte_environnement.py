"""
DermaLogic - Carte Environnement
=================================

Widget carte compacte pour afficher une donnee environnementale
(UV, humidite, PM2.5, temperature).
"""

import flet as ft
from gui.theme import COULEUR_CARTE, COULEUR_TEXTE_SECONDAIRE, COULEUR_ACCENT


class CarteEnvironnement(ft.Container):
    """Carte affichant un titre, une valeur et un niveau colore."""

    def __init__(self, titre: str):
        super().__init__()
        self._valeur = ft.Text("--", size=22, weight=ft.FontWeight.BOLD, color="#ffffff")
        self._niveau = ft.Text("", size=10, color=COULEUR_ACCENT)

        self.bgcolor = COULEUR_CARTE
        self.border_radius = 12
        self.padding = ft.Padding.symmetric(vertical=10, horizontal=8)
        self.expand = True
        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
            controls=[
                ft.Text(
                    titre,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=COULEUR_TEXTE_SECONDAIRE,
                ),
                self._valeur,
                self._niveau,
            ],
        )

    def mettre_a_jour(self, valeur: str, niveau: str = "", couleur: str = COULEUR_ACCENT):
        """Met a jour l'affichage de la carte."""
        self._valeur.value = valeur
        self._niveau.value = niveau
        self._niveau.color = couleur
