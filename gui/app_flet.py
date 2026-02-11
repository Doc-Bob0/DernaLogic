"""
DermaLogic - Application Principale (Flet)
============================================

Point d'entrée de l'interface Flet.
Gère la navigation entre les pages et les données globales.
"""

import flet as ft
import threading

from gui.theme import (
    COULEUR_FOND, COULEUR_PANNEAU, COULEUR_CARTE, COULEUR_CARTE_HOVER,
    COULEUR_ACCENT, COULEUR_TEXTE, COULEUR_TEXTE_SECONDAIRE,
    COULEUR_DANGER, COULEUR_IA,
    couleur_uv, couleur_humidite, couleur_pollution,
)
from gui.gestionnaire_produits import GestionnaireProduits
from gui.pages.page_accueil import PageAccueil
from gui.pages.page_produits import PageProduits
from gui.pages.page_historique import PageHistorique
from gui.pages.page_profil import PageProfil

from gui.dialogs.formulaire_produit import ouvrir_formulaire_produit
from gui.dialogs.recherche_ia import ouvrir_recherche_ia
from gui.dialogs.selection_ville import ouvrir_selection_ville
from gui.dialogs.analyse_ia import ouvrir_analyse_ia_dialog

# Layouts adaptatifs
from gui.layouts import LayoutDesktop, LayoutMobile
from core.plateforme import obtenir_info_plateforme, obtenir_config_ui

from api.open_meteo import ClientOpenMeteo, Localisation, DonneesEnvironnementales
from api.gemini import ClientGemini, ResultatRoutineIA, RoutineMoment
from core.algorithme import (
    ProduitDerma, ConditionsEnvironnementales, MoteurDecision, ResultatDecision,
)
from core.config import GestionnaireConfig, VilleConfig
from core.historique import (
    GestionnaireHistorique, ConditionsAnalyse, ProduitAnalyse,
)
from core.profil import GestionnaireProfil


class ApplicationFlet:
    """
    Application principale DermaLogic en Flet.

    Gère :
    - Navigation entre pages (accueil, produits, historique, profil)
    - Données environnementales (API Open-Meteo)
    - Analyse locale et IA
    - Historique des analyses
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DermaLogic"
        self.page.bgcolor = COULEUR_FOND
        self.page.padding = 0

        # ── Détection de plateforme ──
        self.info_plateforme = obtenir_info_plateforme()
        self.config_ui = obtenir_config_ui()

        # Adapter la taille de fenêtre selon la plateforme
        if self.info_plateforme.est_mobile:
            # Mobile: plein écran ou taille typique smartphone
            self.page.window.width = self.info_plateforme.largeur_ecran_estimee
            self.page.window.height = self.info_plateforme.hauteur_ecran_estimee
        else:
            # Desktop: taille par défaut
            self.page.window.width = 1100
            self.page.window.height = 750

        # ── Services ──
        self.gestionnaire_config = GestionnaireConfig()
        self.gestionnaire = GestionnaireProduits()
        self.gestionnaire_historique = GestionnaireHistorique()
        self.gestionnaire_profil = GestionnaireProfil()
        self.donnees_env: DonneesEnvironnementales = None

        self.client_gemini = ClientGemini()

        # Client météo
        ville_config = self.gestionnaire_config.obtenir_ville_actuelle()
        self.client_meteo = ClientOpenMeteo()
        self.client_meteo.definir_localisation(Localisation(
            nom=ville_config.nom,
            pays=ville_config.pays,
            latitude=ville_config.latitude,
            longitude=ville_config.longitude,
        ))

        # ── Pages ──
        self.page_accueil = PageAccueil(self)
        self.page_produits = PageProduits(
            self.gestionnaire,
            on_ouvrir_formulaire=self._ouvrir_formulaire,
            on_ajouter_ia=self._ouvrir_recherche_ia,
        )
        self.page_historique = PageHistorique(self.gestionnaire_historique)
        self.page_profil = PageProfil(self.gestionnaire_profil)

        # ── Layout adaptatif ──
        self._creer_layout()
        self._afficher_page("accueil")
        self.actualiser_donnees()

    def _creer_layout(self):
        """Crée le layout adaptatif selon la plateforme."""

        # Créer le layout approprié
        if self.info_plateforme.est_mobile:
            self.layout = LayoutMobile(
                page=self.page,
                on_navigation=self._navigation_callback,
                nom_ville=self.client_meteo.nom_ville
            )
        else:
            self.layout = LayoutDesktop(
                page=self.page,
                on_navigation=self._navigation_callback,
                nom_ville=self.client_meteo.nom_ville
            )

        # Configurer les callbacks
        self.layout.configurer_callbacks({
            "changer_ville": self._ouvrir_selection_ville
        })

        # Conteneur de pages (pour compatibilité avec le code existant)
        self.vue_pages = ft.Column(expand=True)

        # Ajouter le layout à la page
        self.page.add(self.layout.obtenir_layout())

    def _navigation_callback(self, page_id: str):
        """Callback appelé lors du changement de page."""
        self._afficher_page(page_id)

    def _afficher_page(self, nom: str):
        """Affiche une page et met à jour la navigation."""
        # Créer un conteneur avec padding adapté à la plateforme
        padding_value = self.config_ui.espacement_base if self.info_plateforme.est_mobile else 15

        contenu_wrapper = ft.Container(
            expand=True,
            padding=ft.padding.all(padding_value),
        )

        if nom == "accueil":
            contenu_wrapper.content = self.page_accueil
            self.layout.definir_contenu(contenu_wrapper)
            self.page.update()
        elif nom == "produits":
            contenu_wrapper.content = self.page_produits
            self.layout.definir_contenu(contenu_wrapper)
            self.page.update()
            self.page_produits.actualiser_liste()
        elif nom == "historique":
            contenu_wrapper.content = self.page_historique
            self.layout.definir_contenu(contenu_wrapper)
            self.page.update()
            self.page_historique.actualiser()
        elif nom == "profil":
            contenu_wrapper.content = self.page_profil
            self.layout.definir_contenu(contenu_wrapper)
            self.page.update()
            self.page_profil.actualiser()

    # =========================================================================
    # DONNÉES MÉTÉO
    # =========================================================================

    def actualiser_donnees(self, utiliser_cache: bool = False, ville_cache: VilleConfig = None):
        """Actualise les données météo."""
        self.page_accueil.btn_actualiser.text = "..."
        self.page.update()

        if utiliser_cache and ville_cache and ville_cache.derniere_maj:
            self.donnees_env = DonneesEnvironnementales(
                indice_uv=ville_cache.indice_uv,
                humidite_relative=ville_cache.humidite,
                temperature=ville_cache.temperature,
                pm2_5=ville_cache.pm2_5,
            )
        else:
            self.donnees_env = self.client_meteo.obtenir_donnees_jour()

            if self.donnees_env:
                self.gestionnaire_config.mettre_a_jour_meteo_actuelle(
                    indice_uv=self.donnees_env.indice_uv,
                    humidite=self.donnees_env.humidite_relative,
                    temperature=self.donnees_env.temperature,
                    pm2_5=self.donnees_env.pm2_5,
                )
                ville = self.gestionnaire_config.obtenir_ville_actuelle()
                if self.gestionnaire_config.est_favorite(ville.nom, ville.pays):
                    self.gestionnaire_config.mettre_a_jour_meteo_favorite(
                        nom=ville.nom, pays=ville.pays,
                        indice_uv=self.donnees_env.indice_uv,
                        humidite=self.donnees_env.humidite_relative,
                        temperature=self.donnees_env.temperature,
                        pm2_5=self.donnees_env.pm2_5,
                    )

        if self.donnees_env:
            self.page_accueil.carte_uv.mettre_a_jour(
                f"{self.donnees_env.indice_uv:.1f}",
                self.donnees_env.niveau_uv,
                couleur_uv(self.donnees_env.niveau_uv),
            )
            self.page_accueil.carte_humidite.mettre_a_jour(
                f"{self.donnees_env.humidite_relative:.0f}%",
                self.donnees_env.niveau_humidite,
                couleur_humidite(self.donnees_env.niveau_humidite),
            )
            pm = f"{self.donnees_env.pm2_5:.0f}" if self.donnees_env.pm2_5 else "--"
            self.page_accueil.carte_pollution.mettre_a_jour(
                f"{pm} µg/m³",
                self.donnees_env.niveau_pollution,
                couleur_pollution(self.donnees_env.niveau_pollution),
            )
            self.page_accueil.carte_temp.mettre_a_jour(
                f"{self.donnees_env.temperature:.1f}°C",
                self.donnees_env.heure if hasattr(self.donnees_env, 'heure') else "",
            )
        else:
            for carte in [
                self.page_accueil.carte_uv,
                self.page_accueil.carte_humidite,
                self.page_accueil.carte_pollution,
                self.page_accueil.carte_temp,
            ]:
                carte.mettre_a_jour("Erreur", "Échec", COULEUR_DANGER)

        self.page_accueil.btn_actualiser.text = "Actualiser"
        self.label_ville.value = self.client_meteo.nom_ville
        self.page.update()

    # =========================================================================
    # ANALYSES
    # =========================================================================

    def lancer_analyse(self):
        """Lance l'analyse rapide (algorithme local)."""
        if not self.donnees_env:
            self._snack("Chargez d'abord les données météo", COULEUR_DANGER)
            return

        produits = self.gestionnaire.obtenir_tous()
        if not produits:
            self._snack("Ajoutez d'abord des produits dans 'Mes Produits'", COULEUR_DANGER)
            return

        self.page_accueil.btn_analyse_simple.text = "⏳ Analyse..."
        self.page.update()

        conditions = ConditionsEnvironnementales(
            indice_uv=self.donnees_env.indice_uv,
            humidite=self.donnees_env.humidite_relative,
            pm2_5=self.donnees_env.pm2_5,
        )
        moteur = MoteurDecision(produits)
        resultat = moteur.analyser(conditions)

        self._sauvegarder_analyse_historique(resultat)
        self.page_accueil.afficher_resultat(resultat)
        self.page_accueil.btn_analyse_simple.text = "⚡ Analyse rapide"
        self.page.update()

    def ouvrir_analyse_ia(self):
        """Ouvre le dialogue d'analyse IA."""
        if not self.donnees_env:
            self._snack("Chargez d'abord les données météo", COULEUR_DANGER)
            return
        produits = self.gestionnaire.obtenir_tous()
        if not produits:
            self._snack("Ajoutez d'abord des produits dans 'Mes Produits'", COULEUR_DANGER)
            return
        ouvrir_analyse_ia_dialog(self.page, self._executer_analyse_ia)

    def _executer_analyse_ia(self, instructions: str = ""):
        """Exécute l'analyse IA personnalisée."""
        self.page_accueil.btn_analyse_ia.text = "⏳ IA en cours..."
        self.page_accueil.btn_analyse_ia.disabled = True
        self.page.update()

        def _run():
            try:
                produits = self.gestionnaire.obtenir_tous()
                produits_dicts = [
                    {
                        "nom": p.nom,
                        "category": p.category.value,
                        "moment": p.moment.value,
                        "photosensitive": p.photosensitive,
                        "occlusivity": p.occlusivity,
                        "cleansing_power": p.cleansing_power,
                        "active_tag": p.active_tag.value,
                    }
                    for p in produits
                ]

                ville = self.gestionnaire_config.obtenir_ville_actuelle()
                donnees_env = {
                    "ville": ville.nom,
                    "temperature": self.donnees_env.temperature,
                    "indice_uv": self.donnees_env.indice_uv,
                    "niveau_uv": self.donnees_env.niveau_uv,
                    "humidite": self.donnees_env.humidite_relative,
                    "niveau_humidite": self.donnees_env.niveau_humidite,
                    "pm2_5": self.donnees_env.pm2_5,
                    "niveau_pollution": self.donnees_env.niveau_pollution,
                }

                profil_texte = self.gestionnaire_profil.generer_contexte_ia()
                etat_texte = self.gestionnaire_profil.etat_quotidien.to_prompt()

                resultat = self.client_gemini.analyser_routine(
                    produits=produits_dicts,
                    donnees_env=donnees_env,
                    profil_utilisateur=profil_texte,
                    etat_quotidien=etat_texte,
                    instructions=instructions,
                )

                if resultat.succes:
                    self._afficher_resultat_ia(resultat)
                else:
                    self._snack(f"Erreur IA: {resultat.erreur}", COULEUR_DANGER)

            except Exception as e:
                self._snack(f"Erreur: {str(e)}", COULEUR_DANGER)
            finally:
                self.page_accueil.btn_analyse_ia.text = "🤖 Analyse IA personnalisée"
                self.page_accueil.btn_analyse_ia.disabled = False
                self.page.update()

        threading.Thread(target=_run, daemon=True).start()

    def _afficher_resultat_ia(self, resultat: ResultatRoutineIA):
        """Affiche le résultat IA dans un dialog."""
        moments = [
            ("☀️ MATIN", resultat.matin, COULEUR_ACCENT),
            ("🌤️ JOURNÉE", resultat.journee, "#f9ed69"),
            ("🌙 SOIR", resultat.soir, "#9b59b6"),
        ]

        sections = []

        # Alertes
        if resultat.alertes:
            alertes_col = ft.Column(
                [ft.Text(f"⚠️ {a}", size=11, color=COULEUR_DANGER) for a in resultat.alertes],
                spacing=3,
            )
            sections.append(
                ft.Container(content=alertes_col, bgcolor="#2a1a2a", border_radius=10, padding=ft.padding.all(10))
            )

        for titre, moment, color in moments:
            sections.append(self._creer_section_moment_ia(titre, moment, color))

        dlg = ft.AlertDialog(
            title=ft.Text("🤖 Votre routine personnalisée", size=22, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE),
            content=ft.Column(sections, scroll=ft.ScrollMode.AUTO, spacing=8, width=650, height=500),
            actions=[
                ft.ElevatedButton(
                    "Fermer",
                    on_click=lambda e: self.page.close(dlg),
                    bgcolor=COULEUR_ACCENT, color=COULEUR_FOND,
                ),
            ],
            bgcolor=COULEUR_FOND,
        )
        self.page.open(dlg)

    def _creer_section_moment_ia(self, titre: str, moment: RoutineMoment, couleur: str) -> ft.Container:
        """Crée une section pour un moment dans le résultat IA."""
        items = [
            ft.Container(
                content=ft.Text(titre, size=14, weight=ft.FontWeight.BOLD, color=COULEUR_FOND,
                                text_align=ft.TextAlign.CENTER),
                bgcolor=couleur, border_radius=8, height=35,
                alignment=ft.Alignment(0, 0),
            ),
        ]

        if moment.conseils:
            items.append(ft.Text(moment.conseils, size=12, color=COULEUR_TEXTE))

        if moment.produits:
            for produit in moment.produits:
                row = [
                    ft.Text(f"• {produit.nom}", size=12, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE, expand=True),
                ]
                if produit.justification:
                    row.append(
                        ft.IconButton(
                            icon=ft.Icons.INFO_OUTLINE, icon_size=18,
                            icon_color=COULEUR_TEXTE_SECONDAIRE,
                            tooltip=produit.justification,
                        )
                    )
                items.append(
                    ft.Container(
                        content=ft.Row(row, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=COULEUR_CARTE, border_radius=8,
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    )
                )

        return ft.Container(
            content=ft.Column(items, spacing=5),
            bgcolor=COULEUR_PANNEAU, border_radius=12,
            padding=ft.padding.all(10),
        )

    # =========================================================================
    # DIALOGUES
    # =========================================================================

    def _ouvrir_formulaire(self, valeurs: dict = None):
        """Ouvre le formulaire d'ajout de produit."""
        ouvrir_formulaire_produit(
            self.page, self.gestionnaire,
            callback=lambda: self.page_produits.actualiser_liste(),
            valeurs=valeurs,
        )

    def _ouvrir_recherche_ia(self):
        """Ouvre la recherche IA."""
        def on_resultat_ia(valeurs: dict):
            self._ouvrir_formulaire(valeurs)

        ouvrir_recherche_ia(self.page, self.gestionnaire, on_resultat_ia)

    def _ouvrir_selection_ville(self):
        """Ouvre la sélection de ville."""
        ouvrir_selection_ville(
            self.page, self.client_meteo, self.gestionnaire_config,
            self._on_ville_changee,
        )

    def _on_ville_changee(self, utiliser_cache: bool = False, ville_cache: VilleConfig = None):
        """Callback quand la ville est changée."""
        # Mettre à jour le layout avec le nouveau nom de ville
        self.layout.mettre_a_jour_ville(self.client_meteo.nom_ville)
        self.actualiser_donnees(utiliser_cache=utiliser_cache, ville_cache=ville_cache)

    # =========================================================================
    # HISTORIQUE
    # =========================================================================

    def _sauvegarder_analyse_historique(self, resultat: ResultatDecision):
        """Sauvegarde le résultat dans l'historique."""
        ville = self.gestionnaire_config.obtenir_ville_actuelle()
        conditions = ConditionsAnalyse(
            ville=ville.nom, pays=ville.pays,
            indice_uv=self.donnees_env.indice_uv,
            niveau_uv=self.donnees_env.niveau_uv,
            humidite=self.donnees_env.humidite_relative,
            niveau_humidite=self.donnees_env.niveau_humidite,
            temperature=self.donnees_env.temperature,
            pm2_5=self.donnees_env.pm2_5,
            niveau_pollution=self.donnees_env.niveau_pollution,
        )

        def convertir(produits_list):
            return [
                ProduitAnalyse(
                    nom=p.nom, category=p.category.value,
                    moment=p.moment.value, active_tag=p.active_tag.value,
                    exclu=False, raison_exclusion="",
                )
                for p in produits_list
            ]

        self.gestionnaire_historique.ajouter_analyse(
            conditions=conditions,
            produits_matin=convertir(resultat.matin.produits),
            produits_journee=convertir(resultat.journee.produits),
            produits_soir=convertir(resultat.soir.produits),
            alertes=resultat.filtres_appliques,
        )

    # =========================================================================
    # UTILS
    # =========================================================================

    def _snack(self, message: str, color: str = COULEUR_ACCENT):
        """Affiche une notification."""
        self.page.open(
            ft.SnackBar(
                content=ft.Text(message, color=COULEUR_TEXTE),
                bgcolor=color,
            )
        )


def lancer_application():
    """Lance l'application DermaLogic avec Flet."""
    ft.app(target=lambda page: ApplicationFlet(page))
