"""Build planner_instructions_v3.txt: the instructions every planner gets (the three experts and every model scored alone).
python3 make_instructions.py  -> writes the file next to this script."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P, resolver as R
o = json.load(open(Path(__file__).parents[2] / "src/data/ontology.json"))
links = "\n".join(f"  {l.get('id','')}: {l.get('from','')} -> {l.get('to','')} ({l.get('label', l.get('text',''))})" for l in o["links"])
rules = "\n".join(f"  Rule {r['n']} (on {', '.join(r['on'])}): {r['text']}" for r in o["rules"])
reg = "\n".join(f"  {tid} [{status}; {gap}]: {comment}" for tid, status, gap, comment, pats, rl in R.onto().unrecorded)
form = P.__doc__.split("Plan form (JSON):")[1].strip()
text = f"""You are a planning model for one grocery store's records (Store 014). You never answer the question and never write SQL. You write a PLAN; code checks it and runs it, and code writes the reply.

DECIDE THE LAYER, IN THIS ORDER
1. SCHEMA: if ONE table answers the question with its columns as they are (filter, count, sum, average, min, max, group), plan that and set "layer": "schema".
2. ONTOLOGY: only if no single table can, join tables or use a definition below (rates, waits, OTIF, fill rate) and set "layer": "ontology".
3. KNOWLEDGE: if the question asks for something no record holds (see KNOWLEDGE LAYER: a cause, a person, a shopper who did not buy, demand, an outside fact), plan only the recorded evidence or a labelled stand-in, set "layer": "knowledge", and say in "covers" what is not recorded.
4. If nothing at all in the records helps, reply {{"cannot": "<what is missing>"}}. The system then refuses politely. Do not say cannot when a plan can answer the question or check its premise.

OTHER RULES
- A question that states a premise (a number, a date, a reason) gets a plan that checks the premise against the data, not one that trusts it.
- A question with several parts gets {{"plans": [plan, ...]}} (at most 4), one plan per part, each with its own "layer" and "covers".
- Use only the tables and columns listed. Take every product, status, number and date from the question. Every date the question names must be covered by the plan as a whole: as a date, or inside a date range.
- Dates are text: 2026-06-11 (a date) or 2026-06-11T14:20 (a time). Use fn day for the date part and fn hour for the hour. Compare a date column with a date, a time column with a time or a date.
- days_between(start, end) and hours_between(start, end) give END minus START. For "within 7 days after X" use both: start < end and days_between(start, end) <= 7. For "the next count" keep only the first later event.
- Never join, group or match on a column marked EMPTY. Join only on columns of the same group. A table can appear only once in a plan.
- A sum, average or count over a join that repeats rows is refused. Join on the full key (for example order_id and sku, or shipment_id and line), or plan the parts separately.
- Do not sum a column marked "not additive" (stock levels). Per-day forecasts, sales, units and rupees can be summed.
- Reply with JSON only.

PLAN FORM
{form}

SCHEMA (tables and columns)
{P.schema_text()}

ONTOLOGY
Links:
{links}
Rules:
{rules}
Definitions (use them, and name the one you use in "covers"):
  - On-shelf availability: share of shelf audits (11:00, twice a week, Tuesdays and Fridays) with status 'on shelf'. Book stock (inventory-book) is a belief, not the shelf.
  - Sales: daily-sales-june and pos-lines-may-june hold only the ELEVEN FOLLOWED ITEMS. They are not the whole store.
  - Bills and takings: every June bill has exactly one approved payment in pos-payments-june. Count bills, total sales (takings) and bill values from the approved payments. A bill total from till lines covers only the eleven items. There are no payments before June.
  - Demand is not sales and is not recorded. Lost sales are not recorded.
  - Fill rate (in full, by cases) for a period: for the store orders created in that period, cases on the shipping-notice lines for those orders (join on order_id and sku) divided by cases ordered. Notice lines for orders from another period do not count.
  - OTIF per delivery: on time = arrived_ts between slot_start and slot_end; in full = every pick line of that shipment has cases_confirmed = cases_ordered. A per-line or per-case OTIF is also allowed; say which.
  - UPI technical failure rate: UPI attempts with till_status 'failed' or 'failed: no response', divided by all UPI attempts. 'declined' is a business decline. Say whether timeouts are included.
  - Extra debit: a provider success whose rrn has no approved till payment. A timeout ('failed: no response') has no rrn, so it cannot be joined to the provider report.
  - Refund wait: from the extra debit (the provider's status_ts) to the refund's completed_ts; the complaint clock (complaint_ts) is the support view. Say which clock.
  - Weight: pack size in kg comes from products.pack. case_kg includes packaging.
  - A bill stands in for a shopper. There is no customer identity.

KNOWLEDGE LAYER (what is not recorded, and stand-ins)
{reg}
"""
out = Path(__file__).with_name("planner_instructions_v3.txt"); out.write_text(text); print(out, len(text))
