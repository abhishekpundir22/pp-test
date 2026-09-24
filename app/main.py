import json
import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn

try:
    from app.matcher import FAQMatcher
except ImportError:
    from matcher import FAQMatcher

app = FastAPI(
    title="FAQ Search API",
    description="Vector search API for FAQ matching using TF-IDF and Cosine Similarity"
)

matcher = FAQMatcher()


class QuestionItem(BaseModel):
    qid: int
    question: str
    answer: Optional[str] = None


class QuestionsPayload(BaseModel):
    questions: List[QuestionItem]


class SearchResponse(BaseModel):
    query: str
    match_found: bool
    question: Optional[str] = None
    answer: Optional[str] = None
    score: float


@app.on_event("startup")
def load_faq_dataset():
    """Load default questions and answers from data/faq.json on startup."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "data", "faq.json"),
        os.path.join(os.path.dirname(__file__), "data", "faq.json"),
        "data/faq.json",
        "faq.json"
    ]
    faq_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if faq_path:
        with open(faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            matcher.fit(data)
        print(f"Successfully loaded and indexed {len(matcher.documents)} FAQ items.")
    else:
        print("Warning: data/faq.json not found during startup.")


@app.post("/index/")
def index_questions(payload: QuestionsPayload):
    """Dynamically register and re-index new questions and answers."""
    new_docs = [
        {"q": item.question, "a": item.answer or "", "index": str(item.qid)}
        for item in payload.questions
    ]
    matcher.add_documents(new_docs)
    return {"indexed": len(new_docs), "total_documents": len(matcher.documents)}


@app.get("/search", response_model=SearchResponse)
def search_faq(
    query: str = Query(..., min_length=1, description="User search query"),
    threshold: float = Query(0.2, ge=0.0, le=1.0, description="Minimum cosine similarity cutoff")
):
    """Finds the most relevant FAQ entry for a given user query."""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty or blank spaces.")

    best_doc, score = matcher.match(query, threshold=threshold)

    if not best_doc:
        return SearchResponse(
            query=query,
            match_found=False,
            question=None,
            answer=None,
            score=score
        )

    return SearchResponse(
        query=query,
        match_found=True,
        question=best_doc.get("q"),
        answer=best_doc.get("a"),
        score=score
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)