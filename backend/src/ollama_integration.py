# -*- coding: utf-8 -*-
"""
Ollama Integration Module
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD

Integrazione con Ollama per LLM locale illimitato
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional, Generator
import time

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Client per interagire con Ollama (LLM locale)
    Supporta: llama3.2, mistral, phi3, etc.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "llama3.2"
        self.timeout = 120  # 2 minuti per generazioni lunghe
        
    def is_available(self) -> bool:
        """Verifica se Ollama è disponibile"""
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """Elenca modelli disponibili"""
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            
            return []
            
        except Exception as e:
            logger.error(f"Errore lista modelli Ollama: {str(e)}")
            return []
    
    def generate(self, 
                 prompt: str, 
                 model: Optional[str] = None,
                 system: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 stream: bool = False) -> Dict[str, Any]:
        """
        Genera testo con Ollama
        
        Args:
            prompt: Prompt utente
            model: Modello da usare (default: llama3.2)
            system: System prompt
            temperature: Temperatura (0-1)
            max_tokens: Massimo numero di token
            stream: Se True, ritorna generator per streaming
        
        Returns:
            Risposta generata o generator se stream=True
        """
        
        try:
            model = model or self.default_model
            
            # Verifica disponibilità
            if not self.is_available():
                raise Exception("Ollama non disponibile. Assicurarsi che sia in esecuzione.")
            
            # Prepara payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature
                }
            }
            
            if system:
                payload["system"] = system
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            # Chiamata API
            if stream:
                return self._generate_stream(payload)
            else:
                return self._generate_complete(payload)
                
        except Exception as e:
            logger.error(f"Errore generazione Ollama: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_complete(self, payload: Dict) -> Dict[str, Any]:
        """Generazione completa (non streaming)"""
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'model': payload['model'],
                    'response': data.get('response', ''),
                    'context': data.get('context', []),
                    'total_duration': data.get('total_duration', 0) / 1e9,  # ns -> s
                    'load_duration': data.get('load_duration', 0) / 1e9,
                    'prompt_eval_count': data.get('prompt_eval_count', 0),
                    'eval_count': data.get('eval_count', 0),
                    'eval_duration': data.get('eval_duration', 0) / 1e9
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Errore generazione completa: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_stream(self, payload: Dict) -> Generator[str, None, None]:
        """Generazione streaming"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get('response'):
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"[ERROR: HTTP {response.status_code}]"
                
        except Exception as e:
            logger.error(f"Errore generazione streaming: {str(e)}")
            yield f"[ERROR: {str(e)}]"
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             temperature: float = 0.7,
             stream: bool = False) -> Dict[str, Any]:
        """
        Chat con Ollama (formato OpenAI-like)
        
        Args:
            messages: Lista di messaggi [{"role": "user/assistant/system", "content": "..."}]
            model: Modello da usare
            temperature: Temperatura
            stream: Streaming
        
        Returns:
            Risposta chat
        """
        
        try:
            model = model or self.default_model
            
            # Verifica disponibilità
            if not self.is_available():
                raise Exception("Ollama non disponibile")
            
            # Prepara payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature
                }
            }
            
            # Chiamata API
            if stream:
                return self._chat_stream(payload)
            else:
                return self._chat_complete(payload)
                
        except Exception as e:
            logger.error(f"Errore chat Ollama: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _chat_complete(self, payload: Dict) -> Dict[str, Any]:
        """Chat completa (non streaming)"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'model': payload['model'],
                    'message': data.get('message', {}),
                    'response': data.get('message', {}).get('content', ''),
                    'total_duration': data.get('total_duration', 0) / 1e9,
                    'prompt_eval_count': data.get('prompt_eval_count', 0),
                    'eval_count': data.get('eval_count', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Errore chat completa: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _chat_stream(self, payload: Dict) -> Generator[str, None, None]:
        """Chat streaming"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            message = data.get('message', {})
                            if message.get('content'):
                                yield message['content']
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"[ERROR: HTTP {response.status_code}]"
                
        except Exception as e:
            logger.error(f"Errore chat streaming: {str(e)}")
            yield f"[ERROR: {str(e)}]"
    
    def embed(self, text: str, model: Optional[str] = None) -> Optional[List[float]]:
        """
        Genera embedding per un testo
        
        Args:
            text: Testo da embeddare
            model: Modello embedding (default: llama3.2)
        
        Returns:
            Vettore embedding o None se errore
        """
        
        try:
            model = model or self.default_model
            
            payload = {
                "model": model,
                "prompt": text
            }
            
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('embedding')
            
            return None
            
        except Exception as e:
            logger.error(f"Errore embedding Ollama: {str(e)}")
            return None
    
    def pull_model(self, model: str) -> bool:
        """
        Scarica un modello da Ollama library
        
        Args:
            model: Nome modello (es. "llama3.2", "mistral")
        
        Returns:
            True se successo
        """
        
        try:
            logger.info(f"📥 Download modello {model}...")
            
            payload = {
                "name": model
            }
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                stream=True,
                timeout=600  # 10 minuti per download
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            status = data.get('status', '')
                            if status:
                                logger.info(f"  {status}")
                        except:
                            continue
                
                logger.info(f"✅ Modello {model} scaricato")
                return True
            else:
                logger.error(f"❌ Errore download: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Errore pull modello: {str(e)}")
            return False


# Istanza globale
ollama_client = OllamaClient()


def generate_with_ollama(prompt: str, **kwargs) -> Dict[str, Any]:
    """Funzione wrapper per compatibilità"""
    return ollama_client.generate(prompt, **kwargs)


def chat_with_ollama(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Funzione wrapper per chat"""
    return ollama_client.chat(messages, **kwargs)


def is_ollama_available() -> bool:
    """Verifica disponibilità Ollama"""
    return ollama_client.is_available()
