# Store 014 Bench

Twenty-two questions about one month at Store 014, the fictional Bengaluru supermarket of the series
*Why Domain Matters* (https://kvinayakpai.github.io/domain-series/). Seven on the shelf, seven on the
truck, seven on the money, and one across them. Each has an answer key from the synthetic world,
which knows what really happened, so an assistant's or an agent's answers can be scored, not judged.

## What is here

- `questions.json`: each question, the time it is asked, and the fields an answer must have.
- `answer-key.json`: the gold answers and the scoring rule for each field.
- `score.py`: the scorer. Plain Python 3, no packages, no model calls.
- `baselines/`: the answers of the series' scripted assistant (rules, not a language model), given
  the schema only (`schema-only.json`), the three posts' domain layers (`domain-layers.json`), and
  the domain layers plus the map of who saw what (`map.json`).

## Run your own

1. Download the records: https://kvinayakpai.github.io/domain-series/data/ (CSV files, one month).
2. Give your assistant the records it would have in your setting, and ask each question. Use only
   rows timestamped before the question's `as_of`.
3. Write its answers as one JSON object, keyed by question id, each answer an object with the
   fields `questions.json` lists.
4. `python score.py answers.json`

Run it twice, once with the schema alone and once with a domain layer (the series' layers are in the
technical companions, and the map is `store-014-map.json` next to the records), and compare.

## Baselines

| Answers | Right |
|---|---|
| Scripted assistant, schema only | 3 of 22 |
| Scripted assistant, with the three domain layers | 21 of 22 |
| Scripted assistant, with the domain layers and the map | 22 of 22 |

The questions come from the series' three technical companions and its last post. Because the world
is synthetic and seeded, every reader sees the same month, and the answer key is complete.
