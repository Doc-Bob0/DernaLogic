"""
DermaLogic - Fenêtre de Sélection de Ville (Flet)
====================================================

Dialogue pour rechercher et sélectionner une ville.
"""

import flet as ft
import threading

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE, COULEUR_CARTE_HOVER,
    COULEUR_ACCENT, COULEUR_ACCENT_HOVER, COULEUR_TEXTE,
    COULEUR_TEXTE_SECONDAIRE, COULEUR_DANGER, COULEUR_FAVORI,
    COULEUR_BORDURE,
)
from api.open_meteo import ClientOpenMeteo, Localisation, rechercher_villes
from core.config import GestionnaireConfig, VilleConfig


def ouvrir_selection_ville(page: ft.Page, client_meteo: ClientOpenMeteo, gestionnaire_config: GestionnaireConfig, callback):
    """
    Ouvre un dialogue pour rechercher et sélectionner une ville.

    Args:
        page: Page Flet
        client_meteo: Client API Open-Meteo
        gestionnaire_config: Gestionnaire de configuration
        callback: Fonction à appeler quand une ville est sélectionnée
    """
    onglet_actif = {"val": "recherche"}
    resultats_ref = {"data": []}

    # ── Ville actuelle ──
    ville_actuelle = gestionnaire_config.obtenir_ville_actuelle()
    est_favori = gestionnaire_config.est_favorite(ville_actuelle.nom, ville_actuelle.pays)

    btn_etoile_actuelle = ft.TextButton(
        "⭐" if est_favori else "☆",
        style=ft.ButtonStyle(
            bgcolor=COULEUR_FAVORI if est_favori else COULEUR_CARTE_HOVER,
            color=COULEUR_FOND if est_favori else COULEUR_FAVORI,
        ),
    )

    # ── Onglets ──
    btn_onglet_recherche = ft.ElevatedButton(
        "Rechercher", width=120,
        bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
    btn_onglet_favoris = ft.ElevatedButton(
        "⭐ Favoris", width=120,
        bgcolor=COULEUR_CARTE, color=COULEUR_TEXTE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    # ── Onglet recherche ──
    entry_recherche = ft.TextField(
        hint_text="Ex: Lyon, Marseille, Bordeaux...",
        bgcolor=COULEUR_CARTE, border_color=COULEUR_BORDURE,
        color=COULEUR_TEXTE, height=40, expand=True,
    )
    btn_recherche = ft.ElevatedButton(
        "Rechercher", bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
        width=100, height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
    col_resultats = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4)

    frame_recherche = ft.Column([
        ft.Row([entry_recherche, btn_recherche], spacing=10),
        ft.Text("Résultats", size=12, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE_SECONDAIRE),
        ft.Container(
            content=col_resultats,
            bgcolor=COULEUR_PANNEAU, border_radius=10,
            padding=ft.padding.all(8),
            height=220,
        ),
    ], spacing=8)

    # ── Onglet favoris ──
    col_favoris = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=4)

    frame_favoris = ft.Column([
        ft.Text("Villes favorites", size=12, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE_SECONDAIRE),
        ft.Text("Données météo en cache - pas de connexion requise", size=10, color="#9b59b6"),
        ft.Container(
            content=col_favoris,
            bgcolor=COULEUR_PANNEAU, border_radius=10,
            padding=ft.padding.all(8),
            height=220,
        ),
    ], spacing=5)

    # ── Conteneur principal ──
    contenu_onglets = ft.Column()
    contenu_onglets.controls.append(frame_recherche)

    def changer_onglet(onglet):
        onglet_actif["val"] = onglet
        contenu_onglets.controls.clear()
        if onglet == "recherche":
            contenu_onglets.controls.append(frame_recherche)
            btn_onglet_recherche.bgcolor = COULEUR_ACCENT
            btn_onglet_recherche.color = COULEUR_FOND
            btn_onglet_favoris.bgcolor = COULEUR_CARTE
            btn_onglet_favoris.color = COULEUR_TEXTE
        else:
            actualiser_favoris()
            contenu_onglets.controls.append(frame_favoris)
            btn_onglet_favoris.bgcolor = COULEUR_FAVORI
            btn_onglet_favoris.color = COULEUR_FOND
            btn_onglet_recherche.bgcolor = COULEUR_CARTE
            btn_onglet_recherche.color = COULEUR_TEXTE
        page.update()

    btn_onglet_recherche.on_click = lambda e: changer_onglet("recherche")
    btn_onglet_favoris.on_click = lambda e: changer_onglet("favoris")

    # ── Fonctions recherche ──
    def _rechercher(e):
        query = entry_recherche.value.strip()
        if not query:
            return

        btn_recherche.text = "..."
        page.update()

        resultats_ref["data"] = rechercher_villes(query)
        col_resultats.controls.clear()

        if not resultats_ref["data"]:
            col_resultats.controls.append(
                ft.Text(f"Aucun résultat pour '{query}'", color=COULEUR_DANGER)
            )
        else:
            for loc in resultats_ref["data"]:
                col_resultats.controls.append(_creer_carte_resultat(loc))

        btn_recherche.text = "Rechercher"
        page.update()

    def _creer_carte_resultat(loc: Localisation) -> ft.Container:
        est_fav = gestionnaire_config.est_favorite(loc.nom, loc.pays)
        return ft.Container(
            content=ft.Row([
                ft.TextButton(
                    "⭐" if est_fav else "☆",
                    on_click=lambda e, l=loc: _toggle_favori(l),
                    style=ft.ButtonStyle(
                        bgcolor=COULEUR_FAVORI if est_fav else COULEUR_CARTE,
                        color=COULEUR_FOND if est_fav else COULEUR_FAVORI,
                    ),
                ),
                ft.Column([
                    ft.Text(loc.nom, size=14, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Text(f"{loc.pays} ({loc.latitude:.2f}, {loc.longitude:.2f})",
                            size=11, color=COULEUR_TEXTE_SECONDAIRE),
                ], spacing=2, expand=True),
                ft.ElevatedButton(
                    "Choisir",
                    on_click=lambda e, l=loc: _selectionner_recherche(l),
                    bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
                    width=70, height=30,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COULEUR_CARTE_HOVER, border_radius=8,
            padding=ft.padding.all(6),
        )

    btn_recherche.on_click = _rechercher
    entry_recherche.on_submit = _rechercher

    # ── Fonctions favoris ──
    def actualiser_favoris():
        col_favoris.controls.clear()
        favoris = gestionnaire_config.obtenir_favorites()
        if not favoris:
            col_favoris.controls.append(
                ft.Text("Aucune ville favorite\n\nRecherchez une ville et cliquez sur ⭐",
                        color=COULEUR_TEXTE_SECONDAIRE, text_align=ft.TextAlign.CENTER)
            )
            return
        for ville in favoris:
            col_favoris.controls.append(_creer_carte_favori(ville))

    def _creer_carte_favori(ville: VilleConfig) -> ft.Container:
        details = ""
        if ville.derniere_maj:
            details = f"UV: {ville.indice_uv:.1f} | H: {ville.humidite:.0f}% | T: {ville.temperature:.1f}°C"
            if ville.pm2_5:
                details += f" | PM2.5: {ville.pm2_5:.0f}"
            details += f"\nMàj: {ville.derniere_maj}"
        else:
            details = "Pas encore de données"

        return ft.Container(
            content=ft.Row([
                ft.TextButton(
                    "⭐",
                    on_click=lambda e, v=ville: _supprimer_favori(v),
                    style=ft.ButtonStyle(bgcolor=COULEUR_FAVORI, color=COULEUR_FOND),
                ),
                ft.Column([
                    ft.Text(str(ville), size=14, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                    ft.Text(details, size=10, color=COULEUR_TEXTE_SECONDAIRE),
                ], spacing=2, expand=True),
                ft.ElevatedButton(
                    "Choisir",
                    on_click=lambda e, v=ville: _selectionner_favori(v),
                    bgcolor="#9b59b6", color=COULEUR_TEXTE,
                    width=70, height=30,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COULEUR_CARTE_HOVER, border_radius=8,
            padding=ft.padding.all(6),
        )

    def _toggle_favori(loc: Localisation):
        ville = VilleConfig(nom=loc.nom, pays=loc.pays, latitude=loc.latitude, longitude=loc.longitude)
        gestionnaire_config.basculer_favorite(ville)
        _rechercher(None)

    def _supprimer_favori(ville: VilleConfig):
        gestionnaire_config.supprimer_favorite(ville.nom, ville.pays)
        actualiser_favoris()
        page.update()

    def _selectionner_recherche(loc: Localisation):
        ville = VilleConfig(nom=loc.nom, pays=loc.pays, latitude=loc.latitude, longitude=loc.longitude)
        gestionnaire_config.definir_ville_actuelle(ville)
        client_meteo.definir_localisation(loc)
        page.close(dlg)
        callback(utiliser_cache=False)

    def _selectionner_favori(ville: VilleConfig):
        gestionnaire_config.definir_ville_actuelle(ville)
        loc = Localisation(nom=ville.nom, pays=ville.pays, latitude=ville.latitude, longitude=ville.longitude)
        client_meteo.definir_localisation(loc)
        page.close(dlg)
        callback(utiliser_cache=True, ville_cache=ville)

    def _toggle_favori_actuelle(e):
        est_fav = gestionnaire_config.basculer_favorite(ville_actuelle)
        btn_etoile_actuelle.text = "⭐" if est_fav else "☆"
        page.update()

    btn_etoile_actuelle.on_click = _toggle_favori_actuelle

    main_content = ft.Column([
        ft.Text("Gérer les villes", size=18, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE,
                text_align=ft.TextAlign.CENTER),
        ft.Row([btn_onglet_recherche, btn_onglet_favoris], spacing=10),
        ft.Container(
            content=ft.Row([
                ft.Text("Ville actuelle:", size=11, color=COULEUR_TEXTE_SECONDAIRE),
                ft.Text(str(ville_actuelle), size=13, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                ft.Container(expand=True),
                btn_etoile_actuelle,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COULEUR_CARTE, border_radius=10,
            padding=ft.padding.all(8),
        ),
        contenu_onglets,
    ], spacing=10, width=450, height=450)

    dlg = ft.AlertDialog(
        title=ft.Text(""),
        content=main_content,
        bgcolor=COULEUR_FOND,
    )

    page.open(dlg)
