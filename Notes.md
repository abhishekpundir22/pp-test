# Notes & Technical Summary

## What I Did

### 1. Diagnosis & Vectorization Fixes (`2-FAQ.ipynb`)
- **Resolved dimension and type mismatches**: Fixed `cv.transform()` taking a bare string query instead of an iterable collection of strings.
- **Vectorized dot products**: Eliminated the row-by-row Python loop in favor of a single matrix-vector product (`Q @ q_vect.T`), computing similarity scores across the whole corpus in one operation.
- **Switched to TF-IDF & Cosine Similarity**: Replaced unweighted term frequencies (`CountVectorizer`) with `TfidfVectorizer(strip_accents="unicode")` and French stop words (via `nltk`). This stops generic filler words (like *est*, *la*, *comment*) from skewing results and makes matching invariant to question length.
- **Implemented a similarity cutoff**: Added a minimum score threshold so out-of-scope or random queries return a clean fallback rather than a misleading match.

### 2. Service Architecture & Startup Ingestion (`app/`)
- **Decoupled business logic**: Extracted the search and document storage logic into a dedicated `FAQMatcher` class (`app/matcher.py`), keeping `app/main.py` lean and focused on routing, validation, and serialization.
- **Preloaded FAQ data**: Implemented FastAPI's startup event to automatically parse and index all questions and HTML answers from `data/faq.json` into memory on boot.
- **Enriched search response**: Updated the `/search` endpoint to return the matched question, the corresponding answer HTML (`"a"`), and the similarity score.
- **Dynamic re-indexing**: Maintained the `/index/` endpoint to allow new questions and answers to be added to the corpus at runtime.

### 3. Automated Testing (`tests/test_api.py`)
- Built an integration test suite using FastAPI's `TestClient` covering:
  - Exact and close semantic queries matching the correct FAQ item and answer.
  - Out-of-scope queries properly falling below the threshold.
  - Validation handling for empty or whitespace-only inputs (400 Bad Request).
  - Dynamic index updates via `POST /index/` verifying that newly added entries are immediately retrievable.

---

## What I Got Stuck On & Trade-offs Made

- **Stop Word Accent Stripping**: 
  - Using `strip_accents="unicode"` converts words like *où* to *ou*. If the stop words list only contains *où*, the stripped query token *ou* bypasses filtering. I resolved this by normalizing the NLTK French stop words to include both accented and unaccented versions.
- **Dynamic Vocabulary Re-fitting**:
  - In a standard TF-IDF pipeline, calling `.fit()` on newly incoming documents via `/index/` would overwrite the existing vocabulary. I addressed this by keeping an in-memory document registry that combines existing and new documents before re-indexing.
- **Lexical vs. Semantic Trade-off**:
  - TF-IDF with stop words was chosen because it runs quickly, requires no heavy weights or GPU dependencies, and fits neatly within the 2–3 hour time box. The trade-off is that it cannot match synonyms (e.g., *facture* vs. *addition*) unless there is lexical overlap.

---

## What I Would Do Next (Production Roadmap)

- **Dense Semantic Embeddings**:
  - Replace or hybridize TF-IDF with a lightweight multilingual bi-encoder (such as `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`). This would capture true conversational intent and synonyms.
- **Modern FastAPI Lifespan**:
  - Migrate from the legacy `@app.on_event("startup")` handler to FastAPI's recommended `lifespan` context manager.
- **Dedicated Vector Store**:
  - If the FAQ grows from tens of questions to tens of thousands, transition from an in-memory matrix to a dedicated vector index (e.g., FAISS or Qdrant) with hybrid search (BM25 + Dense Vectors).
- **Answer Preprocessing**:
  - Provide both raw HTML and sanitized plain-text/markdown versions of the answer field to accommodate different client frontends.