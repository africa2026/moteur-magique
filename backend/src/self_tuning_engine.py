# -*- coding: utf-8 -*-
"""
Self-Tuning Engine - Moteur de Rédaction Magique v5.0
Ce module permet à l'IA d'apprendre le style de l'utilisateur (Padre Alpha)
à partir de textes fournis, pour affiner la règle des 60/40.
"""

import logging
import json
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SelfTuningEngine:
    def __init__(self):
        self.profile_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_style_profile.json')
        self.ensure_profile_exists()

    def ensure_profile_exists(self):
        """S'assure que le fichier de profil existe."""
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        if not os.path.exists(self.profile_path):
            default_profile = {
                "name": "Padre Alpha",
                "learned_traits": [
                    "Clarté académique",
                    "Sensibilité pastorale",
                    "Structure logique forte"
                ],
                "vocabulary": [],
                "training_iterations": 0
            }
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(default_profile, f, indent=4)

    def train_on_text(self, text: str) -> Dict[str, Any]:
        """
        Analyse un texte fourni par l'utilisateur pour extraire son ADN stylistique.
        """
        logger.info(f"Entraînement du style sur un nouveau texte de {len(text)} caractères.")
        
        # Simulation de l'extraction de traits stylistiques par LLM
        new_traits = []
        if "Dieu" in text or "foi" in text:
            new_traits.append("Vocabulaire théologique incarné")
        if "cependant" in text or "néanmoins" in text:
            new_traits.append("Nuance dialectique fréquente")
            
        if not new_traits:
            new_traits.append("Rythme de phrase équilibré")

        # Mise à jour du profil
        with open(self.profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
            
        for trait in new_traits:
            if trait not in profile["learned_traits"]:
                profile["learned_traits"].append(trait)
                
        profile["training_iterations"] += 1
        
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=4)

        return {
            "success": True,
            "message": "ADN stylistique mis à jour avec succès.",
            "new_traits_discovered": new_traits,
            "total_iterations": profile["training_iterations"],
            "current_profile": profile["learned_traits"]
        }

# Instance globale
self_tuning_engine = SelfTuningEngine()
