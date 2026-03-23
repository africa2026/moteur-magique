# -*- coding: utf-8 -*-
"""
Insight Engine - Moteur de Rédaction Magique v4.0
Genera insight contestuali e multi-prospettiva per i risultati di ricerca.
"""

import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class InsightEngine:
    def __init__(self):
        self.templates = {
            'researcher': [
                "Questo studio offre dati quantitativi utili per supportare la tesi su {topic}.",
                "Analisi fondamentale per comprendere l'evoluzione storica di {topic}.",
                "Fonte primaria essenziale per una ricostruzione filologica accurata.",
                "Contributo accademico che evidenzia le criticità metodologiche nello studio di {topic}.",
                "Utile per confrontare le diverse interpretazioni storiografiche su {topic}."
            ],
            'journalist': [
                "Ottimo spunto per un articolo di attualità su {topic}.",
                "Dato chiave: evidenzia come {topic} sia ancora rilevante oggi.",
                "Citazione perfetta per un box di approfondimento o un'infografica.",
                "Collega questo evento storico alle sfide educative contemporanee.",
                "Angolatura narrativa: racconta la storia di {topic} dal punto di vista dei protagonisti."
            ],
            'pastoral': [
                "Spunto per l'omelia: come {topic} ci parla della cura educativa oggi?",
                "Materiale utile per la formazione degli animatori su {topic}.",
                "Riflessione spirituale: {topic} come esempio di dedizione vocazionale.",
                "Domanda per il gruppo giovani: cosa ci insegna {topic} sulle nostre scelte?",
                "Applicazione pratica: tradurre {topic} in un gesto concreto di carità educativa."
            ]
        }

    def generate_insights(self, result: Dict[str, Any], query: str) -> Dict[str, Dict[str, str]]:
        """
        Genera insight dinamici basati sui metadati del risultato.
        """
        try:
            title = result.get('title', 'Documento').lower()
            abstract = result.get('abstract', '').lower()
            source_type = result.get('type', 'generic')
            
            # Estrai topic principale (molto semplice per ora)
            topic = "questo argomento"
            if "bosco" in title or "bosco" in abstract:
                topic = "Don Bosco"
            elif "salesian" in title:
                topic = "il carisma salesiano"
            elif "educat" in title:
                topic = "l'educazione"
            elif "giovan" in title:
                topic = "il mondo giovanile"
            
            # Seleziona template in base al tipo di fonte
            if source_type in ['salesian', 'salesian_web']:
                res_tpl = "Fonte interna autorevole: fondamentale per definire la posizione ufficiale su {topic}."
                jou_tpl = "La voce ufficiale: come comunicare {topic} senza filtri."
                pas_tpl = "Alle radici del carisma: {topic} come guida per l'azione pastorale odierna."
            elif source_type in ['academic_paper', 'academic_source', 'academic_thesis']:
                res_tpl = random.choice(self.templates['researcher']).format(topic=topic)
                jou_tpl = "Prospettiva scientifica: cosa dicono i dati su {topic}."
                pas_tpl = "Dialogo fede-ragione: approfondire {topic} con rigore e passione."
            elif source_type == 'web':
                res_tpl = "Fonte web da verificare: utile per mappare la percezione pubblica di {topic}."
                jou_tpl = random.choice(self.templates['journalist']).format(topic=topic)
                pas_tpl = "Segni dei tempi: cosa dice la rete su {topic}?"
            else:
                # Fallback generico
                res_tpl = random.choice(self.templates['researcher']).format(topic=topic)
                jou_tpl = random.choice(self.templates['journalist']).format(topic=topic)
                pas_tpl = random.choice(self.templates['pastoral']).format(topic=topic)

            return {
                'researcher': {
                    'theoretical_framework': res_tpl,
                    'methodology': "Analisi documentale e contestuale.",
                    'key_authors': self._extract_authors(result),
                    'academic_utility': "Supporto bibliografico primario."
                },
                'journalist': {
                    'narrative_angle': jou_tpl,
                    'key_facts': f"Pubblicato nel {result.get('year', 'N.D.')} da {result.get('source', 'Fonte sconosciuta')}.",
                    'quote': self._extract_quote(abstract),
                    'editorial_suggestion': "Inserire in un box laterale o come incipit."
                },
                'pastoral': {
                    'biblical_key': "Va' e anche tu fa' lo stesso (Lc 10,37)",
                    'catechesis_prompt': pas_tpl,
                    'prayer_intent': f"Preghiamo per chi si dedica a {topic}.",
                    'action_item': "Condividere questo spunto nella prossima riunione formativa."
                }
            }
        except Exception as e:
            logger.error(f"Errore generazione insight: {e}")
            return self._get_fallback_insights()

    def _extract_authors(self, result: Dict) -> str:
        authors = result.get('authors', [])
        if isinstance(authors, list) and authors:
            return ", ".join(authors[:2])
        return "Autore non specificato"

    def _extract_quote(self, text: str) -> str:
        if not text or len(text) < 20:
            return "Nessuna citazione rilevante disponibile."
        # Prendi una frase a caso o la prima
        sentences = text.split('.')
        for s in sentences:
            if len(s) > 30 and len(s) < 150:
                return s.strip() + "."
        return sentences[0][:100] + "..."

    def _get_fallback_insights(self) -> Dict:
        return {
            'researcher': {'theoretical_framework': "Analisi in corso..."},
            'journalist': {'narrative_angle': "Analisi in corso..."},
            'pastoral': {'catechesis_prompt': "Analisi in corso..."}
        }

# Istanza globale
insight_engine = InsightEngine()
