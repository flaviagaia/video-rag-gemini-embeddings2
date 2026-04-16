from __future__ import annotations

import unittest

from src.pipeline import run_pipeline


class VideoRAGGeminiEmbeddings2TestCase(unittest.TestCase):
    def test_pipeline_contract(self) -> None:
        summary = run_pipeline()
        self.assertEqual(summary["dataset_source"], "youcook2_style_local_video_sample")
        self.assertEqual(summary["segment_count"], 6)
        self.assertIn(summary["runtime_mode"], ["gemini_embedding_2", "local_tfidf_fallback"])
        self.assertIsNotNone(summary["top_segment_id"])
        self.assertGreaterEqual(summary["top_similarity"], 0.15)
        self.assertEqual(len(summary["answer"]["citations"]), 3)

    def test_query_hits_sauce_step(self) -> None:
        summary = run_pipeline("Where does the video show slicing garlic and melting butter for the sauce?")
        self.assertEqual(summary["top_segment_id"], "VID-1002")


if __name__ == "__main__":
    unittest.main()
