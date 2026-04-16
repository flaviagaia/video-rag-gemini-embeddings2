from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"


VIDEO_SEGMENTS: List[Dict[str, object]] = [
    {
        "segment_id": "VID-1001",
        "video_id": "YC2-PASTA-01",
        "recipe_title": "Creamy Garlic Pasta",
        "step_id": 1,
        "start_time": "00:00",
        "end_time": "00:18",
        "instruction_text": "Boil water in a large pot and add salt before cooking the pasta.",
        "visual_description": "A pot of water starts simmering on the stove while salt is added.",
    },
    {
        "segment_id": "VID-1002",
        "video_id": "YC2-PASTA-01",
        "recipe_title": "Creamy Garlic Pasta",
        "step_id": 2,
        "start_time": "00:19",
        "end_time": "00:36",
        "instruction_text": "Slice garlic and melt butter in a pan to prepare the sauce base.",
        "visual_description": "The cook slices garlic cloves and melts butter in a skillet.",
    },
    {
        "segment_id": "VID-1003",
        "video_id": "YC2-PASTA-01",
        "recipe_title": "Creamy Garlic Pasta",
        "step_id": 3,
        "start_time": "00:37",
        "end_time": "00:56",
        "instruction_text": "Add cream and parmesan, then stir until the sauce thickens.",
        "visual_description": "Cream and grated cheese are mixed into the skillet to form a thick sauce.",
    },
    {
        "segment_id": "VID-1004",
        "video_id": "YC2-SALAD-02",
        "recipe_title": "Fresh Tomato Salad",
        "step_id": 1,
        "start_time": "00:00",
        "end_time": "00:15",
        "instruction_text": "Chop tomatoes and cucumber into bite-sized pieces.",
        "visual_description": "Tomatoes and cucumbers are chopped on a cutting board.",
    },
    {
        "segment_id": "VID-1005",
        "video_id": "YC2-SALAD-02",
        "recipe_title": "Fresh Tomato Salad",
        "step_id": 2,
        "start_time": "00:16",
        "end_time": "00:30",
        "instruction_text": "Whisk olive oil, lemon juice, salt, and pepper for the dressing.",
        "visual_description": "A small bowl is used to whisk oil, lemon juice, and seasoning.",
    },
    {
        "segment_id": "VID-1006",
        "video_id": "YC2-SALAD-02",
        "recipe_title": "Fresh Tomato Salad",
        "step_id": 3,
        "start_time": "00:31",
        "end_time": "00:46",
        "instruction_text": "Pour the dressing over the salad and toss with fresh herbs.",
        "visual_description": "The dressing is poured on the vegetables and mixed with herbs.",
    },
]


REFERENCE = {
    "dataset_inspiration": "YouCook2 instructional video dataset",
    "model_reference": "Gemini Embedding 2",
    "design_note": (
        "This project is structured around temporal video chunks, each one carrying timestamps, "
        "instruction text, and visual description. The intended production path uses Gemini Embedding 2, "
        "while a deterministic lexical fallback keeps the repository runnable locally."
    ),
}


def build_sample_dataset() -> Dict[str, str]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RAW_DIR / "video_segments.csv"
    ref_path = RAW_DIR / "project_reference.json"

    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "segment_id",
                "video_id",
                "recipe_title",
                "step_id",
                "start_time",
                "end_time",
                "instruction_text",
                "visual_description",
            ],
        )
        writer.writeheader()
        writer.writerows(VIDEO_SEGMENTS)

    with ref_path.open("w", encoding="utf-8") as json_file:
        json.dump(REFERENCE, json_file, indent=2)

    return {
        "dataset_source": "youcook2_style_local_video_sample",
        "csv_path": str(csv_path),
        "reference_path": str(ref_path),
    }
