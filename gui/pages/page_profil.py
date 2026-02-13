"""
DermaLogic - Page Profil Utilisateur
=====================================

Formulaire de gestion du profil dermatologique :
- Type de peau, tranche d'age
- Niveau de stress
- Maladies de peau, allergies
- Objectifs, instructions quotidiennes
"""

import flet as ft
from gui.theme import (
    COULEUR_ACCENT,
    COULEUR_FOND,
    COULEUR_DANGER,
    COULEUR_PANNEAU,
    COULEUR_CARTE,
    COULEUR_TEXTE_SECONDAIRE,
)
from core.models import (
    ProfilUtilisateur,
    TypePeau,
    TrancheAge,
    ObjectifPeau,
)

# Maladies de peau predefinies
MALADIES_PREDEFINIES = [
    "Eczema", "Psoriasis", "Rosacee", "Dermatite",
    "Acne", "Vitiligo", "Keratose", "Couperose",
]

# Labels lisibles pour les objectifs
_LABELS_OBJECTIF = {
    "hydratation": "Hydratation",
    "anti-acne": "Anti-acne",
    "eclat": "Eclat",
    "anti-taches": "Anti-taches",
    "anti-age": "Anti-age",
    "apaisement": "Apaisement",
    "protection": "Protection",
}


class PageProfil(ft.Column):
    """Page de gestion du profil utilisateur."""

    def __init__(self, page: ft.Page, gestionnaire_profil):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.page_ref = page
        self.gestionnaire = gestionnaire_profil

        # --- Type de peau ---
        self.dd_type_peau = ft.Dropdown(
            label="Type de peau",
            options=[
                ft.dropdown.Option("normale", "Normale"),
                ft.dropdown.Option("grasse", "Grasse"),
                ft.dropdown.Option("seche", "Seche"),
                ft.dropdown.Option("mixte", "Mixte"),
                ft.dropdown.Option("sensible", "Sensible"),
            ],
            value="normale",
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )

        # --- Tranche d'age ---
        self.dd_age = ft.Dropdown(
            label="Tranche d'age",
            options=[
                ft.dropdown.Option("<18", "Moins de 18 ans"),
                ft.dropdown.Option("18-25", "18-25 ans"),
                ft.dropdown.Option("26-35", "26-35 ans"),
                ft.dropdown.Option("36-45", "36-45 ans"),
                ft.dropdown.Option("46-55", "46-55 ans"),
                ft.dropdown.Option("55+", "Plus de 55 ans"),
            ],
            value="26-35",
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )

        # --- Niveau de stress ---
        self.label_stress = ft.Text("Stress : 5/10", size=14, color="#ffffff")
        self.slider_stress = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            value=5,
            label="{value}",
            active_color=COULEUR_ACCENT,
            on_change=self._on_stress_change,
        )

        # --- Maladies de peau (chips) ---
        self.maladies_selectionnees: list[str] = []
        self.row_maladies = ft.Row(wrap=True, spacing=8, run_spacing=8)
        self.entry_maladie_custom = ft.TextField(
            hint_text="Ajouter une condition...",
            text_size=13,
            height=40,
            border_color=COULEUR_TEXTE_SECONDAIRE,
            on_submit=self._ajouter_maladie_custom,
            expand=True,
        )

        # --- Allergies ---
        self.entry_allergies = ft.TextField(
            label="Allergies / Intolerances",
            hint_text="Ex: parfum, alcool, retinol (separes par des virgules)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            text_size=14,
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )

        # --- Objectifs ---
        self.objectifs_selectionnes: list[str] = []
        self.row_objectifs = ft.Row(wrap=True, spacing=8, run_spacing=8)

        # --- Instructions quotidiennes ---
        self.entry_instructions = ft.TextField(
            label="Instructions personnalisees quotidiennes",
            hint_text="Ex: J'ai la peau irritee en ce moment, eviter les actifs forts...",
            multiline=True,
            min_lines=3,
            max_lines=6,
            text_size=14,
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
        )

        # --- Bouton sauvegarder ---
        self.btn_sauvegarder = ft.Button(
            "Sauvegarder le profil",
            on_click=self._sauvegarder,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
        )

        self.label_status = ft.Text("", size=12, color=COULEUR_ACCENT)

        # --- Construction ---
        self.controls = [
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=15, bottom=10),
                content=ft.Text("Mon Profil", size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
            ),
            # Section peau et age
            ft.Container(
                bgcolor=COULEUR_PANNEAU, border_radius=15,
                margin=ft.Margin.symmetric(horizontal=20), padding=20,
                content=ft.Column(spacing=15, controls=[
                    ft.Text("Informations generales", size=14, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.ResponsiveRow(controls=[
                        ft.Container(content=self.dd_type_peau, col={"xs": 12, "md": 6}, padding=4),
                        ft.Container(content=self.dd_age, col={"xs": 12, "md": 6}, padding=4),
                    ]),
                    self.label_stress,
                    self.slider_stress,
                ]),
            ),
            # Section maladies
            ft.Container(
                bgcolor=COULEUR_PANNEAU, border_radius=15,
                margin=ft.Margin.only(left=20, right=20, top=15), padding=20,
                content=ft.Column(spacing=12, controls=[
                    ft.Text("Conditions cutanees", size=14, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    self.row_maladies,
                    ft.Row(controls=[
                        self.entry_maladie_custom,
                        ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=COULEUR_ACCENT, on_click=self._ajouter_maladie_custom),
                    ]),
                ]),
            ),
            # Section allergies
            ft.Container(
                bgcolor=COULEUR_PANNEAU, border_radius=15,
                margin=ft.Margin.only(left=20, right=20, top=15), padding=20,
                content=ft.Column(spacing=12, controls=[
                    ft.Text("Allergies / Intolerances", size=14, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    self.entry_allergies,
                ]),
            ),
            # Section objectifs
            ft.Container(
                bgcolor=COULEUR_PANNEAU, border_radius=15,
                margin=ft.Margin.only(left=20, right=20, top=15), padding=20,
                content=ft.Column(spacing=12, controls=[
                    ft.Text("Objectifs de soin", size=14, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    self.row_objectifs,
                ]),
            ),
            # Section instructions
            ft.Container(
                bgcolor=COULEUR_PANNEAU, border_radius=15,
                margin=ft.Margin.only(left=20, right=20, top=15), padding=20,
                content=ft.Column(spacing=12, controls=[
                    ft.Text("Instructions quotidiennes", size=14, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Text("Ces instructions seront prises en compte a chaque analyse.", size=12, color=COULEUR_TEXTE_SECONDAIRE),
                    self.entry_instructions,
                ]),
            ),
            # Bouton sauvegarder
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=20, bottom=20),
                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    self.btn_sauvegarder,
                    self.label_status,
                ]),
            ),
        ]

    def charger_profil(self):
        """Charge le profil depuis le gestionnaire et remplit le formulaire."""
        profil = self.gestionnaire.obtenir()

        self.dd_type_peau.value = profil.type_peau.value
        self.dd_age.value = profil.tranche_age.value
        self.slider_stress.value = profil.niveau_stress
        self.label_stress.value = f"Stress : {profil.niveau_stress}/10"

        self.maladies_selectionnees = profil.maladies_peau.copy()
        self._actualiser_chips_maladies()

        self.entry_allergies.value = ", ".join(profil.allergies)

        self.objectifs_selectionnes = [o.value for o in profil.objectifs]
        self._actualiser_chips_objectifs()

        self.entry_instructions.value = profil.instructions_quotidiennes
        self.label_status.value = ""

    def _on_stress_change(self, e):
        val = int(e.control.value)
        self.label_stress.value = f"Stress : {val}/10"
        self.page_ref.update()

    def _actualiser_chips_maladies(self):
        self.row_maladies.controls.clear()
        for maladie in MALADIES_PREDEFINIES:
            est_sel = maladie in self.maladies_selectionnees
            self.row_maladies.controls.append(
                ft.Chip(
                    label=ft.Text(maladie, size=12), selected=est_sel,
                    on_select=lambda e, m=maladie: self._toggle_maladie(m, e.control.selected),
                    bgcolor=COULEUR_CARTE, selected_color=COULEUR_ACCENT, check_color=COULEUR_FOND,
                )
            )
        for maladie in self.maladies_selectionnees:
            if maladie not in MALADIES_PREDEFINIES:
                self.row_maladies.controls.append(
                    ft.Chip(
                        label=ft.Text(maladie, size=12), selected=True,
                        on_select=lambda e, m=maladie: self._toggle_maladie(m, e.control.selected),
                        bgcolor=COULEUR_CARTE, selected_color="#9b59b6", check_color=COULEUR_FOND,
                    )
                )

    def _toggle_maladie(self, maladie: str, selected: bool):
        if selected and maladie not in self.maladies_selectionnees:
            self.maladies_selectionnees.append(maladie)
        elif not selected and maladie in self.maladies_selectionnees:
            self.maladies_selectionnees.remove(maladie)
        self._actualiser_chips_maladies()
        self.page_ref.update()

    def _ajouter_maladie_custom(self, e=None):
        val = self.entry_maladie_custom.value.strip() if self.entry_maladie_custom.value else ""
        if val and val not in self.maladies_selectionnees:
            self.maladies_selectionnees.append(val)
            self.entry_maladie_custom.value = ""
            self._actualiser_chips_maladies()
            self.page_ref.update()

    def _actualiser_chips_objectifs(self):
        self.row_objectifs.controls.clear()
        for obj in ObjectifPeau:
            est_sel = obj.value in self.objectifs_selectionnes
            self.row_objectifs.controls.append(
                ft.Chip(
                    label=ft.Text(_LABELS_OBJECTIF.get(obj.value, obj.value), size=12),
                    selected=est_sel,
                    on_select=lambda e, o=obj.value: self._toggle_objectif(o, e.control.selected),
                    bgcolor=COULEUR_CARTE, selected_color=COULEUR_ACCENT, check_color=COULEUR_FOND,
                )
            )

    def _toggle_objectif(self, objectif: str, selected: bool):
        if selected and objectif not in self.objectifs_selectionnes:
            self.objectifs_selectionnes.append(objectif)
        elif not selected and objectif in self.objectifs_selectionnes:
            self.objectifs_selectionnes.remove(objectif)
        self._actualiser_chips_objectifs()
        self.page_ref.update()

    def _sauvegarder(self, e=None):
        allergies_text = self.entry_allergies.value or ""
        allergies = [a.strip() for a in allergies_text.split(",") if a.strip()]

        objectifs = []
        for val in self.objectifs_selectionnes:
            try:
                objectifs.append(ObjectifPeau(val))
            except ValueError:
                pass

        profil = ProfilUtilisateur(
            type_peau=TypePeau(self.dd_type_peau.value or "normale"),
            tranche_age=TrancheAge(self.dd_age.value or "26-35"),
            niveau_stress=int(self.slider_stress.value),
            maladies_peau=self.maladies_selectionnees.copy(),
            allergies=allergies,
            objectifs=objectifs,
            instructions_quotidiennes=self.entry_instructions.value or "",
        )

        self.gestionnaire.sauvegarder(profil)
        self.label_status.value = "Profil sauvegarde !"
        self.label_status.color = COULEUR_ACCENT
        self.page_ref.update()
