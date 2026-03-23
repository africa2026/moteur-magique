# -*- coding: utf-8 -*-
"""
Theme Router - Moteur de Rédaction Magique v5.0
Analyse le texte ou la requête pour détecter le thème principal et 
sélectionner dynamiquement les moteurs de recherche les plus pertinents.
"""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ThemeRouter:
    def __init__(self):
        # Définition des thèmes et de leurs mots-clés associés
        self.themes = {
            'theology_exegesis': {
                'keywords': ['dieu', 'bible', 'exégèse', 'jésus', 'christ', 'évangile', 'théologie', 'patristique', 'vatican', 'pape', 'église', 'sacrement', 'foi', 'salut'],
                'preferred_sources': ['vatican', 'salesian_online', 'sdb_org', 'donboscosanto', 'cairn', 'persee'],
                'disabled_sources': ['pubmed', 'arxiv']
            },
            'philosophy': {
                'keywords': ['philosophie', 'éthique', 'morale', 'épistémologie', 'métaphysique', 'kant', 'aristote', 'platon', 'phénoménologie', 'ontologie', 'logique'],
                'preferred_sources': ['sep', 'cairn', 'persee', 'uqac_classiques', 'openedition'],
                'disabled_sources': ['pubmed']
            },
            'psychology_education': {
                'keywords': ['psychologie', 'éducation', 'pédagogie', 'apprentissage', 'cognitif', 'comportement', 'développement', 'enfant', 'adolescent', 'système préventif', 'don bosco'],
                'preferred_sources': ['semantic_scholar', 'core', 'base', 'cairn', 'theses_fr', 'salesian_online'],
                'disabled_sources': ['arxiv']
            },
            'african_cultures': {
                'keywords': ['afrique', 'culture africaine', 'tradition', 'ancêtres', 'mythe', 'oralité', 'tribu', 'ethnie', 'beti', 'bantou', 'colonisation', 'décolonisation', 'anthropologie'],
                'preferred_sources': ['uqac_classiques', 'persee', 'cairn', 'openedition', 'gallica', 'theses_fr'],
                'disabled_sources': ['pubmed', 'arxiv']
            },
            'history': {
                'keywords': ['histoire', 'siècle', 'révolution', 'guerre', 'archive', 'moyen-âge', 'antiquité', 'chronologie', 'historique'],
                'preferred_sources': ['gallica', 'gutenberg', 'persee', 'cairn', 'theses_fr'],
                'disabled_sources': ['pubmed']
            },
            'science_medicine': {
                'keywords': ['médecine', 'santé', 'biologie', 'physique', 'chimie', 'maladie', 'traitement', 'clinique', 'neuroscience'],
                'preferred_sources': ['pubmed', 'semantic_scholar', 'core', 'openalex'],
                'disabled_sources': ['vatican', 'salesian_online', 'sep']
            }
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyse un texte pour déterminer le ou les thèmes dominants.
        Retourne un profil thématique avec les sources à privilégier.
        """
        text_lower = text.lower()
        theme_scores = {theme: 0 for theme in self.themes}
        
        # Calcul des scores basés sur la fréquence des mots-clés
        for theme, data in self.themes.items():
            for keyword in data['keywords']:
                # Utilisation d'expressions régulières pour trouver des mots entiers
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
                theme_scores[theme] += matches
                
        # Identifier le thème principal (ou les thèmes si scores proches)
        max_score = max(theme_scores.values()) if theme_scores else 0
        
        detected_themes = []
        if max_score > 0:
            # On garde les thèmes qui ont au moins 50% du score maximum
            threshold = max_score * 0.5
            detected_themes = [theme for theme, score in theme_scores.items() if score >= threshold]
        
        # Si aucun thème n'est détecté, on utilise un profil généraliste
        if not detected_themes:
            return {
                'detected_themes': ['general'],
                'preferred_sources': ['semantic_scholar', 'core', 'crossref', 'duckduckgo', 'wikipedia'],
                'disabled_sources': [],
                'scores': theme_scores
            }
            
        # Agréger les sources préférées et désactivées
        preferred_sources = set()
        disabled_sources = set()
        
        for theme in detected_themes:
            preferred_sources.update(self.themes[theme]['preferred_sources'])
            disabled_sources.update(self.themes[theme]['disabled_sources'])
            
        # Résoudre les conflits (si une source est à la fois préférée et désactivée, on la garde si elle est préférée par le thème principal)
        # Pour simplifier, on retire les disabled qui sont dans preferred
        disabled_sources = disabled_sources - preferred_sources
        
        logger.info(f"🧠 ThemeRouter: Thèmes détectés: {detected_themes}")
        
        return {
            'detected_themes': detected_themes,
            'preferred_sources': list(preferred_sources),
            'disabled_sources': list(disabled_sources),
            'scores': theme_scores
        }

# Instance globale
theme_router = ThemeRouter()
