# -*- coding: utf-8 -*-
"""
Suggestions Routes
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

suggestions_bp = Blueprint('suggestions', __name__, url_prefix='/api')


@suggestions_bp.route('/suggestions', methods=['POST'])
def get_suggestions():
    """
    Ottieni suggestions magiques per un testo
    
    POST /api/suggestions
    Body: {
        "text": "Il testo da analizzare..."
    }
    """
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Testo richiesto'
            }), 400
        
        # Suggestions mock per ora
        suggestions = [
            {
                'title': 'Sistema Preventivo',
                'text': 'Il Sistema Preventivo di Don Bosco...',
                'confidence': 85,
                'source': 'Corpus Salesiano'
            },
            {
                'title': 'Amorevolezza',
                'text': 'L\'amorevolezza è il cuore...',
                'confidence': 78,
                'source': 'Costituzioni SDB'
            }
        ]
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Errore suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suggestions_bp.route('/search', methods=['POST'])
def search_corpus():
    """
    Ricerca nel corpus salesiano
    
    POST /api/search
    Body: {
        "query": "Sistema Preventivo",
        "mode": "deep_research",          # optionnel
        "sources": ["corpus_salesiano", "semantic_scholar", "wikipedia"]  # optionnel
    }

    Réponse (contrat stable, consommé par le frontend) :
    {
        "success": true,
        "query": "...",
        "results": [ {title, source, type, snippet, relevance_score, url, ...} ],
        "count": 12,
        "suggestions": [...],
        "stats": {...}
    }
    """
    
    try:
        data = request.get_json(silent=True) or {}
        query = (data.get('query') or '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query richiesta'
            }), 400
        
        # REAL SEARCH IMPLEMENTATION
        # CORRECTED IMPORT - ligne corrigée
        from src.multi_source_search import MultiSourceSearchEngine
        search_engine = MultiSourceSearchEngine()
        
        # Fonti richieste dal client (fallback sul corpus salesiano)
        requested_sources = data.get('sources') or [
            'corpus_salesiano',
            'semantic_scholar',
            'wikipedia',
        ]
        filters = {'sources': requested_sources}
        
        # Esegui ricerca reale
        payload = search_engine.search(query, filters=filters)
        
        # Le moteur renvoie un objet {results, suggestions, stats}. On normalise
        # ici pour que `results` soit TOUJOURS une liste plate de documents :
        # c'est le contrat attendu par le frontend (data.results.map).
        if isinstance(payload, dict):
            results = payload.get('results') or []
            suggestions = payload.get('suggestions') or []
            stats = payload.get('stats') or {}
            engine_error = payload.get('error')
            engine_success = payload.get('success', True)
        else:
            results = payload or []
            suggestions = []
            stats = {}
            engine_error = None
            engine_success = True
        
        if not isinstance(results, list):
            results = []
        
        if not engine_success:
            logger.error(f"Errore ricerca multi-fonte: {engine_error}")
            return jsonify({
                'success': False,
                'error': engine_error or 'Errore durante la ricerca',
                'query': query,
                'results': [],
                'count': 0
            }), 502
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results),
            'suggestions': suggestions,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Errore search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'results': [],
            'count': 0
        }), 500


@suggestions_bp.route('/corpus/stats', methods=['GET'])
def corpus_stats():
    """
    Statistiche corpus salesiano
    
    GET /api/corpus/stats
    """
    
    try:
        stats = {
            'total_documents': 15,
            'categories': 5,
            'total_words': 50000,
            'languages': ['IT', 'FR', 'EN']
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Errore stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
