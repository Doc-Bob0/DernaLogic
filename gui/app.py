"""
DermaLogic - Application Flet
==============================

Orchestrateur principal : navigation responsive 5 pages,
double mode d'analyse IA, gestion des callbacks.
"""

import threading
import flet as ft

from gui.theme import (
    COULEUR_FOND,
    COULEUR_PANNEAU,
    COULEUR_ACCENT,
    COULEUR_DANGER,
    BREAKPOINT_MOBILE,
    creer_theme,
)
from gui.state import AppState
from gui.components.nav_bar import NavBarDesktop, creer_nav_mobile, PAGES_INDEX
from gui.pages.page_accueil import PageAccueil
from gui.pages.page_produits import PageProduits
from gui.pages.page_profil import PageProfil
from gui.pages.page_historique import PageHistorique
from gui.pages.page_parametres import PageParametres
from gui.dialogs.fenetre_selection_ville import FenetreSelectionVille
from api.open_meteo import DonneesEnvironnementales
from core.config import VilleConfig


def main(page: ft.Page):
    """Point d'entree Flet."""

    # --- Configuration de la page ---
    page.title = "DermaLogic"
    page.theme = creer_theme()
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COULEUR_FOND
    page.padding = 0
    page.window.width = 1100
    page.window.height = 750

    # --- Etat de l'application ---
    state = AppState()
    is_mobile = page.width < BREAKPOINT_MOBILE if page.width else False
    page_courante = "accueil"

    # --- Helpers ---

    def _afficher_snackbar(message: str, couleur: str = COULEUR_PANNEAU):
        """Affiche un snackbar avec un message."""
        sb = ft.SnackBar(content=ft.Text(message), bgcolor=couleur)
        page.show_dialog(sb)

    # --- Actions meteo ---

    def actualiser_donnees(e=None, utiliser_cache: bool = False, ville_cache: VilleConfig = None):
        """Actualise les donnees meteo + previsions (threade)."""
        page_accueil.set_loading(True)
        page.update()

        def _background():
            if utiliser_cache and ville_cache and ville_cache.derniere_maj:
                state.donnees_env = DonneesEnvironnementales(
                    date="",
                    heure="",
                    indice_uv=ville_cache.indice_uv,
                    indice_uv_max=ville_cache.indice_uv,
                    humidite_relative=ville_cache.humidite,
                    temperature=ville_cache.temperature,
                    pm2_5=ville_cache.pm2_5,
                )
                state.previsions = []
            else:
                state.donnees_env = state.client_meteo.obtenir_donnees_jour()

                if state.donnees_env:
                    state.gestionnaire_config.mettre_a_jour_meteo_actuelle(
                        indice_uv=state.donnees_env.indice_uv,
                        humidite=state.donnees_env.humidite_relative,
                        temperature=state.donnees_env.temperature,
                        pm2_5=state.donnees_env.pm2_5,
                    )

                    # Mettre a jour le favori si applicable
                    ville = state.gestionnaire_config.obtenir_ville_actuelle()
                    if state.gestionnaire_config.est_favorite(ville.nom, ville.pays):
                        state.gestionnaire_config.mettre_a_jour_meteo_favorite(
                            nom=ville.nom,
                            pays=ville.pays,
                            indice_uv=state.donnees_env.indice_uv,
                            humidite=state.donnees_env.humidite_relative,
                            temperature=state.donnees_env.temperature,
                            pm2_5=state.donnees_env.pm2_5,
                        )

                # Recuperer les previsions 3 jours
                try:
                    state.previsions = state.client_meteo.obtenir_previsions_3_jours()
                except Exception:
                    state.previsions = []

            page_accueil.afficher_conditions(state.donnees_env)
            page_accueil.afficher_previsions(state.previsions)
            page_accueil.set_loading(False)
            page.update()

        threading.Thread(target=_background, daemon=True).start()

    # --- Actions analyse IA ---

    def _verifier_pre_analyse() -> bool:
        """Verifie les pre-requis avant une analyse. Retourne True si OK."""
        if not state.client_gemini.est_configure():
            _afficher_snackbar("Configurez d'abord votre cle API Gemini dans Parametres", COULEUR_DANGER)
            afficher_page("parametres")
            return False

        if not state.donnees_env:
            _afficher_snackbar("Chargez d'abord les donnees meteo", COULEUR_DANGER)
            return False

        produits = state.gestionnaire_produits.obtenir_tous()
        if not produits:
            _afficher_snackbar("Ajoutez d'abord des produits dans 'Mes Produits'", COULEUR_PANNEAU)
            return False

        return True

    def lancer_analyse_rapide(e=None):
        """Lance une analyse rapide (sans instructions supplementaires)."""
        if not _verifier_pre_analyse():
            return

        page_accueil.set_analyse_loading(True)
        page.update()

        def _background():
            ville = state.gestionnaire_config.obtenir_ville_actuelle()
            resultat = state.analyseur.analyser(
                conditions_actuelles=state.donnees_env,
                previsions=state.previsions,
                ville=ville.nom,
                mode="rapide",
            )

            page_accueil.set_analyse_loading(False)

            if "erreur" in resultat:
                page_accueil.afficher_erreur_analyse(resultat["erreur"])
            else:
                page_accueil.afficher_resultat_ia(resultat)

            page.update()

        threading.Thread(target=_background, daemon=True).start()

    def lancer_analyse_detaille(instructions: str, niveau_stress: int):
        """Lance une analyse detaillee avec instructions du jour."""
        if not _verifier_pre_analyse():
            return

        page_accueil.set_analyse_loading(True)
        page.update()

        def _background():
            ville = state.gestionnaire_config.obtenir_ville_actuelle()
            resultat = state.analyseur.analyser(
                conditions_actuelles=state.donnees_env,
                previsions=state.previsions,
                ville=ville.nom,
                mode="detaille",
                instructions_jour=instructions,
                niveau_stress_jour=niveau_stress,
            )

            page_accueil.set_analyse_loading(False)

            if "erreur" in resultat:
                page_accueil.afficher_erreur_analyse(resultat["erreur"])
            else:
                page_accueil.afficher_resultat_ia(resultat)

            page.update()

        threading.Thread(target=_background, daemon=True).start()

    # --- Actions ville ---

    def ouvrir_selection_ville(e=None):
        """Ouvre le dialogue de selection de ville."""
        fenetre = FenetreSelectionVille(
            page,
            state.client_meteo,
            state.gestionnaire_config,
            _on_ville_changee,
        )
        fenetre.ouvrir()

    def _on_ville_changee(utiliser_cache: bool = False, ville_cache: VilleConfig = None):
        """Callback quand la ville est changee."""
        nom = state.client_meteo.nom_ville
        nav_desktop.set_ville(nom)
        if mobile_appbar:
            mobile_appbar.title = ft.Text(f"DermaLogic - {nom}", color="#ffffff")
        page.update()
        actualiser_donnees(utiliser_cache=utiliser_cache, ville_cache=ville_cache)

    # --- Callback cle API changee ---

    def _on_cle_changee():
        """Callback quand la cle API Gemini est modifiee dans parametres."""
        state.actualiser_client_gemini()

    # --- Callback export JSON ---

    def _exporter_donnees() -> dict:
        """Retourne toutes les donnees pour l'export JSON."""
        profil = state.gestionnaire_profil.obtenir()
        produits = state.gestionnaire_produits.obtenir_tous()
        historique = state.gestionnaire_historique.obtenir_tous()
        config = state.gestionnaire_config.obtenir_ville_actuelle()

        return {
            "profil": profil.vers_dict(),
            "produits": [p.vers_dict() for p in produits],
            "historique": [e.vers_dict() for e in historique],
            "ville": {
                "nom": config.nom,
                "pays": config.pays,
                "latitude": config.latitude,
                "longitude": config.longitude,
            },
        }

    # --- Pages ---

    page_accueil = PageAccueil(
        on_actualiser=actualiser_donnees,
        on_analyser_rapide=lancer_analyse_rapide,
        on_analyser_detaille=lancer_analyse_detaille,
    )

    page_produits = PageProduits(
        page,
        state.gestionnaire_produits,
        get_api_key=lambda: state.gestionnaire_settings.obtenir_gemini_key(),
    )

    page_profil = PageProfil(page, state.gestionnaire_profil)

    page_historique = PageHistorique(page, state.gestionnaire_historique)

    page_parametres = PageParametres(
        page,
        state.gestionnaire_settings,
        on_cle_changee=_on_cle_changee,
        exporter_callback=_exporter_donnees,
    )

    # --- Content area ---

    content_area = ft.Container(expand=True, content=page_accueil)

    def afficher_page(nom: str):
        nonlocal page_courante
        page_courante = nom

        if nom == "accueil":
            content_area.content = page_accueil
        elif nom == "produits":
            page_produits.actualiser_liste()
            content_area.content = page_produits
        elif nom == "profil":
            page_profil.charger_profil()
            content_area.content = page_profil
        elif nom == "historique":
            page_historique.actualiser_liste()
            content_area.content = page_historique
        elif nom == "parametres":
            content_area.content = page_parametres

        nav_desktop.set_active(nom)

        # Mettre a jour la nav mobile
        if page.navigation_bar:
            page.navigation_bar.selected_index = PAGES_INDEX.get(nom, 0)

        page.update()

    # --- Navigation ---

    nav_desktop = NavBarDesktop(
        on_page_change=afficher_page,
        on_ville_click=ouvrir_selection_ville,
        nom_ville=state.client_meteo.nom_ville,
    )

    nav_mobile_bar = creer_nav_mobile(on_page_change=afficher_page)

    mobile_appbar = ft.AppBar(
        title=ft.Text(f"DermaLogic - {state.client_meteo.nom_ville}", color="#ffffff"),
        bgcolor=COULEUR_PANNEAU,
        actions=[
            ft.IconButton(
                ft.Icons.LOCATION_CITY,
                icon_color=COULEUR_ACCENT,
                on_click=ouvrir_selection_ville,
                tooltip="Changer de ville",
            ),
        ],
    )

    # --- Responsive Layout ---

    def _build_layout():
        nonlocal is_mobile
        page.controls.clear()

        if is_mobile:
            page.appbar = mobile_appbar
            page.navigation_bar = nav_mobile_bar
            nav_mobile_bar.selected_index = PAGES_INDEX.get(page_courante, 0)
            page.controls.append(content_area)
        else:
            page.appbar = None
            page.navigation_bar = None
            page.controls.append(nav_desktop)
            page.controls.append(content_area)

        page.update()

    def on_resize(e):
        nonlocal is_mobile
        new_is_mobile = page.width < BREAKPOINT_MOBILE if page.width else False
        if new_is_mobile != is_mobile:
            is_mobile = new_is_mobile
            _build_layout()

    page.on_resize = on_resize

    # --- Demarrage ---
    _build_layout()
    actualiser_donnees()
