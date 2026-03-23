# -*- coding: utf-8 -*-
"""
Advanced Features Routes
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD

API routes per funzionalità avanzate v4.0
"""

from flask import Blueprint, request, jsonify
import logging
import sys
import os

# Aggiungi path per import moduli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_source_search import search_engine
from ollama_integration import ollama_client, is_ollama_available
from dual_mode_controller import dual_mode
from predictive_trend_ai import predictive_ai
from dialectical_engine import dialectical_engine
from deep_synthesis_engine import deep_synthesis_engine
from incarnation_engine import incarnation_engine
from concept_collider import concept_collider
from quill_engine import quill_engine
from self_tuning_engine import self_tuning_engine

logger = logging.getLogger(__name__)

# Blueprint
advanced_bp = Blueprint('advanced', __name__, url_prefix='/api/advanced')


@advanced_bp.route('/search/multi-source', methods=['POST'])
def multi_source_search():
    """
    Ricerca multi-fonte avanzata
    
    POST /api/advanced/search/multi-source
    Body: {
        "query": "Sistema Preventivo Don Bosco",
        "filters": {
            "year_from": 2020,
            "type": "academic"
        }
    }
    """
    
    try:
        data = request.get_json()
        
        query = data.get('query')
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query richiesta'
            }), 400
        
        # Esegui ricerca
        results = search_engine.search(query, filters)
        
        # Analyse dialectique si un "claim" est fourni
        claim = data.get('claim')
        if claim and results.get('success') and results.get('results'):
            logger.info(f"Application de l'analyse dialectique pour le claim: {claim}")
            dialectical_analysis = dialectical_engine.analyze_results(claim, results['results'])
            results['dialectical_analysis'] = dialectical_analysis
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Errore multi-source search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/storm/outline', methods=['POST'])
def storm_outline():
    """Génère un plan détaillé (STORM-like)"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        discipline = data.get('discipline', 'Général')
        audience = data.get('audience', 'Académique')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
            
        outline = deep_synthesis_engine.generate_outline(topic, discipline, audience)
        return jsonify({'success': True, 'outline': outline})
    except Exception as e:
        logger.error(f"Erreur storm_outline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/storm/critique', methods=['POST'])
def storm_critique():
    """Jury Socratique: Critique experte d'un texte"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        experts = data.get('experts', ['Économiste', 'Théologien'])
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
            
        critique_results = deep_synthesis_engine.expert_critique(text, experts)
        return jsonify({'success': True, 'results': critique_results})
    except Exception as e:
        logger.error(f"Erreur storm_critique: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/incarnation/invoke', methods=['POST'])
def incarnation_invoke():
    """Invoque des esprits historiques pour débattre d'un texte"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        spirits = data.get('spirits', ['don_bosco', 'hannah_arendt'])
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
            
        result = incarnation_engine.invoke_spirits(text, spirits)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Erreur incarnation_invoke: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/collider/collide', methods=['POST'])
def collider_collide():
    """Fracasse deux concepts pour créer un néologisme"""
    try:
        data = request.get_json()
        concept_a = data.get('concept_a', '')
        concept_b = data.get('concept_b', '')
        
        if not concept_a or not concept_b:
            return jsonify({'success': False, 'error': 'Two concepts are required'}), 400
            
        result = concept_collider.collide(concept_a, concept_b)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Erreur collider_collide: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/quill/authors', methods=['GET'])
def quill_authors():
    """Retourne la liste des auteurs disponibles pour le Quill Engine"""
    try:
        domain = request.args.get('domain', 'all')
        authors = quill_engine.get_recommended_authors(domain)
        return jsonify({'success': True, 'authors': authors})
    except Exception as e:
        logger.error(f"Erreur quill_authors: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/quill/rewrite', methods=['POST'])
def quill_rewrite():
    """Réécrit un texte avec le style d'un auteur (Règle 60/40)"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        author_id = data.get('author_id', '')
        
        if not text or not author_id:
            return jsonify({'success': False, 'error': 'Text and author_id are required'}), 400
            
        result = quill_engine.rewrite_with_quill(text, author_id)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Erreur quill_rewrite: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/tuning/train', methods=['POST'])
def tuning_train():
    """Entraîne l'IA sur le style de l'utilisateur"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or len(text) < 50:
            return jsonify({'success': False, 'error': 'Text is too short for training (min 50 chars)'}), 400
            
        result = self_tuning_engine.train_on_text(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur tuning_train: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/ollama/status', methods=['GET'])
def ollama_status():
    """
    Verifica stato Ollama
    
    GET /api/advanced/ollama/status
    """
    
    try:
        is_available = ollama_client.is_available()
        models = ollama_client.list_models() if is_available else []
        
        return jsonify({
            'success': True,
            'available': is_available,
            'models': models,
            'default_model': ollama_client.default_model
        })
        
    except Exception as e:
        logger.error(f"Errore ollama status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/ollama/generate', methods=['POST'])
def ollama_generate():
    """
    Genera testo con Ollama
    
    POST /api/advanced/ollama/generate
    Body: {
        "prompt": "Scrivi una meditazione salesiana...",
        "model": "llama3.2",
        "system": "Sei un esperto salesiano",
        "temperature": 0.7
    }
    """
    
    try:
        data = request.get_json()
        
        prompt = data.get('prompt')
        model = data.get('model')
        system = data.get('system')
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt richiesto'
            }), 400
        
        # Genera con Ollama
        result = ollama_client.generate(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore ollama generate: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/ollama/chat', methods=['POST'])
def ollama_chat():
    """
    Chat con Ollama
    
    POST /api/advanced/ollama/chat
    Body: {
        "messages": [
            {"role": "user", "content": "Ciao!"},
            {"role": "assistant", "content": "Ciao! Come posso aiutarti?"},
            {"role": "user", "content": "Parlami di Don Bosco"}
        ],
        "model": "llama3.2",
        "temperature": 0.7
    }
    """
    
    try:
        data = request.get_json()
        
        messages = data.get('messages', [])
        model = data.get('model')
        temperature = data.get('temperature', 0.7)
        
        if not messages:
            return jsonify({
                'success': False,
                'error': 'Messages richiesti'
            }), 400
        
        # Chat con Ollama
        result = ollama_client.chat(
            messages=messages,
            model=model,
            temperature=temperature
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore ollama chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/mode/status', methods=['GET'])
def mode_status():
    """
    Stato modalità corrente (Online/Offline)
    
    GET /api/advanced/mode/status
    """
    
    try:
        stats = dual_mode.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Errore mode status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/mode/detect', methods=['POST'])
def mode_detect():
    """
    Forza rilevamento modalità
    
    POST /api/advanced/mode/detect
    Body: {
        "force_check": true
    }
    """
    
    try:
        data = request.get_json() or {}
        force_check = data.get('force_check', False)
        
        mode = dual_mode.detect_mode(force_check=force_check)
        suggestion = dual_mode.suggest_online_action()
        
        return jsonify({
            'success': True,
            'mode': mode,
            'suggestion': suggestion
        })
        
    except Exception as e:
        logger.error(f"Errore mode detect: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/trends/scan', methods=['POST'])
def trends_scan():
    """
    Scansiona competitor AI per trend
    
    POST /api/advanced/trends/scan
    Body: {
        "force": false
    }
    """
    
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        
        # Verifica se online
        if not dual_mode.is_online():
            return jsonify({
                'success': False,
                'error': 'Funzione disponibile solo in modalità online'
            }), 400
        
        # Scansiona competitor
        report = predictive_ai.scan_competitors(force=force)
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Errore trends scan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/trends/latest', methods=['GET'])
def trends_latest():
    """
    Ottieni ultimi trend rilevati
    
    GET /api/advanced/trends/latest
    """
    
    try:
        trends = predictive_ai.get_latest_trends()
        
        return jsonify(trends)
        
    except Exception as e:
        logger.error(f"Errore trends latest: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/health', methods=['GET'])
def health():
    """
    Health check per funzionalità avanzate
    
    GET /api/advanced/health
    """
    
    try:
        # Verifica tutti i moduli
        health_status = {
            'success': True,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'modules': {
                'multi_source_search': {
                    'available': True,
                    'engines_count': len(search_engine.search_engines)
                },
                'ollama': {
                    'available': ollama_client.is_available(),
                    'models': ollama_client.list_models() if ollama_client.is_available() else []
                },
                'dual_mode': {
                    'available': True,
                    'current_mode': dual_mode.detect_mode()
                },
                'predictive_ai': {
                    'available': True,
                    'should_update': predictive_ai.should_update_competencies()
                }
            }
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Errore health check: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@advanced_bp.route('/unified-search', methods=['POST'])
def unified_search():
    """
    Ricerca unificata intelligente che combina:
    - Multi-source search
    - Corpus salesiano
    - LLM per sintesi
    
    POST /api/advanced/unified-search
    Body: {
        "query": "Sistema Preventivo educazione digitale",
        "use_llm_synthesis": true,
        "max_results": 20
    }
    """
    
    try:
        data = request.get_json()
        
        query = data.get('query')
        use_llm = data.get('use_llm_synthesis', True)
        max_results = data.get('max_results', 20)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query richiesta'
            }), 400
        
        # Step 1: Ricerca multi-fonte
        search_results = search_engine.search(query, {})
        
        if not search_results.get('success'):
            return jsonify(search_results), 500
        
        results = search_results.get('results', [])[:max_results]
        
        # Step 2: Sintesi con LLM (se richiesto e disponibile)
        synthesis = None
        
        if use_llm and results:
            # Prepara contesto per LLM
            context = "\n\n".join([
                f"[{i+1}] {r.get('title', '')} ({r.get('source', '')})\n{r.get('abstract', '')[:200]}"
                for i, r in enumerate(results[:5])
            ])
            
            prompt = f"""Basandoti su questi risultati di ricerca, fornisci una sintesi concisa e informativa sulla query: "{query}"

Risultati:
{context}

Fornisci una sintesi strutturata con:
1. Risposta diretta alla query
2. Punti chiave emersi
3. Citazioni rilevanti"""
            
            # Usa Ollama se disponibile
            if ollama_client.is_available():
                llm_result = ollama_client.generate(
                    prompt=prompt,
                    system="Sei un assistente di ricerca salesiano esperto.",
                    temperature=0.5
                )
                
                if llm_result.get('success'):
                    synthesis = llm_result.get('response', '')
        
        # Risposta unificata
        return jsonify({
            'success': True,
            'query': query,
            'mode': dual_mode.detect_mode(),
            'results': results,
            'synthesis': synthesis,
            'stats': search_results.get('stats', {})
        })
        
    except Exception as e:
        logger.error(f"Errore unified search: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
