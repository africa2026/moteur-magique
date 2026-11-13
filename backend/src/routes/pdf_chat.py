# -*- coding: utf-8 -*-
"""
PDF Chat Routes
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

pdf_chat_bp = Blueprint('pdf_chat', __name__, url_prefix='/api/pdf')


@pdf_chat_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Upload PDF file
    
    POST /api/pdf/upload
    """
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Mock upload
        file_id = f"PDF-{file.filename}"
        
        logger.info(f"PDF uploaded: {file_id}")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': file.filename,
            'message': 'PDF uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Errore upload PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# NB: la route POST /api/pdf/chat est fournie par
# backend/src/routes/pdf_chat_advanced.py (implémentation réelle avec contexte
# documentaire). Une ancienne version "mock" était déclarée ici et, étant
# enregistrée en premier, masquait l'implémentation réelle. Elle a été supprimée.

