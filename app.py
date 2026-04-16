from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from src.pipeline import run_pipeline


class QueryRequest(BaseModel):
    question: str


app = FastAPI(
    title="Video RAG Gemini Embeddings2",
    description=(
        "RAG para videos instrucionais com chunking temporal, preparado para Gemini Embedding 2 "
        "e fallback local reproduzivel."
    ),
    version="1.0.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/search")
def search(request: QueryRequest) -> dict[str, object]:
    return run_pipeline(request.question)
