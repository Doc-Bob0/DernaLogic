"""
DermaLogic - Fenetre de selection de ville
============================================

Dialogue modal pour rechercher et selectionner une ville.
Deux onglets : recherche (API) et favoris (cache).
"""

import threading
import flet as ft
from gui.theme import (
    COULEUR_ACCENT,
    COULEUR_ACCENT_HOVER,
    COULEUR_FOND,
    COULEUR_DANGER,
    COULEUR_CARTE,
    COULEUR_CARTE_HOVER,
    COULEUR_PANNEAU,
    COULEUR_TEXTE_SECONDAIRE,
)
from api.open_meteo import ClientOpenMeteo, rechercher_villes, Localisation
from core.config import GestionnaireConfig, VilleConfig


class FenetreSelectionVille:
    """Gere le dialogue de selection de ville."""

    def __init__(
        self,
        page: ft.Page,
        client_meteo: ClientOpenMeteo,
        gestionnaire_config: GestionnaireConfig,
        callback,
    ):
        self.page = page
        self.client_meteo = client_meteo
        self.gestionnaire_config = gestionnaire_config
        self.callback = callback
        self.resultats: list[Localisation] = []

        # --- Onglet Recherche ---
        self.entry_recherche = ft.TextField(
            hint_text="Ex: Lyon, Marseille, Bordeaux...",
            expand=True,
            height=40,
            border_color=COULEUR_ACCENT,
            focused_border_color=COULEUR_ACCENT,
            on_submit=self._rechercher,
        )
        self.btn_recherche = ft.Button(
            "Rechercher",
            on_click=self._rechercher,
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_FOND,
            height=40,
        )
        self.liste_resultats = ft.ListView(spacing=4, expand=True, padding=5)
        self.liste_resultats.controls.append(
            ft.Container(
                content=ft.Text(
                    "Entrez le nom d'une ville\net appuyez sur Rechercher",
                    color=COULEUR_TEXTE_SECONDAIRE,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=40,
                alignment=ft.Alignment(0, 0),
            )
        )

        onglet_recherche = ft.Tab(
            text="Rechercher",
            content=ft.Container(
                padding=ft.Padding.only(top=10),
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.Row([self.entry_recherche, self.btn_recherche]),
                        ft.Text(
                            "Resultats",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COULEUR_TEXTE_SECONDAIRE,
                        ),
                        ft.Container(
                            expand=True,
                            bgcolor=COULEUR_PANNEAU,
                            border_radius=10,
                            content=self.liste_resultats,
                        ),
                    ],
                ),
            ),
        )

        # --- Onglet Favoris ---
        self.liste_favoris = ft.ListView(spacing=4, expand=True, padding=5)

        onglet_favoris = ft.Tab(
            text="Favoris",
            content=ft.Container(
                padding=ft.Padding.only(top=10),
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.Text(
                            "Villes favorites",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COULEUR_TEXTE_SECONDAIRE,
                        ),
                        ft.Text(
                            "Donnees meteo en cache - pas de connexion requise",
                            size=10,
                            color="#9b59b6",
                        ),
                        ft.Container(
                            expand=True,
                            bgcolor=COULEUR_PANNEAU,
                            border_radius=10,
                            content=self.liste_favoris,
                        ),
                    ],
                ),
            ),
        )

        # --- Ville actuelle ---
        self.ville_actuelle = self.gestionnaire_config.obtenir_ville_actuelle()
        est_favori = self.gestionnaire_config.est_favorite(
            self.ville_actuelle.nom, self.ville_actuelle.pays
        )
        self.btn_favori_actuel = ft.IconButton(
            icon=ft.Icons.STAR if est_favori else ft.Icons.STAR_BORDER,
            icon_color="#f1c40f",
            on_click=self._toggle_favori_ville_actuelle,
        )

        barre_actuelle = ft.Container(
            bgcolor=COULEUR_CARTE,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            content=ft.Row(
                controls=[
                    ft.Text("Ville actuelle:", size=11, color=COULEUR_TEXTE_SECONDAIRE),
                    ft.Text(
                        str(self.ville_actuelle),
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color="#ffffff",
                    ),
                    ft.Container(expand=True),
                    self.btn_favori_actuel,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # --- Tabs ---
        self.tabs = ft.Tabs(
            tabs=[onglet_recherche, onglet_favoris],
            expand=True,
            on_change=self._on_tab_change,
            indicator_color=COULEUR_ACCENT,
            label_color=COULEUR_ACCENT,
            unselected_label_color=COULEUR_TEXTE_SECONDAIRE,
        )

        # --- Dialog ---
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Gerer les villes", size=18, weight=ft.FontWeight.BOLD, color="#ffffff"
            ),
            content=ft.Container(
                width=450,
                height=450,
                content=ft.Column(
                    controls=[barre_actuelle, self.tabs],
                    expand=True,
                ),
            ),
            actions=[
                ft.TextButton(
                    "Fermer",
                    on_click=self._fermer,
                    style=ft.ButtonStyle(color=COULEUR_TEXTE_SECONDAIRE),
                )
            ],
        )

    def ouvrir(self):
        """Ouvre le dialogue."""
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def _fermer(self, e=None):
        """Ferme le dialogue."""
        self.dialog.open = False
        self.page.update()
        if self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)

    def _on_tab_change(self, e):
        """Callback changement d'onglet."""
        if e.control.selected_index == 1:
            self._actualiser_favoris()

    def _actualiser_favoris(self):
        """Actualise la liste des favoris."""
        self.liste_favoris.controls.clear()
        favoris = self.gestionnaire_config.obtenir_favorites()

        if not favoris:
            self.liste_favoris.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Aucune ville favorite\n\nRecherchez une ville et cliquez sur l'etoile\npour l'ajouter aux favoris",
                        color=COULEUR_TEXTE_SECONDAIRE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=40,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for ville in favoris:
                self.liste_favoris.controls.append(self._creer_carte_favori(ville))

        self.page.update()

    def _rechercher(self, e=None):
        """Lance la recherche de ville (threade)."""
        query = self.entry_recherche.value.strip() if self.entry_recherche.value else ""
        if not query:
            return

        self.btn_recherche.text = "..."
        self.btn_recherche.disabled = True
        self.page.update()

        def _background():
            self.resultats = rechercher_villes(query)

            self.liste_resultats.controls.clear()
            if not self.resultats:
                self.liste_resultats.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"Aucun resultat pour '{query}'",
                            color=COULEUR_DANGER,
                        ),
                        padding=30,
                    )
                )
            else:
                for loc in self.resultats:
                    self.liste_resultats.controls.append(self._creer_carte_resultat(loc))

            self.btn_recherche.text = "Rechercher"
            self.btn_recherche.disabled = False
            self.page.update()

        threading.Thread(target=_background, daemon=True).start()

    def _creer_carte_resultat(self, loc: Localisation) -> ft.Container:
        """Cree une carte pour un resultat de recherche."""
        est_favori = self.gestionnaire_config.est_favorite(loc.nom, loc.pays)

        return ft.Container(
            bgcolor=COULEUR_CARTE_HOVER,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=8, vertical=5),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.STAR if est_favori else ft.Icons.STAR_BORDER,
                        icon_color="#f1c40f",
                        icon_size=20,
                        on_click=lambda e, l=loc: self._toggle_favori_recherche(l),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                loc.nom,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#ffffff",
                            ),
                            ft.Text(
                                f"{loc.pays} ({loc.latitude:.2f}, {loc.longitude:.2f})",
                                size=11,
                                color=COULEUR_TEXTE_SECONDAIRE,
                            ),
                        ],
                    ),
                    ft.Button(
                        "Choisir",
                        on_click=lambda e, l=loc: self._selectionner_recherche(l),
                        bgcolor=COULEUR_ACCENT,
                        color=COULEUR_FOND,
                        height=30,
                        style=ft.ButtonStyle(
                            padding=ft.Padding.symmetric(horizontal=12),
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                    ),
                ],
            ),
        )

    def _creer_carte_favori(self, ville: VilleConfig) -> ft.Container:
        """Cree une carte pour une ville favorite."""
        if ville.derniere_maj:
            details = f"UV: {ville.indice_uv:.1f} | H: {ville.humidite:.0f}% | T: {ville.temperature:.1f}C"
            if ville.pm2_5:
                details += f" | PM2.5: {ville.pm2_5:.0f}"
            details += f"\nMis a jour: {ville.derniere_maj}"
        else:
            details = "Pas encore de donnees"

        return ft.Container(
            bgcolor=COULEUR_CARTE_HOVER,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=8, vertical=5),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.STAR,
                        icon_color="#f1c40f",
                        icon_size=20,
                        on_click=lambda e, v=ville: self._supprimer_favori(v),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                str(ville),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#ffffff",
                            ),
                            ft.Text(details, size=10, color=COULEUR_TEXTE_SECONDAIRE),
                        ],
                    ),
                    ft.Button(
                        "Choisir",
                        on_click=lambda e, v=ville: self._selectionner_favori(v),
                        bgcolor="#9b59b6",
                        color="#ffffff",
                        height=30,
                        style=ft.ButtonStyle(
                            padding=ft.Padding.symmetric(horizontal=12),
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                    ),
                ],
            ),
        )

    def _toggle_favori_recherche(self, loc: Localisation):
        """Bascule l'etat favori d'une ville recherchee."""
        ville = VilleConfig(
            nom=loc.nom,
            pays=loc.pays,
            latitude=loc.latitude,
            longitude=loc.longitude,
        )
        self.gestionnaire_config.basculer_favorite(ville)
        # Rafraichir la recherche
        self._rechercher()

    def _supprimer_favori(self, ville: VilleConfig):
        """Supprime une ville des favoris."""
        self.gestionnaire_config.supprimer_favorite(ville.nom, ville.pays)
        self._actualiser_favoris()

    def _toggle_favori_ville_actuelle(self, e=None):
        """Bascule l'etat favori de la ville actuelle."""
        est_favori = self.gestionnaire_config.basculer_favorite(self.ville_actuelle)
        self.btn_favori_actuel.icon = ft.Icons.STAR if est_favori else ft.Icons.STAR_BORDER
        self.page.update()

    def _selectionner_recherche(self, loc: Localisation):
        """Selectionne une ville depuis la recherche (appel API)."""
        ville = VilleConfig(
            nom=loc.nom,
            pays=loc.pays,
            latitude=loc.latitude,
            longitude=loc.longitude,
        )
        self.gestionnaire_config.definir_ville_actuelle(ville)
        self.client_meteo.definir_localisation(loc)
        self._fermer()
        self.callback(utiliser_cache=False)

    def _selectionner_favori(self, ville: VilleConfig):
        """Selectionne une ville depuis les favoris (utilise le cache)."""
        self.gestionnaire_config.definir_ville_actuelle(ville)
        loc = Localisation(
            nom=ville.nom,
            pays=ville.pays,
            latitude=ville.latitude,
            longitude=ville.longitude,
        )
        self.client_meteo.definir_localisation(loc)
        self._fermer()
        self.callback(utiliser_cache=True, ville_cache=ville)
