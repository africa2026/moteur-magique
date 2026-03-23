# -*- coding: utf-8 -*-
"""
Public Suggestions Routes
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

public_suggestions_bp = Blueprint('public_suggestions', __name__, url_prefix='/api/public')


@public_suggestions_bp.route('/suggest', methods=['POST'])
def submit_suggestion():
    """
    Submit a public suggestion
    
    POST /api/public/suggest
    Body: {
        "type": "vocabulary|document|url|text|improvement|other",
        "content": "...",
        "email": "optional@email.com"
    }
    """
    
    try:
        data = request.get_json()
        
        suggestion_type = data.get('type')
        content = data.get('content')
        email = data.get('email', '')
        
        if not suggestion_type or not content:
            return jsonify({
                'success': False,
                'error': 'Type and content required'
            }), 400
        
        # Save suggestion to file
        suggestion_id = f"SUG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        import os
        import json
        
        suggestions_dir = "/home/ubuntu/data/suggestions"
        os.makedirs(suggestions_dir, exist_ok=True)
        
        suggestion_data = {
            'id': suggestion_id,
            'type': suggestion_type,
            'content': content,
            'email': email,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(suggestions_dir, f"{suggestion_id}.json"), 'w') as f:
            json.dump(suggestion_data, f, indent=2)
        
        logger.info(f"New suggestion saved: {suggestion_id} - Type: {suggestion_type}")
        
        return jsonify({
            'success': True,
            'suggestion_id': suggestion_id,
            'message': 'Grazie per il tuo suggerimento!'
        })
        
    except Exception as e:
        logger.error(f"Errore submit suggestion: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@public_suggestions_bp.route('/suggestions', methods=['GET'])
def list_suggestions():
    """
    List public suggestions (admin only)
    
    GET /api/public/suggestions
    """
    
    try:
        # Read suggestions from files
        import os
        import json
        
        suggestions_dir = "/home/ubuntu/data/suggestions"
        os.makedirs(suggestions_dir, exist_ok=True)
        
        suggestions = []
        for filename in os.listdir(suggestions_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(suggestions_dir, filename), 'r') as f:
                        suggestions.append(json.load(f))
                except:
                    pass
                    
        # Sort by date desc
        suggestions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Errore list suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
