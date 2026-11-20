# Store 014 through NVIDIA Auto-Ontology

A real run of NVIDIA's open-source [Auto-Ontology](https://github.com/NVIDIA/auto-ontology)
on Store 014's June records, for Season 2's post "What would a machine draft for Store 014?".

The workflow `.github/workflows/auto-ontology-demo.yml` does it all on GitHub's own
machine, with no keys or secrets:

1. Loads Season 1's downloadable records (`public/data/india-grocery`, without the
   answer keys) into Postgres as 21 tables in three schemas: store, warehouse and
   payments (`seed_store014.py`).
2. Fetches Auto-Ontology at a fixed commit and starts it with Docker Compose.
3. Serves small open models with Ollama in place of NVIDIA's hosted models.
   `compose.demo.yml` adds Ollama, and `model_adapter.py` passes chat on to it (capping
   each answer's length), serves embeddings and reranking in the shape Auto-Ontology
   expects, and can switch the chat model once the draft is done.
4. Signs in, turns on semantic compilation, waits for the draft, saves its terms and
   asks the questions in `questions.json` (`run_demo.py`).
5. Commits everything, with the logs, to `results/run-N` on the `auto-ontology-demo` branch.

`summarize.py` turns one run's results into `src/data/auto-ontology-run.json` and the two
downloads in `public/data/auto-ontology/`, and checks each answer against a Postgres copy
of the same records.

Small models on a CPU are much weaker than NVIDIA's default models, so read the draft and
the answers as a floor, not as what the tool does with its own models.

Auto-Ontology is NVIDIA's, under the Apache License 2.0. It is fetched when the workflow
runs, not copied into this repository.

## What the runs taught

- Run 3: under a JSON schema, a 4B model repeated itself inside a short answer, 1,600
  tokens and counting. The adapter now caps each answer and adds Qwen's sampling.
- Run 4: the draft took 62 minutes. Asked about "June", the agent searched June 2023.
  Asked how many shoppers left without 5 kg atta, it counted the shelf audits that
  found the bay empty.
- Run 5, a second sample of the same draft: 94 minutes and 67 terms, with the product
  named six times. The same four joins from the goods receipts, no term for demand or a
  lost sale, every question passed by the coverage check, and no answers. The counts vary
  from run to run, and the findings do not.
- Run 6 (the one the post reports): the draft took 44 minutes and named 90 terms. The
  agent wrote the right query for the bags sold (567) but ended every question without
  submitting an answer.
