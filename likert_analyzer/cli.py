"""Command-line interface for likert-analyzer."""
import argparse
import csv
import json

from .core import cronbach_alpha, interpret_alpha, item_analysis, item_summary, reverse_code, scale_scores, to_num


def main(argv=None):
    ap = argparse.ArgumentParser(prog="likert-analyzer", description="Analyse Likert-scale survey items.")
    ap.add_argument("csvfile")
    ap.add_argument("-i", "--items", required=True, help="comma-separated item columns (or prefix*, e.g. q*)")
    ap.add_argument("-r", "--reverse", default="", help="comma-separated items to reverse-code")
    ap.add_argument("--min", type=int, default=1)
    ap.add_argument("--max", type=int, default=5)
    ap.add_argument("--min-answered", type=float, default=0.8)
    ap.add_argument("--scores", help="write respondents' scale scores to this CSV")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    with open(args.csvfile, encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh)
        rows, fields = list(r), r.fieldnames
    items = []
    for spec in args.items.split(","):
        spec = spec.strip()
        items += [f for f in fields if f.startswith(spec[:-1])] if spec.endswith("*") else [spec]
    rev = {x.strip() for x in args.reverse.split(",") if x.strip()}
    matrix = []
    for row in rows:
        vals = []
        for it in items:
            v = to_num(row.get(it))
            if v is not None and not args.min <= v <= args.max:
                v = None   # out-of-range codes (e.g. 9 = don't know) treated as missing
            vals.append(reverse_code(v, args.min, args.max) if it in rev else v)
        matrix.append(vals)
    summaries = {it: item_summary([r[j] for r in matrix], args.min, args.max) for j, it in enumerate(items)}
    res = {"items": summaries, "n_respondents": len(rows)}
    try:
        a = cronbach_alpha(matrix)
        res["alpha"] = round(a, 3)
        res["alpha_interpretation"] = interpret_alpha(a)
        res["item_analysis"] = item_analysis(matrix, items)
    except ValueError as exc:
        res["alpha_error"] = str(exc)
    scores = scale_scores(matrix, args.min_answered)
    if args.scores:
        with open(args.scores, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["row", "scale_mean"])
            w.writerows((i, "" if s is None else s) for i, s in enumerate(scores, 1))
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    print("%d respondents, %d items%s" % (len(rows), len(items), " (reversed: %s)" % ", ".join(sorted(rev)) if rev else ""))
    print("%-12s %5s %6s %5s %6s %6s  distribution" % ("item", "n", "mean", "sd", "top2%", "bot2%"))
    for it, s in summaries.items():
        dist = " ".join("%d:%d%%" % (k, round(p)) for k, _, p in s["distribution"])
        print("%-12s %5d %6.2f %5.2f %6.1f %6.1f  %s" % (it[:12], s["n"], s.get("mean", 0), s.get("sd", 0),
                                                       s.get("top2", 0), s.get("bottom2", 0), dist))
    if "alpha" in res:
        print("\nCronbach's alpha = %.3f (%s)" % (res["alpha"], res["alpha_interpretation"]))
        for ia in res["item_analysis"]:
            flag = "  <- low" if ia["item_total_r"] < 0.3 else ""
            print("  %-12s item-total r = %6.3f, alpha if deleted = %6.3f%s" % (ia["item"][:12], ia["item_total_r"],
                                                                                ia["alpha_if_deleted"], flag))
    else:
        print("alpha not computed: " + res["alpha_error"])
    return 0
