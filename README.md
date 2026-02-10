# DermaLogic 🧬

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet-purple.svg)](https://flet.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Votre Dermatologue IA Personnel - Zéro Charge Cognitive**

DermaLogic est une application cross-platform (Mobile, Web, Desktop) conçue pour gérer intégralement votre routine de soin. Elle s'adapte en temps réel à votre environnement et à votre état, sans que vous ayez à y penser.

---

## 🎯 La Vision : "Zéro Charge Cognitive"

L'objectif de DermaLogic est simple : **L'application s'occupe de tout.**

Fini les questions le matin devant le miroir. L'application sait où vous êtes, le temps qu'il fait, l'état de votre peau, et vous dit exactement quoi faire.

### Deux modes d'analyse IA

Toute l'intelligence repose sur notre IA (Google Gemini) qui analyse votre situation :

1. **⚡ Mode Simple (Automatique)** : L'IA croise votre profil et la météo locale (UV, humidité, pollution) pour générer votre routine instantanée. Un clic, une réponse.
2. **🗣️ Mode Détaillé** : Vous pouvez dire à l'IA "J'ai la peau qui tire ce matin" ou "J'ai une soirée importante". Elle adaptera ses recommandations en conséquence.

### 📱 Mobile & Notifications

DermaLogic est conçue pour votre poche. Elle vous notifie aux moments clés :

- ☀️ **Matin** : Routine protection & hydratation adaptée à la météo du jour.
- 🌙 **Soir** : Routine nettoyage & réparation.
- ⚠️ **Alertes** : "Pic de pollution dans 1h, prévoyez un nettoyage double ce soir."

---

## ✨ Fonctionnalités Clés

- **🌍 Saisie Environnementale Automatique** : Détection des UV, de l'humidité, de la température et de la pollution (PM2.5) via Open-Meteo.
- **🤖 Gestion des Produits par IA** : Ajoutez vos produits en les prenant simplement en photo ou en donnant leur nom. L'IA déduit leurs propriétés (occlusivité, photosensibilité, actifs).
- **🔄 Cross-Platform** : Une seule application pour votre iPhone, votre Android et votre PC (grâce à Flet).
- **📅 Historique Intelligent** : Suivez l'évolution de votre peau corrélée aux conditions environnementales.

---

## 🚀 Installation & Lancement

### Prérequis

- Python 3.10+
- Clé API Google Gemini (pour l'analyse IA)

### Installation

```bash
git clone https://github.com/votre-username/DermaLogic.git
cd DermaLogic
pip install -r requirements.txt
```

### Lancement

```bash
# Lancer l'interface (Desktop/Web)
python main.py

# Pour tester la version Web spécifiquement
flet run --web main.py
```

---

## ⚙️ Configuration (Clé IA)

Pour activer l'intelligence artificielle, créez un fichier `.env` à la racine :

```ini
GEMINI_API_KEY=votre_cle_api_google_studio
```

*(Obtenez votre clé gratuitement sur [Google AI Studio](https://aistudio.google.com/))*

---

## 🏗 Architecture Technique

Le projet repose sur une architecture moderne et maintenable :

- **Frontend** : [Flet](https://flet.dev) (Flutter en Python) pour une UI réactive et multi-plateforme.
- **Backend IA** : Google Gemini 2.0 Flash pour l'analyse sémantique et dermatologique.
- **Data** : Open-Meteo pour les données environnementales temps réel.
- **Core** : Moteur de décision hybride (Algorithmique + IA).

---

## 🤝 Contribuer

Les contributions sont les bienvenues pour nous aider à atteindre le "Zéro Charge Cognitive" !
Forkez, développez, et proposez vos Pull Requests.

---

## 📄 Licence

Distribué sous licence MIT.
