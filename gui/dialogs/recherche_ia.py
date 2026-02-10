"""
DermaLogic - Fenêtre de Recherche IA (Flet)
=============================================

Dialogue pour rechercher et analyser un produit avec Gemini.
"""

import flet as ft
import threading

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_DANGER, COULEUR_IA, COULEUR_IA_HOVER, COULEUR_BORDURE,
)
from gui.gestionnaire_produits import GestionnaireProduits
from api.gemini import ClientGemini


def ouvrir_recherche_ia(page: ft.Page, gestionnaire: GestionnaireProduits, callback):
    """
    Ouvre un dialogue pour rechercher un produit via l'IA Gemini.

    Args:
        page: Page Flet
        gestionnaire: Gestionnaire de produits
        callback: Fonction à appeler après analyse réussie (reçoit un dict de valeurs)
    """
    client_gemini = ClientGemini()

    entry_produit = ft.TextField(
        hint_text="Ex: CeraVe Crème Hydratante...",
        bgcolor=COULEUR_CARTE, border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE, height=45,
        text_size=14,
        on_submit=lambda e: _analyser(e),
    )

    label_status = ft.Text("", size=11, color=COULEUR_TEXTE_SECONDAIRE)

    btn_analyser = ft.ElevatedButton(
        "Analyser avec l'IA",
        bgcolor=COULEUR_IA, color=COULEUR_TEXTE,
        width=180,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        ),
    )

    def _analyser(e):
        nom_produit = entry_produit.value.strip()
        if not nom_produit:
            label_status.value = "Entre le nom d'un produit"
            label_status.color = COULEUR_DANGER
            page.update()
            return

        btn_analyser.text = "Analyse en cours..."
        btn_analyser.disabled = True
        label_status.value = "Connexion à Gemini..."
        label_status.color = COULEUR_TEXTE_SECONDAIRE
        page.update()

        def _run():
            try:
                resultat = client_gemini.analyser_produit(nom_produit)
                if resultat.succes:
                    valeurs = {
                        "nom": resultat.nom,
                        "category": resultat.category,
                        "moment": resultat.moment,
                        "photosensitive": resultat.photosensitive,
                        "occlusivity": resultat.occlusivity,
                        "cleansing_power": resultat.cleansing_power,
                        "active_tag": resultat.active_tag,
                    }
                    page.close(dlg)
                    callback(valeurs)
                else:
                    label_status.value = f"Erreur: {resultat.erreur[:100]}"
                    label_status.color = COULEUR_DANGER
                    btn_analyser.text = "Réessayer"
                    btn_analyser.disabled = False
            except Exception as ex:
                label_status.value = f"Erreur: {str(ex)[:100]}"
                label_status.color = COULEUR_DANGER
                btn_analyser.text = "Réessayer"
                btn_analyser.disabled = False
            page.update()

        threading.Thread(target=_run, daemon=True).start()

    btn_analyser.on_click = _analyser

    contenu = ft.Column(
        [
            ft.Text("🤖 Analyse par IA", size=22, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE,
                     text_align=ft.TextAlign.CENTER),
            ft.Text(
                "L'IA va analyser le produit et remplir automatiquement\nles caractéristiques. Tu pourras les modifier ensuite.",
                size=12, color=COULEUR_TEXTE_SECONDAIRE, text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Nom du produit", size=13, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    entry_produit,
                ], spacing=8),
                bgcolor=COULEUR_PANNEAU, border_radius=12,
                padding=ft.padding.all(15),
            ),
            label_status,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        width=450,
    )

    dlg = ft.AlertDialog(
        title=ft.Text(""),
        content=contenu,
        actions=[
            ft.TextButton("Annuler", on_click=lambda e: page.close(dlg)),
            btn_analyser,
        ],
        bgcolor=COULEUR_FOND,
    )

    page.open(dlg)
