"""
DermaLogic - Design Tokens (Flet)
==================================

Centralise toutes les constantes de style pour l'interface Flet.
"""

import flet as ft

# =============================================================================
# COULEURS PRINCIPALES
# =============================================================================

COULEUR_FOND = "#0f0f1a"
COULEUR_PANNEAU = "#16213e"
COULEUR_CARTE = "#1a1a2e"
COULEUR_CARTE_HOVER = "#252545"
COULEUR_ACCENT = "#4ecca3"
COULEUR_ACCENT_HOVER = "#3db892"
COULEUR_DANGER = "#e94560"
COULEUR_TEXTE = "#ffffff"
COULEUR_TEXTE_SECONDAIRE = "#8b8b9e"
COULEUR_BORDURE = "#2a2a4a"
COULEUR_IA = "#9b59b6"
COULEUR_IA_HOVER = "#8e44ad"
COULEUR_FAVORI = "#f1c40f"

# =============================================================================
# COULEURS PAR CATÉGORIE / MOMENT
# =============================================================================

COULEURS_CATEGORIE = {
    "cleanser": "#00b4d8",
    "treatment": "#f9ed69",
    "moisturizer": "#4ecca3",
    "protection": "#f38181",
}

COULEURS_MOMENT = {
    "matin": ("#f9ed69", "MATIN"),
    "journee": ("#00b4d8", "JOURNÉE"),
    "soir": ("#9b59b6", "SOIR"),
    "tous": ("#4ecca3", "TOUS MOMENTS"),
}

# =============================================================================
# HELPERS COULEUR
# =============================================================================

COULEURS_UV = {
    "Faible": COULEUR_ACCENT,
    "Modere": "#f9ed69",
    "Eleve": "#f38181",
    "Tres eleve": COULEUR_DANGER,
    "Extreme": "#aa2ee6",
}

COULEURS_HUMIDITE = {
    "Tres sec": COULEUR_DANGER,
    "Sec": "#f9ed69",
    "Normal": COULEUR_ACCENT,
    "Humide": "#00b4d8",
}

COULEURS_POLLUTION = {
    "Excellent": COULEUR_ACCENT,
    "Bon": "#9be36d",
    "Modere": "#f9ed69",
    "Mauvais": "#f38181",
    "Tres mauvais": COULEUR_DANGER,
    "Inconnu": COULEUR_TEXTE_SECONDAIRE,
}

COULEURS_STRESS = {
    "low": COULEUR_ACCENT,      # 1-3
    "mid": "#f9ed69",            # 4-6
    "high": COULEUR_DANGER,      # 7-10
}


def couleur_uv(niveau: str) -> str:
    return COULEURS_UV.get(niveau, "#fff")

def couleur_humidite(niveau: str) -> str:
    return COULEURS_HUMIDITE.get(niveau, "#fff")

def couleur_pollution(niveau: str) -> str:
    return COULEURS_POLLUTION.get(niveau, "#fff")

def couleur_stress(niveau: int) -> str:
    if niveau <= 3:
        return COULEURS_STRESS["low"]
    elif niveau <= 6:
        return COULEURS_STRESS["mid"]
    return COULEURS_STRESS["high"]


# =============================================================================
# HELPERS STYLE
# =============================================================================

def titre(text: str, size: int = 24) -> ft.Text:
    """Crée un titre stylisé."""
    return ft.Text(text, size=size, weight=ft.FontWeight.BOLD, color=COULEUR_TEXTE)

def sous_titre(text: str, size: int = 11) -> ft.Text:
    """Crée un sous-titre grisé."""
    return ft.Text(text, size=size, color=COULEUR_TEXTE_SECONDAIRE)

def carte(content: ft.Control, **kwargs) -> ft.Container:
    """Crée un conteneur style carte."""
    return ft.Container(
        content=content,
        bgcolor=COULEUR_CARTE,
        border_radius=12,
        padding=ft.padding.all(12),
        **kwargs,
    )

def panneau(content: ft.Control, **kwargs) -> ft.Container:
    """Crée un conteneur style panneau."""
    return ft.Container(
        content=content,
        bgcolor=COULEUR_PANNEAU,
        border_radius=15,
        padding=ft.padding.all(15),
        **kwargs,
    )

def bouton_principal(text: str, on_click=None, **kwargs) -> ft.ElevatedButton:
    """Crée un bouton principal accent."""
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        bgcolor=COULEUR_ACCENT,
        color=COULEUR_FOND,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        **kwargs,
    )

def bouton_danger(text: str, on_click=None, **kwargs) -> ft.ElevatedButton:
    """Crée un bouton danger."""
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        bgcolor=COULEUR_DANGER,
        color=COULEUR_TEXTE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        **kwargs,
    )

def bouton_ia(text: str, on_click=None, **kwargs) -> ft.ElevatedButton:
    """Crée un bouton IA violet."""
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        bgcolor=COULEUR_IA,
        color=COULEUR_TEXTE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        **kwargs,
    )

def badge(text: str, color: str, bg: str = None) -> ft.Container:
    """Crée un badge coloré."""
    return ft.Container(
        content=ft.Text(text, size=9, weight=ft.FontWeight.BOLD, color=color),
        bgcolor=bg or COULEUR_CARTE,
        border_radius=4,
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
    )
