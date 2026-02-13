"""
DermaLogic - Page Accueil (Analyse)
====================================

Page principale avec conditions environnementales,
previsions 3 jours, double mode d'analyse (rapide/detaille)
et affichage des resultats de routine IA.
"""

import flet as ft
from gui.theme import (
    COULEUR_ACCENT,
    COULEUR_ACCENT_HOVER,
    COULEUR_FOND,
    COULEUR_DANGER,
    COULEUR_PANNEAU,
    COULEUR_CARTE,
    COULEUR_TEXTE_SECONDAIRE,
    COULEURS_UV,
    COULEURS_HUMIDITE,
    COULEURS_POLLUTION,
)
from gui.components.carte_environnement import CarteEnvironnement
from api.open_meteo import DonneesEnvironnementales, PrevisionJournaliere


class PageAccueil(ft.Column):
    """Page principale avec analyse IA et recommandations."""

    def __init__(self, on_actualiser, on_analyser_rapide, on_analyser_detaille):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

        self.on_analyser_detaille = on_analyser_detaille

        # --- Cartes environnement ---
        self.carte_uv = CarteEnvironnement("Indice UV")
        self.carte_humidite = CarteEnvironnement("Humidite")
        self.carte_pollution = CarteEnvironnement("PM2.5")
        self.carte_temp = CarteEnvironnement("Temperature")

        # Bouton actualiser
        self.btn_actualiser = ft.Button(
            "Actualiser",
            on_click=on_actualiser,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=28,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.Padding.symmetric(horizontal=16),
            ),
        )

        # --- Previsions 3 jours ---
        self.row_previsions = ft.Row(spacing=8)
        self.container_previsions = ft.Container(
            visible=False,
            bgcolor=COULEUR_PANNEAU,
            border_radius=15,
            margin=ft.Margin.only(left=20, right=20, bottom=12),
            padding=15,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        "Previsions 3 jours",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="#ffffff",
                    ),
                    self.row_previsions,
                ],
            ),
        )

        # --- Boutons analyse ---
        self.btn_rapide = ft.Button(
            "Analyse Rapide",
            on_click=on_analyser_rapide,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=45,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
            ),
        )

        self.btn_detaille = ft.Button(
            "Analyse Detaillee",
            on_click=self._toggle_panneau_detaille,
            bgcolor="#9b59b6",
            color="#ffffff",
            height=45,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
            ),
        )

        # --- Panneau mode detaille ---
        self.entry_instructions = ft.TextField(
            label="Instructions du jour",
            hint_text="Ex: peau irritee aujourd'hui, maquillage prevu ce soir...",
            multiline=True,
            min_lines=2,
            max_lines=4,
            text_size=13,
            border_color="#9b59b6",
            focused_border_color="#9b59b6",
        )

        self.label_stress = ft.Text("Stress du jour : 5", size=12, color="#ffffff")
        self.slider_stress = ft.Slider(
            min=1,
            max=10,
            value=5,
            divisions=9,
            label="{value}",
            active_color="#9b59b6",
            on_change=self._on_stress_change,
        )

        self.btn_lancer_detaille = ft.Button(
            "Lancer l'analyse detaillee",
            on_click=self._lancer_detaille,
            bgcolor="#9b59b6",
            color="#ffffff",
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

        self.panneau_detaille = ft.Container(
            visible=False,
            bgcolor=COULEUR_CARTE,
            border_radius=12,
            margin=ft.Margin.only(left=20, right=20, top=8),
            padding=15,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "Mode Detaille",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="#9b59b6",
                    ),
                    self.entry_instructions,
                    self.label_stress,
                    self.slider_stress,
                    self.btn_lancer_detaille,
                ],
            ),
        )

        # --- Zone de resultat IA ---
        self.resultat_container = ft.Container(
            visible=False,
            bgcolor=COULEUR_PANNEAU,
            border_radius=15,
            margin=ft.Margin.only(left=20, right=20, top=12, bottom=20),
            padding=20,
            content=ft.Column(spacing=10),
        )

        # --- Label statut ---
        self.label_statut = ft.Text(
            "Lancez une analyse pour obtenir vos recommandations",
            size=11,
            color=COULEUR_TEXTE_SECONDAIRE,
        )

        # --- Construction de la page ---
        self.controls = [
            # Section conditions environnementales
            ft.Container(
                bgcolor=COULEUR_PANNEAU,
                border_radius=15,
                margin=ft.Margin.only(left=20, right=20, top=10, bottom=12),
                padding=15,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Conditions Environnementales",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color="#ffffff",
                                ),
                                ft.Container(expand=True),
                                self.btn_actualiser,
                            ],
                        ),
                        ft.ResponsiveRow(
                            controls=[
                                ft.Container(
                                    content=self.carte_uv,
                                    col={"xs": 6, "md": 3},
                                    padding=4,
                                ),
                                ft.Container(
                                    content=self.carte_humidite,
                                    col={"xs": 6, "md": 3},
                                    padding=4,
                                ),
                                ft.Container(
                                    content=self.carte_pollution,
                                    col={"xs": 6, "md": 3},
                                    padding=4,
                                ),
                                ft.Container(
                                    content=self.carte_temp,
                                    col={"xs": 6, "md": 3},
                                    padding=4,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            # Previsions 3 jours
            self.container_previsions,
            # Boutons d'analyse
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, bottom=4),
                content=ft.Row(
                    spacing=10,
                    controls=[self.btn_rapide, self.btn_detaille],
                ),
            ),
            # Label statut
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=4, bottom=4),
                content=self.label_statut,
            ),
            # Panneau detaille (cache par defaut)
            self.panneau_detaille,
            # Resultat IA
            self.resultat_container,
        ]

    # -------------------------------------------------------
    # Conditions environnementales
    # -------------------------------------------------------

    def afficher_conditions(self, donnees: DonneesEnvironnementales | None):
        """Affiche les conditions environnementales."""
        if donnees:
            self.carte_uv.mettre_a_jour(
                f"{donnees.indice_uv:.1f}",
                donnees.niveau_uv,
                COULEURS_UV.get(donnees.niveau_uv, "#fff"),
            )
            self.carte_humidite.mettre_a_jour(
                f"{donnees.humidite_relative:.0f}%",
                donnees.niveau_humidite,
                COULEURS_HUMIDITE.get(donnees.niveau_humidite, "#fff"),
            )
            pm = f"{donnees.pm2_5:.0f}" if donnees.pm2_5 else "--"
            self.carte_pollution.mettre_a_jour(
                f"{pm} ug/m3",
                donnees.niveau_pollution,
                COULEURS_POLLUTION.get(donnees.niveau_pollution, "#fff"),
            )
            heure = donnees.heure if hasattr(donnees, "heure") and donnees.heure else ""
            self.carte_temp.mettre_a_jour(f"{donnees.temperature:.1f}C", heure)
        else:
            for carte in [self.carte_uv, self.carte_humidite, self.carte_pollution, self.carte_temp]:
                carte.mettre_a_jour("Erreur", "Echec", COULEUR_DANGER)

    # -------------------------------------------------------
    # Previsions 3 jours
    # -------------------------------------------------------

    def afficher_previsions(self, previsions: list):
        """Affiche les cartes de previsions 3 jours."""
        self.row_previsions.controls.clear()

        if not previsions:
            self.container_previsions.visible = False
            return

        for prev in previsions[:3]:
            uv_color = "#4ecca3" if prev.uv_max < 6 else ("#f9ed69" if prev.uv_max < 8 else "#e94560")
            carte = ft.Container(
                expand=True,
                bgcolor=COULEUR_CARTE,
                border_radius=10,
                padding=12,
                content=ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(prev.date, size=11, weight=ft.FontWeight.BOLD, color="#ffffff"),
                        ft.Text(f"UV {prev.uv_max:.0f}", size=13, weight=ft.FontWeight.BOLD, color=uv_color),
                        ft.Text(
                            f"{prev.temperature_min:.0f} / {prev.temperature_max:.0f}C",
                            size=11,
                            color=COULEUR_TEXTE_SECONDAIRE,
                        ),
                        ft.Text(f"{prev.humidite_moyenne:.0f}%", size=11, color=COULEUR_TEXTE_SECONDAIRE),
                    ],
                ),
            )
            self.row_previsions.controls.append(carte)

        self.container_previsions.visible = True

    # -------------------------------------------------------
    # Analyse
    # -------------------------------------------------------

    def _toggle_panneau_detaille(self, e=None):
        """Affiche/masque le panneau de mode detaille."""
        self.panneau_detaille.visible = not self.panneau_detaille.visible
        self.update()

    def _on_stress_change(self, e):
        """Met a jour le label de stress."""
        self.label_stress.value = f"Stress du jour : {int(e.control.value)}"
        self.update()

    def _lancer_detaille(self, e=None):
        """Lance l'analyse detaillee avec instructions et stress."""
        instructions = self.entry_instructions.value.strip() if self.entry_instructions.value else ""
        stress = int(self.slider_stress.value)
        if self.on_analyser_detaille:
            self.on_analyser_detaille(instructions, stress)

    def set_analyse_loading(self, loading: bool):
        """Active/desactive l'etat de chargement des boutons d'analyse."""
        self.btn_rapide.disabled = loading
        self.btn_detaille.disabled = loading
        self.btn_lancer_detaille.disabled = loading
        if loading:
            self.btn_rapide.text = "Analyse en cours..."
            self.label_statut.value = "Analyse IA en cours, veuillez patienter..."
            self.label_statut.color = "#f9ed69"
        else:
            self.btn_rapide.text = "Analyse Rapide"
            self.label_statut.value = ""
            self.label_statut.color = COULEUR_TEXTE_SECONDAIRE

    def set_loading(self, loading: bool):
        """Active/desactive l'etat de chargement meteo."""
        self.btn_actualiser.text = "..." if loading else "Actualiser"
        self.btn_actualiser.disabled = loading

    # -------------------------------------------------------
    # Affichage resultat IA
    # -------------------------------------------------------

    def afficher_resultat_ia(self, resultat: dict):
        """Affiche le resultat de l'analyse IA."""
        col = self.resultat_container.content
        col.controls.clear()

        # Titre
        col.controls.append(
            ft.Text("Resultat de l'analyse", size=18, weight=ft.FontWeight.BOLD, color="#ffffff")
        )

        # Resume
        resume = resultat.get("resume", "")
        if resume:
            col.controls.append(
                ft.Text(resume, size=13, color=COULEUR_TEXTE_SECONDAIRE, italic=True)
            )
            col.controls.append(ft.Divider(color=COULEUR_CARTE, height=1))

        # Routine Matin
        routine_matin = resultat.get("routine_matin", [])
        if routine_matin:
            col.controls.append(self._creer_section_routine("Routine Matin", routine_matin, "#f9ed69"))

        # Routine Soir
        routine_soir = resultat.get("routine_soir", [])
        if routine_soir:
            col.controls.append(self._creer_section_routine("Routine Soir", routine_soir, "#9b59b6"))

        # Alertes
        alertes = resultat.get("alertes", [])
        if alertes:
            col.controls.append(ft.Container(height=5))
            col.controls.append(
                ft.Text("Alertes", size=14, weight=ft.FontWeight.BOLD, color=COULEUR_DANGER)
            )
            for alerte in alertes:
                col.controls.append(
                    ft.Text(f"  ⚠ {alerte}", size=12, color=COULEUR_DANGER)
                )

        # Conseil du jour
        conseil = resultat.get("conseils_jour", "")
        if conseil:
            col.controls.append(ft.Container(height=5))
            col.controls.append(
                ft.Container(
                    bgcolor=COULEUR_CARTE,
                    border_radius=8,
                    padding=12,
                    content=ft.Text(
                        f"💡 {conseil}",
                        size=12,
                        color=COULEUR_ACCENT,
                        italic=True,
                    ),
                )
            )

        self.resultat_container.visible = True
        self.label_statut.value = "Analyse terminee"
        self.label_statut.color = COULEUR_ACCENT

    def afficher_erreur_analyse(self, message: str):
        """Affiche une erreur dans la zone de resultat."""
        col = self.resultat_container.content
        col.controls.clear()
        col.controls.append(
            ft.Text(f"Erreur : {message}", size=13, color=COULEUR_DANGER)
        )
        self.resultat_container.visible = True
        self.label_statut.value = "Echec de l'analyse"
        self.label_statut.color = COULEUR_DANGER

    def _creer_section_routine(self, titre: str, items: list, couleur_titre: str) -> ft.Column:
        """Cree une section routine (matin/soir) avec la liste de produits."""
        section = ft.Column(spacing=4)
        section.controls.append(
            ft.Text(titre, size=14, weight=ft.FontWeight.BOLD, color=couleur_titre)
        )
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                nom = item.get("produit", "?")
                raison = item.get("raison", "")
                section.controls.append(
                    ft.Text(f"  {i}. {nom} — {raison}", size=12, color="#ffffff")
                )
            else:
                section.controls.append(
                    ft.Text(f"  {i}. {item}", size=12, color="#ffffff")
                )
        return section
