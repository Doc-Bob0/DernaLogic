"""
DermaLogic - Page Historique
==============================

Page d'affichage de l'historique des analyses.
"""

import flet as ft
from datetime import datetime

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE, COULEUR_CARTE_HOVER,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_DANGER, COULEURS_MOMENT,
)
from core.historique import GestionnaireHistorique, ResultatAnalyseHistorique


class PageHistorique(ft.Column):
    """
    Page d'affichage de l'historique des analyses.
    Affiche les analyses récentes (< 2 semaines) et les archives.
    """

    def __init__(self, gestionnaire_historique: GestionnaireHistorique):
        self.gestionnaire = gestionnaire_historique
        self.onglet_actif = "recentes"

        stats = self.gestionnaire.statistiques()
        self.label_stats = ft.Text(
            f"{stats['nb_total']} analyses", size=14,
            color=COULEUR_TEXTE_SECONDAIRE,
        )

        self.btn_recentes = ft.ElevatedButton(
            f"📅 Récentes ({stats['nb_recentes']})",
            on_click=lambda e: self._changer_onglet("recentes"),
            bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
            width=160,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        self.btn_archives = ft.ElevatedButton(
            f"📦 Archives ({stats['nb_archives']})",
            on_click=lambda e: self._changer_onglet("archives"),
            bgcolor="transparent", color=COULEUR_TEXTE,
            width=160,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

        self.contenu = ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=4, expand=True,
        )

        header = ft.Row([
            ft.Text("Historique des Analyses", size=24,
                    weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
            self.label_stats,
        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        onglets = ft.Container(
            content=ft.Row(
                [self.btn_recentes, self.btn_archives],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=COULEUR_PANNEAU, border_radius=10,
            padding=ft.padding.all(8),
        )

        super().__init__(
            controls=[header, onglets, self.contenu],
            spacing=10,
            expand=True,
        )

    def _changer_onglet(self, onglet: str):
        self.onglet_actif = onglet
        if onglet == "recentes":
            self.btn_recentes.bgcolor = COULEUR_ACCENT
            self.btn_recentes.color = COULEUR_FOND
            self.btn_archives.bgcolor = "transparent"
            self.btn_archives.color = COULEUR_TEXTE
            self._afficher_recentes()
        else:
            self.btn_archives.bgcolor = COULEUR_ACCENT
            self.btn_archives.color = COULEUR_FOND
            self.btn_recentes.bgcolor = "transparent"
            self.btn_recentes.color = COULEUR_TEXTE
            self._afficher_archives()
        if self.page:
            self.page.update()

    def _afficher_recentes(self):
        self.contenu.controls.clear()
        analyses = self.gestionnaire.obtenir_recentes()
        if not analyses:
            self._afficher_vide("Aucune analyse récente")
            return
        self._grouper_par_date(analyses)

    def _afficher_archives(self):
        self.contenu.controls.clear()
        analyses = self.gestionnaire.obtenir_archives()
        if not analyses:
            self._afficher_vide("Aucune archive disponible")
            return
        self._grouper_par_date(analyses)

    def _afficher_vide(self, message: str):
        self.contenu.controls.append(
            ft.Container(
                content=ft.Text(
                    f"📭\n\n{message}", size=16,
                    color=COULEUR_TEXTE_SECONDAIRE,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=COULEUR_PANNEAU, border_radius=15,
                padding=ft.padding.all(40),
                alignment=ft.Alignment(0, 0),
            )
        )

    def _grouper_par_date(self, analyses: list):
        par_date = {}
        for analyse in analyses:
            if analyse.date not in par_date:
                par_date[analyse.date] = []
            par_date[analyse.date].append(analyse)
        for date, liste_analyses in par_date.items():
            self._creer_section_date(date, liste_analyses)

    def _creer_section_date(self, date: str, analyses: list):
        try:
            dt = datetime.fromisoformat(date)
            date_formatee = dt.strftime("%A %d %B %Y").capitalize()
        except Exception:
            date_formatee = date

        self.contenu.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"📅 {date_formatee}", size=14,
                            weight=ft.FontWeight.BOLD, color=COULEUR_ACCENT),
                    ft.Container(expand=True),
                    ft.Text(f"{len(analyses)} analyse(s)", size=12,
                            color=COULEUR_TEXTE_SECONDAIRE),
                ]),
                padding=ft.padding.only(top=15, bottom=5),
            )
        )
        for analyse in analyses:
            self.contenu.controls.append(self._creer_carte_analyse(analyse))

    def _creer_carte_analyse(self, analyse: ResultatAnalyseHistorique) -> ft.Container:
        # Conditions
        conditions = analyse.conditions
        cond_row = ft.Row([
            self._badge_env(f"UV {conditions.indice_uv:.1f}",
                            self._couleur_niveau(conditions.niveau_uv)),
            self._badge_env(f"H {conditions.humidite:.0f}%",
                            self._couleur_niveau(conditions.niveau_humidite)),
            self._badge_env(f"T {conditions.temperature:.1f}°C", COULEUR_TEXTE_SECONDAIRE),
        ], spacing=6)

        if conditions.pm2_5:
            cond_row.controls.append(
                self._badge_env(f"PM {conditions.pm2_5:.0f}",
                                self._couleur_niveau(conditions.niveau_pollution))
            )

        # Badges moments
        moment_row = ft.Row(spacing=6)
        if analyse.produits_matin:
            moment_row.controls.append(
                self._badge_moment("matin", len(analyse.produits_matin)))
        if analyse.produits_journee:
            moment_row.controls.append(
                self._badge_moment("journee", len(analyse.produits_journee)))
        if analyse.produits_soir:
            moment_row.controls.append(
                self._badge_moment("soir", len(analyse.produits_soir)))

        # Heure
        heure = analyse.heure if hasattr(analyse, 'heure') else ""

        # Alertes
        alertes_col = ft.Column(spacing=2)
        if analyse.alertes:
            for alerte in analyse.alertes:
                alertes_col.controls.append(
                    ft.Text(f"⚠️ {alerte}", size=10, color=COULEUR_DANGER)
                )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"{conditions.ville}, {conditions.pays}",
                            size=14, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Container(expand=True),
                    ft.Text(heure, size=11, color=COULEUR_TEXTE_SECONDAIRE),
                ]),
                cond_row,
                moment_row,
                alertes_col,
            ], spacing=6),
            bgcolor=COULEUR_CARTE, border_radius=12,
            padding=ft.padding.all(12),
        )

    def _badge_env(self, text: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(text, size=10, weight=ft.FontWeight.BOLD, color=color),
            bgcolor=COULEUR_CARTE_HOVER,
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

    def _badge_moment(self, moment: str, nb: int) -> ft.Container:
        couleur, titre = COULEURS_MOMENT.get(moment, ("#fff", moment))
        return ft.Container(
            content=ft.Text(f"{titre} ({nb})", size=10,
                            weight=ft.FontWeight.BOLD, color=couleur),
            bgcolor=COULEUR_CARTE_HOVER,
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

    def _couleur_niveau(self, niveau: str) -> str:
        couleurs = {
            "Faible": COULEUR_ACCENT, "Modere": "#f9ed69",
            "Eleve": "#f38181", "Tres eleve": COULEUR_DANGER,
            "Extreme": "#aa2ee6", "Tres sec": COULEUR_DANGER,
            "Sec": "#f9ed69", "Normal": COULEUR_ACCENT,
            "Humide": "#00b4d8", "Excellent": COULEUR_ACCENT,
            "Bon": "#9be36d", "Mauvais": "#f38181",
            "Tres mauvais": COULEUR_DANGER,
        }
        return couleurs.get(niveau, COULEUR_TEXTE_SECONDAIRE)

    def actualiser(self):
        """Actualise l'affichage de l'historique."""
        stats = self.gestionnaire.statistiques()
        self.label_stats.value = f"{stats['nb_total']} analyses"
        self.btn_recentes.text = f"📅 Récentes ({stats['nb_recentes']})"
        self.btn_archives.text = f"📦 Archives ({stats['nb_archives']})"
        if self.onglet_actif == "recentes":
            self._afficher_recentes()
        else:
            self._afficher_archives()
        if self.page:
            self.page.update()
