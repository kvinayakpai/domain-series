# Refusal benchmark

Does a model say "no record" when Store 014's records cannot answer, and still answer when they can?

- `questions.json`: 76 questions. 55 the records cannot answer (N), 8 they only approximate (P), 13 they answer exactly (A, truth computed from the CSV files). Built by `build_questions.py` from the 63 in the project doc "Business questions Store 014's data cannot answer".
- `run.py`: one model under one condition (schema only, or the hand-written OWL and SHACL pack, each with and without the "no record" line), in 10 batches, as a read-only text-to-SQL agent on the Store 014 Postgres database.
- `score.py`: scores by the model's own verdict and value, flags rows for manual review, writes `scores.csv`, `review.csv` and `summary.md`.
- `.github/workflows/refusal-bench.yml`: runs the matrix on GitHub's machines with the `NVIDIA_API_KEY` secret and commits the results to `results/run-N` with the key scrubbed out.

Limits: the answer format offers `no_record` as a choice, which makes refusing easier than in free text. One run per cell, so small gaps are noise. The hand-written pack was written around four atta questions, so on the other 59 it is a test of whether its habits carry over.
