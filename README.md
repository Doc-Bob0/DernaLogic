# DermaLogic

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet-purple.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Application de recommandations dermatologiques personnalisees par IA**

DermaLogic analyse vos produits de soin, les conditions environnementales (UV, humidite, pollution, temperature) et votre profil cutane pour generer des routines matin/soir personnalisees via Google Gemini.

---

## Fonctionnalites

- Analyse IA des routines de soin via Google Gemini (2.5 Flash)
- Double mode d'analyse : **Rapide** et **Detaillee** (avec instructions du jour et niveau de stress)
- Conditions environnementales en temps reel (UV, humidite, PM2.5, temperature)
- Previsions meteo sur 3 jours integrees au contexte d'analyse
- Ajout de produits manuel ou par IA (detection automatique des caracteristiques)
- Profil utilisateur complet (type de peau, age, allergies, maladies, objectifs)
- Historique des analyses avec detail des routines
- Export JSON des donnees
- Villes favorites avec cache meteo
- Interface responsive (desktop + mobile) avec theme sombre

---

## Bugs connus

- **L'affichage des resultats d'analyse dans l'onglet Analyse ne fonctionne pas toujours** : le terminal affiche le succes de l'analyse Gemini mais les resultats ne s'affichent pas dans l'interface. Le passage de `threading.Thread` a `page.run_thread()` a ete effectue mais le probleme persiste. Investigation en cours.

---

## Installation

### Prerequis

- Python 3.10+
- Connexion internet (APIs meteo et Gemini)

### Etapes

```bash
git clone https://github.com/votre-username/DermaLogic.git
cd DermaLogic
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Configuration

### Cle API Gemini

La cle API est geree directement dans l'application :

1. Creez une cle gratuite sur [Google AI Studio](https://aistudio.google.com/)
2. Lancez DermaLogic
3. Allez dans l'onglet **Parametres**
4. Collez votre cle API et cliquez **Sauvegarder**
5. Utilisez **Tester la connexion** pour verifier

La cle est stockee localement dans `user_data/settings.json` (exclu du git).

---

## Utilisation

### 1. Configurer votre profil

Onglet **Profil** : renseignez votre type de peau, tranche d'age, niveau de stress, maladies cutanees, allergies et objectifs.

### 2. Ajouter vos produits

Onglet **Mes Produits** :
- **Ajouter manuellement** : remplissez les caracteristiques du produit
- **Ajouter avec IA** : entrez le nom du produit, Gemini analyse et pre-remplit les champs

### 3. Selectionner votre ville

Cliquez sur le nom de la ville dans la barre de navigation pour ouvrir la fenetre de selection. Recherchez une ville ou selectionnez un favori.

### 4. Lancer une analyse

Onglet **Analyse** :
- **Analyse Rapide** : routine basee sur votre profil, produits et meteo
- **Analyse Detaillee** : ajoutez des instructions du jour et votre niveau de stress actuel

Les resultats incluent : routine matin, routine soir, alertes et conseils du jour.

---

## Architecture

```
DermaLogic/
|-- main.py                          # Point d'entree Flet
|-- requirements.txt                 # Dependances (flet, requests)
|-- .gitignore
|-- LICENSE
|-- README.md
|
|-- api/                             # Clients API externes
|   |-- open_meteo.py                # Meteo, qualite air, geocodage (Open-Meteo)
|   +-- gemini.py                    # Google Gemini (analyse produits + routines)
|
|-- core/                            # Logique metier
|   |-- models.py                    # Enums et dataclasses (TypePeau, ProduitDerma, etc.)
|   |-- analyseur.py                 # Orchestrateur d'analyse IA
|   |-- config.py                    # Gestion ville + favoris
|   |-- profil.py                    # Gestion profil utilisateur
|   |-- historique.py                # Gestion historique des analyses
|   +-- settings.py                  # Gestion cle API
|
|-- gui/                             # Interface utilisateur Flet
|   |-- app.py                       # Orchestrateur principal (navigation, callbacks)
|   |-- state.py                     # Etat global de l'application
|   |-- theme.py                     # Couleurs, polices, constantes UI
|   |-- data.py                      # Gestionnaire de produits (persistance JSON)
|   |-- pages/
|   |   |-- page_accueil.py          # Analyse + conditions meteo
|   |   |-- page_produits.py         # Gestion des produits
|   |   |-- page_profil.py           # Profil utilisateur
|   |   |-- page_historique.py       # Historique des analyses
|   |   +-- page_parametres.py       # Cle API + export
|   |-- dialogs/
|   |   |-- formulaire_produit.py    # Formulaire ajout/edition produit
|   |   |-- fenetre_recherche_ia.py  # Recherche produit par IA
|   |   +-- fenetre_selection_ville.py # Selection de ville + favoris
|   +-- components/
|       |-- nav_bar.py               # Navigation desktop + mobile
|       +-- carte_environnement.py   # Carte meteo (UV, humidite, etc.)
|
+-- user_data/                       # Donnees utilisateur (gitignore)
    |-- settings.json                # Cle API (genere)
    |-- profile.json                 # Profil (genere)
    |-- produits_derma.json          # Produits (genere)
    |-- historique.json              # Historique (genere)
    +-- config.json                  # Ville + favoris (genere)
```

---

## APIs utilisees

### Open-Meteo (gratuit, sans cle)

| Endpoint | Donnees |
|----------|---------|
| `api.open-meteo.com/v1/forecast` | UV, humidite, temperature |
| `air-quality-api.open-meteo.com/v1/air-quality` | PM2.5 |
| `geocoding-api.open-meteo.com/v1/search` | Recherche de villes |

### Google Gemini (cle requise)

| Modele | Utilisation |
|--------|-------------|
| `gemini-2.0-flash` | Analyse des caracteristiques d'un produit cosmetique |
| `gemini-2.5-flash` | Generation de routine dermatologique personnalisee |

---

## Licence

Distribue sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.
