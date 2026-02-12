"""
DermaLogic - Page Accueil (Analyse)
====================================

Page principale avec conditions environnementales,
bouton d'analyse et recommandations par moment.
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
from gui.components.ligne_moment import LigneMoment
from api.open_meteo import DonneesEnvironnementales
from core.algorithme import ResultatDecision


class PageAccueil(ft.Column):
    """Page principale avec analyse et recommandations."""

    def __init__(self, on_actualiser, on_analyser):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

        # Cartes environnement
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

        # Bouton analyser
        self.btn_analyser = ft.Button(
            "ANALYSER MES PRODUITS",
            on_click=on_analyser,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
        )

        # Barre de filtres
        self.label_filtres = ft.Text(
            "Cliquez sur ANALYSER pour obtenir vos recommandations",
            size=11,
            color=COULEUR_TEXTE_SECONDAIRE,
        )

        # Lignes par moment
        self.ligne_matin = LigneMoment("matin")
        self.ligne_journee = LigneMoment("journee")
        self.ligne_soir = LigneMoment("soir")

        # Section exclus
        self.label_exclus = ft.Text("", size=11, color=COULEUR_DANGER)
        self.container_exclus = ft.Container(
            visible=False,
            bgcolor="#2a1a2a",
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            content=self.label_exclus,
        )

        # Construction de la page
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
            # Bouton analyser
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, bottom=12),
                content=self.btn_analyser,
                alignment=ft.Alignment(0, 0),
            ),
            # Barre de filtres
            ft.Container(
                bgcolor=COULEUR_CARTE,
                border_radius=10,
                margin=ft.Margin.symmetric(horizontal=20),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                content=self.label_filtres,
            ),
            # Recommandations par moment
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=10, bottom=10),
                content=ft.Column(
                    spacing=8,
                    controls=[
                        self.ligne_matin,
                        self.ligne_journee,
                        self.ligne_soir,
                        self.container_exclus,
                    ],
                ),
            ),
        ]

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

    def afficher_resultat(self, resultat: ResultatDecision):
        """Affiche le resultat de l'analyse."""
        # Filtres appliques
        if resultat.filtres_appliques:
            txt = " | ".join(resultat.filtres_appliques)
            self.label_filtres.value = f"Filtres actifs: {txt}"
            self.label_filtres.color = "#f9ed69"
        else:
            self.label_filtres.value = "Aucun filtre - Conditions normales"
            self.label_filtres.color = COULEUR_ACCENT

        # Lignes par moment
        self.ligne_matin.afficher_produits(
            resultat.matin.produits, resultat.matin.nettoyant_optimal
        )
        self.ligne_journee.afficher_produits(
            resultat.journee.produits, resultat.journee.nettoyant_optimal
        )
        self.ligne_soir.afficher_produits(
            resultat.soir.produits, resultat.soir.nettoyant_optimal
        )

        # Produits exclus
        if resultat.produits_exclus:
            noms = ", ".join(
                [
                    f"{p.nom} ({resultat.raisons_exclusion.get(p.nom, '')})"
                    for p in resultat.produits_exclus
                ]
            )
            self.label_exclus.value = f"Exclus: {noms}"
            self.container_exclus.visible = True
        else:
            self.container_exclus.visible = False

    def set_loading(self, loading: bool):
        """Active/desactive l'etat de chargement."""
        self.btn_actualiser.text = "..." if loading else "Actualiser"
        self.btn_actualiser.disabled = loading
