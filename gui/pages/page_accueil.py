"""
DermaLogic - Page Accueil (Analyse)
====================================

Page principale avec conditions environnementales et recommandations.
"""

import flet as ft

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE, COULEUR_ACCENT,
    COULEUR_ACCENT_HOVER, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_DANGER, COULEUR_IA,
)
from gui.composants_flet import CarteEnvironnement, LigneMoment
from core.algorithme import ResultatDecision


class PageAccueil(ft.Column):
    """
    Page principale avec conditions environnementales et recommandations.

    Structure :
    - Section conditions (UV, humidité, PM2.5, température)
    - Boutons d'analyse (rapide + IA)
    - Barre de filtres actifs
    - 3 lignes de recommandations (matin, journée, soir)
    - Section des produits exclus
    """

    def __init__(self, app):
        self.app = app

        # ── Cartes environnement ──
        self.carte_uv = CarteEnvironnement("Indice UV")
        self.carte_humidite = CarteEnvironnement("Humidité")
        self.carte_pollution = CarteEnvironnement("PM2.5")
        self.carte_temp = CarteEnvironnement("Température")

        # ── Boutons ──
        self.btn_actualiser = ft.ElevatedButton(
            "Actualiser",
            on_click=lambda e: self.app.actualiser_donnees(),
            bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
            height=28, width=110,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        self.btn_analyse_simple = ft.ElevatedButton(
            "⚡ Analyse rapide",
            on_click=lambda e: self.app.lancer_analyse(),
            bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
            height=45, expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14),
            ),
        )
        self.btn_analyse_ia = ft.ElevatedButton(
            "🤖 Analyse IA personnalisée",
            on_click=lambda e: self.app.ouvrir_analyse_ia(),
            bgcolor=COULEUR_IA, color=COULEUR_TEXTE,
            height=45, expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14),
            ),
        )

        # ── Filtres ──
        self.label_filtres = ft.Text(
            "Cliquez sur ANALYSER pour obtenir vos recommandations",
            size=11, color=COULEUR_TEXTE_SECONDAIRE,
        )

        # ── Lignes moments ──
        self.ligne_matin = LigneMoment("matin")
        self.ligne_journee = LigneMoment("journee")
        self.ligne_soir = LigneMoment("soir")

        # ── Section exclus ──
        self.label_exclus = ft.Text("", size=11, color=COULEUR_DANGER)
        self.container_exclus = ft.Container(
            content=self.label_exclus,
            bgcolor="#2a1a2a", border_radius=10,
            padding=ft.padding.all(10),
            visible=False,
        )

        # ── Assemblage ──
        section_conditions = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Conditions Environnementales", size=15,
                            weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Container(expand=True),
                    self.btn_actualiser,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    self.carte_uv, self.carte_humidite,
                    self.carte_pollution, self.carte_temp,
                ], spacing=8),
            ], spacing=10),
            bgcolor=COULEUR_PANNEAU, border_radius=15,
            padding=ft.padding.all(15),
        )

        section_btns = ft.Row(
            [self.btn_analyse_simple, self.btn_analyse_ia],
            spacing=10,
        )

        barre_filtres = ft.Container(
            content=ft.Row(
                [self.label_filtres],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=COULEUR_CARTE, border_radius=10,
            height=35,
            alignment=ft.Alignment(0, 0),
        )

        section_reco = ft.Column(
            [
                self.ligne_matin,
                self.ligne_journee,
                self.ligne_soir,
                self.container_exclus,
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        super().__init__(
            controls=[
                section_conditions,
                section_btns,
                barre_filtres,
                section_reco,
            ],
            spacing=12,
            expand=True,
        )

    def afficher_resultat(self, resultat: ResultatDecision):
        """Affiche le résultat de l'analyse."""
        # Filtres
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
            noms = ", ".join([
                f"{p.nom} ({resultat.raisons_exclusion.get(p.nom, '')})"
                for p in resultat.produits_exclus
            ])
            self.label_exclus.value = f"Exclus: {noms}"
            self.container_exclus.visible = True
        else:
            self.container_exclus.visible = False

        if self.page:
            self.page.update()
