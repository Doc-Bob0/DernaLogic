"""
DermaLogic - Fenetre de recherche IA
======================================

Dialogue pour rechercher et analyser un produit avec l'IA Gemini.
L'IA analyse le produit et pre-remplit le formulaire d'ajout.
"""

import threading
import flet as ft
from gui.theme import (
    COULEUR_ACCENT,
    COULEUR_FOND,
    COULEUR_DANGER,
    COULEUR_CARTE,
    COULEUR_PANNEAU,
    COULEUR_TEXTE_SECONDAIRE,
)
from gui.data import GestionnaireProduits
from gui.dialogs.formulaire_produit import FormulaireProduit
from api.gemini import ClientGemini


class FenetreRechercheIA:
    """Gere le dialogue de recherche IA."""

    def __init__(self, page: ft.Page, gestionnaire: GestionnaireProduits, callback, api_key: str = ""):
        self.page = page
        self.gestionnaire = gestionnaire
        self.callback = callback
        self.client_gemini = ClientGemini(api_key=api_key)

        self.entry_produit = ft.TextField(
            hint_text="Ex: CeraVe Creme Hydratante, Paula's Choice BHA...",
            label="Nom du produit",
            height=50,
            text_size=14,
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
            on_submit=self._analyser,
        )

        self.label_status = ft.Text("", size=11, color=COULEUR_TEXTE_SECONDAIRE)

        self.btn_analyser = ft.Button(
            "Analyser avec l'IA",
            on_click=self._analyser,
            bgcolor="#9b59b6",
            color="#ffffff",
            height=40,
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Analyse par IA", size=22, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Text(
                        "L'IA va analyser le produit et remplir automatiquement\n"
                        "les caracteristiques. Tu pourras les modifier ensuite.",
                        size=12,
                        color=COULEUR_TEXTE_SECONDAIRE,
                    ),
                ],
            ),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Container(
                            bgcolor=COULEUR_PANNEAU,
                            border_radius=12,
                            padding=15,
                            content=self.entry_produit,
                        ),
                        self.label_status,
                    ],
                ),
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=self._fermer,
                    style=ft.ButtonStyle(color=COULEUR_TEXTE_SECONDAIRE),
                ),
                self.btn_analyser,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def ouvrir(self):
        """Ouvre le dialogue."""
        self.page.show_dialog(self.dialog)

    def _fermer(self, e=None):
        """Ferme le dialogue."""
        self.page.pop_dialog()

    def _analyser(self, e=None):
        """Lance l'analyse du produit par l'IA (threade)."""
        nom_produit = self.entry_produit.value.strip() if self.entry_produit.value else ""

        if not nom_produit:
            self.label_status.value = "Entre le nom d'un produit"
            self.label_status.color = COULEUR_DANGER
            self.page.update()
            return

        # Etat de chargement
        self.btn_analyser.disabled = True
        self.btn_analyser.text = "Analyse en cours..."
        self.label_status.value = "Analyse IA en cours (~5-10s)..."
        self.label_status.color = COULEUR_TEXTE_SECONDAIRE
        self.page.update()

        def _background():
            try:
                resultat = self.client_gemini.analyser_produit(nom_produit)

                if resultat.succes:
                    # Fermer ce dialogue
                    self.page.pop_dialog()

                    # Ouvrir le formulaire pre-rempli
                    valeurs = {
                        "nom": resultat.nom,
                        "category": resultat.category,
                        "moment": resultat.moment,
                        "photosensitive": resultat.photosensitive,
                        "occlusivity": resultat.occlusivity,
                        "cleansing_power": resultat.cleansing_power,
                        "active_tag": resultat.active_tag,
                    }
                    form = FormulaireProduit(
                        self.page,
                        self.gestionnaire,
                        self.callback,
                        valeurs_initiales=valeurs,
                    )
                    form.ouvrir()
                else:
                    self.label_status.value = f"Erreur: {resultat.erreur[:100]}"
                    self.label_status.color = COULEUR_DANGER
                    self.btn_analyser.disabled = False
                    self.btn_analyser.text = "Reessayer"
                    self.page.update()

            except Exception as ex:
                self.label_status.value = f"Erreur: {str(ex)[:100]}"
                self.label_status.color = COULEUR_DANGER
                self.btn_analyser.disabled = False
                self.btn_analyser.text = "Reessayer"
                self.page.update()

        threading.Thread(target=_background, daemon=True).start()
