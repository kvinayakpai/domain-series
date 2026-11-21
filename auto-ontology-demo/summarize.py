"""Summarise one demo run's results for the post, and check its answers against the data.

Reads auto-ontology-demo/results/run-N and writes src/data/auto-ontology-run.json: the setup,
how long each step took, every term the draft named with the tables behind it, whether any
term names demand or a lost sale, the coverage check for each question, and each answer with
its SQL. Each answer's SQL is run again on a Postgres copy of Store 014 (given as a psql
connection string) so the post can say whether the number is right.

    python3 auto-ontology-demo/summarize.py <results/run-N> [psql-connection] [--bigger <run> --expert <run>] [--nvidia <run>]

With --bigger and --expert it also records the runs answered by a 7B model: --bigger is a run on the
draft alone, and --expert a run that asked, entered Season 2's knowledge (expert_layer.py) and asked
again. With --nvidia it records a run on NVIDIA's own hosted models that did the same. Every answer's
SQL is re-run on the records too.
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


def read_answers(answers: list, conn: str | None) -> list:
    asked = []
    for a in answers or []:
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
    return asked


def coverage_of(items: list) -> list:
    return [
        {"id": c["id"], "question": c["question"],
         "coverage": ((c.get("result") or {}).get("data") or {}).get("coverage"),
         "uncovered": ((c.get("result") or {}).get("data") or {}).get("uncovered_entities"),
         "matched": [f"{m.get('term')}: {m.get('attribute')}" for m in (((c.get("result") or {}).get("data") or {}).get("candidates") or [])]}
        for c in items or []
    ]


def with_a_7b_model(bigger: Path, expert: Path, conn: str | None) -> dict:
    """The runs answered by a 7B model: on the draft alone, and before and after Season 2's knowledge."""
    setup = load(expert, "setup.json", {})
    entered = load(expert, "expert.json", {})
    instructions = (expert / "expert-instructions.txt").read_text() if (expert / "expert-instructions.txt").exists() else ""
    before = read_answers(load(expert, "answers.json", []), conn)
    pick_osa = next((a for a in before if a["id"] == "on-shelf"), {})
    try:
        pick_osa_percent = f"{round(float(json.loads(pick_osa['rows'][0])[0]['on_shelf_availability']) * 100, 2)}%"
    except Exception:
        pick_osa_percent = None
    return {
        "answer_model": setup.get("answer_model"),
        "draft_model": setup.get("chat_model"),
        "runs": {"draft_alone": load(bigger, "setup.json", {}).get("run_number"), "before_and_after": setup.get("run_number")},
        "draft_alone": read_answers(load(bigger, "answers.json", []), conn),
        "before": before,
        "before_on_shelf_percent": pick_osa_percent,
        "entered": {
            "instructions_chars": entered.get("instructions_chars"),
            "rules_quoted": [r["n"] for r in json.loads((ROOT / "src" / "data" / "ontology.json").read_text())["rules"] if r["text"] in instructions],
            "glossary": entered.get("glossary"),
            "tables_certified": sorted(k for k, v in (entered.get("tables") or {}).items() if v == "certified"),
            "tables_error": entered.get("tables_error"),
            "calculations": entered.get("calculations"),
            "analyses": entered.get("analyses"),
        },
        "after": read_answers(load(expert, "answers-after.json", []), conn),
        "coverage_before": coverage_of(load(expert, "coverage.json", [])),
        "coverage_after": coverage_of(load(expert, "coverage-after.json", [])),
        "days_with_sales": rerun("select count(distinct bill_ts::date) from store.pos_lines where sku_scanned = 'ATTA-WW-5KG' and bill_ts >= '2026-06-01' and bill_ts < '2026-07-01'", conn),
        "instructions": instructions,
    }


def draft_of(folder: Path) -> dict:
    """The terms a run drafted, with the tables behind each, and which of them name the gap."""
    terms = load(folder, "terms.json", []) or []
    details = load(folder, "term-details.json", {}) or {}
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
    return {
        "terms": drafted,
        "term_count": len(drafted),
        "terms_naming_the_gap": [t["name"] for t in drafted if gap_words.search(t["name"] or "")],
        "descriptions_mentioning_the_gap": [t["name"] for t in drafted if gap_words.search(t["description"] or "")],
        "product_terms": [t["name"] for t in drafted if re.match(r"Product( SKU)?( \(|$)", t["name"] or "")],
    }


def with_nvidia_models(folder: Path, conn: str | None) -> dict:
    """A run on NVIDIA's own hosted models: its draft, then the questions before and after Season 2's knowledge."""
    run, setup = load(folder, "run.json", {}), load(folder, "setup.json", {})
    entered = load(folder, "expert.json", {})
    instructions = (folder / "expert-instructions.txt").read_text() if (folder / "expert-instructions.txt").exists() else ""
    draft = draft_of(folder)
    export = run.get("phases", {}).get("export", {})
    rate_limited = folder / "logs" / "rate-limited-lines.txt"
    return {
        "run": setup.get("run_number"), "run_id": setup.get("run_id"),
        "chat_model": setup.get("chat_model"), "embedding_model": setup.get("embedding_model"),
        "rerank_model": setup.get("rerank_model"),
        "phases": {k: {"status": v.get("status"), "minutes": v.get("minutes")} for k, v in run.get("phases", {}).items()},
        "draft_minutes": round(run.get("phases", {}).get("compile", {}).get("minutes") or 0),
        "compile": log_facts(folder),
        "term_count": draft["term_count"],
        "terms_naming_the_gap": draft["terms_naming_the_gap"],
        "descriptions_mentioning_the_gap": draft["descriptions_mentioning_the_gap"],
        "product_terms": draft["product_terms"],
        "terms": draft["terms"],
        "ossie_export_refused": (export.get("ossie_refused") or {}).get("body"),
        "export_files": export.get("files"),
        "rate_limited_log_lines": int(rate_limited.read_text().strip() or 0) if rate_limited.exists() else None,
        "before": read_answers(load(folder, "answers.json", []), conn),
        "entered": {
            "instructions_chars": entered.get("instructions_chars"),
            "rules_quoted": [r["n"] for r in json.loads((ROOT / "src" / "data" / "ontology.json").read_text())["rules"] if r["text"] in instructions],
            "glossary": entered.get("glossary"),
            "tables_certified": sorted(k for k, v in (entered.get("tables") or {}).items() if v == "certified"),
            "tables_error": entered.get("tables_error"),
            "calculations": entered.get("calculations"),
            "analyses": entered.get("analyses"),
        },
        "after": read_answers(load(folder, "answers-after.json", []), conn),
        "coverage_before": coverage_of(load(folder, "coverage.json", [])),
        "coverage_after": coverage_of(load(folder, "coverage-after.json", [])),
    }


def main() -> None:
    args = sys.argv[1:]
    flags = {}
    for flag in ("--bigger", "--expert", "--nvidia"):
        if flag in args:
            i = args.index(flag)
            flags[flag] = Path(args[i + 1])
            del args[i:i + 2]
    folder = Path(args[0])
    conn = args[1] if len(args) > 1 else None
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

    asked = read_answers(answers, conn)

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
        "coverage": coverage_of(coverage),
        "answers": asked,
    }
    if "--bigger" in flags and "--expert" in flags:
        summary["with_a_7b_model"] = with_a_7b_model(flags["--bigger"], flags["--expert"], conn)
    if "--nvidia" in flags:
        summary["with_nvidia_models"] = with_nvidia_models(flags["--nvidia"], conn)
    out = ROOT / "src" / "data" / "auto-ontology-run.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    files = ROOT / "public" / "data" / "auto-ontology"
    files.mkdir(parents=True, exist_ok=True)
    (files / "store014-draft-terms.json").write_text(json.dumps(drafted, indent=2, ensure_ascii=False) + "\n")
    (files / "store014-run.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    if "with_a_7b_model" in summary:
        (files / "store014-expert-instructions.txt").write_text(summary["with_a_7b_model"]["instructions"])
    print(f"{out}: {len(drafted)} terms, {len(coverage)} coverage checks, {len(asked)} answers")


if __name__ == "__main__":
    main()
