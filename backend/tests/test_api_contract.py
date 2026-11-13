# -*- coding: utf-8 -*-
"""
Tests de non-régression du contrat d'API du Moteur de Rédaction Magique.

Ces tests ne font AUCUN appel réseau : le moteur de recherche est remplacé par
un double qui renvoie la structure réellement produite par
`MultiSourceSearchEngine.search()`.

Exécution :
    cd backend && python -m unittest discover -s tests -v
"""

import os
import sys
import unittest
from unittest.mock import patch

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import de l'application Flask (ne doit jamais lever, même sans OPENAI_API_KEY)
from src.main import app  # noqa: E402


class SearchContractTests(unittest.TestCase):
    """Le frontend attend `data.results` sous forme de LISTE de documents."""

    def setUp(self):
        self.client = app.test_client()

    def test_search_returns_flat_results_list(self):
        payload = {
            'success': True,
            'query': 'Don Bosco',
            'filters': {'sources': ['corpus_salesiano']},
            'results': [
                {
                    'title': 'Il Sistema Preventivo',
                    'source': 'Corpus Salesiano',
                    'type': 'institutional_source',
                    'abstract': 'La ragione, la religione, l amorevolezza.',
                    'url': 'https://salesian.online/exemple',
                    'citations': 3,
                    'relevance_score': 92,
                }
            ],
            'suggestions': [{'type': 'critical_source', 'text': '...'}],
            'stats': {'engines_queried': 3, 'engines_succeeded': 1},
        }

        with patch('src.multi_source_search.MultiSourceSearchEngine') as engine_cls:
            engine_cls.return_value.search.return_value = payload
            response = self.client.post('/api/search', json={'query': 'Don Bosco'})

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertTrue(data['success'])
        self.assertIsInstance(data['results'], list)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Il Sistema Preventivo')
        self.assertEqual(data['results'][0]['relevance_score'], 92)
        self.assertEqual(len(data['suggestions']), 1)
        self.assertIn('engines_queried', data['stats'])

    def test_search_without_results_still_returns_list(self):
        payload = {
            'success': True,
            'query': 'sujet inconnu',
            'results': [],
            'suggestions': [],
            'stats': {'engines_queried': 92, 'engines_succeeded': 0},
        }

        with patch('src.multi_source_search.MultiSourceSearchEngine') as engine_cls:
            engine_cls.return_value.search.return_value = payload
            response = self.client.post('/api/search', json={'query': 'sujet inconnu'})

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['results'], [])
        self.assertEqual(data['count'], 0)

    def test_search_requires_query(self):
        response = self.client.post('/api/search', json={})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()['success'])

    def test_engine_error_is_reported(self):
        payload = {'success': False, 'error': 'boom', 'query': 'x'}

        with patch('src.multi_source_search.MultiSourceSearchEngine') as engine_cls:
            engine_cls.return_value.search.return_value = payload
            response = self.client.post('/api/search', json={'query': 'x'})

        self.assertEqual(response.status_code, 502)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['results'], [])


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_no_duplicate_rules(self):
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        self.assertEqual(len(rules), len(set(rules)), f'Routes dupliquées: {rules}')

    def test_languages_endpoint(self):
        response = self.client.get('/api/languages')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        codes = [lang['code'] for lang in data['languages']]
        self.assertEqual(codes, ['it', 'fr', 'en', 'es', 'pt'])
        self.assertEqual(data['default_language'], 'it')

    def test_detect_language(self):
        response = self.client.post(
            '/api/languages/detect',
            json={'text': 'Le système préventif de Don Bosco et l éducation'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['language'], 'fr')

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'healthy')


if __name__ == '__main__':
    unittest.main()
