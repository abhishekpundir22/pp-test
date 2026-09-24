import unittest
from fastapi.testclient import TestClient
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, matcher


class TestFAQApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Seed questions for controlled testing
        cls.test_questions = [
            "Quel est le nom de l'entreprise Corcentric?",
            "Quelle est la date de création du BIL?",
            "Comment enregistrer une demande d'achat?",
            "Où trouver la liste des fournisseurs?"
        ]
        matcher.fit(cls.test_questions)

    def test_search_exact_match(self):
        response = self.client.get("/search?query=Ou est la liste des fournisseurs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["match"], "Où trouver la liste des fournisseurs?")
        self.assertGreater(data["score"], 0.5)

    def test_search_below_threshold(self):
        response = self.client.get("/search?query=Recette tarte aux pommes&threshold=0.5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["match"])

    def test_index_new_question(self):
        payload = {
            "questions": [
                {"qid": 101, "question": "Comment réinitialiser mon mot de passe?"}
            ]
        }
        res_post = self.client.post("/index/", json=payload)
        self.assertEqual(res_post.status_code, 200)

        res_search = self.client.get("/search?query=mot de passe oublié")
        self.assertEqual(res_search.status_code, 200)
        self.assertEqual(res_search.json()["match"], "Comment réinitialiser mon mot de passe?")

    def test_search_empty_query(self):
        response = self.client.get("/search?query=   ")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()