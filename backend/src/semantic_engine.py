
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SemanticEngine:
    """
    Motore di ricerca semantica multilingue per il Corpus Salesiano.
    Gestisce sinonimi, concetti e traduzioni automatiche delle query.
    """
    
    def __init__(self):
        # Dizionario dei concetti chiave salesiani in 4 lingue
        self.concepts = {
            "vita_comune": {
                "it": ["vita comune", "vivere insieme", "vivere e lavorare insieme", "comunità", "famiglia", "fraternità"],
                "fr": ["vie commune", "vivre ensemble", "vivre et travailler ensemble", "communauté", "famille", "fraternité"],
                "en": ["common life", "living together", "living and working together", "community", "family", "fraternity"],
                "es": ["vida común", "vivir juntos", "comunidad", "familia", "fraternidad"],
                "pt": ["vida comum", "viver juntos", "comunidade", "família", "fraternidade"]
            },
            "lavoro": {
                "it": ["lavoro", "missione", "apostolato", "servizio", "opera"],
                "fr": ["travail", "mission", "apostolat", "service", "oeuvre"],
                "en": ["work", "mission", "apostolate", "service", "work"],
                "es": ["trabajo", "misión", "apostolado", "servicio", "obra"],
                "pt": ["trabalho", "missão", "apostolado", "serviço", "obra"]
            },
            "sistema_preventivo": {
                "it": ["sistema preventivo", "ragione", "religione", "amorevolezza"],
                "fr": ["système préventif", "raison", "religion", "affection"],
                "en": ["preventive system", "reason", "religion", "loving kindness"],
                "es": ["sistema preventivo", "razón", "religión", "amorevolezza"],
                "pt": ["sistema preventivo", "razão", "religião", "amorevolezza"]
            }
        }

    def expand_query(self, query: str, lang: str = "auto") -> List[str]:
        """
        Espande la query originale con sinonimi e traduzioni in altre lingue.
        Restituisce una lista di termini da cercare.
        """
        expanded_terms = [query.lower()]
        
        # Identifica i concetti presenti nella query
        for concept_key, languages in self.concepts.items():
            # Controlla se qualche termine del concetto è nella query
            found = False
            for l_code, terms in languages.items():
                for term in terms:
                    if term in query.lower():
                        found = True
                        break
                if found: break
            
            # Se trovato, aggiungi tutti i termini di tutte le lingue
            if found:
                for l_code, terms in languages.items():
                    expanded_terms.extend(terms)
                    
        return list(set(expanded_terms))  # Rimuovi duplicati

    def calculate_relevance(self, text: str, query_terms: List[str]) -> int:
        """
        Calcola la rilevanza semantica di un testo rispetto ai termini espansi.
        """
        score = 0
        text_lower = text.lower()
        
        for term in query_terms:
            if term in text_lower:
                # Termini più lunghi valgono di più (probabilmente più specifici)
                weight = len(term.split()) * 10
                score += weight
                
        return min(score, 100)  # Cap a 100
