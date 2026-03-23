# -*- coding: utf-8 -*-
"""
Processore PDF Super Avanzato
Moteur de Rédaction Magique - Rev. Alphonse Owoudou
Versione 3.0 - Capacità Professionali Complete
"""

import logging
import os
import re
import sys
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import json
import hashlib

# Aggiungi il path locale per le librerie installate con --user
sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.11/site-packages'))

logger = logging.getLogger(__name__)

class AdvancedPDFProcessor:
    """
    Processore PDF di livello professionale con funzionalità complete
    """
    
    def __init__(self):
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.chunk_size = 8000  # Caratteri per chunk
        self.overlap_size = 500  # Overlap tra chunks
        self.min_chunk_size = 1000  # Dimensione minima chunk
        
        # Cache per evitare riprocessing
        self.processing_cache = {}
        
    def process_pdf_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Processing PDF completo con tutte le funzionalità avanzate
        """
        try:
            # Verifica dimensione file
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {
                    'success': False,
                    'error': f'File troppo grande: {file_size / (1024*1024):.1f}MB. Limite: {self.max_file_size / (1024*1024):.0f}MB'
                }
            
            logger.info(f"🔄 Inizio processing PDF avanzato: {filename} ({file_size / (1024*1024):.1f}MB)")
            
            # 1. Estrazione testo con metodo migliore
            extraction_result = self._extract_text_robust(file_path, filename)
            if not extraction_result['success']:
                return extraction_result
            
            text = extraction_result['text']
            basic_metadata = extraction_result['metadata']
            
            # 2. Estrazione metadati PDF completa
            pdf_metadata = self._extract_pdf_metadata(file_path)
            
            # 3. Chunking intelligente
            chunks = self._create_intelligent_chunks(text, filename)
            
            # 4. Analisi semantica avanzata
            semantic_analysis = self._perform_semantic_analysis(text)
            
            # 5. Estrazione entità salesiane
            entities = self._extract_salesien_entities(text)
            
            # 6. Analisi struttura documento
            structure = self._analyze_document_structure(text)
            
            # 7. Generazione sommario intelligente
            summary = self._generate_intelligent_summary(text, chunks)
            
            # 8. Estrazione citazioni e bibliografia
            citations = self._extract_citations_and_bibliography(text)
            
            # Risultato completo
            result = {
                'success': True,
                'text': text,
                'metadata': {
                    **basic_metadata,
                    **pdf_metadata,
                    'processing_timestamp': datetime.now().isoformat()
                },
                'chunks': chunks,
                'entities': entities,
                'concepts': semantic_analysis['concepts'],
                'keywords': semantic_analysis['keywords'],
                'themes': semantic_analysis['themes'],
                'structure': structure,
                'summary': summary,
                'citations': citations,
                'processing_info': {
                    'total_chars': len(text),
                    'total_words': len(text.split()),
                    'total_chunks': len(chunks),
                    'extraction_method': basic_metadata.get('extraction_method', 'unknown'),
                    'processing_time': datetime.now().isoformat(),
                    'file_size_mb': round(file_size / (1024 * 1024), 2)
                }
            }
            
            logger.info(f"✅ PDF processing completato: {filename} - {len(chunks)} chunks, {len(text)} caratteri")
            return result
            
        except Exception as e:
            logger.error(f"❌ Errore critico processing PDF {filename}: {str(e)}")
            return {
                'success': False,
                'error': f'Errore critico processing PDF: {str(e)}'
            }
    
    def _extract_text_robust(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Estrazione testo SUPER ROBUSTA con 4 metodi diversi
        """
        
        # Metodo 1: PyMuPDF (fitz) - IL PIÙ POTENTE E COMPLETO
        try:
            import fitz
            doc = fitz.open(file_path)
            
            text = ""
            pages_info = []
            total_images = 0
            total_links = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                if page_text:
                    text += f"\n=== PAGINA {page_num + 1} ===\n{page_text}\n"
                
                # Metadati dettagliati pagina
                images = page.get_images()
                links = page.get_links()
                
                page_info = {
                    'page_number': page_num + 1,
                    'text_length': len(page_text),
                    'word_count': len(page_text.split()),
                    'has_images': len(images) > 0,
                    'images_count': len(images),
                    'has_links': len(links) > 0,
                    'links_count': len(links)
                }
                pages_info.append(page_info)
                
                total_images += len(images)
                total_links += len(links)
            
            # Metadati documento completi
            doc_metadata = doc.metadata
            toc = doc.get_toc()
            
            doc.close()
            
            if text.strip():
                return {
                    'success': True,
                    'text': text,
                    'metadata': {
                        'extraction_method': 'PyMuPDF',
                        'total_pages': len(doc),
                        'pages_info': pages_info,
                        'document_metadata': doc_metadata,
                        'has_toc': len(toc) > 0,
                        'toc_entries': len(toc),
                        'total_images': total_images,
                        'total_links': total_links,
                        'file_size': os.path.getsize(file_path)
                    }
                }
        except Exception as e:
            logger.warning(f"PyMuPDF fallito per {filename}: {str(e)}")
        
        # Metodo 2: pdfplumber - ECCELLENTE PER TABELLE
        try:
            import pdfplumber
            
            text = ""
            pages_info = []
            tables_found = 0
            
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    
                    if page_text:
                        text += f"\n=== PAGINA {i + 1} ===\n{page_text}\n"
                    
                    # Estrazione tabelle
                    tables = page.extract_tables()
                    if tables:
                        tables_found += len(tables)
                        
                        for j, table in enumerate(tables):
                            text += f"\n--- TABELLA {j + 1} PAGINA {i + 1} ---\n"
                            for row in table:
                                if row:
                                    clean_row = [cell or "" for cell in row]
                                    text += " | ".join(clean_row) + "\n"
                    
                    page_info = {
                        'page_number': i + 1,
                        'text_length': len(page_text) if page_text else 0,
                        'tables_count': len(tables) if tables else 0
                    }
                    pages_info.append(page_info)
            
            if text.strip():
                return {
                    'success': True,
                    'text': text,
                    'metadata': {
                        'extraction_method': 'pdfplumber',
                        'total_pages': len(pages_info),
                        'pages_info': pages_info,
                        'tables_found': tables_found,
                        'file_size': os.path.getsize(file_path)
                    }
                }
        except Exception as e:
            logger.warning(f"pdfplumber fallito per {filename}: {str(e)}")
        
        # Metodo 3: PyPDF2 - FALLBACK CLASSICO
        try:
            import PyPDF2
            
            text = ""
            pages_info = []
            
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n=== PAGINA {i + 1} ===\n{page_text}\n"
                        
                        page_info = {
                            'page_number': i + 1,
                            'text_length': len(page_text)
                        }
                        pages_info.append(page_info)
            
            if text.strip():
                return {
                    'success': True,
                    'text': text,
                    'metadata': {
                        'extraction_method': 'PyPDF2',
                        'total_pages': len(pages_info),
                        'pages_info': pages_info,
                        'file_size': os.path.getsize(file_path)
                    }
                }
        except Exception as e:
            logger.warning(f"PyPDF2 fallito per {filename}: {str(e)}")
        
        # Metodo 4: pdfminer - ULTIMO TENTATIVO
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(file_path)
            
            if text.strip():
                return {
                    'success': True,
                    'text': text,
                    'metadata': {
                        'extraction_method': 'pdfminer',
                        'file_size': os.path.getsize(file_path)
                    }
                }
        except Exception as e:
            logger.warning(f"pdfminer fallito per {filename}: {str(e)}")
        
        # Tutti i metodi falliti
        return {
            'success': False,
            'error': f"""❌ ESTRAZIONE PDF FALLITA per {filename}

Tutti i 4 metodi di estrazione hanno fallito:
- PyMuPDF (fitz): Metodo più potente
- pdfplumber: Specializzato in tabelle  
- PyPDF2: Metodo classico
- pdfminer: Ultimo tentativo

Possibili cause:
• PDF protetto da password
• PDF corrotto o malformato
• PDF contenente solo immagini (scansioni)
• PDF con encoding non standard

Suggerimenti:
• Verificare che il PDF sia leggibile
• Provare a salvarlo nuovamente
• Usare un PDF con testo selezionabile"""
        }
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Estrazione metadati PDF completa"""
        metadata = {}
        
        try:
            import fitz
            doc = fitz.open(file_path)
            
            # Metadati base del documento
            doc_metadata = doc.metadata
            metadata.update({
                'title': doc_metadata.get('title', ''),
                'author': doc_metadata.get('author', ''),
                'subject': doc_metadata.get('subject', ''),
                'creator': doc_metadata.get('creator', ''),
                'producer': doc_metadata.get('producer', ''),
                'creation_date': doc_metadata.get('creationDate', ''),
                'modification_date': doc_metadata.get('modDate', ''),
                'keywords': doc_metadata.get('keywords', ''),
                'pdf_version': doc_metadata.get('format', '')
            })
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"Errore estrazione metadati PDF: {str(e)}")
            
        return metadata
    
    def _create_intelligent_chunks(self, text: str, filename: str) -> List[Dict]:
        """Chunking intelligente basato su struttura del documento"""
        
        chunks = []
        
        # Dividi per pagine se presenti
        if "=== PAGINA" in text:
            pages = re.split(r'=== PAGINA \d+ ===', text)
            pages = [page.strip() for page in pages if page.strip()]
            
            for i, page_content in enumerate(pages):
                if len(page_content) > self.chunk_size:
                    # Pagina troppo lunga, dividi ulteriormente
                    page_chunks = self._split_by_paragraphs(page_content, i + 1)
                    chunks.extend(page_chunks)
                else:
                    # Pagina intera come chunk
                    chunk = {
                        'chunk_id': len(chunks) + 1,
                        'content': page_content,
                        'page_number': i + 1,
                        'chunk_type': 'page',
                        'word_count': len(page_content.split()),
                        'char_count': len(page_content)
                    }
                    chunks.append(chunk)
        else:
            # Nessuna divisione per pagine, usa chunking standard
            chunks = self._split_by_paragraphs(text)
        
        logger.info(f"Creati {len(chunks)} chunks intelligenti per {filename}")
        return chunks
    
    def _split_by_paragraphs(self, text: str, page_number: Optional[int] = None) -> List[Dict]:
        """Divisione per paragrafi con overlap intelligente"""
        
        chunks = []
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_words = len(paragraph.split())
            
            # Se aggiungendo questo paragrafo supero la dimensione, crea nuovo chunk
            if current_word_count + paragraph_words > self.chunk_size and current_chunk:
                chunk = {
                    'chunk_id': len(chunks) + 1,
                    'content': current_chunk.strip(),
                    'chunk_type': 'paragraph_group',
                    'word_count': current_word_count,
                    'char_count': len(current_chunk)
                }
                
                if page_number:
                    chunk['page_number'] = page_number
                
                chunks.append(chunk)
                
                # Inizia nuovo chunk con overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + "\n\n" + paragraph
                current_word_count = len(current_chunk.split())
            else:
                # Aggiungi paragrafo al chunk corrente
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_word_count += paragraph_words
        
        # Aggiungi ultimo chunk se non vuoto
        if current_chunk.strip():
            chunk = {
                'chunk_id': len(chunks) + 1,
                'content': current_chunk.strip(),
                'chunk_type': 'paragraph_group',
                'word_count': current_word_count,
                'char_count': len(current_chunk)
            }
            
            if page_number:
                chunk['page_number'] = page_number
            
            chunks.append(chunk)
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Ottieni testo di overlap dalla fine del chunk precedente"""
        words = text.split()
        if len(words) <= 50:
            return text
        
        # Prendi ultime 50 parole come overlap
        overlap_words = words[-50:]
        return " ".join(overlap_words)
    
    def _perform_semantic_analysis(self, text: str) -> Dict[str, List[str]]:
        """Analisi semantica avanzata del testo"""
        
        text_lower = text.lower()
        
        # Concetti salesiani avanzati
        salesien_concepts = [
            'système préventif', 'sistema preventivo', 'amorevolezza',
            'raison religion', 'ragione religione', 'pastorale des jeunes',
            'éducation salésienne', 'educazione salesiana', 'oratorio',
            'marie auxiliatrice', 'maria ausiliatrice', 'valdocco',
            'famille salésienne', 'famiglia salesiana', 'mission salésienne'
        ]
        
        concepts_found = []
        for concept in salesien_concepts:
            if concept in text_lower:
                concepts_found.append(concept)
        
        # Keywords frequenti
        words = text_lower.split()
        word_freq = {}
        
        for word in words:
            if len(word) > 4 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Prendi le 15 parole più frequenti
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        keywords = [word for word, freq in frequent_words if freq > 2]
        
        # Temi salesiani
        themes = []
        theme_patterns = {
            'pastorale_jeunes': ['jeunes', 'giovani', 'youth', 'adolescent'],
            'education': ['éducation', 'educazione', 'formation', 'formazione'],
            'spiritualite': ['spiritualité', 'spiritualità', 'prière', 'preghiera'],
            'mission': ['mission', 'missione', 'évangélisation', 'evangelizzazione']
        }
        
        for theme, patterns in theme_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                themes.append(theme)
        
        return {
            'concepts': concepts_found,
            'keywords': keywords,
            'themes': themes
        }
    
    def _extract_salesien_entities(self, text: str) -> Dict[str, List[str]]:
        """Estrazione entità salesiane specifiche"""
        
        entities = {
            'persone_salesiane': [],
            'luoghi_salesiani': [],
            'opere_salesiane': [],
            'concetti_chiave': [],
            'date_importanti': []
        }
        
        text_lower = text.lower()
        
        # Persone salesiane importanti
        persone = [
            'don bosco', 'giovanni bosco', 'marie auxiliatrice', 'maria ausiliatrice',
            'domenico savio', 'michele magone', 'francesco besucco', 'pietro braido',
            'egidio viganò', 'pascual chavez', 'angel fernandez artime', 'luigi ricceri'
        ]
        
        for persona in persone:
            if persona in text_lower:
                entities['persone_salesiane'].append(persona)
        
        # Luoghi salesiani
        luoghi = [
            'valdocco', 'turin', 'torino', 'mornese', 'castelnuovo', 'chieri',
            'roma', 'vatican', 'vaticano', 'oratorio', 'basilique marie auxiliatrice'
        ]
        
        for luogo in luoghi:
            if luogo in text_lower:
                entities['luoghi_salesiani'].append(luogo)
        
        # Opere salesiane
        opere = [
            'oratorio', 'école salésienne', 'scuola salesiana', 'université salésienne',
            'mission salésienne', 'paroisse salésienne', 'centre de formation'
        ]
        
        for opera in opere:
            if opera in text_lower:
                entities['opere_salesiane'].append(opera)
        
        # Date importanti (pattern migliorato)
        date_patterns = [
            r'\b(18|19|20)\d{2}\b',  # Anni
            r'\b\d{1,2}[/-]\d{1,2}[/-](18|19|20)\d{2}\b',  # Date complete
            r'\b(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(18|19|20)\d{2}\b'
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            entities['date_importanti'].extend([str(date) for date in dates])
        
        return entities
    
    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analisi avanzata della struttura del documento"""
        
        structure = {
            'has_title': False,
            'has_chapters': False,
            'has_sections': False,
            'has_bibliography': False,
            'has_footnotes': False,
            'has_tables': False,
            'estimated_type': 'unknown',
            'language': 'unknown',
            'complexity_level': 'medium'
        }
        
        text_lower = text.lower()
        
        # Rileva struttura
        if any(pattern in text for pattern in ['CHAPITRE', 'CAPITOLO', 'CHAPTER']):
            structure['has_chapters'] = True
            structure['estimated_type'] = 'book_or_thesis'
        
        if any(pattern in text for pattern in ['§', 'Section', 'Sezione', 'Art.']):
            structure['has_sections'] = True
        
        if any(pattern in text_lower for pattern in ['bibliographie', 'bibliografia', 'references', 'sources']):
            structure['has_bibliography'] = True
            structure['estimated_type'] = 'academic_paper'
        
        if any(pattern in text for pattern in ['¹', '²', '³', 'Note:', 'Nota:', 'Footnote']):
            structure['has_footnotes'] = True
        
        if 'TABELLA' in text or 'TABLE' in text:
            structure['has_tables'] = True
        
        # Rileva lingua predominante
        french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'une', 'dans']
        italian_words = ['il', 'la', 'le', 'di', 'del', 'della', 'e', 'è', 'una', 'in']
        english_words = ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'that', 'for']
        
        french_count = sum(1 for word in french_words if word in text_lower)
        italian_count = sum(1 for word in italian_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if french_count > italian_count and french_count > english_count:
            structure['language'] = 'french'
        elif italian_count > english_count:
            structure['language'] = 'italian'
        elif english_count > 0:
            structure['language'] = 'english'
        
        # Stima tipo documento
        if 'constitution' in text_lower:
            structure['estimated_type'] = 'constitutional_document'
        elif any(word in text_lower for word in ['encyclique', 'enciclica', 'exhortation']):
            structure['estimated_type'] = 'papal_document'
        elif 'règlement' in text_lower or 'regolamento' in text_lower:
            structure['estimated_type'] = 'regulatory_document'
        
        # Livello di complessità
        word_count = len(text.split())
        if word_count > 50000:
            structure['complexity_level'] = 'high'
        elif word_count < 5000:
            structure['complexity_level'] = 'low'
        
        return structure
    
    def _generate_intelligent_summary(self, text: str, chunks: List[Dict]) -> Dict[str, Any]:
        """Generazione sommario intelligente"""
        
        summary = {
            'word_count': len(text.split()),
            'char_count': len(text),
            'estimated_reading_time': len(text.split()) // 200,  # 200 parole/minuto
            'key_sections': [],
            'main_topics': [],
            'document_focus': 'unknown'
        }
        
        # Identifica sezioni chiave
        if chunks:
            # Prendi i primi 3 chunks come introduzione
            intro_chunks = chunks[:3]
            summary['key_sections'] = [
                {
                    'section': 'introduction',
                    'content': intro_chunks[0]['content'][:200] + '...' if intro_chunks else '',
                    'chunk_ids': [chunk['chunk_id'] for chunk in intro_chunks]
                }
            ]
        
        # Identifica focus del documento
        text_lower = text.lower()
        if any(word in text_lower for word in ['pastorale', 'jeunes', 'giovani']):
            summary['document_focus'] = 'pastorale_jeunes'
        elif any(word in text_lower for word in ['éducation', 'educazione', 'formation']):
            summary['document_focus'] = 'education'
        elif any(word in text_lower for word in ['spiritualité', 'spiritualità', 'prière']):
            summary['document_focus'] = 'spiritualite'
        
        return summary
    
    def _extract_citations_and_bibliography(self, text: str) -> Dict[str, List[str]]:
        """Estrazione citazioni e bibliografia"""
        
        citations = {
            'internal_references': [],
            'external_citations': [],
            'bibliography_entries': [],
            'footnotes': []
        }
        
        # Pattern per citazioni
        citation_patterns = [
            r'\([A-Z][a-z]+\s+\d{4}\)',  # (Autore 2020)
            r'\[[0-9]+\]',  # [1], [2], etc.
            r'cf\.\s+[A-Z][a-z]+',  # cf. Autore
            r'voir\s+[A-Z][a-z]+',  # voir Autore
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            citations['external_citations'].extend(matches)
        
        # Cerca sezione bibliografia
        if 'bibliographie' in text.lower() or 'bibliografia' in text.lower():
            # Estrai la sezione bibliografia
            biblio_start = text.lower().find('bibliographie')
            if biblio_start == -1:
                biblio_start = text.lower().find('bibliografia')
            
            if biblio_start != -1:
                biblio_section = text[biblio_start:biblio_start + 5000]  # Primi 5000 caratteri
                
                # Pattern per voci bibliografiche
                biblio_entries = re.findall(r'^[A-Z][^.]+\.\s+.+$', biblio_section, re.MULTILINE)
                citations['bibliography_entries'] = biblio_entries[:20]  # Prime 20 voci
        
        return citations


# Funzione di compatibilità per il sistema esistente
def process_pdf_file(file_path: str, filename: str) -> Dict[str, Any]:
    """Funzione wrapper per compatibilità con il sistema esistente"""
    processor = AdvancedPDFProcessor()
    return processor.process_pdf_file(file_path, filename)

