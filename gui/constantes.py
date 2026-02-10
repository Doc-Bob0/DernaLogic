"""
Constantes de style pour l'interface DermaLogic.

Définit les couleurs principales, les couleurs par catégorie de produit
et les couleurs par moment de la journée.
"""

# =============================================================================
# CONSTANTES DE STYLE
# =============================================================================

# Couleurs principales
COULEUR_FOND = "#0f0f1a"
COULEUR_PANNEAU = "#16213e"
COULEUR_CARTE = "#1a1a2e"
COULEUR_CARTE_HOVER = "#252545"
COULEUR_ACCENT = "#4ecca3"
COULEUR_ACCENT_HOVER = "#3db892"
COULEUR_DANGER = "#e94560"
COULEUR_TEXTE_SECONDAIRE = "#8b8b9e"
COULEUR_BORDURE = "#2a2a4a"

# Couleurs par catégorie de produit
COULEURS_CATEGORIE = {
    "cleanser": "#00b4d8",
    "treatment": "#f9ed69",
    "moisturizer": "#4ecca3",
    "protection": "#f38181",
}

# Couleurs par moment
COULEURS_MOMENT = {
    "matin": ("#f9ed69", "MATIN"),
    "journee": ("#00b4d8", "JOURNEE"),
    "soir": ("#9b59b6", "SOIR"),
    "tous": ("#4ecca3", "TOUS MOMENTS"),
}
