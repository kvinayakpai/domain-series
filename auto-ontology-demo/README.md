# Store 014 through NVIDIA Auto-Ontology

A real run of NVIDIA's open-source [Auto-Ontology](https://github.com/NVIDIA/auto-ontology)
on Store 014's June records, for Season 2's post "What would a machine draft for Store 014?".

The workflow `.github/workflows/auto-ontology-demo.yml` does it all on GitHub's own
machine, with no keys or secrets:

1. Loads Season 1's downloadable records (`public/data/india-grocery`, without the
   answer keys) into Postgres as 21 tables in three schemas: store, warehouse and
   payments (`seed_store014.py`).
2. Fetches Auto-Ontology at a fixed commit and starts it with Docker Compose.
3. Serves a small open model with Ollama in place of NVIDIA's hosted models.
   `compose.demo.yml` adds Ollama, and `model_adapter.py` serves embeddings and
   reranking in the shape Auto-Ontology expects.
4. Signs in, turns on semantic compilation, waits for the draft, exports it as Ossie
   YAML and asks the questions in `questions.json` (`run_demo.py`).
5. Commits everything to `results/`.

A small model on a CPU is much weaker than NVIDIA's default models, so read the draft
as a lower bound on what the tool does.

Auto-Ontology is NVIDIA's, under the Apache License 2.0. It is fetched when the
workflow runs, not copied into this repository.
