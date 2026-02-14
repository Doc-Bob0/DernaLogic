"""
DermaLogic - Page Historique
=============================

Affiche l'historique des analyses IA en ordre chronologique.
Chaque entree peut etre expandee pour voir le detail.
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


class PageHistorique(ft.Column):
    """Page d'historique des analyses."""

    def __init__(self, page: ft.Page, gestionnaire_historique):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.page_ref = page
        self.gestionnaire = gestionnaire_historique

        self.label_count = ft.Text("0 analyses", size=14, color=COULEUR_TEXTE_SECONDAIRE)
        self.liste = ft.Column(spacing=8)

        self.controls = [
            ft.Container(
                margin=ft.Margin.only(left=20, right=20, top=15, bottom=10),
                content=ft.Row(controls=[
                    ft.Text("Historique", size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Container(width=15),
                    self.label_count,
                ]),
            ),
            ft.Container(
                margin=ft.Margin.symmetric(horizontal=20),
                expand=True,
                content=self.liste,
            ),
        ]

    def actualiser_liste(self):
        """Actualise l'affichage de l'historique."""
        self.liste.controls.clear()
        entrees = self.gestionnaire.obtenir_tous()
        self.label_count.value = f"{len(entrees)} analyses"

        if not entrees:
            self.liste.controls.append(
                ft.Container(
                    bgcolor=COULEUR_PANNEAU,
                    border_radius=15,
                    margin=ft.Margin.symmetric(vertical=50, horizontal=50),
                    padding=40,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "Aucune analyse dans l'historique\n\nLancez une analyse depuis la page Analyse",
                        size=14,
                        color=COULEUR_TEXTE_SECONDAIRE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )
            return

        for entree in entrees:
            self.liste.controls.append(self._creer_carte(entree))

    def _creer_carte(self, entree) -> ft.Container:
        """Cree une carte pour une entree d'historique."""
        # Formater la date
        date_str = entree.date[:16].replace("T", " ") if entree.date else "?"

        # Badge mode
        mode_color = COULEUR_ACCENT if entree.mode == "rapide" else "#9b59b6"
        mode_label = "Rapide" if entree.mode == "rapide" else "Detaillee"

        # Contenu detaille (initialement cache)
        detail_content = ft.Column(spacing=8, visible=False)

        # Routine matin
        if entree.routine_matin:
            detail_content.controls.append(
                ft.Text("Routine Matin", size=13, weight=ft.FontWeight.BOLD, color="#f9ed69")
            )
            for i, item in enumerate(entree.routine_matin, 1):
                if isinstance(item, dict):
                    nom = item.get("produit", "?")
                    raison = item.get("raison", "")
                    detail_content.controls.append(
                        ft.Text(f"  {i}. {nom} - {raison}", size=12, color="#ffffff")
                    )
                else:
                    detail_content.controls.append(
                        ft.Text(f"  {i}. {item}", size=12, color="#ffffff")
                    )

        # Routine soir
        if entree.routine_soir:
            detail_content.controls.append(ft.Container(height=5))
            detail_content.controls.append(
                ft.Text("Routine Soir", size=13, weight=ft.FontWeight.BOLD, color="#9b59b6")
            )
            for i, item in enumerate(entree.routine_soir, 1):
                if isinstance(item, dict):
                    nom = item.get("produit", "?")
                    raison = item.get("raison", "")
                    detail_content.controls.append(
                        ft.Text(f"  {i}. {nom} - {raison}", size=12, color="#ffffff")
                    )
                else:
                    detail_content.controls.append(
                        ft.Text(f"  {i}. {item}", size=12, color="#ffffff")
                    )

        # Alertes
        if entree.alertes:
            detail_content.controls.append(ft.Container(height=5))
            for alerte in entree.alertes:
                detail_content.controls.append(
                    ft.Text(f"  ⚠ {alerte}", size=12, color=COULEUR_DANGER)
                )

        # Activites du jour
        activites = getattr(entree, "activites_jour", [])
        if activites:
            detail_content.controls.append(ft.Container(height=5))
            detail_content.controls.append(
                ft.Text("Pendant la journee", size=13, weight=ft.FontWeight.BOLD, color="#00b4d8")
            )
            for activite in activites:
                detail_content.controls.append(
                    ft.Text(f"  • {activite}", size=12, color="#ffffff")
                )

        # Conseils
        if entree.conseils_jour:
            detail_content.controls.append(ft.Container(height=5))
            detail_content.controls.append(
                ft.Text(f"Conseil : {entree.conseils_jour}", size=12, color=COULEUR_ACCENT, italic=True)
            )

        def _toggle_detail(e):
            detail_content.visible = not detail_content.visible
            self.page_ref.update()

        # Resume apercu
        resume_apercu = entree.resume_ia[:100] + "..." if len(entree.resume_ia) > 100 else entree.resume_ia

        return ft.Container(
            bgcolor=COULEUR_CARTE,
            border_radius=12,
            padding=15,
            on_click=_toggle_detail,
            ink=True,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(date_str, size=13, weight=ft.FontWeight.BOLD, color="#ffffff"),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(mode_label, size=10, weight=ft.FontWeight.BOLD, color=COULEUR_FOND),
                                bgcolor=mode_color,
                                border_radius=4,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                            ),
                        ],
                    ),
                    ft.Text(
                        resume_apercu if resume_apercu else "Pas de resume",
                        size=12,
                        color=COULEUR_TEXTE_SECONDAIRE,
                    ),
                    detail_content,
                ],
            ),
        )
