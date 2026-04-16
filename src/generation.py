from __future__ import annotations

from typing import Dict, List

from .retrieval import RetrievalHit


def build_grounded_answer(question: str, hits: List[RetrievalHit]) -> Dict[str, object]:
    if not hits:
        return {
            "question": question,
            "answer": "No relevant video segment was found in the current indexed sample.",
            "citations": [],
            "limitation_note": (
                "The answer is limited to the indexed instructional-video sample available in this MVP."
            ),
        }

    top_hit = hits[0]
    answer = (
        f"The most relevant instructional step appears in {top_hit.recipe_title}, "
        f"step {top_hit.step_id}, between {top_hit.start_time} and {top_hit.end_time}. "
        f"The segment explains: {top_hit.instruction_text}"
    )

    citations = [
        {
            "segment_id": hit.segment_id,
            "video_id": hit.video_id,
            "recipe_title": hit.recipe_title,
            "time_range": f"{hit.start_time}-{hit.end_time}",
            "similarity": hit.similarity,
        }
        for hit in hits
    ]

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "limitation_note": (
            "This answer is grounded only in the indexed YouCook2-style sample and should be treated as a demo result."
        ),
    }
