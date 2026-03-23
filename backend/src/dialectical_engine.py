# -*- coding: utf-8 -*-
"""
Dialectical Engine - Moteur de Rédaction Magique v5.0
Analyse les résultats de recherche par rapport à une affirmation (claim)
et les classe en trois catégories : Soutien, Contradiction, Approfondissement.
"""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DialecticalEngine:
    def __init__(self):
        # Mots-clés indiquant une contradiction ou une nuance
        self.contradiction_markers = [
            'cependant', 'toutefois', 'néanmoins', 'au contraire', 'en revanche',
            'critique', 'limite', 'remet en cause', 's\'oppose', 'réfute',
            'débat', 'controverse', 'désaccord', 'nuance', 'faille', 'erreur',
            'however', 'although', 'nevertheless', 'on the contrary', 'critique',
            'challenge', 'refute', 'oppose', 'disagree', 'flaw'
        ]
        
        # Mots-clés indiquant un soutien fort
        self.support_markers = [
            'confirme', 'démontre', 'prouve', 'corrobore', 'soutient', 'valide',
            'en accord', 'comme le montre', 'évidence', 'certitude',
            'confirm', 'demonstrate', 'prove', 'corroborate', 'support', 'validate',
            'agree', 'evidence'
        ]

    def analyze_results(self, claim: str, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyse une liste de résultats par rapport à une affirmation (claim)
        et les répartit dans les catégories dialectiques.
        """
        if not claim or not results:
            return {'support': [], 'contradict': [], 'expand': []}

        claim_lower = claim.lower()
        # Extraire les mots-clés principaux de l'affirmation (très basique pour l'instant)
        claim_words = set(re.findall(r'\b\w{4,}\b', claim_lower))
        
        dialectical_results = {
            'support': [],
            'contradict': [],
            'expand': []
        }

        for result in results:
            text_to_analyze = f"{result.get('title', '')} {result.get('abstract', '')}".lower()
            
            # Calculer la pertinence de base (combien de mots du claim sont dans le résultat)
            result_words = set(re.findall(r'\b\w{4,}\b', text_to_analyze))
            overlap = len(claim_words.intersection(result_words))
            
            if overlap == 0:
                continue # Résultat non pertinent pour ce claim spécifique

            # Détecter les marqueurs
            has_contradiction = any(marker in text_to_analyze for marker in self.contradiction_markers)
            has_support = any(marker in text_to_analyze for marker in self.support_markers)
            
            # Logique de classification
            if has_contradiction:
                # Si on trouve des mots de contradiction ET que le sujet correspond, c'est probablement une critique
                result['dialectical_role'] = 'contradict'
                result['dialectical_reason'] = "Cette source semble présenter une perspective critique ou nuancée."
                dialectical_results['contradict'].append(result)
            elif has_support and overlap > len(claim_words) * 0.3:
                # Si on trouve des mots de soutien ET une forte correspondance thématique
                result['dialectical_role'] = 'support'
                result['dialectical_reason'] = "Cette source corrobore directement votre affirmation."
                dialectical_results['support'].append(result)
            else:
                # Par défaut, si c'est pertinent mais ni explicitement pour/contre, c'est un approfondissement
                result['dialectical_role'] = 'expand'
                result['dialectical_reason'] = "Cette source explore des concepts connexes pour aller plus loin."
                dialectical_results['expand'].append(result)

        # Trier chaque catégorie par score de pertinence (s'il existe)
        for category in dialectical_results:
            dialectical_results[category].sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        logger.info(f"⚖️ DialecticalEngine: {len(dialectical_results['support'])} soutiens, {len(dialectical_results['contradict'])} contradictions, {len(dialectical_results['expand'])} approfondissements.")
        
        return dialectical_results

# Instance globale
dialectical_engine = DialecticalEngine()
