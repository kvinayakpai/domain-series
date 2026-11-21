# Store 014 through NVIDIA Auto-Ontology

A real run of NVIDIA's open-source [Auto-Ontology](https://github.com/NVIDIA/auto-ontology)
on Store 014's June records, for Season 2's post "What would a machine draft for Store 014?".

The workflow `.github/workflows/auto-ontology-demo.yml` does it all on GitHub's own
machine. `run-config.env` picks the models, and changing it starts a run:

- `MODELS=nvidia`: NVIDIA's own hosted models, exactly as Auto-Ontology's
  `.env.example` names them at the fixed commit. Needs a free key from
  build.nvidia.com in the repository secret `NVIDIA_API_KEY`.
- `MODELS=ollama`: small open models on GitHub's machine, with no keys or secrets.

1. Loads Season 1's downloadable records (`public/data/india-grocery`, without the
   answer keys) into Postgres as 21 tables in three schemas: store, warehouse and
   payments (`seed_store014.py`).
2. Fetches Auto-Ontology at a fixed commit and starts it with Docker Compose.
3. With `MODELS=nvidia`, checks that NVIDIA's chat, embedding and reranking models
   answer. With `MODELS=ollama`, serves small open models with Ollama instead:
   `compose.demo.yml` adds Ollama, and `model_adapter.py` passes chat on to it (capping
   each answer's length), serves embeddings and reranking in the shape Auto-Ontology
   expects, and can switch the chat model once the draft is done.
4. Signs in, turns on semantic compilation, waits for the draft, saves its terms and
   asks the questions in `questions.json` (`run_demo.py`). With `EXPERT_LAYER=1` it then
   enters what Season 2's hand-built ontology knows through Auto-Ontology's tools for
   experts (`expert_layer.py`: the table guide, the joins, a glossary and the twelve rules
   as organization instructions, plus calculations and certified queries) and asks again.
5. Commits everything, with the logs, to `results/run-N` on the `auto-ontology-demo` branch.
   `scrub.py` takes the run's throwaway passwords and the NVIDIA key out of every file
   first, at each progress push and at the end.

`summarize.py` turns one run's results into `src/data/auto-ontology-run.json` and the two
downloads in `public/data/auto-ontology/`, and checks each answer against a Postgres copy
of the same records.

Small models on a CPU are much weaker than NVIDIA's default models, so read the Ollama
runs' drafts and answers as a floor, not as what the tool does with its own models.

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
- Run 7: the same draft model, with Qwen2.5 7B answering. It answered, confidently and
  wrongly: 660 bags sold (the goods receipts), no shoppers left without, and on-shelf
  availability from the goods receipts. Lost sales got no answer in 114 minutes.
- Run 8: Qwen2.5 7B before and after Season 2's knowledge went in. Before: 567 sold
  (right), 28 shoppers (the days of book stock), 1.43% on the shelf (the warehouse's
  picks). After: 567 from the till lines matched on the GTIN, on-shelf availability as
  the share of shelf audits but with no number, the 567 bags sold given as the shoppers
  who left without, and 24 "lost sales" that were the days with sales. The coverage check
  passed every question both times. The table descriptions did not go in, here or in run
  10: the API answered in a shape `expert_layer.py` did not expect (fixed after run 10,
  not yet run).
- Run 9: NVIDIA's own models for everything, as Auto-Ontology ships, with a free key.
  NVIDIA's hosted embedding model answered 503 ("Service is overloaded") and 504 from the
  start, the ingest gave up after four attempts, and the draft ran on without the
  embeddings. Read its results with that in mind.
- Run 10: NVIDIA's Nemotron 3.5 Lightning drafting and answering, with the local
  embeddings and reranking of runs 6 to 8 (`EMBEDDINGS=local`), so the chat model is the
  only change. The draft took 10 minutes: 21 terms, one per table, none for demand or a
  lost sale; three joins, all to the shipments, and none between the till's payments and
  UPI's report; no calculations; and the Ossie export went through. Before the knowledge:
  567 sold and 75% on the shelf (both right), 2 shoppers who left without (the shelf
  audits that found the shelf empty) and 3 bags of lost sales (the write-offs). After: the
  same two right answers, and for the other two it said no record holds them and gave the
  two empty audits and the 567 bags sold. The coverage check passed every question both
  times.
