from __future__ import annotations

import csv
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency
    genai = None


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


@dataclass
class RetrievalHit:
    segment_id: str
    video_id: str
    recipe_title: str
    step_id: int
    start_time: str
    end_time: str
    instruction_text: str
    visual_description: str
    similarity: float


class GeminiEmbeddingClient:
    def __init__(self) -> None:
        self.model_name = "gemini-embedding-2-preview"
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            raise RuntimeError("Gemini runtime not configured.")
        self.client = genai.Client(api_key=api_key)

    def embed_text(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
        )
        return list(result.embeddings[0].values)


class VideoRAGRetrievalEngine:
    def __init__(self, csv_path: str) -> None:
        self.rows = self._load_rows(csv_path)
        self.mode = "local_tfidf_fallback"
        self.embedding_client = None
        self.document_vectors: List[List[float]] | None = None

        try:
            self.embedding_client = GeminiEmbeddingClient()
            self.mode = "gemini_embedding_2"
            self.document_vectors = [
                self.embedding_client.embed_text(self._combined_text(row))
                for row in self.rows
            ]
        except Exception:
            self.lexical_vectors, self.vocabulary = self._build_lexical_index(self.rows)

    def _load_rows(self, csv_path: str) -> List[Dict[str, str]]:
        with Path(csv_path).open("r", encoding="utf-8", newline="") as csv_file:
            return list(csv.DictReader(csv_file))

    def _combined_text(self, row: Dict[str, str]) -> str:
        return " ".join(
            [
                row["recipe_title"],
                row["instruction_text"],
                row["visual_description"],
            ]
        )

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in TOKEN_PATTERN.findall(text)]

    def _build_lexical_index(
        self, rows: List[Dict[str, str]]
    ) -> tuple[List[Dict[str, float]], List[str]]:
        docs = [self._tokenize(self._combined_text(row)) for row in rows]
        vocabulary = sorted({token for doc in docs for token in doc})
        doc_freq = {token: 0 for token in vocabulary}

        for doc in docs:
            for token in set(doc):
                doc_freq[token] += 1

        doc_count = len(docs)
        vectors: List[Dict[str, float]] = []
        for doc in docs:
            term_count: Dict[str, int] = {}
            for token in doc:
                term_count[token] = term_count.get(token, 0) + 1
            length = max(len(doc), 1)
            vector: Dict[str, float] = {}
            for token, count in term_count.items():
                tf = count / length
                idf = math.log((1 + doc_count) / (1 + doc_freq[token])) + 1
                vector[token] = tf * idf
            vectors.append(vector)
        return vectors, vocabulary

    def _cosine_sparse(self, left: Dict[str, float], right: Dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        shared = set(left).intersection(right)
        numerator = sum(left[token] * right[token] for token in shared)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _cosine_dense(self, left: List[float], right: List[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def search(self, query: str, top_k: int = 3) -> List[RetrievalHit]:
        scored_hits: List[RetrievalHit] = []

        if self.mode == "gemini_embedding_2":
            assert self.embedding_client is not None
            assert self.document_vectors is not None
            query_vector = self.embedding_client.embed_text(query)
            scores = [
                self._cosine_dense(query_vector, document_vector)
                for document_vector in self.document_vectors
            ]
        else:
            query_tokens = self._tokenize(query)
            query_counts: Dict[str, int] = {}
            for token in query_tokens:
                query_counts[token] = query_counts.get(token, 0) + 1
            query_length = max(len(query_tokens), 1)
            query_vector = {token: count / query_length for token, count in query_counts.items()}
            scores = [
                self._cosine_sparse(query_vector, document_vector)
                for document_vector in self.lexical_vectors
            ]

        for row, score in zip(self.rows, scores):
            scored_hits.append(
                RetrievalHit(
                    segment_id=row["segment_id"],
                    video_id=row["video_id"],
                    recipe_title=row["recipe_title"],
                    step_id=int(row["step_id"]),
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    instruction_text=row["instruction_text"],
                    visual_description=row["visual_description"],
                    similarity=round(float(score), 4),
                )
            )

        scored_hits.sort(key=lambda hit: hit.similarity, reverse=True)
        return scored_hits[:top_k]
