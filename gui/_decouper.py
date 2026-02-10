"""
Script pour découper interface.py en modules séparés.

Ce script lit interface.py et extrait chaque classe/section vers son propre fichier.
"""

from pathlib import Path

# Définir les sections à extraire (lignes de début et de fin)
sections = {
    # Pages
    "gui/pages/accueil.py": (394, 576, ["ResultatDecision"]),
    "gui/pages/produits.py": (583, 803, ["GestionnaireProduits", "ProduitDerma", "FormulaireProduit", "FenetreRechercheIA"]),
    "gui/pages/historique.py": (810, 1135, ["GestionnaireHistorique", "ResultatAnalyseHistorique"]),
    "gui/pages/profil.py": (1142, 1444, ["GestionnaireProfil", "TypePeau"]),
    
    # Fenêtres
    "gui/fenetres/formulaire_produit.py": (1451, 1686, ["GestionnaireProduits", "ProduitDerma", "Categorie", "ActiveTag", "MomentUtilisation"]),
    "gui/fenetres/recherche_ia.py": (1693, 1847, ["GestionnaireProduits", "ClientGemini", "ResultatAnalyseIA", "FormulaireProduit"]),
    "gui/fenetres/analyse_ia.py": (1854, 1994, []),
    "gui/fenetres/selection_ville.py": (2000, 2435, ["ClientOpenMeteo", "GestionnaireConfig", "VilleConfig", "Localisation", "rechercher_villes"]),
    
    # Application principale
    "gui/application.py": (2442, 3095, [
        "ClientOpenMeteo", "DonneesEnvironnementales", "Localisation",
        "ClientGemini", "Result

atRoutineIA", "ResultatRoutineIA", "ProduitRoutine", "RoutineMoment",
        "GestionnaireProduits", "GestionnaireConfig", "GestionnaireHistorique", "GestionnaireProfil",
        "VilleConfig", "ConditionsEnvironnementales", "ResultatDecision", "ConditionsAnalyse", "ProduitAnalyse",
        "PageAccueil", "PageProduits", "PageHistorique", "PageProfil",
        "FenetreSelectionVille"
    ]),
}

def main():
    # Lire interface.py
    interface_path = Path(__file__).parent / "interface.py"
    with open(interface_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    print(f"Fichier interface.py lu : {len(lines)} lignes")
    
    # Pour chaque section
    for target_file, (start_line, end_line, imports_needed) in sections.items():
        print(f"\nCréation de {target_file}...")
        
        # Extraire les lignes (start_line est 1-indexed)
        section_lines = lines[start_line-1:end_line]
        
        # Construire le contenu du fichier
        content = []
        
        # Ajouter le docstring et les imports
        if "pages" in target_file:
            module_name = Path(target_file).stem.capitalize()
            content.append(f'"""\nPage {module_name} pour DermaLogic.\n"""\n\n')
        elif "fenetres" in target_file:
            module_name = Path(target_file).stem.replace("_", " ").title()
            content.append(f'"""\nFenêtre {module_name} pour DermaLogic.\n"""\n\n')
        else:
            content.append('"""\nApplication principale DermaLogic.\n"""\n\n')
        
        # Ajouter les imports
        content.append("import customtkinter as ctk\n")
        content.append("from tkinter import messagebox\n\n")
        
        # Importer depuis les modules internes
        content.append("from ..constantes import *\n")
        if "pages" in target_file and target_file != "gui/pages/accueil.py":
            content.append("from ..composants import *\n")
        if "application.py" in target_file:
            content.append("from .composants import *\n")
            content.append("from .pages.accueil import PageAccueil\n")
            content.append("from .pages.produits import PageProduits\n")
            content.append("from .pages.historique import PageHistorique\n")
            content.append("from .pages.profil import PageProfil\n")
            content.append("from .fenetres.selection_ville import FenetreSelectionVille\n")
        
        content.append("\n")
        
        # Ajouter les imports externes si nécessaire
        # (à compléter selon les besoins)
        
        # Ajouter le contenu de la section
        content.extend(section_lines)
        
        # Écrire le fichier
        target_path = Path(__file__).parent.parent / target_file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.writelines(content)
        
        print(f"✓ {target_file} créé ({len(section_lines)} lignes)")
    
    print("\n✅ Découpage terminé !")

if __name__ == "__main__":
    main()
