"""Likert item distributions, reverse coding, scale scores, Cronbach's alpha and item analysis."""
import math
import statistics
from collections import Counter


def to_num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def reverse_code(x, lo=1, hi=5):
    return None if x is None else lo + hi - x


def item_summary(values, lo=1, hi=5, labels=None):
    """Distribution, median, mean, SD and top/bottom-box percentages for one item."""
    vals = [v for v in values if v is not None]
    n = len(vals)
    c = Counter(int(v) for v in vals)
    dist = [(k, c.get(k, 0), round(100.0 * c.get(k, 0) / n, 1) if n else 0.0) for k in range(int(lo), int(hi) + 1)]
    res = {"n": n, "missing": len(values) - n, "distribution": dist}
    if n:
        res.update({"median": statistics.median(vals), "mean": round(statistics.fmean(vals), 3),
                    "sd": round(statistics.stdev(vals), 3) if n > 1 else 0.0,
                    "top2": round(100.0 * sum(1 for v in vals if v >= hi - 1) / n, 1),
                    "bottom2": round(100.0 * sum(1 for v in vals if v <= lo + 1) / n, 1)})
    if labels:
        res["labels"] = labels
    return res


def scale_scores(matrix, min_answered=0.8, method="mean"):
    """Per-respondent score over items (rows = respondents). Respondents answering fewer than
    min_answered of the items get None (prorated mean otherwise)."""
    out = []
    k = len(matrix[0]) if matrix else 0
    for row in matrix:
        vals = [v for v in row if v is not None]
        if not k or len(vals) / k < min_answered:
            out.append(None)
        else:
            m = statistics.fmean(vals)
            out.append(round(m * k, 4) if method == "sum" else round(m, 4))
    return out


def _complete(matrix):
    return [r for r in matrix if all(v is not None for v in r)]


def cronbach_alpha(matrix):
    """alpha = k/(k-1) * (1 - sum(item variances) / variance(total)), on complete cases."""
    rows = _complete(matrix)
    k = len(rows[0]) if rows else 0
    if k < 2 or len(rows) < 2:
        raise ValueError("need at least 2 items and 2 complete respondents")
    item_vars = [statistics.variance([r[j] for r in rows]) for j in range(k)]
    total_var = statistics.variance([sum(r) for r in rows])
    if total_var == 0:
        raise ValueError("total score has zero variance")
    return k / (k - 1) * (1 - sum(item_vars) / total_var)


def _pearson(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sxy / (sx * sy) if sx and sy else float("nan")


def item_analysis(matrix, names):
    """Corrected item-total correlation and alpha-if-item-deleted for each item."""
    rows = _complete(matrix)
    out = []
    for j, name in enumerate(names):
        item = [r[j] for r in rows]
        rest = [sum(r) - r[j] for r in rows]
        reduced = [[v for i, v in enumerate(r) if i != j] for r in rows]
        try:
            a_del = cronbach_alpha(reduced) if len(names) > 2 else float("nan")
        except ValueError:
            a_del = float("nan")
        out.append({"item": name, "item_total_r": round(_pearson(item, rest), 3), "alpha_if_deleted": round(a_del, 3)})
    return out


def interpret_alpha(a):
    for lim, lab in ((0.9, "excellent"), (0.8, "good"), (0.7, "acceptable"), (0.6, "questionable"), (0.5, "poor")):
        if a >= lim:
            return lab
    return "unacceptable"
