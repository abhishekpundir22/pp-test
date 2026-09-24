# NOTES.md

## What I Did

* **Exploration and Code Diagnostics (`2-FAQ.ipynb`)**:
  * Identified input dimension bugs in `cv.transform()` where single queries were passed directly as raw strings instead of an iterable collection of strings[cite: 4].
  * Replaced the manual iterative loop over question dot products with vectorized matrix multiplication over the entire corpus[cite: 1, 4].
  * Upgraded the text processing pipeline from `CountVectorizer` to `TfidfVectorizer(strip_accents="unicode", stop_words=...)` with French stop words to prevent common filler words and accent differences from biasing matches[cite: 4].
  * Implemented cosine similarity scoring and a minimum similarity threshold cutoff to avoid returning false-positive answers for irrelevant user inputs[cite: 4].

* **FastAPI Service Refactoring (`app/main.py` & `app/matcher.py`)**:
  * Extracted the indexing and similarity matching logic into an isolated, reusable `FAQMatcher` class to keep business logic separate from API endpoints[cite: 4, 5].
  * Configured a FastAPI `@app.on_event("startup")` handler to automatically parse questions from `data/faq.json` into memory on server boot[cite: 2, 5].
  * Updated the `/search` endpoint to accept query strings, execute cosine similarity search against the corpus, and return the best-matching question along with its score[cite: 1, 4, 5].
  * Maintained dynamic updates via `/index/` so that new questions can be added and indexed at runtime[cite: 1].

* **Testing & Validation (`tests/test_api.py`)**:
  * Implemented automated integration tests using `fastapi.testclient.TestClient` to validate API responses[cite: 3].
  * Tested scenarios including exact/near matches, queries below threshold, empty string queries, and re-indexing via `/index/`[cite: 1, 3, 4, 5].

---

## Anything I Got Stuck On

* **Vocabulary Re-fitting on Dynamic Ingestion**:
  * When questions are added via `/index/`, calling `.fit()` directly on only the incoming payload drops previously learned terms from the vocabulary[cite: 1].
  * Solved this by persisting accumulated corpus questions in memory within `FAQMatcher` and refitting against the combined corpus on update[cite: 1, 4].
* **Relative Path Resolution for Datasets**:
  * Launching tests from the `tests/` directory versus running the API from the root directory caused relative lookups for `data/faq.json` to fail intermittently[cite: 5, 6].
  * Resolved this by checking relative path candidates based on `__file__`.

---

## What I Would Do Next

* **Dense Semantic Embeddings**:
  * TF-IDF relies solely on keyword overlap and misses intent when users use synonyms not present in the FAQ[cite: 4]. Transitioning to a pretrained multilingual sentence-transformer (e.g., `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) would improve semantic matching.
* **Return Full Answers & Metadata**:
  * Extend the response model to return the actual answer text (`"a"`) and document index from `faq.json` rather than only the matched question title[cite: 2, 4].
* **Modern FastAPI Lifespan Handler**:
  * Migrate from the legacy `@app.on_event("startup")` pattern to FastAPI’s modern `lifespan` context manager[cite: 5].
* **Vector Store Persistence**:
  * For larger document collections scaling beyond hundreds of entries, replace in-memory matrix computations with dedicated vector search indices (such as FAISS, Chroma, or Qdrant).