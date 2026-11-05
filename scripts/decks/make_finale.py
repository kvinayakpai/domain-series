"""Build the finale deck (Slides artifact data files) from the blog's finale.json."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "decks" / "finale" / "project"
(OUT / "slides").mkdir(parents=True, exist_ok=True)
f = json.loads((ROOT / "src" / "data" / "finale.json").read_text())
J = {j["id"]: j for j in f["joins"]}
T = f["trace"]
H = T["hit"]
SHELF, TRUCK, MONEY = f["incidents"]
A = f["agents"]
GREEN = "#1a9e70"
WORDS = {2: "two", 3: "three", 4: "four", 8: "eight", 12: "twelve"}

SIGN = "font-family:'Anek Latin', Arial, sans-serif"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
SERIF = "font-family:'Literata', Georgia, serif"
INK, PAPER, PANEL, MUTED, RECORD, RED, HL = "#1b2430", "#f5f6f4", "#eceeea", "#59626d", "#2f55a4", "#c8372d", "#ffe14d"
DARK_MUTED = "#a3adb8"


def num(v):
    return f"{v:,}"


def hrs(h):
    return f"{h:.1f} h".replace(".0 h", " h") if h < 10 else f"{round(h)} h"


def section(sid, body, notes, bg=PAPER, fg=INK, gap=48, center=False):
    jc = "justify-content:center;" if center else ""
    return (f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{fg};{SERIF};'
            f'padding:128px 128px 160px;display:flex;flex-direction:column;{jc}gap:{gap}px">\n{body}\n<aside>{notes}</aside>\n</section>\n')


def h2(text, color=INK):
    return f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.05;color:{color}">{text}</h2>'


def foot(text, color=MUTED):
    return f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;{SIGN};font-size:24px;color:{color}">{text}</p>'


slides = {}
copies = [j for j in f["joins"] if j["kind"] == "copy"]
obs = [j for j in f["joins"] if j["kind"] == "observation"]

slides["cover"] = section("cover", "\n".join([
    '<div style="display:flex;flex-direction:column;gap:16px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:{MUTED}">Why Domain Matters: shelf, truck and money, on one map</p>',
    f'<h1 style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{INK}">Who saw what</h1>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">The record says</p>',
    f'<p style="{MONO};font-size:44px;line-height:1.2;color:{RECORD}">The records agree.</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px;align-items:start">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">What actually happened</p>',
    f'<p style="font-size:44px;line-height:1.25;color:{INK};background:{HL};padding:4px 16px">Eight of twelve joins compare a record with its own copy.</p>',
    '</div>',
    foot("kvinayakpai.github.io/domain-series. Every number comes from a synthetic, seeded world."),
]), "This is the last post in the series on why domain knowledge matters, and it puts the three domains on one map. The same fictional supermarket, Store 014 in Jayanagar, Bengaluru, simulated hour by hour through June 2026. The headline: the store's records agree with each other, and two in three of the joins between them compare a record with its own copy.",
    gap=56, center=True)

three = [
    ("The shelf", SHELF["title"], f"{SHELF['when']}. {SHELF['cost']}.", "Availability on the books: 97%"),
    ("The truck", TRUCK["title"], f"{TRUCK['when']}. {TRUCK['cost']}.", "22 June: on time, in full"),
    ("The money", MONEY["title"], f"{MONEY['when']}. ₹{MONEY['cost_inr']:,.2f} taken twice from 24 customers.", "Every bill paid exactly once"),
]
cells = [f'<div style="display:flex;flex-direction:column;gap:16px;border-top:6px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:30px;font-weight:600;color:{MUTED}">{a}</p><p style="{SIGN};font-size:44px;font-weight:700;line-height:1.1">{b}</p><p style="font-size:28px;line-height:1.4">{c}</p><p style="{MONO};font-size:24px;line-height:1.4;color:{RECORD}">{d}</p></div>' for a, b, c, d in three]
slides["three"] = section("three", "\n".join([
    h2("Three failures, one month, every test green"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:64px">', *cells, '</div>',
    foot("Each time, the dashboards were green, the data tests passed, and an AI assistant given the schema said nothing was wrong."),
]), f"The three posts followed three failures through June at Store 014. Bags of 5 kg atta sat in the wrong bay while the shelf stood empty: {SHELF['cost']}. A pallet line held 1 kg packs where every record said 5 kg bags: {TRUCK['cost']}. Twenty-four customers paid twice when the tills gave up on UPI payments their banks had already sent. Each time the dashboards were green, the data tests passed, and an AI assistant given the schema said nothing was wrong. And each time, two of the store's own records disagreed within hours, and nothing joined them.",
    gap=56)

# Hours by joining, days by waiting: three tracks on one axis.
W, MAX = 1664, 72
x = lambda h: min(W, h / MAX * W)
rows = [(SHELF, "5 kg atta in the wrong bay"), (TRUCK, "1 kg packs on a 5 kg line"), (MONEY, "Timeouts the bank had paid (medians)")]
tracks = []
for i, (inc, name) in enumerate(rows):
    y0 = 40 + i * 150
    tracks.append(f'<p style="position:absolute;left:0px;top:{y0 - 40}px;width:1664px;{SIGN};font-size:30px;font-weight:600">{name}</p>')
    tracks.append(f'<div style="position:absolute;left:{x(inc["hours_joined"]):.0f}px;top:{y0 + 18}px;width:{x(inc["hours_found"]) - x(inc["hours_joined"]):.0f}px;height:6px;background:#b9bfb7"></div>')
    tracks.append(f'<div style="position:absolute;left:{x(inc["hours_joined"]) - 16:.0f}px;top:{y0 + 5}px;width:32px;height:32px;border-radius:16px;background:{GREEN}"></div>')
    tracks.append(f'<div style="position:absolute;left:{x(inc["hours_found"]) - 16:.0f}px;top:{y0 + 5}px;width:32px;height:32px;border-radius:16px;background:{RED}"></div>')
    tracks.append(f'<p style="position:absolute;left:{x(inc["hours_joined"]) + 24:.0f}px;top:{y0 + 44}px;width:300px;{SIGN};font-size:30px;font-weight:700;color:{GREEN}">{hrs(inc["hours_joined"])}</p>')
    tracks.append(f'<p style="position:absolute;left:{x(inc["hours_found"]) - 324:.0f}px;top:{y0 + 44}px;width:300px;text-align:right;{SIGN};font-size:30px;font-weight:700;color:{RED}">{hrs(inc["hours_found"])}</p>')
axis = [f'<p style="position:absolute;left:{x(t) - 40:.0f}px;top:470px;width:80px;text-align:center;{SIGN};font-size:24px;color:{MUTED}">{t if t < 72 else "72 h"}</p>' for t in (0, 12, 24, 36, 48, 60, 72)]
slides["time"] = section("time", "\n".join([
    h2("Hours by joining, days by waiting"),
    f'<div style="position:relative;width:{W}px;height:510px">', *tracks,
    f'<div style="position:absolute;left:0px;top:460px;width:{W}px;height:2px;background:#b9bfb7"></div>', *axis, '</div>',
    '<div style="display:flex;gap:48px;align-items:center">'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:28px;height:28px;border-radius:14px;background:{GREEN}"></div><p style="{SIGN};font-size:26px">Two of the store’s records, joined</p></div>'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:28px;height:28px;border-radius:14px;background:{RED}"></div><p style="{SIGN};font-size:26px">Found as the store ran</p></div></div>',
    foot(f"Hours after the shelf emptied, or after the extra debit. {MONEY['found']['never']} of the customers charged twice never complained."),
]), f"For each failure, two times on one clock. The silence in 5 kg atta sales with stock on the books showed the empty shelf {hrs(SHELF['hours_joined'])} after it emptied; staff found the bags {hrs(SHELF['hours_found'])} after. The trace across the warehouse and the store names the wrong pallet line {hrs(TRUCK['hours_joined'])} after the 5 kg shelf emptied; the manager's count found it {hrs(TRUCK['hours_found'])} after. Matching each timeout to the provider's next-morning file finds an extra charge a median {hrs(MONEY['hours_joined'])} after the debit; complaints took a median {hrs(MONEY['hours_found'])}, and {MONEY['found']['never']} customers never complained. Hours if you join, days if you wait.",
    gap=32)

ex = [
    (f"{J['picks-notice']['agree']} of {J['picks-notice']['compared']}", "shipping notice lines match the pick confirmations"),
    (f"{J['notice-receipts']['agree']} of {J['notice-receipts']['compared']}", "goods receipts match the notice"),
    (f"{J['book-ledger']['agree']} of {J['book-ledger']['compared']}", "item-days of book stock equal the sum of receipts, sales, write-offs and counts"),
    (f"{num(J['payments-provider']['agree'])} of {num(J['payments-provider']['compared'])}", "approved UPI payments match the provider’s report"),
]
exo = [
    (f"{J['book-counts']['agree']} of {J['book-counts']['compared']}", "stock counts agree with the books"),
    (f"{J['book-audits']['agree']} of {J['book-audits']['compared']}", "shelf audits agree with the books"),
    (f"{J['receipts-counts']['agree']} of {J['receipts-counts']['compared']}", "receipts survive the next count"),
    (f"{J['timeouts-provider']['agree']} of {J['timeouts-provider']['compared']}", "timeouts agree with the provider’s report"),
]
rowsc = "".join(f'<div style="display:grid;grid-template-columns:340px 1fr;gap:24px;border-top:2px solid #d5d9d4;padding:14px 0 0 0"><p style="{SIGN};font-size:40px;font-weight:700;color:{MUTED}">{a}</p><p style="font-size:26px;line-height:1.35">{b}</p></div>' for a, b in ex)
rowso = "".join(f'<div style="display:grid;grid-template-columns:200px 1fr;gap:24px;border-top:2px solid #d5d9d4;padding:14px 0 0 0"><p style="{SIGN};font-size:40px;font-weight:700;color:{RED}">{a}</p><p style="font-size:26px;line-height:1.35">{b}</p></div>' for a, b in exo)
slides["joins"] = section("joins", "\n".join([
    h2("Join the records two at a time"),
    '<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:80px;align-items:start">',
    f'<div style="display:flex;flex-direction:column;gap:12px"><p style="{SIGN};font-size:34px;font-weight:700">{WORDS[len(copies)].capitalize()} always agree: copies</p>{rowsc}</div>',
    f'<div style="display:flex;flex-direction:column;gap:12px"><p style="{SIGN};font-size:34px;font-weight:700;color:{RED}">{WORDS[len(obs)].capitalize()} sometimes disagree</p>{rowso}</div>',
    '</div>',
    foot(f"{len(f['joins'])} joins between Store 014’s records in June. The eight that agree hold {num(f['summary']['rows_compared_in_copies'])} rows between them, and never disagree."),
]), f"Take every pair of June's records that share a key and count how often they agree. Eight joins agree on every row: the notice and the picks, the receipts and the notice, the book stock and the records it is summed from, the approved UPI payments and the provider's report. Four sometimes disagree: the books against the stock counts, {J['book-counts']['agree']} of {J['book-counts']['compared']}; against the shelf audits, {J['book-audits']['agree']} of {J['book-audits']['compared']}; receipts against the next count, {J['receipts-counts']['agree']} of {J['receipts-counts']['compared']}; and the timeouts against the provider's report, {J['timeouts-provider']['agree']} of {J['timeouts-provider']['compared']}.",
    gap=40)

slides["copy"] = section("copy", "\n".join([
    f'<h2 style="{SIGN};font-size:96px;font-weight:700;line-height:1.08;color:#e6eaee;width:1500px">A test on a copy can only pass.</h2>',
    '<p style="font-size:38px;line-height:1.45;width:1500px">The notice is written from the picks, the receipt by scanning a label against the notice, the book stock from the receipts and the sales. That is why every pipeline in this series was green.</p>',
    f'<p style="font-size:38px;line-height:1.45;width:1500px;color:{HL}">Each of June’s three failures sits on one of the four joins that disagree. On each, one side looks at the world.</p>',
]), "They agree because one record was written from the other, or both from the same event. A data test on such a join can only pass, and that is why every pipeline in this series was green. Those tests are still worth running: they catch lost loads and broken keys. They cannot catch a wrong pallet, because the mistake is in both records. Each of June's failures sits on one of the four joins that disagree, and on each of those, one side looks at the world: someone counting the shelf, someone looking at it, the customer's bank.",
    bg=INK, fg="#e6eaee", gap=56, center=True)

grid_rows = [
    ("The KPI", ["OTIF", "On-shelf availability", "Payment success"], INK, True),
    ("reads", [f"Goods receipts: a copy of the notice ({J['notice-receipts']['agree']} of {J['notice-receipts']['compared']})",
               f"Book stock: a running sum ({J['book-ledger']['agree']} of {J['book-ledger']['compared']})",
               f"Till payments: the provider’s answer, or a timeout ({num(J['payments-provider']['agree'])} of {num(J['payments-provider']['compared'])})"], RECORD, False),
    ("contradicted by", [f"Stock counts: {J['receipts-counts']['agree']} of {J['receipts-counts']['compared']} receipts survive",
                         f"Counts {J['book-counts']['agree']} of {J['book-counts']['compared']}; audits {J['book-audits']['agree']} of {J['book-audits']['compared']}",
                         f"Provider’s report: {J['timeouts-provider']['agree']} of {J['timeouts-provider']['compared']} timeouts agree"], RED, False),
    ("which looks at", ["The shelf and the backroom", "The shelf", "The customer’s bank account"], INK, False),
]
g = [f'<div style="display:grid;grid-template-columns:260px 1fr 1fr 1fr;gap:32px;border-top:2px solid #d5d9d4;padding:16px 0 0 0"><p style="{SIGN};font-size:26px;color:{MUTED}">{lab}</p>'
     + "".join(f'<p style="{SIGN};font-size:{34 if big else 27}px;font-weight:{700 if big else 500};line-height:1.3;color:{c}">{v}</p>' for v in vals) + '</div>'
     for lab, vals, c, big in grid_rows]
g.insert(0, '<div style="display:grid;grid-template-columns:260px 1fr 1fr 1fr;gap:32px"><p style="font-size:26px"> </p>'
         + "".join(f'<p style="{SIGN};font-size:30px;font-weight:700;color:{MUTED}">{d}</p>' for d in ("The truck", "The shelf", "The money")) + '</div>')
slides["map"] = section("map", "\n".join([
    h2("Who saw what"), *g,
    f'<div style="display:flex;gap:24px;align-items:center"><p style="{SIGN};font-size:30px;font-weight:700;background:{HL};padding:4px 16px">Nothing looked at what was on a pallet.</p><p style="font-size:26px;color:{MUTED}">None of June’s {f["evidence"]["pallets"]["n"]} pallets was weighed or case-scanned.</p></div>',
]), f"Draw the records as a map: what writes each one, what it looks at, and which KPI reads it. The KPIs read copies: OTIF reads the goods receipts, on-shelf availability reads the book stock, payment success reads the till payments. The records that look at the world, counts, audits and the provider's report, are read by no headline KPI. And one thing had no record looking at it at all: what was on a pallet. None of June's {f['evidence']['pallets']['n']} pallets was weighed or case-scanned, all {f['evidence']['picks_by_slot_scan']['n']} picks were confirmed by scanning the slot, and all {f['evidence']['receipts_by_label']['n']} receipts by scanning the label. Most of the map can be drawn from the schema; the edges to the world are what only domain knowledge can draw.",
    gap=28)

hops = [
    ("Store, Tue 23 Jun, 20:00", "Till lines and book stock", f"No 5 kg sale since {T['silence']['start'][11:16]}; {T['silence']['expected_at_flag']} expected; {T['silence']['book_at_flag']} on the books"),
    ("Store, Mon 22 Jun, 06:12", f"Goods receipt {H['grn_id']}, line {H['line']}", f"{H['noticed_units']} bags booked by scanning the pallet label against the notice"),
    ("Warehouse, Mon 22 Jun", f"Shipping notice {H['shipment_id']}, line {H['line']}", f"{H['cases_confirmed']} cases of 5 kg atta on pallet …{H['sscc'][-4:]}"),
    ("Warehouse, Mon 22 Jun, 03:00", "Pick confirmation", f"{H['cases_confirmed']} cases from slot {H['pick_slot']}, by a {H['confirmed_by']}"),
    ("Warehouse, Tue 23 Jun, 14:20", f"Correction, slot {H['short_slot']}", f"1 kg atta: −{abs(H['short_cases'])} cases (−{abs(H['short_units'])} packs), “{H['reason']}”"),
]
hh = [f'<div style="display:grid;grid-template-columns:420px 1fr;gap:32px;border-top:2px solid #d5d9d4;padding:12px 0 0 0"><p style="{SIGN};font-size:24px;color:{MUTED}">{a}</p><div style="display:flex;flex-direction:column;gap:4px"><p style="{SIGN};font-size:28px;font-weight:600">{b}</p><p style="{MONO};font-size:24px;color:{RECORD}">{c}</p></div></div>' for a, b, c in hops]
slides["trace"] = section("trace", "\n".join([
    h2("Across the shelf and the truck"), *hh,
    (f'<div style="display:flex;flex-direction:column;gap:8px;align-items:start"><p style="font-size:32px;line-height:1.3;background:{HL};padding:4px 14px">Line {T["names"]["line"]} of {T["names"]["shipment_id"]} held 1 kg atta: {abs(T["names"]["units"])} packs. Right.</p>'
     f'<p style="font-size:30px;line-height:1.4">Named at 20:00 on Tuesday: {round(T["hours_before_pair"])} hours before the warehouse’s pair, {round(T["hours_before_count"])} before the store’s count.</p></div>'),
]), f"A map earns its keep when a question crosses a boundary between departments. At 8 pm on Tuesday 23 June the store's records show 5 kg atta silent since 4 pm with {T['silence']['book_at_flag']} on the books. Follow the map: the books came from the last receipt; the receipt copied the notice; the notice copied the pick, confirmed by a scan of slot {H['pick_slot']}; and that afternoon the warehouse found the slot next to it, {H['short_slot']}, sixteen cases of 1 kg short. One query across five records and two buildings names line {T['names']['line']} of {T['names']['shipment_id']}, and the answer key agrees: it held {T['answer_key']['units']} packs of 1 kg. It does so {round(T['hours_before_pair'])} hours before the warehouse's own corrections pair up and {round(T['hours_before_count'])} hours before the store's count.",
    gap=24)

slides["alone"] = section("alone", "\n".join([
    h2("Neither domain’s rules get there alone"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:start">',
    f'<div style="display:flex;flex-direction:column;gap:16px;border-top:6px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:34px;font-weight:700">The retail rules</p><p style="font-size:30px;line-height:1.45">The scripted agent asked for a shelf check at 22:00 on Tuesday. On Wednesday morning it found the shelf and the backroom empty, corrected the book and reordered: 22 bags lost instead of 72.</p><p style="font-size:30px;line-height:1.45;color:{RED}">It never learned why. The 160 extra packs of 1 kg, the warehouse’s slots and the delivery still counted in full were outside its rules.</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:16px;border-top:6px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:34px;font-weight:700">The logistics rules</p><p style="font-size:30px;line-height:1.45">Pair the warehouse’s corrections: equal and opposite, neighbouring slots, within a week.</p><p style="font-size:30px;line-height:1.45;color:{RED}">The second correction comes on Thursday at 10:00, {round(T["hours_before_pair"])} hours after the map could have named the line.</p></div>',
    '</div>',
    foot("The agent is scripted, so the rerun can be repeated: same customers, same trucks, seed 42."),
]), "Neither domain's rules get there alone that evening. The scripted replenishment agent from the retail post, rerun with the retail rules, asked for a shelf check at 22:00 on Tuesday. On Wednesday morning staff found the shelf and the backroom empty, the agent corrected the book, and the store reordered that night: 22 bags lost instead of 72. It never learned why. Its check counted the 5 kg bay; the 160 extra packs of 1 kg, the warehouse's slots and a delivery the scorecard still counts as in full were outside its rules. The logistics rules pair the warehouse's corrections, and the second one comes on Thursday.",
    gap=48)

led = [(SHELF["title"], f"{SHELF['cost']}", SHELF["ledger"]), (TRUCK["title"], f"{TRUCK['cost']}", TRUCK["ledger"]),
       (MONEY["title"], f"₹{MONEY['cost_inr']:,.2f} taken twice", MONEY["ledger"])]
lt = [f'<table style="font-size:28px;color:{INK}">',
      f'<tr><th style="width:28%;text-align:left;font-weight:600;color:{MUTED}">Failure</th><th style="width:22%;text-align:left;font-weight:600;color:{MUTED}">What it cost</th><th style="width:50%;text-align:left;font-weight:600;color:{MUTED}">What the ledger showed</th></tr>']
lt += [f'<tr><td>{a}</td><td>{b}</td><td>{c.replace(chr(39), "’")}</td></tr>' for a, b, c in led]
lt.append('</table>')
slides["ledger"] = section("ledger", "\n".join([h2("What the ledger showed"), *lt,
    foot("Bags at the shelf price customers would have paid. Corrections at cost, as the store books them.")]),
    "Add the ledger to the records that agree with each other. The bags customers wanted and could not buy appear in no record at all. The four corrections from the wrong pallet net to eighty rupees. The double charges arrived as UPI credits like any other, and the ones nobody claimed sat in suspense.",
    gap=40)

asst = A["assistants"]
rep = A["replenishment"]
slides["agents"] = section("agents", "\n".join([
    h2("Give the agent the map", "#e6eaee"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:64px">',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {GREEN};padding:24px 0 0 0"><p style="{SIGN};font-size:96px;font-weight:700;line-height:1;color:#e6eaee">{asst["naive"]} → {asst["domain"]}</p><p style="{SIGN};font-size:28px;color:{DARK_MUTED}">of {asst["of"]} questions right, schema only → with domain layers, across the three posts</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {GREEN};padding:24px 0 0 0"><p style="{SIGN};font-size:96px;font-weight:700;line-height:1;color:#e6eaee">{round(rep["lost_bags_mean"]["naive"])} → {round(rep["lost_bags_mean"]["domain"])}</p><p style="{SIGN};font-size:28px;color:{DARK_MUTED}">bags of 5 kg atta lost in an average June, a replenishment agent reading the KPIs → reading them with domain rules</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid #8db0f0;padding:24px 0 0 0"><p style="{SIGN};font-size:96px;font-weight:700;line-height:1;color:#e6eaee">65% → 98–100%</p><p style="{SIGN};font-size:28px;color:{DARK_MUTED}">current AI models on an insurer’s business questions: from the raw tables → with a semantic layer of the business’s terms and rules (dbt Labs, 2026)</p></div>',
    '</div>',
    foot("The series’ assistant and agent are scripted so every run can be repeated. dbt Labs (7 April 2026), Semantic Layer vs. Text-to-SQL: 2026 benchmark.", DARK_MUTED),
]), f"Agents act on records, so an agent's mistakes are its records' mistakes, made at the speed of software. Across the three posts, the same scripted assistant answered {asst['naive']} of {asst['of']} questions right given the schema, and all {asst['of']} given a domain layer. A scripted replenishment agent lost {round(rep['lost_bags_mean']['naive'])} bags of 5 kg atta in an average June reading the KPIs as reported, and {round(rep['lost_bags_mean']['domain'])} reading them with the domain rules. Outside this synthetic world, in dbt Labs’ 2026 benchmark, current AI models answered 65 percent of business questions about an insurance database correctly from the raw tables, and 98 to 100 percent once the business’s terms and rules were written down as data models and a semantic layer.",
    bg=INK, fg="#e6eaee", gap=56, center=True)

layer = [
    "Every record, the event that writes it, and what it looks at in the world",
    "Every join, and how often it agrees",
    "Every KPI, the record it reads, and the observation that can contradict it",
    "The rules for reading a silence or a timeout as a question",
]
slides["layer"] = section("layer", "\n".join([
    h2("A domain layer is the map, as data"),
    '<div style="display:flex;flex-direction:column">',
    *[f'<div style="display:grid;grid-template-columns:72px 1fr;gap:24px;border-top:2px solid #d5d9d4;padding:22px 0 22px 0"><p style="{SIGN};font-size:38px;font-weight:700;line-height:1.2;color:{RECORD}">{i}</p><p style="font-size:36px;line-height:1.3">{q}</p></div>' for i, q in enumerate(layer, 1)],
    '</div>',
    f'<p style="{MONO};font-size:28px;color:{RECORD}">kvinayakpai.github.io/domain-series/data/india-grocery/store-014-map.json</p>',
    foot("Store 014’s map, with the SQL for every join, next to the records it describes."),
]), "A domain layer for an agent is this map, as data: every record, the event that writes it, and what it looks at in the world; every join, and how often it agrees; every KPI, the record it reads, and the observation that can contradict it; and the rules for reading a silence or a timeout as a question. Store 014's map is free to download as JSON, next to the records it describes, with the SQL for every join.",
    gap=40)

questions = [
    "For each KPI an agent acts on, which record does it read, and is that record a copy?",
    "Which of our joins have never disagreed, and do we know why?",
    "What in our business does no record look at?",
    "When two departments’ records disagree, who joins them, and how soon?",
    "Can our agents read the map: what each record sees, and what can contradict it?",
]
slides["questions"] = section("questions", "\n".join([
    h2("Five questions to ask your team"),
    '<div style="display:flex;flex-direction:column">',
    *[f'<div style="display:grid;grid-template-columns:72px 1fr;gap:24px;border-top:2px solid #d5d9d4;padding:22px 0 22px 0"><p style="{SIGN};font-size:38px;font-weight:700;line-height:1.2;color:{RECORD}">{i}</p><p style="font-size:36px;line-height:1.3">{q}</p></div>' for i, q in enumerate(questions, 1)],
    '</div>',
    foot("For data and AI leaders."),
]), "For data and AI leaders, five questions to take back to your team. For each KPI an agent acts on, which record does it read, and is that record a copy? Which of our joins have never disagreed, and do we know why? What in our business does no record look at? When two departments' records disagree, who joins them, and how soon? And can our agents read the map: what each record sees, and what can contradict it?",
    gap=48)

slides["close"] = section("close", "\n".join([
    f'<h2 style="{SIGN};font-size:88px;font-weight:700;line-height:1.08;color:#e6eaee;width:1500px">Every record was right about what it saw. Join the ones that look at the world.</h2>',
    '<div style="display:flex;flex-direction:column;gap:16px">',
    '<p style="font-size:34px;line-height:1.45">The series, the KPIs x-rayed, the records and the map:</p>',
    f'<p style="{MONO};font-size:36px;color:#8db0f0"><a href="https://kvinayakpai.github.io/domain-series/who-saw-what/"><span style="color:#8db0f0">kvinayakpai.github.io/domain-series</span></a></p>',
    '</div>',
    f'<div style="display:flex;flex-direction:column;gap:8px;border-left:6px solid {HL};padding:8px 0 8px 32px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:{DARK_MUTED}">One store, one month</p>',
    '<p style="font-size:36px;line-height:1.35">The shelf, the truck and the money. Eighteen KPIs, each measured twice.</p>',
    '</div>',
]), "Every record was right about what it saw. The work is to join the ones that look at the world, and to give agents the map that says which ones those are. The series site has the three domain posts with their technical companions and notebooks, eighteen KPIs x-rayed, the records and answer keys, and the map.",
    bg=INK, fg="#e6eaee", gap=56, center=True)

order = ["cover", "three", "time", "joins", "copy", "map", "trace", "alone", "ledger", "agents", "layer", "questions", "close"]
for sid in order:
    (OUT / "slides" / f"{sid}.html").write_text(slides[sid])
for p in (OUT / "slides").glob("*.html"):
    if p.stem not in order:
        p.unlink()
prev = OUT / "deck.json"
deck = json.loads((prev if prev.exists() else ROOT / "decks" / "payments" / "project" / "deck.json").read_text())
if not prev.exists():
    deck["createdOnFiles"] = {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
deck["title"] = "Why Domain Matters: Who saw what"
deck["order"] = order
deck["sections"] = {
    "s1": {"description": "Three failures, one month, and how long each took to find", "start": "cover"},
    "s2": {"description": "Join the records two at a time: copies and observations, and the map", "start": "joins"},
    "s3": {"description": "Across the shelf and the truck, and what the ledger showed", "start": "trace"},
    "s4": {"description": "Give the agent the map, and questions for leaders", "start": "agents"},
}
prev.write_text(json.dumps(deck))
print(f"wrote {OUT.relative_to(ROOT)}: {len(order)} slides")
