"""
DermaLogic - Formulaire Produit (Flet)
=======================================

Dialogue d'ajout/modification d'un produit.
"""

import flet as ft

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_DANGER, COULEUR_BORDURE,
)
from gui.gestionnaire_produits import GestionnaireProduits
from core.algorithme import ProduitDerma, Categorie, ActiveTag, MomentUtilisation


def ouvrir_formulaire_produit(page: ft.Page, gestionnaire: GestionnaireProduits, callback, valeurs: dict = None):
    """
    Ouvre un bottom-sheet / AlertDialog pour ajouter un produit.

    Args:
        page: Page Flet
        gestionnaire: Gestionnaire de produits
        callback: Fonction à appeler après ajout
        valeurs: Valeurs initiales (pré-remplissage IA)
    """
    valeurs = valeurs or {}
    est_modification = bool(valeurs)

    # Champs
    entry_nom = ft.TextField(
        hint_text="Ex: Mon Sérum Niacinamide",
        value=valeurs.get("nom", ""),
        bgcolor=COULEUR_CARTE, border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE, height=42,
    )

    combo_cat = ft.Dropdown(
        value=valeurs.get("category", "moisturizer"),
        options=[
            ft.dropdown.Option("cleanser", "Nettoyant"),
            ft.dropdown.Option("treatment", "Traitement"),
            ft.dropdown.Option("moisturizer", "Hydratant"),
            ft.dropdown.Option("protection", "Protection"),
        ],
        bgcolor=COULEUR_CARTE, border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE, height=42,
    )

    combo_moment = ft.Dropdown(
        value=valeurs.get("moment", "tous"),
        options=[
            ft.dropdown.Option("matin", "Matin"),
            ft.dropdown.Option("journee", "Journée"),
            ft.dropdown.Option("soir", "Soir"),
            ft.dropdown.Option("tous", "Tous moments"),
        ],
        bgcolor=COULEUR_CARTE, border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE, height=42,
    )

    var_photo = ft.Checkbox(
        label="Photosensible (réagit aux UV : BHA, Retinol...)",
        value=valeurs.get("photosensitive", False),
        fill_color=COULEUR_DANGER,
    )

    lbl_occlu = ft.Text(str(valeurs.get("occlusivity", 3)), size=13, weight=ft.FontWeight.BOLD, color=COULEUR_ACCENT)
    slider_occlu = ft.Slider(
        min=1, max=5, divisions=4,
        value=valeurs.get("occlusivity", 3),
        active_color=COULEUR_ACCENT,
        inactive_color=COULEUR_CARTE,
        on_change=lambda e: setattr(lbl_occlu, "value", str(int(e.control.value))) or page.update(),
    )

    lbl_clean = ft.Text(str(valeurs.get("cleansing_power", 3)), size=13, weight=ft.FontWeight.BOLD, color="#00b4d8")
    slider_clean = ft.Slider(
        min=1, max=5, divisions=4,
        value=valeurs.get("cleansing_power", 3),
        active_color="#00b4d8",
        inactive_color=COULEUR_CARTE,
        on_change=lambda e: setattr(lbl_clean, "value", str(int(e.control.value))) or page.update(),
    )

    combo_tag = ft.Dropdown(
        value=valeurs.get("active_tag", "hydration"),
        options=[
            ft.dropdown.Option("hydration", "Hydratation"),
            ft.dropdown.Option("acne", "Anti-acné"),
            ft.dropdown.Option("repair", "Réparation"),
        ],
        bgcolor=COULEUR_CARTE, border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE, height=42,
    )

    label_status = ft.Text("", size=11, color=COULEUR_DANGER)

    def _valider(e):
        nom = entry_nom.value.strip()
        if not nom:
            label_status.value = "Entrez un nom"
            page.update()
            return

        try:
            produit = ProduitDerma(
                nom=nom,
                category=Categorie(combo_cat.value),
                moment=MomentUtilisation(combo_moment.value),
                photosensitive=var_photo.value,
                occlusivity=int(slider_occlu.value),
                cleansing_power=int(slider_clean.value),
                active_tag=ActiveTag(combo_tag.value),
            )
            gestionnaire.ajouter(produit)
            page.close(dlg)
            callback()
        except Exception as ex:
            label_status.value = str(ex)
            page.update()

    def _annuler(e):
        page.close(dlg)

    titre = "Modifier le produit" if est_modification else "Ajouter un produit"
    sous_titre_text = "Vérifie les informations avant d'ajouter" if est_modification else ""

    contenu = ft.Column(
        [
            ft.Text(titre, size=20, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
            ft.Text(sous_titre_text, size=11, color="#9b59b6") if sous_titre_text else ft.Container(),
            ft.Text("Nom", size=12, color=COULEUR_TEXTE),
            entry_nom,
            ft.Text("Catégorie", size=12, color=COULEUR_TEXTE),
            combo_cat,
            ft.Text("Moment d'utilisation", size=12, color=COULEUR_TEXTE),
            combo_moment,
            var_photo,
            ft.Row([ft.Text("Occlusivité (1=léger, 5=riche)", size=12, color=COULEUR_TEXTE), ft.Container(expand=True), lbl_occlu]),
            slider_occlu,
            ft.Row([ft.Text("Pouvoir nettoyant (1=doux, 5=fort)", size=12, color=COULEUR_TEXTE), ft.Container(expand=True), lbl_clean]),
            slider_clean,
            ft.Text("Action principale", size=12, color=COULEUR_TEXTE),
            combo_tag,
            label_status,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=6,
        width=420,
        height=500,
    )

    dlg = ft.AlertDialog(
        title=ft.Text(""),
        content=contenu,
        actions=[
            ft.TextButton("Annuler", on_click=_annuler),
            ft.ElevatedButton(
                "Ajouter", on_click=_valider,
                bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
            ),
        ],
        bgcolor=COULEUR_FOND,
    )

    page.open(dlg)
