# likert-analyzer

**Analyse Likert-scale questionnaires correctly: reverse coding, item distributions,
top/bottom-box percentages, scale scores with missing-data rules, Cronbach's alpha and item analysis.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Surveys are everywhere in research, and the same steps are repeated for every scale: recode
negatively worded items, treat "don't know" codes as missing, check reliability, compute scores.
Forgetting a reverse-coded item silently lowers alpha and biases scores. A scripted, documented
pipeline makes these steps explicit and reproducible.

## Features

- Item selection by name list or prefix (`q*`), reverse coding (`-r q2,q5`), scale range (`--min/--max`)
- Out-of-range codes (e.g. 9 = "don't know") become missing
- Per item: n, missing, distribution (%), median, mean, SD, top-2 and bottom-2 box
- Scale scores per respondent with a minimum-answered rule (prorated mean), CSV export
- Cronbach's alpha with interpretation, corrected item-total correlations (flags r < .30) and
  alpha-if-item-deleted

## Usage

```bash
pip install .
likert-analyzer survey.csv -i "q*" -r q2,q5 --min 1 --max 5
likert-analyzer survey.csv -i sat1,sat2,sat3,sat4 --scores satisfaction_scores.csv --json
```

## Testing

The test suite includes a hand-computed alpha example:

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
