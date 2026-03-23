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


@pdf_chat_bp.route('/chat', methods=['POST'])
def chat_with_pdf():
    """
    Chat with PDF
    
    POST /api/pdf/chat
    Body: {
        "file_id": "PDF-xxx",
        "message": "What is this about?"
    }
    """
    
    try:
        data = request.get_json()
        
        file_id = data.get('file_id')
        message = data.get('message')
        
        if not file_id or not message:
            return jsonify({
                'success': False,
                'error': 'file_id and message required'
            }), 400
        
        # Mock response
        response = {
            'success': True,
            'response': f'Risposta alla domanda: {message}',
            'citations': [
                {
                    'page': 1,
                    'text': 'Testo citato...'
                }
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Errore chat PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
