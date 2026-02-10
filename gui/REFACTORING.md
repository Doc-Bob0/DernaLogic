# Plan de refactorisation de gui/interface.py

## Objectif

Diviser l'énorme fichier `interface.py` (3095 lignes) en modules séparés pour améliorer la maintenabilité.

## Structure cible

```
gui/
├── __init__.py                    # Point d'entrée, réexporte tout
├── constantes.py                   # ✅ FAIT - Couleurs et constantes
├── composants.py                   # ✅ FAIT - Widgets réutilisables
├── gestionnaire_produits.py        # ✅ FAIT - Gestion des produits
├── pages/
│   ├── __init__.py                 # ✅ FAIT
│   ├── accueil.py                  # TODO - PageAccueil (lignes 394-576)
│   ├── produits.py                 # TODO - PageProduits (lignes 583-803)
│   ├── historique.py               # TODO - PageHistorique (lignes 810-1135)
│   └── profil.py                   # TODO - PageProfil (lignes 1142-1444)
├── fenetres/
│   ├── __init__.py                 # ✅ FAIT
│   ├── formulaire_produit.py      # TODO - FormulaireProduit (lignes 1451-1686)
│   ├── recherche_ia.py             # TODO - FenetreRechercheIA (lignes 1693-1847)
│   ├── analyse_ia.py               # TODO - FenetreAnalyseIA (lignes 1854-1994)
│   └── selection_ville.py          # TODO - FenetreSelectionVille (lignes 2000-2435)
├── application.py                  # TODO - ApplicationPrincipale (lignes 2442-3095)
└── interface.py                    # À CONSERVER temporairement pour compatibilité

```

## Imports nécessaires par fichier

### pages/accueil.py

- `ResultatDecision` (core.algorithme)
- `CarteEnvironnement`, `LigneMoment` (composants)

### pages/produits.py

- `GestionnaireProduits`
- `ProduitDerma` (core.algorithme)
- `FormulaireProduit`, `FenetreRechercheIA` (fenetres)

### pages/historique.py

- `GestionnaireHistorique` (core.historique)
- `ResultatAnalyseHistorique` (core.historique)

### pages/profil.py

- `GestionnaireProfil`, `TypePeau` (core.profil)

### fenetres/formulaire_produit.py

- `GestionnaireProduits`
- `ProduitDerma`, `Categorie`, `ActiveTag`, `MomentUtilisation` (core.algorithme)

### fenetres/recherche_ia.py

- `GestionnaireProduits`
- `ClientGemini`, `ResultatAnalyseIA` (api.gemini)
- `FormulaireProduit`

### fenetres/analyse_ia.py

- Pas d'import spécial, juste l'app parente

### fenetres/selection_ville.py

- `ClientOpenMeteo`, `Localisation`, `rechercher_villes` (api.open_meteo)
- `GestionnaireConfig`, `VilleConfig` (core.config)

### application.py

- Toutes les pages
- Toutes les fenêtres
- Tous les gestionnaires
- Toutes les API

## Stratégie de migration

1. ✅ Créer les constantes, composants, gestionnaire_produits
2. ⏳ Créer les pages une par une
3. ⏳ Créer les fenêtres une par une  
4. ⏳ Créer application.py
5. ⏳ Mettre à jour gui/__init__.py pour réexporter
6. ⏳ Mettre à jour main.py
7. ⏳ Tester que tout fonctionne
8. ⏳ Supprimer interface.py

## Notes

- Garder `interface.py` jusqu'à ce que tout soit migré et testé
- Chaque nouveau fichier doit avoir un docstring clair
- Utiliser des imports relatifs dans gui/ (from .constantes import ...)
