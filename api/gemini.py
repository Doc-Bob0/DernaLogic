"""
DermaLogic - Client API Gemini
==============================

Ce module gere l'integration avec l'API Gemini de Google :
- Analyse de produits cosmetiques (Gemini 2.0 Flash)
- Analyse de routine dermatologique complete (Gemini 2.5 Flash)

La cle API est fournie par l'utilisateur via l'ecran Parametres.
"""

import requests
import json
import re
import time
from typing import Optional
from dataclasses import dataclass


# =============================================================================
# PROMPT EXPERT POUR ANALYSE DE PRODUIT
# =============================================================================

PROMPT_ANALYSE_PRODUIT = """Tu es un expert dermatologue et cosmetologue avec 20 ans d'experience dans l'analyse des produits de soin de la peau. Tu connais parfaitement les ingredients actifs, leur comportement face aux UV, leur texture et leur fonction.

Je vais te donner le nom d'un produit cosmetique. Tu dois analyser ce produit et me retourner ses caracteristiques au format JSON strict.

REGLES IMPORTANTES :
1. Reponds UNIQUEMENT avec un objet JSON valide
2. Pas de texte avant ou apres le JSON
3. Pas de bloc de code markdown (pas de ```)
4. Utilise tes connaissances sur les formulations cosmetiques
5. Si tu ne connais pas le produit exact, analyse en fonction de la marque et du type de produit

STRUCTURE JSON EXACTE A RETOURNER :
{{"nom": "Nom complet du produit", "category": "moisturizer", "moment": "tous", "photosensitive": false, "occlusivity": 3, "cleansing_power": 3, "active_tag": "hydration"}}

VALEURS POSSIBLES :
- category: "cleanser", "treatment", "moisturizer", "protection"
- moment: "matin", "journee", "soir", "tous"
- photosensitive: true ou false
- occlusivity: nombre entier de 1 a 5
- cleansing_power: nombre entier de 1 a 5
- active_tag: "hydration", "acne", "repair"

GUIDE D'EVALUATION :

category:
- "cleanser" : nettoyants, demaquillants, eaux micellaires, gels nettoyants
- "treatment" : serums, acides, retinol, vitamine C, niacinamide
- "moisturizer" : cremes, baumes, lotions hydratantes
- "protection" : ecrans solaires, SPF, protections UV

moment:
- "matin" : SPF, antioxydants, protections
- "soir" : retinol, AHA/BHA, traitements intensifs
- "journee" : reapplication SPF, brumes
- "tous" : nettoyants, hydratants basiques, produits sans actifs photosensibles

photosensitive = true si contient :
- Retinol, retinaldehyde, tretinoine
- AHA (acide glycolique, lactique, mandelique)
- BHA (acide salicylique a haute concentration)
- Vitamine C pure (acide ascorbique)
- Benzoyl peroxide

occlusivity (1=tres leger, 5=tres riche) :
- 1 : eaux, brumes, gels, lotions legeres
- 2 : serums, fluides legers
- 3 : cremes legeres, emulsions
- 4 : cremes riches, baumes legers
- 5 : baumes epais, huiles, onguents

cleansing_power (1=tres doux, 5=tres puissant) :
- 1 : eaux micellaires douces, laits
- 2 : gels doux sans sulfate
- 3 : nettoyants mousse standards
- 4 : nettoyants purifiants, anti-acne
- 5 : demaquillants waterproof, nettoyants profonds

active_tag :
- "hydration" : acide hyaluronique, glycerine, ceramides, uree
- "acne" : BHA, niacinamide, zinc, peroxyde de benzoyle
- "repair" : panthenol, centella, allantoine, ceramides

PRODUIT A ANALYSER : {nom_produit}

Retourne UNIQUEMENT le JSON, rien d'autre."""


# =============================================================================
# PROMPT EXPERT POUR ANALYSE DE ROUTINE
# =============================================================================

PROMPT_ANALYSE_ROUTINE = """Tu es un dermatologue expert avec 20 ans d'experience.
Tu dois creer une routine de soins personnalisee basee sur le contexte suivant.

## PROFIL PATIENT
- Type de peau: {type_peau}
- Tranche d'age: {tranche_age}
- Niveau de stress: {niveau_stress}/10
- Conditions cutanees: {maladies_peau}
- Allergies/intolerances: {allergies}
- Objectifs: {objectifs}

## PRODUITS DISPONIBLES
{produits_json}

## CONDITIONS ENVIRONNEMENTALES ACTUELLES
- Ville: {ville}
- UV actuel: {uv} ({niveau_uv})
- UV max du jour: {uv_max}
- Humidite: {humidite}% ({niveau_humidite})
- Temperature: {temperature}C
- PM2.5: {pm25} ug/m3 ({niveau_pollution})

## PREVISIONS 3 JOURS
{previsions_json}

## HISTORIQUE DES 3 DERNIERES ANALYSES
{historique_json}

{instructions_supplementaires}

## REGLES
1. Utilise UNIQUEMENT les produits de la liste ci-dessus
2. Respecte les contra-indications (photosensibilite + UV eleve, allergies du patient)
3. Ordonne les produits du plus aqueux au plus occlusif
4. Adapte la routine aux conditions meteo actuelles et previsions
5. Si le patient a des maladies de peau, priorise les produits adaptes
6. Assure la continuite avec les analyses precedentes (pas de changements brusques)
7. Prends en compte le stress du patient (stress eleve = routine apaisante, produits doux)
8. Si pollution elevee, insiste sur le nettoyage
9. Tout le texte doit etre en francais

## FORMAT DE REPONSE (JSON strict)
{{
    "routine_matin": [
        {{"produit": "Nom du produit", "raison": "Pourquoi ce produit maintenant"}}
    ],
    "routine_soir": [
        {{"produit": "Nom du produit", "raison": "Pourquoi ce produit maintenant"}}
    ],
    "alertes": ["Alerte 1 si applicable"],
    "conseils_jour": "Conseil personnalise pour aujourd'hui",
    "resume": "Resume court de la strategie pour cette routine"
}}

Retourne UNIQUEMENT le JSON, rien d'autre."""


# =============================================================================
# STRUCTURE RESULTAT
# =============================================================================

@dataclass
class ResultatAnalyseIA:
    """Resultat de l'analyse IA d'un produit."""
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
# CLIENT GEMINI
# =============================================================================

class ClientGemini:
    """
    Client pour l'API Gemini de Google.

    Permet d'analyser des produits cosmetiques et de generer
    des recommandations de routine dermatologique.
    """

    def __init__(self, api_key: str = "", model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def est_configure(self) -> bool:
        """Retourne True si la cle API est definie."""
        return bool(self.api_key)

    def generer(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> Optional[str]:
        """Envoie un prompt a Gemini et retourne la reponse brute."""
        if not self.api_key:
            print("[Gemini] Erreur: cle API non configuree")
            return None

        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        prompt_court = prompt[:80].replace('\n', ' ')
        print(f"[Gemini] Envoi requete vers {self.model}...")
        print(f"[Gemini]   Prompt: {prompt_court}...")
        print(f"[Gemini]   Tokens max: {max_tokens} | Temperature: {temperature}")
        t0 = time.time()

        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=60
            )
            duree = time.time() - t0
            print(f"[Gemini] Reponse recue en {duree:.1f}s (HTTP {response.status_code})")
            response.raise_for_status()

            data = response.json()
            candidates = data.get("candidates", [])

            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    texte = parts[0].get("text", "").strip()
                    print(f"[Gemini] Reponse OK ({len(texte)} caracteres)")
                    return texte

            print("[Gemini] Reponse vide (aucun candidat)")
            return None

        except requests.RequestException as e:
            duree = time.time() - t0
            print(f"[Gemini] Erreur apres {duree:.1f}s: {e}")
            return None

    def _extraire_json(self, texte: str) -> Optional[dict]:
        """Extrait un objet JSON d'un texte, meme s'il est entoure de texte."""
        if not texte:
            return None

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

        # Chercher plus largement (JSON imbrique possible)
        start = texte.find('{')
        if start != -1:
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
        """Analyse un produit cosmetique et retourne ses caracteristiques."""
        print(f"\n{'='*50}")
        print(f"[Gemini] Analyse produit: {nom_produit}")
        print(f"[Gemini] Modele: {self.model}")
        print(f"{'='*50}")
        prompt = PROMPT_ANALYSE_PRODUIT.format(nom_produit=nom_produit)
        reponse = self.generer(prompt)

        if not reponse:
            return ResultatAnalyseIA(
                succes=False,
                erreur="Pas de reponse de Gemini. Verifie ta connexion internet et ta cle API."
            )

        print(f"[Gemini] Reponse brute: {reponse[:300]}")

        data = self._extraire_json(reponse)

        if data is None:
            return ResultatAnalyseIA(
                succes=False,
                erreur=f"Impossible de parser la reponse:\n{reponse[:150]}..."
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
        conditions_actuelles,
        previsions: list,
        profil,
        historique_recent: list,
        ville: str = "",
        mode: str = "rapide",
        instructions_jour: str = "",
        niveau_stress_jour: int = None,
    ) -> dict:
        """
        Analyse complete pour generer une routine dermatologique personnalisee.

        Args:
            produits: Liste de ProduitDerma
            conditions_actuelles: DonneesEnvironnementales
            previsions: Liste de PrevisionJournaliere
            profil: ProfilUtilisateur
            historique_recent: Liste de EntreeHistorique (3 derniers)
            ville: Nom de la ville
            mode: "rapide" ou "detaille"
            instructions_jour: Instructions specifiques du jour (mode detaille)
            niveau_stress_jour: Niveau de stress du jour (mode detaille)

        Returns:
            dict avec routine_matin, routine_soir, alertes, conseils_jour, resume
        """
        # Construire le JSON des produits
        produits_json = json.dumps(
            [p.vers_dict() for p in produits],
            ensure_ascii=False,
            indent=2,
        )

        # Construire le JSON des previsions
        previsions_json = json.dumps(
            [p.vers_dict() for p in previsions],
            ensure_ascii=False,
            indent=2,
        ) if previsions else "Aucune prevision disponible"

        # Construire le JSON de l'historique
        if historique_recent:
            hist_data = []
            for h in historique_recent:
                hist_data.append({
                    "date": h.date,
                    "mode": h.mode,
                    "routine_matin": h.routine_matin,
                    "routine_soir": h.routine_soir,
                    "resume": h.resume_ia,
                })
            historique_json = json.dumps(hist_data, ensure_ascii=False, indent=2)
        else:
            historique_json = "Aucun historique disponible (premiere analyse)"

        # Instructions supplementaires (mode detaille)
        instructions_supplementaires = ""
        if mode == "detaille":
            parts = ["## INSTRUCTIONS DU JOUR (MODE DETAILLE)"]
            if niveau_stress_jour is not None:
                parts.append(f"- Niveau de stress actuel: {niveau_stress_jour}/10")
            if instructions_jour:
                parts.append(f"- Instructions specifiques: {instructions_jour}")
            instructions_supplementaires = "\n".join(parts)

        # Niveau de stress (du jour ou du profil)
        stress = niveau_stress_jour if niveau_stress_jour is not None else profil.niveau_stress

        # Construire le prompt
        prompt = PROMPT_ANALYSE_ROUTINE.format(
            type_peau=profil.type_peau.value,
            tranche_age=profil.tranche_age.value,
            niveau_stress=stress,
            maladies_peau=", ".join(profil.maladies_peau) if profil.maladies_peau else "Aucune",
            allergies=", ".join(profil.allergies) if profil.allergies else "Aucune",
            objectifs=", ".join(
                o.value if hasattr(o, 'value') else str(o) for o in profil.objectifs
            ) if profil.objectifs else "Aucun specifie",
            produits_json=produits_json,
            ville=ville,
            uv=conditions_actuelles.indice_uv,
            niveau_uv=conditions_actuelles.niveau_uv,
            uv_max=conditions_actuelles.indice_uv_max,
            humidite=conditions_actuelles.humidite_relative,
            niveau_humidite=conditions_actuelles.niveau_humidite,
            temperature=conditions_actuelles.temperature,
            pm25=conditions_actuelles.pm2_5 if conditions_actuelles.pm2_5 else "N/A",
            niveau_pollution=conditions_actuelles.niveau_pollution,
            previsions_json=previsions_json,
            historique_json=historique_json,
            instructions_supplementaires=instructions_supplementaires,
        )

        # Logs contexte
        print(f"\n{'='*50}")
        print(f"[Gemini] Analyse routine ({mode})")
        print(f"[Gemini]   Ville: {ville}")
        print(f"[Gemini]   Produits: {len(produits)}")
        print(f"[Gemini]   UV: {conditions_actuelles.indice_uv} | Humidite: {conditions_actuelles.humidite_relative}%")
        print(f"[Gemini]   Previsions: {len(previsions)} jours")
        print(f"[Gemini]   Historique: {len(historique_recent)} analyses precedentes")
        print(f"[Gemini]   Stress: {stress}/10")
        if mode == "detaille" and instructions_jour:
            print(f"[Gemini]   Instructions: {instructions_jour[:80]}")
        print(f"[Gemini] Modele: gemini-2.5-flash")
        print(f"[Gemini] Taille prompt: ~{len(prompt)} caracteres")
        print(f"{'='*50}")

        # Utiliser Gemini 2.5 Flash pour l'analyse (plus capable)
        client_analyse = ClientGemini(
            api_key=self.api_key,
            model="gemini-2.5-flash",
        )

        reponse = client_analyse.generer(prompt, max_tokens=4096, temperature=0.4)

        if not reponse:
            print("[Gemini] ECHEC: pas de reponse")
            return {
                "erreur": "Pas de reponse de Gemini. Verifie ta connexion internet et ta cle API.",
                "routine_matin": [],
                "routine_soir": [],
                "alertes": [],
                "conseils_jour": "",
                "resume": "",
            }

        # Parser la reponse JSON
        resultat = self._extraire_json(reponse)

        if resultat is None:
            print(f"[Gemini] ECHEC: JSON invalide")
            print(f"[Gemini] Reponse brute: {reponse[:300]}")
            return {
                "erreur": f"Impossible de parser la reponse IA:\n{reponse[:200]}...",
                "routine_matin": [],
                "routine_soir": [],
                "alertes": [],
                "conseils_jour": "",
                "resume": "",
            }

        # Logs resultat
        nb_matin = len(resultat.get("routine_matin", []))
        nb_soir = len(resultat.get("routine_soir", []))
        nb_alertes = len(resultat.get("alertes", []))
        print(f"[Gemini] SUCCES: {nb_matin} produits matin, {nb_soir} produits soir, {nb_alertes} alertes")

        # S'assurer que tous les champs existent
        return {
            "routine_matin": resultat.get("routine_matin", []),
            "routine_soir": resultat.get("routine_soir", []),
            "alertes": resultat.get("alertes", []),
            "conseils_jour": resultat.get("conseils_jour", ""),
            "resume": resultat.get("resume", ""),
        }
