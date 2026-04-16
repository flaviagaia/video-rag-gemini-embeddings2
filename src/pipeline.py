from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .generation import build_grounded_answer
from .retrieval import VideoRAGRetrievalEngine
from .sample_data import build_sample_dataset


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


DEFAULT_QUERY = "At what point does the video show how to prepare the sauce with garlic and butter?"


def run_pipeline(question: str = DEFAULT_QUERY) -> Dict[str, object]:
    sample_info = build_sample_dataset()
    engine = VideoRAGRetrievalEngine(sample_info["csv_path"])
    hits = engine.search(question, top_k=3)
    response = build_grounded_answer(question, hits)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROCESSED_DIR / "video_rag_report.json"
    report = {
        "dataset_source": sample_info["dataset_source"],
        "runtime_mode": engine.mode,
        "segment_count": 6,
        "query": question,
        "top_segment_id": hits[0].segment_id if hits else None,
        "top_video_id": hits[0].video_id if hits else None,
        "top_time_range": f"{hits[0].start_time}-{hits[0].end_time}" if hits else None,
        "top_similarity": hits[0].similarity if hits else 0.0,
        "answer": response,
        "report_artifact": str(report_path),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
