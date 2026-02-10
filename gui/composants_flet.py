"""
DermaLogic - Composants Flet Réutilisables
=============================================

Widgets personnalisés :
- CarteEnvironnement : Affichage d'une donnée environnementale
- LigneMoment : Ligne horizontale scrollable de produits pour un moment
- carte_produit : Fonction helper pour créer une carte produit
"""

import flet as ft
from core.algorithme import ProduitDerma

from gui.theme import (
    COULEUR_FOND,
    COULEUR_CARTE,
    COULEUR_CARTE_HOVER,
    COULEUR_PANNEAU,
    COULEUR_TEXTE,
    COULEUR_TEXTE_SECONDAIRE,
    COULEUR_ACCENT,
    COULEUR_DANGER,
    COULEURS_CATEGORIE,
    COULEURS_MOMENT,
)


class CarteEnvironnement(ft.Container):
    """
    Carte compacte pour afficher une donnée environnementale.
    Affiche un titre, une valeur principale et un niveau textuel coloré.
    """

    def __init__(self, titre: str):
        self._lbl_titre = ft.Text(
            titre, size=11, weight=ft.FontWeight.BOLD,
            color=COULEUR_TEXTE_SECONDAIRE, text_align=ft.TextAlign.CENTER,
        )
        self._lbl_valeur = ft.Text(
            "--", size=22, weight=ft.FontWeight.BOLD,
            color=COULEUR_TEXTE, text_align=ft.TextAlign.CENTER,
        )
        self._lbl_niveau = ft.Text(
            "", size=10, color=COULEUR_ACCENT,
            text_align=ft.TextAlign.CENTER,
        )

        super().__init__(
            content=ft.Column(
                [self._lbl_titre, self._lbl_valeur, self._lbl_niveau],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=COULEUR_CARTE,
            border_radius=12,
            padding=ft.padding.symmetric(vertical=10, horizontal=8),
            expand=True,
        )

    def mettre_a_jour(self, valeur: str, niveau: str = "", couleur: str = COULEUR_ACCENT):
        self._lbl_valeur.value = valeur
        self._lbl_niveau.value = niveau
        self._lbl_niveau.color = couleur


def carte_produit(
    produit: ProduitDerma,
    is_optimal: bool = False,
    on_delete=None,
    index: int = None,
    compact: bool = False,
) -> ft.Container:
    """
    Crée une carte produit.
    
    Args:
        produit: Le produit à afficher
        is_optimal: Si True, met en évidence (nettoyant recommandé)
        on_delete: Callback de suppression (reçoit l'index)
        index: Index du produit (pour on_delete)
        compact: Si True, carte compacte (pour les lignes de moments)
    """
    couleur_cat = COULEURS_CATEGORIE.get(produit.category.value, "#fff")

    # Badges
    badges = [
        ft.Container(
            content=ft.Text(
                produit.category.value, size=9,
                weight=ft.FontWeight.BOLD, color=COULEUR_FOND,
            ),
            bgcolor=couleur_cat,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
        )
    ]
    if is_optimal:
        badges.append(ft.Text("OPTIMAL", size=8, weight=ft.FontWeight.BOLD, color=COULEUR_ACCENT))
    if produit.photosensitive:
        badges.append(ft.Text("UV!", size=8, weight=ft.FontWeight.BOLD, color=COULEUR_DANGER))

    # Contenu
    col_items = [
        ft.Row(badges, spacing=6),
        ft.Text(
            produit.nom, size=11 if compact else 14,
            weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE,
            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
        ),
    ]

    if compact:
        col_items.append(
            ft.Text(
                f"O:{produit.occlusivity} C:{produit.cleansing_power}",
                size=9, color=COULEUR_TEXTE_SECONDAIRE,
            )
        )
    else:
        details = (
            f"Occlusivité: {produit.occlusivity}/5 | "
            f"Nettoyage: {produit.cleansing_power}/5 | "
            f"{produit.active_tag.value}"
        )
        col_items.append(ft.Text(details, size=11, color=COULEUR_TEXTE_SECONDAIRE))

    content_col = ft.Column(col_items, spacing=4, expand=True)

    # Construction de la ligne
    row_items = []
    # Indicateur couleur vertical (pour les cartes pleines)
    if not compact:
        row_items.append(
            ft.Container(width=5, bgcolor=couleur_cat, border_radius=2, height=60)
        )
    row_items.append(content_col)

    if on_delete is not None and index is not None:
        row_items.append(
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_color=COULEUR_DANGER,
                icon_size=18,
                on_click=lambda e, idx=index: on_delete(idx),
            )
        )

    return ft.Container(
        content=ft.Row(row_items, spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#0d7377" if is_optimal else (COULEUR_CARTE_HOVER if compact else COULEUR_CARTE),
        border_radius=10,
        padding=ft.padding.all(8),
        width=180 if compact else None,
    )


class LigneMoment(ft.Container):
    """
    Ligne horizontale pour un moment de la journée.
    Header coloré + liste scrollable de cartes produits.
    """

    def __init__(self, moment: str):
        self.moment = moment
        couleur, titre_text = COULEURS_MOMENT.get(moment, ("#fff", moment.upper()))

        self._lbl_count = ft.Text("0 produits", size=11, color=COULEUR_TEXTE_SECONDAIRE)
        self._row_produits = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
        self._container_produits = ft.Container(
            content=self._row_produits,
            height=110,
        )

        # Message vide par défaut
        self._msg_vide = ft.Text(
            "Aucun produit", color=COULEUR_TEXTE_SECONDAIRE, size=12,
        )
        self._row_produits.controls.append(
            ft.Container(content=self._msg_vide, padding=ft.padding.all(25))
        )

        header = ft.Row(
            [
                ft.Container(width=6, height=25, bgcolor=couleur, border_radius=3),
                ft.Text(titre_text, size=14, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                ft.Container(expand=True),
                self._lbl_count,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        super().__init__(
            content=ft.Column([header, self._container_produits], spacing=5),
            bgcolor=COULEUR_PANNEAU,
            border_radius=12,
            padding=ft.padding.all(12),
        )

    def afficher_produits(self, produits: list[ProduitDerma], nettoyant_optimal: ProduitDerma = None):
        self._row_produits.controls.clear()

        if not produits:
            self._row_produits.controls.append(
                ft.Container(content=self._msg_vide, padding=ft.padding.all(25))
            )
            self._lbl_count.value = "0 produits"
            return

        self._lbl_count.value = f"{len(produits)} produits"

        for produit in produits:
            is_optimal = (
                nettoyant_optimal is not None
                and produit.nom == nettoyant_optimal.nom
            )
            self._row_produits.controls.append(
                carte_produit(produit, is_optimal=is_optimal, compact=True)
            )
