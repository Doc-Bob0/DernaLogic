"""
DermaLogic - Fenêtre Analyse IA Personnalisée (Flet)
======================================================

Dialogue pour entrer des instructions personnalisées pour l'IA.
"""

import flet as ft

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_IA, COULEUR_BORDURE,
)


def ouvrir_analyse_ia_dialog(page: ft.Page, callback):
    """
    Ouvre un dialogue pour entrer les instructions personnalisées IA.

    Args:
        page: Page Flet
        callback: Fonction à appeler avec les instructions (str)
    """
    txt_instructions = ft.TextField(
        multiline=True, min_lines=3, max_lines=5,
        bgcolor=COULEUR_CARTE,
        border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE,
        hint_text="Ex: J'ai un rendez-vous important ce soir, ma peau est un peu irritée...",
    )

    label_status = ft.Text("", size=11, color=COULEUR_TEXTE_SECONDAIRE)

    elements = [
        "✓ Votre profil (type de peau, problèmes)",
        "✓ Conditions météo actuelles (UV, humidité, pollution)",
        "✓ Votre niveau de stress du jour",
        "✓ Vos produits enregistrés",
    ]

    def lancer(e):
        instructions = txt_instructions.value or ""
        page.close(dlg)
        callback(instructions)

    contenu = ft.Column([
        ft.Text("🤖 Analyse IA personnalisée", size=20, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
        ft.Text("L'IA analysera vos produits en tenant compte de :", size=12, color=COULEUR_TEXTE_SECONDAIRE),
        ft.Container(
            content=ft.Column(
                [ft.Text(e, size=11, color=COULEUR_TEXTE) for e in elements],
                spacing=4,
            ),
            bgcolor=COULEUR_PANNEAU, border_radius=10,
            padding=ft.padding.all(12),
        ),
        ft.Text("Instructions personnalisées (optionnel) :", size=13, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
        txt_instructions,
        label_status,
    ], spacing=10, width=500, height=380)

    dlg = ft.AlertDialog(
        title=ft.Text(""),
        content=contenu,
        actions=[
            ft.TextButton("Annuler", on_click=lambda e: page.close(dlg)),
            ft.ElevatedButton(
                "🚀 Lancer l'analyse",
                on_click=lancer,
                bgcolor=COULEUR_IA, color=COULEUR_TEXTE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                ),
            ),
        ],
        bgcolor=COULEUR_FOND,
    )

    page.open(dlg)
