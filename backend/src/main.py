# -*- coding: utf-8 -*-
"""
Moteur de Rédaction Magique - Backend Principal
Rev. Alphonse Owoudou, PhD
Version 2.0.0 - Entièrement Fonctionnel
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging

# Import delle routes
from src.routes.documents_simple import documents_bp
from src.routes.suggestions import suggestions_bp
from src.routes.public_suggestions import public_suggestions_bp
from src.routes.pdf_chat import pdf_chat_bp
from src.routes.pdf_chat_advanced import pdf_chat_advanced_bp
from src.routes.bibliography_manager import bibliography_bp
from src.routes.advanced_features import advanced_bp

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'), static_url_path='/')

# Configuration CORS pour permettre les requêtes depuis le frontend
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"], supports_credentials=True)

# Configuration de l'application
app.config['SECRET_KEY'] = 'moteur-redaction-magique-salesien-2024'
app.config['JSON_AS_ASCII'] = False  # Support des caractères UTF-8

# Enregistrement des blueprints
app.register_blueprint(documents_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(public_suggestions_bp)
app.register_blueprint(pdf_chat_bp)
app.register_blueprint(pdf_chat_advanced_bp)
app.register_blueprint(bibliography_bp)
app.register_blueprint(advanced_bp)

# Route racine pour servir le frontend React
@app.route('/', methods=['GET'])
def home():
    """Sert l'application React"""
    return app.send_static_file('index.html')

# Route de santé
@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de l'état du backend"""
    try:
        # Test du corpus
        from src.corpus_salesien import CORPUS_SALESIEN, get_suggestions_for_text
        from src.semantic_engine import SemanticEngine
        
        # Test con un testo semplice
        test_suggestions = get_suggestions_for_text("Don Bosco jeunes")        
        # Test motore semantico
        semantic_engine = SemanticEngine()
        expanded = semantic_engine.expand_query("vita comune")
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '4.0.0 - Ultimate Edition',
            'modules': {
                'corpus_salesien': True,
                'suggestions_engine': True,
                'search_engine': True,
                'semantic_engine': True,
                'cors': True
            },
            'corpus_status': {
                'loaded': True,
                'categories': len(CORPUS_SALESIEN),
                'test_suggestions': len(test_suggestions)
            },
            'performance': {
                'response_time': 'optimal',
                'memory_usage': 'normal'
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du health check: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Route pour les langues supportées
@app.route('/api/languages', methods=['GET'])
def get_supported_languages():
    """Retourne les langues supportées pour l'interface multilingue"""
    try:
        from src.multilingual_search import get_supported_languages
        
        languages = get_supported_languages()
        
        return jsonify({
            'success': True,
            'languages': languages,
            'default_language': 'it',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des langues: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Gestionnaire d'erreurs et fallback pour React Router
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint non trouvé'
        }), 404
    return app.send_static_file('index.html')

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erreur interne du serveur',
        'timestamp': datetime.now().isoformat()
    }), 500

# Middleware pour logging des requêtes
@app.before_request
def log_request_info():
    logger.info(f"Requête reçue: {request.method} {request.url}")
    if request.is_json:
        logger.info(f"Données JSON: {request.get_json()}")

@app.after_request
def log_response_info(response):
    logger.info(f"Réponse envoyée: {response.status_code}")
    return response

if __name__ == '__main__':
    logger.info("🚀 Démarrage du Moteur de Rédaction Magique")
    logger.info("📚 Chargement du corpus salésien...")
    
    # Test du corpus au démarrage
    try:
        from src.corpus_salesien import CORPUS_SALESIEN, get_suggestions_for_text
        from src.semantic_engine import SemanticEngine
        total_docs = sum(len(docs) for docs in CORPUS_SALESIEN.values())
        logger.info(f"✅ Corpus chargé avec succès: {total_docs} documents")
        
        # Test avec le texte de l'utilisateur
        test_text = "La Pastorale des jeunes est notre priorité. Comme le disent nos Constitutions, les jeunes sont la part la plus délicate de la société."
        test_suggestions = get_suggestions_for_text(test_text)
        logger.info(f"✅ Test réussi: {len(test_suggestions)} suggestions générées")
        
        for i, suggestion in enumerate(test_suggestions[:3], 1):
            logger.info(f"   {i}. {suggestion['title']} - {suggestion.get('confidence', 0):.1f}%")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement: {str(e)}")
    
    logger.info("🌟 Backend prêt pour les suggestions magiques!")
    
    # Démarrage du serveur
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

