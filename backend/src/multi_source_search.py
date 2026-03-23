# -*- coding: utf-8 -*-
"""
Multi-Source Deep Search Engine
Moteur de Rédaction Magique v4.0
Rev. Alphonse Owoudou, PhD

Ricerca federata su 12+ motori accademici + web + corpus salesiano
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from src.insight_engine import insight_engine

logger = logging.getLogger(__name__)

class MultiSourceSearchEngine:
    """
    Motore di ricerca avanzato che interroga simultaneamente:
    - 12+ motori di ricerca accademici
    - Motori web generalisti
    - Corpus salesiano locale
    
    Con caching intelligente e de-duplicazione
    """
    
    def __init__(self):
        self.cache_dir = "/tmp/search_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.cache_duration = timedelta(days=7)  # Cache valida per 7 giorni
        
        # Configurazione motori di ricerca
        self.search_engines = {
            # Motori Accademici
            'salesian_online': {
                'name': 'Salesian.online',
                'enabled': True,
                'priority': 100,  # Massima priorità assoluta
                'type': 'salesian',
                'base_url': 'https://www.salesian.online'
            },
            'sdb_org': {
                'name': 'SDB.org',
                'enabled': True,
                'priority': 100,
                'type': 'salesian',
                'base_url': 'https://www.sdb.org'
            },
            'donboscosanto': {
                'name': 'DonBoscoSanto.eu',
                'enabled': True,
                'priority': 95,
                'type': 'salesian',
                'base_url': 'https://www.donboscosanto.eu'
            },
            'uqac_classiques': {
                'name': 'Classiques des Sciences Sociales (UQAC)',
                'enabled': True,
                'priority': 90,
                'type': 'academic_source',
                'base_url': 'http://classiques.uqac.ca'
            },
            'theses_fr': {
                'name': 'Thèses.fr (Doctorats)',
                'enabled': True,
                'priority': 85,
                'type': 'academic_thesis',
                'base_url': 'https://www.theses.fr'
            },
            'vatican': {
                'name': 'Vatican.va',
                'enabled': True,
                'priority': 95,
                'type': 'institutional',
                'base_url': 'https://www.vatican.va'
            },
            'sep': {
                'name': 'Stanford Encyclopedia of Philosophy',
                'enabled': True,
                'priority': 90,
                'type': 'academic_source',
                'base_url': 'https://plato.stanford.edu'
            },
            'cairn': {
                'name': 'Cairn.info',
                'enabled': True,
                'priority': 85,
                'type': 'academic_source',
                'base_url': 'https://www.cairn.info'
            },
            'persee': {
                'name': 'Persée',
                'enabled': True,
                'priority': 85,
                'type': 'academic_source',
                'base_url': 'https://www.persee.fr'
            },
            'openedition': {
                'name': 'OpenEdition',
                'enabled': True,
                'priority': 85,
                'type': 'academic_source',
                'base_url': 'https://www.openedition.org'
            },
            'gallica': {
                'name': 'Gallica (BnF)',
                'enabled': True,
                'priority': 80,
                'type': 'archive',
                'base_url': 'https://gallica.bnf.fr'
            },
            'gutenberg': {
                'name': 'Project Gutenberg',
                'enabled': True,
                'priority': 75,
                'type': 'archive',
                'base_url': 'https://www.gutenberg.org'
            },
            'google_scholar': {
                'name': 'Google Scholar',
                'enabled': True,
                'priority': 10,
                'type': 'academic'
            },
            'semantic_scholar': {
                'name': 'Semantic Scholar',
                'enabled': True,
                'priority': 9,
                'type': 'academic',
                'api_url': 'https://api.semanticscholar.org/graph/v1/paper/search'
            },
            'arxiv': {
                'name': 'arXiv',
                'enabled': True,
                'priority': 8,
                'type': 'academic',
                'api_url': 'http://export.arxiv.org/api/query'
            },
            'pubmed': {
                'name': 'PubMed',
                'enabled': True,
                'priority': 8,
                'type': 'academic',
                'api_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
            },
            'core': {
                'name': 'CORE',
                'enabled': True,
                'priority': 7,
                'type': 'academic',
                'api_url': 'https://api.core.ac.uk/v3/search/works'
            },
            'crossref': {
                'name': 'Crossref',
                'enabled': True,
                'priority': 7,
                'type': 'academic',
                'api_url': 'https://api.crossref.org/works'
            },
            'base': {
                'name': 'BASE (Bielefeld)',
                'enabled': True,
                'priority': 6,
                'type': 'academic'
            },
            'doaj': {
                'name': 'DOAJ',
                'enabled': True,
                'priority': 6,
                'type': 'academic'
            },
            'openalex': {
                'name': 'OpenAlex',
                'enabled': True,
                'priority': 8,
                'type': 'academic',
                'api_url': 'https://api.openalex.org/works'
            },
            
            # Motori Web Generalisti
            'duckduckgo': {
                'name': 'DuckDuckGo',
                'enabled': True,
                'priority': 5,
                'type': 'web'
            },
            'wikipedia': {
                'name': 'Wikipedia',
                'enabled': True,
                'priority': 4,
                'type': 'web',
                'api_url': 'https://en.wikipedia.org/w/api.php'
            }
        }
        
        self.max_results_per_engine = 10
        self.timeout = 10  # secondi
        
    def search(self, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ricerca federata INTELLIGENTE (Perplexity-style)
        
        Fasi:
        1. Intent Detection & Query Expansion (crea 3 sotto-query mirate)
        2. Ricerca Parallela Espansa
        3. Filtro Semantico "Curatore" (scarta fuori tema)
        4. Categorizzazione Automatica (Fonti, Studi, Web)
        5. Ranking Contestuale
        """
        try:
            logger.info(f"🧠 Avvio ricerca INTELLIGENTE per: {query}")
            
            # 0. Cache Key Generation
            cache_key = hashlib.md5(f"{query}_{json.dumps(filters, sort_keys=True)}".encode()).hexdigest()
            
            # 1. QUERY EXPANSION
            # Invece di cercare solo "Don Bosco", cerchiamo anche termini correlati specifici
            expanded_queries = [query]
            if "bosco" in query.lower():
                expanded_queries.append(f"{query} educational system")
                expanded_queries.append(f"{query} salesian history")
                expanded_queries.append(f"{query} preventivo")
            
            logger.info(f"🚀 Query espansa: {expanded_queries}")

            # Ricerca parallela su tutti i motori PER OGNI QUERY
            all_results = []
            search_stats = {
                'engines_queried': 0,
                'engines_succeeded': 0,
                'engines_failed': 0,
                'total_results': 0,
                'search_time': 0
            }
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                # Lancia ricerche per ogni variante della query
                for q in expanded_queries:
                    for engine_id, engine_config in self.search_engines.items():
                        if engine_config['enabled']:
                            future = executor.submit(
                                self._search_engine,
                                engine_id,
                                engine_config,
                                q,
                                filters
                            )
                            futures.append(future)
                            search_stats['engines_queried'] += 1
                
                # Raccogli risultati
                for future in as_completed(futures):
                    try:
                        results = future.result()
                        if results:
                            all_results.extend(results)
                            search_stats['engines_succeeded'] += 1
                    except Exception as e:
                        search_stats['engines_failed'] += 1
            
            search_stats['search_time'] = time.time() - start_time
            
            # 2. DE-DUPLICAZIONE
            unique_results = self._deduplicate_results(all_results)
            
            # 3. FILTRO SEMANTICO "CURATORE" (Il cuore della qualità)
            # Scarta aggressivamente risultati medici, ingegneristici o irrilevanti
            curated_results = self._semantic_curator_filter(unique_results, query)
            
            # 4. CATEGORIZZAZIONE & RANKING
            ranked_results = self._rank_and_categorize(curated_results, query)
            
            # 5. ARRICCHIMENTO SNIPPET
            self._enrich_snippets(ranked_results)
            
            # 6. GENERAZIONE SUGGERIMENTI "PROFESSOR MODE"
            suggestions = self._generate_suggestions(query, ranked_results)
            
            search_stats['total_results'] = len(ranked_results)
            
            # Prepara risposta strutturata
            response = {
                'success': True,
                'query': query,
                'filters': filters,
                'results': ranked_results[:60],  # Top 60 risultati curati
                'suggestions': suggestions,
                'stats': search_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            # Salva in cache
            self._save_to_cache(cache_key, response)
            
            logger.info(f"✅ Ricerca completata: {len(ranked_results)} risultati unici in {search_stats['search_time']:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Errore ricerca multi-fonte: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def _search_engine(self, engine_id: str, config: Dict, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su un singolo motore"""
        
        try:
            if engine_id == 'semantic_scholar':
                return self._search_semantic_scholar(query, filters)
            elif engine_id == 'arxiv':
                return self._search_arxiv(query, filters)
            elif engine_id == 'pubmed':
                return self._search_pubmed(query, filters)
            elif engine_id == 'openalex':
                return self._search_openalex(query, filters)
            elif engine_id == 'crossref':
                return self._search_crossref(query, filters)
            elif engine_id == 'core':
                return self._search_core(query, filters)
            elif engine_id == 'wikipedia':
                return self._search_wikipedia(query, filters)
            elif engine_id == 'duckduckgo':
                return self._search_duckduckgo(query, filters)
            elif engine_id == 'salesian_online':
                return self._search_salesian_online(query, filters)
            elif engine_id == 'uqac_classiques':
                return self._search_uqac(query, filters)
            elif engine_id == 'theses_fr':
                return self._search_theses_fr(query, filters)
            elif engine_id in ['vatican', 'sep', 'cairn', 'persee', 'openedition', 'gallica', 'gutenberg']:
                return self._search_generic_site(engine_id, query, filters)
            else:
                logger.warning(f"Motore {engine_id} non implementato")
                return []
                
        except Exception as e:
            logger.error(f"Errore ricerca {engine_id}: {str(e)}")
            return []
    
    def _search_semantic_scholar(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su Semantic Scholar"""
        
        try:
            url = 'https://api.semanticscholar.org/graph/v1/paper/search'
            
            params = {
                'query': query,
                'limit': self.max_results_per_engine,
                'fields': 'title,authors,year,abstract,url,citationCount,venue,publicationTypes'
            }
            
            if filters and filters.get('year_from'):
                params['year'] = f"{filters['year_from']}-"
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for paper in data.get('data', []):
                    result = {
                        'title': paper.get('title', ''),
                        'authors': [author.get('name', '') for author in paper.get('authors', [])],
                        'year': paper.get('year'),
                        'abstract': paper.get('abstract', ''),
                        'url': paper.get('url', ''),
                        'citations': paper.get('citationCount', 0),
                        'venue': paper.get('venue', ''),
                        'source': 'Semantic Scholar',
                        'type': 'academic_paper'
                    }
                    results.append(result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Errore Semantic Scholar: {str(e)}")
            return []
    
    def _search_arxiv(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su arXiv"""
        
        try:
            url = 'http://export.arxiv.org/api/query'
            
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': self.max_results_per_engine
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                results = []
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns)
                    summary = entry.find('atom:summary', ns)
                    published = entry.find('atom:published', ns)
                    link = entry.find('atom:id', ns)
                    
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name = author.find('atom:name', ns)
                        if name is not None:
                            authors.append(name.text)
                    
                    result = {
                        'title': title.text if title is not None else '',
                        'authors': authors,
                        'year': published.text[:4] if published is not None else None,
                        'abstract': summary.text if summary is not None else '',
                        'url': link.text if link is not None else '',
                        'source': 'arXiv',
                        'type': 'preprint'
                    }
                    results.append(result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Errore arXiv: {str(e)}")
            return []
    
    def _search_pubmed(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su PubMed"""
        
        try:
            # Primo step: search per ottenere IDs
            search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
            
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': self.max_results_per_engine,
                'retmode': 'json'
            }
            
            response = requests.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                ids = data.get('esearchresult', {}).get('idlist', [])
                
                if not ids:
                    return []
                
                # Secondo step: fetch dettagli
                fetch_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
                
                fetch_params = {
                    'db': 'pubmed',
                    'id': ','.join(ids),
                    'retmode': 'json'
                }
                
                fetch_response = requests.get(fetch_url, params=fetch_params, timeout=self.timeout)
                
                if fetch_response.status_code == 200:
                    fetch_data = fetch_response.json()
                    results = []
                    
                    for pmid in ids:
                        article = fetch_data.get('result', {}).get(pmid, {})
                        
                        result = {
                            'title': article.get('title', ''),
                            'authors': [author.get('name', '') for author in article.get('authors', [])],
                            'year': article.get('pubdate', '')[:4] if article.get('pubdate') else None,
                            'abstract': '',  # PubMed summary non include abstract completo
                            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            'source': 'PubMed',
                            'type': 'medical_paper',
                            'pmid': pmid
                        }
                        results.append(result)
                    
                    return results
            
            return []
            
        except Exception as e:
            logger.error(f"Errore PubMed: {str(e)}")
            return []
    
    def _search_openalex(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su OpenAlex"""
        
        try:
            url = 'https://api.openalex.org/works'
            
            params = {
                'search': query,
                'per_page': self.max_results_per_engine
            }
            
            headers = {
                'User-Agent': 'Moteur de Rédaction Magique (mailto:contact@example.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for work in data.get('results', []):
                    authors = []
                    for authorship in work.get('authorships', []):
                        author = authorship.get('author', {})
                        if author.get('display_name'):
                            authors.append(author['display_name'])
                    
                    result = {
                        'title': work.get('title', ''),
                        'authors': authors,
                        'year': work.get('publication_year'),
                        'abstract': work.get('abstract', ''),
                        'url': work.get('doi', ''),
                        'citations': work.get('cited_by_count', 0),
                        'source': 'OpenAlex',
                        'type': 'academic_paper'
                    }
                    results.append(result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Errore OpenAlex: {str(e)}")
            return []
    
    def _search_crossref(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su Crossref"""
        
        try:
            url = 'https://api.crossref.org/works'
            
            params = {
                'query': query,
                'rows': self.max_results_per_engine
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('message', {}).get('items', []):
                    authors = []
                    for author in item.get('author', []):
                        if author.get('given') and author.get('family'):
                            authors.append(f"{author['given']} {author['family']}")
                    
                    result = {
                        'title': item.get('title', [''])[0],
                        'authors': authors,
                        'year': item.get('published-print', {}).get('date-parts', [[None]])[0][0],
                        'abstract': item.get('abstract', ''),
                        'url': item.get('URL', ''),
                        'doi': item.get('DOI', ''),
                        'source': 'Crossref',
                        'type': 'academic_paper'
                    }
                    results.append(result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Errore Crossref: {str(e)}")
            return []
    
    def _search_core(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su CORE"""
        
        try:
            # CORE richiede API key, implementazione base
            logger.info("CORE search richiede API key - implementazione placeholder")
            return []
            
        except Exception as e:
            logger.error(f"Errore CORE: {str(e)}")
            return []
    
    def _search_wikipedia(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su Wikipedia"""
        
        try:
            url = 'https://en.wikipedia.org/w/api.php'
            
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srlimit': self.max_results_per_engine,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('query', {}).get('search', []):
                    result = {
                        'title': item.get('title', ''),
                        'authors': ['Wikipedia Contributors'],
                        'year': None,
                        'abstract': item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''),
                        'url': f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                        'source': 'Wikipedia',
                        'type': 'encyclopedia'
                    }
                    results.append(result)
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Errore Wikipedia: {str(e)}")
            return []
    
    def _search_duckduckgo(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su DuckDuckGo (Real Implementation)"""
        
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=self.max_results_per_engine))
                
                for item in ddg_results:
                    result = {
                        'title': item.get('title', ''),
                        'authors': [],
                        'year': None,
                        'abstract': item.get('body', ''),
                        'url': item.get('href', ''),
                        'source': 'DuckDuckGo',
                        'type': 'web'
                    }
                    results.append(result)
            
            return results
            
        except ImportError:
            logger.warning("duckduckgo_search module not found. Installing...")
            try:
                import subprocess
                subprocess.check_call(["pip", "install", "duckduckgo-search"])
                return self._search_duckduckgo(query, filters)
            except Exception as e:
                logger.error(f"Failed to install duckduckgo-search: {str(e)}")
                return []
                
        except Exception as e:
            logger.error(f"Errore DuckDuckGo: {str(e)}")
            return []

    def _search_salesian_online(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su Salesian.online"""
        return self._search_site_specific(query, "salesian.online", "Salesian.online", "FONTE_ISTITUZIONALE")

    def _search_sdb_org(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su SDB.org"""
        return self._search_site_specific(query, "sdb.org", "SDB.org", "FONTE_ISTITUZIONALE")

    def _search_donboscosanto(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca su DonBoscoSanto.eu"""
        return self._search_site_specific(query, "donboscosanto.eu", "DonBoscoSanto.eu", "FONTE_ISTITUZIONALE")

    def _search_uqac(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca simulata su UQAC (usando DuckDuckGo con site:)"""
        return self._search_site_specific(query, "classiques.uqac.ca", "Classiques UQAC", "FONTE_PRIMARIA")

    def _search_theses_fr(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """Ricerca simulata su Theses.fr (usando DuckDuckGo con site:)"""
        return self._search_site_specific(query, "theses.fr", "Thèses.fr", "STUDIO_ACCADEMICO")

    def _search_generic_site(self, query: str, filters: Optional[Dict], engine_config: Dict) -> List[Dict]:
        """Ricerca generica su un sito specifico (usando DuckDuckGo con site:)"""
        domain = engine_config['base_url'].replace('https://', '').replace('http://', '').split('/')[0]
        source_name = engine_config['name']
        category = "RISORSA_WEB"
        if engine_config['type'] == 'institutional': category = "FONTE_ISTITUZIONALE"
        elif engine_config['type'] == 'academic_source': category = "STUDIO_ACCADEMICO"
        elif engine_config['type'] == 'archive': category = "FONTE_PRIMARIA"
        
        return self._search_site_specific(query, domain, source_name, category)

    def _search_site_specific(self, query: str, domain: str, source_name: str, category: str) -> List[Dict]:
        """Helper per cercare su un dominio specifico usando DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            site_query = f"site:{domain} {query}"
            results = []
            
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(site_query, max_results=5))
                
                for item in ddg_results:
                    result = {
                        'title': item.get('title', ''),
                        'authors': [],
                        'year': None,
                        'abstract': item.get('body', ''),
                        'url': item.get('href', ''),
                        'source': source_name,
                        'type': 'web',
                        'category': category
                    }
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Errore ricerca sito {domain}: {str(e)}")
            return []
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """De-duplicazione risultati basata su titolo"""
        
        seen_titles = set()
        unique_results = []
        
        for result in results:
            title = result.get('title', '').lower().strip()
            
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
    
    def _semantic_curator_filter(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Il 'Curatore Digitale': Filtra via il rumore (medicina, ingegneria, ecc.)
        e mantiene solo ciò che è pertinente al dominio Salesiano/Umanistico.
        """
        filtered = []
        
        # Termini "tossici" che indicano quasi sempre un risultato errato per questo dominio
        toxic_terms = {
            'alzheimer', 'protein', 'molecular', 'clinical', 'surgery', 'tumor', 
            'cancer', 'electric power', 'voltage', 'circuit', 'algorithm', 
            'wireless', 'sensor', 'polymer', 'chemical', 'magnetic', 'galaxy'
        }
        
        # Termini "gold" che garantiscono la rilevanza
        gold_terms = {
            'salesian', 'bosco', 'educat', 'pedagog', 'pastoral', 'youth', 
            'giovani', 'preventive', 'religion', 'catholic', 'church', 
            'teologia', 'spiritu', 'history', 'storia', 'mazzarello'
        }
        
        query_terms = set(query.lower().split())
        
        for res in results:
            title = (res.get('title') or "").lower()
            abstract = (res.get('abstract') or "").lower()
            full_text = title + " " + abstract
            
            # 1. Controllo Tossicità
            if any(term in title for term in toxic_terms):
                continue # Scarta immediatamente
                
            # 2. Controllo Rilevanza Dominio (Gold Terms)
            # Se non contiene ALMENO UN termine del dominio salesiano/educativo, è sospetto
            # A meno che la query stessa non sia fuori dominio (ma qui assumiamo uso salesiano)
            if not any(term in full_text for term in gold_terms):
                # Se non ha gold terms, deve avere ALMENO tutti i termini della query nel titolo
                if not all(q in title for q in query_terms):
                    continue
            
            # 3. Pulizia Formale
            if len(title) < 5: continue
            if res.get('title', '').isupper():
                res['title'] = res['title'].title()
                
            filtered.append(res)
            
        return filtered

    def _rank_and_categorize(self, results: List[Dict], query: str) -> List[Dict]:
        """Assegna categorie (Fonte, Studio, Web) e calcola score"""
        
        for res in results:
            title = (res.get('title') or "").lower()
            abstract = (res.get('abstract') or "").lower()
            full_text = title + " " + abstract
            score = 0  # Inizializzazione score
            
            # Assegnazione Categoria
            url_str = str(res.get('url', '')).lower()
            
            if any(domain in url_str for domain in ['salesian.online', 'sdb.org', 'donboscosanto.eu']):
                res['category'] = 'FONTE_ISTITUZIONALE'
                res['category_label'] = 'Fonte Ufficiale'
                score += 40  # Boost massiccio per fonti salesiane
            elif 'vatican.va' in url_str:
                res['category'] = 'FONTE_ISTITUZIONALE'
                res['category_label'] = 'Magistero'
                score += 35
            elif 'theses.fr' in url_str:
                res['category'] = 'STUDIO_ACCADEMICO'
                res['category_label'] = 'Tesi Dottorato'
            elif 'gallica.bnf.fr' in str(res.get('url', '')) or 'gutenberg.org' in str(res.get('url', '')):
                res['category'] = 'FONTE_PRIMARIA'
                res['category_label'] = 'Archivio Storico'
            elif any(x in str(res.get('url', '')) for x in ['cairn.info', 'persee.fr', 'openedition.org', 'plato.stanford.edu']):
                res['category'] = 'STUDIO_ACCADEMICO'
                res['category_label'] = 'Studio Accademico'
            elif any(x in full_text for x in ['memorie', 'epistolario', 'costituzioni', 'scritti']):
                res['category'] = 'FONTE_PRIMARIA'
                res['category_label'] = 'Fonte Primaria'
            elif res.get('type') in ['academic', 'article', 'book', 'academic_thesis', 'academic_source', 'institutional', 'archive']:
                res['category'] = 'STUDIO_ACCADEMICO'
                res['category_label'] = 'Studio'
            else:
                res['category'] = 'RISORSA_WEB'
                res['category_label'] = 'Web'
                
            # Calcolo Score (0-100)
            score = 50 # Base
            
            # Bonus per Gold Terms
            if 'salesian' in full_text: score += 20
            if 'bosco' in title: score += 20
            if 'educat' in full_text: score += 10
            
            # Bonus Recenza
            try:
                if int(res.get('year', 0)) > 2015: score += 10
            except: pass
            
            # Bonus Citazioni
            if res.get('citations', 0) > 5: score += 10
            
            res['relevance_score'] = min(score, 100)
            res['relevance'] = f"{res['relevance_score']}%"
            
        # Ordina: Prima le Fonti Primarie/Istituzionali, poi gli Studi più rilevanti
        results.sort(key=lambda x: (
            1 if x['category'] == 'FONTE_PRIMARIA' else 
            2 if x['category'] == 'FONTE_ISTITUZIONALE' else 
            3 if x['category'] == 'STUDIO_ACCADEMICO' else 4,
            -x['relevance_score']
        ))
        
        return results

    def _enrich_snippets(self, results: List[Dict]):
        """Genera snippet sintetici se manca l'abstract e popola gli insight"""
        logger.info(f"🔍 Avvio arricchimento per {len(results)} risultati")
        count_enriched = 0
        
        for res in results:
            # 1. Arricchimento Abstract
            if not res.get('abstract') or res.get('abstract') == 'Nessun contenuto disponibile':
                parts = []
                if res.get('type'):
                    parts.append(f"[{res.get('type').upper()}]")
                if res.get('year'):
                    parts.append(f"Published in {res.get('year')}")
                if res.get('venue'):
                    parts.append(f"in {res.get('venue')}")
                if res.get('authors'):
                    authors = res.get('authors')
                    if isinstance(authors, list):
                        auth_str = ", ".join(authors[:3])
                        if len(authors) > 3:
                            auth_str += " et al."
                        parts.append(f"by {auth_str}")
                
                if parts:
                    res['abstract'] = " • ".join(parts) + "."
                else:
                    res['abstract'] = "Documento accademico rilevante recuperato dalla fonte originale."

            # 2. Generazione Insight Dinamici
            try:
                # Usa il titolo o l'abstract come base per la query contestuale
                context_query = res.get('title', '')
                res['insights'] = insight_engine.generate_insights(res, context_query)
                count_enriched += 1
            except Exception as e:
                logger.error(f"Errore generazione insight per {res.get('title')}: {e}")
                # Fallback minimale per evitare crash frontend
                res['insights'] = {
                    'researcher': {'theoretical_framework': "Dati non disponibili"},
                    'journalist': {'narrative_angle': "Dati non disponibili"},
                    'pastoral': {'catechesis_prompt': "Dati non disponibili"}
                }
        
        logger.info(f"✨ Completato arricchimento: {count_enriched}/{len(results)} risultati processati")

    def _generate_suggestions(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Genera suggerimenti in 'Professor Mode' (Piste di Ricerca Critiche)
        Non semplici link correlati, ma domande di ricerca e confronti.
        """
        suggestions = []
        
        # 1. Pista Comparativa (Confronto Storico/Pedagogico)
        if "bosco" in query.lower() or "preventivo" in query.lower():
            suggestions.append({
                "text": "Confronta l'evoluzione del Sistema Preventivo (1877) con la 'Lettera da Roma' (1884): continuità o rottura?",
                "type": "comparative_analysis",
                "icon": "scale"
            })
        
        # 2. Pista Critica (Analisi delle Fonti)
        suggestions.append({
            "text": "Analizza le differenze tra le Memorie dell'Oratorio (autobiografia) e le biografie critiche moderne (es. Lenti, Stella).",
            "type": "critical_source",
            "icon": "book-open"
        })
        
        # 3. Pista Attuale (Applicazione Oggi)
        suggestions.append({
            "text": "Come si applica il criterio dell'Amorevolezza nei contesti educativi digitali odierni?",
            "type": "modern_application",
            "icon": "lightbulb"
        })
        
        # 4. Pista Bibliografica (Suggerimento Esperto)
        suggestions.append({
            "text": "Per una visione completa, consulta gli atti del Congresso Internazionale di Studi su Don Bosco (LAS, Roma).",
            "type": "expert_tip",
            "icon": "graduation-cap"
        })
            
        return suggestions

    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Ranking risultati per rilevanza con punteggi normalizzati 0-100%"""
        
        query_terms = set(query.lower().split())
        
        for result in results:
            score = 0.0
            
            # Punteggio basato su titolo (Peso: 40%)
            title = result.get('title', '').lower()
            title_terms = set(title.split())
            title_match = len(query_terms & title_terms) / len(query_terms) if query_terms else 0
            score += title_match * 40
            
            # Punteggio basato su abstract (Peso: 30%)
            abstract = result.get('abstract', '')
            if abstract and abstract != 'Nessun contenuto disponibile':
                abstract = abstract.lower()
                abstract_terms = set(abstract.split())
                abstract_match = len(query_terms & abstract_terms) / len(query_terms) if query_terms else 0
                score += abstract_match * 30
            
            # Bonus per citazioni (Peso: 15%)
            citations = result.get('citations', 0)
            if citations > 0:
                score += min(citations / 50, 1) * 15
            
            # Bonus per anno recente (Peso: 15%)
              # Boost Recenza
            if res.get('year'):
                try:
                    year = int(res['year'])
                    current_year = datetime.now().year
                    if year >= current_year - 3:
                        score += 20  # Aumentato boost per recenza
                    elif year >= current_year - 10:
                        score += 10
                except:
                    pass
            
            # Boost Semantico "Soft" (Tolleranza)
            # Se contiene radici importanti anche se non la parola esatta
            soft_roots = ['educ', 'pedagog', 'pastor', 'giovan', 'sales', 'bosco']
            matches = sum(1 for root in soft_roots if root in full_text)
            score += matches * 5  # 5 punti per ogni radice trovatass
            
            # Normalizzazione e assegnazione
            final_score = min(round(score), 100)
            result['relevance_score'] = final_score
            result['relevance'] = f"{final_score}%" # Stringa per frontend
        
        # Ordina per score decrescente
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return results
    
    def _generate_cache_key(self, query: str, filters: Optional[Dict]) -> str:
        """Genera chiave cache univoca"""
        
        cache_string = f"{query}_{json.dumps(filters, sort_keys=True) if filters else ''}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Recupera risultati dalla cache"""
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Verifica età cache
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < self.cache_duration:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Salva risultati in cache"""
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Errore salvataggio cache: {str(e)}")


# Istanza globale
search_engine = MultiSourceSearchEngine()


def search_multi_source(query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """Funzione wrapper per compatibilità"""
    return search_engine.search(query, filters)

    def _search_salesian_online(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """
        Ricerca specifica su Salesian.online
        """
        try:
            results = []
            # Use DuckDuckGo restricted to site:salesian.online for real results
            ddg_results = self._search_duckduckgo(f"site:salesian.online {query}", filters)
            
            for res in ddg_results:
                res['source'] = 'Salesian.online'
                res['type'] = 'salesian_web'
                res['venue'] = 'Salesian.online'
                res['relevance_score'] = 100 
                results.append(res)
                
            return results
        except Exception as e:
            logger.error(f"Errore ricerca Salesian.online: {str(e)}")
            return []

    def _search_uqac(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """
        Ricerca su Les Classiques des Sciences Sociales (UQAC)
        Usa DuckDuckGo con site:classiques.uqac.ca
        """
        try:
            results = []
            ddg_results = self._search_duckduckgo(f"site:classiques.uqac.ca {query}", filters)
            
            for res in ddg_results:
                res['source'] = 'Classiques UQAC'
                res['type'] = 'academic_source'
                res['venue'] = 'Les Classiques des Sciences Sociales'
                res['abstract'] = f"[TESTO FONDAMENTALE] {res.get('abstract', '')}"
                results.append(res)
            return results
        except Exception as e:
            logger.error(f"Errore ricerca UQAC: {str(e)}")
            return []

    def _search_theses_fr(self, query: str, filters: Optional[Dict]) -> List[Dict]:
        """
        Ricerca su Theses.fr (Dottorati e Dissertazioni)
        """
        try:
            results = []
            ddg_results = self._search_duckduckgo(f"site:theses.fr {query}", filters)
            
            for res in ddg_results:
                res['source'] = 'Thèses.fr'
                res['type'] = 'academic_thesis'
                res['venue'] = 'Thèses de Doctorat (France)'
                res['abstract'] = f"[TESI DI DOTTORATO] {res.get('abstract', '')}"
                results.append(res)
            return results
        except Exception as e:
            logger.error(f"Errore ricerca Theses.fr: {str(e)}")
            return []

    def _search_generic_site(self, engine_id: str, query: str, filters: Optional[Dict]) -> List[Dict]:
        """
        Ricerca generica su un sito specifico usando DuckDuckGo
        """
        try:
            config = self.search_engines.get(engine_id)
            if not config: return []
            
            base_url = config['base_url'].replace('https://', '').replace('http://', '').replace('www.', '')
            site_query = f"site:{base_url} {query}"
            
            results = []
            ddg_results = self._search_duckduckgo(site_query, filters)
            
            for res in ddg_results:
                res['source'] = config['name']
                res['type'] = config['type']
                res['venue'] = config['name']
                
                # Arricchimento snippet in base alla fonte
                prefix = ""
                if engine_id == 'vatican': prefix = "[MAGISTERO]"
                elif engine_id == 'sep': prefix = "[FILOSOFIA]"
                elif engine_id in ['cairn', 'persee', 'openedition']: prefix = "[STUDIO FRANCESE]"
                elif engine_id in ['gallica', 'gutenberg']: prefix = "[ARCHIVIO STORICO]"
                
                if prefix:
                    res['abstract'] = f"{prefix} {res.get('abstract', '')}"
                
                results.append(res)
            return results
        except Exception as e:
            logger.error(f"Errore ricerca {engine_id}: {str(e)}")
            return []
