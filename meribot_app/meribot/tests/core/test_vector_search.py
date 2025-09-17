import sys
import os
# Añadir la raíz del proyecto al sys.path para permitir imports absolutos
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
meribot_app_path = os.path.join(project_root, 'meribot_app')
if meribot_app_path not in sys.path:
    sys.path.insert(0, meribot_app_path)
import unittest
from unittest.mock import MagicMock, patch
from meribot.core.vector_search import ChromaDBConnector

class TestChromaDBConnector(unittest.TestCase):
    def setUp(self):
        # Mockear chromadb y su Client
        patcher = patch('meribot.core.vector_search.chromadb')
        self.addCleanup(patcher.stop)
        self.mock_chromadb = patcher.start()
        self.mock_client = MagicMock()
        self.mock_chromadb.Client.return_value = self.mock_client
        self.connector = ChromaDBConnector()

    def test_get_collection(self):
        self.mock_client.get_or_create_collection.return_value = 'mock_collection'
        col = self.connector.get_collection('test')
        self.assertEqual(col, 'mock_collection')
        self.mock_client.get_or_create_collection.assert_called_with('test')

    def test_semantic_search_returns_hits(self):
        mock_collection = MagicMock()
        self.connector.get_collection = MagicMock(return_value=mock_collection)
        mock_collection.query.return_value = {
            'ids': [['id1', 'id2']],
            'documents': [['doc1', 'doc2']],
            'distances': [[0.1, 0.2]],
            'metadatas': [[{'fuente': 'url1'}, {'fuente': 'url2'}]]
        }
        hits = self.connector.semantic_search('test', [0.1, 0.2], top_k=2, where={'fuente': 'url1'})
        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0]['id'], 'id1')
        self.assertEqual(hits[0]['metadatas']['fuente'], 'url1')
        self.assertEqual(hits[1]['document'], 'doc2')

    def test_semantic_search_empty(self):
        mock_collection = MagicMock()
        self.connector.get_collection = MagicMock(return_value=mock_collection)
        mock_collection.query.return_value = {
            'ids': [[]],
            'documents': [[]],
            'distances': [[]],
            'metadatas': [[]]
        }
        hits = self.connector.semantic_search('test', [0.1, 0.2], top_k=2)
        self.assertEqual(hits, [])

if __name__ == '__main__':
    unittest.main()
