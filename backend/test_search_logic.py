
import sys
import os
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Aggiungi la directory corrente al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.corpus_salesien import CORPUS_SALESIEN, get_suggestions_for_text
    from src.semantic_engine import SemanticEngine
    
    print("\n=== TEST DIAGNOSTICO RICERCA ===\n")
    
    # 1. Verifica contenuto Corpus
    print(f"1. Verifica Corpus:")
    if 'costituzioni' in CORPUS_SALESIEN:
        docs = CORPUS_SALESIEN['costituzioni']
        print(f"   - Categoria 'costituzioni' trovata: {len(docs)} documenti")
        found_art_50 = False
        for doc in docs:
            if "Art. 50" in doc['title']:
                print(f"   - Trovato: {doc['title']} ({doc['id']})")
                found_art_50 = True
        if not found_art_50:
            print("   - ERRORE: Art. 50 non trovato nel Corpus!")
    else:
        print("   - ERRORE: Categoria 'costituzioni' mancante!")

    # 2. Test Motore Semantico
    print(f"\n2. Test Motore Semantico:")
    semantic = SemanticEngine()
    query = "Vivre et travailler ensemble"
    expanded = semantic.expand_query(query)
    print(f"   - Query: '{query}'")
    print(f"   - Espansione: {expanded}")
    
    if "vita comune" in expanded or "living together" in expanded:
        print("   - OK: Espansione multilingue funzionante")
    else:
        print("   - ERRORE: Espansione fallita")

    # 3. Test Ricerca Completa
    print(f"\n3. Test Ricerca Completa (get_suggestions_for_text):")
    results = get_suggestions_for_text(query)
    print(f"   - Risultati trovati: {len(results)}")
    
    for i, res in enumerate(results):
        print(f"   - Risultato {i+1}: {res['title']} (Score: {res['confidence']})")
        if "Art. 50" in res['title']:
            print("     -> SUCCESSO: Articolo 50 trovato!")

except Exception as e:
    print(f"\n❌ ERRORE CRITICO DURANTE IL TEST: {str(e)}")
    import traceback
    traceback.print_exc()
