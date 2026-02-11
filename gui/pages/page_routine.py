"""
Page Routine - Affichage de la routine quotidienne.

Cette page affiche la routine générée automatiquement avec :
- Conditions météo du jour
- Routine matin avec checklist
- Routine soir avec checklist
- Possibilité de marquer les étapes comme terminées
"""

import flet as ft
from datetime import datetime
from typing import Optional, List, Dict, Any

from gui.theme import (
    COULEUR_FOND, COULEUR_CARTE, COULEUR_CARTE_HOVER,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_IA, couleur_uv, couleur_humidite, couleur_pollution,
    creer_titre_section, creer_carte
)
from core.generateur_routines import obtenir_generateur, ProduitRoutine, RoutineJour
from core.plateforme import obtenir_config_ui


class PageRoutine(ft.Column):
    """Page affichant la routine quotidienne du jour."""

    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 16

        self.config_ui = obtenir_config_ui()
        self.generateur = obtenir_generateur()

        self.routine_jour: Optional[RoutineJour] = None
        self.produits_coches_matin: List[str] = []
        self.produits_coches_soir: List[str] = []

        # Créer les éléments
        self._creer_elements()

    def _creer_elements(self):
        """Crée les éléments de la page."""

        # Header avec date et météo
        self.date_texte = ft.Text(
            self._formater_date(),
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COULEUR_TEXTE
        )

        self.btn_regenerer = ft.ElevatedButton(
            "🔄 Régénérer",
            on_click=lambda e: self._regenerer_routine(),
            bgcolor=COULEUR_ACCENT,
            color=COULEUR_TEXTE,
        )

        self.header = ft.Row([
            self.date_texte,
            ft.Container(expand=True),
            self.btn_regenerer
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Cartes météo compactes
        self.carte_meteo_uv = self._creer_carte_meteo_compacte("☀️", "UV", "--", "--")
        self.carte_meteo_humidite = self._creer_carte_meteo_compacte("💧", "Humidité", "--", "--")
        self.carte_meteo_pollution = self._creer_carte_meteo_compacte("🌫️", "Pollution", "--", "--")
        self.carte_meteo_temp = self._creer_carte_meteo_compacte("🌡️", "Temp", "--", "")

        self.row_meteo = ft.Row(
            [
                self.carte_meteo_uv,
                self.carte_meteo_humidite,
                self.carte_meteo_pollution,
                self.carte_meteo_temp,
            ],
            spacing=8,
            wrap=True,
        )

        # Sections routines
        self.section_matin = ft.Column(spacing=12)
        self.section_soir = ft.Column(spacing=12)

        # Message de chargement
        self.message_chargement = ft.Text(
            "⏳ Chargement de la routine...",
            size=16,
            color=COULEUR_TEXTE_SECONDAIRE,
            text_align=ft.TextAlign.CENTER
        )

        # Assembler la page
        self.controls = [
            self.header,
            ft.Divider(height=1, color=COULEUR_TEXTE_SECONDAIRE),
            self.row_meteo,
            ft.Container(height=8),
            self.message_chargement,
        ]

    def _formater_date(self) -> str:
        """Formate la date du jour."""
        maintenant = datetime.now()
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        mois = ["janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

        jour_semaine = jours[maintenant.weekday()]
        jour = maintenant.day
        mois_nom = mois[maintenant.month - 1]

        return f"{jour_semaine} {jour} {mois_nom}"

    def _creer_carte_meteo_compacte(
        self, icone: str, label: str, valeur: str, niveau: str
    ) -> ft.Container:
        """Crée une carte météo compacte."""
        return ft.Container(
            content=ft.Column([
                ft.Text(icone, size=20),
                ft.Text(label, size=10, color=COULEUR_TEXTE_SECONDAIRE),
                ft.Text(valeur, size=14, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
                ft.Text(niveau, size=9, color=COULEUR_TEXTE_SECONDAIRE),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=COULEUR_CARTE,
            border_radius=12,
            padding=12,
            width=85,
        )

    def _creer_carte_produit(self, produit: ProduitRoutine, moment: str) -> ft.Container:
        """Crée une carte pour un produit de la routine."""

        # Vérifier si le produit est coché
        liste_coches = self.produits_coches_matin if moment == "matin" else self.produits_coches_soir
        est_coche = produit.nom in liste_coches

        checkbox = ft.Checkbox(
            value=est_coche,
            on_change=lambda e, p=produit, m=moment: self._toggle_produit(p, m),
        )

        # Icône selon la catégorie
        icones = {
            "cleanser": "🧼",
            "treatment": "💊",
            "moisturizer": "💧",
            "protection": "☀️",
        }
        icone = icones.get(produit.categorie, "🧴")

        # Indicateur si produit agressif
        tag_agressif = None
        if produit.est_agressif:
            tag_agressif = ft.Container(
                content=ft.Text("⚠️ Actif", size=10, color=COULEUR_TEXTE),
                bgcolor="#ff6b6b",
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
            )

        contenu = ft.Row([
            checkbox,
            ft.Text(icone, size=20),
            ft.Column([
                ft.Text(produit.nom, size=14, weight=ft.FontWeight.W_500, color=COULEUR_TEXTE),
                ft.Text(
                    produit.categorie.capitalize(),
                    size=11,
                    color=COULEUR_TEXTE_SECONDAIRE
                ),
            ], spacing=2, expand=True),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        if tag_agressif:
            contenu.controls.append(tag_agressif)

        return ft.Container(
            content=contenu,
            bgcolor=COULEUR_CARTE if not est_coche else COULEUR_CARTE_HOVER,
            border_radius=12,
            padding=12,
            opacity=0.6 if est_coche else 1.0,
        )

    def _toggle_produit(self, produit: ProduitRoutine, moment: str):
        """Bascule l'état coché d'un produit."""
        liste_coches = self.produits_coches_matin if moment == "matin" else self.produits_coches_soir

        if produit.nom in liste_coches:
            liste_coches.remove(produit.nom)
        else:
            liste_coches.append(produit.nom)

        # Rafraîchir l'affichage
        self._afficher_routine(self.routine_jour)

    def _creer_section_routine(self, titre: str, icone: str, produits: List[ProduitRoutine], moment: str) -> ft.Container:
        """Crée une section de routine (matin ou soir)."""

        # Calculer progression
        liste_coches = self.produits_coches_matin if moment == "matin" else self.produits_coches_soir
        nb_coches = len([p for p in produits if p.nom in liste_coches])
        total = len(produits)
        progression = nb_coches / total if total > 0 else 0

        # Header de section
        header = ft.Row([
            ft.Text(icone, size=24),
            ft.Text(titre, size=20, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
            ft.Container(expand=True),
            ft.Text(
                f"{nb_coches}/{total}",
                size=14,
                color=COULEUR_ACCENT if nb_coches == total else COULEUR_TEXTE_SECONDAIRE
            )
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # Barre de progression
        barre_progression = ft.ProgressBar(
            value=progression,
            color=COULEUR_ACCENT,
            bgcolor=COULEUR_CARTE,
            height=6,
        )

        # Liste des produits
        liste_produits = ft.Column(
            [self._creer_carte_produit(p, moment) for p in produits],
            spacing=8
        )

        return ft.Container(
            content=ft.Column([
                header,
                barre_progression,
                ft.Container(height=8),
                liste_produits,
            ], spacing=8),
            bgcolor=COULEUR_FOND,
            border_radius=16,
            padding=16,
        )

    def charger_routine(self, produits_disponibles: List[Dict[str, Any]]):
        """
        Charge ou génère la routine du jour.

        Args:
            produits_disponibles: Liste des produits de l'utilisateur
        """
        try:
            # Générer la routine (ou charger si existe déjà)
            routine, nouvelle = self.generateur.generer_routine_quotidienne(
                produits_disponibles=produits_disponibles,
                force_regeneration=False
            )

            self.routine_jour = routine
            self._afficher_routine(routine)

        except Exception as e:
            print(f"Erreur chargement routine: {e}")
            self.message_chargement.value = f"❌ Erreur: {str(e)}"
            self.update()

    def _afficher_routine(self, routine: RoutineJour):
        """Affiche la routine dans l'interface."""
        # Mettre à jour les cartes météo
        if routine.conditions_meteo:
            meteo = routine.conditions_meteo

            self.carte_meteo_uv.content.controls[2].value = f"{meteo.get('indice_uv', 0):.1f}"
            self.carte_meteo_uv.content.controls[3].value = meteo.get('niveau_uv', '--')

            self.carte_meteo_humidite.content.controls[2].value = f"{meteo.get('humidite', 0):.0f}%"
            self.carte_meteo_humidite.content.controls[3].value = meteo.get('niveau_humidite', '--')

            self.carte_meteo_pollution.content.controls[2].value = f"{meteo.get('pm2_5', 0):.0f}"
            self.carte_meteo_pollution.content.controls[3].value = meteo.get('niveau_pollution', '--')

            self.carte_meteo_temp.content.controls[2].value = f"{meteo.get('temperature', 0):.1f}°C"

        # Créer les sections
        section_matin_widget = self._creer_section_routine(
            "Routine Matin", "🌅", routine.matin, "matin"
        )

        section_soir_widget = self._creer_section_routine(
            "Routine Soir", "🌙", routine.soir, "soir"
        )

        # Mettre à jour les controls
        self.controls = [
            self.header,
            ft.Divider(height=1, color=COULEUR_TEXTE_SECONDAIRE),
            self.row_meteo,
            ft.Container(height=16),
            section_matin_widget,
            ft.Container(height=16),
            section_soir_widget,
        ]

        self.update()

    def _regenerer_routine(self):
        """Force la régénération de la routine."""
        self.btn_regenerer.text = "⏳ Génération..."
        self.btn_regenerer.disabled = True
        self.update()

        # TODO: Appeler la génération avec force_regeneration=True
        # Pour l'instant, afficher un message
        self.btn_regenerer.text = "🔄 Régénérer"
        self.btn_regenerer.disabled = False
        self.update()

    def actualiser(self, produits_disponibles: List[Dict[str, Any]]):
        """
        Actualise la page (appelé lors de l'affichage).

        Args:
            produits_disponibles: Liste des produits de l'utilisateur
        """
        self.charger_routine(produits_disponibles)
