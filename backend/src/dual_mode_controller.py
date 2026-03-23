# -*- coding: utf-8 -*-
"""
Dual-Mode Controller
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD

Gestisce la modalità duale: Online (ricerca avanzata + cloud LLM) vs Offline (LLM locale)
"""

import logging
import requests
from typing import Dict, Any, Optional
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DualModeController:
    """
    Controller che gestisce la modalità operativa del sistema:
    - ONLINE: Ricerca web + LLM cloud (GPT-4/Claude) + Competitive intelligence
    - OFFLINE: LLM locale (Ollama) + Corpus salesiano locale
    
    Auto-detect connessione e switching intelligente
    """
    
    def __init__(self):
        self.current_mode = None
        self.last_check = None
        self.check_interval = timedelta(minutes=5)
        
        # Configurazione
        self.test_urls = [
            "https://www.google.com",
            "https://api.openai.com",
            "https://www.wikipedia.org"
        ]
        
        self.force_mode = os.getenv('FORCE_MODE')  # 'online' o 'offline' per testing
        
        # Statistiche
        self.stats = {
            'online_requests': 0,
            'offline_requests': 0,
            'mode_switches': 0,
            'last_online': None,
            'last_offline': None
        }
    
    def detect_mode(self, force_check: bool = False) -> str:
        """
        Rileva modalità operativa corrente
        
        Args:
            force_check: Forza controllo anche se recente
        
        Returns:
            'online' o 'offline'
        """
        
        try:
            # Se modalità forzata (per testing)
            if self.force_mode:
                return self.force_mode
            
            # Se check recente, usa cache
            if not force_check and self.last_check:
                if datetime.now() - self.last_check < self.check_interval:
                    return self.current_mode
            
            # Test connessione
            is_online = self._test_connectivity()
            
            new_mode = 'online' if is_online else 'offline'
            
            # Aggiorna stato
            if new_mode != self.current_mode:
                self._on_mode_change(self.current_mode, new_mode)
            
            self.current_mode = new_mode
            self.last_check = datetime.now()
            
            return self.current_mode
            
        except Exception as e:
            logger.error(f"Errore detect mode: {str(e)}")
            # In caso di errore, assume offline per sicurezza
            return 'offline'
    
    def _test_connectivity(self) -> bool:
        """Test connessione internet"""
        
        try:
            # Prova a connettersi a più URL
            for url in self.test_urls:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Errore test connettività: {str(e)}")
            return False
    
    def _on_mode_change(self, old_mode: Optional[str], new_mode: str):
        """Callback quando cambia modalità"""
        
        self.stats['mode_switches'] += 1
        
        if new_mode == 'online':
            self.stats['last_online'] = datetime.now().isoformat()
            logger.info("🌐 MODALITÀ ONLINE ATTIVATA - Ricerca web e LLM cloud disponibili")
        else:
            self.stats['last_offline'] = datetime.now().isoformat()
            logger.info("💻 MODALITÀ OFFLINE ATTIVATA - LLM locale e corpus salesiano")
    
    def is_online(self) -> bool:
        """Verifica se sistema è online"""
        return self.detect_mode() == 'online'
    
    def is_offline(self) -> bool:
        """Verifica se sistema è offline"""
        return self.detect_mode() == 'offline'
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Ritorna configurazione LLM appropriata per modalità corrente
        
        Returns:
            Configurazione LLM
        """
        
        mode = self.detect_mode()
        
        if mode == 'online':
            # Modalità online: usa LLM cloud (GPT-4 o Claude)
            config = {
                'mode': 'online',
                'provider': 'openai',  # o 'anthropic'
                'model': 'gpt-4',
                'use_web_search': True,
                'use_academic_search': True,
                'use_competitive_intel': True,
                'fallback_to_local': True  # Se cloud fallisce, usa locale
            }
        else:
            # Modalità offline: usa Ollama locale
            config = {
                'mode': 'offline',
                'provider': 'ollama',
                'model': 'llama3.2',
                'use_web_search': False,
                'use_academic_search': False,
                'use_local_corpus': True,  # Usa corpus salesiano locale
                'unlimited': True  # Nessun limite di utilizzo
            }
        
        return config
    
    def get_search_config(self) -> Dict[str, Any]:
        """
        Ritorna configurazione ricerca appropriata per modalità corrente
        
        Returns:
            Configurazione ricerca
        """
        
        mode = self.detect_mode()
        
        if mode == 'online':
            config = {
                'mode': 'online',
                'engines': [
                    'google_scholar',
                    'semantic_scholar',
                    'arxiv',
                    'pubmed',
                    'openalex',
                    'crossref',
                    'wikipedia',
                    'corpus_salesiano'
                ],
                'max_engines': 12,
                'use_cache': True,
                'cache_duration_days': 7
            }
        else:
            config = {
                'mode': 'offline',
                'engines': [
                    'corpus_salesiano'  # Solo corpus locale
                ],
                'use_cache': True,
                'cache_duration_days': 30  # Cache più lunga offline
            }
        
        return config
    
    def suggest_online_action(self) -> Optional[str]:
        """
        Suggerisce azione da fare quando torna online
        
        Returns:
            Messaggio suggerimento o None
        """
        
        if not self.is_online():
            return None
        
        # Verifica se è passato molto tempo dall'ultimo aggiornamento
        last_online = self.stats.get('last_online')
        
        if last_online:
            last_online_dt = datetime.fromisoformat(last_online)
            days_offline = (datetime.now() - last_online_dt).days
            
            if days_offline > 7:
                return (
                    f"⚠️ Sistema offline da {days_offline} giorni. "
                    "Suggerisco di eseguire aggiornamento competenze: "
                    "1) Ricerca novità AI competitors, "
                    "2) Aggiornamento corpus salesiano, "
                    "3) Cache ricerche recenti."
                )
        
        return None
    
    def track_request(self, request_type: str):
        """Traccia richiesta per statistiche"""
        
        mode = self.detect_mode()
        
        if mode == 'online':
            self.stats['online_requests'] += 1
        else:
            self.stats['offline_requests'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche utilizzo"""
        
        return {
            'current_mode': self.current_mode,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'stats': self.stats,
            'llm_config': self.get_llm_config(),
            'search_config': self.get_search_config()
        }
    
    def set_mode(self, mode: str):
        """
        Forza modalità (per testing/debugging)
        
        Args:
            mode: 'online' o 'offline'
        """
        
        if mode not in ['online', 'offline']:
            raise ValueError("Mode must be 'online' or 'offline'")
        
        old_mode = self.current_mode
        self.current_mode = mode
        self.force_mode = mode
        
        if old_mode != mode:
            self._on_mode_change(old_mode, mode)
        
        logger.info(f"Modalità forzata: {mode}")


# Istanza globale
dual_mode = DualModeController()


def get_current_mode() -> str:
    """Funzione wrapper per ottenere modalità corrente"""
    return dual_mode.detect_mode()


def is_online() -> bool:
    """Funzione wrapper per verificare se online"""
    return dual_mode.is_online()


def is_offline() -> bool:
    """Funzione wrapper per verificare se offline"""
    return dual_mode.is_offline()


def get_llm_config() -> Dict[str, Any]:
    """Funzione wrapper per configurazione LLM"""
    return dual_mode.get_llm_config()


def get_search_config() -> Dict[str, Any]:
    """Funzione wrapper per configurazione ricerca"""
    return dual_mode.get_search_config()
