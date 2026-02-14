"""
DermaLogic - Formulaire d'ajout de produit
============================================

Dialogue modal pour ajouter un nouveau produit.
Peut etre pre-rempli avec des valeurs initiales (ex: depuis l'IA).
"""

import flet as ft
from gui.theme import COULEUR_ACCENT, COULEUR_FOND, COULEUR_DANGER, COULEUR_CARTE
from gui.data import GestionnaireProduits
from core.models import ProduitDerma, Categorie, MomentUtilisation, ActiveTag


class FormulaireProduit:
    """Gere le dialogue formulaire d'ajout/modification de produit."""

    def __init__(
        self,
        page: ft.Page,
        gestionnaire: GestionnaireProduits,
        callback,
        valeurs_initiales: dict = None,
        index_edition: int = None,
    ):
        self.page = page
        self.gestionnaire = gestionnaire
        self.callback = callback
        self.valeurs = valeurs_initiales or {}
        self.index_edition = index_edition
        self.mode_edition = index_edition is not None

        # Champs du formulaire
        self.entry_nom = ft.TextField(
            label="Nom",
            hint_text="Ex: Mon Serum Niacinamide",
            value=self.valeurs.get("nom", ""),
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )
        self.dropdown_cat = ft.Dropdown(
            label="Categorie",
            value=self.valeurs.get("category", "moisturizer"),
            options=[
                ft.dropdown.Option("cleanser", "Nettoyant"),
                ft.dropdown.Option("treatment", "Traitement"),
                ft.dropdown.Option("moisturizer", "Hydratant"),
                ft.dropdown.Option("protection", "Protection"),
            ],
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )
        self.dropdown_moment = ft.Dropdown(
            label="Moment d'utilisation",
            value=self.valeurs.get("moment", "tous"),
            options=[
                ft.dropdown.Option("matin", "Matin"),
                ft.dropdown.Option("journee", "Journee"),
                ft.dropdown.Option("soir", "Soir"),
                ft.dropdown.Option("tous", "Tous moments"),
            ],
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )
        self.switch_photo = ft.Switch(
            label="Photosensible (reagit aux UV)",
            value=self.valeurs.get("photosensitive", False),
            active_color=COULEUR_DANGER,
        )

        # Slider occlusivite
        occlu_val = self.valeurs.get("occlusivity", 3)
        self._label_occlu = ft.Text(str(occlu_val), weight=ft.FontWeight.BOLD, color="#ffffff")
        self.slider_occlu = ft.Slider(
            min=1,
            max=5,
            divisions=4,
            value=occlu_val,
            label="{value}",
            active_color=COULEUR_ACCENT,
            on_change=lambda e: self._on_slider_change(e, self._label_occlu),
        )

        # Slider pouvoir nettoyant
        clean_val = self.valeurs.get("cleansing_power", 3)
        self._label_clean = ft.Text(str(clean_val), weight=ft.FontWeight.BOLD, color="#ffffff")
        self.slider_clean = ft.Slider(
            min=1,
            max=5,
            divisions=4,
            value=clean_val,
            label="{value}",
            active_color="#00b4d8",
            on_change=lambda e: self._on_slider_change(e, self._label_clean),
        )

        self.dropdown_tag = ft.Dropdown(
            label="Action principale",
            value=self.valeurs.get("active_tag", "hydration"),
            options=[
                ft.dropdown.Option("hydration", "Hydratation"),
                ft.dropdown.Option("acne", "Anti-acne"),
                ft.dropdown.Option("repair", "Reparation"),
            ],
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )

        # Titre
        if self.mode_edition:
            titre = "Modifier le Produit"
        elif valeurs_initiales:
            titre = "Nouveau Produit (IA)"
        else:
            titre = "Nouveau Produit"

        sous_titre_controls = []
        if valeurs_initiales and not self.mode_edition:
            sous_titre_controls.append(
                ft.Text(
                    "Verifie les informations avant d'ajouter",
                    size=11,
                    color="#9b59b6",
                )
            )

        # Construction du dialogue
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(titre, size=20, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    *sous_titre_controls,
                ],
            ),
            content=ft.Container(
                width=400,
                height=500,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                    controls=[
                        self.entry_nom,
                        self.dropdown_cat,
                        self.dropdown_moment,
                        self.switch_photo,
                        ft.Text("Occlusivite (1=leger, 5=riche)", size=12, color="#ffffff"),
                        ft.Row([self.slider_occlu, self._label_occlu]),
                        ft.Text("Pouvoir nettoyant (1=doux, 5=fort)", size=12, color="#ffffff"),
                        ft.Row([self.slider_clean, self._label_clean]),
                        self.dropdown_tag,
                    ],
                ),
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=self._fermer,
                    style=ft.ButtonStyle(color=COULEUR_DANGER),
                ),
                ft.Button(
                    "Modifier" if self.mode_edition else "Ajouter",
                    on_click=self._valider,
                    bgcolor=COULEUR_ACCENT,
                    color=COULEUR_FOND,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _on_slider_change(self, e, label: ft.Text):
        label.value = str(int(e.control.value))
        self.page.update()

    def ouvrir(self):
        """Ouvre le dialogue."""
        self.page.show_dialog(self.dialog)

    def _fermer(self, e=None):
        """Ferme le dialogue."""
        self.page.pop_dialog()

    def _valider(self, e):
        """Valide et ajoute ou modifie le produit."""
        nom = self.entry_nom.value.strip() if self.entry_nom.value else ""
        if not nom:
            self.entry_nom.error_text = "Entrez un nom"
            self.page.update()
            return

        try:
            produit = ProduitDerma(
                nom=nom,
                category=Categorie(self.dropdown_cat.value),
                moment=MomentUtilisation(self.dropdown_moment.value),
                photosensitive=self.switch_photo.value,
                occlusivity=int(self.slider_occlu.value),
                cleansing_power=int(self.slider_clean.value),
                active_tag=ActiveTag(self.dropdown_tag.value),
            )
            if self.mode_edition:
                self.gestionnaire.modifier(self.index_edition, produit)
            else:
                self.gestionnaire.ajouter(produit)
            self._fermer()
            self.callback()
        except Exception as ex:
            self.entry_nom.error_text = str(ex)
            self.page.update()
