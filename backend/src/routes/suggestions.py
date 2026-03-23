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
        "query": "Sistema Preventivo"
    }
    """
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query richiesta'
            }), 400
        
        # REAL SEARCH IMPLEMENTATION
        # CORRECTED IMPORT - ligne corrigée
        from src.multi_source_search import MultiSourceSearchEngine
        search_engine = MultiSourceSearchEngine()
        
        # Esegui ricerca reale
        # Pass sources via filters if needed, or just query
        filters = {"sources": ["corpus_salesiano", "semantic_scholar", "wikipedia"]}
        results = search_engine.search(query, filters=filters)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Errore search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
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
