# -*- coding: utf-8 -*-
"""
Predictive Trend AI Module
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD

Sistema di analisi predittiva e trend detection per monitorare evoluzione AI competitors
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class PredictiveTrendAI:
    """
    Sistema pionieristico che monitora l'evoluzione dei competitor AI
    e predice trend futuri per mantenere il Moteur sempre all'avanguardia
    """
    
    def __init__(self):
        self.data_dir = "/tmp/trend_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Competitor da monitorare
        self.competitors = {
            'perplexity': {
                'name': 'Perplexity AI',
                'blog_url': 'https://www.perplexity.ai/hub/blog',
                'features_url': 'https://www.perplexity.ai/hub/getting-started',
                'priority': 10
            },
            'anthropic': {
                'name': 'Anthropic (Claude)',
                'blog_url': 'https://www.anthropic.com/news',
                'features_url': 'https://www.anthropic.com/claude',
                'priority': 10
            },
            'openai': {
                'name': 'OpenAI',
                'blog_url': 'https://openai.com/blog',
                'features_url': 'https://platform.openai.com/docs',
                'priority': 9
            },
            'manus': {
                'name': 'Manus AI',
                'blog_url': 'https://manus.im/blog',
                'features_url': 'https://manus.im/docs',
                'priority': 9
            }
        }
        
        self.last_scan = None
        self.scan_interval = timedelta(days=7)  # Scan settimanale
        
    def scan_competitors(self, force: bool = False) -> Dict[str, Any]:
        """
        Scansiona tutti i competitor per nuove funzionalità
        
        Args:
            force: Forza scan anche se recente
        
        Returns:
            Report con novità trovate
        """
        
        try:
            # Verifica se scan recente
            if not force and self.last_scan:
                if datetime.now() - self.last_scan < self.scan_interval:
                    logger.info("Scan recente, skip")
                    return self._load_last_report()
            
            logger.info("🔍 Avvio scan competitor AI...")
            
            all_findings = []
            scan_stats = {
                'competitors_scanned': 0,
                'competitors_succeeded': 0,
                'new_features_found': 0,
                'scan_time': 0
            }
            
            import time
            start_time = time.time()
            
            # Scansiona ogni competitor
            for comp_id, comp_config in self.competitors.items():
                try:
                    logger.info(f"Scanning {comp_config['name']}...")
                    
                    findings = self._scan_competitor(comp_id, comp_config)
                    
                    if findings:
                        all_findings.extend(findings)
                        scan_stats['new_features_found'] += len(findings)
                        scan_stats['competitors_succeeded'] += 1
                    
                    scan_stats['competitors_scanned'] += 1
                    
                except Exception as e:
                    logger.error(f"Errore scan {comp_id}: {str(e)}")
            
            scan_stats['scan_time'] = time.time() - start_time
            
            # Analizza findings con LLM
            analyzed_findings = self._analyze_findings_with_llm(all_findings)
            
            # Genera suggerimenti proattivi
            suggestions = self._generate_proactive_suggestions(analyzed_findings)
            
            # Prepara report
            report = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'stats': scan_stats,
                'findings': analyzed_findings,
                'suggestions': suggestions,
                'next_scan': (datetime.now() + self.scan_interval).isoformat()
            }
            
            # Salva report
            self._save_report(report)
            self.last_scan = datetime.now()
            
            logger.info(f"✅ Scan completato: {scan_stats['new_features_found']} novità trovate")
            
            return report
            
        except Exception as e:
            logger.error(f"Errore scan competitors: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _scan_competitor(self, comp_id: str, config: Dict) -> List[Dict]:
        """Scansiona un singolo competitor"""
        
        findings = []
        
        try:
            # Scansiona blog per annunci
            blog_findings = self._scan_blog(config['blog_url'], config['name'])
            findings.extend(blog_findings)
            
            # Scansiona pagina features
            feature_findings = self._scan_features(config['features_url'], config['name'])
            findings.extend(feature_findings)
            
            return findings
            
        except Exception as e:
            logger.error(f"Errore scan {comp_id}: {str(e)}")
            return []
    
    def _scan_blog(self, url: str, competitor_name: str) -> List[Dict]:
        """Scansiona blog per annunci recenti"""
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            findings = []
            
            # Cerca titoli di articoli recenti
            # (Questa è una implementazione generica, andrebbe personalizzata per ogni sito)
            titles = soup.find_all(['h1', 'h2', 'h3'], limit=10)
            
            for title in titles:
                text = title.get_text().strip()
                
                # Filtra per keyword rilevanti
                if self._is_relevant_announcement(text):
                    finding = {
                        'source': competitor_name,
                        'type': 'blog_post',
                        'title': text,
                        'url': url,
                        'timestamp': datetime.now().isoformat(),
                        'relevance': 'high' if self._is_high_priority(text) else 'medium'
                    }
                    findings.append(finding)
            
            return findings
            
        except Exception as e:
            logger.error(f"Errore scan blog {url}: {str(e)}")
            return []
    
    def _scan_features(self, url: str, competitor_name: str) -> List[Dict]:
        """Scansiona pagina features"""
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            findings = []
            
            # Cerca descrizioni di features
            paragraphs = soup.find_all('p', limit=20)
            
            for p in paragraphs:
                text = p.get_text().strip()
                
                if self._is_relevant_feature(text):
                    finding = {
                        'source': competitor_name,
                        'type': 'feature',
                        'description': text[:200],  # Prime 200 char
                        'url': url,
                        'timestamp': datetime.now().isoformat(),
                        'relevance': 'medium'
                    }
                    findings.append(finding)
            
            return findings
            
        except Exception as e:
            logger.error(f"Errore scan features {url}: {str(e)}")
            return []
    
    def _is_relevant_announcement(self, text: str) -> bool:
        """Verifica se annuncio è rilevante"""
        
        keywords = [
            'introducing', 'new', 'launch', 'release', 'feature',
            'capability', 'model', 'update', 'improvement',
            'research', 'reasoning', 'search', 'agent'
        ]
        
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_relevant_feature(self, text: str) -> bool:
        """Verifica se feature è rilevante"""
        
        keywords = [
            'search', 'research', 'reasoning', 'agent', 'autonomous',
            'citation', 'source', 'academic', 'analysis', 'thinking',
            'multi-modal', 'integration', 'api', 'model'
        ]
        
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in keywords) and len(text) > 50
    
    def _is_high_priority(self, text: str) -> bool:
        """Verifica se è alta priorità"""
        
        high_priority_keywords = [
            'breakthrough', 'revolutionary', 'first', 'pioneering',
            'state-of-the-art', 'advanced', 'deep research', 'reasoning'
        ]
        
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in high_priority_keywords)
    
    def _analyze_findings_with_llm(self, findings: List[Dict]) -> List[Dict]:
        """Analizza findings con LLM per estrarre insights"""
        
        if not findings:
            return []
        
        try:
            # Usa Ollama se disponibile, altrimenti skip analisi LLM
            from ollama_integration import ollama_client
            
            if not ollama_client.is_available():
                logger.warning("Ollama non disponibile, skip analisi LLM")
                return findings
            
            # Prepara prompt per analisi
            findings_text = "\n\n".join([
                f"- {f['source']}: {f.get('title') or f.get('description', '')}"
                for f in findings[:10]  # Analizza top 10
            ])
            
            prompt = f"""Analizza questi annunci recenti di competitor AI e identifica:
1. Nuove capacità tecniche
2. Trend emergenti
3. Funzionalità innovative
4. Potenziali minacce competitive

Annunci:
{findings_text}

Fornisci analisi concisa e strutturata."""
            
            response = ollama_client.generate(
                prompt=prompt,
                system="Sei un analista di competitive intelligence specializzato in AI.",
                temperature=0.3
            )
            
            if response.get('success'):
                # Aggiungi analisi LLM ai findings
                for finding in findings:
                    finding['llm_analysis'] = response.get('response', '')[:500]
            
            return findings
            
        except Exception as e:
            logger.error(f"Errore analisi LLM: {str(e)}")
            return findings
    
    def _generate_proactive_suggestions(self, findings: List[Dict]) -> List[Dict]:
        """Genera suggerimenti proattivi basati sui findings"""
        
        suggestions = []
        
        # Analizza pattern nei findings
        feature_keywords = {}
        
        for finding in findings:
            text = (finding.get('title', '') + ' ' + finding.get('description', '')).lower()
            
            # Conta keyword
            for keyword in ['reasoning', 'search', 'citation', 'agent', 'autonomous', 'multi-modal']:
                if keyword in text:
                    feature_keywords[keyword] = feature_keywords.get(keyword, 0) + 1
        
        # Genera suggerimenti basati su trend
        for keyword, count in sorted(feature_keywords.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:  # Se keyword appare almeno 2 volte
                suggestion = self._generate_suggestion_for_keyword(keyword, count)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_suggestion_for_keyword(self, keyword: str, count: int) -> Optional[Dict]:
        """Genera suggerimento specifico per keyword"""
        
        suggestions_map = {
            'reasoning': {
                'title': 'Potenziare Extended Reasoning',
                'description': f'Rilevato {count} annunci su "reasoning". Suggerisco di implementare/migliorare capacità di reasoning visibile con chain-of-thought.',
                'priority': 'high',
                'action': 'implement_extended_reasoning'
            },
            'search': {
                'title': 'Espandere Capacità di Ricerca',
                'description': f'Rilevato {count} annunci su "search". Suggerisco di aggiungere nuovi motori di ricerca o migliorare algoritmi di ranking.',
                'priority': 'medium',
                'action': 'expand_search_engines'
            },
            'citation': {
                'title': 'Migliorare Sistema Citazioni',
                'description': f'Rilevato {count} annunci su "citation". Suggerisco di implementare citazioni automatiche più precise e verificabili.',
                'priority': 'medium',
                'action': 'improve_citations'
            },
            'agent': {
                'title': 'Potenziare Agente Autonomo',
                'description': f'Rilevato {count} annunci su "agent". Suggerisco di espandere capacità autonome e task planning.',
                'priority': 'high',
                'action': 'enhance_autonomous_agent'
            },
            'multi-modal': {
                'title': 'Integrare Capacità Multi-Modali',
                'description': f'Rilevato {count} annunci su "multi-modal". Suggerisco di aggiungere supporto per immagini, audio, video.',
                'priority': 'medium',
                'action': 'add_multimodal_support'
            }
        }
        
        return suggestions_map.get(keyword)
    
    def _save_report(self, report: Dict):
        """Salva report su disco"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trend_report_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # Salva anche come "latest"
            latest_path = os.path.join(self.data_dir, "latest_report.json")
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Report salvato: {filepath}")
            
        except Exception as e:
            logger.error(f"Errore salvataggio report: {str(e)}")
    
    def _load_last_report(self) -> Dict:
        """Carica ultimo report salvato"""
        
        try:
            latest_path = os.path.join(self.data_dir, "latest_report.json")
            
            if os.path.exists(latest_path):
                with open(latest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return {'success': False, 'error': 'No previous report found'}
            
        except Exception as e:
            logger.error(f"Errore caricamento report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_latest_trends(self) -> Dict[str, Any]:
        """Ottieni ultimi trend rilevati"""
        
        return self._load_last_report()
    
    def should_update_competencies(self) -> bool:
        """Verifica se è necessario aggiornare competenze"""
        
        if not self.last_scan:
            return True
        
        days_since_scan = (datetime.now() - self.last_scan).days
        
        return days_since_scan >= 7  # Aggiorna ogni settimana


# Istanza globale
predictive_ai = PredictiveTrendAI()


def scan_ai_competitors(force: bool = False) -> Dict[str, Any]:
    """Funzione wrapper per scan competitor"""
    return predictive_ai.scan_competitors(force=force)


def get_latest_ai_trends() -> Dict[str, Any]:
    """Funzione wrapper per ultimi trend"""
    return predictive_ai.get_latest_trends()


def should_update_competencies() -> bool:
    """Funzione wrapper per verifica aggiornamento"""
    return predictive_ai.should_update_competencies()
