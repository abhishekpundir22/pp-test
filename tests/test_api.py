import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure the root project directory is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, matcher


class TestFAQApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        
        # Controlled seed dataset for deterministic assertions
        cls.sample_faq = [
            {
                "q": "Où trouver la liste des fournisseurs?",
                "a": "<p>La liste est disponible sur l'intranet Achats.</p>",
                "index": "1"
            },
            {
                "q": "Comment enregistrer une demande d'achat?",
                "a": "<p>Consultez le guide DA dans l'onglet documentation.</p>",
                "index": "2"
            },
            {
                "q": "Quelle est la date de création du BIL?",
                "a": "<p>Le BIL a été créé en 2018.</p>",
                "index": "3"
            }
        ]
        matcher.fit(cls.sample_faq)

    def test_search_relevant_query(self):
        """User wording should resolve to the closest question and return the answer."""
        response = self.client.get("/search?query=Ou est la liste des fournisseurs")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["match_found"])
        self.assertEqual(data["question"], "Où trouver la liste des fournisseurs?")
        self.assertIn("l'intranet Achats", data["answer"])
        self.assertGreater(data["score"], 0.4)

    def test_search_out_of_scope_query(self):
        """Unrelated queries should fall below the threshold and return no match."""
        response = self.client.get("/search?query=recette tarte aux pommes&threshold=0.3")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data["match_found"])
        self.assertIsNone(data["question"])
        self.assertIsNone(data["answer"])

    def test_search_empty_query_validation(self):
        """Blank queries should return a 400 validation error."""
        response = self.client.get("/search?query=   ")
        self.assertEqual(response.status_code, 400)

    def test_dynamic_indexing(self):
        """New documents added via /index/ should be searchable immediately."""
        payload = {
            "questions": [
                {
                    "qid": 42,
                    "question": "Comment réinitialiser mon mot de passe?",
                    "answer": "<p>Rendez-vous sur la page login et cliquez sur mot de passe oublié.</p>"
                }
            ]
        }
        res_index = self.client.post("/index/", json=payload)
        self.assertEqual(res_index.status_code, 200)
        self.assertGreaterEqual(res_index.json()["total_documents"], 4)

        # Search for the newly added item
        res_search = self.client.get("/search?query=mot de passe oublié")
        self.assertEqual(res_search.status_code, 200)
        
        data = res_search.json()
        self.assertTrue(data["match_found"])
        self.assertEqual(data["question"], "Comment réinitialiser mon mot de passe?")
        self.assertIn("Rendez-vous sur la page login", data["answer"])


if __name__ == "__main__":
    unittest.main()