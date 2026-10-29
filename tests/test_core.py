import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from likert_analyzer.cli import main
from likert_analyzer.core import cronbach_alpha, interpret_alpha, item_analysis, item_summary, reverse_code, scale_scores

# Worked example: three items, five respondents; item variances 2.5, 1.3, 3.3; total variance 19.2
M = [[2, 3, 2], [4, 5, 5], [3, 3, 4], [5, 4, 5], [1, 2, 1]]


class AlphaTests(unittest.TestCase):
    def test_hand_computed_alpha(self):
        self.assertAlmostEqual(cronbach_alpha(M), 1.5 * (1 - 7.1 / 19.2))   # 0.9453

    def test_parallel_items_alpha_one(self):
        self.assertAlmostEqual(cronbach_alpha([[1, 1], [2, 2], [3, 3]]), 1.0)

    def test_errors_and_missing_rows_dropped(self):
        with self.assertRaises(ValueError):
            cronbach_alpha([[1, 2]])
        self.assertAlmostEqual(cronbach_alpha(M + [[None, 1, 1]]), cronbach_alpha(M))

    def test_item_analysis(self):
        ia = item_analysis(M, ["a", "b", "c"])
        self.assertEqual([x["item"] for x in ia], ["a", "b", "c"])
        self.assertTrue(all(x["item_total_r"] > 0.7 for x in ia))
        self.assertEqual(interpret_alpha(0.95), "excellent")


class ItemTests(unittest.TestCase):
    def test_reverse_and_summary(self):
        self.assertEqual([reverse_code(x) for x in (1, 5, 3, None)], [5, 1, 3, None])
        s = item_summary([1, 2, 5, 5, None])
        self.assertEqual((s["n"], s["missing"], s["median"], s["top2"]), (4, 1, 3.5, 50.0))
        self.assertEqual(s["distribution"][4], (5, 2, 50.0))

    def test_scale_scores(self):
        self.assertEqual(scale_scores([[1, 2, 3, 4, 5], [5, None, 5, 5, 5], [1, None, None, 2, 3]]), [3.0, 5.0, None])
        self.assertEqual(scale_scores([[1, 2]], method="sum"), [3.0])

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p, sc = os.path.join(d, "s.csv"), os.path.join(d, "scores.csv")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("id,q1,q2,q3\n" + "".join("%d,%d,%d,%d\n" % (i, r[0], 6 - r[1], r[2]) for i, r in enumerate(M)))
                fh.write("9,9,3,3\n")
            with redirect_stdout(io.StringIO()) as buf:
                main([p, "-i", "q*", "-r", "q2", "--scores", sc])
            self.assertIn("Cronbach's alpha = 0.945", buf.getvalue())
            self.assertTrue(os.path.exists(sc))


if __name__ == "__main__":
    unittest.main()
