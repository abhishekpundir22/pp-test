import unicodedata
from typing import Any, Dict, List, Optional, Tuple
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_french_stopwords() -> List[str]:
    """
    Retrieves French stop words from NLTK, ensuring automatic download if missing.
    Also strips accents so stop words align with TfidfVectorizer's strip_accents='unicode'.
    """
    try:
        sw = stopwords.words("french")
    except LookupError:
        nltk.download("stopwords", quiet=True)
        sw = stopwords.words("french")

    # When strip_accents='unicode' is enabled, tokens like 'où' become 'ou'.
    # Stripping accents on the stop words list ensures both forms are properly filtered out.
    normalized = {
        unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode("utf-8")
        for word in sw
    }
    return list(normalized | set(sw))


class FAQMatcher:
    """Indexes FAQ entries and retrieves the best match using TF-IDF and Cosine Similarity."""

    def __init__(self, stop_words: Optional[List[str]] = None):
        self.stop_words = stop_words if stop_words is not None else get_french_stopwords()
        self.vectorizer = TfidfVectorizer(strip_accents="unicode", stop_words=self.stop_words)
        self.documents: List[Dict[str, Any]] = []
        self.matrix = None

    def fit(self, documents: List[Dict[str, Any]]):
        """
        Accepts a list of FAQ dictionaries, each containing at least 'q' and 'a'.
        Vectorizes the questions and keeps the metadata in sync.
        """
        self.documents = list(documents)
        questions = [doc["q"] for doc in self.documents]

        if questions:
            self.matrix = self.vectorizer.fit_transform(questions)
        else:
            self.matrix = None

    def add_documents(self, new_docs: List[Dict[str, Any]]):
        """Appends new FAQ documents and updates the TF-IDF vocabulary matrix."""
        existing_qs = {doc["q"] for doc in self.documents}
        unique_new = [d for d in new_docs if d["q"] not in existing_qs]
        self.fit(self.documents + unique_new)

    def match(self, query: str, threshold: float = 0.2) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Calculates cosine similarity between the query and all indexed questions.
        Returns the top document dict and its score, or (None, score) if below threshold.
        """
        if not self.documents or self.matrix is None:
            return None, 0.0

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()

        best_idx = scores.argmax()
        best_score = float(scores[best_idx])

        if best_score < threshold:
            return None, best_score

        return self.documents[best_idx], best_score