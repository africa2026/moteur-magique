# -*- coding: utf-8 -*-
"""
Corpus Salesiano - Modulo di gestione testi e suggerimenti
"""

CORPUS_SALESIEN = {
    "costituzioni": [
        {
            "id": "CONST-050-FR",
            "title": "Art. 50 - Vivre et travailler ensemble",
            "content": "Vivre et travailler ensemble est pour nous salésiens une exigence fondamentale et une voie sûre pour réaliser notre vocation. C'est pourquoi nous nous réunissons en communautés, où nous nous aimons jusqu'à tout partager dans un esprit de famille et où nous construisons la communion des cœurs. Dans la communauté se reflète le mystère de la Trinité, on fait l'expérience de la présence de Dieu et on devient signe prophétique de fraternité pour les jeunes.",
            "source": "Constitutions SDB, Art. 50"
        },
        {
            "id": "CONST-050-IT",
            "title": "Art. 50 - Vivere e lavorare insieme",
            "content": "Vivere e lavorare insieme è per noi salesiani un'esigenza fondamentale e una via sicura per realizzare la nostra vocazione. Per questo ci riuniamo in comunità, nelle quali ci amiamo fino a condividere tutto in spirito di famiglia e costruiamo la comunione dei cuori. Nella comunità si riflette il mistero della Trinità, si fa esperienza della presenza di Dio e si diventa segno profetico di fraternità per i giovani.",
            "source": "Costituzioni SDB, Art. 50"
        },
        {
            "id": "CONST-050-EN",
            "title": "Art. 50 - Living and working together",
            "content": "Living and working together is for us Salesians a fundamental requirement and a sure way of fulfilling our vocation. That is why we come together in communities, where our love for each other leads us to share everything in a family spirit, and so create communion of hearts. The community reflects the mystery of the Trinity; in it we find a response to the deep aspirations of the heart, and become for the young signs of love and unity.",
            "source": "SDB Constitutions, Art. 50"
        },
        {
            "id": "CONST-050-ES",
            "title": "Art. 50 - Vivir y trabajar juntos",
            "content": "Vivir y trabajar juntos es para nosotros, salesianos, una exigencia fundamental y un camino seguro para realizar nuestra vocación. Por esto nos reunimos en comunidades, en las cuales nos amamos hasta compartirlo todo en espíritu de familia y construimos la comunión de los corazones. En la comunidad se refleja el misterio de la Trinidad, se hace experiencia de la presencia de Dios y nos convertimos en signo profético de fraternidad para los jóvenes.",
            "source": "Constituciones SDB, Art. 50"
        },
        {
            "id": "CONST-050-PT",
            "title": "Art. 50 - Viver e trabalhar juntos",
            "content": "Viver e trabalhar juntos é para nós, salesianos, uma exigência fundamental e um caminho seguro para realizar a nossa vocação. Por isso nos reunimos em comunidades, nas quais nos amamos a ponto de partilhar tudo em espírito de família e construímos a comunhão dos corações. Na comunidade reflete-se o mistério da Trindade, faz-se a experiência da presença de Deus e tornamo-nos sinal profético de fraternidade para os jovens.",
            "source": "Constituições SDB, Art. 50"
        },
        {
            "id": "CONST-049-FR",
            "title": "Art. 49 - Signification de la vie commune",
            "content": "La vie commune est un élément essentiel de notre mission. Don Bosco a voulu que la charité pastorale soit vécue et témoignée sous une forme communautaire. La communauté salésienne n'est pas seulement un groupe de travail, mais une famille de frères qui vivent ensemble pour servir les jeunes.",
            "source": "Constitutions SDB, Art. 49"
        },
        {
            "id": "CONST-049-IT",
            "title": "Art. 49 - Significato della vita comune",
            "content": "La vita comune è elemento essenziale della nostra missione. Don Bosco ha voluto che la carità pastorale fosse vissuta e testimoniata in forma comunitaria. La comunità salesiana non è solo un gruppo di lavoro, ma una famiglia di fratelli che vivono insieme per servire i giovani.",
            "source": "Costituzioni SDB, Art. 49"
        },
        {
            "id": "CONST-038-FR",
            "title": "Art. 38 - Le Système Préventif",
            "content": "Le Système Préventif repose entièrement sur la raison, la religion et l'affection. Il ne fait pas appel aux contraintes, mais aux ressources de l'intelligence, du cœur et du désir de Dieu que tout homme porte au plus profond de lui-même. Il associe dans une unique expérience de vie éducateurs et jeunes, dans un climat de famille, de confiance et de dialogue.",
            "source": "Constitutions SDB, Art. 38"
        },
        {
            "id": "CONST-038-IT",
            "title": "Art. 38 - Il Sistema Preventivo",
            "content": "Il Sistema Preventivo si basa interamente sulla ragione, la religione e l'amorevolezza. Non fa appello a costrizioni, ma alle risorse dell'intelligenza, del cuore e del desiderio di Dio, che ogni uomo porta nel profondo di se stesso. Associa in un'unica esperienza di vita educatori e giovani, in un clima di famiglia, di fiducia e di dialogo.",
            "source": "Costituzioni SDB, Art. 38"
        },
        {
            "id": "CONST-002",
            "title": "Art. 2 - La missione salesiana",
            "content": "Noi, salesiani di Don Bosco, siamo una comunità di battezzati che, docili alla voce dello Spirito, intendono realizzare in una specifica forma di vita religiosa il progetto apostolico del Fondatore: essere nella Chiesa segni e portatori dell'amore di Dio ai giovani, specialmente ai più poveri.",
            "source": "Costituzioni SDB, Art. 2"
        }
    ],
    "don_bosco": [
        {
            "id": "DB-001",
            "title": "Lettera da Roma 1884",
            "content": "Non basta amare i giovani, bisogna che essi si accorgano di essere amati. Chi sa di essere amato ama, e chi ama ottiene tutto, specialmente dai giovani.",
            "source": "Lettere di Don Bosco"
        }
    ]
}

def get_suggestions_for_text(text):
    """
    Genera suggerimenti basati sul testo in input cercando nel corpus
    """
    suggestions = []
    text_lower = text.lower()
    
    # Ricerca semplice per parole chiave
    keywords = text_lower.split()
    
    for category, docs in CORPUS_SALESIEN.items():
        for doc in docs:
            score = 0
            doc_content_lower = doc['content'].lower()
            
            # Bonus per corrispondenza esatta della frase
            if text_lower in doc_content_lower:
                score += 10
            
            for keyword in keywords:
                if len(keyword) > 3 and keyword in doc_content_lower:
                    score += 1
            
            if score > 0:
                # Calcolo confidenza migliorato
                confidence = min(score * 20, 99)
                if text_lower in doc_content_lower:
                    confidence = 99  # Quasi certezza per frase esatta
                
                suggestions.append({
                    "title": doc['title'],
                    "content": doc['content'],
                    "source": doc['source'],
                    "confidence": confidence
                })
    
    # Ordina per confidenza
    suggestions.sort(key=lambda x: x['confidence'], reverse=True)
    return suggestions
