# -*- coding: utf-8 -*-
"""
Sistema di Gestione Bibliografica Avanzato
Moteur de Rédaction Magique - Rev. Alphonse Owoudou
Import .ris, Zotero, EndNote, BibTeX e gestione bibliografie complete
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import logging
import os
import json
import re
from typing import List, Dict, Any, Optional
import tempfile
import zipfile

logger = logging.getLogger(__name__)

# Blueprint per gestione bibliografica
bibliography_bp = Blueprint('bibliography', __name__)

class BibliographyManager:
    """
    Gestore bibliografico professionale con:
    - Import file .ris (Zotero, EndNote)
    - Import BibTeX
    - Estrazione da PDF/TXT/DOCX
    - Export in formati multipli
    - Gestione metadati avanzati
    """
    
    def __init__(self):
        self.supported_formats = ['.ris', '.bib', '.txt', '.pdf', '.docx']
        self.bibliography_store = {}  # Storage bibliografie
        
    def import_ris_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Import file .ris da Zotero/EndNote"""
        
        try:
            import rispy
            
            with open(file_path, 'r', encoding='utf-8') as f:
                entries = rispy.load(f)
            
            processed_entries = []
            
            for entry in entries:
                processed_entry = self._process_ris_entry(entry)
                processed_entries.append(processed_entry)
            
            bibliography_id = f"ris_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            bibliography_data = {
                'id': bibliography_id,
                'source_file': filename,
                'source_type': 'ris',
                'import_date': datetime.now().isoformat(),
                'total_entries': len(processed_entries),
                'entries': processed_entries,
                'metadata': {
                    'original_format': 'RIS',
                    'source_software': self._detect_ris_source(entries),
                    'encoding': 'utf-8'
                }
            }
            
            self.bibliography_store[bibliography_id] = bibliography_data
            
            logger.info(f"✅ Import RIS completato: {len(processed_entries)} voci da {filename}")
            
            return {
                'success': True,
                'bibliography_id': bibliography_id,
                'entries_imported': len(processed_entries),
                'entries': processed_entries[:10],  # Prime 10 per preview
                'total_entries': len(processed_entries),
                'source_software': bibliography_data['metadata']['source_software']
            }
            
        except Exception as e:
            logger.error(f"Errore import RIS: {str(e)}")
            return {
                'success': False,
                'error': f'Errore import file RIS: {str(e)}'
            }
    
    def import_bibtex_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Import file BibTeX"""
        
        try:
            import bibtexparser
            
            with open(file_path, 'r', encoding='utf-8') as f:
                bib_database = bibtexparser.load(f)
            
            processed_entries = []
            
            for entry in bib_database.entries:
                processed_entry = self._process_bibtex_entry(entry)
                processed_entries.append(processed_entry)
            
            bibliography_id = f"bib_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            bibliography_data = {
                'id': bibliography_id,
                'source_file': filename,
                'source_type': 'bibtex',
                'import_date': datetime.now().isoformat(),
                'total_entries': len(processed_entries),
                'entries': processed_entries,
                'metadata': {
                    'original_format': 'BibTeX',
                    'encoding': 'utf-8'
                }
            }
            
            self.bibliography_store[bibliography_id] = bibliography_data
            
            logger.info(f"✅ Import BibTeX completato: {len(processed_entries)} voci da {filename}")
            
            return {
                'success': True,
                'bibliography_id': bibliography_id,
                'entries_imported': len(processed_entries),
                'entries': processed_entries[:10],
                'total_entries': len(processed_entries)
            }
            
        except Exception as e:
            logger.error(f"Errore import BibTeX: {str(e)}")
            return {
                'success': False,
                'error': f'Errore import file BibTeX: {str(e)}'
            }
    
    def extract_bibliography_from_text(self, text: str, source_name: str) -> Dict[str, Any]:
        """Estrazione bibliografia da testo (PDF/TXT/DOCX)"""
        
        try:
            # Pattern per diversi stili di citazione
            citation_patterns = [
                # Stile APA: Autore, A. (Anno). Titolo. Editore.
                r'([A-Z][a-z]+(?:,\s+[A-Z]\.)+)\s+\((\d{4})\)\.\s+([^.]+)\.\s+([^.]+)\.',
                
                # Stile Chicago: Autore, "Titolo," Rivista Volume (Anno): pagine.
                r'([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)*),\s+"([^"]+),"\s+([^,]+)\s+(\d+)\s+\((\d{4})\):\s+(\d+-\d+)',
                
                # Stile MLA: Autore. "Titolo." Rivista, vol. X, no. Y, Anno, pp. Z-W.
                r'([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)*)\.\s+"([^"]+)\."\s+([^,]+),\s+vol\.\s+(\d+),\s+no\.\s+(\d+),\s+(\d{4}),\s+pp\.\s+(\d+-\d+)',
                
                # Pattern generico per libri
                r'([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)*)\s+\((\d{4})\)\.\s+([^.]+)\.\s+([^:]+):\s+([^.]+)\.',
                
                # Pattern per articoli web
                r'([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)*)\.\s+"([^"]+)\."\s+([^,]+),\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
            ]
            
            extracted_entries = []
            
            # Cerca sezione bibliografia
            text_lower = text.lower()
            biblio_keywords = ['bibliografia', 'bibliographie', 'references', 'sources', 'works cited']
            
            biblio_start = -1
            for keyword in biblio_keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    biblio_start = pos
                    break
            
            if biblio_start != -1:
                # Estrai sezione bibliografia
                biblio_section = text[biblio_start:biblio_start + 20000]  # Primi 20k caratteri
            else:
                # Usa tutto il testo
                biblio_section = text
            
            # Applica pattern di estrazione
            for i, pattern in enumerate(citation_patterns):
                matches = re.findall(pattern, biblio_section, re.MULTILINE)
                
                for match in matches:
                    entry = self._create_entry_from_pattern(match, i)
                    if entry:
                        extracted_entries.append(entry)
            
            # Rimuovi duplicati
            unique_entries = self._remove_duplicate_entries(extracted_entries)
            
            bibliography_id = f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            bibliography_data = {
                'id': bibliography_id,
                'source_file': source_name,
                'source_type': 'extracted',
                'import_date': datetime.now().isoformat(),
                'total_entries': len(unique_entries),
                'entries': unique_entries,
                'metadata': {
                    'extraction_method': 'pattern_matching',
                    'patterns_used': len(citation_patterns),
                    'source_length': len(text)
                }
            }
            
            self.bibliography_store[bibliography_id] = bibliography_data
            
            logger.info(f"✅ Estrazione bibliografia completata: {len(unique_entries)} voci da {source_name}")
            
            return {
                'success': True,
                'bibliography_id': bibliography_id,
                'entries_extracted': len(unique_entries),
                'entries': unique_entries[:10],
                'total_entries': len(unique_entries)
            }
            
        except Exception as e:
            logger.error(f"Errore estrazione bibliografia: {str(e)}")
            return {
                'success': False,
                'error': f'Errore estrazione bibliografia: {str(e)}'
            }
    
    def export_bibliography(self, bibliography_id: str, format_type: str) -> Dict[str, Any]:
        """Export bibliografia in formato specificato"""
        
        if bibliography_id not in self.bibliography_store:
            return {
                'success': False,
                'error': 'Bibliografia non trovata'
            }
        
        bibliography = self.bibliography_store[bibliography_id]
        entries = bibliography['entries']
        
        try:
            if format_type == 'ris':
                content = self._export_to_ris(entries)
                filename = f"bibliografia_{bibliography_id}.ris"
            elif format_type == 'bibtex':
                content = self._export_to_bibtex(entries)
                filename = f"bibliografia_{bibliography_id}.bib"
            elif format_type == 'apa':
                content = self._export_to_apa(entries)
                filename = f"bibliografia_{bibliography_id}_apa.txt"
            elif format_type == 'chicago':
                content = self._export_to_chicago(entries)
                filename = f"bibliografia_{bibliography_id}_chicago.txt"
            elif format_type == 'mla':
                content = self._export_to_mla(entries)
                filename = f"bibliografia_{bibliography_id}_mla.txt"
            else:
                return {
                    'success': False,
                    'error': f'Formato {format_type} non supportato'
                }
            
            # Salva file temporaneo
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'format': format_type,
                'entries_count': len(entries)
            }
            
        except Exception as e:
            logger.error(f"Errore export bibliografia: {str(e)}")
            return {
                'success': False,
                'error': f'Errore export: {str(e)}'
            }
    
    def _process_ris_entry(self, entry: Dict) -> Dict[str, Any]:
        """Processa voce RIS in formato standardizzato"""
        
        processed = {
            'id': entry.get('id', f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'type': entry.get('type_of_reference', 'JOUR'),
            'title': entry.get('title', ''),
            'authors': entry.get('authors', []),
            'year': entry.get('publication_year', ''),
            'journal': entry.get('journal_name', ''),
            'volume': entry.get('volume', ''),
            'issue': entry.get('number', ''),
            'pages': entry.get('start_page', '') + '-' + entry.get('end_page', '') if entry.get('start_page') else '',
            'publisher': entry.get('publisher', ''),
            'doi': entry.get('doi', ''),
            'url': entry.get('url', ''),
            'abstract': entry.get('abstract', ''),
            'keywords': entry.get('keywords', []),
            'notes': entry.get('notes', ''),
            'language': entry.get('language', ''),
            'original_entry': entry
        }
        
        # Pulisci campi vuoti
        processed = {k: v for k, v in processed.items() if v}
        
        return processed
    
    def _process_bibtex_entry(self, entry: Dict) -> Dict[str, Any]:
        """Processa voce BibTeX in formato standardizzato"""
        
        processed = {
            'id': entry.get('ID', f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'type': entry.get('ENTRYTYPE', 'article'),
            'title': entry.get('title', ''),
            'authors': [entry.get('author', '')],
            'year': entry.get('year', ''),
            'journal': entry.get('journal', ''),
            'volume': entry.get('volume', ''),
            'issue': entry.get('number', ''),
            'pages': entry.get('pages', ''),
            'publisher': entry.get('publisher', ''),
            'doi': entry.get('doi', ''),
            'url': entry.get('url', ''),
            'abstract': entry.get('abstract', ''),
            'keywords': entry.get('keywords', '').split(',') if entry.get('keywords') else [],
            'notes': entry.get('note', ''),
            'original_entry': entry
        }
        
        # Pulisci campi vuoti
        processed = {k: v for k, v in processed.items() if v}
        
        return processed
    
    def _detect_ris_source(self, entries: List[Dict]) -> str:
        """Rileva software sorgente del file RIS"""
        
        if not entries:
            return 'unknown'
        
        # Controlla pattern tipici
        first_entry = entries[0]
        
        if 'zotero' in str(first_entry).lower():
            return 'Zotero'
        elif 'endnote' in str(first_entry).lower():
            return 'EndNote'
        elif 'mendeley' in str(first_entry).lower():
            return 'Mendeley'
        else:
            return 'Generic RIS'
    
    def _create_entry_from_pattern(self, match: tuple, pattern_index: int) -> Optional[Dict]:
        """Crea voce bibliografica da pattern match"""
        
        if not match:
            return None
        
        entry = {
            'id': f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'extraction_pattern': pattern_index
        }
        
        # Pattern 0: APA style
        if pattern_index == 0 and len(match) >= 4:
            entry.update({
                'authors': [match[0]],
                'year': match[1],
                'title': match[2],
                'publisher': match[3],
                'type': 'book'
            })
        
        # Pattern 1: Chicago style
        elif pattern_index == 1 and len(match) >= 6:
            entry.update({
                'authors': [match[0]],
                'title': match[1],
                'journal': match[2],
                'volume': match[3],
                'year': match[4],
                'pages': match[5],
                'type': 'article'
            })
        
        # Pattern 2: MLA style
        elif pattern_index == 2 and len(match) >= 7:
            entry.update({
                'authors': [match[0]],
                'title': match[1],
                'journal': match[2],
                'volume': match[3],
                'issue': match[4],
                'year': match[5],
                'pages': match[6],
                'type': 'article'
            })
        
        # Altri pattern...
        else:
            return None
        
        return entry
    
    def _remove_duplicate_entries(self, entries: List[Dict]) -> List[Dict]:
        """Rimuovi voci duplicate"""
        
        unique_entries = []
        seen_titles = set()
        
        for entry in entries:
            title = entry.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_entries.append(entry)
        
        return unique_entries
    
    def _export_to_ris(self, entries: List[Dict]) -> str:
        """Export in formato RIS"""
        
        ris_content = []
        
        for entry in entries:
            ris_content.append("TY  - JOUR")  # Default type
            
            if entry.get('title'):
                ris_content.append(f"TI  - {entry['title']}")
            
            for author in entry.get('authors', []):
                if author:
                    ris_content.append(f"AU  - {author}")
            
            if entry.get('year'):
                ris_content.append(f"PY  - {entry['year']}")
            
            if entry.get('journal'):
                ris_content.append(f"JO  - {entry['journal']}")
            
            if entry.get('volume'):
                ris_content.append(f"VL  - {entry['volume']}")
            
            if entry.get('issue'):
                ris_content.append(f"IS  - {entry['issue']}")
            
            if entry.get('pages'):
                ris_content.append(f"SP  - {entry['pages']}")
            
            if entry.get('doi'):
                ris_content.append(f"DO  - {entry['doi']}")
            
            if entry.get('url'):
                ris_content.append(f"UR  - {entry['url']}")
            
            ris_content.append("ER  - ")
            ris_content.append("")
        
        return "\n".join(ris_content)
    
    def _export_to_bibtex(self, entries: List[Dict]) -> str:
        """Export in formato BibTeX"""
        
        bibtex_content = []
        
        for entry in entries:
            entry_type = entry.get('type', 'article')
            entry_id = entry.get('id', 'unknown')
            
            bibtex_content.append(f"@{entry_type}{{{entry_id},")
            
            if entry.get('title'):
                bibtex_content.append(f"  title = {{{entry['title']}}},")
            
            if entry.get('authors'):
                authors_str = " and ".join(entry['authors'])
                bibtex_content.append(f"  author = {{{authors_str}}},")
            
            if entry.get('year'):
                bibtex_content.append(f"  year = {{{entry['year']}}},")
            
            if entry.get('journal'):
                bibtex_content.append(f"  journal = {{{entry['journal']}}},")
            
            if entry.get('volume'):
                bibtex_content.append(f"  volume = {{{entry['volume']}}},")
            
            if entry.get('pages'):
                bibtex_content.append(f"  pages = {{{entry['pages']}}},")
            
            if entry.get('doi'):
                bibtex_content.append(f"  doi = {{{entry['doi']}}},")
            
            bibtex_content.append("}")
            bibtex_content.append("")
        
        return "\n".join(bibtex_content)
    
    def _export_to_apa(self, entries: List[Dict]) -> str:
        """Export in stile APA"""
        
        apa_content = []
        
        for entry in entries:
            citation = []
            
            # Autori
            if entry.get('authors'):
                authors = entry['authors']
                if len(authors) == 1:
                    citation.append(authors[0])
                elif len(authors) == 2:
                    citation.append(f"{authors[0]} & {authors[1]}")
                else:
                    citation.append(f"{authors[0]} et al.")
            
            # Anno
            if entry.get('year'):
                citation.append(f"({entry['year']})")
            
            # Titolo
            if entry.get('title'):
                citation.append(f"{entry['title']}.")
            
            # Rivista/Publisher
            if entry.get('journal'):
                journal_part = entry['journal']
                if entry.get('volume'):
                    journal_part += f", {entry['volume']}"
                if entry.get('issue'):
                    journal_part += f"({entry['issue']})"
                if entry.get('pages'):
                    journal_part += f", {entry['pages']}"
                citation.append(f"{journal_part}.")
            elif entry.get('publisher'):
                citation.append(f"{entry['publisher']}.")
            
            # DOI/URL
            if entry.get('doi'):
                citation.append(f"https://doi.org/{entry['doi']}")
            elif entry.get('url'):
                citation.append(entry['url'])
            
            apa_content.append(" ".join(citation))
        
        return "\n\n".join(apa_content)
    
    def _export_to_chicago(self, entries: List[Dict]) -> str:
        """Export in stile Chicago"""
        
        chicago_content = []
        
        for entry in entries:
            citation = []
            
            # Autori (formato Chicago)
            if entry.get('authors'):
                authors = entry['authors']
                citation.append(f"{authors[0]}")
            
            # Titolo
            if entry.get('title'):
                citation.append(f'"{entry["title"]}"')
            
            # Rivista e dettagli
            if entry.get('journal'):
                journal_part = entry['journal']
                if entry.get('volume'):
                    journal_part += f" {entry['volume']}"
                if entry.get('year'):
                    journal_part += f" ({entry['year']})"
                if entry.get('pages'):
                    journal_part += f": {entry['pages']}"
                citation.append(f"{journal_part}.")
            
            chicago_content.append(", ".join(citation))
        
        return "\n\n".join(chicago_content)
    
    def _export_to_mla(self, entries: List[Dict]) -> str:
        """Export in stile MLA"""
        
        mla_content = []
        
        for entry in entries:
            citation = []
            
            # Autore (formato MLA)
            if entry.get('authors'):
                citation.append(f"{entry['authors'][0]}.")
            
            # Titolo
            if entry.get('title'):
                citation.append(f'"{entry["title"]}."')
            
            # Rivista e dettagli
            if entry.get('journal'):
                journal_part = entry['journal']
                if entry.get('volume'):
                    journal_part += f", vol. {entry['volume']}"
                if entry.get('issue'):
                    journal_part += f", no. {entry['issue']}"
                if entry.get('year'):
                    journal_part += f", {entry['year']}"
                if entry.get('pages'):
                    journal_part += f", pp. {entry['pages']}"
                citation.append(f"{journal_part}.")
            
            mla_content.append(" ".join(citation))
        
        return "\n\n".join(mla_content)


# Istanza globale del gestore bibliografico
biblio_manager = BibliographyManager()

@bibliography_bp.route('/api/bibliography/import-ris', methods=['POST'])
def import_ris():
    """Import file .ris"""
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nessun file fornito'
            }), 400
        
        file = request.files['file']
        
        if not file.filename.lower().endswith('.ris'):
            return jsonify({
                'success': False,
                'error': 'File deve essere in formato .ris'
            }), 400
        
        # Salva file temporaneo
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # Import
        result = biblio_manager.import_ris_file(file_path, file.filename)
        
        # Cleanup
        os.remove(file_path)
        os.rmdir(temp_dir)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore import RIS: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore import RIS: {str(e)}'
        }), 500

@bibliography_bp.route('/api/bibliography/import-bibtex', methods=['POST'])
def import_bibtex():
    """Import file BibTeX"""
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nessun file fornito'
            }), 400
        
        file = request.files['file']
        
        if not file.filename.lower().endswith('.bib'):
            return jsonify({
                'success': False,
                'error': 'File deve essere in formato .bib'
            }), 400
        
        # Salva file temporaneo
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # Import
        result = biblio_manager.import_bibtex_file(file_path, file.filename)
        
        # Cleanup
        os.remove(file_path)
        os.rmdir(temp_dir)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore import BibTeX: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore import BibTeX: {str(e)}'
        }), 500

@bibliography_bp.route('/api/bibliography/extract-from-text', methods=['POST'])
def extract_bibliography():
    """Estrai bibliografia da testo"""
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Testo richiesto'
            }), 400
        
        text = data['text']
        source_name = data.get('source_name', 'Testo fornito')
        
        result = biblio_manager.extract_bibliography_from_text(text, source_name)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore estrazione bibliografia: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore estrazione: {str(e)}'
        }), 500

@bibliography_bp.route('/api/bibliography/export/<bibliography_id>/<format_type>', methods=['GET'])
def export_bibliography(bibliography_id, format_type):
    """Export bibliografia in formato specificato"""
    
    try:
        result = biblio_manager.export_bibliography(bibliography_id, format_type)
        
        if result['success']:
            return send_file(
                result['file_path'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype='text/plain'
            )
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Errore export bibliografia: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore export: {str(e)}'
        }), 500

@bibliography_bp.route('/api/bibliography/list', methods=['GET'])
def list_bibliographies():
    """Lista tutte le bibliografie importate"""
    
    try:
        bibliographies = []
        
        for bib_id, bib_data in biblio_manager.bibliography_store.items():
            bibliographies.append({
                'id': bib_id,
                'source_file': bib_data['source_file'],
                'source_type': bib_data['source_type'],
                'import_date': bib_data['import_date'],
                'total_entries': bib_data['total_entries'],
                'metadata': bib_data.get('metadata', {})
            })
        
        # Ordina per data import
        bibliographies.sort(key=lambda x: x['import_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'bibliographies': bibliographies,
            'total_bibliographies': len(bibliographies)
        })
        
    except Exception as e:
        logger.error(f"Errore lista bibliografie: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore lista: {str(e)}'
        }), 500

@bibliography_bp.route('/api/bibliography/<bibliography_id>', methods=['GET'])
def get_bibliography(bibliography_id):
    """Ottieni dettagli bibliografia specifica"""
    
    try:
        if bibliography_id not in biblio_manager.bibliography_store:
            return jsonify({
                'success': False,
                'error': 'Bibliografia non trovata'
            }), 404
        
        bibliography = biblio_manager.bibliography_store[bibliography_id]
        
        return jsonify({
            'success': True,
            'bibliography': bibliography
        })
        
    except Exception as e:
        logger.error(f"Errore get bibliografia: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore recupero: {str(e)}'
        }), 500

