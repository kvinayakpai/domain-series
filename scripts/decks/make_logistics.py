"""Build the logistics deck (Slides artifact data files) from the blog's logistics.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "decks" / "logistics" / "project"
(OUT / "slides").mkdir(parents=True, exist_ok=True)
d = json.loads((ROOT / "src" / "data" / "logistics.json").read_text())
S = {s["key"]: s for s in d["scenarios"]}
A = S["none|label"]
st = d["story"]
ep = st["episode"]
k = A["kpis"]
r = ep["responses"]
pick = next(p for p in st["picks"] if p["sku"] == "ATTA-WW-5KG")
pallet = next(p for p in st["pallets"] if p["sscc"] == st["line"]["sscc"])
light = pick["cases_confirmed"] * (d["case_kg"]["ATTA-WW-5KG"] - d["case_kg"]["ATTA-WW-1KG"])
cost = d["costs"]
five = next(c for c in st["corrections"] if c["sku"] == "ATTA-WW-5KG")
one = next(c for c in st["corrections"] if c["sku"] == "ATTA-WW-1KG")


def pct(v):
    return f"{round(v * 100)}%"


def inr(v):
    return f"{'−' if v < 0 else ''}₹{abs(round(v)):,}"


def plus(v):
    return f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(round(v)):,}"


SIGN = "font-family:'Anek Latin', Arial, sans-serif"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
SERIF = "font-family:'Literata', Georgia, serif"
INK, PAPER, PANEL, MUTED, RECORD, RED, HL = "#1b2430", "#f5f6f4", "#eceeea", "#59626d", "#2f55a4", "#c8372d", "#ffe14d"


def section(sid, body, notes, bg=PAPER, fg=INK, gap=48, center=False):
    jc = "justify-content:center;" if center else ""
    return (f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{fg};{SERIF};'
            f'padding:128px 128px 160px;display:flex;flex-direction:column;{jc}gap:{gap}px">\n{body}\n<aside>{notes}</aside>\n</section>\n')


def h2(text, color=INK):
    return f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.05;color:{color}">{text}</h2>'


def foot(text):
    return (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;{SIGN};font-size:24px;color:{MUTED}">'
            f'{text}</p>')


slides = {}

slides["cover"] = section("cover", "\n".join([
    '<div style="display:flex;flex-direction:column;gap:16px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:{MUTED}">Why Domain Matters, part 2</p>',
    f'<h1 style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{INK}">Logistics and supply chain</h1>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">The record says</p>',
    f'<p style="{MONO};font-size:44px;line-height:1.2;color:{RECORD}">Delivered on time, in full.</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px;align-items:start">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">What actually happened</p>',
    f'<p style="font-size:44px;line-height:1.25;color:{INK};background:{HL};padding:4px 16px">One pallet line held the wrong pack size.</p>',
    '</div>',
    foot("kvinayakpai.github.io/domain-series. Every number comes from a synthetic, seeded world."),
]), "This is the second post in the series on why domain knowledge matters, set in the same synthetic world as the first: a fictional supermarket in Jayanagar, Bengaluru, and the warehouse in Hoskote that supplies it, simulated hour by hour through June 2026. The headline is the whole story: every record says a delivery arrived on time and in full, and one line on its first pallet held the wrong pack size.",
    gap=56, center=True)

slides["scene"] = section("scene", "\n".join([
    f'<p style="{SIGN};font-size:32px;font-weight:500;color:#a3adb8">Monday 22 June, 6:12 am. Store 014, Jayanagar.</p>',
    f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.1;color:#e6eaee">The truck made its slot. Every record says the delivery was in full.</h2>',
    '<div style="background:#222c37;border-left:6px solid #8db0f0;padding:32px 40px;width:1100px">',
    f'<p style="{MONO};font-size:32px;line-height:1.5;color:#8db0f0">Goods receipt {st["receipt"]["grn_id"]}, 06:12<br>Pallet …{st["line"]["sscc"][-4:]} scanned, notice matched<br>Line 1: atta 5 kg, {st["line"]["cases"]} cases, {st["line"]["units"]} bags<br>Discrepancies: none</p>',
    '</div>',
    f'<p style="font-size:32px;line-height:1.45;color:#e6eaee;width:1400px">On line 1, the {st["line"]["cases"]} bales hold 1 kg packs, {st["actual"]["units_actual"]} of them. The 5 kg bags are still in the warehouse.</p>',
]), f"Monday 22 June, twelve minutes past six. The warehouse truck backs into Store 014’s receiving bay, twelve minutes into its six-to-six-thirty slot. The receiving clerk scans the two pallet labels; the handheld matches them to the warehouse’s shipping notice, and the store’s books go up by exactly what the notice lists, including {st['line']['units']} bags of 5 kg atta. No discrepancies. By every record, the delivery is on time and in full. But the {st['line']['cases']} bales on line 1 hold 1 kg packs, {st['actual']['units_actual']} of them. The 5 kg bags are still in the warehouse.",
    bg=INK, fg="#e6eaee", center=True)

late = [x for x in A["by_shipment"] if not x["in_slot"]]
short = [x for x in A["by_shipment"] if not x["in_full_notice"]]
rows = [
    ("DC shift supervisor", "Every line picked and confirmed by a scan; two count variances in the atta bay, both corrected", "“A clean night’s picking.”"),
    ("Transport manager", f"Left 04:30, arrived 06:12, inside the slot; {k['in_slot']} of {k['shipments']} mornings on time", "“TRK-07 made its slot.”"),
    ("Receiving clerk", "Pallet labels matched the shipping notice", "“No discrepancies.”"),
    ("OTIF scorecard", f"{pct(k['otif']['scorecard'])} for June; misses on {', '.join(sorted({x['arrived_ts'][8:10].lstrip('0') for x in late + short}, key=int))} June, none of them atta", "“22 June was perfect.”"),
    ("Stock controller", f"26 June count: 5 kg {plus(five['adjustment'])}, 1 kg {plus(one['adjustment'])}", "“Sloppy counting, or theft.”"),
]
table = [f'<table style="font-size:28px;color:{INK}">',
         f'<tr><th style="width:22%;text-align:left;font-weight:600;color:{MUTED}">Who</th><th style="width:48%;text-align:left;font-weight:600;color:{MUTED}">What they see</th><th style="width:30%;text-align:left;font-weight:600;color:{MUTED}">What they conclude</th></tr>']
table += [f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows]
table.append('</table>')
slides["readings"] = section("readings", "\n".join([h2("Five readings of one delivery"), *table,
    foot("Each conclusion is reasonable given the record in front of that person. Each misses the wrong line.")]),
    f"As in the retail story, nobody is careless. The DC shift supervisor sees pick confirmations for every line, and later two count variances in the atta bay, both corrected and closed. The transport manager sees a trip log: left at 04:30, arrived at 06:12, inside the slot, and on time on {k['in_slot']} of {k['shipments']} mornings in June. The receiving clerk sees pallet labels that matched the notice. The OTIF scorecard shows {pct(k['otif']['scorecard'])} for June, and counts 22 June as perfect. And the stock controller, after a count on Friday 26 June, sees {abs(five['adjustment'])} bags of 5 kg gone and {one['adjustment']} packs of 1 kg from nowhere, and suspects sloppy counting or theft.",
    gap=40)

doc_rows = [
    ("Pick confirmation", f"03:00, slot {pick['slot']}: {pick['cases_confirmed']} cases of atta 5 kg, by slot label scan"),
    ("Shipping notice", f"Line 1: {st['line']['cases']} cases of atta 5 kg, {st['line']['units']} bags"),
    ("Pallet label", f"SSCC {st['line']['sscc']}"),
    ("Goods receipt", f"{st['receipt']['grn_id']}, 06:12: {st['receipt']['units_booked']} bags of atta 5 kg booked"),
]
dtab = ['<div style="display:flex;flex-direction:column">']
dtab += [f'<div style="display:flex;gap:32px;align-items:baseline;border-top:2px solid #d5d9d4;padding:12px 0 12px 0"><p style="width:470px;{SIGN};font-size:30px;font-weight:500">{a}</p><p style="{MONO};font-size:28px;color:{RECORD}">{b}</p></div>' for a, b in doc_rows]
dtab.append(f'<div style="display:flex;gap:32px;align-items:baseline;background:{HL};border-top:4px solid {INK};padding:16px 16px 16px 16px"><p style="width:438px;{SIGN};font-size:30px;font-weight:700;color:{INK}">On the pallet</p><p style="font-size:32px;color:{INK}">{st["line"]["cases"]} bales of atta 1 kg, {st["actual"]["units_actual"]} packs</p></div>')
dtab.append('</div>')
slides["happened"] = section("happened", "\n".join([h2("The scan confirmed the slot, not the item"), *dtab,
    f'<p style="font-size:32px;line-height:1.45;width:1500px">At 03:00 the picker stood at slot {pick["slot"]} (5 kg) and took the bales from {d["slots"]["ATTA-WW-1KG"]} next to it. Every record after that was written from the pick confirmation, so they all agree.</p>']),
    f"Here is what nobody could see. At three in the morning the picker went to slot {pick['slot']} for {pick['cases_confirmed']} cases of 5 kg atta, scanned the slot’s label, and took {pick['cases_confirmed']} bales from {d['slots']['ATTA-WW-1KG']} next to it: the same brand’s 1 kg packs. The scan confirmed where the picker stood, not what the picker took. Every record after that was written from the pick confirmation: the shipping notice, the pallet label, whose SSCC points to the notice and says nothing about the contents, and the store’s goods receipt, booked by matching the label to the notice. They agree with each other perfectly, and with the pallet not at all.",
    gap=40)

# Chart: 5 kg books vs shelf, 20-28 June.
W, H = 1664, 480
book, shelf, empty = A["hourly"]["book_5kg"], A["hourly"]["shelf_5kg"], A["hourly"]["empty_5kg"]
n = len(book)
ymax = 100
x = lambda i: i * W / (n - 1)
y = lambda v: H - v / ymax * H
step = W / (n - 1)
bands = []
start = -1
for i, v in enumerate(empty):
    if v > 0 and start < 0:
        start = i
    if (v <= 0 or i == n - 1) and start >= 0:
        end = i if v > 0 else i - 1
        bands.append((max(0, x(start) - step / 2), min(W, x(end) + step / 2)))
        start = -1
path = lambda vals: "".join(f"{'L' if i else 'M'}{x(i):.0f},{y(v):.0f}" for i, v in enumerate(vals))
svg = [f'<svg aria-label="Line chart, 20 to 28 June, every open hour. Book stock of 5 kg atta jumps by 64 on Monday 22 June and sits at 63 from Tuesday afternoon to Friday morning while the shelf is at zero." width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
svg += [f'<rect x="{a:.0f}" y="0" width="{b - a:.0f}" height="{H}" fill="#fbe68a"/>' for a, b in bands]
for v in (25, 50, 75, 100):
    svg.append(f'<line x1="0" y1="{y(v):.0f}" x2="{W}" y2="{y(v):.0f}" stroke="#dde1dc" stroke-width="2"/>')
svg.append(f'<line x1="0" y1="{H - 1}" x2="{W}" y2="{H - 1}" stroke="#b9bfb7" stroke-width="2"/>')
svg.append(f'<path d="{path(shelf)}" fill="none" stroke="#d9661f" stroke-width="5" stroke-linejoin="round"/>')
svg.append(f'<path d="{path(book)}" fill="none" stroke="#2f55a4" stroke-width="5" stroke-linejoin="round"/>')
svg.append('</svg>')
labels = ["Sat 20", "Sun 21", "Mon 22", "Tue 23", "Wed 24", "Thu 25", "Fri 26", "Sat 27", "Sun 28"]
slides["chart"] = section("chart", "\n".join([
    h2(f"The books said {ep['book_on_hand_max']}. The shelf was empty."), *svg,
    '<div style="display:flex;gap:0">' + "".join(f'<p style="flex:1;{SIGN};font-size:24px;color:{MUTED}">{t}</p>' for t in labels) + '</div>',
    '<div style="display:flex;gap:48px;align-items:center">'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:48px;height:6px;background:#2f55a4"></div><p style="{SIGN};font-size:26px">On the books</p></div>'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:48px;height:6px;background:#d9661f"></div><p style="{SIGN};font-size:26px">On the shelf</p></div>'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:32px;height:32px;background:#fbe68a"></div><p style="{SIGN};font-size:26px">Shelf empty</p></div>'
    + '</div>',
    foot("5 kg atta at Store 014, bags, every open hour from 20 to 28 June 2026. Grid lines every 25 bags. Synthetic world, seed 42."),
]), f"Hour by hour, 20 to 28 June. The blue line is what the books said: on Monday morning it jumps by the {st['line']['units']} bags the notice promised. The orange line is what was on the shelf. It sells down through the stock the store already had and hits zero at half past three on Tuesday. Then three nights in a row the reorder run sees {ep['book_on_hand_max']} bags against a reorder point of {ep['reorder_point'][0]} or {ep['reorder_point'][1]}, and orders nothing. Friday’s count zeroes the books, the system orders that night, and Saturday’s truck refills the bay: {ep['empty_open_hours']} open hours with an empty shelf.",
    gap=24)

slides["cost"] = section("cost", "\n".join([
    h2("What the shelf lost"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:96px">',
    '<div style="display:flex;flex-direction:column;gap:40px">',
    f'<div style="display:flex;flex-direction:column;gap:4px"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">{ep["empty_open_hours"]}</p><p style="{SIGN};font-size:32px;color:{MUTED}">open hours with the 5 kg shelf empty</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:4px"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">{inr(ep["lost_value_inr"])}</p><p style="{SIGN};font-size:32px;color:{MUTED}">of 5 kg atta customers wanted and could not buy</p></div>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:24px">',
    f'<h3 style="{SIGN};font-size:36px;font-weight:600;line-height:1.2">{ep["lost_units"]} bags wanted during the gap and not bought</h3>',
    f'<table style="font-size:30px;color:{INK}">',
    f'<tr><th style="width:75%;text-align:left;font-weight:600;color:{MUTED}">What the shopper did</th><th style="width:25%;text-align:right;font-weight:600;color:{MUTED}">Bags</th></tr>',
    *[f'<tr><td>{a}</td><td style="text-align:right">{b}</td></tr>' for a, b in [("Went to another store", r["elsewhere"]), ("Took a different pack size", r["other_pack"]), ("Bought another brand", r["other_brand"]), ("Came back later", r["delay"]), ("Never bought it", r["skip"])]],
    '</table>', '</div>', '</div>',
    foot("At the shelf price of ₹265 a bag. Shopper responses follow Gruen, Corsten and Bharadwaj (2002)."),
]), f"The 5 kg shelf was empty for {ep['empty_open_hours']} open hours. Customers wanted {ep['lost_units']} bags they could not buy, {inr(ep['lost_value_inr'])} at the shelf price. {r['elsewhere']} of those became trips to another store, {r['other_pack']} a different pack size and {r['other_brand']} another brand; {r['delay']} shoppers came back later and {r['skip']} bags were never bought.",
    bg=PANEL)

ledger = [("Warehouse, Tue 23 Jun 14:20", "Atta 1 kg", "−160 (−16 cases)", inr(-7920), "slot count variance"),
          ("Warehouse, Thu 25 Jun 10:00", "Atta 5 kg", "+64 (+16 cases)", inr(14592), "cycle count variance"),
          ("Store, Fri 26 Jun 09:00", "Atta 5 kg", plus(five["adjustment"]), inr(five["adjustment"] * cost["ATTA-WW-5KG"]), "count after complaints"),
          ("Store, Fri 26 Jun 09:00", "Atta 1 kg", plus(one["adjustment"]), inr(one["adjustment"] * cost["ATTA-WW-1KG"]), "count after complaints")]
assert [a["units"] for a in st["dc_adjustments"]] == [-160, 64]
ltab = [f'<table style="font-size:28px;color:{INK}">',
        f'<tr><th style="width:30%;text-align:left;font-weight:600;color:{MUTED}">Where and when</th><th style="width:15%;text-align:left;font-weight:600;color:{MUTED}">Item</th><th style="width:20%;text-align:right;font-weight:600;color:{MUTED}">Units</th><th style="width:15%;text-align:right;font-weight:600;color:{MUTED}">At cost</th><th style="width:20%;text-align:left;font-weight:600;color:{MUTED}">Recorded as</th></tr>']
ltab += [f'<tr><td>{a}</td><td>{b}</td><td style="text-align:right">{c}</td><td style="text-align:right">{dd}</td><td style="color:{MUTED}">{e}</td></tr>' for a, b, c, dd, e in ledger]
ltab.append(f'<tr style="background:#dfe3dd"><td>Net, across the company</td><td></td><td></td><td style="text-align:right">{inr(st["adjustments_net"]["value_at_cost_inr"])}</td><td></td></tr>')
ltab.append('</table>')
slides["corrections"] = section("corrections", "\n".join([h2("Four corrections, one mistake"), *ltab,
    '<p style="font-size:32px;line-height:1.45;width:1500px">Equal and opposite variances in neighbouring slots, mirrored at a store that got a truck from them, is the signature of a mis-pick.</p>']),
    f"The mis-pick left four records wrong, two in each building, and each was fixed on its own. The warehouse found the 1 kg slot sixteen cases short on Tuesday and the 5 kg slot sixteen cases over on Thursday, and closed both as count variances. The store found its two in a single count on Friday, after complaints. Across the company they net to about {inr(st['adjustments_net']['value_at_cost_inr'])}, which is why nobody chases them. Read together, they are the signature of a mis-pick, and the pick confirmations would name the truck in a minute.",
    gap=40)

slides["normal"] = section("normal", "\n".join([
    h2("This is the normal case"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:64px">',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">99.68%</p><p style="font-size:30px;line-height:1.4">best-in-class order-picking accuracy (WERC DC Measures, 2025). About one in 300 still goes wrong.</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">57%</p><p style="font-size:30px;line-height:1.4">of supplier orders physically checked at retail warehouses, on average; about 1 retailer in 10 checks every unit</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">92%</p><p style="font-size:30px;line-height:1.4">median accuracy those checks found, against a median goal of 98%</p></div>',
    '</div>',
    f'<p style="font-size:32px;line-height:1.45;color:{INK};background:{PANEL};padding:24px 32px">Receiving by scanning a pallet’s SSCC against the shipping notice is how GS1’s standards are meant to work. It is exactly as accurate as the notice.</p>',
    foot("Sources: WERC DC Measures 2025 via Yale; Gibson (2017), Auburn University ASN study; GS1 UK, Logistics labels and SSCCs."),
]), "Mis-picks are a rate, not a freak event. WERC’s DC Measures benchmark puts best-in-class order-picking accuracy at 99.68 percent or better, which still means about one in three hundred goes wrong. Receiving against the shipping notice is the design: under GS1’s standards the shipper sends a despatch advice that identifies every pallet by its SSCC, so the receiver scans a label instead of counting. And checking is sampled: in Auburn University’s 2017 study, retail warehouses physically checked 57 percent of supplier orders on average, about one retailer in ten checked every unit, and the checks found a median accuracy of 92 percent against a goal of 98.",
    gap=56)

ways = [("The DC’s report", "dc_report", "Dispatched on schedule, shipped as ordered, by its own pick confirmations", "#8db0f0"),
        ("Scorecard, per line", "by_line", "Order lines in the slot and in full, by the store’s goods receipt", "#e6eaee"),
        ("Scorecard, per delivery", "scorecard", "Deliveries in the slot with every line in full, by goods receipt", "#e6eaee"),
        ("What the shelf got", "at_the_shelf", "Deliveries in the slot with every case what was ordered", HL)]
cells = [f'<div style="display:flex;flex-direction:column;gap:16px;border-top:4px solid {c};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{c if c != "#e6eaee" else "#e6eaee"}">{pct(k["otif"][key])}</p><p style="{SIGN};font-size:32px;font-weight:600">{label}</p><p style="font-size:26px;line-height:1.4;color:#a3adb8">{how}</p></div>' for label, key, how, c in ways]
slides["fourways"] = section("fourways", "\n".join([
    h2("One name, four numbers", "#e6eaee"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:48px">', *cells, '</div>',
    f'<p style="font-size:34px;line-height:1.45;width:1500px">OTIF for the warehouse’s {k["shipments"]} deliveries to Store 014 in June. The 22 June delivery passes the first three and fails the fourth, which nobody computes because nobody records it.</p>',
]), f"OTIF, on time and in full, sounds like one number. The warehouse measures its own dispatch: {pct(k['otif']['dc_report'])}. The scorecard measures arrival in the slot and fullness by the store’s goods receipt: {pct(k['otif']['by_line'])} per order line, {pct(k['otif']['scorecard'])} per delivery. Only counting what was really on the pallets gives {pct(k['otif']['at_the_shelf'])}. Real programmes move their definitions too: Walmart began fining suppliers three percent of the value of late or missing goods in 2017, early deliveries included; in 2019 full truckloads had to arrive within a two-day window 87 percent of the time; from September 2020 the target was 98. Before comparing two OTIF numbers, ask what window and which record each one uses.",
    bg=INK, fg="#e6eaee", gap=64)

PS, CW, CS = S["pick_scan|label"], S["check_weigh|label"], S["none|case_scan"]
cards = [
    ("Scan every case at pick", f"{pct(k['otif']['scorecard'])} → {pct(PS['kpis']['otif']['scorecard'])}", f"scorecard unchanged, and now true: the shelf got {pct(PS['kpis']['otif']['at_the_shelf'])} too; {PS['kpis']['lost_units_after']} bag missed all week", "The scanner reads the bale, not the slot, and rejects 1 kg on a 5 kg line.", "#1a9e70"),
    ("Weigh every pallet", f"{pct(k['otif']['scorecard'])} → {pct(CW['kpis']['otif']['scorecard'])}", f"scorecard falls; {CW['kpis']['lost_units_after']} bag missed all week", f"The pallet is {round(light)} kg light. Re-picked, the truck arrives {CW['shipment']['arrived_ts'][11:16]}, late.", RED),
    ("Scan every case at the store", f"{pct(k['otif']['scorecard'])} → {pct(CS['kpis']['otif']['scorecard'])}", f"scorecard falls; {CS['kpis']['lost_units_after']} bags missed", "The clerk books what arrived and raises a claim. 5 kg is reordered that night.", RED),
]
cardhtml = [f'<div style="display:flex;flex-direction:column;gap:18px;background:{PANEL};padding:40px;border-top:8px solid {c}"><h3 style="{SIGN};font-size:40px;font-weight:600;line-height:1.2">{t}</h3><p style="{SIGN};font-size:64px;font-weight:700;line-height:1.05">{big}</p><p style="font-size:26px;line-height:1.4">{small}</p><p style="font-size:26px;line-height:1.4;color:{MUTED}">{note}</p></div>' for t, big, small, note, c in cards]
slides["helped"] = section("helped", "\n".join([
    h2("Two of three fixes make OTIF worse"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:40px">', *cardhtml, '</div>',
    foot("OTIF per delivery for June, on the scorecard. Same customers and trucks in every scenario; the changes start on 1 June. Try them in the demo."),
]), f"The demo lets you try three changes from the first of June, with the same customers and trucks. Scanning every case at pick prevents the mistake: the scanner rejects a 1 kg bale on a 5 kg line, and the scorecard and the shelf agree at {pct(PS['kpis']['otif']['scorecard'])}. Weighing every pallet at dispatch catches it: the first pallet is {round(light)} kg light, the line is re-picked, and the truck reaches the store at {CW['shipment']['arrived_ts'][11:16]}, outside its slot, so the scorecard falls to {pct(CW['kpis']['otif']['scorecard'])} while the shelf stays full. Scanning every case at the store catches it on arrival: the clerk books what came and raises a claim, and the scorecard also falls to {pct(CS['kpis']['otif']['scorecard'])}, because it now records what arrived. A measure that only reads the sender’s records improves when you stop checking.",
    gap=48)

slides["data"] = section("data", "\n".join([
    h2("Nothing in the records says “wrong item”"),
    '<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:72px;align-items:start">',
    f'<div style="background:{PANEL};border-left:6px solid {RECORD};padding:24px 32px;display:flex;flex-direction:column;gap:20px">',
    f'<table style="{MONO};font-size:26px;color:{RECORD}">',
    '<tr><th style="width:22%;text-align:left;font-weight:500">Pallet</th><th style="width:14%;text-align:left;font-weight:500">Line</th><th style="width:30%;text-align:left;font-weight:500">Item</th><th style="width:16%;text-align:right;font-weight:500">Cases</th><th style="width:18%;text-align:right;font-weight:500">Units</th></tr>',
    *[f'<tr><td>…{a["sscc"][-4:]}</td><td>{a["line"]}</td><td>{ {"ATTA-WW-5KG": "Atta 5 kg", "ATTA-WW-1KG": "Atta 1 kg", "RICE-SM-5KG": "Rice 5 kg", "SUGAR-1KG": "Sugar 1 kg"}[a["sku"]]}</td><td style="text-align:right">{a["cases"]}</td><td style="text-align:right">{a["units"]}</td></tr>'
      for a in d["records"]["notice"] if a["shipment_id"] == st["shipment"]["shipment_id"]],
    '</table>',
    f'<p style="{MONO};font-size:26px;color:{RECORD}">Receipt: booked as notice. Discrepancies: none.</p>', '</div>',
    '<div style="display:flex;flex-direction:column;gap:28px">',
    '<p style="font-size:32px;line-height:1.45">The notice, the pallet label and the receipt join without a mismatch, because all three come from the same pick.</p>',
    '<p style="font-size:32px;line-height:1.45">The evidence is in records that do not share that source: pallet weights against case weights, a 1 kg backroom growing without receipts, 5 kg sales stopping while the books sit at 63.</p>',
    '</div>', '</div>',
    foot(f"Shipping notice {st['shipment']['shipment_id']} and goods receipt {st['receipt']['grn_id']}. Identifiers use GS1 prefix 29, set aside for restricted circulation."),
]), "If you work with logistics data, slow down here. This is the shipping notice for the 22 June truck, and the store’s receipt simply copies it. The SSCC joins notice, pallet table and receipt without one mismatch, because all three were written from the same pick. The evidence is in records that do not share that source: the weight a pallet’s notice implies against the case weights in the product master, a 1 kg backroom that keeps growing without receipts, 5 kg sales that stop while the books sit at 63, and two warehouse variances in neighbouring slots two days apart. Knowing which records are independent of each other is most of the job.",
    gap=48)

learn = [
    ("How a warehouse works", "Bartholdi and Hackman, <i>Warehouse &amp; Distribution Science</i> (free from the authors), and Gwynne Richards, <i>Warehouse Management</i>. Then walk a warehouse, dock to dispatch."),
    ("Fundamentals", "MIT’s Supply Chain Fundamentals (CTL.SC1x): demand, inventory and transport."),
    ("Documents and IDs", "GS1 logistic label, SSCC and despatch advice. In India, the e-way bill for most consignments over ₹50,000 (rule 138, CGST Rules)."),
    ("Metrics", "OTIF, case fill, pick accuracy, dock-to-stock. How Walmart’s OTIF changed; WERC’s DC Measures."),
    ("Practice", "Download June’s shipping records, compute OTIF two ways, and find the 22 June line."),
]
slides["learn"] = section("learn", "\n".join([
    h2("How to learn this domain"),
    '<div style="display:flex;flex-direction:column;gap:22px">',
    *[f'<div style="display:grid;grid-template-columns:340px 1fr;gap:40px;border-top:2px solid #d5d9d4;padding:20px 0 0 0"><p style="{SIGN};font-size:32px;font-weight:600">{a}</p><p style="font-size:28px;line-height:1.4">{b}</p></div>' for a, b in learn],
    '</div>',
    foot("A rough plan for a few evenings a week over about two months. Links in the post: kvinayakpai.github.io/domain-series/logistics"),
]), "A rough plan for a few evenings a week over about two months. Read Bartholdi and Hackman’s Warehouse and Distribution Science, free from the authors, and Gwynne Richards’s Warehouse Management, then walk a warehouse from the receiving dock to dispatch. Take MIT’s Supply Chain Fundamentals. Learn the GS1 logistic label, the SSCC and the despatch advice, and in India the e-way bill. Learn the metrics and how their definitions differ. Then practise on Store 014’s June shipping records.",
    gap=44)

slides["close"] = section("close", "\n".join([
    f'<h2 style="{SIGN};font-size:88px;font-weight:700;line-height:1.08;color:#e6eaee;width:1500px">Every record agreed. That is why nobody checked the pallet.</h2>',
    '<div style="display:flex;flex-direction:column;gap:16px">',
    '<p style="font-size:34px;line-height:1.45">Run the scenarios and download the records:</p>',
    f'<p style="{MONO};font-size:36px;color:#8db0f0"><a href="https://kvinayakpai.github.io/domain-series/demo/#logistics"><span style="color:#8db0f0">kvinayakpai.github.io/domain-series</span></a></p>',
    '</div>',
    f'<div style="display:flex;flex-direction:column;gap:8px;border-left:6px solid {HL};padding:8px 0 8px 32px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:#a3adb8">Next: payments</p>',
    '<p style="font-size:36px;line-height:1.35">The till says the payment failed. The customer’s bank says it went through.</p>',
    '</div>',
]), "Every record agreed, and that is exactly why nobody checked the pallet. The demo on the series site lets you take each person’s view of the same delivery, switch on the checks, and download June’s shipping records to find the wrong line yourself. The next post moves from goods to money: a UPI payment the till marks as failed, while the customer’s bank has already taken the money.",
    bg=INK, fg="#e6eaee", gap=56, center=True)

order = ["cover", "scene", "readings", "happened", "chart", "cost", "corrections", "normal", "fourways", "helped", "data", "learn", "close"]
for sid in order:
    (OUT / "slides" / f"{sid}.html").write_text(slides[sid])
prev = OUT / "deck.json"
deck = json.loads((prev if prev.exists() else ROOT / "decks" / "retail" / "project" / "deck.json").read_text())
deck["title"] = "Why Domain Matters: Logistics and supply chain"
deck["order"] = order
deck["sections"] = {
    "s1": {"description": "The scene, and five readings of one delivery", "start": "cover"},
    "s2": {"description": "What actually happened, what it cost, and the four corrections", "start": "happened"},
    "s3": {"description": "Why it is normal, and OTIF measured four ways", "start": "normal"},
    "s4": {"description": "What would have helped, what the data looks like, and how to learn the domain", "start": "helped"},
}
(OUT / "deck.json").write_text(json.dumps(deck))
print(f"wrote {OUT.relative_to(ROOT)}: {len(order)} slides")
