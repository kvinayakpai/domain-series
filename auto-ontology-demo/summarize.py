"""Summarise one demo run's results for the post, and check its answers against the data.

Reads auto-ontology-demo/results/run-N and writes src/data/auto-ontology-run.json: the setup,
how long each step took, every term the draft named with the tables behind it, whether any
term names demand or a lost sale, the coverage check for each question, and each answer with
its SQL. Each answer's SQL is run again on a Postgres copy of Store 014 (given as a psql
connection string) so the post can say whether the number is right.

    python3 auto-ontology-demo/summarize.py <results/run-N> [psql-connection]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(folder: Path, name: str, default=None):
    path = folder / name
    return json.loads(path.read_text()) if path.exists() else default


# The true answers, from the records themselves. Demand and lost sales are in no table.
TRUTH = {
    "sold": "select sum(qty) from store.pos_lines where sku_scanned = 'ATTA-WW-5KG' and bill_ts >= '2026-06-01' and bill_ts < '2026-07-01'",
    "on-shelf": "select count(*) filter (where status = 'on shelf') || ' of ' || count(*) from store.shelf_audits where sku = 'ATTA-WW-5KG'",
    "on-shelf-book": "select count(*) filter (where book_on_hand_close > 0) || ' of ' || count(*) from store.inventory_book where sku = 'ATTA-WW-5KG'",
    "left-without": None,
    "lost-sales": None,
}
LOG_FACTS = {
    "compile_summary": r"Semantic calculation finished successfully \(database='store014'\) — (.*)",
    "compiled_seconds": r"semantic: finished successfully — .* compiled in ([\d.]+)s",
    "sql_attributes_from_history": r"New SqlAttribute nodes written: (\d+)",
    "column_attributes_described": r"ColumnAttributes described: (\d+)",
    "bridge_tables": r"Bridge tables built: (\d+)",
    "concept_merges": r"Concept merges applied: (\d+)",
    "joins_inferred": r"resolve_semantic_fks: done — (\d+) declared \+ (\d+) inferred",
}


def log_facts(folder: Path) -> dict:
    path = folder / "logs" / "auto-ontology-ingestion-service.log"
    text = path.read_text(errors="replace") if path.exists() else ""
    facts = {}
    for key, pattern in LOG_FACTS.items():
        found = re.findall(pattern, text)
        facts[key] = found[-1] if found else None
    facts["joins"] = sorted(set(re.findall(r"Semantic FK join default: (\S+ -> \S+)", text)))
    facts["joins_considered"] = sorted(set(re.findall(r"Resolving semantic FK edges… \(\d+/\d+\): (\S+)", text)))
    facts["joins_rejected"] = sorted(set(re.findall(r"resolve_semantic_fks \[values\]: (\S+) — no vector-search hit holds its values", text)))
    facts["concepts_merged"] = sorted(set(re.findall(r"resolve_concepts: (\S+ \+ \S+ -> Concept '[^']+')", text)))
    facts["main_terms_by_table"] = {
        table: names
        for table, names in re.findall(r"\[(\w+)\] → Terms (\[.*?\]) \(", text)
    }
    return facts


def rerun(sql: str, conn: str | None) -> object:
    if not conn or not sql:
        return None
    result = subprocess.run(["psql", conn, "-At", "-F", "\t", "-c", sql], capture_output=True, text=True, timeout=120)
    if result.returncode:
        return {"error": result.stderr.strip()[:500]}
    return [line.split("\t") for line in result.stdout.strip().splitlines()]


def main() -> None:
    folder = Path(sys.argv[1])
    conn = sys.argv[2] if len(sys.argv) > 2 else None
    run, setup = load(folder, "run.json", {}), load(folder, "setup.json", {})
    terms = load(folder, "terms.json", []) or []
    details = load(folder, "term-details.json", {}) or {}
    coverage = load(folder, "coverage.json", []) or []
    answers = load(folder, "answers.json", []) or []

    drafted = []
    for term in terms:
        tables = (details.get(term["id"]) or {}).get("data", {}).get("tables") or []
        drafted.append({
            "name": term.get("name"),
            "description": term.get("description"),
            "tables": sorted({f"{t.get('schema_name')}.{t.get('name')}" for t in tables}),
        })
    drafted.sort(key=lambda t: (t["tables"][:1], t["name"] or ""))
    gap_words = re.compile(r"\b(demand|lost|unmet|stock-?outs?|empty|shoppers?)\b", re.I)
    gap_terms = [t["name"] for t in drafted if gap_words.search(t["name"] or "")]
    gap_mentions = [t["name"] for t in drafted if gap_words.search(t["description"] or "")]
    product_terms = [t["name"] for t in drafted if re.match(r"Product( SKU)?( \(|$)", t["name"] or "")]

    asked = []
    for a in answers:
        result = next((e.get("answer") for e in a.get("events", []) if e.get("type") == "result"), None) or {}
        errors = [e.get("message") for e in a.get("events", []) if e.get("type") == "error"]
        sql = result.get("sql_code")
        asked.append({
            "id": a["id"], "question": a["question"], "seconds": a.get("seconds"),
            "answer": result.get("response"), "sql": sql,
            "rows": (result.get("sql_response_from_db") or [])[:20] if isinstance(result.get("sql_response_from_db"), list) else result.get("sql_response_from_db"),
            "errors": errors or None, "skipped": a.get("skipped"),
            "rerun_on_store014": rerun(sql, conn),
            "truth": rerun(TRUTH[a["id"]], conn) if TRUTH.get(a["id"]) else None,
        })

    phases = {k: {"status": v.get("status"), "minutes": v.get("minutes")} for k, v in run.get("phases", {}).items()}
    export = run.get("phases", {}).get("export", {})
    summary = {
        "run": {
            "number": setup.get("run_number"), "id": setup.get("run_id"),
            "date": "20 November 2026",
            "tables": 21,
            "draft_minutes": round(run.get("phases", {}).get("compile", {}).get("minutes") or 0),
            "answer_model": setup.get("answer_model") or setup.get("chat_model"),
            "nvidia_auto_ontology_commit": setup.get("nvidia_auto_ontology_commit"),
            "chat_model": setup.get("chat_model"), "embedding_model": setup.get("embedding_model"),
            "ollama": setup.get("ollama"), "cpus": (setup.get("runner") or {}).get("cpus"),
            "phases": phases,
            "ossie_export_refused": (export.get("ossie_refused") or {}).get("body"),
            "export_files": export.get("files"),
            "compile": log_facts(folder),
            "book_days_with_stock": rerun(TRUTH["on-shelf-book"], conn),
        },
        "terms": drafted,
        "term_count": len(drafted),
        "terms_naming_the_gap": gap_terms,
        "descriptions_mentioning_the_gap": gap_mentions,
        "product_terms": product_terms,
        "coverage": [
            {"id": c["id"], "question": c["question"],
             "coverage": ((c.get("result") or {}).get("data") or {}).get("coverage"),
             "uncovered": ((c.get("result") or {}).get("data") or {}).get("uncovered_entities"),
             "matched": [f"{m.get('term')}: {m.get('attribute')}" for m in (((c.get("result") or {}).get("data") or {}).get("candidates") or [])]}
            for c in coverage
        ],
        "answers": asked,
    }
    out = ROOT / "src" / "data" / "auto-ontology-run.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    files = ROOT / "public" / "data" / "auto-ontology"
    files.mkdir(parents=True, exist_ok=True)
    (files / "store014-draft-terms.json").write_text(json.dumps(drafted, indent=2, ensure_ascii=False) + "\n")
    (files / "store014-run.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(f"{out}: {len(drafted)} terms, {len(coverage)} coverage checks, {len(asked)} answers")


if __name__ == "__main__":
    main()
