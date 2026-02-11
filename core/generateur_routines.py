"""
Module de génération automatique de routines quotidiennes.

Ce module génère intelligemment les routines matin/soir en analysant :
- Les conditions météorologiques actuelles
- Le profil utilisateur
- L'historique des 3 derniers jours (pour éviter répétition de produits agressifs)
- Les produits disponibles

La routine est générée par l'IA Gemini avec un prompt spécialisé.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from api.gemini import appeler_gemini
from api.open_meteo import obtenir_conditions_actuelles
from core.profil import charger_profil
from core.config import charger_config


# =============================================================================
# MODÈLES DE DONNÉES
# =============================================================================

@dataclass
class ProduitRoutine:
    """Produit dans une routine avec ses métadonnées."""
    nom: str
    categorie: str
    moment: str
    photosensitive: bool = False
    occlusivity: int = 3
    est_agressif: bool = False  # Déterminé par l'IA


@dataclass
class RoutineJour:
    """Routine complète pour un jour (matin + soir)."""
    date: str  # Format: YYYY-MM-DD
    matin: List[ProduitRoutine]
    soir: List[ProduitRoutine]
    conditions_meteo: Dict[str, Any]
    profil_utilise: Dict[str, Any]
    generated_at: str  # ISO timestamp


@dataclass
class HistoriqueProduits:
    """Historique des produits utilisés sur les derniers jours."""
    produits_recents: List[Dict[str, Any]]  # Liste des produits avec dates
    produits_agressifs_recents: List[Dict[str, Any]]  # Produits agressifs uniquement
    jours_analyses: int  # Nombre de jours analysés


# =============================================================================
# GESTIONNAIRE DE ROUTINES
# =============================================================================

class GenerateurRoutines:
    """Génère et gère les routines quotidiennes."""

    def __init__(self, dossier_routines: Optional[Path] = None):
        """
        Initialise le générateur de routines.

        Args:
            dossier_routines: Dossier de stockage des routines (défaut: user_data/routines/)
        """
        if dossier_routines is None:
            projet_dir = Path(__file__).parent.parent
            dossier_routines = projet_dir / "user_data" / "routines"

        self.dossier_routines = Path(dossier_routines)
        self.dossier_routines.mkdir(parents=True, exist_ok=True)

    def charger_routine_date(self, date: datetime) -> Optional[RoutineJour]:
        """
        Charge une routine depuis un fichier.

        Args:
            date: Date de la routine

        Returns:
            RoutineJour si trouvée, None sinon
        """
        nom_fichier = f"routine_{date.strftime('%Y-%m-%d')}.json"
        fichier = self.dossier_routines / nom_fichier

        if not fichier.exists():
            return None

        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Convertir les dicts en ProduitRoutine
                matin = [ProduitRoutine(**p) for p in data.get('matin', [])]
                soir = [ProduitRoutine(**p) for p in data.get('soir', [])]

                return RoutineJour(
                    date=data['date'],
                    matin=matin,
                    soir=soir,
                    conditions_meteo=data.get('conditions_meteo', {}),
                    profil_utilise=data.get('profil_utilise', {}),
                    generated_at=data.get('generated_at', '')
                )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def sauvegarder_routine(self, routine: RoutineJour):
        """
        Sauvegarde une routine dans un fichier.

        Args:
            routine: Routine à sauvegarder
        """
        nom_fichier = f"routine_{routine.date}.json"
        fichier = self.dossier_routines / nom_fichier

        # Convertir en dict pour JSON
        data = {
            'date': routine.date,
            'matin': [asdict(p) for p in routine.matin],
            'soir': [asdict(p) for p in routine.soir],
            'conditions_meteo': routine.conditions_meteo,
            'profil_utilise': routine.profil_utilise,
            'generated_at': routine.generated_at
        }

        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def analyser_historique_produits(self, nb_jours: int = 3) -> HistoriqueProduits:
        """
        Analyse l'historique des routines pour extraire les produits utilisés.

        Args:
            nb_jours: Nombre de jours à analyser (défaut: 3)

        Returns:
            HistoriqueProduits avec les produits récents
        """
        produits_recents = []
        produits_agressifs_recents = []

        aujourd_hui = datetime.now()

        for i in range(1, nb_jours + 1):
            date = aujourd_hui - timedelta(days=i)
            routine = self.charger_routine_date(date)

            if routine is None:
                continue

            # Analyser produits du matin
            for produit in routine.matin:
                info_produit = {
                    'nom': produit.nom,
                    'date': routine.date,
                    'moment': 'matin',
                    'categorie': produit.categorie,
                    'photosensitive': produit.photosensitive,
                    'est_agressif': produit.est_agressif
                }
                produits_recents.append(info_produit)

                if produit.est_agressif:
                    produits_agressifs_recents.append(info_produit)

            # Analyser produits du soir
            for produit in routine.soir:
                info_produit = {
                    'nom': produit.nom,
                    'date': routine.date,
                    'moment': 'soir',
                    'categorie': produit.categorie,
                    'photosensitive': produit.photosensitive,
                    'est_agressif': produit.est_agressif
                }
                produits_recents.append(info_produit)

                if produit.est_agressif:
                    produits_agressifs_recents.append(info_produit)

        return HistoriqueProduits(
            produits_recents=produits_recents,
            produits_agressifs_recents=produits_agressifs_recents,
            jours_analyses=nb_jours
        )

    def generer_routine_quotidienne(
        self,
        produits_disponibles: List[Dict[str, Any]],
        force_regeneration: bool = False
    ) -> Tuple[RoutineJour, bool]:
        """
        Génère la routine quotidienne avec analyse de l'historique.

        Args:
            produits_disponibles: Liste des produits de l'utilisateur
            force_regeneration: Forcer la génération même si routine existe

        Returns:
            Tuple: (RoutineJour, nouvelle_routine_generee)
        """
        aujourd_hui = datetime.now()
        date_str = aujourd_hui.strftime('%Y-%m-%d')

        # Vérifier si routine existe déjà
        if not force_regeneration:
            routine_existante = self.charger_routine_date(aujourd_hui)
            if routine_existante:
                return routine_existante, False

        # 1. Analyser l'historique des 3 derniers jours
        historique = self.analyser_historique_produits(nb_jours=3)

        # 2. Récupérer les conditions météo
        config = charger_config()
        ville = config.get('ville_actuelle', {}).get('nom', 'Paris')
        latitude = config.get('ville_actuelle', {}).get('latitude', 48.8566)
        longitude = config.get('ville_actuelle', {}).get('longitude', 2.3522)

        try:
            conditions = obtenir_conditions_actuelles(latitude, longitude)
        except Exception as e:
            print(f"Erreur récupération météo: {e}")
            conditions = None

        # 3. Charger le profil utilisateur
        profil = charger_profil()

        # 4. Préparer le prompt pour Gemini
        prompt = self._construire_prompt_routine(
            produits_disponibles=produits_disponibles,
            historique=historique,
            conditions=conditions,
            profil=profil,
            ville=ville
        )

        # 5. Appeler Gemini
        try:
            reponse = appeler_gemini(prompt)
            routine_data = self._parser_reponse_gemini(reponse)
        except Exception as e:
            print(f"Erreur génération routine IA: {e}")
            # Fallback: routine basique sans IA
            routine_data = self._generer_routine_basique(produits_disponibles)

        # 6. Créer l'objet RoutineJour
        routine = RoutineJour(
            date=date_str,
            matin=routine_data['matin'],
            soir=routine_data['soir'],
            conditions_meteo=self._conditions_vers_dict(conditions) if conditions else {},
            profil_utilise=profil.to_dict() if profil else {},
            generated_at=datetime.now().isoformat()
        )

        # 7. Sauvegarder
        self.sauvegarder_routine(routine)

        return routine, True

    def _construire_prompt_routine(
        self,
        produits_disponibles: List[Dict[str, Any]],
        historique: HistoriqueProduits,
        conditions: Any,
        profil: Any,
        ville: str
    ) -> str:
        """Construit le prompt pour Gemini avec l'historique."""

        # Formater l'historique
        historique_texte = "Aucune routine précédente trouvée."
        if historique.produits_recents:
            historique_texte = f"Produits utilisés les {historique.jours_analyses} derniers jours :\n"
            for p in historique.produits_recents:
                historique_texte += f"- {p['date']} ({p['moment']}): {p['nom']}"
                if p['est_agressif']:
                    historique_texte += " ⚠️ PRODUIT AGRESSIF"
                historique_texte += "\n"

        # Formater produits disponibles
        produits_texte = "\n".join([
            f"- {p.get('nom', 'Produit')} ({p.get('category', 'inconnu')}) - {p.get('moment', 'tous')}"
            for p in produits_disponibles
        ])

        # Formater profil
        type_peau = profil.type_peau.value if profil else "normale"
        problemes = ", ".join(profil.problemes) if profil and profil.problemes else "aucun"

        # Formater conditions météo
        if conditions:
            uv = f"{conditions.indice_uv:.1f} ({conditions.niveau_uv})"
            temp = f"{conditions.temperature:.1f}°C"
            humidite = f"{conditions.humidite:.0f}% ({conditions.niveau_humidite})"
            pollution = f"{conditions.pm2_5:.1f} µg/m³ ({conditions.niveau_pollution})"
        else:
            uv = "Non disponible"
            temp = "Non disponible"
            humidite = "Non disponible"
            pollution = "Non disponible"

        prompt = f"""Tu es DermaLogic, un dermatologue expert spécialisé dans les routines de soins personnalisées.

MISSION CRITIQUE : Génère une routine matin ET soir OPTIMALE en évitant la répétition de produits agressifs.

═══════════════════════════════════════════════════════════════════════════════
📊 HISTORIQUE DES 3 DERNIERS JOURS (ANALYSE PRIORITAIRE)
═══════════════════════════════════════════════════════════════════════════════

{historique_texte}

⚠️ RÈGLE ABSOLUE : Analyse cet historique et ÉVITE de répéter les produits agressifs
(exfoliants AHA/BHA, rétinol, vitamine C forte, benzoyl peroxide) trop fréquemment.

Critères d'espacement :
- Si un produit agressif a été utilisé hier ou avant-hier → NE PAS le recommander aujourd'hui
- Privilégier des routines douces de "récupération" entre les traitements agressifs
- Alterner entre routines actives (avec actifs) et routines apaisantes (hydratation/réparation)

═══════════════════════════════════════════════════════════════════════════════
🌍 CONDITIONS ENVIRONNEMENTALES AUJOURD'HUI
═══════════════════════════════════════════════════════════════════════════════

Ville : {ville}
Température : {temp}
Indice UV : {uv}
Humidité : {humidite}
Pollution PM2.5 : {pollution}

═══════════════════════════════════════════════════════════════════════════════
👤 PROFIL UTILISATEUR
═══════════════════════════════════════════════════════════════════════════════

Type de peau : {type_peau}
Problèmes : {problemes}

═══════════════════════════════════════════════════════════════════════════════
🧴 PRODUITS DISPONIBLES
═══════════════════════════════════════════════════════════════════════════════

{produits_texte}

═══════════════════════════════════════════════════════════════════════════════
📋 FORMAT DE RÉPONSE REQUIS (JSON STRICT)
═══════════════════════════════════════════════════════════════════════════════

Retourne UNIQUEMENT un objet JSON avec cette structure EXACTE :

{{
  "matin": [
    {{
      "nom": "Nom du produit",
      "categorie": "cleanser|treatment|moisturizer|protection",
      "moment": "matin",
      "photosensitive": false,
      "occlusivity": 3,
      "est_agressif": false
    }}
  ],
  "soir": [
    {{
      "nom": "Nom du produit",
      "categorie": "cleanser|treatment|moisturizer|protection",
      "moment": "soir",
      "photosensitive": true,
      "occlusivity": 3,
      "est_agressif": true
    }}
  ],
  "explication": "Explication courte de tes choix et pourquoi tu as évité certains produits"
}}

IMPORTANT :
- Marque "est_agressif": true pour : AHA, BHA, rétinol, vitamine C >15%, benzoyl peroxide
- Ordre typique MATIN: Nettoyant → Sérum/Traitement → Hydratant → SPF
- Ordre typique SOIR: Nettoyant → Traitement → Hydratant
- Maximum 4-5 produits par routine
- Réponds UNIQUEMENT avec le JSON, sans texte avant/après
"""

        return prompt

    def _parser_reponse_gemini(self, reponse: str) -> Dict[str, List[ProduitRoutine]]:
        """Parse la réponse JSON de Gemini."""
        # Nettoyer la réponse (enlever markdown, etc.)
        reponse_clean = reponse.strip()

        # Enlever les blocs de code markdown si présents
        if reponse_clean.startswith("```"):
            reponse_clean = reponse_clean.split("```")[1]
            if reponse_clean.startswith("json"):
                reponse_clean = reponse_clean[4:]

        reponse_clean = reponse_clean.strip()

        # Parser JSON
        data = json.loads(reponse_clean)

        # Convertir en ProduitRoutine
        matin = [ProduitRoutine(**p) for p in data.get('matin', [])]
        soir = [ProduitRoutine(**p) for p in data.get('soir', [])]

        return {
            'matin': matin,
            'soir': soir,
            'explication': data.get('explication', '')
        }

    def _generer_routine_basique(
        self,
        produits_disponibles: List[Dict[str, Any]]
    ) -> Dict[str, List[ProduitRoutine]]:
        """Génère une routine basique sans IA (fallback)."""
        matin = []
        soir = []

        for produit in produits_disponibles:
            moment = produit.get('moment', 'tous')
            p = ProduitRoutine(
                nom=produit.get('nom', 'Produit'),
                categorie=produit.get('category', 'moisturizer'),
                moment=moment,
                photosensitive=produit.get('photosensitive', False),
                occlusivity=produit.get('occlusivity', 3),
                est_agressif=False
            )

            if moment in ['matin', 'tous']:
                matin.append(p)
            if moment in ['soir', 'tous']:
                soir.append(p)

        return {'matin': matin, 'soir': soir}

    def _conditions_vers_dict(self, conditions) -> Dict[str, Any]:
        """Convertit les conditions météo en dictionnaire."""
        if conditions is None:
            return {}

        return {
            'temperature': conditions.temperature,
            'indice_uv': conditions.indice_uv,
            'niveau_uv': conditions.niveau_uv,
            'humidite': conditions.humidite,
            'niveau_humidite': conditions.niveau_humidite,
            'pm2_5': conditions.pm2_5,
            'niveau_pollution': conditions.niveau_pollution
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

_generateur: Optional[GenerateurRoutines] = None


def obtenir_generateur() -> GenerateurRoutines:
    """Obtient l'instance globale du générateur (singleton)."""
    global _generateur
    if _generateur is None:
        _generateur = GenerateurRoutines()
    return _generateur


if __name__ == "__main__":
    # Test du module
    from core.config import charger_produits

    print("Test du générateur de routines...")
    print("=" * 60)

    generateur = obtenir_generateur()

    # Test 1: Analyser historique
    print("\n1. Analyse de l'historique...")
    historique = generateur.analyser_historique_produits(nb_jours=3)
    print(f"   Produits récents trouvés: {len(historique.produits_recents)}")
    print(f"   Produits agressifs: {len(historique.produits_agressifs_recents)}")

    # Test 2: Générer routine
    print("\n2. Génération de routine...")
    try:
        produits = charger_produits()
        routine, nouvelle = generateur.generer_routine_quotidienne(produits)

        if nouvelle:
            print("   ✓ Nouvelle routine générée!")
        else:
            print("   ℹ Routine existante chargée")

        print(f"   Date: {routine.date}")
        print(f"   Produits matin: {len(routine.matin)}")
        print(f"   Produits soir: {len(routine.soir)}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")

    print("\n" + "=" * 60)
