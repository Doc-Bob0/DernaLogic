"""
DermaLogic - Client API Gemini
==============================

Ce module gère l'intégration avec l'API Gemini de Google
pour l'analyse intelligente de produits cosmétiques.

Utilise Gemini 2.0 Flash pour des réponses rapides et précises.

Configuration :
    La clé API doit être définie dans le fichier .env :
    GEMINI_API_KEY=votre_cle_ici
"""

import os
import requests
import json
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


# =============================================================================
# CHARGEMENT DE LA CONFIGURATION
# =============================================================================

def _charger_env() -> None:
    """Charge les variables d'environnement depuis le fichier .env"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

_charger_env()


# =============================================================================
# CONFIGURATION
# =============================================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


# =============================================================================
# PROMPT EXPERT POUR ANALYSE DE PRODUIT
# =============================================================================

PROMPT_ANALYSE_PRODUIT = """Tu es un expert dermatologue et cosmétologue avec 20 ans d'expérience dans l'analyse des produits de soin de la peau. Tu connais parfaitement les ingrédients actifs, leur comportement face aux UV, leur texture et leur fonction.

Je vais te donner le nom d'un produit cosmétique. Tu dois analyser ce produit et me retourner ses caractéristiques au format JSON strict.

RÈGLES IMPORTANTES :
1. Réponds UNIQUEMENT avec un objet JSON valide
2. Pas de texte avant ou après le JSON
3. Pas de bloc de code markdown (pas de ```)
4. Utilise tes connaissances sur les formulations cosmétiques
5. Si tu ne connais pas le produit exact, analyse en fonction de la marque et du type de produit

STRUCTURE JSON EXACTE À RETOURNER :
{{"nom": "Nom complet du produit", "category": "moisturizer", "moment": "tous", "photosensitive": false, "occlusivity": 3, "cleansing_power": 3, "active_tag": "hydration"}}

VALEURS POSSIBLES :
- category: "cleanser", "treatment", "moisturizer", "protection"
- moment: "matin", "journee", "soir", "tous"
- photosensitive: true ou false
- occlusivity: nombre entier de 1 à 5
- cleansing_power: nombre entier de 1 à 5
- active_tag: "hydration", "acne", "repair"

GUIDE D'ÉVALUATION :

category:
- "cleanser" : nettoyants, démaquillants, eaux micellaires, gels nettoyants
- "treatment" : sérums, acides, rétinol, vitamine C, niacinamide
- "moisturizer" : crèmes, baumes, lotions hydratantes
- "protection" : écrans solaires, SPF, protections UV

moment:
- "matin" : SPF, antioxydants, protections
- "soir" : rétinol, AHA/BHA, traitements intensifs
- "journee" : réapplication SPF, brumes
- "tous" : nettoyants, hydratants basiques, produits sans actifs photosensibles

photosensitive = true si contient :
- Rétinol, rétinaldéhyde, trétinoïne
- AHA (acide glycolique, lactique, mandélique)
- BHA (acide salicylique à haute concentration)
- Vitamine C pure (acide ascorbique)
- Benzoyl peroxide

occlusivity (1=très léger, 5=très riche) :
- 1 : eaux, brumes, gels, lotions légères
- 2 : sérums, fluides légers
- 3 : crèmes légères, émulsions
- 4 : crèmes riches, baumes légers
- 5 : baumes épais, huiles, onguents

cleansing_power (1=très doux, 5=très puissant) :
- 1 : eaux micellaires douces, laits
- 2 : gels doux sans sulfate
- 3 : nettoyants mousse standards
- 4 : nettoyants purifiants, anti-acné
- 5 : démaquillants waterproof, nettoyants profonds

active_tag :
- "hydration" : acide hyaluronique, glycérine, céramides, urée
- "acne" : BHA, niacinamide, zinc, peroxyde de benzoyle
- "repair" : panthénol, centella, allantoïne, céramides

PRODUIT À ANALYSER : {nom_produit}

Retourne UNIQUEMENT le JSON, rien d'autre."""


# =============================================================================
# PROMPT EXPERT POUR ANALYSE DE ROUTINE QUOTIDIENNE
# =============================================================================

PROMPT_ANALYSE_ROUTINE = """Tu es DermaLogic, un assistant dermatologue expert avec 20 ans d'expérience. Tu aides les utilisateurs à optimiser leur routine de soins quotidienne en fonction de leurs produits, des conditions environnementales, et de leur état personnel.

Tu dois créer une routine personnalisée en 3 moments : MATIN, JOURNÉE, SOIR.

# INFORMATIONS UTILISATEUR

## Profil permanent :
{profil_utilisateur}

## État du jour :
{etat_quotidien}

## Instructions personnalisées (si présentes) :
{instructions}

# CONDITIONS ENVIRONNEMENTALES

Ville : {ville}
Température : {temperature}°C
Indice UV : {indice_uv} ({niveau_uv})
Humidité : {humidite}% ({niveau_humidite})
Pollution PM2.5 : {pm2_5} µg/m³ ({niveau_pollution})

# PRODUITS DISPONIBLES

{liste_produits}

# RÈGLES D'EXPERTISE

1. **Sécurité UV** : Si UV > 3, JAMAIS de produits photosensibles le matin ou en journée
2. **Hydratation** : Si humidité < 45%, privilégier les textures riches (occlusivity >= 4)
3. **Légèreté** : Si humidité > 70%, privilégier les textures légères
4. **Pollution** : Si PM2.5 > 25, recommander un nettoyage approfondi le soir
5. **Stress** : Si stress élevé (>7), éviter les actifs irritants comme les acides forts
6. **Ordre d'application** : Du plus léger au plus épais, actifs avant crèmes
7. **Protection** : Toujours terminer le matin par un SPF si UV > 1

# FORMAT DE RÉPONSE

Réponds en JSON avec cette structure EXACTE :
{{
    "matin": {{
        "conseils": "Texte avec les étapes de la routine matin...",
        "produits": [
            {{"nom": "Nom du produit", "justification": "Pourquoi ce produit..."}}
        ]
    }},
    "journee": {{
        "conseils": "Texte avec les conseils pour la journée...",
        "produits": [
            {{"nom": "Nom du produit", "justification": "Pourquoi ce produit..."}}
        ]
    }},
    "soir": {{
        "conseils": "Texte avec les étapes de la routine soir...",
        "produits": [
            {{"nom": "Nom du produit", "justification": "Pourquoi ce produit..."}}
        ]
    }},
    "alertes": ["Alerte 1 si nécessaire", "Alerte 2..."]
}}

RÈGLES DE RÉPONSE :
1. Réponds UNIQUEMENT avec le JSON, rien d'autre
2. Les conseils doivent être concis, personnalisés et bienveillants
3. Justifie chaque produit en 1-2 phrases
4. N'inclus que les produits vraiment nécessaires
5. Adapte ton discours au niveau de stress (plus doux si stress élevé)
6. Si un moment ne nécessite rien de particulier, indique "Pas de routine spécifique"

Génère maintenant la routine optimale."""


# =============================================================================
# STRUCTURE RÉSULTAT ANALYSE PRODUIT
# =============================================================================

@dataclass
class ResultatAnalyseIA:
    """Résultat de l'analyse IA d'un produit."""
    succes: bool
    nom: str = ""
    category: str = "moisturizer"
    moment: str = "tous"
    photosensitive: bool = False
    occlusivity: int = 3
    cleansing_power: int = 3
    active_tag: str = "hydration"
    erreur: str = ""


# =============================================================================
# STRUCTURE RÉSULTAT ANALYSE ROUTINE
# =============================================================================

@dataclass
class ProduitRoutine:
    """Un produit dans la routine avec sa justification."""
    nom: str
    justification: str


@dataclass
class RoutineMoment:
    """Routine pour un moment de la journée."""
    conseils: str
    produits: list  # Liste de ProduitRoutine
    
    @classmethod
    def from_dict(cls, data: dict) -> "RoutineMoment":
        """Crée une instance depuis un dictionnaire."""
        produits = []
        for p in data.get("produits", []):
            if isinstance(p, dict):
                produits.append(ProduitRoutine(
                    nom=p.get("nom", ""),
                    justification=p.get("justification", "")
                ))
        return cls(
            conseils=data.get("conseils", ""),
            produits=produits
        )


@dataclass
class ResultatRoutineIA:
    """Résultat complet de l'analyse de routine par l'IA."""
    succes: bool
    matin: RoutineMoment = None
    journee: RoutineMoment = None
    soir: RoutineMoment = None
    alertes: list = None
    erreur: str = ""
    
    def __post_init__(self):
        if self.matin is None:
            self.matin = RoutineMoment("", [])
        if self.journee is None:
            self.journee = RoutineMoment("", [])
        if self.soir is None:
            self.soir = RoutineMoment("", [])
        if self.alertes is None:
            self.alertes = []


# =============================================================================
# CLIENT GEMINI
# =============================================================================

class ClientGemini:
    """
    Client pour l'API Gemini de Google.
    
    Permet d'analyser des produits cosmétiques et de retourner
    leurs caractéristiques au format structuré.
    """
    
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    def generer(self, prompt: str) -> Optional[str]:
        """Envoie un prompt à Gemini et retourne la réponse brute."""
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 512
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            candidates = data.get("candidates", [])
            
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            
            return None
            
        except requests.RequestException as e:
            print(f"[Gemini] Erreur de requête: {e}")
            return None
    
    def _extraire_json(self, texte: str) -> Optional[dict]:
        """
        Extrait un objet JSON d'un texte, même s'il est entouré de texte.
        """
        if not texte:
            return None
        
        # Nettoyer le texte
        texte = texte.strip()
        
        # Enlever les blocs de code markdown
        texte = re.sub(r'^```(?:json)?\s*', '', texte)
        texte = re.sub(r'\s*```$', '', texte)
        texte = texte.strip()
        
        # Essayer de parser directement
        try:
            return json.loads(texte)
        except json.JSONDecodeError:
            pass
        
        # Chercher un objet JSON dans le texte avec regex
        match = re.search(r'\{[^{}]*\}', texte, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        # Chercher plus largement (JSON imbriqué possible)
        start = texte.find('{')
        if start != -1:
            # Trouver la fin du JSON
            depth = 0
            for i, char in enumerate(texte[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(texte[start:i+1])
                        except json.JSONDecodeError:
                            pass
                        break
        
        return None
    
    def analyser_produit(self, nom_produit: str) -> ResultatAnalyseIA:
        """
        Analyse un produit cosmétique et retourne ses caractéristiques.
        """
        prompt = PROMPT_ANALYSE_PRODUIT.format(nom_produit=nom_produit)
        reponse = self.generer(prompt)
        
        if not reponse:
            return ResultatAnalyseIA(
                succes=False,
                erreur="Pas de réponse de Gemini. Vérifie ta connexion internet."
            )
        
        print(f"[Gemini] Réponse brute: {reponse[:300]}")
        
        # Extraire le JSON
        data = self._extraire_json(reponse)
        
        if data is None:
            return ResultatAnalyseIA(
                succes=False,
                erreur=f"Impossible de parser la réponse:\n{reponse[:150]}..."
            )
        
        # Valider les champs requis
        categories_valides = ["cleanser", "treatment", "moisturizer", "protection"]
        moments_valides = ["matin", "journee", "soir", "tous"]
        tags_valides = ["hydration", "acne", "repair"]
        
        category = data.get("category", "moisturizer")
        if category not in categories_valides:
            category = "moisturizer"
        
        moment = data.get("moment", "tous")
        if moment not in moments_valides:
            moment = "tous"
        
        active_tag = data.get("active_tag", "hydration")
        if active_tag not in tags_valides:
            active_tag = "hydration"
        
        # Gérer occlusivity et cleansing_power
        try:
            occlusivity = int(data.get("occlusivity", 3))
            occlusivity = max(1, min(5, occlusivity))
        except (TypeError, ValueError):
            occlusivity = 3
        
        try:
            cleansing_power = int(data.get("cleansing_power", 3))
            cleansing_power = max(1, min(5, cleansing_power))
        except (TypeError, ValueError):
            cleansing_power = 3
        
        return ResultatAnalyseIA(
            succes=True,
            nom=str(data.get("nom", nom_produit)),
            category=category,
            moment=moment,
            photosensitive=bool(data.get("photosensitive", False)),
            occlusivity=occlusivity,
            cleansing_power=cleansing_power,
            active_tag=active_tag
        )
    
    def analyser_routine(
        self,
        produits: list,
        donnees_env: dict,
        profil_utilisateur: str,
        etat_quotidien: str,
        instructions: str = ""
    ) -> ResultatRoutineIA:
        """
        Analyse la routine quotidienne optimale basée sur tous les paramètres.
        
        Args:
            produits: Liste des produits disponibles (dicts avec nom, category, etc.)
            donnees_env: Données environnementales (dict avec ville, uv, humidite, etc.)
            profil_utilisateur: Texte décrivant le profil permanent
            etat_quotidien: Texte décrivant l'état du jour
            instructions: Instructions personnalisées optionnelles
        
        Returns:
            ResultatRoutineIA avec les conseils pour matin, journée, soir
        """
        # Formater la liste des produits
        liste_produits = []
        for p in produits:
            liste_produits.append(
                f"- {p.get('nom', 'Inconnu')} "
                f"(catégorie: {p.get('category', 'inconnu')}, "
                f"moment: {p.get('moment', 'tous')}, "
                f"photosensible: {'oui' if p.get('photosensitive') else 'non'}, "
                f"occlusivité: {p.get('occlusivity', 3)}/5, "
                f"action: {p.get('active_tag', 'hydration')})"
            )
        
        # Construire le prompt
        prompt = PROMPT_ANALYSE_ROUTINE.format(
            profil_utilisateur=profil_utilisateur or "Non renseigné",
            etat_quotidien=etat_quotidien or "Non renseigné",
            instructions=instructions or "Aucune instruction particulière",
            ville=donnees_env.get("ville", "Inconnue"),
            temperature=donnees_env.get("temperature", "N/A"),
            indice_uv=donnees_env.get("indice_uv", 0),
            niveau_uv=donnees_env.get("niveau_uv", "Inconnu"),
            humidite=donnees_env.get("humidite", 50),
            niveau_humidite=donnees_env.get("niveau_humidite", "Normal"),
            pm2_5=donnees_env.get("pm2_5", 0),
            niveau_pollution=donnees_env.get("niveau_pollution", "Bon"),
            liste_produits="\n".join(liste_produits) if liste_produits else "Aucun produit enregistré"
        )
        
        # Augmenter les tokens pour cette requête
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            candidates = data.get("candidates", [])
            
            if not candidates:
                return ResultatRoutineIA(
                    succes=False,
                    erreur="Pas de réponse de Gemini"
                )
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return ResultatRoutineIA(
                    succes=False,
                    erreur="Réponse vide de Gemini"
                )
            
            reponse_texte = parts[0].get("text", "").strip()
            print(f"[Gemini Routine] Réponse: {reponse_texte[:500]}...")
            
            # Extraire le JSON
            data_json = self._extraire_json(reponse_texte)
            
            if data_json is None:
                return ResultatRoutineIA(
                    succes=False,
                    erreur=f"Impossible de parser: {reponse_texte[:200]}..."
                )
            
            # Construire le résultat
            return ResultatRoutineIA(
                succes=True,
                matin=RoutineMoment.from_dict(data_json.get("matin", {})),
                journee=RoutineMoment.from_dict(data_json.get("journee", {})),
                soir=RoutineMoment.from_dict(data_json.get("soir", {})),
                alertes=data_json.get("alertes", [])
            )
            
        except requests.RequestException as e:
            return ResultatRoutineIA(
                succes=False,
                erreur=f"Erreur réseau: {str(e)}"
            )
        except Exception as e:
            return ResultatRoutineIA(
                succes=False,
                erreur=f"Erreur inattendue: {str(e)}"
            )


# =============================================================================
# TEST DU MODULE
# =============================================================================

if __name__ == "__main__":
    print("Test du module Gemini")
    print("=" * 50)
    
    client = ClientGemini()
    
    produit_test = "CeraVe Crème Hydratante"
    print(f"\nAnalyse de: {produit_test}")
    print("-" * 40)
    
    resultat = client.analyser_produit(produit_test)
    
    if resultat.succes:
        print(f"✓ Nom: {resultat.nom}")
        print(f"  Catégorie: {resultat.category}")
        print(f"  Moment: {resultat.moment}")
        print(f"  Photosensible: {resultat.photosensitive}")
        print(f"  Occlusivité: {resultat.occlusivity}/5")
        print(f"  Pouvoir nettoyant: {resultat.cleansing_power}/5")
        print(f"  Action: {resultat.active_tag}")
    else:
        print(f"✗ Erreur: {resultat.erreur}")
