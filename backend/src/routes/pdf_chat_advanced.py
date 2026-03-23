# -*- coding: utf-8 -*-
"""
Sistema Chat con PDF Avanzato
Moteur de Rédaction Magique - Rev. Alphonse Owoudou
Chat intelligente con documenti PDF usando OpenAI
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import os
import json
from typing import List, Dict, Any, Optional
import openai

# Setup logging
logger = logging.getLogger(__name__)

# Blueprint per chat PDF
pdf_chat_advanced_bp = Blueprint('pdf_chat_advanced', __name__)

# Configurazione OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')

class PDFChatEngine:
    """
    Motore di chat avanzato per PDF con:
    - Ricerca semantica nei chunks
    - Memoria conversazionale
    - Risposte contestuali
    - Citazioni precise
    """
    
    def __init__(self):
        self.conversations = {}  # Memoria conversazioni per documento
        self.max_context_chunks = 5  # Massimo 5 chunks per contesto
        self.max_conversation_history = 10  # Massimo 10 scambi in memoria
        
    def start_conversation(self, document_id: str, document_data: Dict) -> str:
        """Inizia una nuova conversazione con un PDF"""
        
        conversation_id = f"chat_{document_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepara il contesto del documento
        doc_context = {
            'document_id': document_id,
            'title': document_data.get('title', 'Documento'),
            'author': document_data.get('author', 'Sconosciuto'),
            'full_text': document_data.get('full_content', ''),
            'chunks': document_data.get('chunks', []),
            'metadata': document_data.get('advanced_metadata', {}),
            'entities': document_data.get('entities', {}),
            'concepts': document_data.get('concepts', []),
            'themes': document_data.get('themes', []),
            'summary': document_data.get('summary', {}),
            'structure': document_data.get('structure', {})
        }
        
        # Inizializza conversazione
        self.conversations[conversation_id] = {
            'document_context': doc_context,
            'history': [],
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        logger.info(f"Iniziata conversazione {conversation_id} per documento {document_id}")
        return conversation_id
    
    def chat_with_pdf(self, conversation_id: str, user_question: str) -> Dict[str, Any]:
        """Chat intelligente con il PDF"""
        
        if conversation_id not in self.conversations:
            return {
                'success': False,
                'error': 'Conversazione non trovata. Iniziare una nuova conversazione.'
            }
        
        conversation = self.conversations[conversation_id]
        doc_context = conversation['document_context']
        
        try:
            # 1. Trova i chunks più rilevanti per la domanda
            relevant_chunks = self._find_relevant_chunks(user_question, doc_context)
            
            # 2. Prepara il contesto per OpenAI
            context_text = self._prepare_context(relevant_chunks, doc_context)
            
            # 3. Prepara la cronologia conversazione
            conversation_history = self._prepare_conversation_history(conversation['history'])
            
            # 4. Genera risposta con OpenAI
            response = self._generate_response(
                user_question=user_question,
                context_text=context_text,
                conversation_history=conversation_history,
                document_metadata=doc_context
            )
            
            # 5. Salva nella cronologia
            conversation['history'].append({
                'timestamp': datetime.now().isoformat(),
                'user_question': user_question,
                'assistant_response': response['answer'],
                'relevant_chunks': [chunk['chunk_id'] for chunk in relevant_chunks],
                'citations': response.get('citations', [])
            })
            
            # Mantieni solo gli ultimi scambi
            if len(conversation['history']) > self.max_conversation_history:
                conversation['history'] = conversation['history'][-self.max_conversation_history:]
            
            conversation['last_activity'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'answer': response['answer'],
                'citations': response.get('citations', []),
                'relevant_chunks': relevant_chunks,
                'conversation_id': conversation_id,
                'document_title': doc_context['title']
            }
            
        except Exception as e:
            logger.error(f"Errore chat PDF: {str(e)}")
            return {
                'success': False,
                'error': f'Errore durante la chat: {str(e)}'
            }
    
    def _find_relevant_chunks(self, question: str, doc_context: Dict) -> List[Dict]:
        """Trova i chunks più rilevanti per la domanda"""
        
        chunks = doc_context.get('chunks', [])
        if not chunks:
            # Se non ci sono chunks, usa il testo completo
            return [{
                'chunk_id': 1,
                'content': doc_context['full_text'][:8000],  # Primi 8000 caratteri
                'relevance_score': 1.0,
                'chunk_type': 'full_text'
            }]
        
        question_lower = question.lower()
        relevant_chunks = []
        
        # Calcola rilevanza per ogni chunk
        for chunk in chunks:
            content = chunk.get('content', '').lower()
            relevance_score = 0.0
            
            # Punteggio base per parole chiave
            question_words = [word for word in question_lower.split() if len(word) > 3]
            for word in question_words:
                if word in content:
                    relevance_score += content.count(word) * 0.1
            
            # Bonus per entità salesiane
            salesien_entities = ['don bosco', 'salesien', 'jeunes', 'éducation', 'oratorio']
            for entity in salesien_entities:
                if entity in question_lower and entity in content:
                    relevance_score += 0.5
            
            # Bonus per concetti chiave
            concepts = doc_context.get('concepts', [])
            for concept in concepts:
                if concept.lower() in question_lower and concept.lower() in content:
                    relevance_score += 0.3
            
            if relevance_score > 0:
                chunk_data = {
                    **chunk,
                    'relevance_score': relevance_score
                }
                relevant_chunks.append(chunk_data)
        
        # Ordina per rilevanza e prendi i migliori
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Se nessun chunk rilevante, prendi i primi
        if not relevant_chunks and chunks:
            relevant_chunks = chunks[:self.max_context_chunks]
            for chunk in relevant_chunks:
                chunk['relevance_score'] = 0.1
        
        return relevant_chunks[:self.max_context_chunks]
    
    def _prepare_context(self, relevant_chunks: List[Dict], doc_context: Dict) -> str:
        """Prepara il contesto per OpenAI"""
        
        context_parts = []
        
        # Informazioni documento
        context_parts.append(f"DOCUMENTO: {doc_context['title']}")
        if doc_context['author']:
            context_parts.append(f"AUTORE: {doc_context['author']}")
        
        # Metadati utili
        metadata = doc_context.get('metadata', {})
        if metadata.get('language'):
            context_parts.append(f"LINGUA: {metadata['language']}")
        
        structure = doc_context.get('structure', {})
        if structure.get('estimated_type'):
            context_parts.append(f"TIPO: {structure['estimated_type']}")
        
        # Entità e concetti chiave
        entities = doc_context.get('entities', {})
        if entities.get('persone_salesiane'):
            context_parts.append(f"PERSONE SALESIANE: {', '.join(entities['persone_salesiane'][:5])}")
        
        concepts = doc_context.get('concepts', [])
        if concepts:
            context_parts.append(f"CONCETTI CHIAVE: {', '.join(concepts[:5])}")
        
        context_parts.append("\n" + "="*50 + "\n")
        
        # Chunks rilevanti
        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(f"SEZIONE {i+1} (Rilevanza: {chunk.get('relevance_score', 0):.2f}):")
            if chunk.get('page_number'):
                context_parts.append(f"[Pagina {chunk['page_number']}]")
            context_parts.append(chunk['content'])
            context_parts.append("\n" + "-"*30 + "\n")
        
        return "\n".join(context_parts)
    
    def _prepare_conversation_history(self, history: List[Dict]) -> str:
        """Prepara la cronologia conversazione"""
        
        if not history:
            return ""
        
        history_parts = ["CRONOLOGIA CONVERSAZIONE:"]
        
        # Prendi gli ultimi 5 scambi
        recent_history = history[-5:]
        
        for i, exchange in enumerate(recent_history):
            history_parts.append(f"\nSCAMBIO {i+1}:")
            history_parts.append(f"UTENTE: {exchange['user_question']}")
            history_parts.append(f"ASSISTENTE: {exchange['assistant_response']}")
        
        history_parts.append("\n" + "="*50 + "\n")
        return "\n".join(history_parts)
    
    def _generate_response(self, user_question: str, context_text: str, 
                          conversation_history: str, document_metadata: Dict) -> Dict[str, Any]:
        """Genera risposta usando OpenAI"""
        
        # Prompt specializzato per documenti salesiani
        system_prompt = f"""Sei un assistente esperto in pedagogia salesiana e documenti della Famiglia Salesiana. 
Rispondi alle domande basandoti ESCLUSIVAMENTE sul contenuto del documento fornito.

REGOLE IMPORTANTI:
1. Usa SOLO le informazioni presenti nel documento
2. Se la risposta non è nel documento, dillo chiaramente
3. Cita sempre le sezioni specifiche quando possibile
4. Mantieni il tono rispettoso e professionale
5. Se si tratta di temi salesiani, contestualizza con la tradizione salesiana
6. Rispondi nella lingua della domanda (italiano/francese)

DOCUMENTO ANALIZZATO: {document_metadata['title']}
AUTORE: {document_metadata.get('author', 'Non specificato')}
"""
        
        user_prompt = f"""
{conversation_history}

CONTESTO DEL DOCUMENTO:
{context_text}

DOMANDA DELL'UTENTE:
{user_question}

Rispondi alla domanda basandoti sul contenuto del documento. Se citi parti specifiche, indica la sezione di riferimento.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.3,  # Risposte più precise e meno creative
                top_p=0.9
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Estrai citazioni se presenti
            citations = self._extract_citations(answer, context_text)
            
            return {
                'answer': answer,
                'citations': citations,
                'model_used': 'gpt-4',
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Errore OpenAI: {str(e)}")
            
            # Fallback: risposta semplice basata su keyword matching
            return self._generate_fallback_response(user_question, context_text)
    
    def _extract_citations(self, answer: str, context_text: str) -> List[Dict]:
        """Estrai citazioni dalla risposta"""
        
        citations = []
        
        # Cerca riferimenti a sezioni
        import re
        section_refs = re.findall(r'SEZIONE (\d+)', answer, re.IGNORECASE)
        
        for section_num in section_refs:
            citations.append({
                'type': 'section_reference',
                'section': int(section_num),
                'text': f"Riferimento alla Sezione {section_num}"
            })
        
        # Cerca riferimenti a pagine
        page_refs = re.findall(r'[Pp]agina (\d+)', answer)
        
        for page_num in page_refs:
            citations.append({
                'type': 'page_reference',
                'page': int(page_num),
                'text': f"Riferimento alla Pagina {page_num}"
            })
        
        return citations
    
    def _generate_fallback_response(self, question: str, context_text: str) -> Dict[str, Any]:
        """Risposta di fallback senza OpenAI"""
        
        question_lower = question.lower()
        context_lower = context_text.lower()
        
        # Cerca frasi rilevanti nel contesto
        sentences = context_text.split('.')
        relevant_sentences = []
        
        question_words = [word for word in question_lower.split() if len(word) > 3]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = sum(1 for word in question_words if word in sentence_lower)
            
            if score > 0:
                relevant_sentences.append((sentence.strip(), score))
        
        # Ordina per rilevanza
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            answer = f"Basandomi sul documento, posso dire che: {relevant_sentences[0][0]}"
            if len(relevant_sentences) > 1:
                answer += f" Inoltre: {relevant_sentences[1][0]}"
        else:
            answer = "Mi dispiace, non riesco a trovare informazioni specifiche su questa domanda nel documento fornito."
        
        return {
            'answer': answer,
            'citations': [],
            'model_used': 'fallback',
            'tokens_used': 0
        }
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Ottieni riassunto della conversazione"""
        
        if conversation_id not in self.conversations:
            return {'success': False, 'error': 'Conversazione non trovata'}
        
        conversation = self.conversations[conversation_id]
        doc_context = conversation['document_context']
        
        return {
            'success': True,
            'conversation_id': conversation_id,
            'document_title': doc_context['title'],
            'document_author': doc_context['author'],
            'created_at': conversation['created_at'],
            'last_activity': conversation['last_activity'],
            'total_exchanges': len(conversation['history']),
            'recent_topics': [exchange['user_question'][:100] + '...' 
                            for exchange in conversation['history'][-3:]]
        }


# Istanza globale del motore chat
chat_engine = PDFChatEngine()

@pdf_chat_advanced_bp.route('/api/pdf/start-chat', methods=['POST'])
def start_pdf_chat():
    """Inizia una nuova chat con un PDF"""
    
    try:
        data = request.get_json()
        
        if not data or 'document_id' not in data:
            return jsonify({
                'success': False,
                'error': 'document_id richiesto'
            }), 400
        
        document_id = data['document_id']
        
        # Recupera i dati del documento (assumendo che siano memorizzati)
        # In un sistema reale, questi dati verrebbero dal database
        from ..routes.documents_simple import uploaded_documents_store
        
        if document_id not in uploaded_documents_store:
            return jsonify({
                'success': False,
                'error': 'Documento non trovato'
            }), 404
        
        document_data = uploaded_documents_store[document_id]
        
        # Inizia conversazione
        conversation_id = chat_engine.start_conversation(document_id, document_data)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'document_title': document_data.get('title', 'Documento'),
            'document_info': {
                'word_count': document_data.get('word_count', 0),
                'page_count': document_data.get('page_count', 0),
                'chunks_count': len(document_data.get('chunks', [])),
                'file_size_mb': document_data.get('file_size_mb', 0)
            },
            'message': f'Chat iniziata con successo per il documento: {document_data.get("title", "Documento")}'
        })
        
    except Exception as e:
        logger.error(f"Errore start chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore avvio chat: {str(e)}'
        }), 500

@pdf_chat_advanced_bp.route('/api/pdf/chat', methods=['POST'])
def chat_with_pdf():
    """Chat con il PDF"""
    
    try:
        data = request.get_json()
        
        if not data or 'conversation_id' not in data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'conversation_id e question richiesti'
            }), 400
        
        conversation_id = data['conversation_id']
        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Domanda non può essere vuota'
            }), 400
        
        # Esegui chat
        result = chat_engine.chat_with_pdf(conversation_id, question)
        
        if result['success']:
            return jsonify({
                'success': True,
                'answer': result['answer'],
                'citations': result.get('citations', []),
                'relevant_chunks_count': len(result.get('relevant_chunks', [])),
                'document_title': result.get('document_title', ''),
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Errore chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante la chat: {str(e)}'
        }), 500

@pdf_chat_advanced_bp.route('/api/pdf/conversation-summary/<conversation_id>', methods=['GET'])
def get_conversation_summary(conversation_id):
    """Ottieni riassunto conversazione"""
    
    try:
        result = chat_engine.get_conversation_summary(conversation_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Errore summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore recupero summary: {str(e)}'
        }), 500

@pdf_chat_advanced_bp.route('/api/pdf/conversations', methods=['GET'])
def list_conversations():
    """Lista tutte le conversazioni attive"""
    
    try:
        conversations = []
        
        for conv_id, conv_data in chat_engine.conversations.items():
            doc_context = conv_data['document_context']
            conversations.append({
                'conversation_id': conv_id,
                'document_title': doc_context['title'],
                'document_author': doc_context['author'],
                'created_at': conv_data['created_at'],
                'last_activity': conv_data['last_activity'],
                'total_exchanges': len(conv_data['history'])
            })
        
        # Ordina per ultima attività
        conversations.sort(key=lambda x: x['last_activity'], reverse=True)
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'total_conversations': len(conversations)
        })
        
    except Exception as e:
        logger.error(f"Errore list conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore lista conversazioni: {str(e)}'
        }), 500

