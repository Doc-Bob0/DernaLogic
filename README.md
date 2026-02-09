# DermaLogic 🧬

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-lightblue.svg)](https://github.com/TomSchimansky/CustomTkinter)

**Moteur de décision dermatologique intelligent**

Application qui adapte votre protocole de soins aux conditions environnementales (UV, humidité, pollution) pour maximiser l'efficacité de vos actifs.

![DermaLogic Screenshot](https://via.placeholder.com/800x450.png?text=DermaLogic+Screenshot)

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Structure des produits](#-structure-des-produits)
- [Algorithme de décision](#-algorithme-de-décision)
- [APIs utilisées](#-apis-utilisées)
- [Contribuer](#-contribuer)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

### Actuelles

- ✅ Récupération des données météo en temps réel (UV, humidité, PM2.5, température)
- ✅ Sélection de ville avec recherche géocodée
- ✅ **Villes favorites** avec données météo en cache (utilisation hors-ligne)
- ✅ Gestion des produits personnalisés avec persistance JSON
- ✅ **Ajout de produits avec IA** (Google Gemini) - détection automatique des caractéristiques
- ✅ Algorithme de filtrage intelligent (UV, texture, pureté)
- ✅ Recommandations par moment de la journée (Matin / Journée / Soir)
- ✅ **Historique des analyses** avec interface de visualisation (récentes / archives)
- ✅ **Rotation automatique** des analyses > 2 semaines vers les archives
- ✅ Interface graphique moderne avec CustomTkinter

### Prévues

- 🔜 Export des recommandations
- 🔜 Notifications quotidiennes
- 🔜 Incompatibilités entre actifs

---

## 🚀 Installation

### Prérequis

- Python 3.10+
- Connexion internet (pour l'API météo)

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/DermaLogic.git
cd DermaLogic
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
python main.py
```

---

## ⚙️ Configuration

### Clé API Gemini (optionnel)

Pour utiliser la fonctionnalité **"Ajouter avec IA"**, vous devez configurer une clé API Google Gemini :

1. Créez une clé sur [Google AI Studio](https://aistudio.google.com/)
2. Copiez le fichier `.env.example` en `.env` :

   ```bash
   cp .env.example .env
   ```

3. Éditez `.env` et ajoutez votre clé :

   ```
   GEMINI_API_KEY=votre_cle_api_ici
   ```

> **Note** : Sans clé API, l'ajout avec IA sera désactivé. Toutes les autres fonctionnalités restent disponibles.

---

## 📖 Utilisation

### 1. Ajouter vos produits

**Méthode manuelle :**

1. Cliquez sur l'onglet **"Mes Produits"**
2. Cliquez sur **"+ Ajouter"**
3. Remplissez les informations du produit

**Méthode IA (recommandée) :**

1. Cliquez sur **"+ Ajouter avec IA"**
2. Entrez le nom du produit
3. L'IA analyse et pré-remplit les caractéristiques
4. Vérifiez et validez

### 2. Sélectionner votre ville

1. Cliquez sur **"Changer"** en haut à droite
2. Onglet **Rechercher** : trouvez une nouvelle ville
3. Cliquez sur ⭐ pour ajouter aux favoris
4. Onglet **Favoris** : sélectionnez rapidement (données en cache, pas d'internet requis)

### 3. Analyser

1. Revenez sur l'onglet **"Analyse"**
2. Cliquez sur **"ANALYSER MES PRODUITS"**
3. Consultez les recommandations par moment

---

## 🏗 Architecture

```
DermaLogic/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances Python
├── .env.example            # Template configuration
├── .gitignore              # Fichiers ignorés
├── LICENSE                 # Licence MIT
├── README.md               # Documentation
│
├── api/                    # Couche API externe
│   ├── __init__.py
│   ├── open_meteo.py       # Client API Open-Meteo (météo + géocodage)
│   └── gemini.py           # Client API Google Gemini (IA)
│
├── core/                   # Logique métier
│   ├── __init__.py
│   ├── algorithme.py       # Algorithme de décision + modèle Produit
│   ├── config.py           # Gestionnaire de configuration
│   └── historique.py       # Gestionnaire d'historique des analyses
│
├── gui/                    # Interface utilisateur
│   ├── __init__.py
│   └── interface.py        # Interface CustomTkinter complète
│
└── user_data/              # Données utilisateur (ignoré par git)
    ├── README.md
    ├── config.json         # Configuration + favoris (généré)
    ├── produits_derma.json # Produits (généré)
    └── historique/         # Historique des analyses
        ├── analyses_recentes.json  # 2 dernières semaines
        └── analyses_archives.json  # Plus anciennes
```

---

## 🧴 Structure des produits

Chaque produit est défini par 6 caractéristiques :

| Attribut | Type | Description |
|----------|------|-------------|
| `nom` | str | Nom du produit |
| `category` | enum | `cleanser`, `treatment`, `moisturizer`, `protection` |
| `moment` | enum | `matin`, `journee`, `soir`, `tous` |
| `photosensitive` | bool | Réagit aux UV (BHA, rétinol, AHA) |
| `occlusivity` | int 1-5 | Richesse de la texture (5 = très occlusif) |
| `cleansing_power` | int 1-5 | Puissance nettoyante (5 = très puissant) |
| `active_tag` | enum | `acne`, `hydration`, `repair` |

### Exemple JSON

```json
{
  "nom": "Paula's Choice BHA 2%",
  "category": "treatment",
  "moment": "soir",
  "photosensitive": true,
  "occlusivity": 1,
  "cleansing_power": 1,
  "active_tag": "acne"
}
```

---

## 🔬 Algorithme de décision

L'algorithme applique 3 filtres successifs :

### A. Filtre de Sécurité (UV)

```
SI indice_UV > 3 :
   EXCLURE tous les produits photosensitive=True (pour matin/journée)
```

### B. Filtre de Texture (Humidité)

```
SI humidité < 45% :
   PRIORISER les produits avec occlusivity >= 4

SI humidité > 70% :
   EXCLURE les produits avec occlusivity <= 2 (sauf nettoyants)
```

### C. Filtre de Pureté (Pollution)

```
SI PM2.5 > 25 µg/m³ :
   RECOMMANDER le nettoyant avec le cleansing_power le plus élevé
```

---

## 🌍 APIs utilisées

### Open-Meteo (gratuit, sans clé)

| API | Endpoint | Données |
|-----|----------|---------|
| Météo | `api.open-meteo.com/v1/forecast` | UV, humidité, température |
| Qualité de l'air | `air-quality-api.open-meteo.com/v1/air-quality` | PM2.5, PM10 |
| Géocodage | `geocoding-api.open-meteo.com/v1/search` | Recherche de villes |

### Google Gemini (clé requise)

| API | Modèle | Utilisation |
|-----|--------|-------------|
| Gemini | `gemini-2.0-flash` | Analyse automatique des produits cosmétiques |

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

---

## 👤 Auteur

Créé avec ❤️ et l'aide de l'IA
