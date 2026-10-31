"""Write Store 014's domain layer as one YAML file, and a blank template for your own.

    python3 scripts/kit/make_layer.py

Writes public/kit/store-014-domain-layer.yaml, from the map of the records (store-014-map.json) and
the three domain layers the series gave its scripted assistant (src/data/*-ai.json), and
public/kit/domain-layer-template.yaml. Strings are written as JSON strings, which YAML reads as-is.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "data"
DATA = ROOT / "public" / "data" / "india-grocery"
OUT = ROOT / "public" / "kit"
SITE = "https://kvinayakpai.github.io/domain-series/"


RESERVED = {"on", "off", "yes", "no", "y", "n", "true", "false", "null"}  # YAML 1.1 reads these as booleans


def q(s) -> str:
    return json.dumps(s, ensure_ascii=False)


def emit(obj, indent: int = 0) -> list[str]:
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            plain = k.replace("_", "").replace("-", "").isalnum() and k.lower() not in RESERVED
            key = k if plain else q(k)
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{key}:")
                lines += emit(v, indent + 1)
            else:
                lines.append(f"{pad}{key}: {scalar(v)}")
    else:
        for v in obj:
            if isinstance(v, dict):
                sub = emit(v, indent + 1)
                lines.append(f"{pad}- {sub[0].strip()}")
                lines += sub[1:]
            else:
                lines.append(f"{pad}- {scalar(v)}")
    return lines


def scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (list, dict)):
        return "[]" if isinstance(v, list) else "{}"
    return q(v)


def main() -> None:
    m = json.loads((DATA / "store-014-map.json").read_text())
    layers = {d: json.loads((SRC / f"{d}-ai.json").read_text())["assistant"]["domain_layer"] for d in ("retail", "logistics", "payments")}
    tables = {d: json.loads((SRC / f"{d}-ai.json").read_text())["assistant"]["schema_only_tables"] for d in layers}
    layer = {
        "about": ("Store 014's domain layer, as the series Why Domain Matters built it: what writes each record and what it "
                  "looks at, how often each join agrees, which record each headline KPI reads and what can contradict it, "
                  "and the definitions, rules and views the scripted assistant was given. Give it to an agent with the schema. "
                  f"Built from {SITE}data/india-grocery/store-014-map.json and the three technical companions."),
        "records": [{"id": r["id"], "name": r["name"], "file": r["file"], "written_by": r["written_by"],
                     "looks_at": [f"{x['thing']}{' (in part)' if x['how'] == 'part' else ''}" for x in r["looks_at"]],
                     **({"sees": r["sees"]} if "sees" in r else {})} for r in m["records"]],
        "unseen": [t["id"] for t in m["things"] if not t["looked_at_by"]],
        "joins": [{"id": j["id"], "records": [j["a"], j["b"]], "joined_on": j["how"], "agree": f"{j['agree']} of {j['compared']}",
                   "kind": j["kind"]} for j in m["joins"]],
        "kpis": [{"id": k["id"], "name": k["name"], "reads": k["reads"], "contradicted_by": k["contradicted_by"], "rule": k["rule"]}
                 for k in m["kpis"]],
        "all_kpis": f"{SITE}kpis/domain-kpis.yaml",
        "definitions": {d: layers[d]["definitions"] for d in layers},
        "rules": {"across": m["rules"], **{d: layers[d]["rules"] for d in layers}},
        "views": {d: layers[d]["views"] for d in layers},
        "views_sql": f"{SITE}kit/store-014-dbt/models/domain/",
        "tables": {d: {"in_the_schema": tables[d], "added_by_the_layer": layers[d]["tables_added"]} for d in layers},
    }
    head = ["# Store 014's domain layer. " + SITE + "kit/",
            "# Strings are JSON strings, which YAML reads as they are."]
    (OUT / "store-014-domain-layer.yaml").write_text("\n".join(head + emit(layer)) + "\n")

    template = """# A domain layer: what an assistant or agent needs besides the schema.
# Fill one in for the records behind a KPI your agents act on. Store 014's, filled in, is at
# https://kvinayakpai.github.io/domain-series/kit/store-014-domain-layer.yaml

records:
  # One entry per table or file. The question for each: what in the world does it look at?
  - id: goods_receipts
    written_by: "a scan of the pallet label, matched to the supplier's shipping notice"
    looks_at: []            # nothing: it copies the notice. A case scan would look at the pallet.
    copies: [shipping_notice]
  - id: stock_counts
    written_by: "staff counting the shelf and the backroom"
    looks_at: [shelf, backroom]

unseen:
  # Things in the world no record looks at. Name them; that is where a failure can hide longest.
  - what_is_on_a_pallet

joins:
  # Every pair of records that share a key, and how often they agree. A join that always agrees
  # is a copy, and a test on it can only pass. Run the counts; do not assume them.
  - records: [shipping_notice, goods_receipts]
    joined_on: "shipment and line"
    agree: "70 of 70"
    kind: copy
  - records: [inventory_book, stock_counts]
    joined_on: "item"
    agree: "4 of 25"
    kind: observation

kpis:
  # The record each KPI reads, the observations that can contradict it, and the rule for an agent.
  - id: on_shelf_availability
    reads: [inventory_book]
    contradicted_by: [shelf_audits, stock_counts, till_lines]
    rule: "Book stock is a belief. When an item stops selling while the books show stock, ask for a shelf check."
    two_numbers:
      reported: "share of open hours with stock on the books"
      observed: "share of open hours with the item on the shelf, from audits and censored sales"
    time_to_find: "open hours from the shelf emptying to someone knowing"

definitions:
  # Terms whose meaning in the records differs from their meaning in the world.
  sales: "Units the tills scanned. Demand only while the shelf had the item."

rules:
  # Short, testable instructions. Each should be a test in your pipeline too.
  - "A timeout is a question, not a failure. Match it to the final status before acting."

views:
  # Views the layer adds, by name, with what each holds. Keep their SQL with your models.
  censored_hours: "open hours with no stock on the books, or a silence longer than the usual rate allows"
"""
    (OUT / "domain-layer-template.yaml").write_text(template)
    print(f"wrote {(OUT / 'store-014-domain-layer.yaml').relative_to(ROOT)} and {(OUT / 'domain-layer-template.yaml').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
