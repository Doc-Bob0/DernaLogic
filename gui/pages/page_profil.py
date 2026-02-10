"""
DermaLogic - Page Profil
=========================

Page de gestion du profil utilisateur.
"""

import flet as ft

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE, COULEUR_ACCENT,
    COULEUR_ACCENT_HOVER, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_DANGER, COULEUR_BORDURE, couleur_stress,
)
from core.profil import TypePeau, GestionnaireProfil


class PageProfil(ft.Column):
    """
    Page de gestion du profil utilisateur.
    
    Sections :
    - Type de peau (radio)
    - Problèmes de peau (checkboxes)
    - Notes permanentes (textarea)
    - État quotidien (slider stress, champ état du jour)
    """

    def __init__(self, gestionnaire_profil: GestionnaireProfil):
        self.gestionnaire = gestionnaire_profil

        # Contenu scrollable
        self.scroll_col = ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=12, expand=True,
        )

        header = ft.Text(
            "👤 Mon Profil", size=24,
            weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE,
        )

        super().__init__(
            controls=[header, self.scroll_col],
            spacing=15,
            expand=True,
        )

        self._construire()

    def _construire(self):
        self.scroll_col.controls.clear()
        self._creer_section_type_peau()
        self._creer_section_problemes()
        self._creer_section_notes()
        self._creer_section_quotidien()

    # ─── TYPE DE PEAU ───

    def _creer_section_type_peau(self):
        types = [
            ("normale", "Normale"),
            ("seche", "Sèche"),
            ("grasse", "Grasse"),
            ("mixte", "Mixte"),
            ("sensible", "Sensible"),
        ]

        current = self.gestionnaire.profil.type_peau.value
        self._radio_type_peau = ft.RadioGroup(
            value=current,
            on_change=self._on_type_peau_change,
            content=ft.Row(
                [ft.Radio(value=v, label=l, fill_color=COULEUR_ACCENT) for v, l in types],
                spacing=15, wrap=True,
            ),
        )

        self.scroll_col.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("🧬 Type de peau", size=16, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Text("Sélectionnez votre type de peau (sauvegardé)", size=11, color=COULEUR_TEXTE_SECONDAIRE),
                    self._radio_type_peau,
                ], spacing=8),
                bgcolor=COULEUR_PANNEAU, border_radius=12,
                padding=ft.padding.all(15),
            )
        )

    def _on_type_peau_change(self, e):
        type_peau = TypePeau.from_str(e.control.value)
        self.gestionnaire.modifier_type_peau(type_peau)

    # ─── PROBLÈMES DE PEAU ───

    def _creer_section_problemes(self):
        problemes = [
            ("acne", "Acné"), ("eczema", "Eczéma"),
            ("rosacee", "Rosacée"), ("psoriasis", "Psoriasis"),
            ("hyperpigmentation", "Hyperpigmentation"),
            ("rides", "Rides / Ridules"),
            ("pores_dilates", "Pores dilatés"),
            ("deshydratation", "Déshydratation"),
            ("taches", "Taches pigmentaires"),
            ("rougeurs", "Rougeurs"),
        ]

        self._checkboxes_problemes = {}
        rows = []
        row_items = []
        for i, (valeur, label) in enumerate(problemes):
            checked = valeur in self.gestionnaire.profil.problemes
            cb = ft.Checkbox(
                label=label, value=checked,
                fill_color=COULEUR_ACCENT,
                on_change=lambda e, v=valeur: self._on_probleme_change(v, e),
            )
            self._checkboxes_problemes[valeur] = cb
            row_items.append(ft.Container(content=cb, width=180))
            if (i + 1) % 3 == 0:
                rows.append(ft.Row(row_items, spacing=5))
                row_items = []
        if row_items:
            rows.append(ft.Row(row_items, spacing=5))

        self.scroll_col.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("⚠️ Problèmes de peau", size=16, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Text("Sélectionnez vos problèmes de peau ou maladies (sauvegardés)",
                            size=11, color=COULEUR_TEXTE_SECONDAIRE),
                    *rows,
                ], spacing=8),
                bgcolor=COULEUR_PANNEAU, border_radius=12,
                padding=ft.padding.all(15),
            )
        )

    def _on_probleme_change(self, probleme: str, e):
        if e.control.value:
            self.gestionnaire.ajouter_probleme(probleme)
        else:
            self.gestionnaire.retirer_probleme(probleme)

    # ─── NOTES PERMANENTES ───

    def _creer_section_notes(self):
        self._txt_notes = ft.TextField(
            value=self.gestionnaire.profil.notes_permanentes,
            multiline=True, min_lines=3, max_lines=5,
            bgcolor=COULEUR_CARTE,
            border_color=COULEUR_BORDURE,
            color=COULEUR_TEXTE,
        )

        self.scroll_col.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("📝 Notes personnelles", size=16, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Text("Informations permanentes (allergies, préférences, etc.)",
                            size=11, color=COULEUR_TEXTE_SECONDAIRE),
                    self._txt_notes,
                    ft.ElevatedButton(
                        "💾 Sauvegarder les notes",
                        on_click=self._sauvegarder_notes,
                        bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=8),
                bgcolor=COULEUR_PANNEAU, border_radius=12,
                padding=ft.padding.all(15),
            )
        )

    def _sauvegarder_notes(self, e):
        notes = self._txt_notes.value or ""
        self.gestionnaire.modifier_notes(notes)
        if self.page:
            self.page.open(ft.SnackBar(
                content=ft.Text("Vos notes ont été sauvegardées !", color=COULEUR_TEXTE),
                bgcolor=COULEUR_ACCENT,
            ))

    # ─── ÉTAT QUOTIDIEN ───

    def _creer_section_quotidien(self):
        niveau = self.gestionnaire.etat_quotidien.niveau_stress
        self._lbl_stress = ft.Text(
            f"{niveau}/10", size=13,
            weight=ft.FontWeight.BOLD, color=couleur_stress(niveau),
        )
        self._slider_stress = ft.Slider(
            min=1, max=10, divisions=9,
            value=niveau,
            active_color=COULEUR_ACCENT,
            inactive_color=COULEUR_CARTE,
            on_change=self._on_stress_change,
        )

        self._entry_etat_jour = ft.TextField(
            hint_text="Ex: Un peu sèche, quelques rougeurs...",
            bgcolor=COULEUR_CARTE,
            border_color=COULEUR_BORDURE,
            color=COULEUR_TEXTE,
            height=40,
            on_change=self._on_etat_jour_change,
        )

        self.scroll_col.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("📅 État du jour", size=16, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Text("Ces informations sont utilisées pour l'analyse mais non sauvegardées",
                            size=11, color=COULEUR_TEXTE_SECONDAIRE),
                    ft.Row([
                        ft.Text("Niveau de stress :", size=13, color=COULEUR_TEXTE),
                        ft.Container(expand=True),
                        self._lbl_stress,
                    ]),
                    self._slider_stress,
                    ft.Text("État de la peau aujourd'hui (optionnel) :", size=13, color=COULEUR_TEXTE),
                    self._entry_etat_jour,
                ], spacing=8),
                bgcolor=COULEUR_PANNEAU, border_radius=12,
                padding=ft.padding.all(15),
            )
        )

    def _on_stress_change(self, e):
        niveau = int(e.control.value)
        self.gestionnaire.definir_stress(niveau)
        self._lbl_stress.value = f"{niveau}/10"
        self._lbl_stress.color = couleur_stress(niveau)
        if self.page:
            self.page.update()

    def _on_etat_jour_change(self, e):
        etat = e.control.value or ""
        self.gestionnaire.definir_etat_jour(etat)

    def actualiser(self):
        """Actualise l'affichage."""
        self._radio_type_peau.value = self.gestionnaire.profil.type_peau.value
        for valeur, cb in self._checkboxes_problemes.items():
            cb.value = valeur in self.gestionnaire.profil.problemes
        self._txt_notes.value = self.gestionnaire.profil.notes_permanentes
        if self.page:
            self.page.update()
