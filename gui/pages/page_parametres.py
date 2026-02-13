"""
DermaLogic - Page Parametres
==============================

Page de gestion des parametres :
- Cle API Gemini (saisie, sauvegarde, test)
- Export des donnees en JSON
"""

import json
import threading
import flet as ft
from gui.theme import (
    COULEUR_ACCENT,
    COULEUR_FOND,
    COULEUR_DANGER,
    COULEUR_PANNEAU,
    COULEUR_CARTE,
    COULEUR_TEXTE_SECONDAIRE,
)


class PageParametres(ft.Column):
    """Page de gestion des parametres de l'application."""

    def __init__(self, page: ft.Page, gestionnaire_settings, on_cle_changee=None, exporter_callback=None):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.page_ref = page
        self.settings = gestionnaire_settings
        self.on_cle_changee = on_cle_changee
        self.exporter_callback = exporter_callback

        # --- Section Cle API ---
        cle_actuelle = self.settings.obtenir_gemini_key()

        self.entry_cle = ft.TextField(
            value=cle_actuelle,
            label="Cle API Gemini",
            hint_text="Collez votre cle API Google Gemini ici",
            password=True,
            can_reveal_password=True,
            text_size=14,
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )

        self.label_statut = ft.Text(
            "Connecte" if cle_actuelle else "Non configure",
            size=12,
            color=COULEUR_ACCENT if cle_actuelle else COULEUR_DANGER,
            weight=ft.FontWeight.BOLD,
        )

        self.btn_sauvegarder = ft.Button(
            "Sauvegarder",
            on_click=self._sauvegarder_cle,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=36,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

        self.btn_tester = ft.Button(
            "Tester la connexion",
            on_click=self._tester_cle,
            bgcolor=COULEUR_CARTE,
            color="#ffffff",
            height=36,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

        self.label_test = ft.Text("", size=11, color=COULEUR_TEXTE_SECONDAIRE)

        # --- Section Export ---
        self.btn_exporter = ft.Button(
            "Exporter en JSON",
            on_click=self._exporter_json,
            bgcolor=COULEUR_CARTE,
            color="#ffffff",
            height=36,
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

        self.label_export = ft.Text("", size=11, color=COULEUR_TEXTE_SECONDAIRE)

        # --- Construction de la page ---
        self.controls = [
            # Titre
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=15, bottom=10),
                content=ft.Text(
                    "Parametres",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#ffffff",
                ),
            ),
            # Section Cle API
            ft.Container(
                bgcolor=COULEUR_PANNEAU,
                border_radius=15,
                margin=ft.Margin.symmetric(horizontal=20),
                padding=20,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.KEY, color=COULEUR_ACCENT, size=20),
                                ft.Container(width=8),
                                ft.Text(
                                    "Cle API Gemini",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color="#ffffff",
                                ),
                                ft.Container(expand=True),
                                self.label_statut,
                            ],
                        ),
                        ft.Text(
                            "Entrez votre cle API Google Gemini pour utiliser l'analyse IA.\n"
                            "Obtenez-la sur aistudio.google.com",
                            size=12,
                            color=COULEUR_TEXTE_SECONDAIRE,
                        ),
                        self.entry_cle,
                        ft.Row(
                            controls=[
                                self.btn_sauvegarder,
                                ft.Container(width=10),
                                self.btn_tester,
                            ],
                        ),
                        self.label_test,
                    ],
                ),
            ),
            # Section Export
            ft.Container(
                bgcolor=COULEUR_PANNEAU,
                border_radius=15,
                margin=ft.Margin.only(left=20, right=20, top=15),
                padding=20,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SAVE_ALT, color=COULEUR_ACCENT, size=20),
                                ft.Container(width=8),
                                ft.Text(
                                    "Exporter mes donnees",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color="#ffffff",
                                ),
                            ],
                        ),
                        ft.Text(
                            "Exportez toutes vos donnees (profil, produits, historique)\n"
                            "au format JSON pour sauvegarde ou migration.",
                            size=12,
                            color=COULEUR_TEXTE_SECONDAIRE,
                        ),
                        self.btn_exporter,
                        self.label_export,
                    ],
                ),
            ),
        ]

    def _sauvegarder_cle(self, e=None):
        """Sauvegarde la cle API."""
        cle = self.entry_cle.value.strip() if self.entry_cle.value else ""
        self.settings.definir_gemini_key(cle)

        if cle:
            self.label_statut.value = "Connecte"
            self.label_statut.color = COULEUR_ACCENT
            self.label_test.value = "Cle sauvegardee avec succes"
            self.label_test.color = COULEUR_ACCENT
        else:
            self.label_statut.value = "Non configure"
            self.label_statut.color = COULEUR_DANGER
            self.label_test.value = "Cle supprimee"
            self.label_test.color = COULEUR_TEXTE_SECONDAIRE

        if self.on_cle_changee:
            self.on_cle_changee()

        self.page_ref.update()

    def _tester_cle(self, e=None):
        """Teste la connexion a Gemini (threade)."""
        cle = self.entry_cle.value.strip() if self.entry_cle.value else ""
        if not cle:
            self.label_test.value = "Entrez une cle API d'abord"
            self.label_test.color = COULEUR_DANGER
            self.page_ref.update()
            return

        self.btn_tester.disabled = True
        self.btn_tester.text = "Test en cours..."
        self.label_test.value = "Connexion a Gemini..."
        self.label_test.color = COULEUR_TEXTE_SECONDAIRE
        self.page_ref.update()

        def _background():
            from api.gemini import ClientGemini
            client = ClientGemini(api_key=cle)
            reponse = client.generer("Reponds uniquement: OK")

            if reponse:
                self.label_test.value = "Connexion reussie !"
                self.label_test.color = COULEUR_ACCENT
            else:
                self.label_test.value = "Echec de connexion. Verifiez votre cle API."
                self.label_test.color = COULEUR_DANGER

            self.btn_tester.disabled = False
            self.btn_tester.text = "Tester la connexion"
            self.page_ref.update()

        threading.Thread(target=_background, daemon=True).start()

    def _exporter_json(self, e=None):
        """Exporte les donnees en JSON dans user_data/."""
        if not self.exporter_callback:
            self.label_export.value = "Fonction d'export non configuree"
            self.label_export.color = COULEUR_DANGER
            self.page_ref.update()
            return

        try:
            import os
            from datetime import datetime

            data = self.exporter_callback()
            os.makedirs("user_data", exist_ok=True)
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            chemin = os.path.join("user_data", f"dermalogic_export_{horodatage}.json")

            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.label_export.value = f"Exporte : {chemin}"
            self.label_export.color = COULEUR_ACCENT
        except Exception as ex:
            self.label_export.value = f"Erreur: {str(ex)[:80]}"
            self.label_export.color = COULEUR_DANGER

        self.page_ref.update()
