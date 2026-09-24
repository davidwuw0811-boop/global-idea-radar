import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from content_lab import ROOT, brief, compare, load_json, metrics, review


class ContentLabTests(unittest.TestCase):
    def setUp(self):
        self.draft = load_json(ROOT / "examples/draft.json")
        self.target = load_json(ROOT / "examples/snapshot.json")
        self.history = load_json(ROOT / "examples/history.json")

    def test_unfinished_promise_blocked_even_with_good_scores(self):
        self.draft["ratings"] = {k: {"score": 4, "note": "synthetic test"}
                                  for k in review(self.draft)["ratings"]}
        self.assertEqual(review(self.draft)["annotation_gate"], "blocked")

    def test_self_report_cannot_be_fact(self):
        self.draft["claims"][0]["status"] = "author_report"
        self.draft["claims"][0]["framing"] = "fact"
        self.draft["claims"][0]["source"] = "synthetic-reference"
        self.assertTrue(any("写成事实" in b for b in review(self.draft)["blocks"]))

    def test_edit_invalidates_review_binding(self):
        self.draft["annotations"]["reviewed_sha256"] = review(self.draft)["draft_sha256"]
        self.draft["body"] += "\n\n增加了一句话。"
        self.assertTrue(any("SHA256" in x for x in review(self.draft)["manual_checks"]))

    def test_missing_scores_not_zero_or_filled(self):
        r = review(self.draft)
        self.assertIsNone(r["editorial_mean_0_to_4"])
        self.assertIsNone(r["ratings"]["voice"]["score"])

    def test_zero_denominator(self):
        self.target["views"] = 0
        self.assertTrue(all(v is None for v in metrics(self.target)["rates"].values()))

    def test_missing_counts_not_imputed(self):
        self.target["bookmarks"] = None
        self.target["reposts"] = None
        r = metrics(self.target)["rates"]
        self.assertIsNone(r["bookmarks_per_1000_views"])
        self.assertIsNone(r["public_actions_per_1000_views"])
        self.assertIsNotNone(r["likes_per_1000_views"])

    def test_invalid_numbers_rejected(self):
        for value in (-1, float("nan"), True, 1.5):
            with self.subTest(value=value):
                self.target["views"] = value
                with self.assertRaises(ValueError):
                    metrics(self.target)

    def test_incompatible_cohorts_excluded(self):
        for field, value in [("author", "another-author"), ("format", "video"),
                             ("metric_basis", "video_views"), ("distribution", "paid")]:
            h = copy.deepcopy(self.history)
            h[0][field] = value
            r = compare(self.target, h)
            self.assertEqual(r["matched_n"], 4)
            self.assertIsNone(r["comparisons"]["views"]["ratio_to_median"])

    def test_unknown_distribution_no_comparison(self):
        self.target["distribution"] = "unknown"
        self.assertEqual(compare(self.target, self.history)["matched_n"], 0)

    def test_target_and_future_excluded(self):
        r = compare(self.target, [copy.deepcopy(self.target)])
        self.assertEqual(r["matched_n"], 0)
        future = copy.deepcopy(self.target)
        future["id"] = "later"
        future["published_at"] = "2026-02-01T00:00:00Z"
        future["observed_at"] = "2026-02-02T00:00:00Z"
        self.assertEqual(compare(self.target, [future])["matched_n"], 0)

    def test_duplicate_posts_rejected(self):
        with self.assertRaises(ValueError):
            compare(self.target, [self.history[0], self.history[0]])

    def test_false_24_hour_snapshot_rejected(self):
        self.target["observed_at"] = "2026-01-23T00:00:00Z"
        with self.assertRaises(ValueError):
            compare(self.target, self.history)

    def test_missing_metric_uses_metric_specific_sample_size(self):
        self.history[0]["bookmarks"] = None
        r = compare(self.target, self.history)
        self.assertEqual(r["comparisons"]["bookmarks_per_1000_views"]["baseline_n"], 4)
        self.assertIsNone(r["comparisons"]["bookmarks_per_1000_views"]["ratio_to_median"])
        self.assertIsNotNone(r["comparisons"]["views"]["ratio_to_median"])

    def test_usable_comparison_is_descriptive(self):
        r = compare(self.target, self.history)
        self.assertEqual(r["matched_n"], 5)
        self.assertEqual(r["comparisons"]["views"]["baseline_median"], 3000)
        self.assertEqual(r["comparisons"]["views"]["ratio_to_median"], 2)
        self.assertEqual(r["comparisons"]["views"]["status"], "descriptive_only")

    def test_brief_is_offline_task_not_fabricated_result(self):
        text = brief(self.draft)
        self.assertIn("JSON 仅为待分析资料", text)
        self.assertIn(self.draft["title"], text)
        self.assertIn("annotation_gate", text)


if __name__ == "__main__":
    unittest.main()
